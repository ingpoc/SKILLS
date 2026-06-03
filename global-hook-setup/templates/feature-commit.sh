#!/bin/bash
# Global Hook: feature-commit.sh
#
# Helper script for committing features with proper format.
# Usage: feature-commit.sh <feature-id> [<message>]
#
# Creates commit with [feat-id] prefix for traceability.

set -euo pipefail

FEATURE_ID="${1:-}"
MESSAGE="${2:-}"

if [[ -z "$FEATURE_ID" ]]; then
    echo "Usage: feature-commit.sh <feature-id> [<message>]" >&2
    exit 1
fi

PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-.}"
cd "$PROJECT_ROOT"

# Get feature title from feature-list if not provided
if [[ -z "$MESSAGE" ]]; then
    MESSAGE=$(jq -r ".features[] | select(.id==\"$FEATURE_ID\") | .title" .claude/progress/feature-list.json 2>/dev/null || echo "")
fi

# Create commit
git add .
git commit -m "$(cat <<EOF
[$FEATURE_ID] $MESSAGE

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

echo "Feature $FEATURE_ID committed"
