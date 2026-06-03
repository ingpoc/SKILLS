#!/usr/bin/env python3
"""Render GOAL.md and PROGRESS.md for a code quality audit worktree."""

from __future__ import annotations

import argparse
import pathlib
import re


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def section_body(text: str, section_name: str) -> str:
    lines = text.splitlines(keepends=True)
    header = f"## {section_name}"
    start = None
    for index, line in enumerate(lines):
        if line.strip() == header:
            start = index + 1
            break
    if start is None:
        return "None yet."

    end = len(lines)
    for index in range(start, len(lines)):
        line = lines[index]
        if line.startswith("## ") and line.strip() != header:
            end = index
            break

    body = "".join(lines[start:end]).strip()
    return body if body else "None yet."


def next_auditor_turn(existing: str | None) -> str:
    if not existing:
        return "1"
    match = re.search(r"^> Auditor turn:\s*(\d+)\s*$", existing, re.MULTILINE)
    if not match:
        return "1"
    return str(int(match.group(1)) + 1)


def render(template: str, values: dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--base-branch", required=True)
    parser.add_argument("--audit-branch", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--iso-timestamp", required=True)
    parser.add_argument("--template-dir", required=True)
    args = parser.parse_args()

    template_dir = pathlib.Path(args.template_dir)
    worktree = pathlib.Path(args.worktree)
    progress_path = worktree / "PROGRESS.md"

    existing_progress = progress_path.read_text(encoding="utf-8") if progress_path.exists() else None
    completed = section_body(existing_progress, "Completed") if existing_progress else "None yet."
    rejected = section_body(existing_progress, "Rejected") if existing_progress else "None yet."

    values = {
        "ISO_TIMESTAMP": args.iso_timestamp,
        "REPO_ROOT": args.repo_root,
        "WORKTREE": args.worktree,
        "BASE_BRANCH": args.base_branch,
        "AUDIT_BRANCH": args.audit_branch,
        "COMMIT": args.commit,
        "AUDITOR_TURN": next_auditor_turn(existing_progress),
        "COMPLETED_SECTION": completed,
        "REJECTED_SECTION": rejected,
    }

    goal = render(read_text(template_dir / "GOAL.md"), values)
    progress = render(read_text(template_dir / "PROGRESS.md"), values)

    (worktree / "GOAL.md").write_text(goal, encoding="utf-8")
    progress_path.write_text(progress, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
