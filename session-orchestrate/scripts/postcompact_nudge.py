#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def payload() -> dict[str, object]:
    try:
        value = json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def find_state(cwd: Path) -> Path | None:
    current = cwd.resolve()
    for root in (current, *current.parents):
        canonical = root / ".session" / "ORCHESTRATION.json"
        if canonical.is_file():
            return canonical
        legacy = root / ".claude" / "session-data" / "ORCHESTRATION.json"
        if legacy.is_file():
            return legacy
        if root == Path.home():
            break
    return None


def main() -> int:
    event = payload()
    cwd = event.get("cwd")
    if not isinstance(cwd, str) or not cwd.strip():
        print(json.dumps({"continue": True, "suppressOutput": True}))
        return 0
    state_path = find_state(Path(cwd))
    if state_path is None:
        print(json.dumps({"continue": True, "suppressOutput": True}))
        return 0
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print(json.dumps({"continue": True, "suppressOutput": True}))
        return 0
    if state.get("status") != "active":
        print(json.dumps({"continue": True, "suppressOutput": True}))
        return 0

    context = (
        "An automatic compaction occurred during an active session-orchestrate chain. "
        "Finish only the current atomic verification if safe; otherwise use the skill's "
        "unfinished emergency handoff with the exact active goal. Do not continue until a "
        "second compaction, and do not create more than one successor."
    )
    print(json.dumps({
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "PostCompact",
            "additionalContext": context,
        },
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
