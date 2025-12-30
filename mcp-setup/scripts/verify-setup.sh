#!/bin/bash
# Verify MCP servers are configured correctly (works for any user)

echo "=== MCP Setup Verification ==="
echo ""

PASS=0
FAIL=0

check_pass() {
    echo "  ✓ $1"
    ((PASS++))
}

check_fail() {
    echo "  ✗ $1"
    ((FAIL++))
}

# ─────────────────────────────────────────────────────────────────
# Detect paths (works for any user)
# ─────────────────────────────────────────────────────────────────
# Script is at: .skills/mcp-setup/scripts/verify-setup.sh
# Agent harness is 3 levels up (scripts/ → mcp-setup/ → .skills/ → agent-harness/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_HARNESS="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Auto-detect token-efficient MCP in common locations
TOKEN_EFFICIENT=""
for path in \
    "$HOME/Documents/remote-claude/token-efficient-mcp" \
    "$HOME/remote-claude/token-efficient-mcp" \
    "$HOME/token-efficient-mcp" \
    "$(dirname "$AGENT_HARNESS")/token-efficient-mcp"
do
    if [ -d "$path" ]; then
        TOKEN_EFFICIENT="$path"
        break
    fi
done

CONTEXT_GRAPH="$AGENT_HARNESS/context-graph-mcp"

# ─────────────────────────────────────────────────────────────────
# Check .mcp.json exists
# ─────────────────────────────────────────────────────────────────
echo "1. Checking configuration..."

MCP_FILE="$AGENT_HARNESS/.mcp.json"

if [ -f "$MCP_FILE" ]; then
    check_pass ".mcp.json exists at $MCP_FILE"
else
    check_fail ".mcp.json not found"
    echo "     Run setup-all.sh to create it"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# Check token-efficient MCP
# ─────────────────────────────────────────────────────────────────
echo "2. Checking token-efficient MCP..."

if [ -z "$TOKEN_EFFICIENT" ]; then
    check_fail "token-efficient MCP not found in common locations"
    echo "     Locations checked:"
    echo "       - ~/Documents/remote-claude/token-efficient-mcp"
    echo "       - ~/remote-claude/token-efficient-mcp"
    echo "       - ~/token-efficient-mcp"
    echo "       - ../token-efficient-mcp"
elif [ -f "$TOKEN_EFFICIENT/dist/index.js" ]; then
    check_pass "token-efficient built ($TOKEN_EFFICIENT)"
else
    check_fail "token-efficient not built"
    echo "     Run: cd $TOKEN_EFFICIENT && npm install && npm run build"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# Check context-graph MCP
# ─────────────────────────────────────────────────────────────────
echo "3. Checking context-graph MCP..."

if [ -d "$CONTEXT_GRAPH" ]; then
    check_pass "context-graph directory exists ($CONTEXT_GRAPH)"

    # Check Python dependencies
    if python3 -c "import chromadb" 2>/dev/null; then
        check_pass "chromadb installed"
    else
        check_fail "chromadb not installed"
        echo "     Run: pip install chromadb"
    fi
else
    check_fail "context-graph-mcp not found"
    echo "     Expected at: $CONTEXT_GRAPH"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# Check Voyage AI key
# ─────────────────────────────────────────────────────────────────
echo "4. Checking Voyage AI API key..."

VOYAGE_KEY_FOUND=false

if [ -n "$VOYAGE_API_KEY" ]; then
    check_pass "VOYAGE_API_KEY in environment"
    VOYAGE_KEY_FOUND=true
elif [ -f "$MCP_FILE" ]; then
    # Try to read from .mcp.json
    if jq -e '.mcpServers["context-graph"].env.VOYAGE_API_KEY' "$MCP_FILE" > /dev/null 2>&1; then
        check_pass "VOYAGE_API_KEY in .mcp.json"
        VOYAGE_KEY_FOUND=true
    fi
fi

if [ "$VOYAGE_KEY_FOUND" = false ]; then
    check_fail "VOYAGE_API_KEY not configured"
    echo "     Add to .mcp.json or set: export VOYAGE_API_KEY='your_key'"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# Check config syntax
# ─────────────────────────────────────────────────────────────────
echo "5. Checking .mcp.json syntax..."

if [ -f "$MCP_FILE" ]; then
    if jq empty "$MCP_FILE" > /dev/null 2>&1; then
        check_pass ".mcp.json is valid JSON"
    else
        check_fail ".mcp.json has syntax errors"
        echo "     Run: jq '.' $MCP_FILE"
    fi
else
    echo "  (skip - file not found)"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────
echo "=== Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✓ All checks passed!"
    echo ""
    echo "Restart Claude Code to load MCP servers."
    exit 0
else
    echo "✗ Some checks failed. Fix issues above."
    exit 1
fi
