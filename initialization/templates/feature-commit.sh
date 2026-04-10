#!/bin/bash
# TEMPLATE: feature-commit.sh
#
# Purpose: Commit implementation with feature ID for traceability
#
# CUSTOMIZE THIS for your project:
# - Enforce your commit message format (e.g., [FEAT-XXX], feat(id))
# - Add additional checks (linting, formatting)
# - Support different commit workflows (conventional commits, etc)
#
# Usage: ./feature-commit.sh <feature-id> [message]
# Example: ./feature-commit.sh feat-001 "Implement credential validation"

set -e

FEATURE_ID=$1
MESSAGE=$2

if [ -z "$FEATURE_ID" ]; then
  echo "Usage: feature-commit.sh <feature-id> [message]" >&2
  exit 1
fi

# Check for changes
if [ -z "$(git status --porcelain)" ]; then
  echo "No changes to commit" >&2
  exit 0
fi

# Construct commit message with feature ID
COMMIT_MSG="[$FEATURE_ID] ${MESSAGE:-Implementation}"

echo "Committing: $COMMIT_MSG"
git add -A
git commit -m "$COMMIT_MSG"

exit 0
