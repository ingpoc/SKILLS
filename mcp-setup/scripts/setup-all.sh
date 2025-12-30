#!/bin/bash
# MCP Setup Script for agent-harness
# Sets up token-efficient and context-graph MCP servers
# Works for any user - auto-detects paths

set -e

echo "=== agent-harness MCP Setup ==="
echo ""

# ─────────────────────────────────────────────────────────────────
# Detect paths (works for any user)
# ─────────────────────────────────────────────────────────────────
# Script is at: .skills/mcp-setup/scripts/setup-all.sh
# Agent harness is 3 levels up (scripts/ → mcp-setup/ → .skills/ → agent-harness/)
AGENT_HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

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

# If not found, will clone to ~/token-efficient-mcp
if [ -z "$TOKEN_EFFICIENT" ]; then
    TOKEN_EFFICIENT="$HOME/token-efficient-mcp"
fi

echo "Agent harness: $AGENT_HARNESS"
echo "Token-efficient: $TOKEN_EFFICIENT"
echo ""

# ─────────────────────────────────────────────────────────────────
# Setup token-efficient MCP
# ─────────────────────────────────────────────────────────────────
echo "1. Setting up token-efficient MCP..."

if [ -d "$TOKEN_EFFICIENT" ] && [ -f "$TOKEN_EFFICIENT/dist/index.js" ]; then
    echo "   ✓ Already built, skipping..."
elif [ ! -d "$TOKEN_EFFICIENT" ]; then
    echo "   Cloning token-efficient-mcp..."
    git clone https://github.com/gurusharan/token-efficient-mcp.git "$TOKEN_EFFICIENT" 2>/dev/null || true
fi

if [ -d "$TOKEN_EFFICIENT" ]; then
    cd "$TOKEN_EFFICIENT"
    echo "   Installing dependencies..."
    npm install 2>/dev/null || echo "   Note: npm install had issues"
    echo "   Building..."
    npm run build 2>/dev/null || echo "   Note: Build had issues"
    cd - > /dev/null
    echo "   ✓ token-efficient MCP ready"
else
    echo "   ⚠ token-efficient MCP not found"
    echo "     Clone manually: git clone https://github.com/gurusharan/token-efficient-mcp.git ~/token-efficient-mcp"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# Setup context-graph MCP
# ─────────────────────────────────────────────────────────────────
echo "2. Setting up context-graph MCP..."

CONTEXT_GRAPH="$AGENT_HARNESS/context-graph-mcp"
if [ -d "$CONTEXT_GRAPH" ]; then
    echo "   Installing dependencies..."
    cd "$CONTEXT_GRAPH"
    if command -v uv &> /dev/null; then
        uv pip install -q -r requirements.txt 2>/dev/null || pip install -q -r requirements.txt 2>/dev/null
    else
        pip install -q -r requirements.txt 2>/dev/null || true
    fi
    cd - > /dev/null
    echo "   ✓ context-graph MCP ready"
else
    echo "   ✗ context-graph-mcp not found at $CONTEXT_GRAPH"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# Get Voyage AI key
# ─────────────────────────────────────────────────────────────────
echo "3. Voyage AI API Key"

if [ -z "$VOYAGE_API_KEY" ]; then
    read -sp "   Enter your Voyage AI API key (or press Enter to skip): " VOYAGE_KEY_INPUT
    echo ""
    if [ -n "$VOYAGE_KEY_INPUT" ]; then
        VOYAGE_API_KEY="$VOYAGE_KEY_INPUT"
        echo "   ✓ API key provided"
    else
        echo "   ⚠ No API key - you'll need to add it later"
    fi
else
    echo "   ✓ Found in environment"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# Generate .mcp.json (project-level)
# ─────────────────────────────────────────────────────────────────
echo "4. Creating .mcp.json..."

MCP_FILE="$AGENT_HARNESS/.mcp.json"

# Start building config
CONFIG_JSON="{
  \"mcpServers\": {
    \"token-efficient\": {
      \"command\": \"srt\",
      \"args\": [\"node\", \"$TOKEN_EFFICIENT/dist/index.js\"]
    }"

# Add context-graph if exists
if [ -d "$CONTEXT_GRAPH" ]; then
    CONFIG_JSON="$CONFIG_JSON,
    \"context-graph\": {
      \"command\": \"uv\",
      \"args\": [
        \"--directory\",
        \"$CONTEXT_GRAPH\",
        \"run\",
        \"python\",
        \"server.py\"
      ]"

    # Add API key if provided
    if [ -n "$VOYAGE_API_KEY" ]; then
        CONFIG_JSON="$CONFIG_JSON,
      \"env\": {
        \"VOYAGE_API_KEY\": \"$VOYAGE_API_KEY\"
      }"
    fi

    CONFIG_JSON="$CONFIG_JSON
    }"
fi

CONFIG_JSON="$CONFIG_JSON
  }
}"

# Write config
mkdir -p "$(dirname "$MCP_FILE")"
echo "$CONFIG_JSON" | jq '.' > "$MCP_FILE" 2>/dev/null || echo "$CONFIG_JSON" > "$MCP_FILE"

echo "   ✓ Created: $MCP_FILE"
echo ""

# ─────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────
echo "=== Setup Complete ==="
echo ""
echo "MCP servers configured in:"
echo "  $MCP_FILE"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code"
echo "  2. Tools should be available"
echo ""
