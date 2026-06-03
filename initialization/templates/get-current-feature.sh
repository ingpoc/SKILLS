#!/bin/bash
# TEMPLATE: get-current-feature.sh
#
# Purpose: Extract next pending feature from feature-list.json
#
# CUSTOMIZE THIS for your project:
# - If feature-list format is different, adjust jq filter
# - If features are stored elsewhere, update FEATURE_FILE path
#
# Return format (JSON):
#   {
#     "id": "feat-001",
#     "description": "Feature description",
#     "status": "pending"
#   }

set -e

FEATURE_FILE=".claude/progress/feature-list.json"

if [ ! -f "$FEATURE_FILE" ]; then
  echo "Error: feature-list.json not found at $FEATURE_FILE" >&2
  exit 1
fi

# Get first pending feature (adjust jq filter if needed)
FEATURE=$(jq '.features[] | select(.status=="pending")' "$FEATURE_FILE" 2>/dev/null | jq -s '.[0]' 2>/dev/null)

if [ -z "$FEATURE" ] || [ "$FEATURE" = "null" ]; then
  echo "No pending features found" >&2
  exit 1
fi

# Output as JSON
echo "$FEATURE"

exit 0
