"""Scorer for Ralphthon spelling evaluation results."""

import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


def levenshtein_distance(a: str, b: str) -> int:
    """Compute Levenshtein (edit) distance between two strings."""
    if len(a) < len(b):
        return levenshtein_distance(b, a)
    if len(b) == 0:
        return len(a)
    prev_row = range(len(b) + 1)
    for i, ca in enumerate(a):
        curr_row = [i + 1]
        for j, cb in enumerate(b):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (ca != cb)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]


def wilson_ci(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    """Compute Wilson score 95% confidence interval."""
    if trials == 0:
        return (0.0, 0.0)
    p_hat = successes / trials
    denominator = 1 + z**2 / trials
    center = (p_hat + z**2 / (2 * trials)) / denominator
    spread = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * trials)) / trials) / denominator
    return (max(0.0, center - spread), min(1.0, center + spread))


def score_case(response: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    """Score a single probe response against its case definition."""
    result = {
        "case_id": case["case_id"],
        "condition": case["condition"],
        "response_spelling": None,
        "exact_match": False,
        "case_sensitive_match": False,
        "levenshtein_distance": None,
        "error_type": None,
        "is_error_allowed": case.get("error_types_allowed", False),
    }

    # Extract model spelling from response
    model_spelling = _extract_spelling(response)
    if model_spelling is None:
        result["error_type"] = "no_spelling_found"
        return result

    result["response_spelling"] = model_spelling
    canonical = case["canonical"]
    canonical_lower = canonical.lower()

    # Exact match
    result["exact_match"] = model_spelling == canonical

    # Case-sensitive check
    result["case_sensitive_match"] = model_spelling == canonical

    # Levenshtein distance
    result["levenshtein_distance"] = levenshtein_distance(model_spelling, canonical)

    # Error classification
    if not result["exact_match"] and not result["is_error_allowed"]:
        result["error_type"] = _classify_error(model_spelling, canonical)

    return result


def _extract_spelling(response: dict[str, Any]) -> str | None:
    """Extract the model's spelling of the target word from a response."""
    # Check for direct spelling field
    if "response_spelling" in response:
        val = response["response_spelling"]
        if isinstance(val, str) and val.strip():
            return val.strip()
    # Check text field
    if "text" in response:
        text = response["text"]
        if isinstance(text, str):
            # Look for Ralphthon or variant patterns
            for variant in ["Ralphthon", "ralpthon", "Ralpthon", "Ralphathon", "Ralph-thon"]:
                if variant.lower() in text.lower():
                    # Extract the closest match
                    idx = text.lower().find(variant.lower())
                    end = idx + len(variant)
                    return text[idx:end]
    # Check raw_response
    if "raw_response" in response:
        raw = response["raw_response"]
        if isinstance(raw, str):
            for variant in ["Ralphthon", "ralpthon", "Ralpthon", "Ralphathon", "Ralph-thon"]:
                if variant.lower() in raw.lower():
                    idx = raw.lower().find(variant.lower())
                    end = idx + len(variant)
                    return raw[idx:end]
    return None


def _classify_error(model_spelling: str, canonical: str) -> str:
    """Classify the type of spelling error."""
    if model_spelling == canonical.swapcase() or model_spelling == canonical.lower():
        if model_spelling != canonical:
            return "case_error"
    if model_spelling == "ralpthon":
        return "deletion_error"  # missing 'h'
    if model_spelling == "Ralpthon":
        return "deletion_error"  # missing 'h'
    if model_spelling == "Ralphathon":
        return "insertion_error"  # extra 'a'
    if model_spelling == "Ralph-thon":
        return "substitution_error"  # hyphen instead of concatenation
    ld = levenshtein_distance(model_spelling, canonical)
    if ld == 1:
        return "single_edit_error"
    if ld > 1:
        return f"multi_edit_error(ld={ld})"
    return "unknown_error"


def score_all(
    probe_results: list[dict],
    cases: list[dict],
    cases_by_id: dict[str, dict],
) -> dict[str, Any]:
    """Score all probe results and return aggregated summary."""
    scored = []
    for response in probe_results:
        case_id = response.get("case_id")
        if case_id and case_id in cases_by_id:
            case = cases_by_id[case_id]
            scored_result = score_case(response, case)
            scored.append(scored_result)
        else:
            # Response without matching case — score what we can
            scored_result = {
                "case_id": case_id or "unknown",
                "condition": response.get("condition", "unknown"),
                "response_spelling": _extract_spelling(response),
                "exact_match": False,
                "case_sensitive_match": False,
                "levenshtein_distance": None,
                "error_type": "no_matching_case",
                "is_error_allowed": False,
            }
            scored.append(scored_result)

    # Aggregate by condition
    by_condition = _aggregate_by_condition(scored, cases)

    # Compute generation spelling distribution
    spelling_distribution = _compute_spelling_distribution(scored)

    # Compute summary statistics
    summary = {
        "total_scored": len(scored),
        "exact_matches": sum(1 for s in scored if s["exact_match"]),
        "case_sensitive_matches": sum(1 for s in scored if s["case_sensitive_match"]),
        "by_condition": by_condition,
        "spelling_distribution": spelling_distribution,
        "error_type_distribution": _compute_error_distribution(scored),
    }

    return {
        "scored_results": scored,
        "summary": summary,
    }


def _aggregate_by_condition(
    scored: list[dict],
    cases: list[dict],
) -> dict[str, dict]:
    """Aggregate scores by experimental condition."""
    conditions = {}
    for case in cases:
        cond = case["condition"]
        if cond not in conditions:
            conditions[cond] = {
                "condition": cond,
                "total": 0,
                "exact_matches": 0,
                "case_sensitive_matches": 0,
                "avg_levenshtein": 0.0,
                "error_count": 0,
                "wilson_95_ci": (0.0, 0.0),
            }

    ld_values = {c["condition"]: [] for c in cases}
    for s in scored:
        cond = s["condition"]
        if cond in conditions:
            conditions[cond]["total"] += 1
            if s["exact_match"]:
                conditions[cond]["exact_matches"] += 1
            if s["case_sensitive_match"]:
                conditions[cond]["case_sensitive_matches"] += 1
            if s["levenshtein_distance"] is not None:
                ld_values[cond].append(s["levenshtein_distance"])
            if s["error_type"] and s["error_type"] not in ("", None):
                conditions[cond]["error_count"] += 1

    for cond, data in conditions.items():
        if data["total"] > 0:
            data["wilson_95_ci"] = wilson_ci(data["exact_matches"], data["total"])
        if ld_values[cond]:
            data["avg_levenshtein"] = sum(ld_values[cond]) / len(ld_values[cond])

    return conditions


def _compute_spelling_distribution(scored: list[dict]) -> dict[str, int]:
    """Compute frequency distribution of generated spellings."""
    counter: Counter = Counter()
    for s in scored:
        if s["response_spelling"]:
            counter[s["response_spelling"]] += 1
    return dict(counter)


def _compute_error_distribution(scored: list[dict]) -> dict[str, int]:
    """Compute frequency distribution of error types."""
    counter: Counter = Counter()
    for s in scored:
        if s["error_type"]:
            counter[s["error_type"]] += 1
    return dict(counter)


def write_csv(
    scored: list[dict],
    output_path: Path,
) -> None:
    """Write scored results to CSV."""
    if not scored:
        return
    fieldnames = [
        "case_id",
        "condition",
        "response_spelling",
        "exact_match",
        "case_sensitive_match",
        "levenshtein_distance",
        "error_type",
        "is_error_allowed",
    ]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in scored:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def write_json(
    summary_data: dict,
    output_path: Path,
) -> None:
    """Write full summary to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)


def score_deterministic(
    raw_responses: list[dict],
    cases: list[dict],
) -> dict:
    """Score raw responses deterministically — same input produces byte-identical output."""
    cases_by_id = {c["case_id"]: c for c in cases}

    probe_results = []
    for raw in raw_responses:
        # Normalize response structure
        response = {
            "case_id": raw.get("case_id"),
            "condition": raw.get("condition"),
            "prompt": raw.get("prompt"),
            "canonical": raw.get("canonical"),
            "answer_type": raw.get("answer_type"),
            "text": raw.get("text", raw.get("response", raw.get("content", ""))),
            "raw_response": json.dumps(raw, ensure_ascii=False),
        }
        probe_results.append(response)

    scored_data = score_all(probe_results, cases, cases_by_id)

    # Add provenance
    scored_data["provenance"] = {
        "scorer_version": "1.0.0",
        "canonical_spelling": "Ralphthon",
        "canonical_slug": "ralphthon",
        "num_cases": len(cases),
        "num_scored": len(probe_results),
    }

    return scored_data
