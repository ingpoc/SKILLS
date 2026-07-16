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

    def tearDown(self) -> None:
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

    def test_goal_validator_accepts_session_sized_goal(self) -> None:
        result = subprocess.run([sys.executable, str(VALIDATE), str(self.write_goal())], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

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


if __name__ == "__main__":
    unittest.main()
