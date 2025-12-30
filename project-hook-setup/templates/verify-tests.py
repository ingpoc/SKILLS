#!/usr/bin/env python3
"""
Project Hook: verify-tests.py

Blocks marking a feature as tested=true unless tests pass.
Reads test command from .claude/config/project.json
"""

import json
import sys
import subprocess
import os

def main():
    # Read stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    # Support both Write (content) and Edit (new_string)
    content = tool_input.get("content", "") or tool_input.get("new_string", "")

    # Only check feature-list.json writes
    if "feature-list.json" not in file_path:
        sys.exit(0)

    # Only check when marking tested:true
    if '"tested": true' not in content and '"tested":true' not in content:
        sys.exit(0)

    # Get project root
    cwd = input_data.get("cwd", ".")
    project_root = cwd
    config_path = os.path.join(project_root, ".claude", "config", "project.json")

    # Read project config
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # No config, skip test check
        sys.exit(0)

    # Get test command
    test_command = config.get("test_command", "pytest")

    # Run tests
    try:
        result = subprocess.run(
            test_command.split(),
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=60
        )

        if result.returncode != 0:
            print("BLOCKED: Tests failed", file=sys.stderr)
            print("Fix failing tests before marking feature as tested", file=sys.stderr)
            print("", file=sys.stderr)
            print("Test output (last 500 chars):", file=sys.stderr)
            print(result.stdout[-500:] if result.stdout else result.stderr[-500:], file=sys.stderr)
            sys.exit(2)
    except subprocess.TimeoutExpired:
        print("BLOCKED: Tests timed out (>60s)", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print(f"BLOCKED: Test command not found: {test_command}", file=sys.stderr)
        print(f"Update .claude/config/project.json with correct test_command", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"BLOCKED: Error running tests: {e}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
