from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from summarize_experiment import summarize  # noqa: E402


def record(*, run_id: str, route: str, task_class: str = "audit") -> dict[str, object]:
    return {
        "run_id": run_id,
        "task_class": task_class,
        "route": route,
        "quality_pass": True,
        "timed_out": False,
        "actionable_findings": 1,
        "false_positives": 0,
        "stale_claims": 0,
        "files_read": 4,
        "duplicate_files": 0,
        "commands": 2,
        "wall_ms": 100 if route == "baseline" else 70,
        "input_tokens": 1_000 if route == "baseline" else 600,
        "cached_input_tokens": 0 if route == "baseline" else 100,
        "output_tokens": 200 if route == "baseline" else 150,
        "main_context_chars": 10_000 if route == "baseline" else 6_000,
    }


class SummarizeExperimentTests(unittest.TestCase):
    def test_timeout_rejects_treatment(self) -> None:
        delegated = record(run_id="d1", route="delegated")
        delegated["quality_pass"] = False
        delegated["timed_out"] = True
        result = summarize([record(run_id="b1", route="baseline"), delegated], 0.8)
        self.assertEqual(result["verdict"], "reject")

    def test_false_positive_rejects_treatment(self) -> None:
        delegated = record(run_id="d1", route="delegated")
        delegated["false_positives"] = 1
        result = summarize([record(run_id="b1", route="baseline"), delegated], 0.8)
        self.assertEqual(result["verdict"], "reject")

    def test_duplicate_retrieval_requires_tuning(self) -> None:
        delegated = record(run_id="d1", route="delegated")
        delegated["duplicate_files"] = 1
        result = summarize([record(run_id="b1", route="baseline"), delegated], 0.8)
        self.assertEqual(result["verdict"], "tune")

    def test_disjoint_optional_telemetry_is_excluded(self) -> None:
        baseline_a = record(run_id="b1", route="baseline", task_class="a")
        delegated_a = record(run_id="d1", route="delegated", task_class="a")
        delegated_a["wall_ms"] = None
        baseline_b = record(run_id="b2", route="baseline", task_class="b")
        baseline_b["wall_ms"] = None
        delegated_b = record(run_id="d2", route="delegated", task_class="b")
        result = summarize([baseline_a, delegated_a, baseline_b, delegated_b], 0.8)
        self.assertIsNone(result["metrics"]["wall_ms"]["ratio"])
        self.assertEqual(
            result["metrics"]["wall_ms"]["excluded_task_classes"], ["a", "b"]
        )

    def test_cached_input_is_not_double_counted(self) -> None:
        result = summarize(
            [
                record(run_id="b1", route="baseline"),
                record(run_id="d1", route="delegated"),
            ],
            0.8,
        )
        self.assertAlmostEqual(result["metrics"]["total_tokens"]["ratio"], 750 / 1200)


if __name__ == "__main__":
    unittest.main()
