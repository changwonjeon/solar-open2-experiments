#!/usr/bin/env python3
"""Freeze a per-paper input/evidence manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import bootstrap_source

bootstrap_source()

from ralphthon_track2_review_agent.identity import (  # noqa: E402
    canonical_prompt_sha256,
    canonical_schema_sha256,
)
from ralphthon_track2_review_agent.manifest import freeze_manifest  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--paper", required=True, type=Path)
    parser.add_argument("--evidence", action="append", default=[], type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--agent-version", required=True)
    parser.add_argument("--prompt", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    args = parser.parse_args(argv)

    manifest = freeze_manifest(
        args.output,
        paper_id=args.paper_id,
        paper_path=args.paper,
        evidence_paths=args.evidence,
        agent_version=args.agent_version,
        prompt_hash=canonical_prompt_sha256(args.prompt),
        schema_hash=canonical_schema_sha256(args.schema),
    )
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
