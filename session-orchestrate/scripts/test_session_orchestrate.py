#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
STATE = HERE / "chain_state.py"
VALIDATE = HERE / "validate_goal.py"
POSTCOMPACT = HERE / "postcompact_nudge.py"
CHECKPOINT = HERE / "checkpoint.py"
ENTRY = HERE / "entry.py"


def goal(words: int = 220) -> str:
    filler = " ".join(f"detail{i}" for i in range(words - 35))
    return f"""## Outcome
Deliver one bounded result with traceable evidence. {filler}

## Scope
- Implement one owned deliverable and its direct integration seam.

## Constraints
Preserve exact goal text and avoid external effects.

## Verification
- Run deterministic assertions and inspect their outputs.

## Stop conditions
- Stop after the evidence passes or an authority boundary is reached.
"""


class SessionOrchestrateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env = {**os.environ, "SESSION_ORCHESTRATE_ROOT": str(self.root)}
        self.entry_goal_files: list[Path] = []

    def tearDown(self) -> None:
        for path in self.entry_goal_files:
            path.unlink(missing_ok=True)
        self.temp.cleanup()

    def run_state(self, *args: str, ok: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run([sys.executable, str(STATE), *args], env=self.env, text=True, capture_output=True)
        if ok and result.returncode != 0:
            self.fail(result.stderr)
        return result

    def write_goal(self, words: int = 220) -> Path:
        path = self.root / "goal.md"
        path.write_text(goal(words), encoding="utf-8")
        return path

    def write_checkpoint(self, policy: str, objective: str) -> Path:
        path = self.root / ".claude" / "session-data" / "CURRENT.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# Session checkpoint\n\n"
            "## codex_goal\n"
            f"resume_policy: {policy}\n"
            "objective:\n"
            f"{objective.rstrip()}\n\n"
            "## working_on\nSaved work.\n",
            encoding="utf-8",
        )
        return path

    def run_entry(self, ok: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run([sys.executable, str(ENTRY)], env=self.env, text=True, capture_output=True)
        if ok and result.returncode != 0:
            self.fail(result.stderr)
        if result.returncode == 0:
            goal_file = json.loads(result.stdout).get("goal_file")
            if goal_file:
                self.entry_goal_files.append(Path(goal_file))
        return result

    def test_goal_validator_accepts_session_sized_goal(self) -> None:
        result = subprocess.run([sys.executable, str(VALIDATE), str(self.write_goal())], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_entry_extracts_exact_ensure_active_goal(self) -> None:
        objective = goal()
        self.write_checkpoint("ensure-active", objective)
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["mode"], "resume-exact-goal")
        self.assertEqual(output["invocation_authority"], "saved-goal-only")
        self.assertEqual(output["chain_action"], "init-new-chain")
        goal_file = Path(output["goal_file"])
        self.assertEqual(goal_file.read_text(encoding="utf-8").rstrip(), objective.rstrip())
        self.assertEqual(goal_file.stat().st_mode & 0o777, 0o600)

    def test_entry_reuses_active_chain(self) -> None:
        self.write_checkpoint("ensure-active", goal())
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["chain_action"], "reuse-active-chain")
        self.assertEqual(output["chain"]["phase_boundary"], "Phase 5")

    def test_entry_resumes_goal_without_reopening_stopped_chain(self) -> None:
        self.write_checkpoint("ensure-active", goal())
        self.run_state("init", "--max-hops", "1", "--phase-boundary", "Phase 5")
        self.run_state("stop", "--status", "stopped", "--reason", "retry window ended")
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["chain_action"], "resume-goal-chain-closed")
        self.assertEqual(output["chain"]["stop_reason"], "retry window ended")

    def test_entry_does_not_resume_reference_only_goal(self) -> None:
        self.write_checkpoint("reference-only", goal())
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["mode"], "choose-next-goal")
        self.assertIsNone(output["goal_file"])

    def test_entry_starts_new_chain_after_reference_only_checkpoint(self) -> None:
        self.write_checkpoint("reference-only", goal())
        self.run_state("init", "--max-hops", "1", "--phase-boundary", "Phase 5")
        self.run_state("stop", "--status", "completed", "--reason", "phase complete")
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["mode"], "choose-next-goal")
        self.assertEqual(output["chain_action"], "init-new-chain")

    def test_goal_validator_rejects_short_goal(self) -> None:
        result = subprocess.run([sys.executable, str(VALIDATE), str(self.write_goal(50))], text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("too short", result.stderr)

    def test_nonce_handoff_is_single_spawn_and_claimable(self) -> None:
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        goal_path = self.write_goal()
        self.run_state("set-goal", "--objective-file", str(goal_path))
        first = json.loads(self.run_state("prepare-handoff", "--kind", "next-goal", "--nonce", "n1").stdout)
        self.assertTrue(first["spawn_allowed"])
        duplicate = json.loads(self.run_state("prepare-handoff", "--kind", "next-goal").stdout)
        self.assertFalse(duplicate["spawn_allowed"])
        self.assertEqual(duplicate["reason"], "handoff_already_pending")
        self.run_state("record-successor", "--nonce", "n1", "--thread-id", "thread-1")
        claimed = json.loads(self.run_state("claim", "--nonce", "n1").stdout)
        self.assertEqual(claimed["hop"], 2)
        self.assertEqual(claimed["kind"], "next-goal")
        state = json.loads(self.run_state("status").stdout)
        self.assertEqual(state["metrics"]["handoffs_prepared"], 1)
        self.assertEqual(state["metrics"]["successors_created"], 1)
        self.assertEqual(state["metrics"]["duplicate_spawn_attempts"], 1)

    def test_wrong_nonce_cannot_claim(self) -> None:
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        self.run_state("set-goal", "--objective-file", str(self.write_goal()))
        self.run_state("prepare-handoff", "--kind", "continue-goal", "--nonce", "right")
        self.run_state("record-successor", "--nonce", "right", "--thread-id", "thread-1")
        result = self.run_state("claim", "--nonce", "wrong", ok=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("nonce mismatch", result.stderr)

    def test_max_hops_stops_without_spawn(self) -> None:
        self.run_state("init", "--max-hops", "1", "--phase-boundary", "Phase 5")
        self.run_state("set-goal", "--objective-file", str(self.write_goal()))
        result = json.loads(self.run_state("prepare-handoff", "--kind", "next-goal").stdout)
        self.assertFalse(result["spawn_allowed"])
        self.assertEqual(result["reason"], "max_hops_reached")

    def test_postcompact_is_silent_without_active_chain(self) -> None:
        event = json.dumps({"cwd": str(self.root), "hook_event_name": "PostCompact"})
        result = subprocess.run([sys.executable, str(POSTCOMPACT)], input=event, text=True, capture_output=True)
        output = json.loads(result.stdout)
        self.assertTrue(output["suppressOutput"])

    def test_postcompact_nudges_only_active_chain(self) -> None:
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        event = json.dumps({"cwd": str(self.root), "hook_event_name": "PostCompact"})
        result = subprocess.run([sys.executable, str(POSTCOMPACT)], input=event, text=True, capture_output=True)
        output = json.loads(result.stdout)
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "PostCompact")

    def test_checkpoint_round_trips_exact_goal(self) -> None:
        goal_path = self.write_goal()
        result = subprocess.run([
            sys.executable,
            str(CHECKPOINT),
            "--root",
            str(self.root),
            "--goal-file",
            str(goal_path),
            "--resume-policy",
            "ensure-active",
            "--next-action",
            "Run the exact saved first action.",
        ], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        saved = (self.root / ".claude" / "session-data" / "CURRENT.md").read_text(encoding="utf-8")
        self.assertIn(goal_path.read_text(encoding="utf-8").rstrip(), saved)
        self.assertIn("resume_policy: ensure-active", saved)

    def test_record_metric_works_after_stop(self) -> None:
        self.run_state("init", "--max-hops", "1", "--phase-boundary", "Phase 5")
        self.run_state("stop", "--status", "stopped", "--reason", "trial complete")
        result = json.loads(self.run_state("record-metric", "--name", "operator_repairs", "--increment", "3").stdout)
        self.assertEqual(result["value"], 3)


if __name__ == "__main__":
    unittest.main()
