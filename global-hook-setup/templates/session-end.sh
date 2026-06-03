#!/bin/bash
# Global Hook: session-end.sh
#
# Session end hook: Creates checkpoint commit with session summary.
# Non-blocking - ensures session state is preserved for next session.

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-.}"
PROGRESS_DIR="$PROJECT_ROOT/.claude/progress"
SESSION_FILE="$PROGRESS_DIR/session-state.json"

# Only run if session file exists
if [[ ! -f "$SESSION_FILE" ]]; then
    exit 0
fi

# Read session summary
SUMMARY=$(jq -r '.session_summary // "Session checkpoint"' "$SESSION_FILE" 2>/dev/null || echo "Session checkpoint")

# Create checkpoint commit
cd "$PROJECT_ROOT"

# Check if there are changes to commit
if git diff --quiet && git diff --cached --quiet; then
    # No changes, just update session file
    jq -n \
        --arg summary "$SUMMARY" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{checkpoint_at: $timestamp, summary: $summary}' > "$PROGRESS_DIR/checkpoint.json"
else
    # Has changes - create checkpoint commit
    git add .claude/progress/
    git commit -m "$(cat <<EOF
[checkpoint] Session summary

$SUMMARY

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)" 2>/dev/null || true
fi

exit 0
