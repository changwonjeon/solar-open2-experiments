#!/usr/bin/env python3
"""Validate one canonical ReviewDraft and optional frozen manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from _bootstrap import bootstrap_source

bootstrap_source()

from ralphthon_track2_review_agent.contract import validate_review  # noqa: E402


def _read_object(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--lease-id", help="active Root lease expected in the ReviewDraft")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    review = _read_object(args.review)
    manifest = _read_object(args.manifest) if args.manifest else None
    errors = validate_review(review, manifest, expected_lease_id=args.lease_id)
    result = {"valid": not errors, "errors": errors, "review": str(args.review)}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    elif errors:
        for error in errors:
            print(error)
    else:
        print(f"valid: {args.review}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
