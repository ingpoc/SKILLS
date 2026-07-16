#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

MAX_WORDS = 300
LEGACY_MAX_WORDS = 450
BASE_REQUIRED = ("Outcome", "Scope", "Constraints", "Verification", "Stop conditions")
NEW_REQUIRED = ("Plan linkage", "Acceptance gap", "Expected durable delta")
BASE_LIST_REQUIRED = ("Scope", "Verification", "Stop conditions")
NEW_LIST_REQUIRED = ("Acceptance gap", "Expected durable delta")
DELIVERY_UNITS = ("bounded-deliverable", "project-lifecycle")
LIFECYCLE_KINDS = ("implementation", "verification", "promotion", "handoff", "hardening")


def canonical_objective(text: str) -> str:
    """Return the byte-stable objective representation shared by every owner."""
    return text.rstrip() + "\n"


def objective_hash(text: str) -> str:
    canonical = canonical_objective(text)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def section(text: str, name: str) -> str:
    pattern = rf"(?ms)^## {re.escape(name)}\s*$\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def validate(
    text: str,
    *,
    legacy_resume: bool = False,
    delivery_unit: str = "bounded-deliverable",
) -> list[str]:
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
        actions = section(text, "Actions")
        if delivery_unit == "bounded-deliverable" and not actions:
            errors.append("missing or empty section: ## Actions")
        if delivery_unit == "bounded-deliverable" and actions and not re.search(
            r"(?m)^\s*(?:[-*]|\d+\.)\s+\S", actions
        ):
            errors.append("section requires at least one concrete list item: ## Actions")
        if delivery_unit == "project-lifecycle" and actions:
            errors.append("project lifecycle must omit ## Actions; ## Delivery lifecycle owns its actions")

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

        if delivery_unit == "project-lifecycle":
            lifecycle = section(text, "Delivery lifecycle")
            if not lifecycle:
                errors.append("missing or empty section: ## Delivery lifecycle")
            else:
                kinds = [
                    kind.lower()
                    for kind in re.findall(
                        rf"(?mi)^\s*[-*]\s*\[({'|'.join(LIFECYCLE_KINDS)})\]\s+\S",
                        lifecycle,
                    )
                ]
                if "implementation" not in kinds:
                    errors.append("delivery lifecycle requires an [implementation] stage")
                implementation_index = kinds.index("implementation") if "implementation" in kinds else -1
                later_verification = any(
                    kind == "verification" and index > implementation_index
                    for index, kind in enumerate(kinds)
                )
                if not later_verification:
                    errors.append("delivery lifecycle requires [verification] after [implementation]")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a session-sized Codex goal")
    parser.add_argument("goal_file", type=Path)
    parser.add_argument(
        "--legacy-resume",
        action="store_true",
        help="allow the old goal shape only when preserving an eligible checkpoint exactly",
    )
    parser.add_argument(
        "--delivery-unit",
        choices=DELIVERY_UNITS,
        default="bounded-deliverable",
        help="apply the selected program goal's delivery-unit contract",
    )
    args = parser.parse_args()
    try:
        text = args.goal_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"validate_goal: {exc}", file=sys.stderr)
        return 2

    errors = validate(
        text,
        legacy_resume=args.legacy_resume,
        delivery_unit=args.delivery_unit,
    )
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: session goal is {len(re.findall(r'\b[\w\'-]+\b', text))} words")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
