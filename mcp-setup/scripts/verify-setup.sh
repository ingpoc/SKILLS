#!/bin/bash
# Verify MCP servers are configured correctly for the current project
# Works in any project directory, checks project-local mcp/ folder

set -e

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
# Project root is current working directory
# ─────────────────────────────────────────────────────────────────
PROJECT_ROOT="$(pwd)"
MCP_DIR="$PROJECT_ROOT/mcp"
MCP_FILE="$PROJECT_ROOT/.mcp.json"

# ─────────────────────────────────────────────────────────────────
# 1. Check .mcp.json exists in project
# ─────────────────────────────────────────────────────────────────
echo "1. Checking project configuration..."

if [ -f "$MCP_FILE" ]; then
    check_pass ".mcp.json exists at $MCP_FILE"
else
    check_fail ".mcp.json not found in project"
    echo "     Run setup-all.sh to create it"
    echo ""
    echo "=== Summary ==="
    echo "Passed: $PASS"
    echo "Failed: $FAIL"
    echo ""
    echo "✗ Project .mcp.json not found. Run setup-all.sh to create it."
    exit 1
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# 2. Check .mcp.json has valid JSON
# ─────────────────────────────────────────────────────────────────
echo "2. Checking .mcp.json syntax..."

if jq empty "$MCP_FILE" 2>/dev/null; then
    check_pass ".mcp.json is valid JSON"
else
    check_fail ".mcp.json has syntax errors"
    echo "     Run: jq '.' $MCP_FILE"
    echo ""
    echo "=== Summary ==="
    echo "Passed: $PASS"
    echo "Failed: $FAIL"
    exit 1
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# 3. Check runtime dependencies
# ─────────────────────────────────────────────────────────────────
echo "3. Checking runtime dependencies..."

# Check srt (sandbox-runtime)
if command -v srt > /dev/null 2>&1; then
    check_pass "srt installed ($(command -v srt))"
else
    check_fail "srt not installed"
    echo "     Run: npm install -g @anthropic-ai/sandbox-runtime"
fi

# Check Node.js
if command -v node > /dev/null 2>&1; then
    NODE_VERSION=$(node -v)
    check_pass "node installed ($NODE_VERSION)"
else
    check_fail "node not installed"
    echo "     Run: brew install node (macOS) or visit nodejs.org"
fi

# Check Python
if command -v python3 > /dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    check_pass "python3 installed ($PYTHON_VERSION)"
else
    check_fail "python3 not installed"
    echo "     Run: brew install python3 (macOS)"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# 4. Check srt settings
# ─────────────────────────────────────────────────────────────────
echo "4. Checking srt configuration..."

SRT_SETTINGS="$HOME/.srt-settings.json"
if [ -f "$SRT_SETTINGS" ]; then
    check_pass "~/.srt-settings.json exists"
    if jq empty "$SRT_SETTINGS" 2>/dev/null; then
        check_pass "~/.srt-settings.json is valid JSON"
    else
        check_fail "~/.srt-settings.json has syntax errors"
    fi
else
    check_fail "~/.srt-settings.json not found"
    echo "     Create it or srt will use restrictive defaults"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# 5. Check token-efficient MCP server
# ─────────────────────────────────────────────────────────────────
echo "5. Checking token-efficient MCP..."

# Check if token-efficient is configured in .mcp.json
if jq -e '.mcpServers["token-efficient"]' "$MCP_FILE" > /dev/null 2>&1; then
    check_pass "token-efficient configured in .mcp.json"

    # Get the path from config
    TE_PATH=$(jq -r '.mcpServers["token-efficient"].args[]? // empty' "$MCP_FILE" 2>/dev/null | head -1)

    # Check if the MCP server file exists
    if [ -n "$TE_PATH" ] && [ -f "$TE_PATH" ]; then
        check_pass "token-efficient server file exists ($TE_PATH)"
    elif [ -n "$TE_PATH" ]; then
        check_fail "token-efficient server file not found: $TE_PATH"
        echo "     Run: cd mcp/token-efficient-mcp && npm install && npm run build"
    else
        check_fail "token-efficient path not configured correctly"
    fi
else
    check_fail "token-efficient not configured in .mcp.json"
    echo "     Run: setup-all.sh"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# 6. Check context-graph MCP server
# ─────────────────────────────────────────────────────────────────
echo "6. Checking context-graph MCP..."

# Check if context-graph is configured in .mcp.json
if jq -e '.mcpServers["context-graph"]' "$MCP_FILE" > /dev/null 2>&1; then
    check_pass "context-graph configured in .mcp.json"

    # Check Python dependencies
    if python3 -c "import chromadb" 2>/dev/null; then
        check_pass "chromadb installed"
    else
        check_fail "chromadb not installed"
        echo "     Run: pip install chromadb"
    fi

    # Check VOYAGE_API_KEY (in env or .mcp.json)
    VOYAGE_KEY_FOUND=false

    if [ -n "$VOYAGE_API_KEY" ]; then
        check_pass "VOYAGE_API_KEY in environment"
        VOYAGE_KEY_FOUND=true
    elif jq -e '.mcpServers["context-graph"].env.VOYAGE_API_KEY' "$MCP_FILE" > /dev/null 2>&1; then
        check_pass "VOYAGE_API_KEY in .mcp.json"
        VOYAGE_KEY_FOUND=true
    fi

    if [ "$VOYAGE_KEY_FOUND" = false ]; then
        check_fail "VOYAGE_API_KEY not configured"
        echo "     Add to .mcp.json or set: export VOYAGE_API_KEY='your_key'"
    fi
else
    check_fail "context-graph not configured in .mcp.json"
    echo "     Run: setup-all.sh"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# 7. Check mcp/ folder exists
# ─────────────────────────────────────────────────────────────────
echo "7. Checking mcp/ folder..."

if [ -d "$MCP_DIR" ]; then
    check_pass "mcp/ folder exists"

    # Check for token-efficient-mcp
    if [ -d "$MCP_DIR/token-efficient-mcp" ]; then
        check_pass "token-efficient-mcp exists in mcp/"
    else
        check_fail "token-efficient-mcp not found in mcp/"
    fi

    # Check for context-graph-mcp
    if [ -d "$MCP_DIR/context-graph-mcp" ]; then
        check_pass "context-graph-mcp exists in mcp/"
    else
        check_fail "context-graph-mcp not found in mcp/"
    fi
else
    check_fail "mcp/ folder not found"
    echo "     Run: setup-all.sh"
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
