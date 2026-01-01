#!/usr/bin/env python3
"""
Configure ~/.claude/settings.json with global hook entries.

Adds PreToolUse, PostToolUse, and SessionEnd hooks for:
- State transition validation
- Git hygiene enforcement
- Outcome tracking
- Feature-trace linking
- Session checkpoints
"""

import json
import sys
from pathlib import Path

HOOKS_DIR = Path.home() / ".claude" / "hooks"
SETTINGS_FILE = Path.home() / ".claude" / "settings.json"

# Hook configuration
GLOBAL_HOOKS_CONFIG = {
    "PreToolUse": [
        {
            "matcher": "Write|Edit",
            "hooks": [
                {"type": "command", "command": f"python3 {HOOKS_DIR}/verify-state-transition.py"},
                {"type": "command", "command": f"python3 {HOOKS_DIR}/require-commit-before-tested.py"},
                {"type": "command", "command": f"python3 {HOOKS_DIR}/require-outcome-update.py"}
            ]
        }
    ],
    "PostToolUse": [
        {
            "matcher": "Write|Edit",
            "hooks": [
                {"type": "command", "command": f"python3 {HOOKS_DIR}/link-feature-to-trace.py"},
                {"type": "command", "command": f"/bin/bash {HOOKS_DIR}/markdownlint-fix.sh"}
            ]
        }
    ],
    "SessionEnd": [
        {
            "hooks": [
                {"type": "command", "command": f"/bin/bash {HOOKS_DIR}/session-end.sh"},
                {"type": "command", "command": f"/bin/bash {HOOKS_DIR}/remind-decision-trace.sh"}
            ]
        }
    ]
}


def load_settings():
    """Load existing settings or create default."""
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    return {}


def save_settings(settings):
    """Save settings with proper formatting."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)


def configure_hooks():
    """Add global hooks to settings.json."""
    settings = load_settings()

    # Initialize hooks section if missing
    if "hooks" not in settings:
        settings["hooks"] = {}

    # Update each hook type
    for hook_type, config in GLOBAL_HOOKS_CONFIG.items():
        settings["hooks"][hook_type] = config
        print(f"✓ Configured {hook_type}")

    save_settings(settings)
    print(f"\n✅ Updated {SETTINGS_FILE}")


def verify_hooks():
    """Verify all hook scripts exist."""
    required = [
        "verify-state-transition.py",
        "require-commit-before-tested.py",
        "require-outcome-update.py",
        "link-feature-to-trace.py",
        "markdownlint-fix.sh",
        "session-end.sh",
        "remind-decision-trace.sh"
    ]

    missing = []
    for hook in required:
        if not (HOOKS_DIR / hook).exists():
            missing.append(hook)

    if missing:
        print(f"⚠️  Missing hooks: {', '.join(missing)}", file=sys.stderr)
        print("Run install-hooks.sh first", file=sys.stderr)
        return False
    return True


def main():
    if not verify_hooks():
        sys.exit(1)

    configure_hooks()
    print("\nGlobal hooks configured in settings.json")


if __name__ == "__main__":
    main()
