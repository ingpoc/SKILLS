#!/bin/bash
# setup-global-hooks.sh
#
# Main setup script for global Claude Code hooks.
# Creates ~/.claude/hooks/ directory and installs 7 global hooks.

set -euo pipefail

# Paths
HOOKS_DIR="$HOME/.claude/hooks"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/../templates"

echo "Setting up global Claude Code hooks..."

# Create hooks directory
if [[ ! -d "$HOOKS_DIR" ]]; then
    echo "Creating $HOOKS_DIR"
    mkdir -p "$HOOKS_DIR"
else
    echo "Hooks directory exists: $HOOKS_DIR"
fi

# Run install script
"$SCRIPT_DIR/install-hooks.sh"

# Configure settings.json
echo ""
echo "Configuring settings.json..."
python3 "$SCRIPT_DIR/configure-settings.py"

# Verify installation
echo ""
echo "Verifying hook files..."
"$SCRIPT_DIR/verify-global-hooks.sh"

# Validate settings.json
echo ""
echo "Validating settings.json..."
python3 "$SCRIPT_DIR/validate-settings.py"

echo ""
echo "✅ Global hooks setup complete!"
echo ""
echo "Hooks installed in: $HOOKS_DIR"
echo "Settings configured in: ~/.claude/settings.json"
echo "Next: Set up project-specific hooks with project-hook-setup skill"
