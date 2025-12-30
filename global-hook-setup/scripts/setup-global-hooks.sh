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

# Verify installation
echo ""
echo "Verifying installation..."
"$SCRIPT_DIR/verify-global-hooks.sh"

echo ""
echo "✅ Global hooks setup complete!"
echo ""
echo "Hooks installed in: $HOOKS_DIR"
echo "Next: Set up project-specific hooks with project-hook-setup skill"
