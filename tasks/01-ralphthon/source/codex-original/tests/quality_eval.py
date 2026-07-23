"""Deterministic evaluator for the frozen synthetic review-quality fixture."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def normalize_locator(locator: str) -> str:
    return " ".join(locator.strip().lower().split())


def finding_key(finding: dict[str, Any]) -> tuple[str, str, str]:
    return (
        finding["paper_id"],
        finding["finding_type"],
        normalize_locator(finding["locator"]),
    )


def evaluate(
    predictions: list[dict[str, Any]],
    gold: list[dict[str, Any]],
    *,
    paper_count: int = 10,
) -> dict[str, float | int]:
    available: dict[tuple[str, str, str], int] = defaultdict(int)
    for finding in gold:
        available[finding_key(finding)] += 1

    true_positives = 0
    covered_papers: set[str] = set()
    for prediction in predictions:
        key = finding_key(prediction)
        if available[key] > 0:
            available[key] -= 1
            true_positives += 1
            covered_papers.add(prediction["paper_id"])

    false_positives = len(predictions) - true_positives
    false_negatives = len(gold) - true_positives
    precision = true_positives / len(predictions) if predictions else 0.0
    recall = true_positives / len(gold) if gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "tp": true_positives,
        "fp": false_positives,
        "fn": false_negatives,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "paper_coverage": len(covered_papers) / paper_count if paper_count else 0.0,
        "location_accuracy": true_positives / len(predictions) if predictions else 0.0,
    }


def passes_threshold(metrics: dict[str, float | int], baseline_f1: float) -> bool:
    return all(
        (
            metrics["precision"] >= 0.80,
            metrics["recall"] >= 0.80,
            metrics["f1"] >= 0.80,
            metrics["paper_coverage"] == 1.0,
            metrics["location_accuracy"] >= 0.80,
            metrics["f1"] - baseline_f1 >= 0.10,
        )
    )


def predictions_from_outbox(outbox: Path) -> list[dict[str, str]]:
    predictions: list[dict[str, str]] = []
    for review_path in sorted(outbox.glob("*.json")):
        review = json.loads(review_path.read_text(encoding="utf-8"))
        for field, finding_type in (("strengths", "strength"), ("weaknesses", "weakness")):
            for finding in review.get(field, []):
                predictions.append(
                    {
                        "paper_id": review["paper_id"],
                        "finding_type": finding_type,
                        "locator": finding["location"],
                        "text": finding["claim"],
                    }
                )
    return predictions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument(
        "--predictions-format",
        choices=("findings", "outbox"),
        default="findings",
    )
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-pass", action="store_true")
    arguments = parser.parse_args()

    predictions_document = (
        json.loads(arguments.predictions.read_text(encoding="utf-8"))
        if arguments.predictions_format == "findings"
        else None
    )
    gold_document = json.loads(arguments.gold.read_text(encoding="utf-8"))
    baseline_document = json.loads(arguments.baseline.read_text(encoding="utf-8"))
    if arguments.predictions_format == "outbox":
        predictions = predictions_from_outbox(arguments.predictions)
    else:
        predictions = (
            predictions_document.get("predictions", predictions_document)
            if isinstance(predictions_document, dict)
            else predictions_document
        )
    gold = (
        gold_document.get("findings", gold_document)
        if isinstance(gold_document, dict)
        else gold_document
    )
    baseline_metrics = evaluate(baseline_document["predictions"], gold)
    metrics = evaluate(predictions, gold)
    result = {
        "metrics": metrics,
        "baseline_metrics": baseline_metrics,
        "threshold_passed": passes_threshold(metrics, float(baseline_metrics["f1"])),
        "warning": "Synthetic seeded-fixture evaluation; not live-platform quality.",
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 1 if arguments.require_pass and not result["threshold_passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
