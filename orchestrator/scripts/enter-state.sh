#!/bin/bash
# Transition to new state
# Usage: enter-state.sh NEW_STATE [FEATURE_ID]

NEW_STATE=$1
FEATURE_ID=$2
STATE_FILE=".claude/progress/state.json"

mkdir -p .claude/progress

# Get current state for history
CURRENT=""
if [ -f "$STATE_FILE" ]; then
    CURRENT=$(cat "$STATE_FILE")
fi

# Build new state
case "$NEW_STATE" in
    "INIT")
        echo '{
  "state": "INIT",
  "entered_at": "'$(date -Iseconds)'"
}' > "$STATE_FILE"
        ;;
    "IMPLEMENT")
        if [ -z "$FEATURE_ID" ]; then
            # Get first pending feature
            FEATURE_ID=$(jq -r '.features[] | select(.status=="pending") | .id' .claude/progress/feature-list.json 2>/dev/null | head -1)
        fi
        echo '{
  "state": "IMPLEMENT",
  "feature_id": "'$FEATURE_ID'",
  "entered_at": "'$(date -Iseconds)'",
  "attempts": 1
}' > "$STATE_FILE"
        ;;
    "TEST")
        # Preserve feature_id from current state
        FEATURE_ID=$(echo "$CURRENT" | jq -r '.feature_id // empty')
        ATTEMPTS=$(echo "$CURRENT" | jq -r '.attempts // 1')
        echo '{
  "state": "TEST",
  "feature_id": "'$FEATURE_ID'",
  "entered_at": "'$(date -Iseconds)'",
  "attempts": '$ATTEMPTS'
}' > "$STATE_FILE"
        ;;
    "COMPLETE")
        echo '{
  "state": "COMPLETE",
  "entered_at": "'$(date -Iseconds)'"
}' > "$STATE_FILE"
        ;;
esac

cat "$STATE_FILE"
