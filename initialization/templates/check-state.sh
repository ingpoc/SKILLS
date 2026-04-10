#!/bin/bash
# Check current state from state.json
# Usage: ./check-state.sh [--json]
# Responsibility: State machine status (ORCHESTRATOR)

set -e

STATE_FILE=".claude/progress/state.json"
JSON_OUTPUT="${1:-}"

if [ ! -f "$STATE_FILE" ]; then
    if [ "$JSON_OUTPUT" = "--json" ]; then
        echo '{"state": "START", "exists": false}'
    else
        echo "START (no state file)"
    fi
    exit 0
fi

CURRENT_STATE=$(jq -r '.state' "$STATE_FILE")
ENTERED_AT=$(jq -r '.entered_at // "unknown"' "$STATE_FILE")
HEALTH=$(jq -r '.health_status // "unknown"' "$STATE_FILE")

if [ "$JSON_OUTPUT" = "--json" ]; then
    jq -c '. + {"exists": true}' "$STATE_FILE"
else
    echo "State: $CURRENT_STATE"
    echo "Entered: $ENTERED_AT"
    echo "Health: $HEALTH"
fi
