#!/usr/bin/env python3
from __future__ import annotations

import json
import stat
import tempfile
import unittest
from pathlib import Path

from session_workspace import (
    canonical_paths,
    ensure_workspace,
    mark_goal,
    sync_program,
    workspace_status,
)


class SessionWorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        docs = self.root / "docs"
        docs.mkdir()
        self.product_plan = docs / "PRODUCTPLAN.md"
        self.product_plan.write_text("# Product plan\n\n## Phase 1\nShip the product.\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def program(self, *, first_status: str = "planned", first_evidence: list[str] | None = None) -> dict:
        return {
            "completion_gate": "An operator completes the full product loop with traceable evidence.",
            "phase_boundary": "Phase 1",
            "plan_sources": ["docs/PRODUCTPLAN.md"],
            "selected_goal_id": "foundation" if first_status != "completed" else "verification",
            "goals": [
                {
                    "id": "foundation",
                    "title": "Build the foundation",
                    "status": first_status,
                    "plan_ref": "PRODUCTPLAN Phase 1 foundation",
                    "prerequisites": [],
                    "actions": ["Implement the narrow foundation slice."],
                    "verification": ["Run the deterministic foundation gate."],
                    "evidence": first_evidence or [],
                    "authority_gates": [],
                },
                {
                    "id": "verification",
                    "title": "Prove the product loop",
                    "status": "planned",
                    "plan_ref": "PRODUCTPLAN Phase 1 exit gate",
                    "prerequisites": ["foundation"],
                    "actions": ["Exercise the operator journey."],
                    "verification": ["Trace every output to evidence."],
                    "evidence": [],
                    "authority_gates": ["Stop before deployment without operator authority."],
                },
            ],
        }

    def write_program(self, value: dict) -> Path:
        path = self.root / "program.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_ensure_creates_one_private_canonical_workspace(self) -> None:
        output = ensure_workspace(self.root)
        paths = canonical_paths(self.root)
        self.assertTrue(paths["tracking"].is_file())
        self.assertTrue(paths["plan"].is_file())
        self.assertFalse(paths["current"].exists())
        self.assertEqual(stat.S_IMODE(paths["session"].stat().st_mode), 0o700)
        self.assertEqual(output["program_action"], "rebuild-plan")
        self.assertIn("program_not_derived", output["stale_reasons"])

    def test_ensure_migrates_legacy_checkpoint_and_chain_without_deleting_them(self) -> None:
        legacy = self.root / ".claude" / "session-data"
        legacy.mkdir(parents=True)
        current = legacy / "CURRENT.md"
        chain = legacy / "ORCHESTRATION.json"
        current.write_text("legacy current\n", encoding="utf-8")
        chain.write_text('{"schema_version": 1, "status": "stopped"}\n', encoding="utf-8")
        output = ensure_workspace(self.root)
        paths = canonical_paths(self.root)
        self.assertEqual(paths["current"].read_text(encoding="utf-8"), "legacy current\n")
        self.assertEqual(paths["orchestration"].read_text(encoding="utf-8"), chain.read_text(encoding="utf-8"))
        self.assertTrue(current.exists())
        self.assertTrue(chain.exists())
        self.assertEqual(
            set(output["migrated"]),
            {".claude/session-data/CURRENT.md", ".claude/session-data/ORCHESTRATION.json"},
        )

    def test_sync_renders_plan_and_detects_owner_source_change(self) -> None:
        ensure_workspace(self.root)
        output = sync_program(self.root, self.write_program(self.program()))
        self.assertEqual(output["program_status"], "ready")
        self.assertEqual(output["program_action"], "use-plan")
        plan = canonical_paths(self.root)["plan"].read_text(encoding="utf-8")
        self.assertIn("foundation — Build the foundation", plan)
        self.assertIn("verification — Prove the product loop", plan)
        self.product_plan.write_text("# Product plan\n\nChanged owner decision.\n", encoding="utf-8")
        stale = workspace_status(self.root)
        self.assertEqual(stale["program_action"], "rebuild-plan")
        self.assertIn("plan_source_changed:docs/PRODUCTPLAN.md", stale["stale_reasons"])

    def test_projection_edit_is_rejected_as_stale(self) -> None:
        ensure_workspace(self.root)
        sync_program(self.root, self.write_program(self.program()))
        canonical_paths(self.root)["plan"].write_text("manual edit\n", encoding="utf-8")
        self.assertIn("plan_projection_modified", workspace_status(self.root)["stale_reasons"])

    def test_completed_goal_requires_evidence(self) -> None:
        ensure_workspace(self.root)
        with self.assertRaisesRegex(ValueError, "completed goal requires evidence"):
            sync_program(self.root, self.write_program(self.program(first_status="completed")))

    def test_mark_goal_records_evidence_and_requests_next_plan_selection(self) -> None:
        ensure_workspace(self.root)
        sync_program(self.root, self.write_program(self.program()))
        with self.assertRaisesRegex(ValueError, "requires at least one evidence"):
            mark_goal(self.root, "foundation", "completed", [])
        output = mark_goal(self.root, "foundation", "completed", ["tests/foundation-proof.txt"])
        self.assertEqual(output["program_status"], "needs_refresh")
        self.assertEqual(output["program_action"], "rebuild-plan")
        tracking = json.loads(canonical_paths(self.root)["tracking"].read_text(encoding="utf-8"))
        goal = next(item for item in tracking["goals"] if item["id"] == "foundation")
        self.assertEqual(goal["status"], "completed")
        self.assertEqual(goal["evidence"], ["tests/foundation-proof.txt"])
        with self.assertRaisesRegex(ValueError, "full program resync"):
            mark_goal(self.root, "foundation", "planned", [])

    def test_selected_goal_cannot_bypass_prerequisites(self) -> None:
        ensure_workspace(self.root)
        value = self.program()
        value["selected_goal_id"] = "verification"
        with self.assertRaisesRegex(ValueError, "selected goal has incomplete prerequisites"):
            sync_program(self.root, self.write_program(value))

    def test_mark_cannot_start_goal_before_prerequisites_complete(self) -> None:
        ensure_workspace(self.root)
        sync_program(self.root, self.write_program(self.program()))
        with self.assertRaisesRegex(ValueError, "goal has incomplete prerequisites"):
            mark_goal(self.root, "verification", "in_progress", [])


if __name__ == "__main__":
    unittest.main()
