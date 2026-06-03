#!/bin/bash
# start-next-test.sh
#
# Purpose: Get next feature to test and trigger testing skill
# Loads the testing skill to begin browser testing
#
# Usage: ./start-next-test.sh

set -eo pipefail

TESTING_FILE=".claude/progress/testing-list.json"

if [ ! -f "$TESTING_FILE" ]; then
  echo "Error: testing-list.json not found at $TESTING_FILE" >&2
  echo "Run 'initialize-testing-list.sh' first" >&2
  exit 1
fi

# Get next pending feature
NEXT_FEATURE=$(jq '.features[] | select(.browser_test_status=="pending")' "$TESTING_FILE" 2>/dev/null | jq -s '.[0]' 2>/dev/null)

if [ -z "$NEXT_FEATURE" ] || [ "$NEXT_FEATURE" = "null" ]; then
  echo "No pending features found" >&2
  exit 1
fi

# Extract feature info
FEATURE_ID=$(echo "$NEXT_FEATURE" | jq -r '.id')
FEATURE_DESC=$(echo "$NEXT_FEATURE" | jq -r '.description')

# Mark as in_progress
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S+00:00")
jq --arg id "$FEATURE_ID" \
  --arg timestamp "$TIMESTAMP" \
  '(.features[] | select(.id == $id)) |= (.browser_test_status = "in_progress" | .last_tested = $timestamp)' \
  "$TESTING_FILE" > "${TESTING_FILE}.tmp"
mv "${TESTING_FILE}.tmp" "$TESTING_FILE"

# Output feature info for testing skill
echo "=== Next Feature to Test ==="
echo ""
echo "ID: $FEATURE_ID"
echo "Description: $FEATURE_DESC"
echo ""
echo "Acceptance Criteria:"
echo "$NEXT_FEATURE" | jq -r '.browser_acceptance_criteria[]' | sed 's/^/  - /'
echo ""
echo "Loading testing skill..."
echo ""

# Trigger testing skill via Skill tool - this will be called by the skill
echo "TESTING_FEATURE_ID=$FEATURE_ID"
echo "TESTING_FEATURE_DESC=$FEATURE_DESC"

exit 0
