#!/usr/bin/env python3
"""
Project Hook: require-dependencies.py

Blocks writing to source files if required dependencies are missing.
Reads env vars and services from .claude/config/project.json
"""

import json
import sys
import os
import socket
import subprocess

def check_port(port):
    """Check if a port is open (service running)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("127.0.0.1", int(port)))
        sock.close()
        return result == 0
    except:
        return False

def main():
    # Read stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Only check writes to source directories
    # Common patterns: src/, lib/, app/, .py, .js, .ts files
    if not any(pattern in file_path for pattern in ["src/", "lib/", "app/", ".py", ".js", ".ts"]):
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
        # No config, skip dependency check
        sys.exit(0)

    issues = []

    # Check required environment variables
    required_env = config.get("required_env", [])
    for env_var in required_env:
        if not os.environ.get(env_var):
            issues.append(f"Environment variable not set: {env_var}")

    # Check required services
    required_services = config.get("required_services", [])
    for service in required_services:
        # Parse service format: "redis://localhost:6379" or just "6379"
        if "://" in service:
            # Extract port from URL
            try:
                parts = service.split("://")
                if ":" in parts[1]:
                    port = parts[1].split(":")[1]
                    if not check_port(port):
                        issues.append(f"Service not running: {service}")
            except:
                pass
        elif service.isdigit():
            # Just a port number
            if not check_port(service):
                issues.append(f"Service not running on port: {service}")

    if issues:
        print("BLOCKED: Required dependencies missing", file=sys.stderr)
        print("", file=sys.stderr)
        print("Missing:", file=sys.stderr)
        for issue in issues[:5]:
            print(f"  - {issue}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Update .claude/config/project.json if this is incorrect", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
