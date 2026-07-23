"""Persist a real two-process DRY-RUN interruption and resume proof."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ralphthon_track2_review_agent.io_utils import (  # noqa: E402
    atomic_write_bytes,
    atomic_write_json,
    sha256_bytes,
)
from ralphthon_track2_review_agent.ledger import audit_ledger  # noqa: E402
from ralphthon_track2_review_agent.runtime import load_papers  # noqa: E402


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPYCACHEPREFIX"] = "/tmp/ralphthon-pycache"
    environment["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def _artifact_hashes(run_dir: Path, paper_ids: list[str]) -> dict[str, dict[str, str]]:
    return {
        paper_id: {
            "manifest_sha256": sha256_bytes(
                (run_dir / "manifests" / f"{paper_id}.json").read_bytes()
            ),
            "outbox_sha256": sha256_bytes(
                (run_dir / "outbox" / f"{paper_id}.json").read_bytes()
            ),
        }
        for paper_id in paper_ids
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--exit-after", type=int, default=4)
    arguments = parser.parse_args()
    destination = arguments.output
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite evidence directory: {destination}")
    destination.mkdir(parents=True)

    papers_path = ROOT / "fixtures/throughput/papers.json"
    papers = load_papers(papers_path)
    assigned_ids = [paper["paper_id"] for paper in papers]
    run_dir = destination / "run"
    failure_plan_path = destination / "controlled-exit-plan.json"
    atomic_write_json(
        failure_plan_path,
        {"controlled_process_exit_after": arguments.exit_after},
    )

    base_command = [
        sys.executable,
        "-m",
        "ralphthon_track2_review_agent.run_batch",
        "--mode",
        "DRY-RUN",
        "--papers",
        str(papers_path),
        "--output-dir",
        str(run_dir),
        "--workers",
        "3",
        "--root-dir",
        str(ROOT),
    ]
    interrupted_command = [*base_command, "--failure-plan", str(failure_plan_path)]
    display_base_command = [
        "python3",
        "-m",
        "ralphthon_track2_review_agent.run_batch",
        "--mode",
        "DRY-RUN",
        "--papers",
        "fixtures/throughput/papers.json",
        "--output-dir",
        str(run_dir),
        "--workers",
        "3",
        "--root-dir",
        ".",
    ]
    display_interrupted_command = [
        *display_base_command,
        "--failure-plan",
        str(failure_plan_path),
    ]
    interrupted = _run(interrupted_command)
    atomic_write_bytes(destination / "interrupted.stdout.json", interrupted.stdout.encode("utf-8"))
    atomic_write_bytes(destination / "interrupted.stderr.log", interrupted.stderr.encode("utf-8"))
    interrupted_payload = json.loads(interrupted.stdout)

    ledger_prefix = (run_dir / "ledger.jsonl").read_bytes()
    prefix_events = [
        json.loads(line)
        for line in ledger_prefix.decode("utf-8").splitlines()
        if line.strip()
    ]
    completed_ids = sorted(
        {
            event["paper_id"]
            for event in prefix_events
            if event.get("state") == "posted_verified"
        }
    )
    artifacts_before = _artifact_hashes(run_dir, completed_ids)

    resumed = _run(base_command)
    atomic_write_bytes(destination / "resumed.stdout.json", resumed.stdout.encode("utf-8"))
    atomic_write_bytes(destination / "resumed.stderr.log", resumed.stderr.encode("utf-8"))
    resumed_payload = json.loads(resumed.stdout)
    final_ledger = (run_dir / "ledger.jsonl").read_bytes()
    artifacts_after = _artifact_hashes(run_dir, completed_ids)
    audit = audit_ledger(run_dir / "ledger.jsonl", assigned_ids)

    ledger_prefix_preserved = final_ledger.startswith(ledger_prefix)
    completed_artifacts_preserved = artifacts_before == artifacts_after
    success = bool(
        interrupted.returncode == 75
        and interrupted_payload.get("interrupted") is True
        and interrupted_payload.get("posted_verified") == arguments.exit_after
        and len(completed_ids) == arguments.exit_after
        and resumed.returncode == 0
        and resumed_payload.get("success") is True
        and resumed_payload.get("posted_verified") == len(assigned_ids)
        and resumed_payload.get("schema_valid_count") == len(assigned_ids)
        and resumed_payload.get("duplicate_post_attempts") == 0
        and resumed_payload.get("duplicate_idempotency_keys") == 0
        and audit["success"]
        and ledger_prefix_preserved
        and completed_artifacts_preserved
    )
    aggregate = {
        "evidence_kind": "actual_two_process_dry_run_resume",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "working_directory": "project root",
        "commands": {
            "interrupted_process": shlex.join(display_interrupted_command),
            "resumed_process": shlex.join(display_base_command),
        },
        "interrupted_process": {
            "exit_code": interrupted.returncode,
            "payload": interrupted_payload,
        },
        "ledger_prefix": {
            "sha256": sha256_bytes(ledger_prefix),
            "byte_count": len(ledger_prefix),
            "event_count": len(prefix_events),
            "posted_verified_count": len(completed_ids),
            "posted_verified_ids": completed_ids,
        },
        "resumed_process": {
            "exit_code": resumed.returncode,
            "summary": resumed_payload,
            "audit": audit,
        },
        "preservation": {
            "ledger_prefix_preserved": ledger_prefix_preserved,
            "completed_manifest_and_outbox_hashes_preserved": completed_artifacts_preserved,
            "before": artifacts_before,
            "after": artifacts_after,
        },
        "external_side_effects": False,
        "production_claim_or_post": False,
        "success": success,
        "warning": "Synthetic fixtures and mock adapter only; not live-platform performance.",
    }
    atomic_write_json(destination / "aggregate.json", aggregate)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
