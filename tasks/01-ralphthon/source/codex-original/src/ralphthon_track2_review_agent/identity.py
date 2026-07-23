"""Canonical prompt and schema identity shared by every manifest producer."""

from __future__ import annotations

import json
from pathlib import Path

from .contract import REVIEW_DRAFT_SCHEMA, SCHEMA_SHA256
from .io_utils import canonical_json_bytes, sha256_bytes

CANONICAL_WORKER_PROMPT = (
    "Read only the frozen paper and evidence. Return one ReviewDraft with independent "
    "Contribution, Significance, Originality, and Comment fields. Cite locations and "
    "never perform claim, post, status, or ledger operations."
)
CANONICAL_WORKER_PROMPT_BYTES = CANONICAL_WORKER_PROMPT.encode("utf-8")
PROMPT_SHA256 = sha256_bytes(CANONICAL_WORKER_PROMPT_BYTES)


class IdentityMismatchError(ValueError):
    """Raised when a named prompt or schema is not the frozen canonical definition."""


def canonical_prompt_sha256(path: str | Path | None = None) -> str:
    """Hash the exact model prompt bytes and verify its POSIX text asset when supplied."""

    if path is not None:
        raw_asset = Path(path).read_bytes()
        expected_asset = CANONICAL_WORKER_PROMPT_BYTES + b"\n"
        if raw_asset != expected_asset:
            raise IdentityMismatchError(
                "prompt asset must equal the canonical UTF-8 prompt bytes plus one final LF"
            )
    return PROMPT_SHA256


def canonical_schema_sha256(path: str | Path | None = None) -> str:
    """Hash canonical JSON and verify a supplied schema has the exact frozen meaning."""

    if path is not None:
        with Path(path).open("r", encoding="utf-8") as handle:
            candidate = json.load(handle)
        if candidate != REVIEW_DRAFT_SCHEMA:
            raise IdentityMismatchError("schema asset differs from the canonical ReviewDraft schema")
        candidate_hash = sha256_bytes(canonical_json_bytes(candidate))
        if candidate_hash != SCHEMA_SHA256:
            raise IdentityMismatchError("schema canonical hash read-back mismatch")
    return SCHEMA_SHA256
