#!/bin/bash
# Auto-commit with feature ID message
# Usage: ./feature-commit.sh <feature-id> [message]
# Example: ./feature-commit.sh feat-001 "Implement user login"

set -e

FEATURE_ID="${1:-}"
MESSAGE="${2:-}"

if [ -z "$FEATURE_ID" ]; then
    echo "Usage: ./feature-commit.sh <feature-id> [message]"
    echo "Example: ./feature-commit.sh feat-001 'Implement user login'"
    exit 1
fi

# Check if in git repo
if [ ! -d ".git" ]; then
    echo "ERROR: Not a git repository"
    exit 1
fi

# Check for uncommitted changes
if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit"
    exit 0
fi

# Get feature details from feature-list.json if no message provided
if [ -z "$MESSAGE" ]; then
    if [ -f ".claude/progress/feature-list.json" ]; then
        FEATURE_NAME=$(jq -r --arg id "$FEATURE_ID" '.features[] | select(.id == $id) | .name // .description // "Feature implementation"' .claude/progress/feature-list.json 2>/dev/null)
        if [ -n "$FEATURE_NAME" ] && [ "$FEATURE_NAME" != "null" ]; then
            MESSAGE="$FEATURE_NAME"
        else
            MESSAGE="Implement $FEATURE_ID"
        fi
    else
        MESSAGE="Implement $FEATURE_ID"
    fi
fi

# Stage all changes
git add -A

# Create commit with standardized format
COMMIT_MSG="[$FEATURE_ID] $MESSAGE"

git commit -m "$COMMIT_MSG"

# Output commit hash for tracking
COMMIT_HASH=$(git rev-parse --short HEAD)
echo ""
echo "Committed: $COMMIT_HASH - $COMMIT_MSG"

# Update feature-list.json with commit hash
if [ -f ".claude/progress/feature-list.json" ]; then
    jq --arg id "$FEATURE_ID" --arg hash "$COMMIT_HASH" \
        '(.features[] | select(.id == $id)) += {"last_commit": $hash}' \
        .claude/progress/feature-list.json > /tmp/feature-list.tmp && \
        mv /tmp/feature-list.tmp .claude/progress/feature-list.json
    echo "Updated feature-list.json with commit hash"
fi

# Output JSON for programmatic use
cat << EOF
{
  "feature_id": "$FEATURE_ID",
  "commit_hash": "$COMMIT_HASH",
  "message": "$COMMIT_MSG"
}
EOF
