#!/bin/bash
# auto-load-orchestrator.sh
#
# Reminds user to load orchestrator skill on first prompt of session.
# Only triggers once per session using a marker file.

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-.}"
STATE_DIR="$PROJECT_ROOT/.claude/progress"
MARKER_FILE="$STATE_DIR/.session_started"

# Only trigger once per session
if [[ -f "$MARKER_FILE" ]]; then
    exit 0
fi

# Create marker
mkdir -p "$STATE_DIR"
touch "$MARKER_FILE"

# Check current state
CURRENT_STATE="START"
if [[ -f "$STATE_DIR/state.json" ]]; then
    CURRENT_STATE=$(jq -r '.state // "START"' "$STATE_DIR/state.json" 2>/dev/null)
fi

# Output reminder
cat << 'EOF'
SESSION START PROTOCOL:
1. Load orchestrator skill: /orchestrator
2. Current state: IMPLEMENT
3. Run check-state.sh if needed
4. Load appropriate skill for state (init/implement/test/complete)
EOF

echo "Current state: $CURRENT_STATE"

exit 0
