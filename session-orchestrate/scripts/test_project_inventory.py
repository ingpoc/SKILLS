#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "project_inventory.py"


class ProjectInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "project"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.name", "Test"], check=True)
        (self.root / "AGENTS.md").write_text("Use the product plan owner.\n", encoding="utf-8")
        docs = self.root / "docs"
        docs.mkdir()
        (docs / "PRODUCTPLAN.md").write_text("# Product plan\n", encoding="utf-8")
        (docs / "IMPLEMENTATION_STATUS.md").write_text("# Status\n", encoding="utf-8")
        skill = self.root / ".codex" / "skills" / "project-test"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: project-test\n---\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "initial product plan"], check=True)

        self.codex_home = self.base / "codex"
        session = self.codex_home / "sessions" / "2026" / "07" / "16" / "rollout-test.jsonl"
        session.parent.mkdir(parents=True)
        rows = [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "session_meta",
                "payload": {
                    "id": "session-test",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "cwd": str(self.root),
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{
                        "type": "input_text",
                        "text": "# AGENTS.md instructions for /tmp/project\nUse $contaminating-skill.",
                    }],
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{
                        "type": "input_text",
                        "text": "Run [$project-test](/tmp/skills/project-test/SKILL.md) then $session-orchestrate. SECRET=do-not-copy",
                    }],
                },
            },
        ]
        session.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_inventory(self) -> dict[str, object]:
        env = {**os.environ, "CODEX_HOME": str(self.codex_home)}
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), "--session-days", "30"],
            env=env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_inventory_finds_owners_status_skills_and_recent_sessions(self) -> None:
        output = self.run_inventory()
        self.assertEqual(output["owner_routing_candidates"], ["AGENTS.md"])
        self.assertIn("docs/PRODUCTPLAN.md", output["product_plan_candidates"])
        self.assertIn("docs/IMPLEMENTATION_STATUS.md", output["implementation_status_candidates"])
        self.assertEqual(output["local_skills"], [".codex/skills/project-test/SKILL.md"])
        history = output["recent_project_sessions"]
        self.assertEqual(history["authority"], "hints-only")
        self.assertEqual(history["sessions"][0]["id"], "session-test")
        names = {item["name"] for item in history["common_skill_mentions"]}
        self.assertIn("project-test", names)
        self.assertIn("session-orchestrate", names)
        self.assertNotIn("contaminating-skill", names)

    def test_inventory_does_not_echo_session_message_text(self) -> None:
        encoded = json.dumps(self.run_inventory())
        self.assertNotIn("SECRET", encoded)
        self.assertNotIn("do-not-copy", encoded)


if __name__ == "__main__":
    unittest.main()
