#!/usr/bin/env python3
"""
Enforcement hook: Block feature work if required dependencies are missing.

Event: PreToolUse (Write/Edit on src/ files)
Blocks: If required_env vars in project.json are not set
"""

import json
import sys
import os


def load_project_config() -> dict:
    """Load project.json config."""
    config_path = ".claude/config/project.json"
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {}


def check_required_env(config: dict) -> list:
    """Check if required environment variables are set."""
    missing = []
    required = config.get("required_env", [])

    for var in required:
        if not os.environ.get(var):
            missing.append(var)

    return missing


def main():
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Only check writes to src/ files (feature implementation)
    if not file_path:
        sys.exit(0)

    # Allow writes to config and progress files
    if ".claude/" in file_path or "config" in file_path:
        sys.exit(0)

    # Only check src/ or app/ directories (actual implementation)
    is_source_file = any(x in file_path for x in ["/src/", "/app/", "/lib/", "/components/"])
    if not is_source_file:
        sys.exit(0)

    # Load config and check dependencies
    config = load_project_config()
    if not config:
        sys.exit(0)  # No config, allow

    missing_env = check_required_env(config)

    if missing_env:
        print("BLOCKED: Missing required environment variables", file=sys.stderr)
        print("", file=sys.stderr)
        for var in missing_env:
            print(f"  - {var}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Set these variables before implementing features:", file=sys.stderr)
        print(f"  export {missing_env[0]}=your_value", file=sys.stderr)
        print("", file=sys.stderr)
        print("Or update .claude/config/project.json to remove from required_env", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
