#!/usr/bin/env python3
"""
Global Hook: require-outcome-update.py

Blocks marking a feature as tested=true unless decision trace outcomes are updated.
Part of Layer 3 (Learning) - ensures feedback loop completes.
"""

import json
import sys
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

    # Check for context-graph MCP availability
    # This is a simplified check - full implementation would query MCP
    traces_file = os.path.join(project_root, ".claude", "progress", "traces.json")

    # If no traces tracking, allow (agent discretion)
    if not os.path.exists(traces_file):
        sys.exit(0)

    try:
        with open(traces_file, "r") as f:
            traces_data = json.load(f)

        # Check if there are pending traces for this feature
        # Simplified - full implementation would parse feature_id from content
        pending_count = sum(1 for t in traces_data.get("traces", [])
                          if t.get("outcome") == "pending")

        if pending_count > 0:
            print(f"BLOCKED: {pending_count} decision trace(s) still pending", file=sys.stderr)
            print("Update outcomes before marking feature as tested", file=sys.stderr)
            print("Use: context_update_outcome(trace_id, outcome='success|failure')", file=sys.stderr)
            sys.exit(2)
    except (json.JSONDecodeError, FileNotFoundError):
        pass  # Can't read traces, allow

    sys.exit(0)

if __name__ == "__main__":
    main()
