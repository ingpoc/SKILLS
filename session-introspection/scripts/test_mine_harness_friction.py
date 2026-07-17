#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("mine_harness_friction.py")
SPEC = importlib.util.spec_from_file_location("mine_harness_friction", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_session(
    path: Path,
    *,
    cwd: str,
    records: list[dict[str, object]],
    parent_thread_id: str | None = None,
) -> None:
    payloads = [
        {
            "type": "session_meta",
            "payload": {"id": path.stem, "cwd": cwd, "parent_thread_id": parent_thread_id},
        },
        *records,
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(item) + "\n" for item in payloads), encoding="utf-8")


class MineHarnessFrictionTests(unittest.TestCase):
    def test_injected_instructions_are_not_friction_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "rollout-injected.jsonl"
            write_session(
                path,
                cwd="/target",
                records=[
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "developer",
                            "content": [{"type": "input_text", "text": "hook must block; Owner topology changed"}],
                        },
                    },
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": "workflow list then normal repo retrieval"}],
                        },
                    },
                ],
            )

            scan = MODULE.scan_session(path)
            assert scan is not None
            self.assertEqual(MODULE.classify(scan), [])

    def test_retrieved_tool_output_is_not_friction_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "rollout-tool-output.jsonl"
            write_session(
                path,
                cwd="/target",
                records=[
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "custom_tool_call_output",
                            "output": [{"type": "input_text", "text": '{"decision":"block"}'}],
                        },
                    }
                ],
            )

            scan = MODULE.scan_session(path)
            assert scan is not None
            self.assertEqual(MODULE.classify(scan), [])

    def test_assistant_report_is_friction_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "rollout-assistant-report.jsonl"
            write_session(
                path,
                cwd="/target",
                records=[
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "assistant",
                            "content": [{"type": "output_text", "text": "The pre-execution hook blocked the valid command."}],
                        },
                    }
                ],
            )

            scan = MODULE.scan_session(path)
            assert scan is not None
            self.assertEqual([item["type"] for item in MODULE.classify(scan)], ["hook_block_or_loop"])

    def test_negated_hook_summary_is_not_friction_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "rollout-negated-hook-summary.jsonl"
            write_session(
                path,
                cwd="/target",
                records=[
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": "No session was flagged for generic checkpoints, hook blocking/loops, or handoff nudges.",
                                }
                            ],
                        },
                    }
                ],
            )

            scan = MODULE.scan_session(path)
            assert scan is not None
            self.assertEqual(MODULE.classify(scan), [])

    def test_patch_payload_is_not_classified_as_executed_retrieval(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "rollout-patch.jsonl"
            patch_text = "\n".join(["rg AGENTS docs skills workflows"] * 5)
            write_session(
                path,
                cwd="/target",
                records=[
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "custom_tool_call",
                            "name": "exec",
                            "input": f'const patch = "*** Begin Patch\\n{patch_text}"; await tools.apply_patch(patch);',
                        },
                    }
                ],
            )

            scan = MODULE.scan_session(path)
            assert scan is not None
            self.assertEqual(MODULE.classify(scan), [])

    def test_retrieval_count_without_route_sequence_is_not_friction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "rollout-multiphase-audit.jsonl"
            records = []
            for index in range(5):
                records.append(
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "custom_tool_call",
                            "name": "exec",
                            "input": f"rg -n owner-{index} docs/workflows skill-{index}",
                        },
                    }
                )
            write_session(path, cwd="/target", records=records)

            scan = MODULE.scan_session(path)
            assert scan is not None
            self.assertEqual(MODULE.classify(scan), [])

    def test_retrieval_after_known_route_is_friction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "rollout-route-miss.jsonl"
            write_session(
                path,
                cwd="/target",
                records=[
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "assistant",
                            "content": [{"type": "output_text", "text": "The route_contract is already authoritative."}],
                        },
                    },
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "custom_tool_call",
                            "name": "exec",
                            "input": "workflow list && workflow search owner",
                        },
                    },
                ],
            )

            scan = MODULE.scan_session(path)
            assert scan is not None
            self.assertEqual(
                [item["type"] for item in MODULE.classify(scan)],
                ["broad_retrieval_before_known_route"],
            )

    def test_limit_is_applied_after_cwd_filter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "older" / "rollout-target.jsonl"
            other = root / "newer" / "rollout-other.jsonl"
            write_session(target, cwd="/target", records=[])
            write_session(other, cwd="/other", records=[])
            os.utime(target, (1, 1))
            os.utime(other, (2, 2))

            result = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--sessions-root",
                    str(root),
                    "--cwd",
                    "/target",
                    "--limit",
                    "1",
                    "--include-latest-family",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            self.assertEqual(report["candidate_files_examined"], 2)
            self.assertEqual(report["sessions_considered"], 1)
            self.assertEqual(report["sessions"][0]["cwd"], "/target")

    def test_active_root_and_subagents_are_excluded_from_prior_window(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prior = root / "rollout-prior.jsonl"
            current = root / "rollout-current.jsonl"
            subagent = root / "rollout-subagent.jsonl"
            write_session(prior, cwd="/target", records=[])
            write_session(current, cwd="/target", records=[])
            write_session(subagent, cwd="/target", records=[], parent_thread_id=current.stem)
            os.utime(prior, (1, 1))
            os.utime(current, (2, 2))
            os.utime(subagent, (3, 3))

            result = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--sessions-root",
                    str(root),
                    "--cwd",
                    "/target",
                    "--limit",
                    "1",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            self.assertEqual(report["excluded_current_family"], current.stem)
            self.assertEqual([item["source_ref"] for item in report["sessions"]], [prior.stem])


if __name__ == "__main__":
    unittest.main()
