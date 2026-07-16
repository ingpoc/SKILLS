#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from session_workspace import atomic_text, ensure_workspace, git_root
from validate_goal import canonical_objective

HERE = Path(__file__).resolve().parent
SKILLS_REPOSITORY_ROOT = HERE.parents[1]
INSPECTOR = HERE.parent.parent / "resume-session" / "scripts" / "inspect_checkpoint.py"
INVENTORY = HERE / "project_inventory.py"
CHAIN_STATE = HERE / "chain_state.py"
WORKFLOW = HERE.parent / "references" / "workflow.md"
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
        capture_output=True,
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
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "project inventory failed")
    return json.loads(result.stdout)


def claim_handoff(root: Path, nonce: str) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(CHAIN_STATE), "claim", "--nonce", nonce],
        cwd=root,
        env={**os.environ, "SESSION_ORCHESTRATE_ROOT": str(root)},
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "handoff claim failed")
    return json.loads(result.stdout)


def read_chain(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("invalid orchestration state")
    return data


def chain_action(state: dict[str, Any] | None, mode: str) -> str:
    if not state:
        return "review-current-owner" if mode == "review-checkpoint" else "init-new-chain"
    handoff = state.get("handoff") or {}
    if state.get("status") == "awaiting_authority":
        return "await-operator-authority"
    if state.get("status") == "blocked":
        return "review-closed-chain"
    if state.get("status") == "active" and handoff.get("claimed_at"):
        return "recover-claimed-handoff"
    if mode == "review-checkpoint":
        return "review-current-owner"
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
        objective = handoff.get("next_goal_objective") or state.get("goal_objective")
        goal_file = None
        if objective:
            goal_file = Path(workspace["paths"]["claimed-goal"])
            atomic_text(goal_file, canonical_objective(objective))
        return {
            "kind": handoff.get("kind"),
            "nonce": handoff.get("nonce"),
            "goal_file": None if goal_file is None else str(goal_file),
            "goal_hash": state.get("goal_hash"),
            "delivery_unit": handoff.get("next_delivery_unit"),
            "first_command": handoff.get("first_command"),
        }
    if state.get("status") == "awaiting_authority":
        objective = state.get("goal_objective")
        goal_file = None
        if objective:
            goal_file = Path(workspace["paths"]["claimed-goal"])
            atomic_text(goal_file, canonical_objective(objective))
        return {
            "kind": "authority-pause",
            "goal_file": None if goal_file is None else str(goal_file),
            "goal_hash": state.get("goal_hash"),
            **(state.get("authority") or {}),
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


def exploration_route(
    workspace: dict[str, Any],
    inspection: dict[str, Any],
    chain_action_name: str,
) -> dict[str, Any]:
    if chain_action_name in {
        "recover-claimed-handoff",
        "await-operator-authority",
        "review-active-chain",
        "review-closed-chain",
    }:
        return {
            "action": "skip",
            "reason": chain_action_name,
            "decision_owner": "mechanical-chain-state",
        }
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
    if chain == "recover-claimed-handoff":
        return (
            "revalidate-claimed-handoff"
            if workspace.get("program_action") == "rebuild-plan"
            else "execute-claimed-handoff"
        )
    if chain == "claim-pending-handoff":
        return "claim-pending-handoff"
    if chain == "await-operator-authority":
        return "await-operator-authority"
    if chain == "review-closed-chain":
        return "review-closed-chain"
    if chain == "review-active-chain":
        return "review-active-goal"
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


REFERENCE_SECTIONS = {
    "review-current-owner": ["Entry lane", "Negative scenarios"],
    "rebuild-program-map": ["Source precedence", "Build the program map"],
    "resume-exact-goal": ["Entry lane", "Closeout lane"],
    "admission-probe-selected-goal": ["Choose and start one session goal"],
    "rerun-selection-probe": ["Choose and start one session goal"],
    "review-blocked-goal": ["Negative scenarios", "Mechanical stop"],
    "review-closed-chain": ["Closed chain review"],
    "review-active-goal": ["Active chain review"],
    "revalidate-claimed-handoff": ["Source precedence"],
    "verify-product-completion": ["Outcome contract", "Negative scenarios"],
}


def route_receipt(
    action: str,
    chain_action_name: str,
    workspace: dict[str, Any],
    inspection: dict[str, Any],
    state: dict[str, Any] | None,
    recovery: dict[str, Any] | None,
) -> dict[str, Any]:
    sections = REFERENCE_SECTIONS.get(action, [])
    identity = {
        "action": action,
        "chain_action": chain_action_name,
        "checkpoint_hash": inspection.get("goal_hash"),
        "goal_hash": None if not state else state.get("goal_hash"),
        "goal_id": None if not state else state.get("goal_id"),
        "hop": None if not state else state.get("hop"),
        "program_action": workspace.get("program_action"),
        "program_policy_version": workspace.get("program_policy_version"),
        "selected_goal_id": workspace.get("selected_goal_id"),
        "stale_reasons": workspace.get("stale_reasons") or [],
    }
    digest = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "id": f"sha256:{digest}",
        "action": action,
        "goal_file": (recovery or {}).get("goal_file") or inspection.get("goal_file"),
        "current_goal_id": None if not state else state.get("goal_id"),
        "first_command": (recovery or {}).get("first_command") or inspection.get("first_command"),
        "reference_sections": sections,
        "reference_command": None if not sections else (
            f"python3 {HERE / 'workflow_slice.py'} --action {action}"
        ),
        "goal_detail_argv": None if not workspace.get("selected_goal_id") else [
            sys.executable,
            str(HERE / "session_workspace.py"),
            "goal",
            "--root",
            workspace["project_root"],
            "--goal-id",
            workspace["selected_goal_id"],
        ],
        "full_workflow_read_required": False,
        "state_transition_performed": chain_action_name == "recover-claimed-handoff",
        "revalidate_only_after": [
            "owner source changed",
            "selector target changed",
            "chain state changed",
            "checkpoint eligibility changed",
        ],
        "evidence_budget": {
            "inline_chars": 12000,
            "inline_images": 1,
            "retain": "artifact path, stable id or hash, and concise result",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve session-orchestrate entry state")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--claim-nonce")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    try:
        root = project_root(args.root)
        workspace = ensure_workspace(root)
        claim_receipt = claim_handoff(root, args.claim_nonce) if args.claim_nonce else None
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
    if (
        action == "init-new-chain"
        and state
        and state.get("status") == "stopped"
        and workspace.get("program_action") == "review-blocked-goal"
    ):
        action = "review-closed-chain"
    if action == "recover-orphaned-chain":
        inspection["reasons"] = list(dict.fromkeys([
            *(inspection.get("reasons") or []),
            "active_chain_goal_unset_recoverable",
        ]))
    orchestration = orchestration_action(mode, action, workspace)
    recovery = chain_recovery(state, action, workspace)
    if action == "recover-orphaned-chain":
        invocation_authority = "orphaned-chain-recovery"
    elif action == "recover-claimed-handoff":
        invocation_authority = "claimed-handoff"
    elif action == "review-active-chain":
        invocation_authority = "active-chain-review"
    elif action == "review-closed-chain":
        invocation_authority = "closed-chain-review"
    elif action == "await-operator-authority":
        invocation_authority = "authority-pause"
    else:
        invocation_authority = {
            "resume-exact-goal": "saved-goal-only",
            "choose-next-goal": "new-bounded-chain",
            "review-checkpoint": "orchestration-only",
        }[mode]

    output = {
        **inspection,
        "invocation_authority": invocation_authority,
        "chain_action": action,
        "orchestration_action": orchestration,
        "claim_receipt": claim_receipt,
        "route_receipt": route_receipt(
            orchestration,
            action,
            workspace,
            inspection,
            state,
            recovery,
        ),
        "workspace": workspace,
        "project_inventory": inventory,
        "exploration": exploration_route(workspace, inspection, action),
        "chain": None if not state else {
            "chain_id": state.get("chain_id"),
            "status": state.get("status"),
            "hop": state.get("hop"),
            "max_hops": state.get("max_hops"),
            "phase_boundary": state.get("phase_boundary"),
            "stop_reason": state.get("stop_reason"),
            "goal_hash": state.get("goal_hash"),
            "goal_id": state.get("goal_id"),
            "recovery": recovery,
        },
    }
    if args.compact:
        owner_candidates = inventory.get("owner_routing_candidates") or []
        output["workspace"] = {
            key: workspace.get(key)
            for key in (
                "program_action",
                "program_status",
                "stale",
                "stale_reasons",
                "selected_goal_id",
                "selected_goal_delivery_unit",
                "selection_probe",
                "plan_sources",
            )
        }
        output["project_inventory"] = {
            "inventory_mode": inventory.get("inventory_mode"),
            "owner_routing_candidates": owner_candidates,
            "fallback_product_plan_candidates": (
                [] if owner_candidates else (inventory.get("product_plan_candidates") or [])[:5]
            ),
            "fallback_status_candidates": (
                [] if owner_candidates else (inventory.get("implementation_status_candidates") or [])[:5]
            ),
            "candidate_counts": {
                "product_plan": len(inventory.get("product_plan_candidates") or []),
                "implementation_status": len(inventory.get("implementation_status_candidates") or []),
            },
        }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
