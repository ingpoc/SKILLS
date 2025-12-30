#!/bin/bash
# Session checkpoint commit
# Usage: ./session-commit.sh [message]
# Creates a checkpoint commit at session end

set -e

MESSAGE="${1:-Session checkpoint}"

# Check if in git repo
if [ ! -d ".git" ]; then
    echo "Not a git repository, skipping commit"
    exit 0
fi

# Check for uncommitted changes
if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit"
    exit 0
fi

# Get session info
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
STATE="UNKNOWN"
if [ -f ".claude/progress/state.json" ]; then
    STATE=$(jq -r '.state // "UNKNOWN"' .claude/progress/state.json)
fi

# Count completed features
COMPLETED=0
TOTAL=0
if [ -f ".claude/progress/feature-list.json" ]; then
    COMPLETED=$(jq '[.features[] | select(.status == "tested" or .status == "completed")] | length' .claude/progress/feature-list.json 2>/dev/null || echo 0)
    TOTAL=$(jq '.features | length' .claude/progress/feature-list.json 2>/dev/null || echo 0)
fi

# Stage all changes
git add -A

# Create commit with session info
COMMIT_MSG="[session] $MESSAGE

State: $STATE
Features: $COMPLETED/$TOTAL completed
Timestamp: $TIMESTAMP"

git commit -m "$COMMIT_MSG"

# Output commit hash
COMMIT_HASH=$(git rev-parse --short HEAD)
echo ""
echo "Session commit: $COMMIT_HASH"
echo "State: $STATE, Features: $COMPLETED/$TOTAL"

# Output JSON
cat << EOF
{
  "type": "session",
  "commit_hash": "$COMMIT_HASH",
  "state": "$STATE",
  "features_completed": $COMPLETED,
  "features_total": $TOTAL,
  "timestamp": "$TIMESTAMP"
}
EOF
