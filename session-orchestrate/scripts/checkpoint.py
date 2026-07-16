#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def resolve_command() -> str:
    command = shutil.which("save-session")
    if command:
        return command
    fallback = Path.home() / ".local" / "bin" / "save-session"
    if fallback.is_file():
        return str(fallback)
    raise FileNotFoundError("save-session command is unavailable")


def main() -> int:
    parser = argparse.ArgumentParser(description="Checkpoint one exact session-orchestrate goal")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--goal-file", type=Path, required=True)
    parser.add_argument("--resume-policy", choices=("ensure-active", "reference-only"), required=True)
    parser.add_argument("--resume-window-hours", type=int, choices=range(1, 169), default=24)
    parser.add_argument("--next-action", required=True)
    parser.add_argument("--blocker", default="None.")
    parser.add_argument("--verification", default="No verification summary supplied.")
    parser.add_argument("--introspection", default="None.")
    parser.add_argument("--avoid", default="Do not broaden the saved goal or bypass its constraints.")
    args = parser.parse_args()

    try:
        objective = args.goal_file.read_text(encoding="utf-8").rstrip()
        command = resolve_command()
    except OSError as exc:
        print(f"checkpoint: {exc}", file=sys.stderr)
        return 2

    env = {
        **os.environ,
        "SAVE_SESSION_ROOT": str(args.root.resolve()),
        "SAVE_SESSION_GOAL_OBJECTIVE": objective,
        "SAVE_SESSION_GOAL_RESUME_POLICY": args.resume_policy,
        "SAVE_SESSION_RESUME_WINDOW_HOURS": str(args.resume_window_hours),
        "SAVE_SESSION_HANDOFF_FOCUS": args.next_action,
        "SAVE_SESSION_WORKING_ON": "Session-orchestrate goal checkpoint.",
        "SAVE_SESSION_NEXT_ACTION": args.next_action,
        "SAVE_SESSION_BLOCKERS": args.blocker,
        "SAVE_SESSION_VERIFICATION_STATE": args.verification,
        "SAVE_SESSION_INTROSPECTION": args.introspection,
        "SAVE_SESSION_AVOID": args.avoid,
    }
    result = subprocess.run([command], env=env, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        sys.stderr.write(result.stderr or result.stdout)
        return result.returncode

    checkpoint = args.root.resolve() / ".claude" / "session-data" / "CURRENT.md"
    try:
        saved = checkpoint.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"checkpoint: {exc}", file=sys.stderr)
        return 2
    if f"resume_policy: {args.resume_policy}" not in saved or objective not in saved:
        print("checkpoint: exact goal or resume policy did not round-trip", file=sys.stderr)
        return 1

    print(json.dumps({
        "success": True,
        "checkpoint": str(checkpoint),
        "resume_policy": args.resume_policy,
        "resume_window_hours": args.resume_window_hours,
        "goal_chars": len(objective),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
