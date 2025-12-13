#!/bin/bash
# PostToolUse hook: Verify coding-agent updated progress files
# Triggered after Task tool completes with coding-agent
#
# This hook only activates when .claude/progress/ exists in the project

PROGRESS_DIR=".claude/progress"
FEATURE_FILE="$PROGRESS_DIR/feature-list.json"

# Only run if progress files exist
if [ ! -f "$FEATURE_FILE" ]; then
    exit 0
fi

# Check if feature-list.json was modified in last 5 minutes
MODIFIED_TIME=$(stat -f %m "$FEATURE_FILE" 2>/dev/null || stat -c %Y "$FEATURE_FILE" 2>/dev/null)
CURRENT_TIME=$(date +%s)
DIFF=$((CURRENT_TIME - MODIFIED_TIME))

if [ "$DIFF" -gt 300 ]; then
    echo "⚠️ VERIFICATION WARNING: feature-list.json not updated in last 5 minutes"
    echo "Coding-agent may have failed to update progress."
    echo ""
    echo "ACTION REQUIRED: Read .claude/progress/feature-list.json and verify/fix manually"
fi

# Validate JSON structure
if ! python3 -c "import json; json.load(open('$FEATURE_FILE'))" 2>/dev/null; then
    echo "⚠️ VERIFICATION FAILED: feature-list.json has invalid JSON"
    exit 1
fi

exit 0
