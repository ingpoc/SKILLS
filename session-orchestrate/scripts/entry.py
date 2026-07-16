#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
INSPECTOR = HERE.parent.parent / "resume-session" / "scripts" / "inspect_checkpoint.py"
INVENTORY = HERE / "project_inventory.py"


def checkpoint_inspection() -> dict[str, Any]:
    command = [sys.executable, str(INSPECTOR), "--write-goal-file"]
    override = os.environ.get("SESSION_ORCHESTRATE_ROOT", "").strip()
    if override:
        command.extend(["--root", override])
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
    command = [sys.executable, str(INVENTORY), "--root", str(root)]
    session_limit = os.environ.get("SESSION_ORCHESTRATE_SESSION_LIMIT", "").strip()
    if session_limit:
        command.extend(["--session-limit", session_limit])
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
    status = state.get("status")
    if mode == "resume-exact-goal":
        if status == "active":
            return "reuse-active-chain"
        if status == "handoff_pending":
            return "claim-pending-handoff"
        return "resume-goal-chain-closed"
    if status in {"active", "handoff_pending"}:
        return "review-active-chain"
    return "init-new-chain"


def downgrade(inspection: dict[str, Any], reason: str) -> None:
    goal_file = inspection.get("goal_file")
    if goal_file:
        Path(goal_file).unlink(missing_ok=True)
    inspection["goal_file"] = None
    inspection["eligibility"] = "conflict"
    inspection["mode"] = "review-checkpoint"
    inspection["reasons"] = list(dict.fromkeys([*(inspection.get("reasons") or []), reason]))


def main() -> int:
    try:
        inspection = checkpoint_inspection()
        root = Path(inspection["project_root"])
        state_path = root / ".claude" / "session-data" / "ORCHESTRATION.json"
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
        elif state.get("status") in {"active", "handoff_pending", "stopped", "blocked"} and not recorded_hash:
            downgrade(inspection, "chain_goal_hash_missing")

    mode = inspection["mode"]
    output = {
        **inspection,
        "invocation_authority": {
            "resume-exact-goal": "saved-goal-only",
            "choose-next-goal": "new-bounded-chain",
            "review-checkpoint": "orchestration-only",
        }[mode],
        "chain_action": chain_action(state, mode),
        "project_inventory": inventory,
        "chain": None if not state else {
            "chain_id": state.get("chain_id"),
            "status": state.get("status"),
            "hop": state.get("hop"),
            "max_hops": state.get("max_hops"),
            "phase_boundary": state.get("phase_boundary"),
            "stop_reason": state.get("stop_reason"),
            "goal_hash": state.get("goal_hash"),
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
