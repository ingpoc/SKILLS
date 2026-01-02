#!/bin/bash
# MCP Setup Script for agent-harness projects
# Sets up token-efficient and context-graph MCP servers in project's .mcp/ folder
# Works for any project - creates .mcp/ in current directory
#
# Usage:
#   setup-all.sh                    # Interactive mode
#   setup-all.sh --non-interactive  # Skip all prompts (agent mode)
#
# Environment:
#   CLAUDE_NON_INTERACTIVE=1        # Skip prompts (agent mode)
#   VOYAGE_API_KEY=...              # Pre-set API key

set -e

# Default values
NON_INTERACTIVE="${CLAUDE_NON_INTERACTIVE:-0}"

# Auto-detect non-interactive mode
auto_detect_non_interactive() {
    # If no TTY (running in automation/agent)
    if [ ! -t 0 ]; then
        NON_INTERACTIVE=1
    fi
}

auto_detect_non_interactive

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --non-interactive|-n)
            NON_INTERACTIVE=1
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--non-interactive]"
            echo "  --non-interactive  Skip all prompts (agent mode)"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

echo "=== Project MCP Setup ==="
echo ""

# ─────────────────────────────────────────────────────────────────
# Project root is current working directory
# ─────────────────────────────────────────────────────────────────
PROJECT_ROOT="$(pwd)"
MCP_DIR="$PROJECT_ROOT/mcp"
MCP_FILE="$PROJECT_ROOT/.mcp.json"

echo "Project: $PROJECT_ROOT"
echo "MCP folder: $MCP_DIR"
echo ""

# ─────────────────────────────────────────────────────────────────
# 0. Install/check runtime dependencies
# ─────────────────────────────────────────────────────────────────
echo "0. Checking runtime dependencies..."

# Check and install srt if needed
if ! command -v srt > /dev/null 2>&1; then
    echo "   Installing srt (sandbox-runtime)..."
    npm install -g @anthropic-ai/sandbox-runtime 2>/dev/null || {
        echo "   ✗ Failed to install srt"
        echo "   Run manually: npm install -g @anthropic-ai/sandbox-runtime"
        exit 1
    }
    echo "   ✓ srt installed"
else
    echo "   ✓ srt already installed ($(command -v srt))"
fi

# Check node
if ! command -v node > /dev/null 2>&1; then
    echo "   ✗ node not found - please install Node.js"
    echo "   Run: brew install node (macOS) or visit nodejs.org"
    exit 1
fi
echo "   ✓ node available ($(node -v))"

# Check python3
if ! command -v python3 > /dev/null 2>&1; then
    echo "   ✗ python3 not found - please install Python 3"
    echo "   Run: brew install python3 (macOS)"
    exit 1
fi
echo "   ✓ python3 available ($(python3 --version))"

# Check jq
if ! command -v jq > /dev/null 2>&1; then
    echo "   ✗ jq not found - please install jq"
    echo "   Run: brew install jq (macOS)"
    exit 1
fi
echo "   ✓ jq available"

echo ""

# ─────────────────────────────────────────────────────────────────
# Create srt settings if not exists
# ─────────────────────────────────────────────────────────────────
SRT_SETTINGS="$HOME/.srt-settings.json"
if [ ! -f "$SRT_SETTINGS" ]; then
    echo "Creating ~/.srt-settings.json with default configuration..."
    cat > "$SRT_SETTINGS" << EOF
{
  "filesystem": {
    "allowRead": [
      "/tmp",
      "/var/folders",
      "$PROJECT_ROOT",
      "/usr/local/bin",
      "/usr/bin"
    ],
    "allowWrite": ["/tmp", "/var/folders", "/tmp/claude", "/var/tmp"],
    "denyRead": ["~/.ssh", "~/.aws", "~/.gnupg", "/etc/shadow"],
    "denyWrite": ["~/.ssh", "~/.aws", "~/.gnupg", "/etc", "~/.env"]
  },
  "network": {
    "allowedDomains": ["localhost", "127.0.0.1", "0.0.0.0", "api.anthropic.com"],
    "deniedDomains": [],
    "allowLocalBinding": true
  },
  "execution": {
    "timeoutMs": 60000,
    "maxMemoryMB": 1024,
    "maxProcesses": 5
  }
}
EOF
    echo "   ✓ Created ~/.srt-settings.json"
    echo "   ⚠ Review and customize for your environment"
else
    echo "   ✓ ~/.srt-settings.json already exists"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# 1. Setup token-efficient MCP
# ─────────────────────────────────────────────────────────────────
echo "1. Setting up token-efficient MCP..."

TOKEN_EFFICIENT_MCP="$MCP_DIR/token-efficient-mcp"

# Clone if not exists
if [ ! -d "$TOKEN_EFFICIENT_MCP" ]; then
    echo "   Cloning to $TOKEN_EFFICIENT_MCP..."
    mkdir -p "$MCP_DIR"
    git clone https://github.com/ingpoc/token-efficient-mcp.git "$TOKEN_EFFICIENT_MCP" 2>/dev/null || {
        echo "   ✗ Failed to clone token-efficient-mcp"
        exit 1
    }
fi

# Build
if [ -f "$TOKEN_EFFICIENT_MCP/dist/index.js" ]; then
    echo "   ✓ Already built"
else
    echo "   Installing dependencies..."
    cd "$TOKEN_EFFICIENT_MCP"
    npm install 2>/dev/null || echo "   ⚠ npm install had issues"
    echo "   Building..."
    npm run build 2>/dev/null || {
        echo "   ✗ Build failed"
        cd - > /dev/null
        exit 1
    }
    cd - > /dev/null
    echo "   ✓ token-efficient MCP ready"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# 2. Setup context-graph MCP
# ─────────────────────────────────────────────────────────────────
echo "2. Setting up context-graph MCP..."

CONTEXT_GRAPH_MCP="$MCP_DIR/context-graph-mcp"

# Clone if not exists
if [ ! -d "$CONTEXT_GRAPH_MCP" ]; then
    echo "   Cloning to $CONTEXT_GRAPH_MCP..."
    mkdir -p "$MCP_DIR"
    git clone https://github.com/ingpoc/context-graph-mcp.git "$CONTEXT_GRAPH_MCP" 2>/dev/null || {
        echo "   ✗ Failed to clone context-graph-mcp"
        exit 1
    }
fi

# Install dependencies
if [ -f "$CONTEXT_GRAPH_MCP/requirements.txt" ]; then
    # No subdirectory
    CONTEXT_GRAPH_SERVER="$CONTEXT_GRAPH_MCP"
elif [ -f "$CONTEXT_GRAPH_MCP/context-graph-mcp/requirements.txt" ]; then
    # Nested context-graph-mcp directory
    CONTEXT_GRAPH_SERVER="$CONTEXT_GRAPH_MCP/context-graph-mcp"
else
    CONTEXT_GRAPH_SERVER="$CONTEXT_GRAPH_MCP"
fi

echo "   Installing Python dependencies..."
if command -v uv &> /dev/null; then
    uv pip install -q -r "$CONTEXT_GRAPH_SERVER/requirements.txt" 2>/dev/null || pip install -q -r "$CONTEXT_GRAPH_SERVER/requirements.txt" 2>/dev/null
else
    pip install -q -r "$CONTEXT_GRAPH_SERVER/requirements.txt" 2>/dev/null || true
fi

echo "   ✓ context-graph MCP ready"

echo ""

# ─────────────────────────────────────────────────────────────────
# 3. Get Voyage AI API Key
# ─────────────────────────────────────────────────────────────────
echo "3. Voyage AI API Key"

VOYAGE_KEY=""

if [ -n "$VOYAGE_API_KEY" ]; then
    echo "   ✓ Found in environment"
    VOYAGE_KEY="$VOYAGE_API_KEY"
elif [ "$NON_INTERACTIVE" -eq 1 ]; then
    echo "   ⚠ Non-interactive mode: No API key provided"
    echo "   Set VOYAGE_API_KEY env var or update .mcp.json later"
    VOYAGE_KEY=""
else
    read -sp "   Enter your Voyage AI API key (or press Enter to skip): " VOYAGE_KEY_INPUT
    echo ""
    if [ -n "$VOYAGE_KEY_INPUT" ]; then
        VOYAGE_KEY="$VOYAGE_KEY_INPUT"
        echo "   ✓ API key provided"
    else
        echo "   ⚠ No API key - context-graph will have limited functionality"
    fi
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# 4. Generate .mcp.json
# ─────────────────────────────────────────────────────────────────
echo "4. Creating .mcp.json..."

# Start building config
CONFIG_JSON="{
  \"mcpServers\": {
    \"token-efficient\": {
      \"command\": \"srt\",
      \"args\": [\"node\", \"$TOKEN_EFFICIENT_MCP/dist/index.js\"]
    }"

# Add context-graph if server.py exists
if [ -f "$CONTEXT_GRAPH_SERVER/server.py" ]; then
    CONFIG_JSON="$CONFIG_JSON,
    \"context-graph\": {
      \"command\": \"uv\",
      \"args\": [
        \"--directory\",
        \"$CONTEXT_GRAPH_SERVER\",
        \"run\",
        \"python\",
        \"server.py\"
      ]"

    # Add env with API key (use env var reference if not provided directly)
    if [ -n "$VOYAGE_KEY" ]; then
        CONFIG_JSON="$CONFIG_JSON,
      \"env\": {
        \"VOYAGE_API_KEY\": \"$VOYAGE_KEY\"
      }"
    else
        CONFIG_JSON="$CONFIG_JSON,
      \"env\": {
        \"VOYAGE_API_KEY\": \"\${VOYAGE_API_KEY}\"
      }"
    fi

    CONFIG_JSON="$CONFIG_JSON
    }"
fi

CONFIG_JSON="$CONFIG_JSON
  }
}"

# Write config
echo "$CONFIG_JSON" | jq '.' > "$MCP_FILE" 2>/dev/null || echo "$CONFIG_JSON" > "$MCP_FILE"

echo "   ✓ Created: $MCP_FILE"
echo ""

# ─────────────────────────────────────────────────────────────────
# 5. Verify setup
# ─────────────────────────────────────────────────────────────────
echo "5. Verifying setup..."

# Run verify-setup.sh if exists
VERIFY_SCRIPT="$(dirname "${BASH_SOURCE[0]}")/verify-setup.sh"
if [ -f "$VERIFY_SCRIPT" ]; then
    bash "$VERIFY_SCRIPT"
else
    echo "   ⚠ verify-setup.sh not found, skipping verification"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "MCP servers installed in:"
echo "  $MCP_DIR/"
echo ""
echo "Config file:"
echo "  $MCP_FILE"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code"
echo "  2. MCP tools should be available"
echo ""
