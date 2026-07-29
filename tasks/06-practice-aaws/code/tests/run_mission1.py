"""Repeatable role-isolation runner for Mission 1.

Run with the repository-local environment:
    ./.venv/bin/python -m tests.run_mission1 --pilot
"""

from __future__ import annotations

import argparse
import asyncio
import difflib
import hashlib
import json
import os
import shutil
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env", override=True)

from app.agents.supervisor import create_supervisor_agent
from app.scenario_parser import Scenario
from tests.mission1_evaluator import evaluate_result

GEMINI = ("google_genai:gemini-2.5-pro", None)
GEMINI_CODER = ("google_genai:gemini-flash-latest", None)
SOLAR = ("solar-open2", "upstage")
CONDITIONS = {
    "GGG": (GEMINI, GEMINI, GEMINI_CODER),
    "SSS": (SOLAR, SOLAR, SOLAR),
    "SGG": (SOLAR, GEMINI, GEMINI_CODER),
    "GSG": (GEMINI, SOLAR, GEMINI_CODER),
    "GGS": (GEMINI, GEMINI, SOLAR),
}
PROMPT_FILES = (
    ROOT / "app" / "prompts" / "supervisor.py",
    ROOT / "app" / "prompts" / "navigator.py",
    ROOT / "app" / "prompts" / "coder.py",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true", help="3 repeats (default: 5)")
    parser.add_argument("--repeats", type=int)
    parser.add_argument("--conditions", nargs="+", choices=CONDITIONS, default=list(CONDITIONS))
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=["quotes_01_pagination", "quotes_02_tag_filter"],
    )
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--site-mode", choices=["live", "fixture"], default="live")
    parser.add_argument("--experiment-phase", default="baseline")
    parser.add_argument("--round-id", default="baseline")
    parser.add_argument("--prompt-version", default="v0")
    return parser.parse_args()


def json_write(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def classify_exception(exc: BaseException) -> str:
    text = f"{type(exc).__name__}: {exc}".lower()
    if any(word in text for word in ("rate limit", "authentication", "api key", "timeout")):
        return "model_api"
    if any(word in text for word in ("connect", "network", "dns", "browser")):
        return "site_environment"
    return "orchestration"


def preserve_prompt_provenance(
    out_dir: Path, prompt_version: str
) -> dict[str, object]:
    """Save prompt snapshots, hashes, and a v0-relative diff without secrets."""
    version_root = ROOT / "artifacts" / "results" / "mission1_prompt_tuning" / "prompt_versions"
    version_dir = version_root / prompt_version
    version_dir.mkdir(parents=True, exist_ok=True)
    snapshot_dir = out_dir / "prompt_snapshot"
    snapshot_dir.mkdir()
    hashes: dict[str, str] = {}
    diff_parts: list[str] = []
    previous_parts: list[str] = []
    previous_version = (
        f"v{int(prompt_version[1:]) - 1}"
        if prompt_version.startswith("v") and prompt_version[1:].isdigit()
        else None
    )
    for source in PROMPT_FILES:
        text = source.read_text(encoding="utf-8")
        name = source.name
        (snapshot_dir / name).write_text(text, encoding="utf-8")
        version_path = version_dir / name
        if not version_path.exists():
            version_path.write_text(text, encoding="utf-8")
        hashes[f"app/prompts/{name}"] = hashlib.sha256(text.encode()).hexdigest()
        baseline_path = version_root / "v0" / name
        if baseline_path.exists():
            baseline = baseline_path.read_text(encoding="utf-8")
            diff_parts.extend(
                difflib.unified_diff(
                    baseline.splitlines(keepends=True),
                    text.splitlines(keepends=True),
                    fromfile=f"v0/{name}",
                    tofile=f"{prompt_version}/{name}",
                )
            )
        previous_path = version_root / str(previous_version) / name
        if previous_version and previous_path.exists():
            previous = previous_path.read_text(encoding="utf-8")
            previous_parts.extend(
                difflib.unified_diff(
                    previous.splitlines(keepends=True),
                    text.splitlines(keepends=True),
                    fromfile=f"{previous_version}/{name}",
                    tofile=f"{prompt_version}/{name}",
                )
            )
    (out_dir / "prompt_diff_from_v0.patch").write_text(
        "".join(diff_parts), encoding="utf-8"
    )
    if previous_version:
        previous_diff_name = f"prompt_diff_from_{previous_version}.patch"
        previous_diff = "".join(previous_parts)
        (out_dir / previous_diff_name).write_text(previous_diff, encoding="utf-8")
        (version_dir / previous_diff_name).write_text(
            previous_diff, encoding="utf-8"
        )
    json_write(
        version_dir / "manifest.json",
        {
            "prompt_version": prompt_version,
            "sha256": hashes,
            "diff_base": "v0",
            "previous_version": previous_version,
        },
    )
    return {
        "sha256": hashes,
        "diff_base": "v0",
        "previous_version": previous_version,
    }


async def stream_mission_execution(agent, prompt: str, log_path: Path):
    """Stream one run with a larger graph budget and collect basic operations."""
    metrics = {
        "model_calls": 0,
        "tool_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }
    final_message = ""
    config = {
        "configurable": {"thread_id": f"mission1_{uuid4().hex[:12]}"},
        "recursion_limit": 60,
    }
    async for event in agent.astream_events(
        {"messages": [HumanMessage(content=prompt)]},
        config=config,
        version="v2",
    ):
        kind = event["event"]
        if kind == "on_tool_start":
            metrics["tool_calls"] += 1
            name = event.get("name", "unknown")
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(f"\n[tool_start] {name}\n")
        elif kind == "on_chat_model_end":
            metrics["model_calls"] += 1
            output = event["data"].get("output")
            if output and getattr(output, "content", None):
                final_message = output.content
            usage = getattr(output, "usage_metadata", None) or {}
            for key in ("input_tokens", "output_tokens", "total_tokens"):
                metrics[key] += int(usage.get(key, 0) or 0)
    return final_message, metrics


async def run_one(
    scenario_path: Path,
    condition: str,
    repeat: int,
    timeout_s: int,
    max_retries: int,
    site_mode: str,
    experiment_phase: str,
    round_id: str,
    prompt_version: str,
) -> None:
    scenario = Scenario.from_file(str(scenario_path))
    started = datetime.now(timezone.utc)
    run_id = f"{started.strftime('%Y%m%dT%H%M%S.%fZ')}-r{repeat:02d}-{uuid4().hex[:8]}"
    out_dir = ROOT / "artifacts" / "results" / scenario.scenario_id / condition / run_id
    out_dir.mkdir(parents=True, exist_ok=False)
    result_path = out_dir / "result.json"
    log_path = out_dir / "execution.log"
    log_path.write_text("", encoding="utf-8")

    supervisor, navigator, coder = CONDITIONS[condition]
    metadata = {
        "scenario_id": scenario.scenario_id,
        "condition": condition,
        "run_id": run_id,
        "repeat": repeat,
        "model_supervisor": supervisor[0],
        "provider_supervisor": supervisor[1] or "google_genai",
        "model_navigator": navigator[0],
        "provider_navigator": navigator[1] or "google_genai",
        "model_coder": coder[0],
        "provider_coder": coder[1] or "google_genai",
        "site_mode": site_mode,
        "experiment_phase": experiment_phase,
        "round_id": round_id,
        "prompt_version": prompt_version,
        "timeout_seconds": timeout_s,
        "timeout_policy": "identical per-run timeout for every condition",
        "max_retries": max_retries,
        "retry_backoff_seconds": [5 * (2**index) for index in range(max_retries)],
        "started_at": started.isoformat(),
        "langsmith_project": os.getenv(
            "AAWS_LANGSMITH_PROJECT_UPSTAGE"
            if "S" in condition
            else "AAWS_LANGSMITH_PROJECT_GEMINI",
            "aaws-mission1-role-evaluation",
        ),
    }
    metadata["prompt_provenance"] = preserve_prompt_provenance(
        out_dir, prompt_version
    )
    json_write(out_dir / "metadata.json", metadata)
    os.environ["LANGSMITH_PROJECT"] = metadata["langsmith_project"]

    agent = create_supervisor_agent(
        model_name=supervisor[0],
        model_provider=supervisor[1],
        navigator_model_name=navigator[0],
        navigator_model_provider=navigator[1],
        coder_model_name=coder[0],
        coder_model_provider=coder[1],
        project_name=metadata["langsmith_project"],
    )
    prompt = f"""
Use Navigator first, then give its complete Blueprint to Coder. Complete the
scenario below. Save the final JSON array at exactly: {result_path}
Do not substitute another filename. Validate that exact file before finishing.

Scenario ID: {scenario.scenario_id}
Target URL: {scenario.target_url}
{scenario.prompt}
"""
    started_perf = time.perf_counter()
    failure_type = None
    retry_count = 0
    while True:
        try:
            final_message, operations = await asyncio.wait_for(
                stream_mission_execution(agent, prompt, log_path),
                timeout=timeout_s,
            )
            failure_type = None
            break
        except Exception as exc:
            failure_type = classify_exception(exc)
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(f"\n[{failure_type}] {type(exc).__name__}: {exc}\n")
                handle.write(traceback.format_exc())
            if failure_type != "model_api" or retry_count >= max_retries:
                final_message = ""
                operations = {}
                break
            delay = 5 * (2**retry_count)
            retry_count += 1
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(f"\n[retry] count={retry_count} backoff_seconds={delay}\n")
            await asyncio.sleep(delay)

    try:
        # Some generated scripts honor the scenario filename instead of the
        # explicit destination. Preserve it without overwriting another run.
        if not result_path.exists():
            candidates = [
                ROOT / "artifacts" / "code" / "quotes_5pages.json",
                ROOT / "artifacts" / "code" / "quotes_tag_inspirational.json",
            ]
            for candidate in candidates:
                if candidate.exists() and candidate.stat().st_mtime >= started.timestamp():
                    shutil.copy2(candidate, result_path)
                    break
        (out_dir / "final_message.txt").write_text(
            str(final_message), encoding="utf-8"
        )
    except Exception as exc:
        failure_type = classify_exception(exc)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"\n[{failure_type}] {type(exc).__name__}: {exc}\n")
            handle.write(traceback.format_exc())

    evaluation = evaluate_result(scenario, result_path)
    if failure_type:
        evaluation["failure_types"] = sorted(
            set(evaluation["failure_types"] + [failure_type])
        )
    elapsed = time.perf_counter() - started_perf
    evaluation["elapsed_seconds"] = round(elapsed, 3)
    evaluation["operations"] = operations
    evaluation["external_failure"] = any(
        item in {"site_environment", "model_api", "evaluator"}
        for item in evaluation["failure_types"]
    )
    json_write(out_dir / "evaluation.json", evaluation)
    metadata["finished_at"] = datetime.now(timezone.utc).isoformat()
    metadata["elapsed_seconds"] = round(elapsed, 3)
    metadata["retry_count"] = retry_count
    json_write(out_dir / "metadata.json", metadata)


async def main() -> None:
    args = parse_args()
    repeats = args.repeats or (3 if args.pilot else 5)
    for repeat in range(1, repeats + 1):
        conditions = args.conditions if repeat % 2 else list(reversed(args.conditions))
        for scenario_id in args.scenarios:
            scenario_path = ROOT / "artifacts" / "scenarios" / f"{scenario_id}.md"
            for condition in conditions:
                print(f"[Mission1] {scenario_id} {condition} repeat={repeat}")
                await run_one(
                    scenario_path,
                    condition,
                    repeat,
                    args.timeout,
                    args.retries,
                    args.site_mode,
                    args.experiment_phase,
                    args.round_id,
                    args.prompt_version,
                )


if __name__ == "__main__":
    asyncio.run(main())
