#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
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

from session_workspace import atomic_text, canonical_paths, ensure_workspace, exact_git_root, git_root
from validate_goal import (
    DELIVERY_UNITS,
    canonical_objective,
    objective_hash,
)
from validate_goal import (
    validate as validate_goal,
)

SCHEMA_VERSION = 1
ACTIVE = {"active", "handoff_pending", "awaiting_authority", "proof_blocked"}
SKILLS_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
METRIC_NAMES = {
    "handoffs_prepared",
    "successors_created",
    "duplicate_spawn_attempts",
    "operator_repairs",
    "auto_compactions",
    "source_freezes",
    "post_freeze_source_mutations",
    "proof_reruns",
    "review_cycles",
}
CONTINUE_HANDOFF_REASONS = {
    "compaction-boundary",
    "context-exhausted",
    "operator-requested-task",
}
NEXT_GOAL_HANDOFF_REASON = "completed-goal"


def now() -> str:
    return datetime.now(UTC).isoformat()


def text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def project_root() -> Path:
    override = os.environ.get("SESSION_ORCHESTRATE_ROOT", "").strip()
    if override:
        root = exact_git_root(Path(override))
        cwd_root = git_root(Path.cwd().resolve())
        if root is None:
            raise ValueError("SESSION_ORCHESTRATE_ROOT is not a Git repository root")
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
    pending = state.get("pending_command") or {}
    consumed = bool(pending.get("consumed_at"))
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
        "handoff_reason": handoff.get("handoff_reason"),
        "source_goal_state": handoff.get("source_goal_state"),
        "execution_owner_thread_id": state.get("execution_owner_thread_id"),
        "first_command": None if consumed else pending.get("command") or handoff.get("first_command"),
        "first_command_hash": pending.get("command_hash") or handoff.get("first_command_hash"),
        "first_command_action": "already-consumed" if consumed else "execute-once",
    }


def bind_pending_command(
    state: dict[str, Any],
    command: str,
    *,
    source: str,
    source_id: str | None = None,
    allow_repeat: bool = False,
) -> dict[str, Any]:
    digest = text_hash(command)
    existing = state.get("pending_command") or {}
    if existing.get("command_hash") == digest and (
        not existing.get("consumed_at") or not allow_repeat
    ):
        return existing
    pending = {
        "command": command,
        "command_hash": digest,
        "source": source,
        "source_id": source_id,
        "created_at": now(),
        "consumed_at": None,
    }
    state["pending_command"] = pending
    return pending


def require_command_consumed(state: dict[str, Any], operation: str) -> None:
    pending = state.get("pending_command") or {}
    if pending and not pending.get("consumed_at"):
        raise ValueError(
            f"{operation} requires consuming pending first command {pending.get('command_hash')}"
        )


def record_proof_generation(
    state: dict[str, Any],
    *,
    scope: str,
    proof_status: str,
    product_fingerprint: str,
    proof_environment_fingerprint: str | None,
    result: str,
    evidence: list[str],
    final_acceptance: bool = False,
) -> tuple[dict[str, Any], bool]:
    normalized = {
        "scope": scope.strip(),
        "status": proof_status,
        "product_fingerprint": product_fingerprint.strip(),
        "proof_environment_fingerprint": (
            proof_environment_fingerprint.strip()
            if proof_environment_fingerprint
            else None
        ),
        "result": result.strip(),
        "evidence": list(dict.fromkeys(item.strip() for item in evidence if item.strip())),
        "final_acceptance": final_acceptance,
    }
    if not normalized["scope"]:
        raise ValueError("proof scope is required")
    if not normalized["product_fingerprint"]:
        raise ValueError("product fingerprint is required")
    if not normalized["result"]:
        raise ValueError("proof result is required")
    if proof_status in {"pass", "blocked"} and not normalized["evidence"]:
        raise ValueError(f"{proof_status} proof requires at least one evidence reference")
    generation_id = "sha256:" + text_hash(
        json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    )
    current = state.setdefault("proof_current", {})
    generations = state.setdefault("proof_generations", [])
    existing_id = current.get(normalized["scope"])
    if existing_id == generation_id:
        existing = next(
            (item for item in generations if item.get("generation_id") == generation_id),
            None,
        )
        if existing:
            return existing, True

    stamp = now()
    if existing_id:
        previous = next(
            (item for item in generations if item.get("generation_id") == existing_id),
            None,
        )
        if previous and not previous.get("superseded_at"):
            previous["superseded_at"] = stamp
            previous["superseded_by"] = generation_id
    generation = {
        "generation_id": generation_id,
        **normalized,
        "recorded_at": stamp,
    }
    generations.append(generation)
    current[normalized["scope"]] = generation_id
    return generation, False


def proof_artifact_matches(artifact_root: str, evidence: list[str]) -> bool:
    prefix = artifact_root.rstrip("/")
    return any(item == prefix or item.startswith(prefix + "/") for item in evidence)


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
            "execution_owner_thread_id": None,
            "handoff": None,
            "pending_command": None,
            "authority": None,
            "proof_blocker": None,
            "proof_history": [],
            "proof_current": {},
            "proof_generations": [],
            "proof_readiness": None,
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
        try:
            require_command_consumed(state, "prepare-handoff")
        except ValueError as exc:
            return fail(str(exc))
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

        if args.kind == "continue-goal":
            if args.reason not in CONTINUE_HANDOFF_REASONS:
                allowed = ", ".join(sorted(CONTINUE_HANDOFF_REASONS))
                return fail(f"continue-goal handoff reason must be one of: {allowed}")
            if args.source_goal_state != "paused":
                return fail("continue-goal requires the source Codex goal to be paused before spawning")
            if args.completion_evidence:
                return fail("continue-goal does not accept completion evidence")
        elif args.kind == "next-goal":
            if args.reason != NEXT_GOAL_HANDOFF_REASON:
                return fail("next-goal handoff reason must be completed-goal")
            if args.source_goal_state != "completed":
                return fail("next-goal requires the source Codex goal to be completed before spawning")
            if not args.completion_evidence:
                return fail("next-goal requires accepted current-goal completion evidence")

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
            "first_command_hash": text_hash(args.first_command),
            "handoff_reason": args.reason,
            "source_goal_state": args.source_goal_state,
            "completion_evidence": list(args.completion_evidence),
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
            bind_pending_command(
                state,
                existing["first_command"],
                source="handoff",
                source_id=existing.get("nonce"),
            )
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
        state["execution_owner_thread_id"] = handoff.get("successor_thread_id")
        bind_pending_command(
            state,
            handoff["first_command"],
            source="handoff",
            source_id=handoff.get("nonce"),
        )
        if handoff["kind"] == "next-goal":
            normalize_next_goal(state, handoff)
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit(claim_receipt(state, handoff, recovered=False))


def consume_command(args: argparse.Namespace) -> int:
    with locked() as (path, state):
        if not state or state.get("status") != "active":
            return fail("consume-command requires an active chain")
        pending = state.get("pending_command") or {}
        if not pending:
            return fail("no pending first command")
        if pending.get("command_hash") != args.command_hash:
            return fail("pending first command hash mismatch")
        if pending.get("consumed_at"):
            return emit({
                "chain_id": state["chain_id"],
                "command_hash": args.command_hash,
                "consumed_at": pending["consumed_at"],
                "idempotent": True,
            })
        pending["consumed_at"] = now()
        pending["result"] = args.result
        state["pending_command"] = pending
        state.setdefault("command_history", []).append({**pending})
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({
            "chain_id": state["chain_id"],
            "command_hash": args.command_hash,
            "consumed_at": pending["consumed_at"],
            "idempotent": False,
        })


def freeze_proof(args: argparse.Namespace) -> int:
    with locked() as (path, state):
        if not state or state.get("status") != "active":
            return fail("freeze-proof requires an active chain")
        try:
            require_command_consumed(state, "freeze-proof")
            product_fingerprint = args.product_fingerprint.strip()
            acceptance_contract = args.acceptance_contract.strip()
            proof_owner = args.proof_owner.strip()
            artifact_root = args.artifact_root.strip().rstrip("/")
            evidence = list(dict.fromkeys(item.strip() for item in args.evidence if item.strip()))
            if not all((product_fingerprint, acceptance_contract, proof_owner, artifact_root)):
                raise ValueError("freeze-proof requires non-empty contract, owner, fingerprint, and artifact root")
            if not evidence:
                raise ValueError("freeze-proof requires semantic readiness evidence")
            fingerprint_token = product_fingerprint.removeprefix("sha256:")
            if fingerprint_token not in artifact_root:
                raise ValueError("artifact root must be keyed by the product fingerprint")
        except ValueError as exc:
            return fail(str(exc))

        normalized = {
            "product_fingerprint": product_fingerprint,
            "acceptance_contract": acceptance_contract,
            "acceptance_contract_hash": "sha256:" + text_hash(acceptance_contract),
            "proof_owner": proof_owner,
            "artifact_root": artifact_root,
            "evidence": evidence,
        }
        readiness_id = "sha256:" + text_hash(
            json.dumps(normalized, sort_keys=True, separators=(",", ":"))
        )
        previous = state.get("proof_readiness") or {}
        if previous.get("readiness_id") == readiness_id:
            return emit({**previous, "idempotent": True})

        metrics = state.setdefault("metrics", {})
        if previous and previous.get("product_fingerprint") != product_fingerprint:
            metrics["post_freeze_source_mutations"] = (
                int(metrics.get("post_freeze_source_mutations", 0)) + 1
            )
        metrics["source_freezes"] = int(metrics.get("source_freezes", 0)) + 1
        readiness = {
            "readiness_id": readiness_id,
            **normalized,
            "recorded_at": now(),
        }
        state["proof_readiness"] = readiness
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({**readiness, "idempotent": False})


def record_proof(args: argparse.Namespace) -> int:
    with locked() as (path, state):
        if not state or state.get("status") not in {"active", "proof_blocked"}:
            return fail("record-proof requires an active or proof-blocked chain")
        try:
            require_command_consumed(state, "record-proof")
            if args.final_acceptance:
                readiness = state.get("proof_readiness") or {}
                if not readiness:
                    raise ValueError("final acceptance proof requires freeze-proof readiness")
                if readiness.get("product_fingerprint") != args.product_fingerprint.strip():
                    raise ValueError("final acceptance fingerprint differs from the frozen product source")
                if not proof_artifact_matches(readiness["artifact_root"], args.evidence):
                    raise ValueError("final acceptance evidence must use the frozen artifact root")
            generation, idempotent = record_proof_generation(
                state,
                scope=args.scope,
                proof_status=args.proof_status,
                product_fingerprint=args.product_fingerprint,
                proof_environment_fingerprint=args.proof_environment_fingerprint,
                result=args.result,
                evidence=args.evidence,
                final_acceptance=args.final_acceptance,
            )
        except ValueError as exc:
            return fail(str(exc))
        metrics = state.setdefault("metrics", {})
        if not idempotent and generation.get("superseded_by") is None:
            previous_count = sum(
                1
                for item in state.get("proof_generations", [])
                if item.get("scope") == generation.get("scope")
            )
            if previous_count > 1:
                metrics["proof_reruns"] = int(metrics.get("proof_reruns", 0)) + 1
        if args.final_acceptance and not idempotent:
            metrics["review_cycles"] = int(metrics.get("review_cycles", 0)) + 1
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({**generation, "idempotent": idempotent})


def pause_proof(args: argparse.Namespace) -> int:
    with locked() as (path, state):
        if not state or state.get("status") != "active":
            return fail("pause-proof requires an active chain")
        if not state.get("goal_hash") or not state.get("goal_objective"):
            return fail("pause-proof requires an exact active goal")
        try:
            require_command_consumed(state, "pause-proof")
            generation, _ = record_proof_generation(
                state,
                scope=args.scope,
                proof_status="blocked",
                product_fingerprint=args.product_fingerprint,
                proof_environment_fingerprint=args.proof_environment_fingerprint,
                result=args.reason,
                evidence=args.evidence,
            )
        except ValueError as exc:
            return fail(str(exc))
        blocker_identity = {
            "owner": args.owner,
            "scope": args.scope,
            "reason": args.reason,
            "next_command": args.next_command,
            "product_fingerprint": args.product_fingerprint,
            "proof_environment_fingerprint": args.proof_environment_fingerprint,
            "bounded_recovery_used": args.recovery_used,
            "generation_id": generation["generation_id"],
        }
        blocker = {
            **blocker_identity,
            "blocker_fingerprint": "sha256:" + text_hash(
                json.dumps(blocker_identity, sort_keys=True, separators=(",", ":"))
            ),
            "paused_at": now(),
        }
        state["status"] = "proof_blocked"
        state["proof_blocker"] = blocker
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({"chain_id": state["chain_id"], "status": state["status"], **blocker})


def resume_proof(args: argparse.Namespace) -> int:
    with locked() as (path, state):
        if not state or state.get("status") != "proof_blocked":
            return fail("resume-proof requires a proof-blocked chain")
        blocker = state.get("proof_blocker") or {}
        next_command = blocker.get("next_command")
        if not next_command:
            return fail("proof blocker has no exact next command")
        blocker["resumed_at"] = now()
        blocker["resume_reason"] = args.reason
        state.setdefault("proof_history", []).append(blocker)
        state["proof_blocker"] = None
        state["status"] = "active"
        pending = bind_pending_command(
            state,
            next_command,
            source="proof-resume",
            source_id=blocker.get("blocker_fingerprint"),
            allow_repeat=True,
        )
        state["updated_at"] = now()
        atomic_write(path, state)
        return emit({
            "chain_id": state["chain_id"],
            "status": state["status"],
            "goal_id": state.get("goal_id"),
            "goal_hash": state.get("goal_hash"),
            "goal_file": str(materialize_goal(state["goal_objective"])),
            "first_command": pending["command"],
            "first_command_hash": pending["command_hash"],
            "first_command_action": "execute-once",
        })


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
    command.add_argument("--reason")
    command.add_argument("--source-goal-state", choices=("paused", "completed"))
    command.add_argument("--completion-evidence", action="append", default=[])
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

    command = commands.add_parser("consume-command")
    command.add_argument("--command-hash", required=True)
    command.add_argument("--result", choices=("completed", "failed", "blocked"), required=True)
    command.set_defaults(handler=consume_command)

    command = commands.add_parser("freeze-proof")
    command.add_argument("--product-fingerprint", required=True)
    command.add_argument("--acceptance-contract", required=True)
    command.add_argument("--proof-owner", required=True)
    command.add_argument("--artifact-root", required=True)
    command.add_argument("--evidence", action="append", default=[])
    command.set_defaults(handler=freeze_proof)

    command = commands.add_parser("record-proof")
    command.add_argument("--scope", required=True)
    command.add_argument(
        "--proof-status",
        choices=("pass", "fail", "blocked", "not-tested"),
        required=True,
    )
    command.add_argument("--product-fingerprint", required=True)
    command.add_argument("--proof-environment-fingerprint")
    command.add_argument("--result", required=True)
    command.add_argument("--evidence", action="append", default=[])
    command.add_argument("--final-acceptance", action="store_true")
    command.set_defaults(handler=record_proof)

    command = commands.add_parser("pause-proof")
    command.add_argument("--owner", required=True)
    command.add_argument("--scope", required=True)
    command.add_argument("--reason", required=True)
    command.add_argument("--next-command", required=True)
    command.add_argument("--product-fingerprint", required=True)
    command.add_argument("--proof-environment-fingerprint")
    command.add_argument("--evidence", action="append", default=[])
    command.add_argument("--recovery-used", action="store_true")
    command.set_defaults(handler=pause_proof)

    command = commands.add_parser("resume-proof")
    command.add_argument("--reason", required=True)
    command.set_defaults(handler=resume_proof)

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
