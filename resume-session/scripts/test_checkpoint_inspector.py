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
INSPECTOR = HERE / "inspect_checkpoint.py"
NOW = "2026-07-16T06:00:00Z"
GOAL = """## Outcome
Complete the exact saved objective without shrinking its exit gate.

## Verification
- Preserve embedded Markdown headings during checkpoint parsing."""


class CheckpointInspectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test User")
        self.git("config", "user.email", "test@example.com")
        (self.root / "owner.txt").write_text("owner\n", encoding="utf-8")
        self.git("add", "owner.txt")
        self.git("commit", "-m", "owner")
        self.commit = self.git("rev-parse", "HEAD").stdout.strip()
        self.goal_files: list[Path] = []
        self.env = {
            **os.environ,
            "SESSION_WORKSPACE_HELPER": str(HERE.parent.parent / "session-orchestrate" / "scripts" / "session_workspace.py"),
        }

    def tearDown(self) -> None:
        for path in self.goal_files:
            path.unlink(missing_ok=True)
        self.temp.cleanup()

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", "-C", str(self.root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            self.fail(result.stderr)
        return result

    def write_checkpoint(
        self,
        *,
        policy: str = "ensure-active",
        saved_time: str = NOW,
        saved_root: Path | None = None,
        branch: str = "main",
        commit: str | None = None,
        window: str = "24",
        first_command: str | None = None,
    ) -> None:
        checkpoint = self.root / ".session" / "CURRENT.md"
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        route = "## route_contract\n*(none supplied)*\n"
        if first_command is not None:
            route = f"## route_contract\nroute_id: test\nfirst_command: {first_command}\n"
        checkpoint.write_text(
            "# Session checkpoint\n\n"
            f"**time:** {saved_time}\n"
            f"**repo_root:** {saved_root or self.root}\n"
            f"**branch:** {branch}\n"
            f"**last_commit:** {commit or self.commit}\n"
            f"**resume_window_hours:** {window}\n\n"
            "## handoff_focus\nSaved work.\n\n"
            "## codex_goal\n"
            f"resume_policy: {policy}\n"
            f"objective:\n{GOAL}\n\n"
            "## working_on\nSaved work.\n\n"
            f"{route}",
            encoding="utf-8",
        )

    def inspect(self, *, write_goal: bool = False) -> dict:
        command = [sys.executable, str(INSPECTOR), "--root", str(self.root), "--now", NOW]
        if write_goal:
            command.append("--write-goal-file")
        result = subprocess.run(command, env=self.env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        if output.get("goal_file"):
            self.goal_files.append(Path(output["goal_file"]))
        return output

    def test_fresh_ensure_active_goal_is_exact_and_private(self) -> None:
        self.write_checkpoint()
        output = self.inspect(write_goal=True)
        self.assertEqual(output["eligibility"], "fresh")
        self.assertEqual(output["mode"], "resume-exact-goal")
        path = Path(output["goal_file"])
        self.assertEqual(path.read_text(encoding="utf-8").rstrip(), GOAL)
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_reference_only_never_resumes(self) -> None:
        self.write_checkpoint(policy="reference-only")
        output = self.inspect(write_goal=True)
        self.assertEqual(output["eligibility"], "reference-only")
        self.assertEqual(output["mode"], "choose-next-goal")
        self.assertIsNone(output["goal_file"])

    def test_expired_checkpoint_requires_review(self) -> None:
        self.write_checkpoint(saved_time="2026-07-14T06:00:00Z")
        output = self.inspect(write_goal=True)
        self.assertEqual(output["mode"], "review-checkpoint")
        self.assertIn("checkpoint_expired", output["reasons"])
        self.assertIsNone(output["goal_file"])

    def test_future_checkpoint_requires_review(self) -> None:
        self.write_checkpoint(saved_time="2026-07-17T06:00:00Z")
        self.assertIn("checkpoint_from_future", self.inspect()["reasons"])

    def test_wrong_root_requires_review(self) -> None:
        self.write_checkpoint(saved_root=self.root.parent / "other")
        self.assertIn("repo_root_mismatch", self.inspect()["reasons"])

    def test_wrong_branch_requires_review(self) -> None:
        self.write_checkpoint(branch="other")
        self.assertIn("branch_mismatch", self.inspect()["reasons"])

    def test_missing_saved_commit_requires_review(self) -> None:
        self.write_checkpoint(commit="0" * 40)
        self.assertIn("saved_commit_missing", self.inspect()["reasons"])

    def test_missing_absolute_first_command_requires_review(self) -> None:
        self.write_checkpoint(first_command="/definitely/missing/session-command")
        self.assertIn("first_command_missing", self.inspect()["reasons"])

    def test_unavailable_path_command_requires_review(self) -> None:
        self.write_checkpoint(first_command="definitely-not-a-real-session-command --check")
        self.assertIn("first_command_unavailable", self.inspect()["reasons"])

    def test_invalid_policy_requires_review(self) -> None:
        self.write_checkpoint(policy="replace-existing")
        output = self.inspect()
        self.assertEqual(output["eligibility"], "invalid")
        self.assertIn("resume_policy_invalid", output["reasons"])

    def test_missing_checkpoint_chooses_next_goal(self) -> None:
        output = self.inspect()
        self.assertEqual(output["eligibility"], "missing")
        self.assertEqual(output["mode"], "choose-next-goal")


if __name__ == "__main__":
    unittest.main()
