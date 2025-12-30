#!/bin/bash
# setup-project-hooks.sh
#
# Main setup script for project-specific Claude Code hooks.
# Prompts for config, creates .claude/config/project.json, installs hooks.
#
# Usage:
#   setup-project-hooks.sh                    # Interactive mode
#   setup-project-hooks.sh --non-interactive  # Skip all prompts
#   setup-project-hooks.sh --yes              # Auto-confirm all prompts
#   setup-project-hooks.sh --config <path>    # Use existing config
#
# Environment:
#   CLAUDE_NON_INTERACTIVE=1                  # Skip prompts (agent mode)

set -euo pipefail

# Default values
NON_INTERACTIVE="${CLAUDE_NON_INTERACTIVE:-0}"
AUTO_YES=0
CONFIG_PATH=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --non-interactive|-n)
            NON_INTERACTIVE=1
            shift
            ;;
        --yes|-y)
            AUTO_YES=1
            shift
            ;;
        --config|-c)
            CONFIG_PATH="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--non-interactive] [--yes] [--config <path>]"
            echo "  --non-interactive  Skip all prompts (agent mode)"
            echo "  --yes              Auto-confirm all prompts"
            echo "  --config <path>    Use existing config file"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Paths
PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-.}"
HOOKS_DIR="$PROJECT_ROOT/.claude/hooks"
CONFIG_DIR="$PROJECT_ROOT/.claude/config"
CONFIG_FILE="$CONFIG_DIR/project.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Setting up project-specific Claude Code hooks..."
echo ""

# Create directories
mkdir -p "$HOOKS_DIR"
mkdir -p "$CONFIG_DIR"

# Use provided config path if specified
if [[ -n "$CONFIG_PATH" ]]; then
    if [[ ! -f "$CONFIG_PATH" ]]; then
        echo "Error: Config file not found: $CONFIG_PATH" >&2
        exit 1
    fi
    echo "Using provided config: $CONFIG_PATH"
    cp "$CONFIG_PATH" "$CONFIG_FILE"
else
    # Create or update config
    if [[ -f "$CONFIG_FILE" ]]; then
        echo "Found existing config: $CONFIG_FILE"
        if [[ "$NON_INTERACTIVE" -eq 1 ]] || [[ "$AUTO_YES" -eq 1 ]]; then
            echo "Non-interactive mode: Keeping existing config"
        else
            echo "Current config:"
            cat "$CONFIG_FILE"
            echo ""
            read -p "Update config? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Keeping existing config"
            else
                "$SCRIPT_DIR/prompt-project-config.sh"
            fi
        fi
    else
        echo "Creating new project config..."
        "$SCRIPT_DIR/prompt-project-config.sh"
    fi
fi

# Install hooks
echo ""
echo "Installing project hooks..."
"$SCRIPT_DIR/install-hooks.sh"

# Verify
echo ""
echo "Verifying installation..."
"$SCRIPT_DIR/verify-project-hooks.sh"

echo ""
echo "✅ Project hooks setup complete!"
echo ""
echo "Config: $CONFIG_FILE"
echo "Hooks: $HOOKS_DIR"

