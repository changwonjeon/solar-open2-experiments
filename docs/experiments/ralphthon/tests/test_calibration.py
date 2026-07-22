from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ralphthon_track2_review_agent.calibration import (  # noqa: E402
    CalibrationGateSnapshot,
    CalibrationPolicy,
    CalibrationRequest,
    MockVerifier,
    RiskSignals,
    VerifierDecision,
    VerifierDecisionError,
    assess_risk,
    calibration_cap,
    parse_verifier_decision,
    select_for_calibration,
)
from support import matching_manifest, valid_review  # noqa: E402


def request_for(paper_id: str = "paper-001") -> CalibrationRequest:
    review = valid_review(paper_id=paper_id, lease_id=f"lease-{paper_id}-1")
    return CalibrationRequest(
        paper_id=paper_id,
        paper_path=f"/frozen/{paper_id}.pdf",
        manifest=matching_manifest(review),
        lease_id=review["lease_id"],
        review=review,
        risk=assess_risk(RiskSignals(central_evidence_mismatch=True)),
    )


class RiskAndPolicyTests(unittest.TestCase):
    def test_risk_is_weighted_only_from_explicit_signals(self) -> None:
        assessment = assess_risk(
            RiskSignals(
                central_evidence_mismatch=True,
                extraction_degraded=True,
                borderline_rationale_missing=True,
            )
        )
        self.assertEqual(assessment.score, 6)
        self.assertEqual(
            assessment.reasons,
            (
                "central_evidence_mismatch",
                "extraction_degraded",
                "borderline_rationale_missing",
            ),
        )

    def test_calibration_cap_uses_ceiling_and_three_paper_maximum(self) -> None:
        expected = {0: 0, 1: 1, 3: 1, 4: 2, 7: 3, 10: 3, 100: 3}
        for assigned_count, cap in expected.items():
            with self.subTest(assigned_count=assigned_count):
                self.assertEqual(calibration_cap(assigned_count), cap)

    def test_policy_rejects_non_integer_or_non_boolean_gate_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "risk signals must be boolean"):
            RiskSignals(extraction_degraded=1)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "risk_threshold"):
            CalibrationPolicy(risk_threshold=3.5)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "max_validated_backlog"):
            CalibrationPolicy(max_validated_backlog=True)
        with self.assertRaisesRegex(ValueError, "pending_draft_assignments"):
            CalibrationGateSnapshot(0, 0, True, pending_draft_assignments=1)  # type: ignore[arg-type]

    def test_selection_includes_exact_risk_time_and_backlog_boundaries(self) -> None:
        policy = CalibrationPolicy()
        risk = assess_risk(RiskSignals(central_evidence_mismatch=True))
        eligible = select_for_calibration(
            policy,
            risk,
            CalibrationGateSnapshot(899.999, 2, True),
            assigned_count=10,
            selected_count=2,
        )
        self.assertTrue(eligible.selected)
        self.assertEqual(eligible.reason, "selected")
        self.assertEqual(eligible.cap, 3)

        cases = (
            (
                assess_risk(RiskSignals(extraction_degraded=True)),
                CalibrationGateSnapshot(0, 0, True),
                0,
                False,
                CalibrationPolicy(),
                "below_threshold",
            ),
            (risk, CalibrationGateSnapshot(900, 0, True), 0, False, policy, "t15"),
            (risk, CalibrationGateSnapshot(0, 3, True), 0, False, policy, "backlog"),
            (risk, CalibrationGateSnapshot(0, 0, False), 0, False, policy, "slow_pace"),
            (risk, CalibrationGateSnapshot(0, 0, True), 0, True, policy, "prior_repair"),
            (risk, CalibrationGateSnapshot(0, 0, True), 3, False, policy, "budget_exhausted"),
            (
                risk,
                CalibrationGateSnapshot(0, 0, True),
                0,
                False,
                CalibrationPolicy(fast_mode=True),
                "fast",
            ),
            (
                risk,
                CalibrationGateSnapshot(0, 0, True),
                0,
                False,
                CalibrationPolicy(emergency_mode=True),
                "emergency",
            ),
            (
                risk,
                CalibrationGateSnapshot(0, 0, True, pending_draft_assignments=True),
                0,
                False,
                policy,
                "pending_drafts",
            ),
        )
        for case_risk, gate, selected, repaired, case_policy, reason in cases:
            with self.subTest(reason=reason):
                result = select_for_calibration(
                    case_policy,
                    case_risk,
                    gate,
                    assigned_count=10,
                    selected_count=selected,
                    repaired=repaired,
                )
                self.assertFalse(result.selected)
                self.assertEqual(result.reason, reason)


class VerifierDecisionTests(unittest.TestCase):
    def test_pass_requires_and_preserves_an_empty_finding_set(self) -> None:
        decision = parse_verifier_decision({"verdict": "PASS", "findings": []})
        self.assertEqual(decision, VerifierDecision("PASS"))

    def test_repair_accepts_one_to_three_exact_field_scoped_findings(self) -> None:
        decision = parse_verifier_decision(
            {
                "verdict": "REPAIR",
                "findings": [
                    {
                        "field_path": "/weaknesses/0/claim",
                        "problem": "The strongest weakness conflicts with the reported ablation.",
                        "location": "Table 3 (page 7)",
                        "instruction": "Narrow the claim to the unsupported condition.",
                    },
                    {
                        "field_path": "/score_rationales/confidence/location",
                        "problem": "The rationale points to the wrong result.",
                        "location": "Section 5.2 (page 8)",
                        "instruction": "Point to the uncertainty analysis.",
                    },
                ],
            }
        )
        self.assertEqual(decision.verdict, "REPAIR")
        self.assertEqual(len(decision.findings), 2)

    def test_parser_rejects_unbounded_or_authority_crossing_outputs(self) -> None:
        valid_finding = {
            "field_path": "/comment",
            "problem": "The conclusion is too broad.",
            "location": "Conclusion (page 9)",
            "instruction": "Narrow the conclusion.",
        }
        invalid_cases = (
            {"verdict": "PASS", "findings": [valid_finding]},
            {"verdict": "REPAIR", "findings": []},
            {"verdict": "REPAIR", "findings": [valid_finding] * 4},
            {
                "verdict": "REPAIR",
                "findings": [{**valid_finding, "field_path": "/paper_id"}],
            },
            {
                "verdict": "REPAIR",
                "findings": [{**valid_finding, "location": "somewhere"}],
            },
            {"verdict": "PASS", "findings": [], "rationale": "hidden scratchpad"},
        )
        for raw in invalid_cases:
            with self.subTest(raw=raw):
                with self.assertRaises(VerifierDecisionError):
                    parse_verifier_decision(raw)

    def test_parser_rejects_duplicate_field_paths(self) -> None:
        finding = {
            "field_path": "/summary",
            "problem": "The scope is overstated.",
            "location": "Abstract (page 1)",
            "instruction": "Narrow the scope.",
        }
        with self.assertRaisesRegex(VerifierDecisionError, "duplicate field paths"):
            parse_verifier_decision(
                {"verdict": "REPAIR", "findings": [finding, dict(finding)]}
            )

    def test_parser_matches_schema_pointer_and_text_bounds(self) -> None:
        base = {
            "field_path": "/weaknesses/0/claim",
            "problem": "The scope is overstated.",
            "location": "Table 2 (page 5)",
            "instruction": "Narrow the scope.",
        }
        allowed = (
            "/strengths",
            "/weaknesses/12",
            "/evidence_trace/0/location",
            "/questions/2",
            "/score_rationales/overall_recommendation",
            "/score_rationales/confidence/claim",
        )
        for pointer in allowed:
            with self.subTest(pointer=pointer):
                decision = parse_verifier_decision(
                    {
                        "verdict": "REPAIR",
                        "findings": [{**base, "field_path": pointer}],
                    }
                )
                self.assertEqual(decision.findings[0].field_path, pointer)

        invalid = (
            {**base, "field_path": "weaknesses[0].claim"},
            {**base, "field_path": "/score_rationales"},
            {**base, "problem": "x" * 1001},
            {**base, "location": "page " + "x" * 496},
            {**base, "instruction": "x" * 1001},
        )
        for finding in invalid:
            with self.subTest(finding=finding):
                with self.assertRaises(VerifierDecisionError):
                    parse_verifier_decision({"verdict": "REPAIR", "findings": [finding]})


class MockVerifierTests(unittest.TestCase):
    def test_default_pass_and_scripted_repair_are_observable(self) -> None:
        repair = {
            "verdict": "REPAIR",
            "findings": [
                {
                    "field_path": "/confidence",
                    "problem": "Evidence coverage is thin.",
                    "location": "Appendix A (page 11)",
                    "instruction": "Lower confidence or add a matching rationale.",
                }
            ],
        }
        verifier = MockVerifier({"paper-002": repair})
        first = parse_verifier_decision(verifier.verify(request_for("paper-001")))
        second = parse_verifier_decision(verifier.verify(request_for("paper-002")))
        self.assertEqual(first.verdict, "PASS")
        self.assertEqual(second.verdict, "REPAIR")
        self.assertEqual(verifier.calls, ["paper-001", "paper-002"])
        self.assertEqual(verifier.max_active, 1)

    def test_fault_tokens_are_deterministic_and_counted_once(self) -> None:
        for token, exception in (("timeout", TimeoutError), ("failure", RuntimeError)):
            with self.subTest(token=token):
                verifier = MockVerifier({"paper-001": token})
                with self.assertRaises(exception):
                    verifier.verify(request_for())
                self.assertEqual(verifier.calls, ["paper-001"])
                self.assertEqual(verifier.max_active, 1)

        malformed = MockVerifier({"paper-001": "malformed"})
        with self.assertRaises(VerifierDecisionError):
            parse_verifier_decision(malformed.verify(request_for()))
        self.assertEqual(malformed.calls, ["paper-001"])


if __name__ == "__main__":
    unittest.main()
