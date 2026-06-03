#!/bin/bash
# Apply Reflexion learning loop to session traces
# Usage: apply-learning.sh [SESSION_ID]
# Output: Learnings summary

SESSION="${1:-$(cat .claude/progress/state.json 2>/dev/null | jq -r '.session // "current"')}"
TRACES_DIR=".claude/traces"
LEARNINGS_DIR=".claude/learnings"

mkdir -p "$LEARNINGS_DIR"

echo "=== Applying Reflexion Learning Loop ==="
echo "Session: $SESSION"

# Collect all traces from session
TRACES=$(find "$TRACES_DIR" -name "*.json" -exec grep -l "\"session\": \"$SESSION\"" {} \; 2>/dev/null)

if [ -z "$TRACES" ]; then
    echo "No traces found for session"
    exit 0
fi

# Extract decisions and outcomes
echo ""
echo "Decisions made:"
for trace in $TRACES; do
    DECISION=$(jq -r '.decision' "$trace")
    OUTCOME=$(jq -r '.outcome' "$trace")
    echo "  - $DECISION → $OUTCOME"
done

# Generate learning summary (in practice, this would use LLM)
LEARNING_ID="learning_$(date +%s)"
cat > "$LEARNINGS_DIR/$LEARNING_ID.json" << EOF
{
  "id": "$LEARNING_ID",
  "session": "$SESSION",
  "created_at": "$(date -Iseconds)",
  "trace_count": $(echo "$TRACES" | wc -l),
  "status": "pending_review",
  "learnings": []
}
EOF

echo ""
echo "Learning file created: $LEARNINGS_DIR/$LEARNING_ID.json"
echo "Review and add learnings manually or via LLM analysis"
