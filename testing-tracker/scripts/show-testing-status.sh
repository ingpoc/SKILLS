#!/bin/bash
# show-testing-status.sh
#
# Purpose: Show testing progress summary
# Human-readable or JSON output
#
# Usage: ./show-testing-status.sh [--json]

set -eo pipefail

TESTING_FILE=".claude/progress/testing-list.json"
OUTPUT_FORMAT="human"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --json)
      OUTPUT_FORMAT="json"
      shift
      ;;
    *)
      echo "Usage: show-testing-status.sh [--json]" >&2
      exit 1
      ;;
  esac
done

if [ ! -f "$TESTING_FILE" ]; then
  echo "Error: testing-list.json not found at $TESTING_FILE" >&2
  echo "Run 'initialize-testing-list.sh' first" >&2
  exit 1
fi

# JSON output
if [ "$OUTPUT_FORMAT" = "json" ]; then
  jq '.' "$TESTING_FILE"
  exit 0
fi

# Human-readable output
echo ""
echo "=== Browser Testing Status ==="
echo ""

# Summary
jq -r '
  "Total Features:  \(.summary.total)
Tested:           \(.summary.tested)
Pending:          \(.summary.pending)
Failed:           \(.summary.failed)
Skipped:          \(.summary.skipped // 0)

Progress:         \((.summary.tested / (.summary.total // 1) * 100) | floor)%"
' "$TESTING_FILE"

echo ""
echo "--- Features by Status ---"
echo ""

# Tested features
TESTED_COUNT=$(jq '[.features[] | select(.browser_test_status == "passed")] | length' "$TESTING_FILE")
if [ "$TESTED_COUNT" -gt 0 ]; then
  echo "✓ Tested ($TESTED_COUNT):"
  jq -r '.features[] | select(.browser_test_status == "passed") | "  - \(.id): \(.description)"' "$TESTING_FILE"
  echo ""
fi

# Pending features
PENDING_COUNT=$(jq '[.features[] | select(.browser_test_status == "pending")] | length' "$TESTING_FILE")
if [ "$PENDING_COUNT" -gt 0 ]; then
  echo "○ Pending ($PENDING_COUNT):"
  jq -r '.features[] | select(.browser_test_status == "pending") | "  - \(.id): \(.description)"' "$TESTING_FILE"
  echo ""
fi

# Failed features
FAILED_COUNT=$(jq '[.features[] | select(.browser_test_status == "failed")] | length' "$TESTING_FILE")
if [ "$FAILED_COUNT" -gt 0 ]; then
  echo "✗ Failed ($FAILED_COUNT):"
  jq -r '.features[] | select(.browser_test_status == "failed") | "  - \(.id): \(.description)"' "$TESTING_FILE"
  echo ""
fi

# In-progress features
IN_PROGRESS_COUNT=$(jq '[.features[] | select(.browser_test_status == "in_progress")] | length' "$TESTING_FILE")
if [ "$IN_PROGRESS_COUNT" -gt 0 ]; then
  echo "→ In Progress ($IN_PROGRESS_COUNT):"
  jq -r '.features[] | select(.browser_test_status == "in_progress") | "  - \(.id): \(.description)"' "$TESTING_FILE"
  echo ""
fi

# Next feature to test
NEXT_FEATURE=$(jq '.features[] | select(.browser_test_status == "pending") | .id' "$TESTING_FILE" | head -1)
if [ -n "$NEXT_FEATURE" ]; then
  echo "--- Next Feature to Test ---"
  echo ""
  jq -r --arg id "$NEXT_FEATURE" '.features[] | select(.id == $id) | "ID:     \(.id)\nDesc:   \(.description)\n\nAcceptance Criteria:\n  \(.browser_acceptance_criteria[])"' "$TESTING_FILE"
  echo ""
fi

exit 0
