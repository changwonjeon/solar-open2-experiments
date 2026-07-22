from __future__ import annotations

import sys
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ralphthon_track2_review_agent.contract import (  # noqa: E402
    REVIEW_DRAFT_SCHEMA,
    SCORE_RANGES,
    validate_review,
)
from support import matching_manifest, valid_review  # noqa: E402


class ReviewContractTests(unittest.TestCase):
    def test_canonical_valid_review_passes(self) -> None:
        review = valid_review()
        self.assertEqual(validate_review(review, matching_manifest(review)), [])

    def test_contribution_significance_and_originality_are_independent(self) -> None:
        review = valid_review()
        review["contribution"] = 1
        review["significance"] = 4
        review["originality"] = 2
        self.assertEqual(validate_review(review), [])
        description = REVIEW_DRAFT_SCHEMA["description"]
        self.assertIn("Contribution", description)
        self.assertIn("Significance", description)
        self.assertIn("never converted", description)

    def test_every_score_rejects_below_and_above_bounds(self) -> None:
        for field, (minimum, maximum) in SCORE_RANGES.items():
            for invalid in (minimum - 1, maximum + 1, float(minimum), True):
                with self.subTest(field=field, invalid=invalid):
                    review = valid_review()
                    review[field] = invalid
                    errors = validate_review(review)
                    self.assertTrue(any(error.startswith(f"{field}:") for error in errors), errors)

    def test_missing_empty_and_placeholder_comment_are_rejected(self) -> None:
        for invalid in (None, "", "  ", "TODO"):
            with self.subTest(invalid=invalid):
                review = valid_review()
                review["comment"] = invalid
                self.assertTrue(any(error.startswith("comment:") for error in validate_review(review)))

    def test_evidence_location_must_be_traceable(self) -> None:
        review = valid_review()
        review["strengths"][0]["location"] = "somewhere in the paper"
        errors = validate_review(review)
        self.assertIn(
            "strengths[0].location: expected page, section, table, figure, appendix, or saved result",
            errors,
        )

    def test_manifest_identity_mismatch_is_rejected(self) -> None:
        review = valid_review()
        manifest = matching_manifest(review)
        manifest["input_hash"] = "d" * 64
        self.assertIn("input_hash: does not match frozen manifest", validate_review(review, manifest))

    def test_worker_lease_must_match_active_root_lease(self) -> None:
        review = valid_review()
        errors = validate_review(
            review,
            matching_manifest(review),
            expected_lease_id="different-active-lease",
        )
        self.assertIn("lease_id: does not match active Root lease", errors)

    def test_unknown_field_is_rejected(self) -> None:
        review = valid_review()
        review["derived_significance"] = 4
        self.assertTrue(any("unexpected fields" in error for error in validate_review(review)))

    def test_malformed_review_returns_structured_errors(self) -> None:
        errors = validate_review("{malformed json")  # type: ignore[arg-type]
        self.assertEqual(errors, ["review: expected object"])

    def test_completion_time_cannot_precede_start(self) -> None:
        review = deepcopy(valid_review())
        review["completed_at"] = "2026-07-12T03:44:59Z"
        self.assertIn("completed_at: precedes started_at", validate_review(review))


if __name__ == "__main__":
    unittest.main()
