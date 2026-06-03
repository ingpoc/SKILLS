#!/bin/bash
# Store a decision trace
# Usage: store-trace.sh "DECISION_SUMMARY" [CATEGORY]
# Output: Trace ID

DECISION="$1"
CATEGORY="${2:-general}"
TRACES_DIR=".claude/traces"
TIMESTAMP=$(date -Iseconds)
TRACE_ID="trace_$(date +%s)"

mkdir -p "$TRACES_DIR"

# Create trace file
cat > "$TRACES_DIR/$TRACE_ID.json" << EOF
{
  "id": "$TRACE_ID",
  "timestamp": "$TIMESTAMP",
  "category": "$CATEGORY",
  "decision": "$DECISION",
  "outcome": "pending",
  "session": "${SESSION_ID:-unknown}",
  "metadata": {
    "state": "$(jq -r '.state // "unknown"' .claude/progress/state.json 2>/dev/null)",
    "feature": "$(jq -r '.feature_id // "none"' .claude/progress/state.json 2>/dev/null)"
  }
}
EOF

echo "$TRACE_ID"
echo "Trace stored: $TRACES_DIR/$TRACE_ID.json"
