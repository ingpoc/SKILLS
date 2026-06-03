#!/usr/bin/env python3
"""Ensure ChatGPT Atlas is always allowed for Codex Computer Use on macOS."""

from __future__ import annotations

import json
import os
from pathlib import Path


BUNDLE_ID = "com.openai.atlas"
APPROVALS_PATH = (
    Path.home()
    / "Library/Group Containers/2DC432GLL2.com.openai.sky.CUAService"
    / "Library/Application Support/Software/ComputerUseAppApprovals.json"
)


def main() -> int:
    if os.uname().sysname != "Darwin":
        print("atlas-computer-use: this helper only applies to macOS")
        return 2

    APPROVALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = json.loads(APPROVALS_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    approved = data.get("approvedBundleIdentifiers")
    if not isinstance(approved, list):
        approved = []

    normalized: list[str] = []
    seen: set[str] = set()
    for item in approved + [BUNDLE_ID]:
        if isinstance(item, str):
            item = item.strip()
            if item and item not in seen:
                normalized.append(item)
                seen.add(item)

    data["approvedBundleIdentifiers"] = normalized
    APPROVALS_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"atlas-computer-use: ensured {BUNDLE_ID}")
    print(APPROVALS_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
