#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


MIN_WORDS = 180
MAX_WORDS = 450
REQUIRED = ("Outcome", "Scope", "Constraints", "Verification", "Stop conditions")
LIST_REQUIRED = ("Scope", "Verification", "Stop conditions")


def section(text: str, name: str) -> str:
    pattern = rf"(?ms)^## {re.escape(name)}\s*$\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def validate(text: str) -> list[str]:
    errors: list[str] = []
    words = re.findall(r"\b[\w'-]+\b", text)
    if len(words) < MIN_WORDS:
        errors.append(f"goal is too short: {len(words)} words; minimum is {MIN_WORDS}")
    if len(words) > MAX_WORDS:
        errors.append(f"goal is too long: {len(words)} words; maximum is {MAX_WORDS}")

    for name in REQUIRED:
        if not section(text, name):
            errors.append(f"missing or empty section: ## {name}")

    for name in LIST_REQUIRED:
        body = section(text, name)
        if body and not re.search(r"(?m)^\s*(?:[-*]|\d+\.)\s+\S", body):
            errors.append(f"section requires at least one concrete list item: ## {name}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a session-sized Codex goal")
    parser.add_argument("goal_file", type=Path)
    args = parser.parse_args()
    try:
        text = args.goal_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"validate_goal: {exc}", file=sys.stderr)
        return 2

    errors = validate(text)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: session goal is {len(re.findall(r'\b[\w\'-]+\b', text))} words")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
