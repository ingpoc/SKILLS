#!/bin/bash
# initialize-testing-list.sh
#
# Purpose: Create testing-list.json from feature-list.json
# Filters features by status="implemented" and adds browser acceptance criteria
#
# Usage: ./initialize-testing-list.sh [--phase PHASE_ID]
#
# Environment: Requires jq for JSON processing

set -eo pipefail

FEATURE_FILE=".claude/progress/feature-list.json"
TESTING_FILE=".claude/progress/testing-list.json"
PHASE_FILTER=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --phase)
      PHASE_FILTER="$2"
      shift 2
      ;;
    *)
      echo "Usage: initialize-testing-list.sh [--phase PHASE_ID]" >&2
      exit 1
      ;;
  esac
done

# Check feature-list.json exists
if [ ! -f "$FEATURE_FILE" ]; then
  echo "Error: feature-list.json not found at $FEATURE_FILE" >&2
  exit 1
fi

# Get current timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S+00:00")

# Read current phase from state.json if no filter provided
if [ -z "$PHASE_FILTER" ]; then
  STATE_FILE=".claude/progress/state.json"
  if [ -f "$STATE_FILE" ]; then
    CURRENT_FEATURE=$(jq -r '.current_feature // ""' "$STATE_FILE" 2>/dev/null || echo "")
    if [ -n "$CURRENT_FEATURE" ]; then
      PHASE_FILTER=$(jq -r --arg id "$CURRENT_FEATURE" '.features[] | select(.id == $id) | .phase // ""' "$FEATURE_FILE" 2>/dev/null || echo "")
    fi
  fi
fi

# Build jq filter based on phase
if [ -n "$PHASE_FILTER" ]; then
  PHASE_FILTER="\"$PHASE_FILTER\""
fi

# Create browser acceptance criteria based on feature type
# This is done via jq logic
jq --arg timestamp "$TIMESTAMP" \
  --arg phase_filter "$PHASE_FILTER" \
  '
    # Helper function to generate browser acceptance criteria
    def generate_criteria($desc; $id):
      if ($desc | test("API|api|Endpoint|endpoint")) or ($id | test("API|WEEK")) then
        ["Navigate to endpoint route", "Verify network request returns 200", "Check response JSON structure", "Verify no console errors", "Test error handling"]
      elif ($desc | test("UI|ui|Component|component|Page|page")) or ($id | test("WEBSITE")) then
        ["Component renders on page", "User interaction works", "State updates correctly", "No console errors", "Responsive layout works"]
      elif ($desc | test("Form|form|Input|input|Validation|validation")) or ($id | test("CART|CHECKOUT")) then
        ["Form submits successfully", "Validation displays correctly", "Error handling works", "Clear form after submit", "No console errors"]
      elif ($desc | test("Navigation|navigation|Route|route")) or ($id | test("ORDERS")) then
        ["Route loads correctly", "URL params work", "Back/forward navigation", "Page title updates", "No 404 errors"]
      elif ($desc | test("Integration|integration|SDK|sdk|Client|client")) or ($id | test("SDK|SELLER|BUYER")) then
        ["End-to-end flow works", "Data syncs correctly", "No console errors", "Network requests complete", "UI reflects state"]
      else
        ["Feature accessible in UI", "No console errors", "Network requests succeed", "Expected behavior works", "No visual bugs"]
      end;

    # Build the testing list
    {
      version: "1.0.0",
      created: $timestamp,
      updated: $timestamp,
      current_phase: ($phase_filter // "" | if . == "" then "" else fromjson end),
      features: [
        .features[] |
        select(.status == "implemented") |
        select(
          if $phase_filter == "" then
            true
          else
            .phase == ($phase_filter | fromjson)
          end
        ) |
        {
          id: .id,
          description: .description,
          browser_test_status: "pending",
          browser_acceptance_criteria: generate_criteria(.description; .id),
          last_tested: null,
          test_evidence: [],
          attempts: 0,
          phase: .phase
        }
      ],
      summary: {
        total: 0,
        tested: 0,
        pending: 0,
        failed: 0
      }
    } |
    # Calculate summary
    .summary.total = (.features | length) |
    .summary.pending = (.features | length)
  ' "$FEATURE_FILE" > "${TESTING_FILE}.new"

# If testing-list.json exists, preserve existing test status for features
if [ -f "$TESTING_FILE" ]; then
  # Merge existing test status into new list
  jq -s '
   .[0] as $new | .[1] as $existing |
    $new | .features |= map(
      .id as $fid |
      ($existing.features[]? | select(.id == $fid)) as $existing_feat |
      if $existing_feat then
        .browser_test_status = $existing_feat.browser_test_status |
        .last_tested = $existing_feat.last_tested |
        .test_evidence = $existing_feat.test_evidence |
        .attempts = $existing_feat.attempts
      else
        .
      end
    ) |
    .summary.tested = ([.features[] | select(.browser_test_status == "passed")] | length) |
    .summary.pending = ([.features[] | select(.browser_test_status == "pending")] | length) |
    .summary.failed = ([.features[] | select(.browser_test_status == "failed")] | length)
  ' "${TESTING_FILE}.new" "$TESTING_FILE" > "${TESTING_FILE}.merged"
  mv "${TESTING_FILE}.merged" "$TESTING_FILE"
else
  mv "${TESTING_FILE}.new" "$TESTING_FILE"
fi

# Output summary
echo "Testing list initialized: $TESTING_FILE"
echo ""
jq -r '"Features: \(.summary.total) | Tested: \(.summary.tested) | Pending: \(.summary.pending) | Failed: \(.summary.failed)"' "$TESTING_FILE"
echo ""
echo "Next feature to test:"
~/.claude/skills/testing-tracker/scripts/get-next-to-test.sh 2>/dev/null || echo "  (all features tested or none available)"

exit 0
