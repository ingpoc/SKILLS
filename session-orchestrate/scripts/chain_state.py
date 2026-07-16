#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import tempfile
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from session_workspace import atomic_text, canonical_paths, ensure_workspace, git_root
from validate_goal import (
    DELIVERY_UNITS,
    canonical_objective,
    objective_hash,
)
from validate_goal import (
    validate as validate_goal,
)

SCHEMA_VERSION = 1
ACTIVE = {"active", "handoff_pending", "awaiting_authority"}
SKILLS_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
METRIC_NAMES = {
    "handoffs_prepared",
    "successors_created",
    "duplicate_spawn_attempts",
    "operator_repairs",
    "auto_compactions",
}


def now() -> str:
    return datetime.now(UTC).isoformat()


def project_root() -> Path:
    override = os.environ.get("SESSION_ORCHESTRATE_ROOT", "").strip()
    if override:
        root = git_root(Path(override).expanduser().resolve())
        cwd_root = git_root(Path.cwd().resolve())
        if root is None:
            raise ValueError("SESSION_ORCHESTRATE_ROOT is not a Git repository")
        if cwd_root is not None and cwd_root != root:
            raise ValueError("SESSION_ORCHESTRATE_ROOT does not match the current repository")
    else:
        root = git_root(Path.cwd().resolve())
        if root is None:
            raise ValueError("session-orchestrate requires invocation from a Git product repository")
    if root == SKILLS_REPOSITORY_ROOT:
        raise ValueError("refusing to mutate orchestration state in the global skills repository")
    return root


def paths() -> tuple[Path, Path]:
    root = project_root()
    ensure_workspace(root)
    workspace = canonical_paths(root)
    return workspace["orchestration"], workspace["orchestration-lock"]


def read_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported or invalid orchestration state")
    return data


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp = Path(raw)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


@contextmanager
def locked() -> Iterator[tuple[Path, dict[str, Any] | None]]:
    state_path, lock_path = paths()
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        yield state_path, read_state(state_path)


def emit(data: dict[str, Any]) -> int:
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def fail(message: str) -> int:
    print(f"chain_state: {message}", file=sys.stderr)
    return 1


def materialize_goal(objective: str) -> Path:
    path = canonical_paths(project_root())["claimed-goal"]
    atomic_text(path, canonical_objective(objective))
    return path


def claim_receipt(state: dict[str, Any], handoff: dict[str, Any], *, recovered: bool) -> dict[str, Any]:
    objective = handoff.get("next_goal_objective") or state.get("goal_objective")
    if not objective:
        raise ValueError("claimed handoff has no exact goal objective")
    goal_file = materialize_goal(objective)
    return {
        "chain_id": state["chain_id"],
        "hop": state["hop"],
        "kind": handoff["kind"],
        "status": "active",
        "recovered": recovered,
        "goal_hash": state.get("goal_hash"),
        "goal_id": state.get("goal_id"),
        "goal_file": str(goal_file),
        "goal_chars": len(canonical_objective(objective)),
        "delivery_unit": handoff.get("next_delivery_unit"),
        "first_command": handoff.get("first_command"),
    }


def normalize_next_goal(state: dict[str, Any], handoff: dict[str, Any]) -> None:
    objective = handoff.get("next_goal_objective")
    if handoff.get("kind") != "next-goal" or not objective:
        return
    canonical = canonical_objective(objective)
    digest = objective_hash(canonical)
    handoff["next_goal_objective"] = canonical
    handoff["next_goal_hash"] = digest
    state["goal_objective"] = canonical
    state["goal_hash"] = digest
    if handoff.get("next_goal_id"):
        state["goal_id"] = handoff["next_goal_id"]


def public_handoff(handoff: dict[str, Any]) -> dict[str, Any]:
    receipt = {key: value for key, value in handoff.items() if key != "next_goal_objective"}
    objective = handoff.get("next_goal_objective")
    if objective:
        receipt["goal_chars"] = len(canonical_objective(objective))
    return receipt


def init(args: argparse.Namespace) -> int:
    with locked() as (path, state):
        if state and state.get("status") in ACTIVE:
            return fail(f"active chain already exists: {state.get('chain_id')}")
        stamp = now()
        state = {
            "schema_version": SCHEMA_VERSION,
            "chain_id": args.chain_id or str(uuid.uuid4()),
            "project_root": str(project_root()),
            "status": "active",
            "hop": 1,
            "max_hops": args.max_hops,
            "phase_boundary": args.phase_boundary,
            "goal_id": None,
            "goal_hash": None,
            "goal_objective": None,
            "handoff": None,
            "authority": None,
            "history": [],
            "metrics": {name: 0 for name in sorted(METRIC_NAMES)},
            "created_at": stamp,
            "updated_at": stamp,
        }
        atomic_write(path, state)
        return emit(state)


def status(_: argparse.Namespace) -> int:
    path, _ = paths()
    try:
        state = read_state(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return fail(str(exc))
    if state is None:
        return fail("no orchestration state")
    return emit(state)


def set_goal(args: argparse.Namespace) -> int:
    objective = canonical_objective(args.objective_file.read_text(encoding="utf-8"))
    digest = objective_hash(objective)
    with locked() as (path, state):
        if not state or state.get("status") != "active":
            return fail("set-goal requires an active chain")
        handoff = state.get("handoff") or {}
        if handoff.get("claimed_at"):
            expected = handoff.get("next_goal_hash") or state.get("goal_hash")
            if expected and digest != expected:
                return fail("claimed handoff goal hash mismatch")
        elif state.get("goal_hash") and state.get("goal_hash") != digest:
            return fail("active chain is already bound to a different goal")
        if args.goal_id and state.get("goal_id") and state["goal_id"] != args.goal_id:
            return fail("active chain is already bound to a different goal id")
        if args.goal_id:
            state["goal_id"] = args.goal_id
        state["goal_hash"] = digest
        state["goal_objective"] = objective
        if handoff.get("claimed_at"):
            state["handoff"] = None
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({
            "chain_id": state["chain_id"],
            "goal_id": state.get("goal_id"),
            "goal_hash": digest,
            "hop": state["hop"],
        })


def prepare_handoff(args: argparse.Namespace) -> int:
    with locked() as (path, state):
        if not state:
            return fail("no orchestration state")
        if state.get("status") == "handoff_pending":
            metrics = state.setdefault("metrics", {})
            metrics["duplicate_spawn_attempts"] = int(metrics.get("duplicate_spawn_attempts", 0)) + 1
            state["updated_at"] = now()
            atomic_write(path, state)
            handoff = state.get("handoff") or {}
            return emit({**public_handoff(handoff), "chain_id": state["chain_id"], "spawn_allowed": False, "reason": "handoff_already_pending"})
        if state.get("status") != "active":
            return fail(f"chain is not active: {state.get('status')}")
        if not state.get("goal_hash"):
            return fail("set the exact goal hash before preparing a handoff")
        if int(state["hop"]) >= int(state["max_hops"]):
            state["status"] = "stopped"
            state["stop_reason"] = "max_hops_reached"
            state["updated_at"] = now()
            atomic_write(path, state)
            return emit({"chain_id": state["chain_id"], "spawn_allowed": False, "reason": "max_hops_reached"})
        if not args.first_command:
            return fail("handoff requires --first-command")

        next_objective = None
        next_digest = None
        if args.kind == "next-goal":
            if not args.next_objective_file:
                return fail("next-goal handoff requires --next-objective-file")
            if not args.next_goal_id:
                return fail("next-goal handoff requires --next-goal-id")
            next_objective = canonical_objective(args.next_objective_file.read_text(encoding="utf-8"))
            errors = validate_goal(next_objective, delivery_unit=args.next_delivery_unit)
            if errors:
                return fail("next goal failed admission: " + "; ".join(errors))
            next_digest = objective_hash(next_objective)
        elif args.kind == "continue-goal":
            next_objective = state.get("goal_objective")
            if not next_objective:
                return fail("continue-goal requires the exact objective; re-run set-goal once")
            next_digest = state.get("goal_hash") or objective_hash(next_objective)

        handoff = {
            "kind": args.kind,
            "nonce": args.nonce or str(uuid.uuid4()),
            "pending_hop": int(state["hop"]) + 1,
            "successor_thread_id": None,
            "first_command": args.first_command,
            "prepared_at": now(),
        }
        if next_objective is not None:
            handoff["next_goal_objective"] = next_objective
            handoff["next_goal_hash"] = next_digest
            if args.kind == "next-goal":
                handoff["next_delivery_unit"] = args.next_delivery_unit
                handoff["next_goal_id"] = args.next_goal_id
        state["status"] = "handoff_pending"
        state["handoff"] = handoff
        metrics = state.setdefault("metrics", {})
        metrics["handoffs_prepared"] = int(metrics.get("handoffs_prepared", 0)) + 1
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({**public_handoff(handoff), "chain_id": state["chain_id"], "max_hops": state["max_hops"], "spawn_allowed": True})


def record_successor(args: argparse.Namespace) -> int:
    with locked() as (path, state):
        if not state or state.get("status") != "handoff_pending":
            return fail("no pending handoff")
        handoff = state.get("handoff") or {}
        if handoff.get("nonce") != args.nonce:
            return fail("handoff nonce mismatch")
        existing = handoff.get("successor_thread_id")
        if existing and existing != args.thread_id:
            return fail(f"successor already recorded: {existing}")
        handoff["successor_thread_id"] = args.thread_id
        state["handoff"] = handoff
        metrics = state.setdefault("metrics", {})
        if not existing:
            metrics["successors_created"] = int(metrics.get("successors_created", 0)) + 1
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({"chain_id": state["chain_id"], "successor_thread_id": args.thread_id, "recorded": True})


def claim(args: argparse.Namespace) -> int:
    with locked() as (path, state):
        if not state:
            return fail("no pending handoff to claim")
        existing = state.get("handoff") or {}
        if state.get("status") == "active" and existing.get("claimed_at"):
            if existing.get("nonce") != args.nonce:
                return fail("handoff nonce mismatch")
            normalize_next_goal(state, existing)
            state["handoff"] = existing
            state["updated_at"] = now()
            atomic_write(path, state)
            return emit(claim_receipt(state, existing, recovered=True))
        if state.get("status") != "handoff_pending":
            return fail("no pending handoff to claim")
        handoff = state.get("handoff") or {}
        if handoff.get("nonce") != args.nonce:
            return fail("handoff nonce mismatch")
        if not handoff.get("successor_thread_id"):
            return fail("parent has not recorded the successor thread")
        normalize_next_goal(state, handoff)
        history_handoff = {key: value for key, value in handoff.items() if key != "next_goal_objective"}
        state.setdefault("history", []).append({
            "hop": state["hop"],
            "goal_hash": state.get("goal_hash"),
            "handoff": history_handoff,
            "closed_at": now(),
        })
        state["hop"] = handoff["pending_hop"]
        state["status"] = "active"
        handoff["claimed_at"] = now()
        state["handoff"] = handoff
        if handoff["kind"] == "next-goal":
            normalize_next_goal(state, handoff)
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit(claim_receipt(state, handoff, recovered=False))


def await_authority(args: argparse.Namespace) -> int:
    with locked() as (path, state):
        if not state or state.get("status") != "active":
            return fail("await-authority requires an active chain")
        if not state.get("goal_objective") and args.goal_file:
            objective = canonical_objective(args.goal_file.read_text(encoding="utf-8"))
            digest = objective_hash(objective)
            if state.get("goal_hash") and state["goal_hash"] != digest:
                return fail("authority goal hash mismatch")
            state["goal_hash"] = digest
            state["goal_objective"] = objective
        if not state.get("goal_hash") or not state.get("goal_objective"):
            return fail("await-authority requires an exact active goal")
        state["status"] = "awaiting_authority"
        state["authority"] = {
            "reason": args.reason,
            "next_command": args.next_command,
            "paused_at": now(),
        }
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({
            "chain_id": state["chain_id"],
            "status": state["status"],
            "goal_id": state.get("goal_id"),
            **state["authority"],
        })


def resume_authority(args: argparse.Namespace) -> int:
    with locked() as (path, state):
        if not state:
            return fail("resume-authority requires orchestration state")
        if state.get("status") == "awaiting_authority":
            authority = state.get("authority") or {}
        elif args.legacy_authority_stop and state.get("status") in {"stopped", "blocked"}:
            if not args.goal_file:
                return fail("legacy authority resume requires --goal-file")
            objective = canonical_objective(args.goal_file.read_text(encoding="utf-8"))
            digest = objective_hash(objective)
            if state.get("goal_hash") and state["goal_hash"] != digest:
                return fail("legacy authority goal hash mismatch")
            state["goal_hash"] = digest
            state["goal_objective"] = objective
            authority = {
                "reason": state.get("stop_reason"),
                "paused_at": state.get("updated_at"),
                "legacy_status": state.get("status"),
            }
        else:
            return fail("resume-authority requires an authority pause")
        authority["resumed_at"] = now()
        authority["resume_reason"] = args.reason
        state.setdefault("authority_history", []).append(authority)
        state["authority"] = None
        state["status"] = "active"
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({
            "chain_id": state["chain_id"],
            "status": state["status"],
            "goal_id": state.get("goal_id"),
            "goal_hash": state.get("goal_hash"),
            "goal_file": str(materialize_goal(state["goal_objective"])),
        })


def stop(args: argparse.Namespace) -> int:
    with locked() as (path, state):
        if not state:
            return fail("no orchestration state")
        state["status"] = args.status
        state["stop_reason"] = args.reason
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({"chain_id": state["chain_id"], "status": args.status, "reason": args.reason})


def record_metric(args: argparse.Namespace) -> int:
    with locked() as (path, state):
        if not state:
            return fail("no orchestration state")
        metrics = state.setdefault("metrics", {})
        metrics[args.name] = int(metrics.get(args.name, 0)) + args.increment
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({"chain_id": state["chain_id"], "metric": args.name, "value": metrics[args.name]})


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Manage bounded session-orchestrate state")
    commands = root.add_subparsers(dest="command", required=True)

    command = commands.add_parser("init")
    command.add_argument("--chain-id")
    command.add_argument("--max-hops", type=int, default=3, choices=range(1, 13))
    command.add_argument("--phase-boundary", required=True)
    command.set_defaults(handler=init)

    command = commands.add_parser("status")
    command.set_defaults(handler=status)

    command = commands.add_parser("set-goal")
    command.add_argument("--objective-file", type=Path, required=True)
    command.add_argument("--goal-id")
    command.set_defaults(handler=set_goal)

    command = commands.add_parser("prepare-handoff")
    command.add_argument("--kind", choices=("next-goal", "continue-goal"), required=True)
    command.add_argument("--nonce")
    command.add_argument("--next-objective-file", type=Path)
    command.add_argument("--next-goal-id")
    command.add_argument("--next-delivery-unit", choices=DELIVERY_UNITS, default="bounded-deliverable")
    command.add_argument("--first-command")
    command.set_defaults(handler=prepare_handoff)

    command = commands.add_parser("record-successor")
    command.add_argument("--nonce", required=True)
    command.add_argument("--thread-id", required=True)
    command.set_defaults(handler=record_successor)

    command = commands.add_parser("claim")
    command.add_argument("--nonce", required=True)
    command.set_defaults(handler=claim)

    command = commands.add_parser("await-authority")
    command.add_argument("--reason", required=True)
    command.add_argument("--next-command", required=True)
    command.add_argument("--goal-file", type=Path)
    command.set_defaults(handler=await_authority)

    command = commands.add_parser("resume-authority")
    command.add_argument("--reason", required=True)
    command.add_argument("--goal-file", type=Path)
    command.add_argument("--legacy-authority-stop", action="store_true")
    command.set_defaults(handler=resume_authority)

    command = commands.add_parser("stop")
    command.add_argument("--status", choices=("completed", "blocked", "stopped"), required=True)
    command.add_argument("--reason", required=True)
    command.set_defaults(handler=stop)

    command = commands.add_parser("record-metric")
    command.add_argument("--name", choices=sorted(METRIC_NAMES), required=True)
    command.add_argument("--increment", type=int, default=1)
    command.set_defaults(handler=record_metric)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return fail(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
