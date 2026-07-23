"""Command-line entry point for the bounded Track 2 mock runtime."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .calibration import (
    CalibrationGateSnapshot,
    CalibrationPolicy,
    MockVerifier,
)
from .runtime import (
    ControlledProcessInterruption,
    LiveAdapterUnavailable,
    Mode,
    load_papers,
    run_batch,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=[mode.value for mode in Mode], default=Mode.DRY_RUN.value)
    parser.add_argument("--papers", required=True, help="JSON corpus or papers array")
    parser.add_argument("--output-dir", required=True, help="run evidence directory")
    parser.add_argument("--workers", type=int, default=3, help="bounded worker count (1..3)")
    parser.add_argument("--failure-plan", help="optional deterministic fault-injection JSON")
    parser.add_argument("--root-dir", default=".", help="base for relative paper/evidence paths")
    parser.add_argument(
        "--calibration",
        choices=("off", "mock"),
        default="off",
        help="explicit DRY-RUN verifier adapter; default preserves the fast path",
    )
    parser.add_argument(
        "--calibration-plan",
        help="JSON risk signals and verifier scripts required by --calibration mock",
    )
    parser.add_argument("--fast-mode", action="store_true", help="bypass calibration")
    parser.add_argument("--emergency-mode", action="store_true", help="bypass calibration")
    return parser


def _load_object(path: str, label: str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    return payload


def _calibration_components(
    args: argparse.Namespace,
    failure_plan: dict[str, Any],
) -> tuple[
    MockVerifier | None,
    Mapping[str, Mapping[str, Any]] | None,
    CalibrationPolicy | None,
    CalibrationGateSnapshot | None,
]:
    if args.calibration == "off":
        if args.calibration_plan or args.fast_mode or args.emergency_mode:
            raise ValueError(
                "calibration plan and mode flags require --calibration mock"
            )
        return None, None, None, None
    if args.mode != Mode.DRY_RUN.value:
        raise ValueError("--calibration mock is available only in DRY-RUN")
    if not args.calibration_plan:
        raise ValueError("--calibration mock requires --calibration-plan")

    plan = _load_object(args.calibration_plan, "calibration plan")
    allowed = {"risk_signals", "verifier_results", "gate", "repair_values"}
    unknown = sorted(set(plan) - allowed)
    if unknown:
        raise ValueError(f"unknown calibration plan fields: {unknown}")
    risk_signals = plan.get("risk_signals", {})
    verifier_results = plan.get("verifier_results", {})
    gate_payload = plan.get("gate")
    repair_values = plan.get("repair_values", {})
    for label, value in (
        ("risk_signals", risk_signals),
        ("verifier_results", verifier_results),
        ("repair_values", repair_values),
    ):
        if not isinstance(value, dict):
            raise ValueError(f"calibration plan {label} must be an object")
    if repair_values:
        failure_plan["calibration_repair_values"] = repair_values
    gate = None
    if gate_payload is not None:
        if not isinstance(gate_payload, dict):
            raise ValueError("calibration plan gate must be an object")
        gate = CalibrationGateSnapshot(**gate_payload)
    return (
        MockVerifier(verifier_results),
        risk_signals,
        CalibrationPolicy(
            fast_mode=args.fast_mode,
            emergency_mode=args.emergency_mode,
        ),
        gate,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    failure_plan = {}
    if args.failure_plan:
        failure_plan = _load_object(args.failure_plan, "failure plan")
    try:
        verifier, risk_signals, calibration_policy, calibration_gate = (
            _calibration_components(args, failure_plan)
        )
        summary = run_batch(
            load_papers(args.papers),
            args.output_dir,
            mode=args.mode,
            workers=args.workers,
            failure_plan=failure_plan,
            root_dir=args.root_dir,
            verifier=verifier,
            risk_signals=risk_signals,
            calibration_policy=calibration_policy,
            calibration_gate=calibration_gate,
        )
    except ControlledProcessInterruption as exc:
        print(
            json.dumps(
                {
                    "success": False,
                    "interrupted": True,
                    "mode": Mode.DRY_RUN.value,
                    "posted_verified": exc.posted_verified,
                    "error": str(exc),
                },
                sort_keys=True,
            )
        )
        return exc.exit_code
    except LiveAdapterUnavailable as exc:
        print(json.dumps({"success": False, "error": str(exc)}, sort_keys=True))
        return 2
    except (TypeError, ValueError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(summary.to_dict(), sort_keys=True))
    return 0 if summary.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
