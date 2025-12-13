#!/bin/bash
# Post-Tool Guard: Reminds about progress updates after implementation changes
#
# Exit codes: 0 = success (can output warnings)
#
# This hook only activates when .claude/progress/ exists in the project

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // empty')

FILE_PATH=""
if [ "$TOOL_NAME" = "Edit" ] || [ "$TOOL_NAME" = "Write" ]; then
    FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty')
fi

# ============================================================
# REMINDER: Update progress after implementation file changes
# ============================================================
if [ "$TOOL_NAME" = "Edit" ] || [ "$TOOL_NAME" = "Write" ]; then
    # Check if editing source files
    if echo "$FILE_PATH" | grep -qE '^.*(src/|lib/|app/|components/|pages/).*\.(ts|tsx|js|jsx|py|rb|go|rs)$'; then
        # Check if progress files exist
        if [ -f ".claude/progress/feature-list.json" ]; then
            # Check last modification time of progress files
            FEATURE_MOD=$(stat -f %m ".claude/progress/feature-list.json" 2>/dev/null || stat -c %Y ".claude/progress/feature-list.json" 2>/dev/null)
            CURRENT=$(date +%s)
            DIFF=$((CURRENT - FEATURE_MOD))

            # If progress file not updated in last 10 minutes, remind
            if [ "$DIFF" -gt 600 ]; then
                echo ""
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                echo "📝 REMINDER: Update progress files after code changes"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                echo "Files to update:"
                echo "  - .claude/progress/session-state.json (update last_action)"
                echo "  - .claude/progress/feature-list.json (update status)"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            fi
        fi
    fi
fi

exit 0
