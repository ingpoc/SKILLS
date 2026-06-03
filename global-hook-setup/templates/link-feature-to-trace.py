#!/usr/bin/env python3
"""
Global Hook: link-feature-to-trace.py

Automatically links new features to decision traces.
Non-blocking - creates a "feature created" trace for bookkeeping.
"""

import json
import sys
import subprocess
from datetime import datetime

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

    # Only process feature-list.json writes
    if "feature-list.json" not in file_path:
        sys.exit(0)

    # Check if new feature being added
    try:
        new_data = json.loads(content) if content else {}
        new_features = new_data.get("features", [])

        if not new_features:
            sys.exit(0)

        # Get the most recently added feature
        latest_feature = new_features[-1]
        feature_id = latest_feature.get("id", "")
        feature_title = latest_feature.get("title", "")

        if not feature_id:
            sys.exit(0)

        # Check for context-graph MCP and store trace
        # This is a placeholder - full implementation would use MCP tool
        # For now, just log to stderr (visible during setup)
        timestamp = datetime.now().isoformat()
        trace_entry = {
            "id": f"trace_{feature_id}_{timestamp}",
            "timestamp": timestamp,
            "category": "feature",
            "decision": f"Feature created: {feature_title}",
            "outcome": "pending",
            "feature_id": feature_id,
            "auto": True
        }

        # Would normally call: context_store_trace(...)
        # For now, just note what would happen
        print(f"[INFO] Would create trace for feature: {feature_id}", file=sys.stderr)

    except (json.JSONDecodeError, KeyError, IndexError):
        pass

    sys.exit(0)

if __name__ == "__main__":
    main()
