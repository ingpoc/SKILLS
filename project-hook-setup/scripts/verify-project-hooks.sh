#!/bin/bash
# verify-project-hooks.sh
#
# Verification script for project hooks.
# Checks config exists, hooks are installed, config has required fields.

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-.}"
HOOKS_DIR="$PROJECT_ROOT/.claude/hooks"
CONFIG_FILE="$PROJECT_ROOT/.claude/config/project.json"

# Expected hooks
EXPECTED_HOOKS=(
    "verify-tests.py"
    "verify-files-exist.py"
    "verify-health.py"
    "require-dependencies.py"
    "session-entry.sh"
)

MISSING=0
NOT_EXECUTABLE=0
CONFIG_MISSING=0

echo "Verifying project hooks in $PROJECT_ROOT"
echo ""

# Check config
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ MISSING: .claude/config/project.json"
    ((CONFIG_MISSING++))
else
    echo "✅ Config exists: project.json"

    # Check required fields
    for field in "project_type" "health_check" "test_command"; do
        if jq -e ".$field" "$CONFIG_FILE" >/dev/null 2>&1; then
            VALUE=$(jq -r ".$field" "$CONFIG_FILE")
            echo "  ✓ $field: $VALUE"
        else
            echo "  ✗ Missing field: $field"
            ((CONFIG_MISSING++))
        fi
    done
fi

echo ""

# Check hooks
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

if [[ $CONFIG_MISSING -gt 0 ]]; then
    echo "Verification failed: Config incomplete"
    echo "Run: .skills/project-hook-setup/scripts/setup-project-hooks.sh"
    exit 1
fi

if [[ $MISSING -gt 0 ]]; then
    echo "Verification failed: $MISSING hook(s) missing"
    echo "Run: .skills/project-hook-setup/scripts/setup-project-hooks.sh"
    exit 1
fi

if [[ $NOT_EXECUTABLE -gt 0 ]]; then
    echo "Warning: $NOT_EXECUTABLE hook(s) not executable"
    echo "Run: chmod +x $HOOKS_DIR/*"
    exit 1
fi

echo "✅ All project hooks verified!"
exit 0
