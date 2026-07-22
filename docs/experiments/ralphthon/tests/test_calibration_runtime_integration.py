from __future__ import annotations

import json
import sys
import tempfile
import unittest
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ralphthon_track2_review_agent.calibration import (  # noqa: E402
    CalibrationGateSnapshot,
    CalibrationPolicy,
    MockVerifier,
)
from ralphthon_track2_review_agent.contract import validate_review  # noqa: E402
from ralphthon_track2_review_agent.io_utils import (  # noqa: E402
    canonical_json_bytes,
    sha256_bytes,
)
from ralphthon_track2_review_agent.ledger import AtomicLedger  # noqa: E402
from ralphthon_track2_review_agent.runtime import (  # noqa: E402
    MockReviewPlatform,
    load_papers,
    run_batch,
)


PAPERS = load_papers(ROOT / "fixtures/throughput/papers.json")
OPEN_GATE = CalibrationGateSnapshot(
    elapsed_seconds=0,
    validated_backlog=0,
    posting_pace_on_target=True,
    pending_draft_assignments=False,
)
HIGH_RISK = {"central_evidence_mismatch": True}
REPAIR_COMMENT = {
    "verdict": "REPAIR",
    "findings": [
        {
            "field_path": "/comment",
            "problem": "The conclusion is broader than the reported comparison.",
            "location": "Results (page 3)",
            "instruction": "Narrow the conclusion to the reported comparison.",
        }
    ],
}


class CapturingPlatform(MockReviewPlatform):
    """Capture Worker output before Root calibration without changing behavior."""

    def __init__(self, failure_plan: Mapping[str, Any] | None = None) -> None:
        super().__init__(failure_plan)
        self.worker_drafts: dict[str, dict[str, Any]] = {}

    def draft(self, paper, manifest, worker_id):  # type: ignore[no-untyped-def]
        result = super().draft(paper, manifest, worker_id)
        if isinstance(result, Mapping):
            self.worker_drafts[str(paper["paper_id"])] = deepcopy(dict(result))
        return result


def _risk_map(papers: list[dict[str, Any]]) -> dict[str, dict[str, bool]]:
    return {str(paper["paper_id"]): dict(HIGH_RISK) for paper in papers}


def _events(output: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (output / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _states(output: Path, paper_id: str | None = None) -> Counter[str]:
    return Counter(
        str(event["state"])
        for event in _events(output)
        if paper_id is None or event["paper_id"] == paper_id
    )


def _outbox_review(output: Path, paper_id: str) -> dict[str, Any]:
    return json.loads((output / "outbox" / f"{paper_id}.json").read_text(encoding="utf-8"))


class CalibrationRuntimeIntegrationTests(unittest.TestCase):
    def test_high_risk_pass_preserves_worker_draft_and_posted_hash(self) -> None:
        paper = PAPERS[0]
        paper_id = str(paper["paper_id"])
        platform = CapturingPlatform()
        verifier = MockVerifier()

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "pass-unchanged"
            summary = run_batch(
                [paper],
                output,
                workers=1,
                platform=platform,
                root_dir=ROOT,
                verifier=verifier,
                risk_signals={paper_id: HIGH_RISK},
                calibration_gate=OPEN_GATE,
            )
            worker_draft = platform.worker_drafts[paper_id]
            posted_review = _outbox_review(output, paper_id)

            self.assertTrue(summary.success, summary.to_dict())
            self.assertEqual(summary.verifier_selected_count, 1)
            self.assertEqual(summary.verifier_pass_count, 1)
            self.assertEqual(verifier.calls, [paper_id])
            self.assertEqual(posted_review, worker_draft)
            self.assertEqual(
                canonical_json_bytes(posted_review),
                canonical_json_bytes(worker_draft),
            )
            expected_hash = sha256_bytes(canonical_json_bytes(worker_draft))
            self.assertEqual(platform.posted[paper_id], expected_hash)
            self.assertEqual(_states(output, paper_id)["verifier_attempt"], 1)
            self.assertEqual(_states(output, paper_id)["verifier_pass"], 1)

    def test_risk_two_bypasses_while_risk_three_is_selected(self) -> None:
        papers = PAPERS[:2]
        low_id, high_id = (str(paper["paper_id"]) for paper in papers)
        verifier = MockVerifier()

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "risk-boundary"
            summary = run_batch(
                papers,
                output,
                workers=2,
                root_dir=ROOT,
                verifier=verifier,
                risk_signals={
                    low_id: {"extraction_degraded": True},
                    high_id: HIGH_RISK,
                },
                calibration_gate=OPEN_GATE,
            )

            self.assertTrue(summary.success, summary.to_dict())
            self.assertEqual(summary.risk_scored_count, 2)
            self.assertEqual(summary.high_risk_count, 1)
            self.assertEqual(summary.verifier_selected_count, 1)
            self.assertEqual(verifier.calls, [high_id])
            self.assertEqual(summary.verifier_bypass_counts["below_threshold"], 1)
            low_risk = next(
                event
                for event in _events(output)
                if event["paper_id"] == low_id and event["state"] == "risk_assessed"
            )
            high_risk = next(
                event
                for event in _events(output)
                if event["paper_id"] == high_id and event["state"] == "risk_assessed"
            )
            self.assertEqual(low_risk["details"]["score"], 2)
            self.assertEqual(high_risk["details"]["score"], 3)

    def test_ten_paper_cap_serializes_verifier_and_pending_gate_bypasses(self) -> None:
        verifier = MockVerifier(delay_seconds=0.001)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "cap"
            summary = run_batch(
                PAPERS,
                output,
                workers=3,
                root_dir=ROOT,
                verifier=verifier,
                risk_signals=_risk_map(PAPERS),
                calibration_gate=OPEN_GATE,
            )

            self.assertTrue(summary.success, summary.to_dict())
            self.assertEqual(summary.verifier_cap, 3)
            self.assertEqual(summary.verifier_selected_count, 3)
            self.assertEqual(len(verifier.calls), 3)
            self.assertEqual(len(set(verifier.calls)), 3)
            self.assertEqual(summary.verifier_max_active, 1)
            self.assertEqual(verifier.max_active, 1)
            self.assertEqual(summary.verifier_bypass_counts["budget_exhausted"], 7)

        pending_verifier = MockVerifier()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "pending-gate"
            summary = run_batch(
                [PAPERS[0]],
                output,
                workers=1,
                root_dir=ROOT,
                verifier=pending_verifier,
                risk_signals={str(PAPERS[0]["paper_id"]): HIGH_RISK},
                calibration_gate=CalibrationGateSnapshot(
                    elapsed_seconds=0,
                    validated_backlog=0,
                    posting_pace_on_target=True,
                    pending_draft_assignments=True,
                ),
            )
            self.assertTrue(summary.success, summary.to_dict())
            self.assertEqual(summary.verifier_selected_count, 0)
            self.assertEqual(summary.verifier_bypass_counts["pending_drafts"], 1)
            self.assertEqual(pending_verifier.calls, [])

    def test_repair_is_field_scoped_revalidated_and_never_verified_twice(self) -> None:
        paper = PAPERS[0]
        paper_id = str(paper["paper_id"])
        platform = CapturingPlatform()
        verifier = MockVerifier({paper_id: REPAIR_COMMENT})

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "repair-once"
            first = run_batch(
                [paper],
                output,
                workers=1,
                platform=platform,
                root_dir=ROOT,
                verifier=verifier,
                risk_signals={paper_id: HIGH_RISK},
                calibration_gate=OPEN_GATE,
            )
            original = platform.worker_drafts[paper_id]
            repaired = _outbox_review(output, paper_id)
            manifest = json.loads(
                (output / "manifests" / f"{paper_id}.json").read_text(encoding="utf-8")
            )

            self.assertTrue(first.success, first.to_dict())
            self.assertEqual(first.verifier_repair_count, 1)
            self.assertEqual(first.calibration_repair_count, 1)
            self.assertEqual(platform.attempts[("calibration_repair", paper_id)], 1)
            self.assertNotEqual(repaired["comment"], original["comment"])
            self.assertEqual(
                {key: value for key, value in repaired.items() if key != "comment"},
                {key: value for key, value in original.items() if key != "comment"},
            )
            self.assertEqual(validate_review(repaired, manifest), [])
            self.assertEqual(_states(output, paper_id)["calibration_repair_validated"], 1)

            second = run_batch(
                [paper],
                output,
                workers=1,
                platform=platform,
                root_dir=ROOT,
                verifier=verifier,
                risk_signals={paper_id: HIGH_RISK},
                calibration_gate=OPEN_GATE,
            )
            self.assertTrue(second.success, second.to_dict())
            self.assertEqual(verifier.calls, [paper_id])
            self.assertEqual(platform.attempts[("calibration_repair", paper_id)], 1)
            self.assertEqual(_states(output, paper_id)["verifier_attempt"], 1)

    def test_resume_after_unfinished_calibration_never_posts_a_fresh_draft(self) -> None:
        paper = PAPERS[0]
        paper_id = str(paper["paper_id"])
        platform = CapturingPlatform()

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "unfinished-calibration"
            ledger = AtomicLedger(output / "ledger.jsonl")
            ledger.append(
                paper_id,
                "verifier_attempt",
                score=3,
                cap=1,
                timeout_seconds=20,
                active=1,
            )
            ledger.append(
                paper_id,
                "verifier_repair_requested",
                findings=REPAIR_COMMENT["findings"],
            )
            ledger.append(
                paper_id,
                "repair_attempt",
                source="calibration",
                fields=["/comment"],
            )
            ledger.append(
                paper_id,
                "calibration_repair_validated",
                changed=["/comment"],
            )

            summary = run_batch(
                [paper],
                output,
                workers=1,
                platform=platform,
                root_dir=ROOT,
            )

            self.assertFalse(summary.success)
            self.assertEqual(summary.posted_verified, 0)
            self.assertEqual(summary.failed_ids, (paper_id,))
            self.assertEqual(platform.attempts[("calibration_repair", paper_id)], 0)
            self.assertEqual(platform.posted, {})
            self.assertEqual(list((output / "outbox").glob("*.json")), [])
            self.assertEqual(_states(output, paper_id)["calibration_resume_blocked"], 1)
            self.assertEqual(_states(output, paper_id)["post_attempt"], 0)

    def test_schema_repair_consumes_the_shared_repair_budget(self) -> None:
        paper = PAPERS[0]
        paper_id = str(paper["paper_id"])
        failure_plan = {"malformed_json": [paper_id]}
        platform = MockReviewPlatform(failure_plan)
        verifier = MockVerifier({paper_id: REPAIR_COMMENT})

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "schema-repair"
            summary = run_batch(
                [paper],
                output,
                workers=1,
                failure_plan=failure_plan,
                platform=platform,
                root_dir=ROOT,
                verifier=verifier,
                risk_signals={paper_id: HIGH_RISK},
                calibration_gate=OPEN_GATE,
            )

            self.assertTrue(summary.success, summary.to_dict())
            self.assertEqual(summary.malformed_json_repairs, 1)
            self.assertEqual(summary.schema_repair_count, 1)
            self.assertEqual(summary.calibration_repair_count, 0)
            self.assertEqual(summary.verifier_selected_count, 0)
            self.assertEqual(summary.verifier_bypass_counts["prior_repair"], 1)
            self.assertEqual(verifier.calls, [])
            self.assertEqual(_states(output, paper_id)["repair_attempt"], 1)

    def test_verifier_faults_fail_open_once_and_match_summary_ledger_counts(self) -> None:
        papers = PAPERS[:3]
        paper_ids = [str(paper["paper_id"]) for paper in papers]
        platform = CapturingPlatform()
        verifier = MockVerifier(
            {
                paper_ids[0]: "timeout",
                paper_ids[1]: "failure",
                paper_ids[2]: "malformed",
            }
        )

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "fail-open"
            summary = run_batch(
                papers,
                output,
                workers=3,
                platform=platform,
                root_dir=ROOT,
                verifier=verifier,
                risk_signals=_risk_map(papers),
                calibration_policy=CalibrationPolicy(
                    max_papers=3,
                    assignment_fraction=1.0,
                ),
                calibration_gate=OPEN_GATE,
            )

            self.assertTrue(summary.success, summary.to_dict())
            self.assertEqual(summary.posted_verified, 3)
            self.assertEqual(summary.verifier_selected_count, 3)
            self.assertEqual(summary.verifier_timeout_count, 1)
            self.assertEqual(summary.verifier_failure_count, 1)
            self.assertEqual(summary.verifier_malformed_count, 1)
            self.assertEqual(Counter(verifier.calls), Counter(paper_ids))
            for paper_id in paper_ids:
                self.assertEqual(
                    _outbox_review(output, paper_id),
                    platform.worker_drafts[paper_id],
                )
                self.assertEqual(_states(output, paper_id)["verifier_attempt"], 1)
                self.assertEqual(_states(output, paper_id)["post_attempt"], 1)

            state_counts = _states(output)
            self.assertEqual(summary.verifier_selected_count, state_counts["verifier_attempt"])
            self.assertEqual(summary.verifier_timeout_count, state_counts["verifier_timeout"])
            self.assertEqual(summary.verifier_failure_count, state_counts["verifier_failure"])
            self.assertEqual(summary.verifier_malformed_count, state_counts["verifier_malformed"])
            saved_summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(saved_summary, summary.to_dict())

    def test_invalid_identity_or_scope_changing_repair_never_posts(self) -> None:
        papers = PAPERS[:3]
        paper_ids = [str(paper["paper_id"]) for paper in papers]
        failure_plan = {
            "calibration_repair_invalid": [paper_ids[0]],
            "calibration_repair_identity": [paper_ids[1]],
            "calibration_repair_scope": [paper_ids[2]],
        }
        platform = MockReviewPlatform(failure_plan)
        verifier = MockVerifier({paper_id: REPAIR_COMMENT for paper_id in paper_ids})

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "rejected-repairs"
            summary = run_batch(
                papers,
                output,
                workers=3,
                platform=platform,
                root_dir=ROOT,
                verifier=verifier,
                risk_signals=_risk_map(papers),
                calibration_policy=CalibrationPolicy(
                    max_papers=3,
                    assignment_fraction=1.0,
                ),
                calibration_gate=OPEN_GATE,
            )

            self.assertFalse(summary.success)
            self.assertEqual(summary.posted_verified, 0)
            self.assertEqual(summary.verifier_selected_count, 3)
            self.assertEqual(summary.verifier_repair_count, 3)
            self.assertEqual(summary.calibration_repair_count, 3)
            self.assertEqual(set(summary.failed_ids), set(paper_ids))
            self.assertEqual(Counter(verifier.calls), Counter(paper_ids))
            self.assertEqual(platform.posted, {})
            self.assertEqual(list((output / "outbox").glob("*.json")), [])
            self.assertEqual(_states(output)["post_attempt"], 0)
            self.assertEqual(
                _states(output, paper_ids[0])["calibration_repair_failed"],
                1,
            )
            for paper_id in paper_ids[1:]:
                paper_states = _states(output, paper_id)
                self.assertEqual(paper_states["verifier_attempt"], 1)
                self.assertEqual(
                    paper_states["calibration_scope_reject"]
                    + paper_states["identity_reject"],
                    1,
                )

    def test_build_mode_never_calls_the_verifier(self) -> None:
        paper = PAPERS[0]
        paper_id = str(paper["paper_id"])
        verifier = MockVerifier({paper_id: REPAIR_COMMENT})

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "build"
            summary = run_batch(
                [paper],
                output,
                mode="BUILD",
                root_dir=ROOT,
                verifier=verifier,
                risk_signals={paper_id: HIGH_RISK},
                calibration_gate=OPEN_GATE,
            )

            self.assertTrue(summary.success, summary.to_dict())
            self.assertEqual(summary.mode, "BUILD")
            self.assertEqual(summary.calibration_adapter, "none")
            self.assertEqual(summary.verifier_selected_count, 0)
            self.assertEqual(summary.risk_scored_count, 0)
            self.assertEqual(verifier.calls, [])
            self.assertEqual((output / "ledger.jsonl").read_bytes(), b"")
            self.assertEqual(list((output / "outbox").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
