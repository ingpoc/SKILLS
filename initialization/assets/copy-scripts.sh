#!/bin/bash
# Copy project automation scripts from initialization skill templates
# Usage: copy-scripts.sh [project-dir]
# Copies: All script templates with TEMPLATE- prefix to project .claude/scripts/
#
# Scripts are copied as TEMPLATE-*.sh to signal they need customization.
# After customizing for your project, rename to remove TEMPLATE- prefix.

set -e

PROJECT_DIR="${1:-$PWD}"
cd "$PROJECT_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../templates"

echo "=== Copying automation scripts to .claude/scripts/ ==="

# ─────────────────────────────────────────────────────────────────
# Create .claude/scripts/ directory
# ─────────────────────────────────────────────────────────────────
mkdir -p .claude/scripts

# ─────────────────────────────────────────────────────────────────
# Copy scripts from templates with TEMPLATE- prefix
# ─────────────────────────────────────────────────────────────────
SCRIPTS_COPIED=0

# Script templates to copy
SCRIPT_TEMPLATES=(
    "get-current-feature.sh"
    "health-check.sh"
    "run-tests.sh"
    "restart-servers.sh"
    "feature-commit.sh"
    "mark-feature-complete.sh"
    "check-state.sh"
    "validate-transition.sh"
    "transition-state.sh"
    "check-context.sh"
)

for script in "${SCRIPT_TEMPLATES[@]}"; do
    src="$TEMPLATE_DIR/$script"
    # Add TEMPLATE- prefix to destination filename
    dst=".claude/scripts/TEMPLATE-$script"
    final_dst=".claude/scripts/$script"

    if [ -f "$src" ]; then
        # Check if either TEMPLATE- version or customized version exists
        if [ -f "$dst" ]; then
            echo "Exists: .claude/scripts/TEMPLATE-$script (skipped)"
        elif [ -f "$final_dst" ]; then
            echo "Customized: .claude/scripts/$script (skipped)"
        else
            cp "$src" "$dst"
            chmod +x "$dst"
            echo "Created: .claude/scripts/TEMPLATE-$script"
            SCRIPTS_COPIED=$((SCRIPTS_COPIED + 1))
        fi
    else
        echo "Warning: Template not found: $src"
    fi
done

# ─────────────────────────────────────────────────────────────────
# Copy testing-tracker scripts (needed by testing workflow)
# ─────────────────────────────────────────────────────────────────
TESTING_TRACKER_DIR="$HOME/.claude/skills/testing-tracker/scripts"
TESTING_SCRIPTS=(
    "mark-tested.py"
    "mark-in-progress.py"
    "initialize-testing-list.sh"
    "show-testing-status.sh"
    "get-next-to-test.sh"
    "start-next-test.sh"
)

for script in "${TESTING_SCRIPTS[@]}"; do
    src="$TESTING_TRACKER_DIR/$script"
    dst=".claude/scripts/$script"
    
    if [ -f "$src" ] && [ ! -f "$dst" ]; then
        cp "$src" "$dst"
        chmod +x "$dst"
        echo "Created: .claude/scripts/$script (from testing-tracker)"
        SCRIPTS_COPIED=$((SCRIPTS_COPIED + 1))
    fi
done

# ─────────────────────────────────────────────────────────────────
# Copy README
# ─────────────────────────────────────────────────────────────────
README_SRC="$TEMPLATE_DIR/SCRIPTS_README.md"
README_DST=".claude/scripts/README.md"

if [ -f "$README_SRC" ]; then
    if [ ! -f "$README_DST" ]; then
        cp "$README_SRC" "$README_DST"
        echo "Created: .claude/scripts/README.md"
        SCRIPTS_COPIED=$((SCRIPTS_COPIED + 1))
    else
        echo "Exists: .claude/scripts/README.md (skipped, preserving customization)"
    fi
fi

# ─────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────
echo ""
if [ $SCRIPTS_COPIED -gt 0 ]; then
    echo "=== Scripts copied: $SCRIPTS_COPIED ==="
    echo ""
    echo "⚠️  IMPORTANT: Scripts are copied with TEMPLATE- prefix"
    echo ""
    echo "Before using a script, you MUST:"
    echo "  1. Review and customize it for your project"
    echo "  2. Rename: TEMPLATE-script.sh → script.sh"
    echo "  3. Commit the customized script"
    echo ""
    echo "Example:"
    echo "  mv .claude/scripts/TEMPLATE-health-check.sh .claude/scripts/health-check.sh"
    echo ""
    echo "See .claude/scripts/README.md for script documentation"
else
    echo "=== All scripts already exist (no changes) ==="
fi
