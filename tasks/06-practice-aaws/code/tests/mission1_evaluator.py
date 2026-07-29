"""Deterministic Mission 1 result metrics.

This module deliberately does not call an LLM. Provider, network, and judge
failures therefore cannot be mistaken for a model-quality failure.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.evaluator import validate_schema
from app.scenario_parser import Scenario


EXPECTED_COUNTS = {
    "ajax_01_playwright_wait": 3,
    "quotes_01_pagination": 50,
    "quotes_02_tag_filter": 13,
}

REQUIRED_FIELDS = {
    "ajax_01_playwright_wait": ("year", "title", "is_best_picture"),
    "quotes_01_pagination": ("text", "author", "tags"),
    "quotes_02_tag_filter": ("text", "author", "tags"),
}

EXPECTED_AJAX_ROWS = {
    (2015, "Spotlight", True),
    (2014, "Birdman", True),
    (2013, "12 Years a Slave", True),
}


def evaluate_result(scenario: Scenario, result_path: Path) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "schema_pass": False,
        "task_completion": False,
        "record_completeness": 0.0,
        "value_accuracy": None,
        "missing_rate": 1.0,
        "duplicate_rate": 0.0,
        "filter_compliance": None,
        "page_coverage": None,
        "deterministic_pass": False,
        "failure_types": [],
    }
    if not result_path.exists():
        metrics["failure_types"] = ["persistence"]
        return metrics

    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        metrics["error"] = f"{type(exc).__name__}: {exc}"
        metrics["failure_types"] = ["persistence"]
        return metrics

    schema_pass, schema_detail = validate_schema(data, scenario.expected_schema)
    if scenario.scenario_id == "ajax_01_playwright_wait" and isinstance(data, list):
        ajax_types_pass = all(
            isinstance(row, dict)
            and isinstance(row.get("year"), int)
            and not isinstance(row.get("year"), bool)
            and isinstance(row.get("title"), str)
            and isinstance(row.get("is_best_picture"), bool)
            for row in data
        )
        if not ajax_types_pass:
            schema_pass = False
            schema_detail = (
                "스키마 검증 실패: year는 integer, title은 string, "
                "is_best_picture는 boolean이어야 함"
            )
    metrics["schema_pass"] = schema_pass
    metrics["schema_detail"] = schema_detail
    metrics["task_completion"] = isinstance(data, list)
    if not isinstance(data, list):
        metrics["failure_types"] = ["structured_output"]
        return metrics

    expected_count = EXPECTED_COUNTS.get(scenario.scenario_id)
    if expected_count:
        metrics["expected_records"] = expected_count
        metrics["record_count"] = len(data)
        metrics["record_completeness"] = min(len(data) / expected_count, 1.0)

    fields = REQUIRED_FIELDS.get(scenario.scenario_id, ())
    cells = len(data) * len(fields)
    missing = sum(
        value is None or (isinstance(value, str) and not value.strip())
        for row in data
        if isinstance(row, dict)
        for value in (row.get(field) for field in fields)
    )
    metrics["missing_rate"] = missing / cells if cells else (0.0 if not fields else 1.0)

    canonical = [
        json.dumps(row, ensure_ascii=False, sort_keys=True)
        for row in data
        if isinstance(row, dict)
    ]
    metrics["duplicate_rate"] = (
        (len(canonical) - len(set(canonical))) / len(canonical) if canonical else 0.0
    )

    if scenario.scenario_id == "quotes_02_tag_filter":
        compliant = sum(
            "inspirational" in row.get("tags", [])
            for row in data
            if isinstance(row, dict)
        )
        metrics["filter_compliance"] = compliant / len(data) if data else 0.0
    if scenario.scenario_id == "quotes_01_pagination":
        metrics["page_coverage"] = (
            min(len(data) // 10, 5) / 5 if data else 0.0
        )
    if scenario.scenario_id == "ajax_01_playwright_wait":
        actual_rows = {
            (
                int(row.get("year"))
                if str(row.get("year")).isdigit()
                else row.get("year"),
                row.get("title"),
                row.get("is_best_picture"),
            )
            for row in data
            if isinstance(row, dict)
        }
        metrics["value_accuracy"] = (
            len(actual_rows & EXPECTED_AJAX_ROWS) / len(EXPECTED_AJAX_ROWS)
        )

    # No gold fixture exists yet, so value_accuracy stays null rather than
    # presenting schema validity as content accuracy.
    content_ok = (
        metrics["record_completeness"] == 1.0
        and metrics["missing_rate"] == 0.0
        and metrics["duplicate_rate"] == 0.0
        and metrics["filter_compliance"] in (None, 1.0)
        and metrics["page_coverage"] in (None, 1.0)
        and metrics["value_accuracy"] in (None, 1.0)
    )
    metrics["deterministic_pass"] = bool(schema_pass and content_ok)
    if not schema_pass:
        metrics["failure_types"].append("structured_output")
    if not content_ok:
        metrics["failure_types"].append("content")
    return metrics
