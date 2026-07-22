"""Generate persistent synthetic runtime evidence without external side effects."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quality_eval import evaluate, passes_threshold, predictions_from_outbox  # noqa: E402
from ralphthon_track2_review_agent.io_utils import atomic_write_json, sha256_bytes  # noqa: E402
from ralphthon_track2_review_agent.ledger import audit_ledger  # noqa: E402
from ralphthon_track2_review_agent.runtime import (  # noqa: E402
    MockReviewPlatform,
    load_papers,
    run_batch,
)


def _run_record(papers: list[dict], output: Path, **options: object) -> dict:
    summary = run_batch(papers, output, root_dir=ROOT, **options)
    audit = audit_ledger(output / "ledger.jsonl", [paper["paper_id"] for paper in papers])
    return {"summary": summary.to_dict(), "audit": audit}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--process-restart-evidence",
        required=True,
        type=Path,
        help="successful aggregate from run_process_restart_evidence.py",
    )
    arguments = parser.parse_args()
    destination = arguments.output
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite evidence directory: {destination}")
    destination.mkdir(parents=True)

    papers = load_papers(ROOT / "fixtures/throughput/papers.json")
    assigned_ids = [paper["paper_id"] for paper in papers]
    normal_runs: list[dict] = []
    for run_number in range(1, 4):
        normal_runs.append(
            _run_record(papers, destination / f"normal-{run_number}", workers=3)
        )

    failure_plan = {
        "malformed_json": ["paper-001"],
        "worker_timeout": ["paper-002"],
        "claim_timeout": ["paper-003"],
        "post_timeout": ["paper-004"],
        "process_restart_after": 5,
    }
    failure_platform = MockReviewPlatform(failure_plan)
    failure_run = _run_record(
        papers,
        destination / "failure-injection",
        workers=3,
        failure_plan=failure_plan,
        platform=failure_platform,
    )
    failure_run["platform_observations"] = {
        "claim_status_checks_paper_003": failure_platform.status_checks[("claimed", "paper-003")],
        "post_status_checks_paper_004": failure_platform.status_checks[("posted", "paper-004")],
        "claim_attempts_paper_003": failure_platform.attempts[("claim_timeout", "paper-003")],
        "post_attempts_paper_004": failure_platform.attempts[("post_timeout", "paper-004")],
        "worker_attempts_paper_002": failure_platform.attempts[("worker_timeout", "paper-002")],
    }

    restart_path = destination / "process-rerun"
    restart_first = _run_record(papers, restart_path, workers=3)
    ledger_before = (restart_path / "ledger.jsonl").read_bytes()
    outbox_before = {
        path.name: path.read_bytes() for path in sorted((restart_path / "outbox").glob("*.json"))
    }
    restart_second = _run_record(papers, restart_path, workers=3)
    restart_idempotent = (
        ledger_before == (restart_path / "ledger.jsonl").read_bytes()
        and outbox_before
        == {
            path.name: path.read_bytes()
            for path in sorted((restart_path / "outbox").glob("*.json"))
        }
    )

    gold = json.loads((ROOT / "fixtures/quality/gold.json").read_text(encoding="utf-8"))["findings"]
    baseline_document = json.loads(
        (ROOT / "fixtures/quality/naive-single-pass.json").read_text(encoding="utf-8")
    )
    baseline_quality = evaluate(baseline_document["predictions"], gold)
    mock_quality = evaluate(
        predictions_from_outbox(destination / "normal-1/outbox"),
        gold,
    )
    quality_passed = passes_threshold(mock_quality, float(baseline_quality["f1"]))
    process_restart_path = arguments.process_restart_evidence
    process_restart_bytes = process_restart_path.read_bytes()
    process_restart = json.loads(process_restart_bytes)
    process_restart_link = {
        "aggregate_path": str(process_restart_path),
        "aggregate_sha256": sha256_bytes(process_restart_bytes),
        "success": process_restart.get("success") is True,
        "interrupted_exit_code": process_restart.get("interrupted_process", {}).get("exit_code"),
        "resumed_exit_code": process_restart.get("resumed_process", {}).get("exit_code"),
        "ledger_prefix_preserved": process_restart.get("preservation", {}).get(
            "ledger_prefix_preserved"
        ),
        "completed_artifacts_preserved": process_restart.get("preservation", {}).get(
            "completed_manifest_and_outbox_hashes_preserved"
        ),
    }

    aggregate = {
        "evidence_kind": "synthetic_mock_runtime_validation",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": (
            f"python3 tests/run_mock_evidence.py --output {destination} "
            f"--process-restart-evidence {process_restart_path}"
        ),
        "fixture_manifest": "fixtures/FROZEN_MANIFEST.sha256",
        "assigned_ids": assigned_ids,
        "normal_runs": normal_runs,
        "failure_injection": failure_run,
        "process_rerun": {
            "first": restart_first,
            "second": restart_second,
            "ledger_and_outbox_byte_idempotent": restart_idempotent,
        },
        "actual_process_restart": process_restart_link,
        "quality": {
            "baseline": baseline_quality,
            "mock_runtime": mock_quality,
            "threshold_passed": quality_passed,
            "threshold_note": (
                "The deterministic mock reviewer passed the frozen seeded-fixture threshold."
                if quality_passed
                else "Mock runtime quality is below the frozen candidate threshold; do not claim "
                "a quality pass without a separate blind Review Worker result."
            ),
        },
        "external_side_effects": False,
        "production_claim_or_post": False,
        "warning": "Synthetic fixtures and mock adapter only; not live-platform performance.",
    }
    atomic_write_json(destination / "aggregate.json", aggregate)

    all_normal_green = all(
        record["summary"]["success"]
        and record["summary"]["posted_verified"] == len(papers)
        and record["summary"]["schema_valid_count"] == len(papers)
        and record["summary"]["duplicate_post_attempts"] == 0
        for record in normal_runs
    )
    runtime_green = (
        all_normal_green
        and failure_run["summary"]["success"]
        and restart_first["summary"]["success"]
        and restart_second["summary"]["success"]
        and restart_idempotent
        and process_restart_link["success"]
        and process_restart_link["interrupted_exit_code"] == 75
        and process_restart_link["resumed_exit_code"] == 0
        and process_restart_link["ledger_prefix_preserved"] is True
        and process_restart_link["completed_artifacts_preserved"] is True
    )
    return 0 if runtime_green else 1


if __name__ == "__main__":
    raise SystemExit(main())
