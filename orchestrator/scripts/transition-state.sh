#!/bin/bash
# Execute state transition
# Usage: ./transition-state.sh TO
# Responsibility: State machine update (ORCHESTRATOR)

set -e

TO="${1:-}"
STATE_FILE=".claude/progress/state.json"

if [ -z "$TO" ]; then
    echo "Usage: $0 TO_STATE"
    exit 1
fi

mkdir -p .claude/progress

# Get current state
if [ -f "$STATE_FILE" ]; then
    FROM=$(jq -r '.state' "$STATE_FILE")
else
    FROM="START"
fi

# Validate transition
SCRIPT_DIR="$(dirname "$0")"
if ! "$SCRIPT_DIR/validate-transition.sh" "$FROM" "$TO"; then
    exit 1
fi

# Record transition
TIMESTAMP=$(date -Iseconds)

if [ -f "$STATE_FILE" ]; then
    jq --arg to "$TO" --arg ts "$TIMESTAMP" --arg from "$FROM" \
       '.history += [{"from": $from, "to": $to, "at": $ts}] | .state = $to | .entered_at = $ts' \
       "$STATE_FILE" > /tmp/state.tmp && mv /tmp/state.tmp "$STATE_FILE"
else
    cat > "$STATE_FILE" << EOF
{
  "state": "$TO",
  "entered_at": "$TIMESTAMP",
  "health_status": "UNKNOWN",
  "history": [{"from": "$FROM", "to": "$TO", "at": "$TIMESTAMP"}]
}
EOF
fi

echo "Transition: $FROM → $TO"
echo "Recorded at: $TIMESTAMP"
