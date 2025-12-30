#!/bin/bash
# Get current feature from state or find next pending
# Output: JSON with feature details

STATE_FILE=".claude/progress/state.json"
FEATURE_FILE=".claude/progress/feature-list.json"

# Check if we have a current feature in state
if [ -f "$STATE_FILE" ]; then
    FEATURE_ID=$(jq -r '.feature_id // empty' "$STATE_FILE")
    if [ -n "$FEATURE_ID" ] && [ "$FEATURE_ID" != "null" ]; then
        jq '.features[] | select(.id == "'$FEATURE_ID'")' "$FEATURE_FILE"
        exit 0
    fi
fi

# Otherwise get first pending feature
if [ -f "$FEATURE_FILE" ]; then
    jq '.features[] | select(.status == "pending") | first' "$FEATURE_FILE"
else
    echo '{"error": "No feature-list.json found"}'
    exit 1
fi
