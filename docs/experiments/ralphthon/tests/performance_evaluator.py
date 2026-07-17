#!/usr/bin/env python3
"""Evaluator for review quality-per-minute workflow improvements."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHONPATH = str(ROOT / "src")


def run(command: list[str], *, expected: int = 0) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = PYTHONPATH
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != expected:
        raise AssertionError(
            f"expected exit {expected}, got {result.returncode}: "
            f"{' '.join(command)}\n{result.stdout}\n{result.stderr}"
        )
    return result


def contains_all(text: str, markers: tuple[str, ...]) -> bool:
    return all(marker in text for marker in markers)


def main() -> int:
    checks: dict[str, object] = {}

    regression = run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_*.py",
        ]
    )
    test_count_match = re.search(r"Ran (\d+) tests?", regression.stderr)
    checks["regression_suite_pass"] = bool(
        test_count_match and int(test_count_match.group(1)) > 0
    )
    checks["regression_tests_run"] = (
        int(test_count_match.group(1)) if test_count_match else 0
    )

    worker_path = ROOT / ".codex/agents/track2-review-worker.toml"
    verifier_path = ROOT / ".codex/agents/track2-review-verifier.toml"
    skill_path = ROOT / ".codex/skills/ralphthon-track2-review-agent/SKILL.md"
    worker = worker_path.read_text(encoding="utf-8")
    verifier = verifier_path.read_text(encoding="utf-8")
    skill = skill_path.read_text(encoding="utf-8")

    checks["worker_native_instruction_budget_under_4kb"] = (
        worker_path.stat().st_size <= 4096
    )
    checks["worker_evidence_first_calibration"] = contains_all(
        worker,
        (
            "evidence-first calibration",
            "claim map",
            "falsification pass",
            "score anchoring",
            "consistency pass",
        ),
    )
    checks["risk_gated_verifier_fast_path"] = contains_all(
        skill,
        (
            "Risk-gated calibration",
            "confidence <= 3",
            "overall_recommendation <= 2",
            "overall_recommendation >= 5",
            "Do not send every draft",
        ),
    )
    checks["risk_gate_is_compound_and_bounded"] = contains_all(
        skill,
        (
            "risk score",
            "scoring at least 3",
            "indicators only and never sufficient by themselves",
            "min(3, ceil(assigned_count * 0.3))",
            "one verifier at a time",
            "20 seconds",
            "before T+15",
            "validated backlog is at most two",
        ),
    )
    checks["verifier_supports_draft_calibration"] = contains_all(
        verifier,
        ("draft-calibration mode", "frozen paper", "ReviewDraft", "one targeted repair"),
    )

    for relative in (
        "skills/auto-research",
        "skills/ralphthon-track2-review-agent",
        "agents",
    ):
        run(["diff", "-qr", f"staging/.codex/{relative}", f".codex/{relative}"])
    checks["installed_matches_staging"] = True

    summaries: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="track2-performance-") as temporary:
        temporary_root = Path(temporary)
        for index in range(3):
            result = run(
                [
                    sys.executable,
                    "-m",
                    "ralphthon_track2_review_agent.run_batch",
                    "--mode",
                    "DRY-RUN",
                    "--papers",
                    "fixtures/throughput/papers.json",
                    "--root-dir",
                    ".",
                    "--output-dir",
                    str(temporary_root / f"normal-{index + 1}"),
                    "--workers",
                    "3",
                ]
            )
            summaries.append(json.loads(result.stdout))

        calibration_result = run(
            [
                sys.executable,
                "-m",
                "ralphthon_track2_review_agent.run_batch",
                "--mode",
                "DRY-RUN",
                "--papers",
                "fixtures/throughput/papers.json",
                "--root-dir",
                ".",
                "--output-dir",
                str(temporary_root / "calibration-high-risk-pass"),
                "--workers",
                "3",
                "--calibration",
                "mock",
                "--calibration-plan",
                "fixtures/calibration/high-risk-pass.json",
            ]
        )
        calibration_summary = json.loads(calibration_result.stdout)

        live_output = temporary_root / "live-guard"
        run(
            [
                sys.executable,
                "-m",
                "ralphthon_track2_review_agent.run_batch",
                "--mode",
                "LIVE",
                "--papers",
                "fixtures/throughput/papers.json",
                "--root-dir",
                ".",
                "--output-dir",
                str(live_output),
            ],
            expected=2,
        )
        checks["live_guard_before_writes"] = not live_output.exists()

    checks["calibration_runtime_executed"] = (
        calibration_summary["success"] is True
        and calibration_summary["calibration_adapter"] == "mock"
        and calibration_summary["risk_scored_count"] == 10
        and 1 <= calibration_summary["verifier_selected_count"] <= 3
        and calibration_summary["verifier_selected_count"]
        == calibration_summary["verifier_pass_count"]
        and calibration_summary["verifier_cap"] == 3
        and calibration_summary["verifier_max_active"] == 1
        and calibration_summary["posted_verified"] == 10
    )

    checks["mock_30_of_30"] = sum(int(item["posted_verified"]) for item in summaries) == 30
    checks["mock_schema_30_of_30"] = sum(
        int(item["schema_valid_count"]) for item in summaries
    ) == 30
    checks["mock_duplicate_posts_zero"] = all(
        int(item["duplicate_post_attempts"]) == 0 for item in summaries
    )
    checks["mock_elapsed_seconds"] = [item["elapsed_seconds"] for item in summaries]
    checks["mock_each_run_under_one_second"] = all(
        float(item["elapsed_seconds"]) < 1.0 for item in summaries
    )

    failed = [name for name, value in checks.items() if value is False]
    result = {"passed": not failed, "failed": failed, "checks": checks}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
