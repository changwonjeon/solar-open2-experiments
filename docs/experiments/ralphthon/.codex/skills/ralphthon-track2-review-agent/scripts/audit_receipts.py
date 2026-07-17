#!/usr/bin/env python3
"""Audit assigned papers against posted_verified ledger evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _bootstrap import bootstrap_source

bootstrap_source()

from ralphthon_track2_review_agent.ledger import audit_ledger  # noqa: E402


def _assigned_ids(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as handle:
        value: Any = json.load(handle)
    if isinstance(value, dict):
        value = value.get("papers", value.get("assigned_ids"))
    if not isinstance(value, list):
        raise ValueError("assigned file must contain a list or a papers/assigned_ids list")
    result: list[str] = []
    for item in value:
        paper_id = item.get("paper_id") if isinstance(item, dict) else item
        if not isinstance(paper_id, str) or not paper_id:
            raise ValueError("each assigned entry must provide a non-empty paper_id")
        result.append(paper_id)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--assigned", type=Path)
    parser.add_argument("--assigned-id", action="append", default=[])
    args = parser.parse_args(argv)

    assigned = list(args.assigned_id)
    if args.assigned:
        assigned.extend(_assigned_ids(args.assigned))
    result = audit_ledger(args.ledger, assigned or None)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
