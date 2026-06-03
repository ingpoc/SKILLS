#!/bin/bash
set -uo pipefail

PASS=0
FAIL=0

check_pass() { echo "  ✓ $1"; PASS=$((PASS+1)); }
check_fail() { echo "  ✗ $1"; FAIL=$((FAIL+1)); }

PROJECT_ROOT="$(pwd)"
MCP_SERVERS_ROOT="${MCP_SERVERS_ROOT:-$HOME/Documents/remote-claude/mcp-servers}"
TOKEN_EFFICIENT_PATH="$MCP_SERVERS_ROOT/token-efficient-mcp/dist/index.js"
CONTEXT_GRAPH_DIR="$MCP_SERVERS_ROOT/context-graph-mcp"

if [ -n "${MCP_RUNTIME:-}" ]; then
  RUNTIME="$MCP_RUNTIME"
elif [ -f "$PROJECT_ROOT/.codex/config.toml" ]; then
  RUNTIME="codex"
elif [ -f "$PROJECT_ROOT/.mcp.json" ]; then
  RUNTIME="claude"
else
  RUNTIME="unknown"
fi

echo "=== MCP Setup Verification ==="
echo "Project: $PROJECT_ROOT"
echo "Runtime: $RUNTIME"
echo ""

echo "1. Central server paths"
[ -f "$TOKEN_EFFICIENT_PATH" ] && check_pass "token-efficient exists" || check_fail "token-efficient missing: $TOKEN_EFFICIENT_PATH"
[ -f "$CONTEXT_GRAPH_DIR/server.py" ] && check_pass "context-graph exists" || check_fail "context-graph missing: $CONTEXT_GRAPH_DIR/server.py"

echo ""
echo "2. Project config"
if [ "$RUNTIME" = "codex" ]; then
  CFG="$PROJECT_ROOT/.codex/config.toml"
  if [ -f "$CFG" ]; then
    check_pass "Codex config exists: .codex/config.toml"
    rg -n "\[mcp_servers.token-efficient\]|\[mcp_servers.context-graph\]" "$CFG" >/dev/null && check_pass "Codex MCP entries present" || check_fail "Codex MCP entries missing"
  else
    check_fail "Missing .codex/config.toml"
  fi
elif [ "$RUNTIME" = "claude" ]; then
  CFG="$PROJECT_ROOT/.mcp.json"
  if [ -f "$CFG" ]; then
    check_pass "Claude config exists: .mcp.json"
    jq -e '.mcpServers["token-efficient"] and .mcpServers["context-graph"]' "$CFG" >/dev/null 2>&1 && check_pass "Claude MCP entries present" || check_fail "Claude MCP entries missing"
  else
    check_fail "Missing .mcp.json"
  fi
else
  check_fail "No project MCP config found"
fi

echo ""
echo "3. Dependencies"
command -v node >/dev/null 2>&1 && check_pass "node available" || check_fail "node missing"
command -v uv >/dev/null 2>&1 && check_pass "uv available" || check_fail "uv missing"
python3 -c "import chromadb" >/dev/null 2>&1 && check_pass "chromadb import ok" || check_fail "chromadb missing"

echo ""
echo "=== Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
[ $FAIL -eq 0 ] && exit 0 || exit 1
