from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ralphthon_track2_review_agent.contract import (  # noqa: E402
    REVIEW_DRAFT_SCHEMA,
    SCHEMA_SHA256,
)
from ralphthon_track2_review_agent.identity import (  # noqa: E402
    CANONICAL_WORKER_PROMPT_BYTES,
    IdentityMismatchError,
    PROMPT_SHA256,
    canonical_prompt_sha256,
    canonical_schema_sha256,
)
from ralphthon_track2_review_agent.io_utils import read_json  # noqa: E402
from ralphthon_track2_review_agent.runtime import (  # noqa: E402
    AGENT_VERSION,
    PROMPT_SHA256 as RUNTIME_PROMPT_SHA256,
    load_papers,
    run_batch,
)


SKILL = ROOT / "staging/.codex/skills/ralphthon-track2-review-agent"
PROMPT = SKILL / "assets/review-worker-prompt.md"
SOURCE_PROMPT = ROOT / "src/ralphthon_track2_review_agent/assets/review-worker-prompt.md"
SCHEMA = SKILL / "assets/review-draft.schema.json"
PAPERS = ROOT / "fixtures/throughput/papers.json"


class IdentityContractTests(unittest.TestCase):
    def test_assets_are_exact_canonical_definitions(self) -> None:
        self.assertEqual(PROMPT.read_bytes(), CANONICAL_WORKER_PROMPT_BYTES + b"\n")
        self.assertEqual(SOURCE_PROMPT.read_bytes(), PROMPT.read_bytes())
        self.assertEqual(json.loads(SCHEMA.read_text(encoding="utf-8")), REVIEW_DRAFT_SCHEMA)
        self.assertEqual(canonical_prompt_sha256(PROMPT), PROMPT_SHA256)
        self.assertEqual(canonical_prompt_sha256(SOURCE_PROMPT), PROMPT_SHA256)
        self.assertEqual(canonical_schema_sha256(SCHEMA), SCHEMA_SHA256)
        self.assertEqual(RUNTIME_PROMPT_SHA256, PROMPT_SHA256)

    def test_run_batch_and_hash_inputs_freeze_identical_identities(self) -> None:
        paper = load_papers(PAPERS)[0]
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            run_output = temporary_path / "run"
            summary = run_batch([paper], run_output, root_dir=ROOT)
            self.assertTrue(summary.success, summary.to_dict())
            run_manifest = read_json(run_output / "manifests/paper-001.json")

            hash_manifest_path = temporary_path / "hash-inputs.json"
            environment = dict(os.environ)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            environment["PYTHONPATH"] = str(ROOT / "src")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL / "scripts/hash_inputs.py"),
                    "--paper-id",
                    "paper-001",
                    "--paper",
                    str(ROOT / paper["paper_path"]),
                    "--evidence",
                    str(ROOT / paper["evidence_paths"][0]),
                    "--output",
                    str(hash_manifest_path),
                    "--agent-version",
                    AGENT_VERSION,
                    "--prompt",
                    str(PROMPT),
                    "--schema",
                    str(SCHEMA),
                ],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            hash_manifest = read_json(hash_manifest_path)
            self.assertEqual(run_manifest["prompt_hash"], PROMPT_SHA256)
            self.assertEqual(hash_manifest["prompt_hash"], PROMPT_SHA256)
            self.assertEqual(run_manifest["schema_hash"], SCHEMA_SHA256)
            self.assertEqual(hash_manifest["schema_hash"], SCHEMA_SHA256)

    def test_identity_helpers_reject_definition_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            prompt = temporary_path / "prompt.md"
            prompt.write_bytes(CANONICAL_WORKER_PROMPT_BYTES + b"changed\n")
            with self.assertRaises(IdentityMismatchError):
                canonical_prompt_sha256(prompt)

            schema = temporary_path / "schema.json"
            changed = dict(REVIEW_DRAFT_SCHEMA)
            changed["title"] = "ChangedReviewDraft"
            schema.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(IdentityMismatchError):
                canonical_schema_sha256(schema)


if __name__ == "__main__":
    unittest.main()
