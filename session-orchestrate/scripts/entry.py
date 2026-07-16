#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


POLICIES = {"ensure-active", "reference-only"}


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


def parse_checkpoint(path: Path) -> tuple[str | None, str | None]:
    if not path.exists():
        return None, None
    text = path.read_text(encoding="utf-8")
    marker = "## codex_goal\n"
    if marker not in text:
        return None, None
    section = text.split(marker, 1)[1].split("\n## working_on", 1)[0]
    policy_line = next((line for line in section.splitlines() if line.startswith("resume_policy: ")), None)
    if not policy_line:
        raise ValueError("checkpoint codex_goal is missing resume_policy")
    policy = policy_line.split(":", 1)[1].strip()
    if policy not in POLICIES:
        raise ValueError(f"unsupported checkpoint resume_policy: {policy}")
    objective_marker = "objective:\n"
    if objective_marker not in section:
        raise ValueError("checkpoint codex_goal is missing objective")
    objective = section.split(objective_marker, 1)[1].rstrip()
    if policy == "ensure-active" and not objective:
        raise ValueError("ensure-active checkpoint has an empty objective")
    return policy, objective or None


def private_goal_file(objective: str) -> tuple[Path, str]:
    content = objective.rstrip() + "\n"
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    path = Path(tempfile.gettempdir()) / f"session-orchestrate-goal-{digest[:16]}.md"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(content)
    path.chmod(0o600)
    return path, f"sha256:{digest}"


def read_chain(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("invalid orchestration state")
    return data


def chain_action(state: dict[str, Any] | None, mode: str) -> str:
    if not state:
        return "init-new-chain"
    status = state.get("status")
    if status == "active":
        return "reuse-active-chain"
    if status == "handoff_pending":
        return "claim-pending-handoff"
    if mode == "resume-exact-goal":
        return "resume-goal-chain-closed"
    return "init-new-chain"


def main() -> int:
    root = project_root()
    checkpoint = root / ".claude" / "session-data" / "CURRENT.md"
    state_path = root / ".claude" / "session-data" / "ORCHESTRATION.json"
    try:
        policy, objective = parse_checkpoint(checkpoint)
        state = read_chain(state_path)
        goal_path = None
        goal_hash = None
        if policy == "ensure-active" and objective:
            goal_path, goal_hash = private_goal_file(objective)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"entry: {exc}", file=sys.stderr)
        return 1

    mode = "resume-exact-goal" if policy == "ensure-active" and objective else "choose-next-goal"
    output = {
        "success": True,
        "project_root": str(root),
        "checkpoint": str(checkpoint) if checkpoint.exists() else None,
        "mode": mode,
        "resume_policy": policy,
        "goal_file": str(goal_path) if goal_path else None,
        "goal_hash": goal_hash,
        "invocation_authority": "saved-goal-only" if mode == "resume-exact-goal" else "new-bounded-chain",
        "chain_action": chain_action(state, mode),
        "chain": None if not state else {
            "chain_id": state.get("chain_id"),
            "status": state.get("status"),
            "hop": state.get("hop"),
            "max_hops": state.get("max_hops"),
            "phase_boundary": state.get("phase_boundary"),
            "stop_reason": state.get("stop_reason"),
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
