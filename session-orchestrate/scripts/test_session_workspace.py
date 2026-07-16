#!/usr/bin/env python3
from __future__ import annotations

import json
import stat
import tempfile
import unittest
from pathlib import Path

from session_workspace import (
    PROGRAM_POLICY_VERSION,
    canonical_paths,
    ensure_workspace,
    mark_goal,
    render_plan,
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

    def project_lifecycle_program(self, profile: str = "web-release") -> dict:
        value = self.program()
        value["selected_goal_id"] = "project-lifecycle"
        if profile == "editor-runtime":
            title = "Complete the Phase 1 runtime acceptance lifecycle"
            authority_gates = ["Stop before unowned editor or process teardown."]
            stages = [
                {
                    "id": "scene-integration",
                    "kind": "implementation",
                    "title": "Scene integration",
                    "action": "complete the accepted editor and runtime seam",
                    "route": "repository editor integration route",
                    "acceptance": "the scene loads with the intended structure",
                },
                {
                    "id": "rendered-proof",
                    "kind": "verification",
                    "title": "Rendered proof",
                    "action": "exercise the actual editor, PIE, and capture route",
                    "route": "repository runtime verification skill",
                    "acceptance": "the artifact meets the visual acceptance rubric",
                },
                {
                    "id": "capability-hardening",
                    "kind": "hardening",
                    "title": "Capability hardening",
                    "action": "encode only proven repeated friction in the local owner",
                    "route": "existing repository skill or local skill-creation route",
                    "acceptance": "positive and negative route tests pass",
                },
            ]
        else:
            title = "Complete the Phase 1 web release lifecycle"
            authority_gates = ["Deployment and external sends retain their normal authority."]
            stages = [
                {
                    "id": "implementation",
                    "kind": "implementation",
                    "title": "Implementation",
                    "action": "complete the accepted product scope",
                    "route": "repository implementation owner",
                    "acceptance": "the integration seam is complete",
                },
                {
                    "id": "local-proof",
                    "kind": "verification",
                    "title": "Local proof",
                    "action": "run the repository-owned deterministic profile",
                    "route": "repository local test route",
                    "acceptance": "the local release gate passes",
                },
                {
                    "id": "deployment",
                    "kind": "promotion",
                    "title": "Deployment",
                    "action": "promote only with normal authority",
                    "route": "repository deployment route",
                    "acceptance": "the canonical target is ready",
                    "authority_gate": "deployment authority",
                },
                {
                    "id": "production-proof",
                    "kind": "verification",
                    "title": "Production proof",
                    "action": "test the canonical release and repair defects",
                    "route": "repository production verification route",
                    "acceptance": "the production acceptance flow passes",
                },
                {
                    "id": "stakeholder-handoff",
                    "kind": "handoff",
                    "title": "Stakeholder handoff",
                    "action": "send only with external-send authority",
                    "route": "repository handoff route or explicit gate",
                    "acceptance": "the authorized handoff is independently confirmed",
                    "authority_gate": "external-send authority",
                },
            ]
        value["goals"] = [{
            "id": "project-lifecycle",
            "title": title,
            "status": "planned",
            "delivery_unit": "project-lifecycle",
            "plan_ref": "PRODUCTPLAN Phase 1 exit gate",
            "prerequisites": [],
            "lifecycle_stages": stages,
            "verification": ["Prove the complete release lifecycle or preserve its exact gate."],
            "evidence": [],
            "authority_gates": authority_gates,
        }]
        return value

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

    def test_project_lifecycle_accepts_web_and_editor_runtime_profiles(self) -> None:
        ensure_workspace(self.root)
        output = sync_program(self.root, self.write_program(self.project_lifecycle_program()))
        self.assertEqual(output["program_policy_version"], PROGRAM_POLICY_VERSION)
        self.assertEqual(output["selected_goal_delivery_unit"], "project-lifecycle")
        plan = canonical_paths(self.root)["plan"].read_text(encoding="utf-8")
        self.assertIn("Delivery unit: `project-lifecycle`", plan)
        self.assertIn("`production-proof` [verification]", plan)

        editor = self.project_lifecycle_program("editor-runtime")
        output = sync_program(self.root, self.write_program(editor))
        self.assertEqual(len(output["selected_goal_lifecycle_stages"]), 3)
        plan = canonical_paths(self.root)["plan"].read_text(encoding="utf-8")
        self.assertIn("`rendered-proof` [verification]", plan)
        self.assertNotIn("Deployment", plan)

        no_proof = self.project_lifecycle_program("editor-runtime")
        no_proof["goals"][0]["lifecycle_stages"] = [no_proof["goals"][0]["lifecycle_stages"][0], no_proof["goals"][0]["lifecycle_stages"][2]]
        with self.assertRaisesRegex(ValueError, "requires verification after implementation"):
            sync_program(self.root, self.write_program(no_proof))

        missing_route = self.project_lifecycle_program("editor-runtime")
        missing_route["goals"][0]["lifecycle_stages"][1].pop("route")
        with self.assertRaisesRegex(ValueError, "rendered-proof.route must be non-empty"):
            sync_program(self.root, self.write_program(missing_route))

        early_promotion = self.project_lifecycle_program()
        stages = early_promotion["goals"][0]["lifecycle_stages"]
        stages[1], stages[2] = stages[2], stages[1]
        with self.assertRaisesRegex(ValueError, "require verification before: deployment"):
            sync_program(self.root, self.write_program(early_promotion))

    def test_dynamic_queue_selection_must_match_the_only_unfinished_goal(self) -> None:
        ensure_workspace(self.root)
        program = self.project_lifecycle_program("editor-runtime")
        program["selection_probe"] = {
            "scope": "dynamic-queue",
            "route": "npm run queue:next -- --read-only",
            "target": "community-detail/share-report-community",
            "source_refs": ["docs/PRODUCTPLAN.md"],
        }
        program["goals"][0]["admission_target"] = "community-detail/share-report-community"
        output = sync_program(self.root, self.write_program(program))
        self.assertEqual(output["selection_probe"]["target"], "community-detail/share-report-community")
        plan = canonical_paths(self.root)["plan"].read_text(encoding="utf-8")
        self.assertIn("npm run queue:next -- --read-only", plan)
        refreshed = mark_goal(
            self.root,
            "project-lifecycle",
            "completed",
            ["evidence:accepted-current-queue-item"],
        )
        self.assertEqual(refreshed["program_action"], "rebuild-plan")
        self.assertIn("program_not_derived", refreshed["stale_reasons"])

        mismatch = self.project_lifecycle_program("editor-runtime")
        mismatch["selection_probe"] = program["selection_probe"]
        mismatch["goals"][0]["admission_target"] = "circle-detail"
        with self.assertRaisesRegex(ValueError, "admission_target does not match"):
            sync_program(self.root, self.write_program(mismatch))

        speculative = self.project_lifecycle_program("editor-runtime")
        speculative["selection_probe"] = program["selection_probe"]
        speculative["goals"][0]["admission_target"] = program["selection_probe"]["target"]
        extra = dict(speculative["goals"][0])
        extra["id"] = "speculative-next"
        extra["admission_target"] = "speculative-next"
        speculative["goals"].append(extra)
        with self.assertRaisesRegex(ValueError, "only the admitted unfinished goal"):
            sync_program(self.root, self.write_program(speculative))

    def test_legacy_program_policy_forces_source_preserving_rebuild(self) -> None:
        ensure_workspace(self.root)
        sync_program(self.root, self.write_program(self.program()))
        paths = canonical_paths(self.root)
        tracking = json.loads(paths["tracking"].read_text(encoding="utf-8"))
        tracking.pop("program_policy_version")
        paths["tracking"].write_text(json.dumps(tracking, indent=2) + "\n", encoding="utf-8")
        paths["plan"].write_text(render_plan(tracking), encoding="utf-8")
        output = workspace_status(self.root)
        self.assertEqual(output["program_action"], "rebuild-plan")
        self.assertEqual(output["stale_reasons"], ["program_policy_changed"])

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
