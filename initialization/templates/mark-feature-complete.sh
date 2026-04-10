#!/bin/bash
# TEMPLATE: mark-feature-complete.sh
#
# Purpose: Update feature-list.json with new feature status
#
# CUSTOMIZE THIS for your project:
# - Adjust feature-list format if different
# - Add validation (check feature exists before updating)
# - Support different status values (pending, in_progress, implemented, tested, blocked)
#
# Usage: ./mark-feature-complete.sh <feature-id> [status]
# Example: ./mark-feature-complete.sh feat-001 implemented

set -e

FEATURE_ID=$1
STATUS=${2:-"implemented"}

if [ -z "$FEATURE_ID" ]; then
  echo "Usage: mark-feature-complete.sh <feature-id> [status]" >&2
  exit 1
fi

FEATURE_FILE=".claude/progress/feature-list.json"

if [ ! -f "$FEATURE_FILE" ]; then
  echo "Error: feature-list.json not found at $FEATURE_FILE" >&2
  exit 1
fi

# Update status using jq (adjust filter if feature-list format is different)
jq ".features[] |= if .id==\"$FEATURE_ID\" then .status=\"$STATUS\" else . end" "$FEATURE_FILE" > "${FEATURE_FILE}.tmp"

# Verify update was successful
if ! jq -e --arg id "$FEATURE_ID" --arg status "$STATUS" '.features[] | select(.id == $id and .status == $status)' "${FEATURE_FILE}.tmp" > /dev/null 2>&1; then
  rm "${FEATURE_FILE}.tmp"
  echo "Error: Failed to update feature status" >&2
  exit 1
fi

# Move temp file to replace original
mv "${FEATURE_FILE}.tmp" "$FEATURE_FILE"

echo "Updated $FEATURE_ID status to: $STATUS"
exit 0
