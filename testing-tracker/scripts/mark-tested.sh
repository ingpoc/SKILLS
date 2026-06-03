#!/bin/bash
# mark-tested.sh
#
# Purpose: Mark feature as browser tested
# Updates testing-list.json with test result
#
# Usage: ./mark-tested.sh <feature-id> [passed|failed|skipped]
# Example: ./mark-tested.sh AGENT-006 passed
#
# Status values: pending, in_progress, passed, failed, skipped

set -eo pipefail

FEATURE_ID=$1
STATUS=${2:-"passed"}
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S+00:00")

# Validate status
case "$STATUS" in
  pending|in_progress|passed|failed|skipped)
    ;;
  *)
    echo "Usage: mark-tested.sh <feature-id> [status]" >&2
    echo "Status values: pending, in_progress, passed, failed, skipped" >&2
    exit 1
    ;;
esac

if [ -z "$FEATURE_ID" ]; then
  echo "Usage: mark-tested.sh <feature-id> [status]" >&2
  echo "Status values: pending, in_progress, passed, failed, skipped" >&2
  exit 1
fi

TESTING_FILE=".claude/progress/testing-list.json"

if [ ! -f "$TESTING_FILE" ]; then
  echo "Error: testing-list.json not found at $TESTING_FILE" >&2
  echo "Run 'initialize-testing-list.sh' first" >&2
  exit 1
fi

# Check if feature exists
FEATURE_EXISTS=$(jq -r --arg id "$FEATURE_ID" '.features[] | select(.id == $id) | .id' "$TESTING_FILE")
if [ -z "$FEATURE_EXISTS" ]; then
  echo "Error: Feature '$FEATURE_ID' not found in testing-list.json" >&2
  exit 1
fi

# Update status, last_tested, and increment attempts
jq --arg id "$FEATURE_ID" \
  --arg status "$STATUS" \
  --arg timestamp "$TIMESTAMP" \
  '(.features[] | select(.id == $id)) |= (
      .browser_test_status = $status |
      .last_tested = $timestamp |
      .attempts += 1
    )' \
  "$TESTING_FILE" > "${TESTING_FILE}.tmp"

# Recalculate summary
jq '
  .summary.tested = ([.features[] | select(.browser_test_status == "passed")] | length) |
  .summary.pending = ([.features[] | select(.browser_test_status == "pending")] | length) |
  .summary.failed = ([.features[] | select(.browser_test_status == "failed")] | length) |
  .updated = "'"$TIMESTAMP"'" |
  if .summary.skipped == null then .summary.skipped = 0 else . end
' "${TESTING_FILE}.tmp" > "${TESTING_FILE}.tmp2"
mv "${TESTING_FILE}.tmp2" "${TESTING_FILE}.tmp"

# Verify update was successful
UPDATED_STATUS=$(jq -r --arg id "$FEATURE_ID" '.features[] | select(.id == $id) | .browser_test_status' "${TESTING_FILE}.tmp")
if [ "$UPDATED_STATUS" != "$STATUS" ]; then
  rm "${TESTING_FILE}.tmp"
  echo "Error: Failed to update feature test status (expected '$STATUS', got '$UPDATED_STATUS')" >&2
  exit 1
fi

# Move temp file to replace original
mv "${TESTING_FILE}.tmp" "$TESTING_FILE"

# Output summary
echo "Updated $FEATURE_ID browser test status to: $STATUS"
jq -r '"Summary: Tested: \(.summary.tested) | Pending: \(.summary.pending) | Failed: \(.summary.failed)"' "$TESTING_FILE"

exit 0
