from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ralphthon_track2_review_agent.ledger import (  # noqa: E402
    AtomicLedger,
    LedgerOwnershipError,
    audit_ledger,
)
from ralphthon_track2_review_agent.manifest import (  # noqa: E402
    ManifestConflictError,
    build_manifest,
    freeze_manifest,
)
from support import SHA_A  # noqa: E402


PAPER = ROOT / "fixtures/throughput/paper-001.md"
EVIDENCE = ROOT / "fixtures/throughput/evidence-bundle.json"


class ManifestTests(unittest.TestCase):
    def test_manifest_hashes_input_and_evidence_before_worker_use(self) -> None:
        manifest = build_manifest(
            paper_id="paper-001",
            paper_path=PAPER,
            evidence_paths=[EVIDENCE],
            agent_version="test-agent-v1",
            prompt_hash=SHA_A,
            schema_hash="b" * 64,
            frozen_at="2026-07-12T03:45:00Z",
        )
        self.assertEqual(manifest["paper_id"], "paper-001")
        self.assertEqual(len(manifest["paper_hash"]), 64)
        self.assertEqual(len(manifest["evidence_hash"]), 64)
        self.assertEqual(len(manifest["input_hash"]), 64)
        self.assertEqual(manifest["paper"]["name"], "paper-001.md")
        self.assertEqual(manifest["evidence"][0]["name"], "evidence-bundle.json")

    def test_freeze_is_idempotent_but_rejects_identity_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "paper-001.json"
            arguments = {
                "paper_id": "paper-001",
                "paper_path": PAPER,
                "evidence_paths": [EVIDENCE],
                "agent_version": "test-agent-v1",
                "prompt_hash": SHA_A,
                "schema_hash": "b" * 64,
                "frozen_at": "2026-07-12T03:45:00Z",
            }
            first = freeze_manifest(output, **arguments)
            second = freeze_manifest(output, **arguments)
            self.assertEqual(first, second)
            with self.assertRaises(ManifestConflictError):
                freeze_manifest(output, **{**arguments, "agent_version": "changed"})

    def test_exactly_one_paper_input_is_required(self) -> None:
        common = {
            "paper_id": "paper-001",
            "agent_version": "v1",
            "prompt_hash": SHA_A,
            "schema_hash": "b" * 64,
        }
        with self.assertRaises(ValueError):
            build_manifest(**common)
        with self.assertRaises(ValueError):
            build_manifest(**common, paper_path=PAPER, paper_bytes=b"duplicate")


class LedgerTests(unittest.TestCase):
    def test_only_root_coordinator_can_own_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(LedgerOwnershipError):
                AtomicLedger(Path(temporary) / "ledger.jsonl", owner="worker-1")

    def test_append_restart_and_audit_preserve_exactly_once_post(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "ledger.jsonl"
            ledger = AtomicLedger(path)
            for paper_id in ("paper-001", "paper-002"):
                ledger.append(paper_id, "claimed")
                ledger.append(
                    paper_id,
                    "post_attempt",
                    idempotency_key=f"event:{paper_id}:review-v1",
                )
                ledger.append(paper_id, "posted_verified")

            restarted = AtomicLedger(path)
            self.assertEqual(restarted.posted_verified_ids(), {"paper-001", "paper-002"})
            audit = audit_ledger(path, ["paper-001", "paper-002"])
            self.assertTrue(audit["success"])
            self.assertEqual(audit["post_attempt_count"], 2)
            self.assertEqual(audit["duplicate_idempotency_keys"], 0)
            self.assertEqual(audit["duplicate_post_attempts_by_paper"], 0)
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 6)
            self.assertTrue(all(isinstance(json.loads(line), dict) for line in lines))

    def test_audit_rejects_duplicate_post_attempt_for_same_paper(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "ledger.jsonl"
            ledger = AtomicLedger(path)
            ledger.append("paper-001", "post_attempt", idempotency_key="key-1")
            ledger.append("paper-001", "post_attempt", idempotency_key="key-2")
            ledger.append("paper-001", "posted_verified")
            audit = audit_ledger(path, ["paper-001"])
            self.assertFalse(audit["success"])
            self.assertEqual(audit["duplicate_post_attempts_by_paper"], 1)

    def test_audit_requires_all_assigned_papers_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "ledger.jsonl"
            ledger = AtomicLedger(path)
            ledger.append("paper-001", "post_attempt", idempotency_key="key-1")
            ledger.append("paper-001", "posted_verified")
            audit = audit_ledger(path, ["paper-001", "paper-002"])
            self.assertFalse(audit["success"])
            self.assertEqual(audit["missing_ids"], ["paper-002"])


if __name__ == "__main__":
    unittest.main()
