#!/bin/bash
# Initialize .claude/progress/ tracking structure
# Usage: ./init-progress.sh
# Responsibility: Progress tracking setup (INIT state)

set -e

echo "Initializing progress tracking..."

# Create directories
mkdir -p .claude/progress
mkdir -p .claude/config
mkdir -p .claude/traces

# ─────────────────────────────────────────────────────────────────
# Create state.json
# ─────────────────────────────────────────────────────────────────

STATE_FILE=".claude/progress/state.json"
if [ ! -f "$STATE_FILE" ]; then
    cat > "$STATE_FILE" << EOF
{
  "state": "INIT",
  "entered_at": "$(date -Iseconds)",
  "health_status": "UNKNOWN",
  "history": []
}
EOF
    echo "Created: $STATE_FILE"
else
    echo "Exists: $STATE_FILE"
fi

# ─────────────────────────────────────────────────────────────────
# Create file_history.json (for context resumption)
# ─────────────────────────────────────────────────────────────────

HISTORY_FILE=".claude/progress/file_history.json"
if [ ! -f "$HISTORY_FILE" ]; then
    echo '{"files": [], "last_updated": "'$(date -Iseconds)'"}' | jq '.' > "$HISTORY_FILE"
    echo "Created: $HISTORY_FILE"
else
    echo "Exists: $HISTORY_FILE"
fi

# ─────────────────────────────────────────────────────────────────
# Create checkpoint.json (for compression triggers)
# ─────────────────────────────────────────────────────────────────

CHECKPOINT_FILE=".claude/progress/checkpoint.json"
if [ ! -f "$CHECKPOINT_FILE" ]; then
    cat > "$CHECKPOINT_FILE" << EOF
{
  "last_checkpoint": null,
  "compression_level": 0,
  "summaries": []
}
EOF
    echo "Created: $CHECKPOINT_FILE"
else
    echo "Exists: $CHECKPOINT_FILE"
fi

# ─────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────

echo ""
echo "=== Progress Structure ==="
ls -la .claude/progress/
echo ""
echo "Next: Run detect-project.sh → check-dependencies.sh → create-feature-list.sh"
