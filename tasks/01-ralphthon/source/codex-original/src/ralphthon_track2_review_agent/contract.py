"""Canonical ReviewDraft contract and deterministic validator."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Mapping, Sequence

from .io_utils import canonical_json_bytes, sha256_bytes

SCHEMA_VERSION = "1.0"
HEX_256 = re.compile(r"^[0-9a-f]{64}$")
PLACEHOLDER = re.compile(r"(?i)(?:\b(?:todo|tbd|placeholder|lorem ipsum)\b|\[[A-Z _-]+\])")
EVIDENCE_LOCATION = re.compile(
    r"(?i)(?:\bp(?:age)?\.?\s*\d+\b|\bsec(?:tion)?\.?\s*[A-Z0-9][\w.-]*|"
    r"\btable\s*[A-Z0-9][\w.-]*|\bfig(?:ure)?\.?\s*[A-Z0-9][\w.-]*|"
    r"\bappendix\s*[A-Z0-9][\w.-]*|\bsaved\s+result\b|\bevidence\s*:)"
)

SCORE_RANGES = {
    "soundness": (1, 4),
    "presentation": (1, 4),
    "contribution": (1, 4),
    "significance": (1, 4),
    "originality": (1, 4),
    "overall_recommendation": (1, 6),
    "confidence": (1, 5),
}

REQUIRED_FIELDS = (
    "review_draft_version",
    "paper_id",
    "lease_id",
    "summary",
    "strengths",
    "weaknesses",
    "questions",
    *SCORE_RANGES,
    "comment",
    "ethics_and_limitations",
    "evidence_trace",
    "score_rationales",
    "worker_id",
    "agent_version",
    "prompt_hash",
    "input_hash",
    "evidence_hash",
    "started_at",
    "completed_at",
)

REVIEW_DRAFT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://ralphthon.local/schemas/review-draft-1.0.json",
    "title": "ReviewDraft",
    "description": (
        "Canonical Track 2 draft. Contribution is the upstream score; Significance, "
        "Originality, and Comment are independent event fields and are never converted."
    ),
    "type": "object",
    "additionalProperties": False,
    "required": list(REQUIRED_FIELDS),
    "properties": {
        "review_draft_version": {"const": SCHEMA_VERSION},
        "paper_id": {"type": "string", "minLength": 1},
        "lease_id": {"type": "string", "minLength": 1},
        "summary": {"type": "string", "minLength": 1},
        "strengths": {
            "type": "array",
            "minItems": 1,
            "items": {"$ref": "#/$defs/evidenceClaim"},
        },
        "weaknesses": {
            "type": "array",
            "minItems": 1,
            "items": {"$ref": "#/$defs/evidenceClaim"},
        },
        "questions": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
        "soundness": {"type": "integer", "minimum": 1, "maximum": 4},
        "presentation": {"type": "integer", "minimum": 1, "maximum": 4},
        "contribution": {
            "type": "integer",
            "minimum": 1,
            "maximum": 4,
            "description": "Upstream Contribution score; never derived from another field.",
        },
        "significance": {
            "type": "integer",
            "minimum": 1,
            "maximum": 4,
            "description": "Event Significance score; never derived from Contribution.",
        },
        "originality": {
            "type": "integer",
            "minimum": 1,
            "maximum": 4,
            "description": "Event Originality score; never derived from Contribution.",
        },
        "overall_recommendation": {"type": "integer", "minimum": 1, "maximum": 6},
        "confidence": {"type": "integer", "minimum": 1, "maximum": 5},
        "comment": {"type": "string", "minLength": 1},
        "ethics_and_limitations": {"type": "string", "minLength": 1},
        "evidence_trace": {
            "type": "array",
            "minItems": 1,
            "items": {"$ref": "#/$defs/evidenceClaim"},
        },
        "score_rationales": {
            "type": "object",
            "additionalProperties": False,
            "required": list(SCORE_RANGES),
            "properties": {
                name: {"$ref": "#/$defs/evidenceClaim"} for name in SCORE_RANGES
            },
        },
        "worker_id": {"type": "string", "minLength": 1},
        "agent_version": {"type": "string", "minLength": 1},
        "prompt_hash": {"$ref": "#/$defs/sha256"},
        "input_hash": {"$ref": "#/$defs/sha256"},
        "evidence_hash": {"$ref": "#/$defs/sha256"},
        "started_at": {"type": "string", "format": "date-time"},
        "completed_at": {"type": "string", "format": "date-time"},
    },
    "$defs": {
        "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
        "evidenceClaim": {
            "type": "object",
            "additionalProperties": False,
            "required": ["claim", "location"],
            "properties": {
                "claim": {"type": "string", "minLength": 1},
                "location": {"type": "string", "minLength": 1},
            },
        },
    },
}

SCHEMA_SHA256 = sha256_bytes(canonical_json_bytes(REVIEW_DRAFT_SCHEMA))


class ReviewValidationError(ValueError):
    """Raised when a ReviewDraft violates the canonical contract."""

    def __init__(self, errors: Sequence[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _check_text(name: str, value: Any, errors: list[str]) -> None:
    if not _nonempty_string(value):
        errors.append(f"{name}: expected non-empty string")
    elif PLACEHOLDER.search(value):
        errors.append(f"{name}: placeholder text is forbidden")


def _check_timestamp(name: str, value: Any, errors: list[str]) -> datetime | None:
    if not _nonempty_string(value):
        errors.append(f"{name}: expected ISO-8601 timestamp")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{name}: invalid ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{name}: timezone is required")
        return None
    return parsed


def _check_evidence_claim(name: str, value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append(f"{name}: expected object")
        return
    unknown = sorted(set(value) - {"claim", "location"})
    if unknown:
        errors.append(f"{name}: unexpected fields {unknown}")
    _check_text(f"{name}.claim", value.get("claim"), errors)
    location = value.get("location")
    _check_text(f"{name}.location", location, errors)
    if _nonempty_string(location) and not EVIDENCE_LOCATION.search(location):
        errors.append(f"{name}.location: expected page, section, table, figure, appendix, or saved result")


def _check_evidence_list(name: str, value: Any, errors: list[str], *, allow_empty: bool) -> None:
    if not isinstance(value, list):
        errors.append(f"{name}: expected array")
        return
    if not allow_empty and not value:
        errors.append(f"{name}: expected at least one evidence claim")
    for index, entry in enumerate(value):
        _check_evidence_claim(f"{name}[{index}]", entry, errors)


def validate_review(
    review: Mapping[str, Any],
    manifest: Mapping[str, Any] | None = None,
    *,
    expected_lease_id: str | None = None,
) -> list[str]:
    """Return all deterministic contract violations without mutating the draft."""

    errors: list[str] = []
    if not isinstance(review, Mapping):
        return ["review: expected object"]

    missing = [field for field in REQUIRED_FIELDS if field not in review]
    if missing:
        errors.append(f"review: missing required fields {missing}")
    unknown = sorted(set(review) - set(REQUIRED_FIELDS))
    if unknown:
        errors.append(f"review: unexpected fields {unknown}")

    if review.get("review_draft_version") != SCHEMA_VERSION:
        errors.append(f"review_draft_version: expected {SCHEMA_VERSION!r}")

    for field in ("paper_id", "lease_id", "summary", "comment", "ethics_and_limitations", "worker_id", "agent_version"):
        _check_text(field, review.get(field), errors)

    for name, (minimum, maximum) in SCORE_RANGES.items():
        value = review.get(name)
        if isinstance(value, bool) or not isinstance(value, int):
            errors.append(f"{name}: expected integer")
        elif not minimum <= value <= maximum:
            errors.append(f"{name}: expected {minimum}..{maximum}")

    _check_evidence_list("strengths", review.get("strengths"), errors, allow_empty=False)
    _check_evidence_list("weaknesses", review.get("weaknesses"), errors, allow_empty=False)
    _check_evidence_list("evidence_trace", review.get("evidence_trace"), errors, allow_empty=False)

    questions = review.get("questions")
    if not isinstance(questions, list):
        errors.append("questions: expected array")
    else:
        for index, question in enumerate(questions):
            _check_text(f"questions[{index}]", question, errors)

    rationales = review.get("score_rationales")
    if not isinstance(rationales, Mapping):
        errors.append("score_rationales: expected object")
    else:
        missing_rationales = sorted(set(SCORE_RANGES) - set(rationales))
        unknown_rationales = sorted(set(rationales) - set(SCORE_RANGES))
        if missing_rationales:
            errors.append(f"score_rationales: missing {missing_rationales}")
        if unknown_rationales:
            errors.append(f"score_rationales: unexpected {unknown_rationales}")
        for name in SCORE_RANGES:
            if name in rationales:
                _check_evidence_claim(f"score_rationales.{name}", rationales[name], errors)

    for field in ("prompt_hash", "input_hash", "evidence_hash"):
        value = review.get(field)
        if not isinstance(value, str) or not HEX_256.fullmatch(value):
            errors.append(f"{field}: expected lowercase SHA-256")

    started = _check_timestamp("started_at", review.get("started_at"), errors)
    completed = _check_timestamp("completed_at", review.get("completed_at"), errors)
    if started is not None and completed is not None and completed < started:
        errors.append("completed_at: precedes started_at")

    if manifest is not None:
        expected = {
            "paper_id": manifest.get("paper_id"),
            "input_hash": manifest.get("input_hash"),
            "evidence_hash": manifest.get("evidence_hash"),
            "prompt_hash": manifest.get("prompt_hash"),
            "agent_version": manifest.get("agent_version"),
        }
        for field, value in expected.items():
            if value is not None and review.get(field) != value:
                errors.append(f"{field}: does not match frozen manifest")

    if expected_lease_id is not None and review.get("lease_id") != expected_lease_id:
        errors.append("lease_id: does not match active Root lease")

    return errors


def require_valid_review(review: Mapping[str, Any], manifest: Mapping[str, Any] | None = None) -> None:
    errors = validate_review(review, manifest)
    if errors:
        raise ReviewValidationError(errors)
