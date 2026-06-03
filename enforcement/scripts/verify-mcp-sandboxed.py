#!/usr/bin/env python3
"""
Verify MCP servers are wrapped with sandbox-runtime (srt)
Event: PreToolUse (Write .mcp.json)
"""

import json
import sys

def main():
    input_data = json.load(sys.stdin)
    tool_input = input_data.get("tool_input", {})
    content = tool_input.get("content", "")

    try:
        config = json.loads(content)
        mcp_servers = config.get("mcpServers", {})

        unsandboxed = []
        for name, server in mcp_servers.items():
            command = server.get("command", "")
            # Allow local scripts
            if command.startswith("./") or command.startswith("python") or command.startswith("node"):
                continue
            # npx commands should be wrapped with srt
            if "npx" in command and "srt" not in command:
                unsandboxed.append(name)

        if unsandboxed:
            print("BLOCKED: MCP servers must be wrapped with 'srt'", file=sys.stderr)
            print(f"Unsandboxed: {unsandboxed}", file=sys.stderr)
            print("Fix: \"command\": \"srt\", \"args\": [\"npx\", ...]", file=sys.stderr)
            sys.exit(2)

    except json.JSONDecodeError:
        pass

    sys.exit(0)

if __name__ == "__main__":
    main()
