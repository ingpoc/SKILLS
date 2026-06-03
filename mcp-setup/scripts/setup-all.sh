#!/bin/bash
set -euo pipefail

echo "=== Runtime-Aware MCP Setup ==="

PROJECT_ROOT="$(pwd)"
MCP_SERVERS_ROOT="${MCP_SERVERS_ROOT:-$HOME/Documents/remote-claude/mcp-servers}"
TOKEN_EFFICIENT_PATH="$MCP_SERVERS_ROOT/token-efficient-mcp/dist/index.js"
CONTEXT_GRAPH_DIR="$MCP_SERVERS_ROOT/context-graph-mcp"

if [ -n "${MCP_RUNTIME:-}" ]; then
  RUNTIME="$MCP_RUNTIME"
elif [ -d "$HOME/.codex" ]; then
  RUNTIME="codex"
else
  RUNTIME="claude"
fi

echo "Project: $PROJECT_ROOT"
echo "Runtime: $RUNTIME"
echo "MCP root: $MCP_SERVERS_ROOT"

if [ ! -f "$TOKEN_EFFICIENT_PATH" ]; then
  echo "✗ Missing token-efficient build: $TOKEN_EFFICIENT_PATH"
  echo "  Build it once in central repo."
  exit 1
fi

if [ ! -f "$CONTEXT_GRAPH_DIR/server.py" ]; then
  echo "✗ Missing context-graph server: $CONTEXT_GRAPH_DIR/server.py"
  exit 1
fi

if [ "$RUNTIME" = "codex" ]; then
  mkdir -p "$PROJECT_ROOT/.codex"
  CONFIG_FILE="$PROJECT_ROOT/.codex/config.toml"
  MANAGED_BLOCK=$(cat <<BLOCK
# BEGIN mcp-setup managed
[mcp_servers.token-efficient]
command = "node"
args = ["$TOKEN_EFFICIENT_PATH"]

[mcp_servers.context-graph]
command = "uv"
args = ["--directory", "$CONTEXT_GRAPH_DIR", "run", "python", "server.py"]

[mcp_servers.context-graph.env]
UV_CACHE_DIR = "/tmp/uv-cache-codex"
VOYAGE_API_KEY = "\${VOYAGE_API_KEY}"
# END mcp-setup managed
BLOCK
)

  if [ -f "$CONFIG_FILE" ]; then
    awk '
      BEGIN {skip=0}
      /# BEGIN mcp-setup managed/ {skip=1; next}
      /# END mcp-setup managed/ {skip=0; next}
      skip==0 {print}
    ' "$CONFIG_FILE" > "$CONFIG_FILE.tmp"
    printf "\n%s\n" "$MANAGED_BLOCK" >> "$CONFIG_FILE.tmp"
    mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
  else
    printf "%s\n" "$MANAGED_BLOCK" > "$CONFIG_FILE"
  fi

  echo "✓ Wrote Codex MCP config: $CONFIG_FILE"
else
  MCP_FILE="$PROJECT_ROOT/.mcp.json"
  python3 - <<PY
import json, pathlib
p = pathlib.Path(r"$MCP_FILE")
data = {"mcpServers": {}}
if p.exists():
    try:
        data = json.loads(p.read_text())
    except Exception:
        data = {"mcpServers": {}}
servers = data.setdefault("mcpServers", {})
servers["token-efficient"] = {
    "command": "node",
    "args": [r"$TOKEN_EFFICIENT_PATH"],
}
servers["context-graph"] = {
    "command": "uv",
    "args": ["--directory", r"$CONTEXT_GRAPH_DIR", "run", "python", "server.py"],
    "env": {"VOYAGE_API_KEY": "${VOYAGE_API_KEY}"},
}
p.write_text(json.dumps(data, indent=2) + "\n")
print(f"✓ Wrote Claude MCP config: {p}")
PY
fi

echo ""
echo "Setup complete."
echo "Next: run verify-setup.sh"
