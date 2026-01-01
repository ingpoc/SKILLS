#!/bin/bash
# verify-global-hooks.sh
#
# Verification script for global hooks.
# Checks all 8 hooks exist and are executable.

set -euo pipefail

HOOKS_DIR="$HOME/.claude/hooks"

# Expected hooks
EXPECTED_HOOKS=(
    "verify-state-transition.py"
    "require-commit-before-tested.py"
    "require-outcome-update.py"
    "link-feature-to-trace.py"
    "markdownlint-fix.sh"
    "remind-decision-trace.sh"
    "session-end.sh"
    "feature-commit.sh"
)

MISSING=0
NOT_EXECUTABLE=0

echo "Verifying global hooks in $HOOKS_DIR"
echo ""

for hook in "${EXPECTED_HOOKS[@]}"; do
    hook_path="$HOOKS_DIR/$hook"

    if [[ ! -f "$hook_path" ]]; then
        echo "❌ MISSING: $hook"
        ((MISSING++))
    elif [[ ! -x "$hook_path" ]]; then
        echo "⚠️  NOT EXECUTABLE: $hook"
        ((NOT_EXECUTABLE++))
    else
        echo "✅ $hook"
    fi
done

echo ""

if [[ $MISSING -gt 0 ]]; then
    echo "Verification failed: $MISSING hook(s) missing"
    echo "Run: ~/.claude/skills/global-hook-setup/scripts/setup-global-hooks.sh"
    exit 1
fi

if [[ $NOT_EXECUTABLE -gt 0 ]]; then
    echo "Warning: $NOT_EXECUTABLE hook(s) not executable"
    echo "Run: chmod +x $HOOKS_DIR/*"
    exit 1
fi

echo "✅ All global hooks verified!"
exit 0
