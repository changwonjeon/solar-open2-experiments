from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLED_SKILL = ROOT / ".codex/skills/ralphthon-track2-review-agent"
STAGED_SKILL = ROOT / "staging/.codex/skills/ralphthon-track2-review-agent"
SKILL = INSTALLED_SKILL if INSTALLED_SKILL.is_dir() else STAGED_SKILL
PAPERS = ROOT / "fixtures/throughput/papers.json"


def _run(command: list[str], **options: object) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
        **options,
    )


class CliInterfaceTests(unittest.TestCase):
    def test_source_module_cli_runs_ten_papers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "source-cli"
            result = _run(
                [
                    sys.executable,
                    "-m",
                    "ralphthon_track2_review_agent.run_batch",
                    "--mode",
                    "DRY-RUN",
                    "--papers",
                    str(PAPERS),
                    "--output-dir",
                    str(output),
                    "--workers",
                    "3",
                    "--root-dir",
                    str(ROOT),
                ]
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads(result.stdout)
            self.assertTrue(summary["success"])
            self.assertEqual(summary["posted_verified"], 10)
            self.assertEqual(summary["schema_valid_count"], 10)
            self.assertEqual(summary["duplicate_post_attempts"], 0)

    def test_source_cli_executes_explicit_mock_calibration_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "calibration-cli"
            result = _run(
                [
                    sys.executable,
                    "-m",
                    "ralphthon_track2_review_agent.run_batch",
                    "--mode",
                    "DRY-RUN",
                    "--papers",
                    str(PAPERS),
                    "--output-dir",
                    str(output),
                    "--workers",
                    "3",
                    "--root-dir",
                    str(ROOT),
                    "--calibration",
                    "mock",
                    "--calibration-plan",
                    str(ROOT / "fixtures/calibration/high-risk-pass.json"),
                ]
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads(result.stdout)
            self.assertTrue(summary["success"], summary)
            self.assertEqual(summary["calibration_adapter"], "mock")
            self.assertEqual(summary["risk_scored_count"], 10)
            self.assertGreaterEqual(summary["verifier_selected_count"], 1)
            self.assertLessEqual(summary["verifier_selected_count"], 3)
            self.assertEqual(
                summary["verifier_selected_count"],
                summary["verifier_pass_count"],
            )
            self.assertEqual(summary["verifier_max_active"], 1)

    def test_build_cli_rejects_mock_calibration_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "build-calibration"
            result = _run(
                [
                    sys.executable,
                    "-m",
                    "ralphthon_track2_review_agent.run_batch",
                    "--mode",
                    "BUILD",
                    "--papers",
                    str(PAPERS),
                    "--output-dir",
                    str(output),
                    "--root-dir",
                    str(ROOT),
                    "--calibration",
                    "mock",
                    "--calibration-plan",
                    str(ROOT / "fixtures/calibration/high-risk-pass.json"),
                ]
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertFalse(json.loads(result.stdout)["success"])
            self.assertFalse(output.exists())

    def test_controlled_exit_resumes_in_a_second_process_without_duplicate_posts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            output = temporary_path / "process-restart"
            failure_plan = temporary_path / "controlled-exit.json"
            failure_plan.write_text(
                json.dumps({"controlled_process_exit_after": 4}),
                encoding="utf-8",
            )
            base_command = [
                sys.executable,
                "-m",
                "ralphthon_track2_review_agent.run_batch",
                "--mode",
                "DRY-RUN",
                "--papers",
                str(PAPERS),
                "--output-dir",
                str(output),
                "--workers",
                "3",
                "--root-dir",
                str(ROOT),
            ]

            interrupted = _run([*base_command, "--failure-plan", str(failure_plan)])
            self.assertEqual(interrupted.returncode, 75, interrupted.stderr)
            interruption = json.loads(interrupted.stdout)
            self.assertTrue(interruption["interrupted"])
            self.assertEqual(interruption["posted_verified"], 4)

            ledger_prefix = (output / "ledger.jsonl").read_bytes()
            events = [
                json.loads(line)
                for line in ledger_prefix.decode("utf-8").splitlines()
                if line.strip()
            ]
            completed_ids = {
                event["paper_id"]
                for event in events
                if event["state"] == "posted_verified"
            }
            self.assertEqual(len(completed_ids), 4)
            outbox_before = {
                paper_id: (output / "outbox" / f"{paper_id}.json").read_bytes()
                for paper_id in completed_ids
            }
            manifests_before = {
                paper_id: (output / "manifests" / f"{paper_id}.json").read_bytes()
                for paper_id in completed_ids
            }

            resumed = _run(base_command)
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            summary = json.loads(resumed.stdout)
            self.assertTrue(summary["success"])
            self.assertEqual(summary["posted_verified"], 10)
            self.assertEqual(summary["schema_valid_count"], 10)
            self.assertEqual(summary["duplicate_post_attempts"], 0)
            self.assertEqual(summary["duplicate_idempotency_keys"], 0)
            self.assertTrue((output / "ledger.jsonl").read_bytes().startswith(ledger_prefix))
            for paper_id in completed_ids:
                self.assertEqual(
                    (output / "outbox" / f"{paper_id}.json").read_bytes(),
                    outbox_before[paper_id],
                )
                self.assertEqual(
                    (output / "manifests" / f"{paper_id}.json").read_bytes(),
                    manifests_before[paper_id],
                )

    def test_skill_run_validate_hash_and_audit_wrappers(self) -> None:
        scripts = SKILL / "scripts"
        self.assertTrue(scripts.is_dir(), SKILL)
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            output = temporary_path / "skill-cli"
            run_result = _run(
                [
                    sys.executable,
                    str(scripts / "run_batch.py"),
                    "--mode",
                    "DRY-RUN",
                    "--papers",
                    str(PAPERS),
                    "--output-dir",
                    str(output),
                    "--workers",
                    "3",
                    "--root-dir",
                    str(ROOT),
                ]
            )
            self.assertEqual(run_result.returncode, 0, run_result.stderr)
            self.assertTrue(json.loads(run_result.stdout)["success"])

            review_path = output / "outbox/paper-001.json"
            manifest_path = output / "manifests/paper-001.json"
            validate_result = _run(
                [
                    sys.executable,
                    str(scripts / "validate_review.py"),
                    str(review_path),
                    "--manifest",
                    str(manifest_path),
                    "--json",
                ]
            )
            self.assertEqual(validate_result.returncode, 0, validate_result.stderr)
            self.assertTrue(json.loads(validate_result.stdout)["valid"])

            hash_output = temporary_path / "frozen-paper-001.json"
            hash_result = _run(
                [
                    sys.executable,
                    str(scripts / "hash_inputs.py"),
                    "--paper-id",
                    "paper-001",
                    "--paper",
                    str(ROOT / "fixtures/throughput/paper-001.md"),
                    "--evidence",
                    str(ROOT / "fixtures/throughput/evidence-bundle.json"),
                    "--output",
                    str(hash_output),
                    "--agent-version",
                    "cli-test-v1",
                    "--prompt",
                    str(SKILL / "assets/review-worker-prompt.md"),
                    "--schema",
                    str(SKILL / "assets/review-draft.schema.json"),
                ]
            )
            self.assertEqual(hash_result.returncode, 0, hash_result.stderr)
            self.assertEqual(json.loads(hash_result.stdout), json.loads(hash_output.read_text()))

            audit_result = _run(
                [
                    sys.executable,
                    str(scripts / "audit_receipts.py"),
                    "--ledger",
                    str(output / "ledger.jsonl"),
                    "--assigned",
                    str(PAPERS),
                ]
            )
            self.assertEqual(audit_result.returncode, 0, audit_result.stderr)
            audit = json.loads(audit_result.stdout)
            self.assertTrue(audit["success"])
            self.assertEqual(audit["posted_verified"], 10)

    def test_malformed_json_cli_hard_fails(self) -> None:
        scripts = SKILL / "scripts"
        with tempfile.TemporaryDirectory() as temporary:
            malformed = Path(temporary) / "malformed.json"
            malformed.write_text("{malformed-json", encoding="utf-8")
            result = _run(
                [
                    sys.executable,
                    str(scripts / "validate_review.py"),
                    str(malformed),
                    "--json",
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(result.stdout.strip())

    def test_live_cli_returns_guard_error_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "live-cli"
            result = _run(
                [
                    sys.executable,
                    "-m",
                    "ralphthon_track2_review_agent.run_batch",
                    "--mode",
                    "LIVE",
                    "--papers",
                    str(PAPERS),
                    "--output-dir",
                    str(output),
                    "--root-dir",
                    str(ROOT),
                ]
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["success"])
            self.assertIn("verifies the platform adapter", payload["error"])
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
