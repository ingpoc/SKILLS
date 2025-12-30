#!/bin/bash
# install-hooks.sh
#
# Copies hook templates from templates/ to ~/.claude/hooks/
# and sets executable permissions.

set -euo pipefail

HOOKS_DIR="$HOME/.claude/hooks"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/../templates"

# Ensure hooks directory exists
mkdir -p "$HOOKS_DIR"

# Copy all templates
echo "Installing hooks from $TEMPLATES_DIR to $HOOKS_DIR"

for template in "$TEMPLATES_DIR"/*; do
    if [[ -f "$template" ]]; then
        hook_name=$(basename "$template")
        target="$HOOKS_DIR/$hook_name"

        # Copy file
        cp "$template" "$target"

        # Set executable
        chmod +x "$target"

        echo "  ✓ $hook_name"
    fi
done

echo "Installation complete"
