#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = 1
PROGRAM_POLICY_VERSION = 3
SESSION_DIR = ".session"
LEGACY_DIR = Path(".claude/session-data")
GOAL_ID = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
GOAL_STATUSES = {"unknown", "planned", "in_progress", "blocked", "completed"}
DELIVERY_UNITS = {"bounded-deliverable", "project-lifecycle"}
LIFECYCLE_KINDS = {"implementation", "verification", "promotion", "handoff", "hardening"}
FIELDS = {
    "session": None,
    "plan": "PLAN.md",
    "tracking": "TRACKING.json",
    "current": "CURRENT.md",
    "orchestration": "ORCHESTRATION.json",
    "orchestration-lock": "ORCHESTRATION.lock",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_root(candidate: Path) -> Path | None:
    result = subprocess.run(
        ["git", "-C", str(candidate.expanduser().resolve()), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return Path(result.stdout.strip()).resolve() if result.returncode == 0 and result.stdout.strip() else None


def canonical_paths(root: Path) -> dict[str, Path]:
    directory = root / SESSION_DIR
    return {
        key: directory if name is None else directory / name
        for key, name in FIELDS.items()
    }


def legacy_paths(root: Path) -> dict[str, Path]:
    directory = root / LEGACY_DIR
    return {
        "current": directory / "CURRENT.md",
        "orchestration": directory / "ORCHESTRATION.json",
        "orchestration-lock": directory / "ORCHESTRATION.lock",
    }


def resolve_path(root: Path, field: str) -> Path:
    root = root.expanduser().resolve()
    paths = canonical_paths(root)
    if paths["session"].is_dir() or field in {"session", "plan", "tracking"}:
        return paths[field]
    legacy = legacy_paths(root)
    candidate = legacy.get(field)
    if candidate is not None and candidate.exists():
        return candidate
    return paths[field]


def atomic_bytes(path: Path, content: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(raw)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        path.chmod(mode)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_text(path: Path, content: str, mode: int = 0o600) -> None:
    atomic_bytes(path, content.encode("utf-8"), mode)


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    atomic_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


@contextmanager
def workspace_lock(root: Path) -> Iterator[None]:
    directory = root / SESSION_DIR
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    lock_path = directory / "WORKSPACE.lock"
    with lock_path.open("a+", encoding="utf-8") as lock:
        lock_path.chmod(0o600)
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        yield


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def initial_tracking(root: Path, migrated: list[str]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "program_policy_version": PROGRAM_POLICY_VERSION,
        "project_root": str(root),
        "status": "needs_refresh",
        "updated_at": now(),
        "completion_gate": "",
        "phase_boundary": "",
        "selected_goal_id": None,
        "selection_probe": None,
        "plan_sources": [],
        "goals": [],
        "migrated_from": migrated,
    }


def render_plan(tracking: dict[str, Any]) -> str:
    lines = [
        "# Session Program Plan",
        "",
        "> Generated from `.session/TRACKING.json` by `$session-orchestrate`. Do not edit this projection directly.",
        "> Product intent remains owned by the repository sources listed below.",
        "",
        f"**Status:** {tracking.get('status', 'needs_refresh')}",
        f"**Program policy:** {tracking.get('program_policy_version', 'legacy')}",
        f"**Updated:** {tracking.get('updated_at', 'unknown')}",
        f"**Phase boundary:** {tracking.get('phase_boundary') or 'not derived'}",
        f"**Selected goal:** {tracking.get('selected_goal_id') or 'none'}",
        "",
        "## Product completion gate",
        "",
        tracking.get("completion_gate") or "*(not derived; rebuild from current product-plan owners)*",
        "",
        "## Authoritative sources",
        "",
    ]
    sources = tracking.get("plan_sources") or []
    if sources:
        for source in sources:
            lines.append(f"- `{source['path']}` — `{source['sha256']}`")
    else:
        lines.append("- *(none recorded)*")
    selection = tracking.get("selection_probe")
    lines.extend(["", "## Work selection", ""])
    if selection:
        lines.extend([
            f"- Scope: `{selection['scope']}`",
            f"- Route: {selection['route']}",
            f"- Target: `{selection['target']}`",
            "- Source references:",
            *([f"  - `{item}`" for item in selection["source_refs"]] or ["  - *(none; rerun route before activation)*"]),
        ])
    else:
        lines.append("- *(owner plan ordering; no repository selector declared)*")
    lines.extend(["", "## Ordered session goals", ""])
    goals = tracking.get("goals") or []
    if not goals:
        lines.append("*(not derived)*")
    for goal in goals:
        marker = "x" if goal["status"] == "completed" else " "
        lines.extend([
            f"### [{marker}] {goal['id']} — {goal['title']}",
            "",
            f"- Status: `{goal['status']}`",
            f"- Delivery unit: `{goal.get('delivery_unit', 'bounded-deliverable')}`",
            f"- Plan reference: {goal['plan_ref']}",
            f"- Prerequisites: {', '.join(goal['prerequisites']) or 'none'}",
        ])
        if goal.get("delivery_unit") == "project-lifecycle":
            lines.append("- Lifecycle stages:")
            for stage in goal["lifecycle_stages"]:
                lines.extend([
                    f"  - `{stage['id']}` [{stage['kind']}] {stage['title']}: {stage['action']}",
                    f"    - Route: {stage['route']}",
                    f"    - Acceptance: {stage['acceptance']}",
                    f"    - Authority: {stage['authority_gate'] or 'none'}",
                ])
        else:
            lines.extend(["- Actions:", *[f"  - {item}" for item in goal["actions"]]])
        lines.extend([
            "- Verification:",
            *[f"  - {item}" for item in goal["verification"]],
            "- Evidence:",
            *([f"  - {item}" for item in goal["evidence"]] or ["  - *(none)*"]),
            "- Authority gates:",
            *([f"  - {item}" for item in goal["authority_gates"]] or ["  - *(none)*"]),
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def add_git_exclude(root: Path) -> None:
    if git_root(root) != root:
        return
    exclude_result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--git-path", "info/exclude"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if exclude_result.returncode != 0 or not exclude_result.stdout.strip():
        return
    raw = Path(exclude_result.stdout.strip())
    exclude = raw if raw.is_absolute() else (root / raw).resolve()
    if not exclude.is_file():
        return
    content = exclude.read_text(encoding="utf-8")
    if ".session/" not in content.splitlines():
        with exclude.open("a", encoding="utf-8") as handle:
            if content and not content.endswith("\n"):
                handle.write("\n")
            handle.write(".session/\n")


def read_tracking(root: Path) -> dict[str, Any]:
    path = canonical_paths(root)["tracking"]
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported or invalid .session/TRACKING.json")
    if Path(str(data.get("project_root", ""))).resolve() != root:
        raise ValueError("tracking project_root does not match the current repository")
    return data


def ensure_workspace(root: Path) -> dict[str, Any]:
    root = root.expanduser().resolve()
    paths = canonical_paths(root)
    legacy = legacy_paths(root)
    migrated: list[str] = []
    with workspace_lock(root):
        for field in ("current", "orchestration"):
            source = legacy[field]
            target = paths[field]
            if not target.exists() and source.is_file():
                atomic_bytes(target, source.read_bytes())
                migrated.append(str(source.relative_to(root)))
        if not paths["tracking"].exists():
            tracking = initial_tracking(root, migrated)
            atomic_json(paths["tracking"], tracking)
        else:
            tracking = read_tracking(root)
            if migrated:
                prior = list(tracking.get("migrated_from") or [])
                tracking["migrated_from"] = list(dict.fromkeys([*prior, *migrated]))
                tracking["updated_at"] = now()
                atomic_json(paths["tracking"], tracking)
        if not paths["plan"].exists():
            atomic_text(paths["plan"], render_plan(tracking))
    add_git_exclude(root)
    return workspace_status(root, migrated=migrated)


def program_staleness(root: Path, tracking: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    policy_current = tracking.get("program_policy_version") == PROGRAM_POLICY_VERSION
    if not policy_current:
        reasons.append("program_policy_changed")
    if tracking.get("status") == "needs_refresh":
        reasons.append("program_not_derived")
    for source in tracking.get("plan_sources") or []:
        path = root / source.get("path", "")
        if not path.is_file():
            reasons.append(f"plan_source_missing:{source.get('path')}")
        elif sha256_file(path) != source.get("sha256"):
            reasons.append(f"plan_source_changed:{source.get('path')}")
    if policy_current:
        plan = canonical_paths(root)["plan"]
        expected = render_plan(tracking)
        if not plan.is_file():
            reasons.append("plan_projection_missing")
        elif plan.read_text(encoding="utf-8") != expected:
            reasons.append("plan_projection_modified")
    return reasons


def workspace_status(root: Path, *, migrated: list[str] | None = None) -> dict[str, Any]:
    root = root.expanduser().resolve()
    paths = canonical_paths(root)
    tracking = read_tracking(root)
    stale_reasons = program_staleness(root, tracking)
    status = tracking.get("status")
    if stale_reasons:
        action = "rebuild-plan"
    elif status == "complete":
        action = "product-complete"
    elif status == "blocked":
        action = "review-blocked-goal"
    else:
        action = "use-plan"
    counts: dict[str, int] = {name: 0 for name in sorted(GOAL_STATUSES)}
    for goal in tracking.get("goals") or []:
        counts[goal["status"]] += 1
    selected_goal = next(
        (goal for goal in tracking.get("goals") or [] if goal.get("id") == tracking.get("selected_goal_id")),
        None,
    )
    legacy = legacy_paths(root)
    return {
        "schema_version": SCHEMA_VERSION,
        "program_policy_version": tracking.get("program_policy_version"),
        "project_root": str(root),
        "paths": {key: str(value) for key, value in paths.items()},
        "program_status": status,
        "program_action": action,
        "stale": bool(stale_reasons),
        "stale_reasons": stale_reasons,
        "selected_goal_id": tracking.get("selected_goal_id"),
        "selection_probe": tracking.get("selection_probe"),
        "selected_goal_delivery_unit": (
            selected_goal.get("delivery_unit", "bounded-deliverable") if selected_goal else None
        ),
        "selected_goal_lifecycle_stages": selected_goal.get("lifecycle_stages", []) if selected_goal else [],
        "goal_counts": counts,
        "plan_sources": tracking.get("plan_sources") or [],
        "migrated": migrated or [],
        "legacy_present": any(path.exists() for path in legacy.values()),
    }


def string_list(value: Any, field: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{field} must be a list of non-empty strings")
    if nonempty and not value:
        raise ValueError(f"{field} must not be empty")
    return [item.strip() for item in value]


def validate_selection_probe(raw: dict[str, Any], plan_sources: list[str]) -> dict[str, Any] | None:
    value = raw.get("selection_probe")
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("selection_probe must be an object")
    scope = value.get("scope")
    if scope not in {"dynamic-queue", "static-plan"}:
        raise ValueError("selection_probe.scope must be dynamic-queue or static-plan")
    normalized: dict[str, Any] = {"scope": scope}
    for field in ("route", "target"):
        field_value = value.get(field)
        if not isinstance(field_value, str) or not field_value.strip():
            raise ValueError(f"selection_probe.{field} must be non-empty")
        normalized[field] = field_value.strip()
    source_refs = string_list(value.get("source_refs", []), "selection_probe.source_refs")
    missing = [source for source in source_refs if source not in plan_sources]
    if missing:
        raise ValueError(
            "selection_probe.source_refs must also be plan_sources: " + ", ".join(missing)
        )
    normalized["source_refs"] = source_refs
    return normalized


def validate_delivery_unit(goal_id: str, raw_goal: dict[str, Any]) -> str:
    delivery_unit = raw_goal.get("delivery_unit", "bounded-deliverable")
    if delivery_unit not in DELIVERY_UNITS:
        raise ValueError(f"{goal_id}.delivery_unit is invalid")
    return delivery_unit


def validate_lifecycle_stages(goal_id: str, raw_goal: dict[str, Any], delivery_unit: str) -> list[dict[str, str]]:
    raw_stages = raw_goal.get("lifecycle_stages")
    if delivery_unit == "bounded-deliverable":
        if raw_stages is not None:
            raise ValueError(f"{goal_id}.lifecycle_stages requires delivery_unit project-lifecycle")
        return []
    if not isinstance(raw_stages, list) or not 2 <= len(raw_stages) <= 8:
        raise ValueError(f"{goal_id}.lifecycle_stages must contain 2 to 8 ordered stages")
    stages: list[dict[str, str]] = []
    ids: set[str] = set()
    for index, raw_stage in enumerate(raw_stages):
        if not isinstance(raw_stage, dict):
            raise ValueError(f"{goal_id}.lifecycle_stages[{index}] must be an object")
        stage_id = raw_stage.get("id")
        kind = raw_stage.get("kind")
        if not isinstance(stage_id, str) or not GOAL_ID.fullmatch(stage_id) or stage_id in ids:
            raise ValueError(f"{goal_id}.lifecycle_stages[{index}].id must be unique kebab-case")
        if kind not in LIFECYCLE_KINDS:
            raise ValueError(f"{goal_id}.{stage_id}.kind is invalid")
        ids.add(stage_id)
        stage: dict[str, str] = {"id": stage_id, "kind": kind}
        for field in ("title", "action", "route", "acceptance"):
            value = raw_stage.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{goal_id}.{stage_id}.{field} must be non-empty")
            stage[field] = value.strip()
        authority = raw_stage.get("authority_gate", "")
        if not isinstance(authority, str):
            raise ValueError(f"{goal_id}.{stage_id}.authority_gate must be a string")
        stage["authority_gate"] = authority.strip()
        stages.append(stage)
    implementation = [index for index, stage in enumerate(stages) if stage["kind"] == "implementation"]
    verification = [index for index, stage in enumerate(stages) if stage["kind"] == "verification"]
    if not implementation:
        raise ValueError(f"{goal_id}.lifecycle_stages requires an implementation stage")
    verification_after_implementation = [
        index for index in verification if index > min(implementation)
    ]
    if not verification_after_implementation:
        raise ValueError(f"{goal_id}.lifecycle_stages requires verification after implementation")
    first_acceptance_verification = min(verification_after_implementation)
    early_exit = [
        stage["id"]
        for index, stage in enumerate(stages)
        if stage["kind"] in {"promotion", "handoff"} and index < first_acceptance_verification
    ]
    if early_exit:
        raise ValueError(f"{goal_id}.lifecycle stages require verification before: {', '.join(early_exit)}")
    return stages


def validate_program(root: Path, raw: dict[str, Any], migrated_from: list[str]) -> dict[str, Any]:
    completion_gate = raw.get("completion_gate")
    phase_boundary = raw.get("phase_boundary")
    if not isinstance(completion_gate, str) or not completion_gate.strip():
        raise ValueError("completion_gate must be a non-empty string")
    if not isinstance(phase_boundary, str) or not phase_boundary.strip():
        raise ValueError("phase_boundary must be a non-empty string")
    source_values = string_list(raw.get("plan_sources"), "plan_sources", nonempty=True)
    selection_probe = validate_selection_probe(raw, source_values)
    sources = []
    for value in source_values:
        candidate = Path(value)
        path = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
        try:
            relative = path.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"plan source is outside the project root: {value}") from exc
        if not path.is_file():
            raise ValueError(f"plan source does not exist: {relative}")
        sources.append({"path": str(relative), "sha256": sha256_file(path)})

    raw_goals = raw.get("goals")
    if not isinstance(raw_goals, list) or not raw_goals:
        raise ValueError("goals must be a non-empty list")
    goals = []
    ids: set[str] = set()
    for index, raw_goal in enumerate(raw_goals):
        if not isinstance(raw_goal, dict):
            raise ValueError(f"goals[{index}] must be an object")
        goal_id = raw_goal.get("id")
        if not isinstance(goal_id, str) or not GOAL_ID.fullmatch(goal_id):
            raise ValueError(f"goals[{index}].id must be unique kebab-case")
        if goal_id in ids:
            raise ValueError(f"duplicate goal id: {goal_id}")
        ids.add(goal_id)
        title = raw_goal.get("title")
        plan_ref = raw_goal.get("plan_ref")
        status = raw_goal.get("status", "planned")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{goal_id}.title must be non-empty")
        if not isinstance(plan_ref, str) or not plan_ref.strip():
            raise ValueError(f"{goal_id}.plan_ref must be non-empty")
        if status not in GOAL_STATUSES:
            raise ValueError(f"{goal_id}.status is invalid")
        delivery_unit = validate_delivery_unit(goal_id, raw_goal)
        lifecycle_stages = validate_lifecycle_stages(goal_id, raw_goal, delivery_unit)
        if delivery_unit == "project-lifecycle":
            if raw_goal.get("actions") is not None:
                raise ValueError(f"{goal_id}.actions must be omitted; lifecycle_stages owns lifecycle actions")
        else:
            actions = string_list(raw_goal.get("actions"), f"{goal_id}.actions", nonempty=True)
        goal = {
            "id": goal_id,
            "title": title.strip(),
            "status": status,
            "delivery_unit": delivery_unit,
            "plan_ref": plan_ref.strip(),
            "prerequisites": string_list(raw_goal.get("prerequisites", []), f"{goal_id}.prerequisites"),
            "verification": string_list(raw_goal.get("verification"), f"{goal_id}.verification", nonempty=True),
            "evidence": string_list(raw_goal.get("evidence", []), f"{goal_id}.evidence"),
            "authority_gates": string_list(raw_goal.get("authority_gates", []), f"{goal_id}.authority_gates"),
        }
        admission_target = raw_goal.get("admission_target")
        if admission_target is not None:
            if not isinstance(admission_target, str) or not admission_target.strip():
                raise ValueError(f"{goal_id}.admission_target must be non-empty")
            goal["admission_target"] = admission_target.strip()
        if delivery_unit == "project-lifecycle":
            goal["lifecycle_stages"] = lifecycle_stages
        else:
            goal["actions"] = actions
        if status == "completed" and not goal["evidence"]:
            raise ValueError(f"completed goal requires evidence: {goal_id}")
        goals.append(goal)
    goal_by_id = {goal["id"]: goal for goal in goals}
    positions = {goal["id"]: index for index, goal in enumerate(goals)}
    for goal in goals:
        missing = [item for item in goal["prerequisites"] if item not in ids]
        if missing:
            raise ValueError(f"{goal['id']} has unknown prerequisites: {', '.join(missing)}")
        unordered = [item for item in goal["prerequisites"] if positions[item] >= positions[goal["id"]]]
        if unordered:
            raise ValueError(f"{goal['id']} prerequisites must appear earlier: {', '.join(unordered)}")
        if goal["status"] == "completed":
            incomplete = [item for item in goal["prerequisites"] if goal_by_id[item]["status"] != "completed"]
            if incomplete:
                raise ValueError(f"completed goal has incomplete prerequisites: {goal['id']}")

    selected = raw.get("selected_goal_id")
    all_complete = all(goal["status"] == "completed" for goal in goals)
    if selected is not None:
        if selected not in goal_by_id:
            raise ValueError("selected_goal_id does not exist")
        if goal_by_id[selected]["status"] == "completed":
            raise ValueError("selected_goal_id cannot be completed")
        if goal_by_id[selected]["status"] == "unknown":
            raise ValueError("selected_goal_id cannot have unknown status")
        unmet = [item for item in goal_by_id[selected]["prerequisites"] if goal_by_id[item]["status"] != "completed"]
        if unmet:
            raise ValueError(f"selected goal has incomplete prerequisites: {', '.join(unmet)}")
    elif not all_complete:
        raise ValueError("selected_goal_id is required while goals remain")
    active = [goal["id"] for goal in goals if goal["status"] == "in_progress"]
    if len(active) > 1 or (active and active[0] != selected):
        raise ValueError("only selected_goal_id may be in_progress")
    if selection_probe:
        if selected is None:
            raise ValueError("selection_probe requires selected_goal_id")
        if goal_by_id[selected].get("admission_target") != selection_probe["target"]:
            raise ValueError("selected goal admission_target does not match selection_probe.target")
        if selection_probe["scope"] == "dynamic-queue":
            unfinished = [goal["id"] for goal in goals if goal["status"] != "completed"]
            if unfinished != [selected]:
                raise ValueError("dynamic-queue programs may contain only the admitted unfinished goal")
    status = "complete" if all_complete else (
        "blocked" if selected and goal_by_id[selected]["status"] == "blocked" else "ready"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "program_policy_version": PROGRAM_POLICY_VERSION,
        "project_root": str(root),
        "status": status,
        "updated_at": now(),
        "completion_gate": completion_gate.strip(),
        "phase_boundary": phase_boundary.strip(),
        "selected_goal_id": selected,
        "selection_probe": selection_probe,
        "plan_sources": sources,
        "goals": goals,
        "migrated_from": migrated_from,
    }


def sync_program(root: Path, program_file: Path) -> dict[str, Any]:
    root = root.expanduser().resolve()
    raw = json.loads(program_file.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("program file must contain one JSON object")
    with workspace_lock(root):
        existing = read_tracking(root)
        tracking = validate_program(root, raw, list(existing.get("migrated_from") or []))
        paths = canonical_paths(root)
        atomic_json(paths["tracking"], tracking)
        atomic_text(paths["plan"], render_plan(tracking))
    return workspace_status(root)


def mark_goal(root: Path, goal_id: str, status: str, evidence: list[str]) -> dict[str, Any]:
    root = root.expanduser().resolve()
    if status not in GOAL_STATUSES:
        raise ValueError(f"invalid goal status: {status}")
    with workspace_lock(root):
        tracking = read_tracking(root)
        goal = next((item for item in tracking.get("goals") or [] if item.get("id") == goal_id), None)
        if goal is None:
            raise ValueError(f"unknown goal id: {goal_id}")
        if goal["status"] == "completed" and status != "completed":
            raise ValueError("completed goals can be changed only by a full program resync")
        if status in {"in_progress", "completed"}:
            goal_by_id = {item["id"]: item for item in tracking["goals"]}
            unmet = [item for item in goal["prerequisites"] if goal_by_id[item]["status"] != "completed"]
            if unmet:
                raise ValueError(f"goal has incomplete prerequisites: {', '.join(unmet)}")
        goal["status"] = status
        goal["evidence"] = list(dict.fromkeys([*(goal.get("evidence") or []), *evidence]))
        if status == "completed" and not goal["evidence"]:
            raise ValueError("completed goal requires at least one evidence reference")
        if status in {"in_progress", "blocked"}:
            tracking["selected_goal_id"] = goal_id
        elif status == "completed" and tracking.get("selected_goal_id") == goal_id:
            tracking["selected_goal_id"] = None
        all_complete = all(item["status"] == "completed" for item in tracking["goals"])
        dynamic_queue = (tracking.get("selection_probe") or {}).get("scope") == "dynamic-queue"
        if all_complete and dynamic_queue:
            tracking["status"] = "needs_refresh"
            tracking["selected_goal_id"] = None
        elif all_complete:
            tracking["status"] = "complete"
            tracking["selected_goal_id"] = None
        elif tracking.get("selected_goal_id") is None:
            tracking["status"] = "needs_refresh"
        else:
            selected = next(item for item in tracking["goals"] if item["id"] == tracking["selected_goal_id"])
            tracking["status"] = "blocked" if selected["status"] == "blocked" else "ready"
        tracking["updated_at"] = now()
        paths = canonical_paths(root)
        atomic_json(paths["tracking"], tracking)
        atomic_text(paths["plan"], render_plan(tracking))
    return workspace_status(root)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Manage the canonical repo-local .session workspace")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("ensure", "status"):
        command = commands.add_parser(name)
        command.add_argument("--root", type=Path, default=Path.cwd())
    command = commands.add_parser("path")
    command.add_argument("--root", type=Path, default=Path.cwd())
    command.add_argument("--field", choices=sorted(FIELDS), required=True)
    command = commands.add_parser("sync")
    command.add_argument("--root", type=Path, default=Path.cwd())
    command.add_argument("--program-file", type=Path, required=True)
    command = commands.add_parser("mark")
    command.add_argument("--root", type=Path, default=Path.cwd())
    command.add_argument("--goal-id", required=True)
    command.add_argument("--status", choices=sorted(GOAL_STATUSES), required=True)
    command.add_argument("--evidence", action="append", default=[])
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        root = args.root.expanduser().resolve()
        if args.command == "ensure":
            output: Any = ensure_workspace(root)
        elif args.command == "status":
            output = workspace_status(root)
        elif args.command == "path":
            print(resolve_path(root, args.field))
            return 0
        elif args.command == "sync":
            ensure_workspace(root)
            output = sync_program(root, args.program_file)
        else:
            ensure_workspace(root)
            output = mark_goal(root, args.goal_id, args.status, args.evidence)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"session_workspace: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
