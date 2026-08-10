#!/usr/bin/env python3
"""Summarize paired direct-versus-delegated experiment records."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REQUIRED = {
    "run_id",
    "task_class",
    "route",
    "quality_pass",
    "timed_out",
    "actionable_findings",
    "false_positives",
    "stale_claims",
    "files_read",
    "duplicate_files",
    "commands",
}
OPTIONAL_METRICS = (
    "wall_ms",
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "main_context_chars",
)
COUNT_FIELDS = (
    "actionable_findings",
    "false_positives",
    "stale_claims",
    "files_read",
    "duplicate_files",
    "commands",
)


class ExperimentError(ValueError):
    """Raised when an experiment record is invalid."""


def _number(value: Any, field: str, *, nullable: bool = False) -> float | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ExperimentError(f"{field} must be a non-negative number")
    return float(value)


def load_record(path: Path) -> dict[str, Any]:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExperimentError(f"cannot read {path}: {exc}") from exc
    if not isinstance(record, dict):
        raise ExperimentError(f"{path}: record must be an object")
    missing = sorted(REQUIRED - record.keys())
    if missing:
        raise ExperimentError(f"{path}: missing {', '.join(missing)}")
    if record["route"] not in {"baseline", "delegated"}:
        raise ExperimentError(f"{path}: route must be baseline or delegated")
    if not isinstance(record["quality_pass"], bool):
        raise ExperimentError(f"{path}: quality_pass must be boolean")
    if not isinstance(record["timed_out"], bool):
        raise ExperimentError(f"{path}: timed_out must be boolean")
    for field in ("run_id", "task_class"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise ExperimentError(f"{path}: {field} must be a non-empty string")
    for field in COUNT_FIELDS:
        _number(record[field], f"{path}:{field}")
    for field in OPTIONAL_METRICS:
        _number(record.get(field), f"{path}:{field}", nullable=True)
    record["_path"] = str(path)
    return record


def _mean(records: list[dict[str, Any]], field: str) -> float | None:
    values = [float(item[field]) for item in records if item.get(field) is not None]
    return statistics.fmean(values) if values else None


def _matched_metric(
    paired: dict[str, dict[str, list[dict[str, Any]]]], field: str
) -> tuple[float | None, float | None, list[str], list[str]]:
    baseline_values: list[float] = []
    delegated_values: list[float] = []
    matched: list[str] = []
    excluded: list[str] = []
    for task, routes in sorted(paired.items()):
        baseline = routes["baseline"]
        delegated = routes["delegated"]
        if (
            len(baseline) != len(delegated)
            or any(item.get(field) is None for item in baseline + delegated)
        ):
            excluded.append(task)
            continue
        baseline_values.extend(float(item[field]) for item in baseline)
        delegated_values.extend(float(item[field]) for item in delegated)
        matched.append(task)
    return (
        statistics.fmean(baseline_values) if baseline_values else None,
        statistics.fmean(delegated_values) if delegated_values else None,
        matched,
        excluded,
    )


def summarize(records: list[dict[str, Any]], max_ratio: float) -> dict[str, Any]:
    if not 0 < max_ratio <= 1:
        raise ExperimentError("max_ratio must be greater than 0 and at most 1")
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: {"baseline": [], "delegated": []}
    )
    for record in records:
        grouped[record["task_class"]][record["route"]].append(record)

    paired = {
        task: routes
        for task, routes in grouped.items()
        if routes["baseline"] and routes["delegated"]
    }
    if not paired:
        return {
            "status": "ok",
            "verdict": "insufficient",
            "reason": "no task_class has both baseline and delegated records",
            "records": len(records),
        }

    baseline = [item for routes in paired.values() for item in routes["baseline"]]
    delegated = [item for routes in paired.values() for item in routes["delegated"]]
    quality_base = _mean(baseline, "quality_pass") or 0.0
    quality_delegated = _mean(delegated, "quality_pass") or 0.0
    false_positives = sum(int(item["false_positives"]) for item in delegated)
    stale_claims = sum(int(item["stale_claims"]) for item in delegated)
    duplicate_files = sum(int(item["duplicate_files"]) for item in delegated)
    timeouts = sum(int(item["timed_out"]) for item in delegated)

    metric_comparison: dict[str, dict[str, Any]] = {}
    improving_metrics: list[str] = []
    for field in OPTIONAL_METRICS:
        base_value, delegated_value, matched_tasks, excluded_tasks = _matched_metric(
            paired, field
        )
        ratio = None
        if base_value not in (None, 0) and delegated_value is not None:
            ratio = delegated_value / base_value
            if field in {"wall_ms", "main_context_chars"} and ratio <= max_ratio:
                improving_metrics.append(field)
        metric_comparison[field] = {
            "baseline_mean": base_value,
            "delegated_mean": delegated_value,
            "ratio": ratio,
            "matched_task_classes": matched_tasks,
            "excluded_task_classes": excluded_tasks,
        }

    token_fields = ("input_tokens", "output_tokens")
    token_paired: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for task, routes in paired.items():
        token_paired[task] = {"baseline": [], "delegated": []}
        for route in ("baseline", "delegated"):
            for item in routes[route]:
                values = [item.get(field) for field in token_fields]
                total = None if any(value is None for value in values) else sum(values)
                token_paired[task][route].append({"total_tokens": total})
    token_base, token_delegated, matched_tasks, excluded_tasks = _matched_metric(
        token_paired, "total_tokens"
    )
    token_ratio = None
    if token_base not in (None, 0) and token_delegated is not None:
        token_ratio = token_delegated / token_base
        if token_ratio <= max_ratio:
            improving_metrics.append("total_tokens")
    metric_comparison["total_tokens"] = {
        "baseline_mean": token_base,
        "delegated_mean": token_delegated,
        "ratio": token_ratio,
        "matched_task_classes": matched_tasks,
        "excluded_task_classes": excluded_tasks,
    }

    if quality_delegated < quality_base or false_positives or timeouts:
        verdict = "reject"
        reason = "delegated quality regressed, timed out, or produced false positives"
    elif stale_claims or duplicate_files:
        verdict = "tune"
        reason = "quality held, but stale claims or duplicate retrieval require tuning"
    elif improving_metrics:
        verdict = "keep_candidate"
        reason = "quality held and at least one comparable efficiency metric improved"
    else:
        verdict = "tune"
        reason = "quality held, but comparable efficiency improvement is unproven"

    return {
        "status": "ok",
        "verdict": verdict,
        "reason": reason,
        "paired_task_classes": sorted(paired),
        "record_counts": {
            "baseline": len(baseline),
            "delegated": len(delegated),
        },
        "quality_pass_rate": {
            "baseline": quality_base,
            "delegated": quality_delegated,
        },
        "delegated_findings": sum(
            int(item["actionable_findings"]) for item in delegated
        ),
        "delegated_false_positives": false_positives,
        "delegated_stale_claims": stale_claims,
        "delegated_duplicate_files": duplicate_files,
        "delegated_timeouts": timeouts,
        "metrics": metric_comparison,
        "improving_metrics": sorted(set(improving_metrics)),
        "max_ratio": max_ratio,
    }


def self_test() -> None:
    base = {
        "run_id": "b1",
        "task_class": "audit",
        "route": "baseline",
        "quality_pass": True,
        "timed_out": False,
        "actionable_findings": 1,
        "false_positives": 0,
        "stale_claims": 0,
        "files_read": 8,
        "duplicate_files": 0,
        "commands": 6,
        "wall_ms": 100,
        "input_tokens": 1000,
        "cached_input_tokens": 0,
        "output_tokens": 200,
        "main_context_chars": 10000,
    }
    treatment = {
        **base,
        "run_id": "d1",
        "route": "delegated",
        "actionable_findings": 2,
        "files_read": 5,
        "commands": 4,
        "wall_ms": 70,
        "input_tokens": 600,
        "cached_input_tokens": 100,
        "output_tokens": 150,
        "main_context_chars": 6000,
    }
    assert summarize([base, treatment], 0.8)["verdict"] == "keep_candidate"
    assert summarize([base, {**treatment, "stale_claims": 1}], 0.8)[
        "verdict"
    ] == "tune"
    assert summarize([base, {**treatment, "false_positives": 1}], 0.8)[
        "verdict"
    ] == "reject"
    assert summarize([base, {**treatment, "duplicate_files": 1}], 0.8)[
        "verdict"
    ] == "tune"
    assert summarize(
        [base, {**treatment, "quality_pass": False, "timed_out": True}], 0.8
    )["verdict"] == "reject"
    disjoint = summarize(
        [
            {**base, "task_class": "a", "wall_ms": 100},
            {**treatment, "task_class": "a", "wall_ms": None},
            {**base, "run_id": "b2", "task_class": "b", "wall_ms": None},
            {**treatment, "run_id": "d2", "task_class": "b", "wall_ms": 50},
        ],
        0.8,
    )
    assert disjoint["metrics"]["wall_ms"]["ratio"] is None
    assert disjoint["metrics"]["wall_ms"]["excluded_task_classes"] == ["a", "b"]
    assert summarize([base, treatment], 0.8)["metrics"]["total_tokens"]["ratio"] == 750 / 1200
    assert summarize([base], 0.8)["verdict"] == "insufficient"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--max-ratio", type=float, default=0.8)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.self_test:
            self_test()
            print(json.dumps({"status": "ok", "self_test": "passed"}))
            return 0
        if not args.paths:
            raise ExperimentError("provide at least one experiment JSON path")
        result = summarize([load_record(path) for path in args.paths], args.max_ratio)
    except ExperimentError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{result['verdict']}: {result['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
