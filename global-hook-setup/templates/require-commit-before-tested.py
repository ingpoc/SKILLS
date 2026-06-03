#!/usr/bin/env python3
"""
Global Hook: require-commit-before-tested.py

Blocks marking a feature as tested=true if there are uncommitted changes.
Ensures git hygiene - all code must be committed before validation.
"""

import json
import sys
import subprocess

def main():
    # Read stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    # Support both Write (content) and Edit (new_string)
    content = tool_input.get("content", "") or tool_input.get("new_string", "")

    # Only check when marking tested:true
    if '"tested": true' not in content and '"tested":true' not in content:
        sys.exit(0)

    # Check git status
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=input_data.get("cwd", ".")
        )

        # If any output, there are uncommitted changes
        if result.stdout.strip():
            print("BLOCKED: Uncommitted changes detected", file=sys.stderr)
            print("Commit changes before marking feature as tested", file=sys.stderr)
            print("Uncommitted files:", file=sys.stderr)
            for line in result.stdout.strip().split('\n')[:5]:  # Show first 5
                print(f"  {line}", file=sys.stderr)
            sys.exit(2)
    except (FileNotFoundError, subprocess.SubprocessError):
        pass  # Git not available, skip check

    sys.exit(0)

if __name__ == "__main__":
    main()
