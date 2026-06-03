#!/bin/bash
# Clone and build token-efficient MCP server

set -e

INSTALL_DIR="${1:-$HOME/token-efficient-mcp}"

echo "=== Installing token-efficient MCP ==="
echo "Target: $INSTALL_DIR"
echo ""

# Clone if not exists
if [ -d "$INSTALL_DIR" ]; then
    echo "Directory exists, pulling latest..."
    cd "$INSTALL_DIR"
    git pull
else
    echo "Cloning repository..."
    git clone https://github.com/gurusharan/token-efficient-mcp.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""
echo "Installing dependencies..."
npm install

echo ""
echo "Building..."
npm run build

echo ""
echo "✓ token-efficient MCP installed!"
echo ""
echo "Built file: $INSTALL_DIR/dist/index.js"
echo ""
echo "Use scripts/setup-all.sh to configure in .mcp.json"
