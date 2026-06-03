#!/bin/bash
# Global Hook: remind-decision-trace.sh
#
# Non-blocking reminder to store decision traces after implementation.
# Triggers when feature is marked implemented but no recent trace found.

set -euo pipefail

# Read stdin
INPUT=$(cat)

# Parse content
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')

# Only check when marking implemented:true
if [[ ! "$CONTENT" =~ "implemented":true ]] && [[ ! "$CONTENT" =~ "implemented":true ]]; then
    exit 0
fi

# Check if we should remind (simple heuristic)
# In full implementation, would check context-graph for recent traces

# Get current time and last modification time
NOW=$(date +%s)
FEATURE_FILE=".claude/progress/feature-list.json"

if [[ -f "$FEATURE_FILE" ]]; then
    LAST_MOD=$(stat -f %m "$FEATURE_FILE" 2>/dev/null || stat -c %Y "$FEATURE_FILE" 2>/dev/null)
    DIFF=$((NOW - LAST_MOD))

    # If modified in last 10 minutes, check for traces
    if [[ $DIFF -lt 600 ]]; then
        # Would check context-graph here
        # For now, just emit reminder if this looks like a completed implementation
        if [[ "$CONTENT" =~ "status" ]] && [[ "$CONTENT" =~ "implemented" ]]; then
            echo "REMINDER: Consider storing decision trace for this feature" >&2
            echo "Use: context_store_trace(decision='...', category='framework|api|...')" >&2
            # Exit 0 - reminder only, don't block
        fi
    fi
fi

exit 0
