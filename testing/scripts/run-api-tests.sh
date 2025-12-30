#!/bin/bash
# Run API endpoint tests
# Exit: 0 = all pass, 1 = failures
# Config: .claude/config/project.json → api_url, dev_server_port

EVIDENCE_DIR="/tmp/test-evidence"
mkdir -p "$EVIDENCE_DIR"

# ─────────────────────────────────────────────────────────────────
# Config helper (self-contained)
# ─────────────────────────────────────────────────────────────────
CONFIG="$PWD/.claude/config/project.json"
get_config() { jq -r ".$1 // empty" "$CONFIG" 2>/dev/null || echo "$2"; }

# ─────────────────────────────────────────────────────────────────
# Get base URL from config
# ─────────────────────────────────────────────────────────────────
PORT=$(get_config "dev_server_port" "3000")
BASE_URL=$(get_config "api_url" "http://localhost:$PORT")

ERRORS=0
TESTS=0

echo "=== Running API Tests ==="
echo "Base URL: $BASE_URL"

# ─────────────────────────────────────────────────────────────────
# Test endpoint helper
# ─────────────────────────────────────────────────────────────────
test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local description=$4

    ((TESTS++))
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" --max-time 5 2>/dev/null || echo "000")

    if [ "$STATUS" = "$expected_status" ]; then
        echo "✓ $description - $STATUS"
    else
        echo "✗ $description - Expected $expected_status, got $STATUS"
        ((ERRORS++))
    fi
}

# ─────────────────────────────────────────────────────────────────
# Run tests
# ─────────────────────────────────────────────────────────────────
test_endpoint "GET" "/health" "200" "Health check"
test_endpoint "GET" "/" "200" "Root endpoint"

# Save evidence
cat > "$EVIDENCE_DIR/api-tests.json" << EOF
{
  "api_tests": {
    "base_url": "$BASE_URL",
    "total": $TESTS,
    "passed": $((TESTS - ERRORS)),
    "failed": $ERRORS,
    "all_passed": $([ $ERRORS -eq 0 ] && echo true || echo false)
  }
}
EOF

[ $ERRORS -eq 0 ] && exit 0 || exit 1
