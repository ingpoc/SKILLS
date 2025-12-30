#!/bin/bash
# Collect all test evidence into summary
# Output: results.json with all test outcomes

EVIDENCE_DIR="/tmp/test-evidence"
mkdir -p "$EVIDENCE_DIR"

echo "=== Collecting Test Evidence ==="

# Initialize results
ALL_PASSED=true
RESULTS="{\"timestamp\": \"$(date -Iseconds)\", \"tests\": {}}"

# Collect unit test results
if [ -f "$EVIDENCE_DIR/unit-tests.json" ]; then
    UNIT=$(cat "$EVIDENCE_DIR/unit-tests.json")
    PASSED=$(echo "$UNIT" | jq '.unit_tests.passed')
    RESULTS=$(echo "$RESULTS" | jq '.tests.unit = '"$UNIT"'')
    [ "$PASSED" = "false" ] && ALL_PASSED=false
fi

# Collect API test results
if [ -f "$EVIDENCE_DIR/api-tests.json" ]; then
    API=$(cat "$EVIDENCE_DIR/api-tests.json")
    PASSED=$(echo "$API" | jq '.api_tests.passed')
    RESULTS=$(echo "$RESULTS" | jq '.tests.api = '"$API"'')
    [ "$PASSED" = "false" ] && ALL_PASSED=false
fi

# Collect browser test results
if [ -f "$EVIDENCE_DIR/browser-tests.json" ]; then
    BROWSER=$(cat "$EVIDENCE_DIR/browser-tests.json")
    PASSED=$(echo "$BROWSER" | jq '.browser_tests.passed')
    RESULTS=$(echo "$RESULTS" | jq '.tests.browser = '"$BROWSER"'')
    [ "$PASSED" = "false" ] && ALL_PASSED=false
fi

# Set overall result
RESULTS=$(echo "$RESULTS" | jq '.all_passed = '$ALL_PASSED'')

# Save final results
echo "$RESULTS" | jq '.' > "$EVIDENCE_DIR/results.json"

echo "Evidence collected to $EVIDENCE_DIR/results.json"
cat "$EVIDENCE_DIR/results.json"

[ "$ALL_PASSED" = "true" ] && exit 0 || exit 1
