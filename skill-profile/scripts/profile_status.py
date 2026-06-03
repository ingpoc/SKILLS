#!/usr/bin/env python3
"""Read-only status helper for ~/.codex/skills profile branches."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def branch_exists(repo: Path, branch: str) -> bool:
    return git(repo, "rev-parse", "--verify", "--quiet", branch, check=False).returncode == 0


def path_exists_on_branch(repo: Path, branch: str, path: str) -> bool:
    return git(repo, "cat-file", "-e", f"{branch}:{path}", check=False).returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Report skill profile branch state")
    parser.add_argument("--repo", default="~/.codex/skills", help="skills repo path")
    parser.add_argument("--profile", help="expected profile branch name")
    parser.add_argument("--skill", help="skill directory to check")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    current_branch = git(repo, "branch", "--show-current").stdout.strip()
    status = git(repo, "status", "--short", "--branch").stdout.splitlines()
    branches = git(repo, "branch", "--format", "%(refname:short)").stdout.splitlines()

    data: dict[str, object] = {
        "repo": str(repo),
        "current_branch": current_branch,
        "status": status,
        "has_main": "main" in branches,
        "has_skill_profile": (repo / "skill-profile" / "SKILL.md").exists(),
    }

    if args.profile:
        data["profile"] = args.profile
        data["profile_branch_exists"] = branch_exists(repo, args.profile)

    if args.skill:
        skill = args.skill.strip().strip("/")
        data["skill"] = skill
        data["current_has_skill"] = (repo / skill / "SKILL.md").exists()
        data["main_has_skill"] = path_exists_on_branch(repo, "main", skill)

    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
