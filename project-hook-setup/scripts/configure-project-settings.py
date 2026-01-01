#!/usr/bin/env python3
"""
Configure .claude/settings.json with project hook entries.

Adds PreToolUse hooks for project-specific validation:
- Test verification before marking tested
- File existence before marking complete
- Health checks for API projects
- Dependency validation
"""

import json
import sys
import os
from pathlib import Path

def get_project_root():
    """Get project root from env or cwd."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()

def configure_project_hooks():
    """Configure project hooks in .claude/settings.json."""
    project_root = get_project_root()
    hooks_dir = project_root / ".claude" / "hooks"
    settings_file = project_root / ".claude" / "settings.json"

    # Verify hooks exist
    required = [
        "verify-tests.py",
        "verify-files-exist.py",
        "verify-health.py",
        "require-dependencies.py",
        "session-entry.sh"
    ]

    missing = [h for h in required if not (hooks_dir / h).exists()]
    if missing:
        print(f"⚠️  Missing hooks: {', '.join(missing)}", file=sys.stderr)
        print("Run install-hooks.sh first", file=sys.stderr)
        return False

    # Load existing settings
    settings = {}
    if settings_file.exists():
        with open(settings_file) as f:
            settings = json.load(f)

    # Project hooks configuration using $CLAUDE_PROJECT_DIR
    project_hooks = {
        "PreToolUse": [
            {
                "matcher": "Write|Edit",
                "hooks": [
                    {"type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/verify-tests.py"},
                    {"type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/verify-files-exist.py"},
                    {"type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/verify-health.py"},
                    {"type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/require-dependencies.py"}
                ]
            }
        ]
    }

    # Merge hooks
    if "hooks" not in settings:
        settings["hooks"] = {}

    for hook_type, config in project_hooks.items():
        settings["hooks"][hook_type] = config
        print(f"✓ Configured {hook_type}")

    # Ensure .claude directory exists
    settings_file.parent.mkdir(parents=True, exist_ok=True)

    # Save
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)

    print(f"\n✅ Updated {settings_file}")
    return True


def main():
    if not configure_project_hooks():
        sys.exit(1)
    print("\nProject hooks configured in .claude/settings.json")


if __name__ == "__main__":
    main()
