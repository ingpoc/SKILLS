#!/usr/bin/env python3
"""
Validate .claude/settings.json has correct project hook configuration.

Exit codes:
  0 - All hooks configured correctly
  1 - Missing or incorrect configuration
"""

import json
import os
import sys
from pathlib import Path


def get_project_root():
    """Get project root from env or cwd."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()


REQUIRED_HOOKS = {
    "PreToolUse": {
        "matcher": "Write|Edit",
        "scripts": [
            "verify-tests.py",
            "verify-files-exist.py",
            "verify-health.py",
            "require-dependencies.py"
        ]
    }
}


def validate():
    project_root = get_project_root()
    settings_file = project_root / ".claude" / "settings.json"
    errors = []

    print(f"Validating project hooks in: {project_root}")

    # Check settings file exists
    if not settings_file.exists():
        print(f"❌ Settings file not found: {settings_file}")
        return False

    # Load settings
    try:
        with open(settings_file) as f:
            settings = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in settings: {e}")
        return False

    # Check hooks section
    hooks = settings.get("hooks", {})
    if not hooks:
        print("❌ No 'hooks' section in settings.json")
        return False

    # Validate each hook type
    for hook_type, config in REQUIRED_HOOKS.items():
        print(f"\nChecking {hook_type}...")

        if hook_type not in hooks:
            errors.append(f"Missing {hook_type} configuration")
            print(f"  ❌ {hook_type} not configured")
            continue

        hook_entries = hooks[hook_type]
        if not hook_entries:
            errors.append(f"Empty {hook_type} configuration")
            print(f"  ❌ {hook_type} is empty")
            continue

        # Check matcher
        found_matcher = False
        for entry in hook_entries:
            if entry.get("matcher") == config["matcher"]:
                found_matcher = True
                # Check scripts
                entry_hooks = entry.get("hooks", [])
                for script in config["scripts"]:
                    script_found = any(script in h.get("command", "") for h in entry_hooks)
                    if script_found:
                        print(f"  ✓ {script}")
                    else:
                        errors.append(f"Missing {script} in {hook_type}")
                        print(f"  ❌ {script} not found")
                break

        if not found_matcher:
            errors.append(f"Missing matcher '{config['matcher']}' for {hook_type}")
            print(f"  ❌ No entry with matcher '{config['matcher']}'")

    # Summary
    print("")
    if errors:
        print(f"❌ Validation failed with {len(errors)} error(s)")
        for err in errors:
            print(f"   - {err}")
        return False
    else:
        print("✅ All project hooks configured correctly in .claude/settings.json")
        return True


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
