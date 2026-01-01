#!/usr/bin/env python3
"""
CLAUDE.md Type Detection

Determines which CLAUDE.md type to create/update based on context.

Usage:
    python detect-claude-type.py [--json]

Returns:
    JSON with type, path, exists, reason
"""

import json
import sys
from pathlib import Path


def detect_claude_type(cwd=None):
    """
    Detect which CLAUDE.md type based on current working directory.

    Returns:
        dict: {type, path, exists, suggested_type, reason}
    """
    cwd = Path(cwd or Path.cwd())
    home = Path.home()

    # Global detection
    if cwd == home / ".claude" or str(cwd).startswith(str(home / ".claude")):
        return {
            "type": "global",
            "path": str(home / ".claude/CLAUDE.md"),
            "exists": (home / ".claude/CLAUDE.md").exists(),
            "suggested_type": "global",
            "reason": "In ~/.claude directory"
        }

    # Project detection
    if (cwd / ".claude").exists() and (cwd / ".claude").is_dir():
        return {
            "type": "project",
            "path": str(cwd / ".claude/CLAUDE.md"),
            "exists": (cwd / ".claude/CLAUDE.md").exists(),
            "suggested_type": "project",
            "reason": ".claude directory found"
        }

    # Local detection (gitignored personal overrides)
    if (cwd / "CLAUDE.local.md").exists():
        return {
            "type": "local",
            "path": str(cwd / "CLAUDE.local.md"),
            "exists": True,
            "suggested_type": "local",
            "reason": "CLAUDE.local.md exists"
        }

    # Rules detection (check if .claude/rules exists)
    rules_dir = cwd / ".claude" / "rules"
    if rules_dir.exists() and rules_dir.is_dir():
        return {
            "type": "rules",
            "path": str(rules_dir),
            "exists": True,
            "suggested_type": "rules",
            "reason": ".claude/rules directory exists"
        }

    # Default: suggest project type
    return {
        "type": "project",
        "path": str(cwd / ".claude/CLAUDE.md"),
        "exists": (cwd / ".claude" / "CLAUDE.md").exists(),
        "suggested_type": "project",
        "reason": "Default for project directories"
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Detect CLAUDE.md type from context")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--path", help="Directory to check (default: cwd)")
    args = parser.parse_args()

    result = detect_claude_type(args.path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Type: {result['type']}")
        print(f"Path: {result['path']}")
        print(f"Exists: {result['exists']}")
        print(f"Reason: {result['reason']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
