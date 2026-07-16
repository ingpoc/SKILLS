#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = 1
ACTIVE = {"active", "handoff_pending"}
METRIC_NAMES = {
    "handoffs_prepared",
    "successors_created",
    "duplicate_spawn_attempts",
    "operator_repairs",
    "auto_compactions",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def project_root() -> Path:
    override = os.environ.get("SESSION_ORCHESTRATE_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip()).resolve()
    return Path.cwd().resolve()


def paths() -> tuple[Path, Path]:
    directory = project_root() / ".claude" / "session-data"
    return directory / "ORCHESTRATION.json", directory / "ORCHESTRATION.lock"


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
            "goal_hash": None,
            "handoff": None,
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
    objective = args.objective_file.read_text(encoding="utf-8")
    digest = "sha256:" + hashlib.sha256(objective.encode("utf-8")).hexdigest()
    with locked() as (path, state):
        if not state or state.get("status") != "active":
            return fail("set-goal requires an active chain")
        state["goal_hash"] = digest
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({"chain_id": state["chain_id"], "goal_hash": digest, "hop": state["hop"]})


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
            return emit({**handoff, "chain_id": state["chain_id"], "spawn_allowed": False, "reason": "handoff_already_pending"})
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

        handoff = {
            "kind": args.kind,
            "nonce": args.nonce or str(uuid.uuid4()),
            "pending_hop": int(state["hop"]) + 1,
            "successor_thread_id": None,
            "prepared_at": now(),
        }
        state["status"] = "handoff_pending"
        state["handoff"] = handoff
        metrics = state.setdefault("metrics", {})
        metrics["handoffs_prepared"] = int(metrics.get("handoffs_prepared", 0)) + 1
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({**handoff, "chain_id": state["chain_id"], "max_hops": state["max_hops"], "spawn_allowed": True})


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
        if not state or state.get("status") != "handoff_pending":
            return fail("no pending handoff to claim")
        handoff = state.get("handoff") or {}
        if handoff.get("nonce") != args.nonce:
            return fail("handoff nonce mismatch")
        if not handoff.get("successor_thread_id"):
            return fail("parent has not recorded the successor thread")
        state["history"].append({
            "hop": state["hop"],
            "goal_hash": state.get("goal_hash"),
            "handoff": handoff,
            "closed_at": now(),
        })
        state["hop"] = handoff["pending_hop"]
        state["status"] = "active"
        state["handoff"] = None
        state["goal_hash"] = None if handoff["kind"] == "next-goal" else state.get("goal_hash")
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({"chain_id": state["chain_id"], "hop": state["hop"], "kind": handoff["kind"], "status": "active"})


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
    command.add_argument("--max-hops", type=int, default=3, choices=range(1, 11))
    command.add_argument("--phase-boundary", required=True)
    command.set_defaults(handler=init)

    command = commands.add_parser("status")
    command.set_defaults(handler=status)

    command = commands.add_parser("set-goal")
    command.add_argument("--objective-file", type=Path, required=True)
    command.set_defaults(handler=set_goal)

    command = commands.add_parser("prepare-handoff")
    command.add_argument("--kind", choices=("next-goal", "continue-goal"), required=True)
    command.add_argument("--nonce")
    command.set_defaults(handler=prepare_handoff)

    command = commands.add_parser("record-successor")
    command.add_argument("--nonce", required=True)
    command.add_argument("--thread-id", required=True)
    command.set_defaults(handler=record_successor)

    command = commands.add_parser("claim")
    command.add_argument("--nonce", required=True)
    command.set_defaults(handler=claim)

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
