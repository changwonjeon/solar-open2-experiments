from __future__ import annotations

import hashlib
import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quality_eval import evaluate, passes_threshold, predictions_from_outbox  # noqa: E402
from ralphthon_track2_review_agent.contract import validate_review  # noqa: E402
from ralphthon_track2_review_agent.ledger import audit_ledger  # noqa: E402


EVIDENCE = ROOT / "evidence/mock-validation-final-20260712T1335KST"
AGGREGATE = EVIDENCE / "aggregate.json"


class EvidenceConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.aggregate = json.loads(AGGREGATE.read_text(encoding="utf-8"))
        cls.assigned_ids = cls.aggregate["assigned_ids"]

    def test_three_raw_normal_runs_match_aggregate_and_contract(self) -> None:
        self.assertEqual(len(self.aggregate["normal_runs"]), 3)
        for run_number, aggregate_record in enumerate(self.aggregate["normal_runs"], start=1):
            run_dir = EVIDENCE / f"normal-{run_number}"
            stored_summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(stored_summary, aggregate_record["summary"])
            self.assertEqual(stored_summary["assigned_count"], 10)
            self.assertEqual(stored_summary["posted_verified"], 10)
            self.assertEqual(stored_summary["schema_valid_count"], 10)
            self.assertEqual(stored_summary["duplicate_post_attempts"], 0)
            self.assertEqual(stored_summary["duplicate_idempotency_keys"], 0)
            self.assertTrue(stored_summary["success"])
            self.assertEqual(audit_ledger(run_dir / "ledger.jsonl", self.assigned_ids), aggregate_record["audit"])
            for paper_id in self.assigned_ids:
                manifest = json.loads((run_dir / "manifests" / f"{paper_id}.json").read_text())
                review = json.loads((run_dir / "outbox" / f"{paper_id}.json").read_text())
                self.assertEqual(validate_review(review, manifest), [], paper_id)

    def test_failure_evidence_has_every_required_injection_and_no_duplicate(self) -> None:
        record = self.aggregate["failure_injection"]
        summary = record["summary"]
        self.assertTrue(summary["success"])
        self.assertEqual(summary["malformed_json_repairs"], 1)
        self.assertEqual(summary["worker_timeout_recoveries"], 1)
        self.assertEqual(summary["claim_timeout_reconciliations"], 1)
        self.assertEqual(summary["post_timeout_reconciliations"], 1)
        self.assertEqual(summary["restart_recoveries"], 1)
        self.assertEqual(summary["duplicate_post_attempts"], 0)
        self.assertEqual(summary["duplicate_idempotency_keys"], 0)
        observations = record["platform_observations"]
        self.assertEqual(observations["claim_status_checks_paper_003"], 2)
        self.assertEqual(observations["post_status_checks_paper_004"], 2)
        self.assertEqual(observations["claim_attempts_paper_003"], 1)
        self.assertEqual(observations["post_attempts_paper_004"], 1)

    def test_process_rerun_is_recorded_as_byte_idempotent(self) -> None:
        rerun = self.aggregate["process_rerun"]
        self.assertTrue(rerun["first"]["summary"]["success"])
        self.assertTrue(rerun["second"]["summary"]["success"])
        self.assertEqual(rerun["second"]["summary"]["posted_verified"], 10)
        self.assertEqual(rerun["second"]["summary"]["schema_valid_count"], 10)
        self.assertTrue(rerun["ledger_and_outbox_byte_idempotent"])

    def test_actual_two_process_restart_proof_is_linked_and_green(self) -> None:
        link = self.aggregate["actual_process_restart"]
        proof_path = ROOT / link["aggregate_path"]
        proof_bytes = proof_path.read_bytes()
        proof = json.loads(proof_bytes)

        self.assertEqual(hashlib.sha256(proof_bytes).hexdigest(), link["aggregate_sha256"])
        self.assertTrue(link["success"])
        self.assertEqual(link["interrupted_exit_code"], 75)
        self.assertEqual(link["resumed_exit_code"], 0)
        self.assertTrue(link["ledger_prefix_preserved"])
        self.assertTrue(link["completed_artifacts_preserved"])
        self.assertTrue(proof["success"])
        self.assertEqual(proof["resumed_process"]["summary"]["posted_verified"], 10)
        self.assertEqual(proof["resumed_process"]["summary"]["duplicate_post_attempts"], 0)

    def test_quality_numbers_recompute_from_frozen_gold_and_raw_outbox(self) -> None:
        gold = json.loads((ROOT / "fixtures/quality/gold.json").read_text())["findings"]
        baseline_document = json.loads(
            (ROOT / "fixtures/quality/naive-single-pass.json").read_text()
        )
        baseline = evaluate(baseline_document["predictions"], gold)
        candidate = evaluate(predictions_from_outbox(EVIDENCE / "normal-1/outbox"), gold)
        self.assertEqual(baseline, self.aggregate["quality"]["baseline"])
        self.assertEqual(candidate, self.aggregate["quality"]["mock_runtime"])
        self.assertTrue(passes_threshold(candidate, float(baseline["f1"])))
        self.assertTrue(self.aggregate["quality"]["threshold_passed"])

    def test_evidence_contains_no_local_identity_or_path(self) -> None:
        forbidden = ("/Users/", "redux80", "changwonjeon")
        email = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
        for path in EVIDENCE.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, path)
            self.assertIsNone(email.search(text), path)


if __name__ == "__main__":
    unittest.main()
