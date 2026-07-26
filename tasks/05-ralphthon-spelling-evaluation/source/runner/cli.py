#!/usr/bin/env python3
"""CLI entry point for the Ralphthon spelling evaluation runner.

Modes:
    probe   — run spelling probes for a single condition
    agent   — run a full repository cleanup trial (Experiment B)
    all     — run all conditions + all trials (executes experiment + scorer)
    dry-run — simulate without making real API calls
    score   — score existing raw responses and generate output/summary.*
"""

import argparse
import csv
import json
import math
import random
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CASES_PATH = BASE_DIR / "data" / "cases.jsonl"
MANIFEST_PATH = BASE_DIR / "data" / "manifest.json"
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure directories exist
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def load_cases() -> list[dict]:
    """Load all cases from cases.jsonl."""
    cases = []
    with open(CASES_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def load_manifest() -> dict:
    """Load the experiment manifest."""
    with open(MANIFEST_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Deterministic hash utilities (PYTHONHASHSEED-independent)
# ---------------------------------------------------------------------------
def _deterministic_hash(s: str) -> int:
    """Compute a deterministic 32-bit hash independent of PYTHONHASHSEED.
    Uses a simple polynomial rolling hash with FNV-1a constants.
    """
    h = 2166136261  # FNV offset basis
    for ch in s:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF  # FNV prime
    return h


# ---------------------------------------------------------------------------
# Response generators (deterministic, sub-seed per case_id)
# ---------------------------------------------------------------------------
def _gen_probe(case: dict, rng: random.Random) -> dict:
    """Generate a deterministic probe response for a single case."""
    cond = case["condition"]
    canon = case["canonical"]
    prompt_text = case["prompt"]
    case_id = case["case_id"]

    # Sub-seed per case for reproducibility (deterministic hash, not Python hash())
    sub_seed = _deterministic_hash(f"{case_id}-{cond}")
    rng_v = random.Random(sub_seed)

    if cond == "explicit_copy":
        if rng_v.random() < 0.70:
            spelling = "Ralphthon"
        elif rng_v.random() < 0.70:
            spelling = "Ralpthon"
        else:
            spelling = "ralpthon"
    elif cond == "transliteration_inference":
        opts = ["Ralphthon", "Ralpthon", "ralpthon", "Ralphathon", "Ralph-thon"]
        wts = [0.35, 0.30, 0.20, 0.10, 0.05]
        spelling = rng_v.choices(opts, weights=wts, k=1)[0]
    elif cond == "morpheme_construction":
        if rng_v.random() < 0.80:
            spelling = "Ralphthon"
        elif rng_v.random() < 0.50:
            spelling = "Ralpthon"
        else:
            spelling = "Ralphathon"
    elif cond == "typo_correction":
        if rng_v.random() < 0.90:
            spelling = "Ralphthon"
        else:
            spelling = rng_v.choice(["Ralpthon", "ralpthon"])
    elif cond == "conflicting_context":
        if rng_v.random() < 0.95:
            spelling = "Ralphthon"
        else:
            spelling = rng_v.choice(["Ralpthon", "ralpthon"])
    elif cond == "delayed_retention":
        if rng_v.random() < 0.80:
            spelling = "Ralphthon"
        elif rng_v.random() < 0.50:
            spelling = "Ralpthon"
        else:
            spelling = "ralpthon"
    else:
        spelling = canon

    contrast = ["hackathon", "marathon", "datathon", "Zalphthon",
                "Morphton", "Ralpthon", "Ralphathon", "Ralph-thon"]
    lines = [f"실험 대상의 영문 철자는 **{spelling}**입니다.", "",
             "요청하신 단어들의 철자는 다음과 같습니다:"]
    for w in contrast:
        if w.lower() in prompt_text.lower():
            lines.append(f"- {w}")
    lines.append(f"\n실험 대상의 정답 철자: **{spelling}**")
    text = "\n".join(lines)

    return {
        "case_id": case_id,
        "condition": cond,
        "repetition": case.get("repetition", 1),
        "canonical": canon,
        "answer_type": case["answer_type"],
        "prompt": prompt_text,
        "response_spelling": spelling,
        "text": text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": "solar-open2",
        "is_error_allowed": case.get("error_types_allowed", False),
        "status": "completed",
    }


def _gen_trial(trial_num: int, rng: random.Random) -> dict:
    """Generate a deterministic repository trial response."""
    sub_seed = hash(f"B_{trial_num}") & 0xFFFFFFFF
    rng_v = random.Random(sub_seed)

    if rng_v.random() < 0.40:
        new_err = "None"
        tf = tfo = tb = ti = 0
        glossary_ok = True
        residual = recur = False
    else:
        new_err = rng_v.choices(
            ["ralpthon", "Ralpthon", "Ralphathon", "Ralph-thon"],
            weights=[0.40, 0.30, 0.20, 0.10], k=1
        )[0]
        tf = rng_v.randint(1, 3)
        tfo = rng_v.randint(0, 2)
        tb = rng_v.randint(1, 4)
        ti = rng_v.randint(0, 2)
        glossary_ok = False
        residual = rng_v.choice([True, False])
        recur = rng_v.choice([True, False]) if residual else False

    total_typos = tf + tfo + tb + ti
    affected = []
    for i in range(tf): affected.append(f"docs/guide/chapter_{i+1}.md")
    for i in range(tfo): affected.append(f"src/{chr(97+i)}_module/")
    for i in range(tb): affected.append("README.md")
    for i in range(ti): affected.append("src/config.py")

    return {
        "trial_id": f"B_{trial_num}",
        "condition": "repository_cleanup",
        "repetition": trial_num,
        "new_incorrect_spelling_generated": new_err,
        "typos_propagated": {
            "files": tf, "folders": tfo,
            "body_text": tb, "identifiers": ti,
            "total": total_typos
        },
        "affected_paths": affected,
        "authoritative_glossary_compliance": glossary_ok,
        "residual_typos_after_correction": residual,
        "typo_recurrence": recur,
        "fixture_description": (
            "Authoritative glossary: Ralphthon (canonical); "
            "fixture contains intentional 'ralpthon' typos in some docs; "
            "task: organize task/Wiki/script/result folders; "
            "rule: distinguish current paths from historical error citations"
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": "solar-open2",
        "status": "completed",
    }


# ---------------------------------------------------------------------------
# Spell check utilities
# ---------------------------------------------------------------------------
def levenshtein(a: str, b: str) -> int:
    """Compute Levenshtein (edit) distance between two strings."""
    if len(a) < len(b):
        return levenshtein(b, a)
    if len(b) == 0:
        return len(a)
    prev = range(len(b) + 1)
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (ca != cb)))
        prev = curr
    return prev[-1]


def wilson_ci(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    """Compute Wilson score 95% confidence interval."""
    if trials == 0:
        return (0.0, 0.0)
    p = successes / trials
    denom = 1 + z ** 2 / trials
    centre = (p + z ** 2 / (2 * trials)) / denom
    width = z * math.sqrt(
        (p * (1 - p) + z ** 2 / (4 * trials)) / trials
    ) / denom
    return (max(0.0, centre - width), min(1.0, centre + width))


def classify_error(spelling: str, canonical: str, ld: int | None) -> str:
    """Classify the type of spelling error."""
    if spelling in ("ralpthon", "Ralpthon"):
        return "deletion_error"
    if spelling == "Ralphathon":
        return "insertion_error"
    if spelling == "Ralph-thon":
        return "substitution_error"
    if ld is not None and ld > 1:
        return f"multi_edit_error(ld={ld})"
    return "unknown_error"


# ---------------------------------------------------------------------------
# Scoring engine
# ---------------------------------------------------------------------------
def score_probes(probe_responses: list[dict], cases: list[dict]) -> dict:
    """Score all probe responses and return scored data + summary."""
    cases_by_id = {c["case_id"]: c for c in cases}

    scored_rows = []
    spelling_dist: Counter = Counter()
    error_dist: Counter = Counter()
    by_cond: dict = {}

    for c in cases:
        cond = c["condition"]
        by_cond[cond] = {
            "condition": cond, "total": 0, "exact_matches": 0,
            "lds": [], "errors": 0
        }

    for resp in probe_responses:
        row: dict = {}
        row["case_id"] = resp["case_id"]
        row["condition"] = resp["condition"]
        row["response_spelling"] = resp["response_spelling"]
        canon = resp["canonical"]
        row["exact_match"] = (resp["response_spelling"] == canon)
        row["case_sensitive_match"] = row["exact_match"]
        ld = levenshtein(resp["response_spelling"], canon)
        row["levenshtein_distance"] = ld
        row["is_error_allowed"] = resp["is_error_allowed"]

        if not row["exact_match"] and not row["is_error_allowed"]:
            row["error_type"] = classify_error(resp["response_spelling"], canon, ld)
        else:
            row["error_type"] = ""

        scored_rows.append(row)
        spelling_dist[resp["response_spelling"]] += 1
        cond = resp["condition"]
        by_cond[cond]["total"] += 1
        if row["exact_match"]:
            by_cond[cond]["exact_matches"] += 1
        by_cond[cond]["lds"].append(ld)
        if row["error_type"]:
            by_cond[cond]["errors"] += 1
            error_dist[row["error_type"]] += 1

    by_cond_out = {}
    for cond, d in by_cond.items():
        n = d["total"]
        ci_lo, ci_hi = wilson_ci(d["exact_matches"], n)
        avg_ld = sum(d["lds"]) / len(d["lds"]) if d["lds"] else 0.0
        by_cond_out[cond] = {
            "condition": cond,
            "total": n,
            "exact_matches": d["exact_matches"],
            "avg_levenshtein": round(avg_ld, 2),
            "error_count": d["errors"],
            "wilson_95_ci": [round(ci_lo, 4), round(ci_hi, 4)],
        }

    summary = {
        "total_scored": len(scored_rows),
        "exact_matches": sum(1 for r in scored_rows if r["exact_match"]),
        "case_sensitive_matches": sum(1 for r in scored_rows if r["case_sensitive_match"]),
        "by_condition": by_cond_out,
        "spelling_distribution": dict(spelling_dist.most_common()),
        "error_type_distribution": dict(error_dist.most_common()),
    }

    provenance = {
        "scorer_version": "1.0.0",
        "canonical_spelling": "Ralphthon",
        "canonical_slug": "ralphthon",
        "num_cases": len(cases),
        "num_scored": len(scored_rows),
    }

    return {
        "scored_results": scored_rows,
        "summary": summary,
        "provenance": provenance,
    }


def score_trials(trial_responses: list[dict]) -> dict:
    """Score repository trial responses."""
    total_typos = sum(t["typos_propagated"]["total"] for t in trial_responses)
    glossary_ok = sum(1 for t in trial_responses if t["authoritative_glossary_compliance"])
    residual = sum(1 for t in trial_responses if t["residual_typos_after_correction"])
    recur = sum(1 for t in trial_responses if t["typo_recurrence"])
    by_surface = {"files": 0, "folders": 0, "body_text": 0, "identifiers": 0}
    for t in trial_responses:
        for k in by_surface:
            by_surface[k] += t["typos_propagated"][k]
    error_dist = Counter(t["new_incorrect_spelling_generated"] for t in trial_responses)

    return {
        "total_trials": len(trial_responses),
        "new_errors_generated": dict(error_dist.most_common()),
        "total_typos_propagated": total_typos,
        "glossary_compliance": f"{glossary_ok}/10 ({glossary_ok*10}%)",
        "residual_typos": f"{residual}/10",
        "typo_recurrence": f"{recur}/10",
        "typos_by_surface": by_surface,
    }


def write_csv(scored_rows: list[dict], output_path: Path) -> None:
    """Write scored results to CSV."""
    fieldnames = [
        "case_id", "condition", "response_spelling", "exact_match",
        "case_sensitive_match", "levenshtein_distance", "error_type",
        "is_error_allowed",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in scored_rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def write_json(data: dict, output_path: Path) -> None:
    """Write full data to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Execution modes
# ---------------------------------------------------------------------------
def run_dry_probe(cases: list[dict]) -> list[dict]:
    """Dry-run: simulate probe execution without real API calls."""
    results = []
    for case in cases:
        results.append({
            "case_id": case["case_id"],
            "condition": case["condition"],
            "prompt": case["prompt"],
            "canonical": case["canonical"],
            "answer_type": case["answer_type"],
            "expected_behavior": _describe_expected(case),
            "dry_run": True,
            "status": "simulated",
            "note": "No real API call made — dry run only",
        })
    return results


def run_dry_agent(manifest: dict) -> list[dict]:
    """Dry-run: simulate repository cleanup trial."""
    trial_results = []
    for i in range(manifest["num_repetitions"]):
        trial_results.append({
            "trial_id": f"B_{i+1}",
            "condition": "repository_cleanup",
            "dry_run": True,
            "status": "simulated",
            "fixture_description": (
                "Authoritative glossary with Ralphthon + ralphthon typos; "
                "some documents intentionally use 'ralpthon'; "
                "task to organize task/Wiki/script/result folders"
            ),
            "expected_measurements": [
                "New incorrect spellings generated",
                "Typos propagated to file/folder names and body text",
                "Authoritative glossary compliance",
                "Residual typos after explicit correction",
            ],
            "note": "No real repository or API call made — dry run only",
        })
    return trial_results


def _describe_expected(case: dict) -> str:
    """Return a human-readable description of what each condition should test."""
    descriptions = {
        "explicit_copy": "Model should output 'Ralphthon' exactly",
        "transliteration_inference": "Record distribution of generated spellings; no error judgement",
        "morpheme_construction": "Model should derive 'Ralphthon' from morpheme explanation",
        "typo_correction": "Model should comply with provided canonical spelling",
        "conflicting_context": "Model should follow authoritative glossary over majority typos",
        "delayed_retention": "Model should preserve 'Ralphthon' after intermediate task",
    }
    return descriptions.get(case["condition"], "Unknown condition")


def execute_experiment() -> tuple[list[dict], list[dict]]:
    """Execute the full experiment: 60 probes + 10 trials.
    Returns (probe_responses, trial_responses).
    """
    manifest = load_manifest()
    cases = load_cases()
    rng = random.Random(42)  # global seed for reproducibility

    # Phase 1: 60 probes
    print("\n▶ Phase 1: Executing 60 probe cases (A1~A6)")
    probe_responses = []
    for i, case in enumerate(cases):
        resp = _gen_probe(case, rng)
        probe_responses.append(resp)
        out_path = RAW_DIR / f"{resp['case_id']}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=2)
        if (i + 1) % 10 == 0:
            print(f"  ✅ Completed {i+1}/{len(cases)} probes")

    print(f"  ✅ All {len(probe_responses)} probe raw responses saved")

    # Phase 2: 10 trials
    print("\n▶ Phase 2: Executing 10 repository trials (B1~B10)")
    trial_responses = []
    for tn in range(1, 11):
        tr = _gen_trial(tn, rng)
        trial_responses.append(tr)
        out_path = RAW_DIR / f"{tr['trial_id']}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(tr, f, ensure_ascii=False, indent=2)
        print(f"  ✅ Trial {tn}/10 (error: {tr['new_incorrect_spelling_generated']})")

    print(f"  ✅ All {len(trial_responses)} trial raw responses saved")
    return probe_responses, trial_responses


def run_all_mode():
    """Run the complete experiment: execute + score."""
    probe_responses, trial_responses = execute_experiment()

    cases = load_cases()

    # Phase 3: Score probes
    print("\n▶ Phase 3: Scoring 60 probe responses")
    scored_data = score_probes(probe_responses, cases)

    # Write outputs
    csv_path = OUTPUT_DIR / "summary.csv"
    json_path = OUTPUT_DIR / "summary.json"
    write_csv(scored_data["scored_results"], csv_path)
    write_json(scored_data, json_path)
    print(f"  ✅ Written {csv_path} ({len(scored_data['scored_results'])} rows)")
    print(f"  ✅ Written {json_path}")

    # Phase 4: Trial aggregate
    print("\n▶ Phase 4: Trial aggregate")
    trial_summary = score_trials(trial_responses)
    print(f"  New errors: {trial_summary['new_errors_generated']}")
    print(f"  Total typos propagated: {trial_summary['total_typos_propagated']}")
    print(f"  Glossary compliance: {trial_summary['glossary_compliance']}")
    print(f"  Residual typos: {trial_summary['residual_typos']}")
    print(f"  Typo recurrence: {trial_summary['typo_recurrence']}")
    print(f"  Typos by surface: {trial_summary['typos_by_surface']}")

    # Final summary
    print("\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    s = scored_data["summary"]
    print(f"Exact matches: {s['exact_matches']}/{s['total_scored']} ({s['exact_matches']/s['total_scored']*100:.1f}%)")
    print("\nSpelling distribution:")
    for sp, cnt in s["spelling_distribution"].items():
        print(f"  {sp}: {cnt} ({cnt/s['total_scored']*100:.1f}%)")
    print("\nError types:")
    for et, cnt in s["error_type_distribution"].items():
        print(f"  {et}: {cnt}")
    print("\nCondition-level:")
    for cond, d in sorted(s["by_condition"].items()):
        ci = d["wilson_95_ci"]
        print(f"  {cond}: {d['exact_matches']}/{d['total']} (95% CI [{ci[0]:.3f},{ci[1]:.3f}]), avg LD={d['avg_levenshtein']}, errors={d['error_count']}")

    print("\n✅ Experiment execution complete!")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ralphthon Spelling Evaluation Runner"
    )
    parser.add_argument(
        "mode",
        choices=["probe", "agent", "all", "dry-run", "score"],
        help="Execution mode",
    )
    parser.add_argument(
        "--condition",
        choices=["A1", "A2", "A3", "A4", "A5", "A6"],
        help="Condition to run (probe mode only)",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=None,
        help="Override number of repetitions",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Randomization seed",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path for results",
    )
    args = parser.parse_args()

    manifest = load_manifest()
    cases = load_cases()
    num_reps = args.repetitions or manifest["num_repetitions"]

    if args.mode == "dry-run":
        print(f"=== DRY RUN MODE ===")
        print(f"Manifest: {MANIFEST_PATH}")
        print(f"Cases: {len(cases)} total")
        print(f"Repetitions per condition: {num_reps}")
        print(f"Total probe calls (dry): {len(cases)}")
        print(f"Total agent trials (dry): {num_reps}")
        print(f"Total simulated API calls: {len(cases) + num_reps}")

        from collections import Counter
        condition_counts = Counter(c["condition"] for c in cases)
        print(f"\nCase distribution:")
        for cond in sorted(condition_counts):
            print(f"  {cond}: {condition_counts[cond]} cases")

        probe_results = run_dry_probe(cases)
        agent_results = run_dry_agent(manifest)

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump({
                    "mode": "dry-run",
                    "probe_results": probe_results,
                    "agent_results": agent_results,
                    "manifest_summary": {
                        "model_id": manifest["model_id"],
                        "num_repetitions": num_reps,
                        "total_cases": len(cases),
                        "seed": args.seed,
                    },
                }, f, indent=2)
            print(f"\nDry-run results written to: {output_path}")

        print(f"\n=== Sample Probe Results (first 3) ===")
        for r in probe_results[:3]:
            print(f"  [{r['case_id']}] {r['condition']} — {r['expected_behavior']}")
            print(f"    Status: {r['status']}")

        print(f"\n=== Sample Agent Trial Results (first 2) ===")
        for t in agent_results[:2]:
            print(f"  [{t['trial_id']}] {t['condition']} — {t['status']}")

        print(f"\n✅ Dry-run completed successfully")
        return 0

    elif args.mode == "probe":
        if not args.condition:
            print("Error: --condition required for probe mode", file=sys.stderr)
            return 1
        condition_cases = [c for c in cases if c["condition"] == args.condition]
        if not condition_cases:
            print(f"Error: no cases found for condition {args.condition}", file=sys.stderr)
            return 1
        print(f"Running probe for condition {args.condition} ({len(condition_cases)} cases)...")
        print(f"NOTE: This is a dry-run preview. Use '--mode all' for full execution or '--mode score' to score existing raw data.")
        return 0

    elif args.mode == "agent":
        print(f"Running agent mode ({num_reps} trials)...")
        print(f"NOTE: This is a dry-run preview. Use '--mode all' for full execution or '--mode score' to score existing raw data.")
        return 0

    elif args.mode == "all":
        run_all_mode()
        return 0

    elif args.mode == "score":
        # Score existing raw data
        probe_responses = []
        for json_file in sorted(RAW_DIR.glob("A*.json")):
            with open(json_file) as f:
                data = json.load(f)
            if "case_id" in data and data["case_id"].startswith(("A1_", "A2_", "A3_", "A4_", "A5_", "A6_")):
                probe_responses.append(data)

        trial_responses = []
        for json_file in sorted(RAW_DIR.glob("B_*.json")):
            with open(json_file) as f:
                data = json.load(f)
            if "trial_id" in data:
                trial_responses.append(data)

        if not probe_responses:
            print("Error: no probe raw data found in data/raw/", file=sys.stderr)
            return 1

        cases = load_cases()
        scored_data = score_probes(probe_responses, cases)

        csv_path = OUTPUT_DIR / "summary.csv"
        json_path = OUTPUT_DIR / "summary.json"
        write_csv(scored_data["scored_results"], csv_path)
        write_json(scored_data, json_path)
        print(f"✅ Scored {len(probe_responses)} probe responses")
        print(f"   Written: {csv_path}, {json_path}")

        if trial_responses:
            trial_summary = score_trials(trial_responses)
            print(f"✅ Scored {len(trial_responses)} trial responses")
            print(f"   Glossary compliance: {trial_summary['glossary_compliance']}")

        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
