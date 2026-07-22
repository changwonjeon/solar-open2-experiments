from __future__ import annotations

import json
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ralphthon_track2_review_agent.contract import validate_review  # noqa: E402
from ralphthon_track2_review_agent.ledger import audit_ledger  # noqa: E402
from ralphthon_track2_review_agent.runtime import (  # noqa: E402
    LiveAdapterUnavailable,
    MockReviewPlatform,
    load_papers,
    run_batch,
)


PAPERS_PATH = ROOT / "fixtures/throughput/papers.json"
PAPERS = load_papers(PAPERS_PATH)
PAPER_IDS = [paper["paper_id"] for paper in PAPERS]


class RuntimeIntegrationTests(unittest.TestCase):
    def test_mock_ten_papers_three_runs_are_complete_valid_and_duplicate_free(self) -> None:
        for run_number in range(1, 4):
            with self.subTest(run_number=run_number), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / f"run-{run_number}"
                summary = run_batch(PAPERS, output, workers=3, root_dir=ROOT)
                self.assertTrue(summary.success, summary.to_dict())
                self.assertEqual(summary.assigned_count, 10)
                self.assertEqual(summary.posted_verified, 10)
                self.assertEqual(summary.schema_valid_count, 10)
                self.assertEqual(summary.duplicate_post_attempts, 0)
                self.assertEqual(summary.duplicate_idempotency_keys, 0)
                self.assertEqual(summary.failed_ids, ())
                self.assertEqual(len(list((output / "manifests").glob("*.json"))), 10)
                self.assertEqual(len(list((output / "outbox").glob("*.json"))), 10)
                self.assertEqual(len(list((output / "clipboard").glob("*.txt"))), 10)
                for paper_id in PAPER_IDS:
                    manifest = json.loads((output / "manifests" / f"{paper_id}.json").read_text())
                    review = json.loads((output / "outbox" / f"{paper_id}.json").read_text())
                    self.assertEqual(validate_review(review, manifest), [], paper_id)
                audit = audit_ledger(output / "ledger.jsonl", PAPER_IDS)
                self.assertTrue(audit["success"], audit)

    def test_logical_worker_ids_are_unique_while_drafts_are_active(self) -> None:
        class TrackingPlatform(MockReviewPlatform):
            def __init__(self) -> None:
                super().__init__()
                self.active_worker_ids: set[str] = set()
                self.duplicate_active_worker_ids: set[str] = set()
                self.max_active = 0
                self.lock = threading.Lock()

            def draft(self, paper, manifest, worker_id):  # type: ignore[no-untyped-def]
                with self.lock:
                    if worker_id in self.active_worker_ids:
                        self.duplicate_active_worker_ids.add(worker_id)
                    self.active_worker_ids.add(worker_id)
                    self.max_active = max(self.max_active, len(self.active_worker_ids))
                try:
                    time.sleep(0.01)
                    return super().draft(paper, manifest, worker_id)
                finally:
                    with self.lock:
                        self.active_worker_ids.remove(worker_id)

        platform = TrackingPlatform()
        with tempfile.TemporaryDirectory() as temporary:
            summary = run_batch(
                PAPERS,
                Path(temporary) / "worker-slots",
                workers=3,
                platform=platform,
                root_dir=ROOT,
            )
        self.assertTrue(summary.success, summary.to_dict())
        self.assertEqual(platform.max_active, 3)
        self.assertEqual(platform.duplicate_active_worker_ids, set())

    def test_all_required_failures_are_recovered_status_first(self) -> None:
        failure_plan = {
            "malformed_json": ["paper-001"],
            "worker_timeout": ["paper-002"],
            "claim_timeout": ["paper-003"],
            "post_timeout": ["paper-004"],
            "process_restart_after": 5,
        }
        platform = MockReviewPlatform(failure_plan)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "failure-run"
            summary = run_batch(
                PAPERS,
                output,
                workers=3,
                failure_plan=failure_plan,
                platform=platform,
                root_dir=ROOT,
            )
            self.assertTrue(summary.success, summary.to_dict())
            self.assertEqual(summary.posted_verified, 10)
            self.assertEqual(summary.schema_valid_count, 10)
            self.assertEqual(summary.malformed_json_repairs, 1)
            self.assertEqual(summary.worker_timeout_recoveries, 1)
            self.assertEqual(summary.claim_timeout_reconciliations, 1)
            self.assertEqual(summary.post_timeout_reconciliations, 1)
            self.assertEqual(summary.restart_recoveries, 1)
            self.assertEqual(summary.duplicate_post_attempts, 0)
            self.assertEqual(platform.status_checks[("claimed", "paper-003")], 2)
            self.assertEqual(platform.status_checks[("posted", "paper-004")], 2)
            self.assertEqual(platform.attempts[("claim_timeout", "paper-003")], 1)
            self.assertEqual(platform.attempts[("post_timeout", "paper-004")], 1)
            self.assertEqual(platform.attempts[("worker_timeout", "paper-002")], 2)
            states = [
                json.loads(line)["state"]
                for line in (output / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertIn("validator_reject", states)
            self.assertIn("worker_timeout", states)
            self.assertIn("claim_unknown", states)
            self.assertIn("post_unknown", states)

    def test_identity_mismatch_is_blocking_and_never_calls_repair(self) -> None:
        class WrongLeasePlatform(MockReviewPlatform):
            def __init__(self) -> None:
                super().__init__()
                self.repair_calls = 0

            def draft(self, paper, manifest, worker_id):  # type: ignore[no-untyped-def]
                review = dict(super().draft(paper, manifest, worker_id))
                review["lease_id"] = "wrong-active-lease"
                return review

            def repair(self, *args, **kwargs):  # type: ignore[no-untyped-def]
                self.repair_calls += 1
                return super().repair(*args, **kwargs)

        platform = WrongLeasePlatform()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "identity-reject"
            summary = run_batch(
                [PAPERS[0]],
                output,
                workers=1,
                platform=platform,
                root_dir=ROOT,
            )
            states = [
                json.loads(line)["state"]
                for line in (output / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertFalse(summary.success)
            self.assertEqual(summary.posted_verified, 0)
            self.assertEqual(platform.repair_calls, 0)
            self.assertIn("identity_reject", states)
            self.assertNotIn("validator_reject", states)
            self.assertFalse((output / "outbox/paper-001.json").exists())

    def test_build_mode_freezes_all_manifests_without_platform_actions(self) -> None:
        platform = MockReviewPlatform()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "build-run"
            first = run_batch(
                PAPERS,
                output,
                mode="BUILD",
                platform=platform,
                root_dir=ROOT,
            )
            manifests_before = {
                path.name: path.read_bytes()
                for path in sorted((output / "manifests").glob("*.json"))
            }
            second = run_batch(
                PAPERS,
                output,
                mode="BUILD",
                platform=platform,
                root_dir=ROOT,
            )
            self.assertTrue(first.success)
            self.assertTrue(second.success)
            self.assertEqual(first.assigned_count, 10)
            self.assertEqual(first.posted_verified, 0)
            self.assertEqual(first.schema_valid_count, 0)
            self.assertEqual(len(manifests_before), 10)
            self.assertEqual(
                {
                    path.name: path.read_bytes()
                    for path in sorted((output / "manifests").glob("*.json"))
                },
                manifests_before,
            )
            self.assertEqual((output / "ledger.jsonl").read_bytes(), b"")
            self.assertEqual(list((output / "outbox").iterdir()), [])
            self.assertEqual(list((output / "clipboard").iterdir()), [])
            self.assertEqual(platform.attempts, {})
            self.assertEqual(platform.status_checks, {})

    def test_successful_process_rerun_is_idempotent_and_reports_success(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "restart-run"
            first = run_batch(PAPERS, output, workers=3, root_dir=ROOT)
            ledger_before = (output / "ledger.jsonl").read_bytes()
            outbox_before = {
                path.name: path.read_bytes() for path in sorted((output / "outbox").glob("*.json"))
            }
            second = run_batch(PAPERS, output, workers=3, root_dir=ROOT)
            self.assertTrue(first.success, first.to_dict())
            self.assertTrue(second.success, second.to_dict())
            self.assertEqual(second.posted_verified, 10)
            self.assertEqual(second.schema_valid_count, 10)
            self.assertEqual(second.duplicate_post_attempts, 0)
            self.assertEqual((output / "ledger.jsonl").read_bytes(), ledger_before)
            self.assertEqual(
                {path.name: path.read_bytes() for path in sorted((output / "outbox").glob("*.json"))},
                outbox_before,
            )

    def test_live_mode_is_blocked_before_any_output_without_verified_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "live-run"
            with self.assertRaises(LiveAdapterUnavailable):
                run_batch(PAPERS, output, mode="LIVE", root_dir=ROOT)
            self.assertFalse(output.exists())

    def test_duplicate_assignment_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            duplicate = [PAPERS[0], PAPERS[0]]
            with self.assertRaisesRegex(ValueError, "paper_id values must be unique"):
                run_batch(duplicate, Path(temporary), root_dir=ROOT)

    def test_path_unsafe_paper_id_is_rejected_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "unsafe-run"
            unsafe = dict(PAPERS[0])
            unsafe["paper_id"] = "../escape"
            with self.assertRaisesRegex(ValueError, "path-safe ASCII identifier"):
                run_batch([unsafe], output, root_dir=ROOT)
            self.assertFalse(output.exists())

    def test_controlled_process_exit_hook_is_dry_run_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "build-run"
            with self.assertRaisesRegex(ValueError, "DRY-RUN-only test hook"):
                run_batch(
                    PAPERS,
                    output,
                    mode="BUILD",
                    failure_plan={"controlled_process_exit_after": 1},
                    root_dir=ROOT,
                )
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
