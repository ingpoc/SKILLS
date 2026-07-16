#!/usr/bin/env python3
from __future__ import annotations

import json
import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

from session_workspace import ensure_workspace, git_root


HERE = Path(__file__).resolve().parent
SKILLS_REPOSITORY_ROOT = HERE.parents[1]
INSPECTOR = HERE.parent.parent / "resume-session" / "scripts" / "inspect_checkpoint.py"
INVENTORY = HERE / "project_inventory.py"
EXPLORATION_CONFLICT_REASONS = {
    "chain_completed",
    "chain_goal_hash_mismatch",
    "chain_goal_hash_missing",
    "program_already_complete",
    "program_goal_blocked",
}


def project_root(explicit: Path | None = None) -> Path:
    root = git_root(Path.cwd().resolve())
    if root is None:
        raise ValueError("session-orchestrate requires invocation from a Git product repository")
    if explicit:
        explicit_root = git_root(explicit.expanduser().resolve())
        if explicit_root is None:
            raise ValueError("the explicit session-orchestrate root is not a Git repository")
        if explicit_root != root:
            raise ValueError("the explicit session-orchestrate root does not match the current repository")
    if root == SKILLS_REPOSITORY_ROOT:
        raise ValueError("refusing to orchestrate the global skills repository; run from the product repository or pass --root")
    return root


def checkpoint_inspection(root: Path) -> dict[str, Any]:
    command = [sys.executable, str(INSPECTOR), "--write-goal-file", "--root", str(root)]
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "checkpoint inspector failed")
    return json.loads(result.stdout)


def project_inventory(root: Path) -> dict[str, Any]:
    command = [sys.executable, str(INVENTORY), "--root", str(root), "--detail", "cheap"]
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "project inventory failed")
    return json.loads(result.stdout)


def read_chain(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("invalid orchestration state")
    return data


def chain_action(state: dict[str, Any] | None, mode: str) -> str:
    if mode == "review-checkpoint":
        return "review-current-owner"
    if not state:
        return "init-new-chain"
    handoff = state.get("handoff") or {}
    if state.get("status") == "active" and handoff.get("claimed_at"):
        return "recover-claimed-handoff"
    status = state.get("status")
    if mode == "resume-exact-goal":
        if status == "active":
            return "reuse-active-chain" if state.get("goal_hash") else "recover-unset-goal"
        if status == "handoff_pending":
            return "claim-pending-handoff"
        return "resume-goal-chain-closed"
    if (
        mode == "choose-next-goal"
        and status == "active"
        and not state.get("goal_hash")
        and not handoff
    ):
        return "recover-orphaned-chain"
    if status in {"active", "handoff_pending"}:
        return "review-active-chain"
    return "init-new-chain"


def chain_recovery(
    state: dict[str, Any] | None,
    action: str,
    workspace: dict[str, Any],
) -> dict[str, Any] | None:
    if not state:
        return None
    handoff = state.get("handoff") or {}
    if handoff.get("claimed_at"):
        return {
            "kind": handoff.get("kind"),
            "nonce": handoff.get("nonce"),
            "next_goal_objective": handoff.get("next_goal_objective"),
            "first_command": handoff.get("first_command"),
        }
    if action == "recover-orphaned-chain":
        rebuild = workspace.get("program_action") == "rebuild-plan"
        return {
            "kind": "orphaned-active-chain",
            "selected_goal_id": None if rebuild else workspace.get("selected_goal_id"),
            "selected_goal_delivery_unit": (
                None if rebuild else workspace.get("selected_goal_delivery_unit")
            ),
            "selected_goal_lifecycle_stages": (
                [] if rebuild else workspace.get("selected_goal_lifecycle_stages", [])
            ),
            "next_action": "rebuild-program-map" if rebuild else "admission-probe-selected-goal",
            "reuse_chain": True,
            "set_goal_required": True,
        }
    return None


def downgrade(inspection: dict[str, Any], reason: str) -> None:
    goal_file = inspection.get("goal_file")
    if goal_file:
        Path(goal_file).unlink(missing_ok=True)
    inspection["goal_file"] = None
    inspection["eligibility"] = "conflict"
    inspection["mode"] = "review-checkpoint"
    inspection["reasons"] = list(dict.fromkeys([*(inspection.get("reasons") or []), reason]))


def exploration_route(workspace: dict[str, Any], inspection: dict[str, Any]) -> dict[str, Any]:
    reasons = set(inspection.get("reasons") or [])
    goal_count = sum((workspace.get("goal_counts") or {}).values())
    bootstrap = not workspace.get("plan_sources") and goal_count == 0
    if reasons & EXPLORATION_CONFLICT_REASONS:
        action = "conflict"
        reason = "checkpoint-chain-program-conflict"
    elif workspace.get("program_action") == "rebuild-plan" and bootstrap:
        action = "first-migration"
        reason = "program-map-missing"
    elif workspace.get("program_action") == "rebuild-plan":
        action = "stale-rebuild"
        reason = "program-map-stale"
    else:
        return {
            "action": "skip",
            "reason": "fresh-or-terminal-program-state",
            "decision_owner": "main-agent",
        }
    return {
        "action": action,
        "reason": reason,
        "decision_owner": "main-agent",
        "agent_type": "explorer",
        "agent_config_owner": "~/.codex/agents/explorer.toml",
        "spawn_policy": "conditional",
        "constraints": [
            "read-only",
            "use deterministic owner reads first",
            "persist only main-agent-validated findings",
            "collect existing result before retry",
            "no recursive codex exec fallback",
        ],
    }


def orchestration_action(mode: str, chain: str, workspace: dict[str, Any]) -> str:
    if mode == "review-checkpoint":
        return "review-current-owner"
    if chain == "recover-orphaned-chain":
        return "rebuild-program-map" if workspace.get("program_action") == "rebuild-plan" else "admission-probe-selected-goal"
    if mode == "resume-exact-goal":
        return "resume-exact-goal"
    program = workspace.get("program_action")
    if program == "rebuild-plan":
        return "rebuild-program-map"
    if program == "product-complete":
        return "verify-product-completion"
    if program == "review-blocked-goal":
        return "review-blocked-goal"
    if workspace.get("selection_probe"):
        return "rerun-selection-probe"
    return "admission-probe-selected-goal"


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve session-orchestrate entry state")
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    try:
        root = project_root(args.root)
        workspace = ensure_workspace(root)
        inspection = checkpoint_inspection(root)
        state_path = Path(workspace["paths"]["orchestration"])
        state = read_chain(state_path)
        inventory = project_inventory(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"entry: {exc}", file=sys.stderr)
        return 1

    if inspection.get("mode") == "resume-exact-goal" and state:
        recorded_hash = state.get("goal_hash")
        if state.get("status") == "completed":
            downgrade(inspection, "chain_completed")
        elif recorded_hash and recorded_hash != inspection.get("goal_hash"):
            downgrade(inspection, "chain_goal_hash_mismatch")
        elif state.get("status") == "active" and not recorded_hash:
            inspection["reasons"] = list(dict.fromkeys([
                *(inspection.get("reasons") or []),
                "chain_goal_hash_unset_recoverable",
            ]))
        elif state.get("status") in {"handoff_pending", "stopped", "blocked"} and not recorded_hash:
            downgrade(inspection, "chain_goal_hash_missing")

    if inspection.get("mode") == "resume-exact-goal":
        if workspace.get("program_action") == "rebuild-plan":
            downgrade(inspection, "program_state_stale")
        elif workspace.get("program_action") == "product-complete":
            downgrade(inspection, "program_already_complete")
        elif workspace.get("program_action") == "review-blocked-goal":
            downgrade(inspection, "program_goal_blocked")

    mode = inspection["mode"]
    action = chain_action(state, mode)
    if action == "recover-orphaned-chain":
        inspection["reasons"] = list(dict.fromkeys([
            *(inspection.get("reasons") or []),
            "active_chain_goal_unset_recoverable",
        ]))
    output = {
        **inspection,
        "invocation_authority": "orphaned-chain-recovery" if action == "recover-orphaned-chain" else {
            "resume-exact-goal": "saved-goal-only",
            "choose-next-goal": "new-bounded-chain",
            "review-checkpoint": "orchestration-only",
        }[mode],
        "chain_action": action,
        "orchestration_action": orchestration_action(mode, action, workspace),
        "workspace": workspace,
        "project_inventory": inventory,
        "exploration": exploration_route(workspace, inspection),
        "chain": None if not state else {
            "chain_id": state.get("chain_id"),
            "status": state.get("status"),
            "hop": state.get("hop"),
            "max_hops": state.get("max_hops"),
            "phase_boundary": state.get("phase_boundary"),
            "stop_reason": state.get("stop_reason"),
            "goal_hash": state.get("goal_hash"),
            "recovery": chain_recovery(state, action, workspace),
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
