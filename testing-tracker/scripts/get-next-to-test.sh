#!/bin/bash
# get-next-to-test.sh
#
# Purpose: Get next feature for browser testing
# Returns feature with browser_test_status="pending"
#
# Usage: ./get-next-to-test.sh
# Return format (JSON):
#   {
#     "id": "feat-001",
#     "description": "Feature description",
#     "browser_test_status": "pending"
#   }

set -eo pipefail

TESTING_FILE=".claude/progress/testing-list.json"

if [ ! -f "$TESTING_FILE" ]; then
  echo "Error: testing-list.json not found at $TESTING_FILE" >&2
  echo "Run 'initialize-testing-list.sh' first" >&2
  exit 1
fi

# Get first pending feature
FEATURE=$(jq '.features[] | select(.browser_test_status=="pending")' "$TESTING_FILE" 2>/dev/null | jq -s '.[0]' 2>/dev/null)

if [ -z "$FEATURE" ] || [ "$FEATURE" = "null" ]; then
  # Check if there are any in_progress features
  IN_PROGRESS=$(jq '.features[] | select(.browser_test_status=="in_progress")' "$TESTING_FILE" 2>/dev/null | jq -s '.[0]' 2>/dev/null)
  if [ -n "$IN_PROGRESS" ] && [ "$IN_PROGRESS" != "null" ]; then
    echo "Feature currently in progress:" >&2
    echo "$IN_PROGRESS" >&2
    exit 1
  fi

  # Check if all features are tested
  ALL_TESTED=$(jq -r '(.features | length) == (.summary.tested + .summary.skipped // 0)' "$TESTING_FILE" 2>/dev/null || echo "false")
  if [ "$ALL_TESTED" = "true" ]; then
    echo "All features have been tested!" >&2
    exit 0
  fi

  echo "No pending features found" >&2
  exit 1
fi

# Output as JSON
echo "$FEATURE"

exit 0
