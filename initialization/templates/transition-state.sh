#!/bin/bash
# Execute state transition with validation
# Usage: ./transition-state.sh TO_STATE [REASON]
# Responsibility: State machine update (ORCHESTRATOR)

set -e

TO="${1:-}"
REASON="${2:-State transition}"
STATE_FILE=".claude/progress/state.json"

if [ -z "$TO" ]; then
    echo "Usage: $0 TO_STATE [REASON]"
    exit 1
fi

# Validate state name
VALID_STATES=("START" "INIT" "IMPLEMENT" "TEST" "COMPLETE")
if [[ ! " ${VALID_STATES[@]} " =~ " ${TO} " ]]; then
    echo "Error: Invalid state '$TO'. Valid states: ${VALID_STATES[*]}" >&2
    exit 1
fi

mkdir -p .claude/progress

# Get current state
if [ -f "$STATE_FILE" ]; then
    FROM=$(jq -r '.state // "START"' "$STATE_FILE")
    CURRENT_HEALTH=$(jq -r '.health_status // "HEALTHY"' "$STATE_FILE")
    CURRENT_FEATURE=$(jq -r '.feature_id // ""' "$STATE_FILE")
    CURRENT_ATTEMPTS=$(jq -r '.attempts // 1' "$STATE_FILE")
else
    FROM="START"
    CURRENT_HEALTH="HEALTHY"
    CURRENT_FEATURE=""
    CURRENT_ATTEMPTS=1
fi

# Validate transition
SCRIPT_DIR="$(dirname "$0")"
if ! "$SCRIPT_DIR/validate-transition.sh" "$FROM" "$TO"; then
    echo "Error: Invalid transition $FROM → $TO" >&2
    exit 1
fi

# Record transition
TIMESTAMP=$(date -Iseconds)

# Build history entry with reason
HISTORY_ENTRY=$(cat <<EOF
{
  "from": "$FROM",
  "to": "$TO",
  "at": "$TIMESTAMP",
  "reason": "$REASON"
}
EOF
)

# Update state file preserving all fields
if [ -f "$STATE_FILE" ]; then
    jq --arg to "$TO" \
       --arg ts "$TIMESTAMP" \
       --arg from "$FROM" \
       --arg health "$CURRENT_HEALTH" \
       --arg feature "$CURRENT_FEATURE" \
       --argjson attempts "$CURRENT_ATTEMPTS" \
       --argjson entry "$HISTORY_ENTRY" \
       '.history += [$entry] | .state = $to | .entered_at = $ts | .health_status = $health | .feature_id = $feature | .attempts = $attempts | .last_updated = $ts' \
       "$STATE_FILE" > /tmp/state.tmp && mv /tmp/state.tmp "$STATE_FILE"
else
    cat > "$STATE_FILE" << EOF
{
  "state": "$TO",
  "entered_at": "$TIMESTAMP",
  "health_status": "$CURRENT_HEALTH",
  "feature_id": "$CURRENT_FEATURE",
  "attempts": $CURRENT_ATTEMPTS,
  "history": [$HISTORY_ENTRY],
  "last_updated": "$TIMESTAMP"
}
EOF
fi

echo "Transition: $FROM → $TO"
echo "Recorded at: $TIMESTAMP"
echo "Reason: $REASON"
