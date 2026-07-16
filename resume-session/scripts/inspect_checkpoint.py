#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_RESUME_WINDOW_HOURS = 24
MAX_RESUME_WINDOW_HOURS = 168
FUTURE_TOLERANCE_SECONDS = 300
POLICIES = {"ensure-active", "reference-only"}
HERE = Path(__file__).resolve().parent
WORKSPACE_HELPER = HERE.parent.parent / "session-orchestrate" / "scripts" / "session_workspace.py"
CHECKPOINT_SECTIONS = (
    "handoff_focus",
    "codex_goal",
    "working_on",
    "next_action",
    "blockers",
    "learnings",
    "verification_state",
    "session_introspection",
    "relevant_files",
    "relevant_commits",
    "avoid_next_session",
    "route_contract",
    "useful_commands",
    "git_status",
)


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def resolve_root(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()
    override = os.environ.get("RESUME_SESSION_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    candidate = Path.cwd().resolve()
    for directory in (candidate, *candidate.parents):
        if (directory / ".session").is_dir():
            return directory
        if (directory / ".claude" / "session-data" / "CURRENT.md").is_file():
            return directory
    result = run_git(candidate, "rev-parse", "--show-toplevel")
    if result.returncode == 0 and result.stdout.strip():
        root = Path(result.stdout.strip()).resolve()
        if root == Path.home().resolve() and candidate != root:
            return candidate
        return root
    return candidate


def metadata(text: str, key: str) -> str | None:
    match = re.search(rf"^\*\*{re.escape(key)}:\*\*\s*(.*?)\s*$", text, re.MULTILINE)
    return match.group(1) if match else None


def section(text: str, heading: str) -> str | None:
    boundaries = "|".join(re.escape(name) for name in CHECKPOINT_SECTIONS if name != heading)
    match = re.search(
        rf"^## {re.escape(heading)}\n(.*?)(?=^## (?:{boundaries})\s*$|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1).rstrip() if match else None


def parse_goal(text: str) -> tuple[str | None, str | None, list[str]]:
    block = section(text, "codex_goal")
    if block is None or block.startswith("*(none supplied"):
        return None, None, []
    lines = block.splitlines()
    policy = next((line.split(":", 1)[1].strip() for line in lines if line.startswith("resume_policy:")), None)
    objective_index = next((index for index, line in enumerate(lines) if line == "objective:"), None)
    reasons: list[str] = []
    if policy is None:
        reasons.append("resume_policy_missing")
    elif policy not in POLICIES:
        reasons.append("resume_policy_invalid")
    objective = None
    if objective_index is None:
        reasons.append("objective_missing")
    else:
        objective_lines = []
        for line in lines[objective_index + 1:]:
            if line.startswith("resume_policy:"):
                break
            objective_lines.append(line)
        objective = "\n".join(objective_lines).rstrip() or None
        if objective is None:
            reasons.append("objective_empty")
    return policy, objective, reasons


def parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def route_first_command(text: str) -> str | None:
    block = section(text, "route_contract")
    if not block or block.startswith("*(none supplied"):
        return None
    match = re.search(r"^first_command:\s*(.*?)\s*$", block, re.MULTILINE)
    return match.group(1) if match and match.group(1) else None


def private_goal_file(objective: str) -> tuple[Path, str]:
    content = objective.rstrip() + "\n"
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    path = Path(tempfile.gettempdir()) / f"resume-session-goal-{digest[:16]}.md"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(content)
    path.chmod(0o600)
    return path, f"sha256:{digest}"


def checkpoint_path(root: Path) -> Path:
    helper = Path(os.environ.get("SESSION_WORKSPACE_HELPER", WORKSPACE_HELPER)).expanduser()
    if helper.is_file():
        result = subprocess.run(
            [sys.executable, str(helper), "path", "--root", str(root), "--field", "current"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip())
    canonical = root / ".session" / "CURRENT.md"
    legacy = root / ".claude" / "session-data" / "CURRENT.md"
    return canonical if canonical.parent.is_dir() or not legacy.is_file() else legacy


def current_git_state(root: Path) -> tuple[str | None, str | None]:
    top = run_git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root:
        return None, None
    branch = run_git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    commit = run_git(root, "rev-parse", "HEAD")
    return (
        branch.stdout.strip() if branch.returncode == 0 and branch.stdout.strip() else None,
        commit.stdout.strip() if commit.returncode == 0 and commit.stdout.strip() else None,
    )


def inspect(root: Path, *, now: datetime, write_goal_file: bool) -> dict[str, Any]:
    checkpoint = checkpoint_path(root)
    if not checkpoint.is_file():
        return {
            "success": True,
            "project_root": str(root),
            "checkpoint": None,
            "eligibility": "missing",
            "mode": "choose-next-goal",
            "reasons": ["checkpoint_missing"],
            "resume_policy": None,
            "goal_file": None,
            "goal_hash": None,
        }

    text = checkpoint.read_text(encoding="utf-8")
    policy, objective, reasons = parse_goal(text)
    saved_root = metadata(text, "repo_root")
    saved_branch = metadata(text, "branch")
    saved_commit = metadata(text, "last_commit")
    saved_time = metadata(text, "time")
    window_raw = metadata(text, "resume_window_hours")
    first_command = route_first_command(text)
    current_branch, current_commit = current_git_state(root)
    age_hours: float | None = None

    if policy == "ensure-active":
        if not saved_root:
            reasons.append("repo_root_missing")
        elif Path(saved_root).expanduser().resolve() != root:
            reasons.append("repo_root_mismatch")

        try:
            window_hours = int(window_raw) if window_raw is not None else DEFAULT_RESUME_WINDOW_HOURS
            if window_hours < 1 or window_hours > MAX_RESUME_WINDOW_HOURS:
                raise ValueError
        except ValueError:
            window_hours = DEFAULT_RESUME_WINDOW_HOURS
            reasons.append("resume_window_invalid")

        if not saved_time:
            reasons.append("checkpoint_time_missing")
        else:
            try:
                saved_at = parse_timestamp(saved_time)
                age_seconds = (now - saved_at).total_seconds()
                age_hours = round(age_seconds / 3600, 3)
                if age_seconds < -FUTURE_TOLERANCE_SECONDS:
                    reasons.append("checkpoint_from_future")
                elif age_seconds > window_hours * 3600:
                    reasons.append("checkpoint_expired")
            except ValueError:
                reasons.append("checkpoint_time_invalid")

        if current_branch is not None:
            if not saved_branch or saved_branch == "unknown":
                reasons.append("branch_unverifiable")
            elif saved_branch != current_branch:
                reasons.append("branch_mismatch")
        elif saved_branch and saved_branch != "unknown":
            reasons.append("repo_not_git")

        if current_commit is not None:
            if not saved_commit or saved_commit == "unknown":
                reasons.append("commit_unverifiable")
            else:
                exists = run_git(root, "cat-file", "-e", f"{saved_commit}^{{commit}}")
                if exists.returncode != 0:
                    reasons.append("saved_commit_missing")
                elif run_git(root, "merge-base", "--is-ancestor", saved_commit, current_commit).returncode != 0:
                    reasons.append("commit_diverged")
        elif saved_commit and saved_commit != "unknown":
            reasons.append("repo_not_git")

        if first_command:
            try:
                tokens = shlex.split(first_command)
            except ValueError:
                tokens = []
                reasons.append("first_command_invalid")
            command = next((token for token in tokens if "=" not in token.split("/", 1)[0]), None)
            if command:
                command_path = Path(command)
                if command_path.is_absolute() and not command_path.exists():
                    reasons.append("first_command_missing")
                elif "/" in command and not (root / command_path).exists():
                    reasons.append("first_command_missing")
                elif "/" not in command and shutil.which(command) is None:
                    reasons.append("first_command_unavailable")
    else:
        window_hours = None

    reasons = list(dict.fromkeys(reasons))
    if policy == "reference-only" and not reasons:
        eligibility = "reference-only"
        mode = "choose-next-goal"
    elif policy is None and not reasons:
        eligibility = "no-goal"
        mode = "choose-next-goal"
    elif policy == "ensure-active" and objective and not reasons:
        eligibility = "fresh"
        mode = "resume-exact-goal"
    elif any(reason in {"resume_policy_missing", "resume_policy_invalid", "objective_missing", "objective_empty"} for reason in reasons):
        eligibility = "invalid"
        mode = "review-checkpoint"
    else:
        eligibility = "stale"
        mode = "review-checkpoint"

    goal_file = None
    goal_hash = None
    if objective:
        content = objective.rstrip() + "\n"
        goal_hash = "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()
    if mode == "resume-exact-goal" and write_goal_file and objective:
        path, goal_hash = private_goal_file(objective)
        goal_file = str(path)

    return {
        "success": True,
        "project_root": str(root),
        "checkpoint": str(checkpoint),
        "eligibility": eligibility,
        "mode": mode,
        "reasons": reasons,
        "resume_policy": policy,
        "goal_file": goal_file,
        "goal_hash": goal_hash,
        "goal_chars": len(objective) if objective else 0,
        "metadata": {
            "saved_time": saved_time,
            "age_hours": age_hours,
            "resume_window_hours": window_hours,
            "saved_root": saved_root,
            "saved_branch": saved_branch,
            "current_branch": current_branch,
            "saved_commit": saved_commit,
            "current_commit": current_commit,
            "first_command": first_command,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect tactical checkpoint eligibility")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--path-only", action="store_true")
    parser.add_argument("--write-goal-file", action="store_true")
    parser.add_argument("--now", help="UTC ISO timestamp override for deterministic tests")
    args = parser.parse_args()
    try:
        root = resolve_root(args.root)
        checkpoint = checkpoint_path(root)
        if args.path_only:
            print(checkpoint)
            return 0
        now = parse_timestamp(args.now) if args.now else datetime.now(timezone.utc)
        print(json.dumps(inspect(root, now=now, write_goal_file=args.write_goal_file), indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"inspect_checkpoint: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
