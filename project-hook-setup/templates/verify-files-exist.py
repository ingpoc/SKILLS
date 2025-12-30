#!/usr/bin/env python3
"""
Project Hook: verify-files-exist.py

Blocks marking a feature as completed=true unless required files exist.
Reads implementation files from feature-list.json
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

    # Only check when marking completed:true
    if '"completed": true' not in content and '"completed":true' not in content:
        sys.exit(0)

    # Get project root
    cwd = input_data.get("cwd", ".")
    project_root = cwd
    feature_list_path = os.path.join(project_root, ".claude", "progress", "feature-list.json")

    # Read feature list
    try:
        with open(feature_list_path, "r") as f:
            feature_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        sys.exit(0)

    # Parse new content to find which feature is being marked complete
    try:
        new_data = json.loads(content) if content else {}
        features = new_data.get("features", [])

        missing_files = []
        for feature in features:
            if feature.get("completed") == True:
                # Check for implementation files
                impl_files = feature.get("files", [])
                feature_id = feature.get("id", "unknown")

                if not impl_files:
                    # No files specified, check common patterns
                    # If feature has "id", expect some implementation
                    print(f"Warning: Feature {feature_id} has no files specified", file=sys.stderr)
                    continue

                for file_path in impl_files:
                    full_path = os.path.join(project_root, file_path)
                    if not os.path.exists(full_path):
                        missing_files.append(file_path)

        if missing_files:
            print("BLOCKED: Required files missing for completed feature", file=sys.stderr)
            print("Missing files:", file=sys.stderr)
            for f in missing_files[:5]:  # Show first 5
                print(f"  - {f}", file=sys.stderr)
            sys.exit(2)

    except (json.JSONDecodeError, KeyError):
        pass

    sys.exit(0)

if __name__ == "__main__":
    main()
