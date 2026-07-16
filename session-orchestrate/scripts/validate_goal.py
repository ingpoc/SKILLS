#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


MAX_WORDS = 300
LEGACY_MAX_WORDS = 450
BASE_REQUIRED = ("Outcome", "Scope", "Constraints", "Verification", "Stop conditions")
NEW_REQUIRED = ("Plan linkage", "Acceptance gap", "Actions", "Expected durable delta")
BASE_LIST_REQUIRED = ("Scope", "Verification", "Stop conditions")
NEW_LIST_REQUIRED = ("Acceptance gap", "Actions", "Expected durable delta")


def section(text: str, name: str) -> str:
    pattern = rf"(?ms)^## {re.escape(name)}\s*$\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def validate(text: str, *, legacy_resume: bool = False) -> list[str]:
    errors: list[str] = []
    words = re.findall(r"\b[\w'-]+\b", text)
    maximum = LEGACY_MAX_WORDS if legacy_resume else MAX_WORDS
    if len(words) > maximum:
        errors.append(f"goal is too long: {len(words)} words; maximum is {maximum}")

    required = BASE_REQUIRED if legacy_resume else (*BASE_REQUIRED, *NEW_REQUIRED)
    for name in required:
        if not section(text, name):
            errors.append(f"missing or empty section: ## {name}")

    list_required = BASE_LIST_REQUIRED if legacy_resume else (*BASE_LIST_REQUIRED, *NEW_LIST_REQUIRED)
    for name in list_required:
        body = section(text, name)
        if body and not re.search(r"(?m)^\s*(?:[-*]|\d+\.)\s+\S", body):
            errors.append(f"section requires at least one concrete list item: ## {name}")

    if not legacy_resume:
        gap = section(text, "Acceptance gap")
        if gap and not re.search(r"(?mi)^\s*[-*]\s*current\s*:\s+\S", gap):
            errors.append("acceptance gap requires a '- Current: ...' item")
        if gap and not re.search(r"(?mi)^\s*[-*]\s*exit\s*:\s+\S", gap):
            errors.append("acceptance gap requires an '- Exit: ...' item")

        delta = section(text, "Expected durable delta")
        delta_kinds = {
            kind.lower()
            for kind in re.findall(
                r"(?mi)^\s*[-*]\s*(implementation|runtime|evidence)\s*:\s+\S",
                delta,
            )
        }
        if "evidence" not in delta_kinds:
            errors.append("durable delta requires an '- Evidence: ...' item")
        if not delta_kinds.intersection({"implementation", "runtime"}):
            errors.append("durable delta requires an '- Implementation: ...' or '- Runtime: ...' item")

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
