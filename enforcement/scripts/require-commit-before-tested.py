#!/usr/bin/env python3
"""
Enforcement hook: Block marking feature as tested without git commit.

From Anthropic Effective Harnesses: "Git commit history with descriptive messages"

Event: PreToolUse (Write/Edit on feature-list.json)
Blocks: Setting status="tested" when there are uncommitted changes
"""

import json
import sys
import os
import subprocess


def has_uncommitted_changes() -> bool:
    """Check if there are uncommitted changes in the repo."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def get_last_commit_for_feature(feature_id: str) -> str:
    """Get the last commit hash for a feature from feature-list.json."""
    try:
        with open(".claude/progress/feature-list.json") as f:
            data = json.load(f)
            for feature in data.get("features", []):
                if feature.get("id") == feature_id:
                    return feature.get("last_commit", "")
    except Exception:
        pass
    return ""


def main():
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")

    # Only check writes to feature-list.json
    if "feature-list.json" not in file_path:
        sys.exit(0)

    # Only check if setting status to "tested"
    if '"status": "tested"' not in content and '"status":"tested"' not in content:
        sys.exit(0)

    # Check for uncommitted changes
    if has_uncommitted_changes():
        print("BLOCKED: Cannot mark feature as tested with uncommitted changes", file=sys.stderr)
        print("", file=sys.stderr)
        print("Run: .skills/implementation/scripts/feature-commit.sh <feature-id>", file=sys.stderr)
        print("Then retry marking the feature as tested.", file=sys.stderr)
        sys.exit(2)

    # Parse the new content to find which feature is being marked tested
    try:
        new_data = json.loads(content)
        for feature in new_data.get("features", []):
            if feature.get("status") == "tested":
                feature_id = feature.get("id", "")
                last_commit = feature.get("last_commit", "")

                # Warn if no commit hash recorded (but don't block)
                if not last_commit:
                    print(f"WARNING: Feature {feature_id} has no commit hash recorded", file=sys.stderr)
                    print("Consider running feature-commit.sh to track commits", file=sys.stderr)
    except json.JSONDecodeError:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
