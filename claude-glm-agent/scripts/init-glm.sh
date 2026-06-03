#!/bin/bash
# Initialize project for GLM configuration: copy configure-glm.sh to .claude/scripts/
# Usage: ~/.claude/skills/claude-glm-agent/scripts/init-glm.sh

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
SCRIPTS_DIR="$PROJECT_DIR/.claude/scripts"

echo "=== GLM Configuration Initialization ==="
echo ""

# 1. Create scripts directory if needed
echo "1. Creating .claude/scripts/ directory..."
mkdir -p "$SCRIPTS_DIR"
echo "✓ Created: $SCRIPTS_DIR"
echo ""

# 2. Detect project type
echo "2. Detecting project type..."
PROJECT_TYPE=""
ENV_PREFIX=""

if [ -f "package.json" ]; then
    # Check for Next.js
    if grep -q '"next"' package.json 2>/dev/null; then
        PROJECT_TYPE="nextjs"
        ENV_PREFIX="NEXT_PUBLIC_"
        echo "✓ Detected: Next.js (frontend)"
    # Check for Vite
    elif grep -q '"vite"' package.json 2>/dev/null; then
        PROJECT_TYPE="vite"
        ENV_PREFIX="VITE_"
        echo "✓ Detected: Vite (frontend)"
    # Check for React
    elif grep -q '"react"' package.json 2>/dev/null; then
        PROJECT_TYPE="node"
        ENV_PREFIX=""
        echo "✓ Detected: Node.js"
    else
        PROJECT_TYPE="node"
        ENV_PREFIX=""
        echo "✓ Detected: Node.js"
    fi
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    PROJECT_TYPE="python"
    ENV_PREFIX=""
    echo "✓ Detected: Python"
elif [ -f "go.mod" ]; then
    PROJECT_TYPE="go"
    ENV_PREFIX=""
    echo "✓ Detected: Go"
elif [ -f "Cargo.toml" ]; then
    PROJECT_TYPE="rust"
    ENV_PREFIX=""
    echo "✓ Detected: Rust"
else
    echo "⚠️  Could not auto-detect project type"
    PROJECT_TYPE="unknown"
fi
echo ""

# 3. Copy template script
echo "3. Copying configure-glm.sh template to project..."
TEMPLATE="$SKILL_DIR/scripts/configure-glm.sh"
TARGET="$SCRIPTS_DIR/configure-glm.sh"

if [ -f "$TEMPLATE" ]; then
    cp "$TEMPLATE" "$TARGET"
    chmod +x "$TARGET"
    echo "✓ Copied to: $TARGET"
else
    echo "❌ Template not found: $TEMPLATE"
    exit 1
fi
echo ""

# 4. Tailor the script with detected values
echo "4. Tailoring script for this project..."
sed -i.bak "s|PROJECT_TYPE=\"\"|PROJECT_TYPE=\"$PROJECT_TYPE\"|" "$TARGET"
sed -i.bak "s|ENV_PREFIX=\"\"|ENV_PREFIX=\"$ENV_PREFIX\"|" "$TARGET"
rm -f "$TARGET.bak"
echo "✓ Configured with detected values"
echo ""

# 5. Instructions
echo "=== Initialization Complete ==="
echo ""
echo "Next steps:"
echo "  1. Run: ./$TARGET"
echo "  2. Enter your z.ai token when prompted"
echo "  3. Verify .env files were created correctly"
echo ""
echo "To test the proxy connection:"
echo "  ~/.claude/skills/claude-glm-agent/scripts/test-proxy.sh"
echo ""
echo "Configuration:"
echo "  Project Type: $PROJECT_TYPE"
echo "  Env Prefix:  ${ENV_PREFIX:-<none>}"
