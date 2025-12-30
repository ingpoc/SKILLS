#!/usr/bin/env python3
"""
Project Hook: verify-health.py

Blocks marking a feature as tested=true for API projects unless server is healthy.
Reads health_check command from .claude/config/project.json
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
        # No config, skip health check
        sys.exit(0)

    # Check if this is an API project that needs health check
    project_type = config.get("project_type", "")
    if project_type not in ["fastapi", "django", "node", "express", "api"]:
        # Not an API project, skip health check
        sys.exit(0)

    # Get health check command
    health_check = config.get("health_check", "")

    if not health_check:
        # No health check configured, skip
        sys.exit(0)

    # Run health check
    try:
        result = subprocess.run(
            health_check,
            shell=True,
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=10
        )

        if result.returncode != 0:
            print("BLOCKED: Development server health check failed", file=sys.stderr)
            print("Ensure dev server is running before marking feature as tested", file=sys.stderr)
            print(f"Health check: {health_check}", file=sys.stderr)
            if result.stderr:
                print(f"Error: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(2)
    except subprocess.TimeoutExpired:
        print("BLOCKED: Health check timed out (>10s)", file=sys.stderr)
        print("Server may be unresponsive", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        # Health check failed, but might be environment issue
        # Log warning but don't block
        print(f"Warning: Could not run health check: {e}", file=sys.stderr)
        print("Continuing anyway (ensure server is running manually)", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()
