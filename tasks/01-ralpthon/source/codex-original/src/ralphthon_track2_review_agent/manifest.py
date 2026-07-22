"""Per-paper immutable input and evidence manifests."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .io_utils import atomic_write_json, canonical_json_bytes, read_json, sha256_bytes, sha256_file

MANIFEST_VERSION = "1.0"
IMMUTABLE_KEYS = (
    "manifest_version",
    "paper_id",
    "paper",
    "evidence",
    "paper_hash",
    "evidence_hash",
    "input_hash",
    "agent_version",
    "prompt_hash",
    "schema_hash",
)


class ManifestConflictError(ValueError):
    """Raised when an existing frozen manifest differs from the new identity."""


def _file_identity(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    return {
        "name": source.name,
        "sha256": sha256_file(source),
        "size_bytes": source.stat().st_size,
    }


def build_manifest(
    *,
    paper_id: str,
    paper_path: str | Path | None = None,
    paper_bytes: bytes | None = None,
    paper_name: str | None = None,
    evidence_paths: Iterable[str | Path] = (),
    agent_version: str,
    prompt_hash: str,
    schema_hash: str,
    frozen_at: str | None = None,
) -> dict[str, Any]:
    if bool(paper_path) == bool(paper_bytes is not None):
        raise ValueError("provide exactly one of paper_path or paper_bytes")
    if not paper_id.strip():
        raise ValueError("paper_id must be non-empty")

    if paper_path is not None:
        paper = _file_identity(paper_path)
    else:
        assert paper_bytes is not None
        data = paper_bytes
        paper = {
            "name": paper_name or f"{paper_id}.txt",
            "sha256": sha256_bytes(data),
            "size_bytes": len(data),
        }

    evidence = sorted(
        (_file_identity(path) for path in evidence_paths),
        key=lambda identity: (identity["name"], identity["sha256"]),
    )
    evidence_hash = sha256_bytes(canonical_json_bytes(evidence))
    input_hash = sha256_bytes(
        canonical_json_bytes(
            {
                "paper_id": paper_id,
                "paper_hash": paper["sha256"],
                "evidence_hash": evidence_hash,
            }
        )
    )
    return {
        "manifest_version": MANIFEST_VERSION,
        "paper_id": paper_id,
        "paper": paper,
        "evidence": evidence,
        "paper_hash": paper["sha256"],
        "evidence_hash": evidence_hash,
        "input_hash": input_hash,
        "agent_version": agent_version,
        "prompt_hash": prompt_hash,
        "schema_hash": schema_hash,
        "frozen_at": frozen_at or datetime.now(timezone.utc).isoformat(),
    }


def _immutable_identity(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {key: manifest.get(key) for key in IMMUTABLE_KEYS}


def freeze_manifest(output_path: str | Path, **manifest_args: Any) -> dict[str, Any]:
    """Create once, or prove that an existing manifest has the same identity."""

    destination = Path(output_path)
    candidate = build_manifest(**manifest_args)
    if destination.exists():
        existing = read_json(destination)
        if _immutable_identity(existing) != _immutable_identity(candidate):
            raise ManifestConflictError(
                f"frozen manifest conflict for {candidate['paper_id']} at {destination}"
            )
        return existing
    atomic_write_json(destination, candidate)
    persisted = read_json(destination)
    if _immutable_identity(persisted) != _immutable_identity(candidate):
        raise OSError(f"manifest read-back mismatch at {destination}")
    return persisted
