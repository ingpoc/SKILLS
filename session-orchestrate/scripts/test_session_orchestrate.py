#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from entry import orchestration_action
from session_workspace import canonical_paths, ensure_workspace, render_plan, sync_program
from workflow_slice import render as render_workflow_slice

HERE = Path(__file__).resolve().parent
STATE = HERE / "chain_state.py"
VALIDATE = HERE / "validate_goal.py"
POSTCOMPACT = HERE / "postcompact_nudge.py"
CHECKPOINT = HERE / "checkpoint.py"
ENTRY = HERE / "entry.py"


def goal(words: int = 150) -> str:
    filler = " ".join(f"detail{i}" for i in range(max(0, words - 70)))
    return f"""## Outcome
Deliver one bounded result with traceable evidence. {filler}

## Plan linkage
This goal advances one current owner-plan deliverable and its acceptance gate.

## Acceptance gap
- Current: The deliverable lacks its owned implementation seam and accepted proof.
- Exit: The seam works and the direct deterministic evidence passes.

## Scope
- Implement one owned deliverable and its direct integration seam.

## Actions
- Read the narrow owner slice, implement the deliverable, and run its direct proof.

## Expected durable delta
- Implementation: Update the owned implementation surface and integration seam.
- Evidence: Retain deterministic proof that the acceptance gate passes.

## Constraints
Preserve exact goal text and avoid external effects.

## Verification
- Run deterministic assertions and inspect their outputs.

## Stop conditions
- Stop after the evidence passes or an authority boundary is reached.
"""


def project_lifecycle_goal(profile: str = "web-release") -> str:
    if profile == "editor-runtime":
        lifecycle = """
## Delivery lifecycle
- [implementation] Scene integration: complete the accepted editor and runtime seam through the repository owner.
- [verification] Rendered proof: exercise editor, PIE, capture, and independent visual acceptance routes.
- [hardening] Capability packaging: encode only proven reusable friction in the correct local owner.
"""
    else:
        lifecycle = """
## Delivery lifecycle
- [implementation] Product implementation: complete the accepted phase scope and integration seam.
- [verification] Local proof: run the repository-owned deterministic release gate.
- [promotion] Deployment: promote only when normal deployment authority is present.
- [verification] Production proof: test the canonical release and repair any observed defect.
- [handoff] Stakeholder handoff: send only with explicit external-send authority.
"""
    base = re.sub(r"(?ms)^## Actions\s*$\n.*?(?=^## )", "", goal())
    return base.replace(
        "\n## Constraints\n",
        lifecycle + "\n## Constraints\n",
    )


class SessionOrchestrateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "initial", "--allow-empty"], check=True)
        self.env = {
            **os.environ,
            "SESSION_ORCHESTRATE_ROOT": str(self.root),
        }
        self.entry_goal_files: list[Path] = []

    def tearDown(self) -> None:
        for path in self.entry_goal_files:
            path.unlink(missing_ok=True)
        self.temp.cleanup()

    def run_state(self, *args: str, ok: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(STATE), *args],
            cwd=self.root,
            env=self.env,
            text=True,
            capture_output=True,
        )
        if ok and result.returncode != 0:
            self.fail(result.stderr)
        return result

    def write_goal(self, words: int = 150) -> Path:
        path = self.root / "goal.md"
        path.write_text(goal(words), encoding="utf-8")
        return path

    def write_checkpoint(self, policy: str, objective: str, *, age_hours: int = 0) -> Path:
        docs = self.root / "docs"
        docs.mkdir(exist_ok=True)
        (docs / "PRODUCTPLAN.md").write_text("# Product plan\n\n## Test phase\n", encoding="utf-8")
        ensure_workspace(self.root)
        program = self.root / "program.json"
        program.write_text(json.dumps({
            "completion_gate": "The exact test goal passes with deterministic evidence.",
            "phase_boundary": "Test phase",
            "plan_sources": ["docs/PRODUCTPLAN.md"],
            "selected_goal_id": "test-goal",
            "goals": [{
                "id": "test-goal",
                "title": "Complete the exact test goal",
                "status": "in_progress",
                "plan_ref": "PRODUCTPLAN Test phase",
                "prerequisites": [],
                "actions": ["Execute the bounded test action."],
                "verification": ["Run the deterministic test proof."],
                "evidence": [],
                "authority_gates": [],
            }],
        }), encoding="utf-8")
        sync_program(self.root, program)
        path = self.root / ".session" / "CURRENT.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        saved_at = datetime.now(UTC) - timedelta(hours=age_hours)
        branch = subprocess.run(
            ["git", "-C", str(self.root), "branch", "--show-current"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        commit = subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        path.write_text(
            "# Session checkpoint\n\n"
            f"**time:** {saved_at.isoformat().replace('+00:00', 'Z')}\n"
            f"**repo_root:** {self.root}\n"
            f"**branch:** {branch}\n"
            f"**last_commit:** {commit}\n"
            "**resume_window_hours:** 24\n\n"
            "## codex_goal\n"
            f"resume_policy: {policy}\n"
            "objective:\n"
            f"{objective.rstrip()}\n\n"
            "## working_on\nSaved work.\n",
            encoding="utf-8",
        )
        return path

    def sync_program_status(self, status: str) -> None:
        docs = self.root / "docs"
        docs.mkdir(exist_ok=True)
        (docs / "PRODUCTPLAN.md").write_text("# Product plan\n\n## Test phase\n", encoding="utf-8")
        ensure_workspace(self.root)
        selected = None if status == "completed" else "test-goal"
        program = self.root / f"program-{status}.json"
        program.write_text(json.dumps({
            "completion_gate": "The exact test goal passes with deterministic evidence.",
            "phase_boundary": "Test phase",
            "plan_sources": ["docs/PRODUCTPLAN.md"],
            "selected_goal_id": selected,
            "goals": [{
                "id": "test-goal",
                "title": "Complete the exact test goal",
                "status": status,
                "plan_ref": "PRODUCTPLAN Test phase",
                "prerequisites": [],
                "actions": ["Execute the bounded test action."],
                "verification": ["Run the deterministic test proof."],
                "evidence": ["test:verified"] if status == "completed" else [],
                "authority_gates": [],
            }],
        }), encoding="utf-8")
        sync_program(self.root, program)

    def run_entry(self, *args: str, ok: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(ENTRY), "--root", str(self.root), *args],
            cwd=self.root,
            env=self.env,
            text=True,
            capture_output=True,
        )
        if ok and result.returncode != 0:
            self.fail(result.stderr)
        if result.returncode == 0:
            output = json.loads(result.stdout)
            for goal_file in (
                output.get("goal_file"),
                (output.get("route_receipt") or {}).get("goal_file"),
            ):
                if goal_file:
                    self.entry_goal_files.append(Path(goal_file))
        return result

    def test_goal_validator_accepts_session_sized_goal(self) -> None:
        result = subprocess.run([sys.executable, str(VALIDATE), str(self.write_goal())], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_orchestration_action_surfaces_selection_probe(self) -> None:
        self.assertEqual(
            orchestration_action(
                "choose-next-goal",
                "init-new-chain",
                {"program_action": "use-plan", "selection_probe": {"target": "queue-item"}},
            ),
            "rerun-selection-probe",
        )

    def test_workflow_slice_is_bounded_to_the_entry_route(self) -> None:
        selected = render_workflow_slice("admission-probe-selected-goal")
        full = (HERE.parent / "references" / "workflow.md").read_text(encoding="utf-8")
        self.assertIn("## Operator DNA", selected)
        self.assertIn("## Choose and start one session goal", selected)
        self.assertIn("### Freeze before expensive acceptance", selected)
        self.assertNotIn("## Build the program map", selected)
        self.assertLess(len(selected), len(full) // 2)

        deterministic = render_workflow_slice("resume-proof-campaign")
        self.assertNotIn("## Operator DNA", deterministic)
        self.assertIn("### Proof campaign pause", deterministic)

    def test_successor_authority_is_explicit_and_bounded(self) -> None:
        skill = (HERE.parent / "SKILL.md").read_text(encoding="utf-8")
        workflow = (HERE.parent / "references" / "workflow.md").read_text(encoding="utf-8")
        interface = (HERE.parent / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn("explicit request required to create one eligible same-project successor", skill)
        self.assertIn("Do not request separate confirmation", workflow)
        self.assertIn("codex_app__create_thread", workflow)
        self.assertIn("leave the chain `handoff_pending`", workflow)
        self.assertIn("do not prepare or create a duplicate successor", workflow)
        self.assertIn("create exactly one eligible same-project successor", interface)

    def test_goal_validator_limits_legacy_shape_to_exact_resume(self) -> None:
        legacy = goal().replace(
            "\n## Plan linkage\nThis goal advances one current owner-plan deliverable and its acceptance gate.\n",
            "",
        ).replace(
            "\n## Actions\n- Read the narrow owner slice, implement the deliverable, and run its direct proof.\n",
            "",
        ).replace(
            "\n## Acceptance gap\n- Current: The deliverable lacks its owned implementation seam and accepted proof.\n- Exit: The seam works and the direct deterministic evidence passes.\n",
            "",
        ).replace(
            "\n## Expected durable delta\n- Implementation: Update the owned implementation surface and integration seam.\n- Evidence: Retain deterministic proof that the acceptance gate passes.\n",
            "",
        )
        path = self.root / "legacy.md"
        path.write_text(legacy, encoding="utf-8")
        rejected = subprocess.run([sys.executable, str(VALIDATE), str(path)], text=True, capture_output=True)
        self.assertEqual(rejected.returncode, 1)
        accepted = subprocess.run(
            [sys.executable, str(VALIDATE), str(path), "--legacy-resume"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(accepted.returncode, 0, accepted.stderr)

    def test_entry_extracts_exact_ensure_active_goal(self) -> None:
        objective = goal()
        self.write_checkpoint("ensure-active", objective)
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["mode"], "resume-exact-goal")
        self.assertEqual(output["invocation_authority"], "saved-goal-only")
        self.assertEqual(output["chain_action"], "init-new-chain")
        self.assertEqual(output["orchestration_action"], "resume-exact-goal")
        self.assertEqual(output["exploration"]["action"], "skip")
        self.assertEqual(output["route_receipt"]["execution_route"]["decision"], "direct")
        self.assertEqual(output["route_receipt"]["session_rebuild"]["action"], "none")
        goal_file = Path(output["goal_file"])
        self.assertEqual(output["route_receipt"]["goal_file"], str(goal_file))
        self.assertEqual(goal_file.read_text(encoding="utf-8").rstrip(), objective.rstrip())
        self.assertEqual(goal_file.stat().st_mode & 0o777, 0o600)

    def test_fresh_task_without_checkpoint_builds_current_project_inventory(self) -> None:
        (self.root / "AGENTS.md").write_text("Use the current product-plan owner.\n", encoding="utf-8")
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["mode"], "choose-next-goal")
        self.assertIn("checkpoint_missing", output["reasons"])
        self.assertEqual(output["project_inventory"]["owner_routing_candidates"], ["AGENTS.md"])
        self.assertEqual(output["workspace"]["program_action"], "rebuild-plan")
        self.assertEqual(output["orchestration_action"], "rebuild-program-map")
        self.assertEqual(output["project_inventory"]["inventory_mode"], "cheap")
        self.assertNotIn("discovery_hints", output["project_inventory"])
        self.assertEqual(output["exploration"]["action"], "first-migration")
        self.assertTrue(output["exploration"]["delegation_candidate"])
        execution = output["route_receipt"]["execution_route"]
        self.assertEqual(execution["decision"], "gate-required")
        self.assertEqual(execution["lane_owner"], "codex-routing-policy")
        self.assertEqual(execution["agent_type_owner"], "subagent-playbook")
        self.assertEqual(execution["efficiency_owner"], "codex-efficient-delegation")
        rebuild = output["route_receipt"]["session_rebuild"]
        self.assertEqual(rebuild["action"], "rebuild-derived-projections-in-place")
        self.assertFalse(rebuild["delete_session_allowed"])
        self.assertIn(".session/ORCHESTRATION.json", rebuild["preserve"])
        self.assertEqual(rebuild["regenerate"], [
            ".session/TRACKING.json",
            ".session/PLAN.md",
        ])
        self.assertIsNone(output["goal_file"])

    def test_route_receipt_is_stable_until_chain_state_changes(self) -> None:
        first = json.loads(self.run_entry().stdout)
        second = json.loads(self.run_entry().stdout)
        self.assertEqual(first["route_receipt"]["id"], second["route_receipt"]["id"])
        self.assertFalse(first["route_receipt"]["full_workflow_read_required"])
        self.assertFalse(first["route_receipt"]["state_transition_performed"])
        self.assertEqual(first["route_receipt"]["evidence_budget"]["inline_images"], 1)

        self.run_state("init", "--max-hops", "1", "--phase-boundary", "Test phase")
        changed = json.loads(self.run_entry().stdout)
        self.assertNotEqual(first["route_receipt"]["id"], changed["route_receipt"]["id"])

    def test_compact_entry_keeps_the_route_and_drops_inventory_noise(self) -> None:
        full_result = self.run_entry()
        compact_result = self.run_entry("--compact")
        full = json.loads(full_result.stdout)
        compact = json.loads(compact_result.stdout)
        self.assertEqual(full["route_receipt"]["id"], compact["route_receipt"]["id"])
        self.assertLess(len(compact_result.stdout), len(full_result.stdout))
        self.assertNotIn("git", compact["project_inventory"])
        self.assertIn("owner_routing_candidates", compact["project_inventory"])

    def test_entry_refuses_global_skills_repository_as_project_root(self) -> None:
        env = dict(os.environ)
        env.pop("SESSION_ORCHESTRATE_ROOT", None)
        skills_root = HERE.parents[1]
        state_before = (skills_root / ".session").exists()
        result = subprocess.run(
            [sys.executable, str(ENTRY)],
            cwd=skills_root,
            env=env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("refusing to orchestrate the global skills repository", result.stderr)
        self.assertEqual((skills_root / ".session").exists(), state_before)
        state_result = subprocess.run(
            [sys.executable, str(STATE), "status"],
            cwd=skills_root,
            env=env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(state_result.returncode, 1)
        self.assertIn("refusing to mutate orchestration state", state_result.stderr)

    def test_entry_fails_closed_outside_git_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run(
                [sys.executable, str(ENTRY)],
                cwd=root,
                env={key: value for key, value in os.environ.items() if key != "SESSION_ORCHESTRATE_ROOT"},
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("requires invocation from a Git product repository", result.stderr)
            self.assertFalse((root / ".session").exists())

    def test_explicit_descendant_root_fails_before_parent_workspace_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outer = Path(directory)
            subprocess.run(["git", "init", "-q", str(outer)], check=True)
            nested = outer / "nested-product"
            nested.mkdir()
            env = {key: value for key, value in os.environ.items() if key != "SESSION_ORCHESTRATE_ROOT"}

            entry = subprocess.run(
                [sys.executable, str(ENTRY), "--root", str(nested)],
                cwd=nested,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(entry.returncode, 1)
            self.assertIn("explicit session-orchestrate root is not a Git repository root", entry.stderr)
            self.assertFalse((outer / ".session").exists())
            self.assertFalse((nested / ".session").exists())

            state = subprocess.run(
                [sys.executable, str(STATE), "status"],
                cwd=nested,
                env={**env, "SESSION_ORCHESTRATE_ROOT": str(nested)},
                text=True,
                capture_output=True,
            )
            self.assertEqual(state.returncode, 1)
            self.assertIn("SESSION_ORCHESTRATE_ROOT is not a Git repository root", state.stderr)
            self.assertFalse((outer / ".session").exists())
            self.assertFalse((nested / ".session").exists())

    def test_invocation_uses_current_repo_and_rejects_stale_chain_root(self) -> None:
        other = self.root / "other-project"
        other.mkdir()
        subprocess.run(["git", "init", "-q", str(other)], check=True)
        stale_env = {**os.environ, "SESSION_ORCHESTRATE_ROOT": str(self.root)}

        entry = subprocess.run(
            [sys.executable, str(ENTRY)],
            cwd=other,
            env=stale_env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(entry.returncode, 0, entry.stderr)
        self.assertEqual(json.loads(entry.stdout)["project_root"], str(other.resolve()))
        self.assertTrue((other / ".session").is_dir())
        self.assertFalse((self.root / ".session").exists())

        mismatched_entry = subprocess.run(
            [sys.executable, str(ENTRY), "--root", str(self.root)],
            cwd=other,
            env=stale_env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(mismatched_entry.returncode, 1)
        self.assertIn("explicit session-orchestrate root does not match", mismatched_entry.stderr)

        state = subprocess.run(
            [sys.executable, str(STATE), "status"],
            cwd=other,
            env=stale_env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(state.returncode, 1)
        self.assertIn("does not match the current repository", state.stderr)

    def test_fresh_checkpoint_is_not_activated_when_program_source_changed(self) -> None:
        self.write_checkpoint("ensure-active", goal())
        (self.root / "docs" / "PRODUCTPLAN.md").write_text("# Product plan\n\nChanged current owner.\n", encoding="utf-8")
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["mode"], "review-checkpoint")
        self.assertIn("program_state_stale", output["reasons"])
        self.assertIn("plan_source_changed:docs/PRODUCTPLAN.md", output["workspace"]["stale_reasons"])
        self.assertEqual(output["exploration"]["action"], "stale-rebuild")
        self.assertEqual(
            output["route_receipt"]["session_rebuild"]["action"],
            "rebuild-derived-projections-in-place",
        )
        self.assertIsNone(output["goal_file"])

    def test_entry_reuses_active_chain(self) -> None:
        self.write_checkpoint("ensure-active", goal())
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        self.run_state("set-goal", "--objective-file", str(self.write_goal()))
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["chain_action"], "reuse-active-chain")
        self.assertEqual(output["chain"]["phase_boundary"], "Phase 5")

    def test_entry_recovers_exact_checkpoint_when_active_chain_goal_was_never_set(self) -> None:
        self.write_checkpoint("ensure-active", goal())
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["mode"], "resume-exact-goal")
        self.assertEqual(output["chain_action"], "recover-unset-goal")
        self.assertIn("chain_goal_hash_unset_recoverable", output["reasons"])
        self.assertEqual(output["exploration"]["action"], "skip")

    def test_entry_reuses_orphaned_active_chain_for_reference_only_checkpoint(self) -> None:
        self.write_checkpoint("reference-only", goal())
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["mode"], "choose-next-goal")
        self.assertEqual(output["chain_action"], "recover-orphaned-chain")
        self.assertEqual(output["invocation_authority"], "orphaned-chain-recovery")
        self.assertIn("active_chain_goal_unset_recoverable", output["reasons"])
        self.assertEqual(output["exploration"]["action"], "skip")
        self.assertEqual(output["chain"]["recovery"], {
            "kind": "orphaned-active-chain",
            "next_action": "admission-probe-selected-goal",
            "reuse_chain": True,
            "selected_goal_delivery_unit": "bounded-deliverable",
            "selected_goal_id": "test-goal",
            "selected_goal_lifecycle_stages": [],
            "set_goal_required": True,
        })

        admitted = self.write_goal()
        self.run_state("set-goal", "--objective-file", str(admitted))
        state = json.loads(self.run_state("status").stdout)
        self.assertEqual(state["hop"], 1)
        self.assertIsNotNone(state["goal_hash"])

    def test_reference_only_checkpoint_does_not_replace_bound_active_goal(self) -> None:
        self.write_checkpoint("reference-only", goal())
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        original = self.write_goal()
        self.run_state("set-goal", "--objective-file", str(original))
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["chain_action"], "review-active-chain")
        self.assertEqual(output["orchestration_action"], "review-active-goal")
        self.assertEqual(output["invocation_authority"], "active-chain-review")
        self.assertIsNone(output["chain"]["recovery"])

        different = self.root / "different-goal.md"
        different.write_text(goal().replace("one bounded result", "a different bounded result"), encoding="utf-8")
        result = self.run_state("set-goal", "--objective-file", str(different), ok=False)
        self.assertIn("already bound to a different goal", result.stderr)

    def test_orphaned_chain_rebuilds_stale_policy_before_goal_admission(self) -> None:
        self.write_checkpoint("reference-only", goal())
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        paths = canonical_paths(self.root)
        tracking = json.loads(paths["tracking"].read_text(encoding="utf-8"))
        tracking.pop("program_policy_version")
        paths["tracking"].write_text(json.dumps(tracking, indent=2) + "\n", encoding="utf-8")
        paths["plan"].write_text(render_plan(tracking), encoding="utf-8")

        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["workspace"]["program_action"], "rebuild-plan")
        self.assertEqual(output["chain_action"], "recover-orphaned-chain")
        self.assertEqual(output["chain"]["recovery"]["next_action"], "rebuild-program-map")
        self.assertEqual(output["orchestration_action"], "rebuild-program-map")
        self.assertIsNone(output["chain"]["recovery"]["selected_goal_id"])
        self.assertIsNone(output["chain"]["recovery"]["selected_goal_delivery_unit"])

    def test_entry_resumes_goal_without_reopening_stopped_chain(self) -> None:
        self.write_checkpoint("ensure-active", goal())
        self.run_state("init", "--max-hops", "1", "--phase-boundary", "Phase 5")
        self.run_state("set-goal", "--objective-file", str(self.write_goal()))
        self.run_state("stop", "--status", "stopped", "--reason", "retry window ended")
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["chain_action"], "resume-goal-chain-closed")
        self.assertEqual(output["chain"]["stop_reason"], "retry window ended")

    def test_entry_does_not_activate_expired_checkpoint(self) -> None:
        self.write_checkpoint("ensure-active", goal(), age_hours=25)
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["mode"], "review-checkpoint")
        self.assertEqual(output["chain_action"], "review-current-owner")
        self.assertIn("checkpoint_expired", output["reasons"])
        self.assertEqual(output["exploration"]["action"], "skip")
        self.assertIsNone(output["goal_file"])

    def test_blocked_program_stops_without_explorer(self) -> None:
        self.sync_program_status("blocked")
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["workspace"]["program_action"], "review-blocked-goal")
        self.assertEqual(output["exploration"]["action"], "skip")

    def test_complete_program_stops_without_explorer(self) -> None:
        self.sync_program_status("completed")
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["workspace"]["program_action"], "product-complete")
        self.assertEqual(output["exploration"]["action"], "skip")

    def test_entry_rejects_chain_goal_hash_mismatch(self) -> None:
        self.write_checkpoint("ensure-active", goal())
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        different = self.root / "different-goal.md"
        different.write_text(goal().replace("one bounded result", "a different bounded result"), encoding="utf-8")
        self.run_state("set-goal", "--objective-file", str(different))
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["mode"], "review-checkpoint")
        self.assertIn("chain_goal_hash_mismatch", output["reasons"])
        self.assertEqual(output["exploration"]["action"], "conflict")
        self.assertIsNone(output["goal_file"])

    def test_entry_does_not_reopen_completed_chain(self) -> None:
        self.write_checkpoint("ensure-active", goal())
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        self.run_state("set-goal", "--objective-file", str(self.write_goal()))
        self.run_state("stop", "--status", "completed", "--reason", "goal complete")
        output = json.loads(self.run_entry().stdout)
        self.assertEqual(output["mode"], "review-checkpoint")
        self.assertIn("chain_completed", output["reasons"])
        self.assertIsNone(output["goal_file"])

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

    def test_goal_validator_rejects_reconciliation_without_durable_delta(self) -> None:
        path = self.write_goal()
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "- Implementation: Update the owned implementation surface and integration seam.\n- Evidence: Retain deterministic proof that the acceptance gate passes.",
                "- Evidence: Inspect the already completed work.",
            ),
            encoding="utf-8",
        )
        result = subprocess.run([sys.executable, str(VALIDATE), str(path)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Implementation", result.stderr)

    def test_project_lifecycle_goal_accepts_project_defined_profiles(self) -> None:
        path = self.root / "project-lifecycle-goal.md"
        for profile in ("web-release", "editor-runtime"):
            path.write_text(project_lifecycle_goal(profile), encoding="utf-8")
            accepted = subprocess.run(
                [sys.executable, str(VALIDATE), str(path), "--delivery-unit", "project-lifecycle"],
                text=True,
                capture_output=True,
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr)

        path.write_text(goal(), encoding="utf-8")
        rejected = subprocess.run(
            [sys.executable, str(VALIDATE), str(path), "--delivery-unit", "project-lifecycle"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(rejected.returncode, 1)
        self.assertIn("Delivery lifecycle", rejected.stderr)

        path.write_text(
            project_lifecycle_goal("editor-runtime").replace(
                "- [verification] Rendered proof: exercise editor, PIE, capture, and independent visual acceptance routes.\n",
                "",
            ),
            encoding="utf-8",
        )
        missing_proof = subprocess.run(
            [sys.executable, str(VALIDATE), str(path), "--delivery-unit", "project-lifecycle"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(missing_proof.returncode, 1)
        self.assertIn("requires [verification] after [implementation]", missing_proof.stderr)

    def test_nonce_handoff_is_single_spawn_and_claimable(self) -> None:
        self.write_checkpoint("reference-only", goal())
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        goal_path = self.write_goal()
        self.run_state("set-goal", "--objective-file", str(goal_path))
        next_goal = self.root / "next-goal.md"
        next_goal.write_text(goal().replace("one bounded result", "the next bounded result"), encoding="utf-8")
        first = json.loads(self.run_state(
            "prepare-handoff", "--kind", "next-goal", "--nonce", "n1",
            "--reason", "completed-goal", "--source-goal-state", "completed",
            "--completion-evidence", "tests/current-goal-proof.json",
            "--next-goal-id", "next-goal", "--next-objective-file", str(next_goal),
            "--first-command", "run-next-proof",
        ).stdout)
        self.assertTrue(first["spawn_allowed"])
        duplicate = json.loads(self.run_state("prepare-handoff", "--kind", "next-goal").stdout)
        self.assertFalse(duplicate["spawn_allowed"])
        self.assertEqual(duplicate["reason"], "handoff_already_pending")
        self.run_state("record-successor", "--nonce", "n1", "--thread-id", "thread-1")
        entry = json.loads(self.run_entry("--claim-nonce", "n1").stdout)
        claimed = entry["claim_receipt"]
        self.assertEqual(claimed["hop"], 2)
        self.assertEqual(claimed["kind"], "next-goal")
        self.assertEqual(claimed["handoff_reason"], "completed-goal")
        self.assertEqual(claimed["source_goal_state"], "completed")
        self.assertEqual(claimed["execution_owner_thread_id"], "thread-1")
        self.assertEqual(claimed["goal_id"], "next-goal")
        self.assertNotIn("next_goal_objective", claimed)
        claimed_goal = Path(claimed["goal_file"])
        self.assertEqual(claimed_goal.read_text(encoding="utf-8").rstrip(), next_goal.read_text(encoding="utf-8").rstrip())
        self.assertEqual(claimed["first_command"], "run-next-proof")
        self.assertEqual(entry["chain_action"], "recover-claimed-handoff")
        self.assertEqual(entry["orchestration_action"], "execute-claimed-handoff")
        self.assertEqual(entry["route_receipt"]["goal_file"], str(claimed_goal))
        self.assertEqual(entry["route_receipt"]["reference_sections"], [])
        self.assertFalse(entry["route_receipt"]["full_workflow_read_required"])
        self.assertTrue(entry["route_receipt"]["state_transition_performed"])
        state = json.loads(self.run_state("status").stdout)
        self.assertIsNotNone(state["handoff"])
        self.assertEqual(state["goal_hash"], first["next_goal_hash"])
        self.assertEqual(state["metrics"]["handoffs_prepared"], 1)
        self.assertEqual(state["metrics"]["successors_created"], 1)
        self.assertEqual(state["metrics"]["duplicate_spawn_attempts"], 1)

        recovered = json.loads(self.run_state("claim", "--nonce", "n1").stdout)
        self.assertTrue(recovered["recovered"])
        self.assertEqual(len(json.loads(self.run_state("status").stdout)["history"]), 1)
        recovered_entry = json.loads(self.run_entry().stdout)
        self.assertEqual(recovered_entry["chain_action"], "recover-claimed-handoff")
        self.assertEqual(recovered_entry["chain"]["recovery"]["first_command"], "run-next-proof")

        without_terminal_newline = self.root / "extracted-goal.md"
        without_terminal_newline.write_text(claimed_goal.read_text(encoding="utf-8").rstrip(), encoding="utf-8")
        self.run_state("set-goal", "--objective-file", str(without_terminal_newline))
        settled = json.loads(self.run_state("status").stdout)
        self.assertIsNone(settled["handoff"])
        self.assertEqual(settled["goal_objective"], claimed_goal.read_text(encoding="utf-8"))
        self.assertEqual(settled["goal_id"], "next-goal")
        self.assertNotIn("next_goal_objective", settled["history"][0]["handoff"])

    def test_handoff_requires_terminal_source_goal_and_typed_reason(self) -> None:
        self.write_checkpoint("reference-only", goal())
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        self.run_state("set-goal", "--objective-file", str(self.write_goal()))

        role_switch = self.run_state(
            "prepare-handoff", "--kind", "continue-goal",
            "--reason", "role-switch", "--source-goal-state", "paused",
            "--first-command", "run-fixer", ok=False,
        )
        self.assertIn("handoff reason must be one of", role_switch.stderr)

        active_source = self.run_state(
            "prepare-handoff", "--kind", "continue-goal",
            "--reason", "context-exhausted", "--first-command", "continue-proof", ok=False,
        )
        self.assertIn("source Codex goal to be paused", active_source.stderr)

        next_goal = self.root / "next-goal.md"
        next_goal.write_text(
            goal().replace("one bounded result", "the next bounded result"),
            encoding="utf-8",
        )
        missing_completion = self.run_state(
            "prepare-handoff", "--kind", "next-goal",
            "--reason", "completed-goal", "--source-goal-state", "completed",
            "--next-goal-id", "next-goal", "--next-objective-file", str(next_goal),
            "--first-command", "run-next-proof", ok=False,
        )
        self.assertIn("completion evidence", missing_completion.stderr)

    def test_claimed_first_command_is_consumed_once_across_goal_settlement(self) -> None:
        objective = goal()
        self.write_checkpoint("reference-only", objective)
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        goal_path = self.write_goal()
        self.run_state("set-goal", "--objective-file", str(goal_path))
        self.run_state(
            "prepare-handoff", "--kind", "continue-goal", "--nonce", "once",
            "--reason", "context-exhausted", "--source-goal-state", "paused",
            "--first-command", "run-exact-proof",
        )
        self.run_state("record-successor", "--nonce", "once", "--thread-id", "thread-once")
        claimed = json.loads(self.run_state("claim", "--nonce", "once").stdout)
        command_hash = claimed["first_command_hash"]
        self.assertEqual(claimed["first_command_action"], "execute-once")

        self.run_state("set-goal", "--objective-file", str(goal_path))
        pending_entry = json.loads(self.run_entry().stdout)
        self.assertEqual(pending_entry["chain_action"], "execute-pending-command")
        self.assertEqual(pending_entry["orchestration_action"], "execute-pending-command")
        self.assertEqual(pending_entry["route_receipt"]["first_command"], "run-exact-proof")
        self.assertEqual(pending_entry["route_receipt"]["first_command_hash"], command_hash)

        wrong = self.run_state(
            "consume-command", "--command-hash", "wrong", "--result", "completed", ok=False,
        )
        self.assertIn("hash mismatch", wrong.stderr)
        consumed = json.loads(self.run_state(
            "consume-command", "--command-hash", command_hash, "--result", "completed",
        ).stdout)
        self.assertFalse(consumed["idempotent"])
        repeated = json.loads(self.run_state(
            "consume-command", "--command-hash", command_hash, "--result", "completed",
        ).stdout)
        self.assertTrue(repeated["idempotent"])

        after = json.loads(self.run_entry().stdout)
        self.assertIsNone(after["route_receipt"]["first_command"])
        self.assertNotEqual(after["chain_action"], "execute-pending-command")
        state = json.loads(self.run_state("status").stdout)
        self.assertEqual(len(state["command_history"]), 1)
        self.assertEqual(state["pending_command"]["command_hash"], command_hash)

    def test_scoped_proof_generations_and_nonterminal_proof_pause(self) -> None:
        objective = goal()
        self.write_checkpoint("reference-only", objective)
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        goal_path = self.write_goal()
        self.run_state("set-goal", "--goal-id", "test-goal", "--objective-file", str(goal_path))

        first = json.loads(self.run_state(
            "record-proof",
            "--scope", "customer-browser",
            "--proof-status", "pass",
            "--product-fingerprint", "product-v1",
            "--proof-environment-fingerprint", "browser-v1",
            "--result", "first customer pass",
            "--evidence", "evidence/customer-v1.json",
        ).stdout)
        duplicate = json.loads(self.run_state(
            "record-proof",
            "--scope", "customer-browser",
            "--proof-status", "pass",
            "--product-fingerprint", "product-v1",
            "--proof-environment-fingerprint", "browser-v1",
            "--result", "first customer pass",
            "--evidence", "evidence/customer-v1.json",
        ).stdout)
        self.assertTrue(duplicate["idempotent"])
        self.assertEqual(first["generation_id"], duplicate["generation_id"])

        second = json.loads(self.run_state(
            "record-proof",
            "--scope", "customer-browser",
            "--proof-status", "pass",
            "--product-fingerprint", "product-v2",
            "--proof-environment-fingerprint", "browser-v1",
            "--result", "pass after source change",
            "--evidence", "evidence/customer-v2.json",
        ).stdout)
        self.assertNotEqual(first["generation_id"], second["generation_id"])

        paused = json.loads(self.run_state(
            "pause-proof",
            "--owner", "repository-browser-owner",
            "--scope", "customer-browser",
            "--reason", "owned browser lease disappeared",
            "--next-command", "run-browser-owner-diagnostic",
            "--product-fingerprint", "product-v2",
            "--proof-environment-fingerprint", "browser-v1",
            "--evidence", "evidence/browser-blocker.json",
            "--recovery-used",
        ).stdout)
        self.assertEqual(paused["status"], "proof_blocked")
        self.assertTrue(paused["bounded_recovery_used"])

        entry = json.loads(self.run_entry().stdout)
        self.assertEqual(entry["chain_action"], "resume-proof-campaign")
        self.assertEqual(entry["orchestration_action"], "resume-proof-campaign")
        self.assertEqual(entry["exploration"]["action"], "skip")
        self.assertIsNone(entry["route_receipt"]["first_command"])
        self.assertEqual(
            entry["route_receipt"]["proof_blocker"]["next_command"],
            "run-browser-owner-diagnostic",
        )

        resumed = json.loads(self.run_state(
            "resume-proof", "--reason", "proof owner repaired and verified",
        ).stdout)
        self.assertEqual(resumed["status"], "active")
        self.assertEqual(resumed["first_command_action"], "execute-once")
        recovery_entry = json.loads(self.run_entry().stdout)
        self.assertEqual(recovery_entry["chain_action"], "execute-pending-command")
        self.assertEqual(
            recovery_entry["route_receipt"]["first_command"],
            "run-browser-owner-diagnostic",
        )
        self.run_state(
            "consume-command",
            "--command-hash", resumed["first_command_hash"],
            "--result", "completed",
        )

        final = json.loads(self.run_state(
            "record-proof",
            "--scope", "customer-browser",
            "--proof-status", "pass",
            "--product-fingerprint", "product-v2",
            "--proof-environment-fingerprint", "browser-v2",
            "--result", "customer pass after proof-owner repair",
            "--evidence", "evidence/customer-v2-browser-v2.json",
        ).stdout)
        state = json.loads(self.run_state("status").stdout)
        self.assertEqual(state["hop"], 1)
        self.assertEqual(len(state["proof_history"]), 1)
        self.assertEqual(state["proof_current"]["customer-browser"], final["generation_id"])
        self.assertEqual(len(state["proof_generations"]), 4)
        self.assertEqual(state["proof_generations"][0]["superseded_by"], second["generation_id"])

    def test_final_acceptance_requires_frozen_contract_and_immutable_artifact_root(self) -> None:
        self.run_state("init", "--max-hops", "1", "--phase-boundary", "Acceptance")
        goal_path = self.write_goal()
        self.run_state("set-goal", "--goal-id", "test-goal", "--objective-file", str(goal_path))

        missing = self.run_state(
            "record-proof",
            "--scope", "customer-review",
            "--proof-status", "pass",
            "--product-fingerprint", "product-v1",
            "--result", "blind review passed",
            "--evidence", "output/acceptance/product-v1/review.json",
            "--final-acceptance",
            ok=False,
        )
        self.assertIn("requires freeze-proof readiness", missing.stderr)

        frozen = json.loads(self.run_state(
            "freeze-proof",
            "--product-fingerprint", "product-v1",
            "--acceptance-contract", "owner plan: profile acceptance",
            "--proof-owner", "repo customer-review route",
            "--artifact-root", "output/acceptance/product-v1",
            "--evidence", "tests/proof-contract-review.json",
        ).stdout)
        self.assertFalse(frozen["idempotent"])

        wrong_root = self.run_state(
            "record-proof",
            "--scope", "customer-review",
            "--proof-status", "pass",
            "--product-fingerprint", "product-v1",
            "--result", "blind review passed",
            "--evidence", "output/latest/review.json",
            "--final-acceptance",
            ok=False,
        )
        self.assertIn("frozen artifact root", wrong_root.stderr)

        first = json.loads(self.run_state(
            "record-proof",
            "--scope", "customer-review",
            "--proof-status", "pass",
            "--product-fingerprint", "product-v1",
            "--result", "blind review passed",
            "--evidence", "output/acceptance/product-v1/review.json",
            "--final-acceptance",
        ).stdout)
        self.assertTrue(first["final_acceptance"])

        self.run_state(
            "freeze-proof",
            "--product-fingerprint", "product-v2",
            "--acceptance-contract", "owner plan: profile acceptance",
            "--proof-owner", "repo customer-review route",
            "--artifact-root", "output/acceptance/product-v2",
            "--evidence", "tests/proof-contract-review-v2.json",
        )
        self.run_state(
            "record-proof",
            "--scope", "customer-review",
            "--proof-status", "pass",
            "--product-fingerprint", "product-v2",
            "--result", "blind review passed after one batched fix",
            "--evidence", "output/acceptance/product-v2/review.json",
            "--final-acceptance",
        )
        state = json.loads(self.run_state("status").stdout)
        self.assertEqual(state["metrics"]["source_freezes"], 2)
        self.assertEqual(state["metrics"]["post_freeze_source_mutations"], 1)
        self.assertEqual(state["metrics"]["review_cycles"], 2)
        self.assertEqual(state["metrics"]["proof_reruns"], 1)

    def test_authority_pause_preserves_and_reactivates_the_same_goal(self) -> None:
        self.write_checkpoint("ensure-active", goal())
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        goal_path = self.write_goal()
        self.run_state("set-goal", "--objective-file", str(goal_path))
        original = json.loads(self.run_state("status").stdout)
        state_path = self.root / ".session" / "ORCHESTRATION.json"
        legacy_state = json.loads(state_path.read_text(encoding="utf-8"))
        legacy_state["goal_objective"] = None
        state_path.write_text(json.dumps(legacy_state), encoding="utf-8")

        paused = json.loads(self.run_state(
            "await-authority",
            "--goal-file", str(goal_path),
            "--reason", "operator authentication required",
            "--next-command", "run-production-proof",
        ).stdout)
        self.assertEqual(paused["status"], "awaiting_authority")
        entry = json.loads(self.run_entry().stdout)
        self.assertEqual(entry["chain_action"], "await-operator-authority")
        self.assertEqual(entry["orchestration_action"], "await-operator-authority")
        self.assertEqual(entry["exploration"]["action"], "skip")
        self.assertEqual(entry["route_receipt"]["goal_file"], entry["chain"]["recovery"]["goal_file"])

        resumed = json.loads(self.run_state(
            "resume-authority", "--reason", "operator supplied the required authority",
        ).stdout)
        self.assertEqual(resumed["status"], "active")
        after = json.loads(self.run_state("status").stdout)
        self.assertEqual(after["goal_hash"], original["goal_hash"])
        self.assertEqual(after["hop"], original["hop"])
        self.assertEqual(len(after["authority_history"]), 1)

    def test_legacy_authority_stop_requires_exact_goal_to_resume(self) -> None:
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        goal_path = self.write_goal()
        self.run_state("set-goal", "--goal-id", "test-goal", "--objective-file", str(goal_path))
        self.run_state("stop", "--status", "stopped", "--reason", "authentication authority required")
        wrong = self.root / "wrong.md"
        wrong.write_text(goal().replace("one bounded result", "a wrong result"), encoding="utf-8")
        rejected = self.run_state(
            "resume-authority", "--legacy-authority-stop", "--goal-file", str(wrong),
            "--reason", "operator supplied authority", ok=False,
        )
        self.assertIn("goal hash mismatch", rejected.stderr)

        resumed = json.loads(self.run_state(
            "resume-authority", "--legacy-authority-stop", "--goal-file", str(goal_path),
            "--reason", "operator supplied authority",
        ).stdout)
        self.assertEqual(resumed["status"], "active")
        state = json.loads(self.run_state("status").stdout)
        self.assertEqual(state["goal_id"], "test-goal")
        self.assertEqual(state["hop"], 1)

    def test_next_goal_handoff_requires_an_admitted_exact_goal(self) -> None:
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        self.run_state("set-goal", "--objective-file", str(self.write_goal()))
        missing = self.run_state(
            "prepare-handoff", "--kind", "next-goal",
            "--reason", "completed-goal", "--source-goal-state", "completed",
            "--completion-evidence", "tests/current-goal-proof.json",
            "--first-command", "run-next-proof", ok=False,
        )
        self.assertIn("requires --next-objective-file", missing.stderr)

        tiny = self.root / "tiny-next.md"
        tiny.write_text("## Outcome\nInspect existing work.\n", encoding="utf-8")
        rejected = self.run_state(
            "prepare-handoff", "--kind", "next-goal", "--next-goal-id", "tiny-next",
            "--reason", "completed-goal", "--source-goal-state", "completed",
            "--completion-evidence", "tests/current-goal-proof.json",
            "--next-objective-file", str(tiny),
            "--first-command", "inspect", ok=False,
        )
        self.assertIn("failed admission", rejected.stderr)

    def test_claimed_handoff_uses_narrow_revalidation_when_owner_source_changed(self) -> None:
        self.write_checkpoint("reference-only", goal())
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        self.run_state("set-goal", "--objective-file", str(self.write_goal()))
        next_goal = self.root / "next-goal.md"
        next_goal.write_text(goal().replace("one bounded result", "the next bounded result"), encoding="utf-8")
        self.run_state(
            "prepare-handoff", "--kind", "next-goal", "--nonce", "stale-nonce",
            "--reason", "completed-goal", "--source-goal-state", "completed",
            "--completion-evidence", "tests/current-goal-proof.json",
            "--next-goal-id", "next-goal", "--next-objective-file", str(next_goal),
            "--first-command", "run-next-proof",
        )
        self.run_state("record-successor", "--nonce", "stale-nonce", "--thread-id", "thread-2")
        (self.root / "docs" / "PRODUCTPLAN.md").write_text("# Product plan\n\nChanged owner gate.\n", encoding="utf-8")

        output = json.loads(self.run_entry("--claim-nonce", "stale-nonce").stdout)
        self.assertEqual(output["chain_action"], "recover-claimed-handoff")
        self.assertEqual(output["orchestration_action"], "revalidate-claimed-handoff")
        self.assertEqual(output["exploration"]["action"], "skip")
        self.assertEqual(output["route_receipt"]["reference_sections"], ["Source precedence"])
        self.assertTrue(Path(output["route_receipt"]["goal_file"]).is_file())

    def test_wrong_nonce_cannot_claim(self) -> None:
        self.run_state("init", "--max-hops", "3", "--phase-boundary", "Phase 5")
        self.run_state("set-goal", "--objective-file", str(self.write_goal()))
        self.run_state(
            "prepare-handoff", "--kind", "continue-goal", "--nonce", "right",
            "--reason", "compaction-boundary", "--source-goal-state", "paused",
            "--first-command", "continue-proof",
        )
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

    def test_phase_goal_budget_accepts_twelve_and_rejects_thirteen(self) -> None:
        accepted = self.run_state("init", "--max-hops", "12", "--phase-boundary", "Phase 5")
        self.assertEqual(json.loads(accepted.stdout)["max_hops"], 12)
        rejected = self.run_state("init", "--max-hops", "13", "--phase-boundary", "Phase 5", ok=False)
        self.assertNotEqual(rejected.returncode, 0)

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
        saved = (self.root / ".session" / "CURRENT.md").read_text(encoding="utf-8")
        self.assertIn(goal_path.read_text(encoding="utf-8").rstrip(), saved)
        self.assertIn("resume_policy: ensure-active", saved)
        self.assertIn("**resume_window_hours:** 24", saved)

    def test_record_metric_works_after_stop(self) -> None:
        self.run_state("init", "--max-hops", "1", "--phase-boundary", "Phase 5")
        self.run_state("stop", "--status", "stopped", "--reason", "trial complete")
        result = json.loads(self.run_state("record-metric", "--name", "operator_repairs", "--increment", "3").stdout)
        self.assertEqual(result["value"], 3)


if __name__ == "__main__":
    unittest.main()
