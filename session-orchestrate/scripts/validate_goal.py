#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


MIN_WORDS = 180
MAX_WORDS = 450
BASE_REQUIRED = ("Outcome", "Scope", "Constraints", "Verification", "Stop conditions")
NEW_REQUIRED = ("Plan linkage", "Actions")
BASE_LIST_REQUIRED = ("Scope", "Verification", "Stop conditions")


def section(text: str, name: str) -> str:
    pattern = rf"(?ms)^## {re.escape(name)}\s*$\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def validate(text: str, *, legacy_resume: bool = False) -> list[str]:
    errors: list[str] = []
    words = re.findall(r"\b[\w'-]+\b", text)
    if len(words) < MIN_WORDS:
        errors.append(f"goal is too short: {len(words)} words; minimum is {MIN_WORDS}")
    if len(words) > MAX_WORDS:
        errors.append(f"goal is too long: {len(words)} words; maximum is {MAX_WORDS}")

    required = BASE_REQUIRED if legacy_resume else (*BASE_REQUIRED, *NEW_REQUIRED)
    for name in required:
        if not section(text, name):
            errors.append(f"missing or empty section: ## {name}")

    list_required = BASE_LIST_REQUIRED if legacy_resume else (*BASE_LIST_REQUIRED, "Actions")
    for name in list_required:
        body = section(text, name)
        if body and not re.search(r"(?m)^\s*(?:[-*]|\d+\.)\s+\S", body):
            errors.append(f"section requires at least one concrete list item: ## {name}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a session-sized Codex goal")
    parser.add_argument("goal_file", type=Path)
    parser.add_argument(
        "--legacy-resume",
        action="store_true",
        help="allow the old goal shape only when preserving an eligible checkpoint exactly",
    )
    args = parser.parse_args()
    try:
        text = args.goal_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"validate_goal: {exc}", file=sys.stderr)
        return 2

    errors = validate(text, legacy_resume=args.legacy_resume)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: session goal is {len(re.findall(r'\b[\w\'-]+\b', text))} words")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
