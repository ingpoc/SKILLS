#!/bin/bash
# run-tests.sh - Batch API endpoint testing
# Usage: ./run-tests.sh [base_url]
# Default base_url: http://localhost:3000
#
# CUSTOMIZE FOR YOUR PROJECT:
# 1. Update BASE_URL default to match your server
# 2. Add/remove test_endpoint calls for your API routes
# 3. Adjust expected status codes (not all are 200)

set -e

BASE_URL="${1:-http://localhost:3000}"
EVIDENCE_DIR="/tmp/test-evidence"
TIMESTAMP=$(date +%s)
LOG_FILE="$EVIDENCE_DIR/api-tests-$TIMESTAMP.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create evidence directory
mkdir -p "$EVIDENCE_DIR"

echo "Running API endpoint tests against: $BASE_URL"
echo "Evidence log: $LOG_FILE"
echo ""

# Track results
PASS=0
FAIL=0
TOTAL=0

# Test endpoint function
test_endpoint() {
  local name="$1"
  local endpoint="$2"
  local expected="${3:-200}"

  TOTAL=$((TOTAL + 1))
  printf "%-40s" "$name"

  # Make request and capture status
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint" 2>/dev/null || echo "000")

  if [ "$status" = "$expected" ]; then
    echo -e "${GREEN}✓ PASS${NC} (HTTP $status)"
    PASS=$((PASS + 1))
    echo "✓ $name: HTTP $status" >> "$LOG_FILE"
  else
    echo -e "${RED}✗ FAIL${NC} (got $status, expected $expected)"
    FAIL=$((FAIL + 1))
    echo "✗ $name: HTTP $status (expected $expected)" >> "$LOG_FILE"
  fi
}

echo "=== Core API Endpoints ==="
# TODO: Add your API endpoints here
# Example:
# test_endpoint "Health Check" "/api/health"
# test_endpoint "Users API" "/api/users"
# test_endpoint "Status" "/api/status"

echo -e "${YELLOW}⚠ No endpoints configured yet${NC}"
echo -e "${YELLOW}  Edit this script and add test_endpoint calls for your API routes${NC}"

echo ""
echo "=== Summary ==="
echo "Total: $TOTAL | ${GREEN}Pass: $PASS${NC} | ${RED}Fail: $FAIL${NC}"
echo "Full log: $LOG_FILE"

# Exit codes: 0=pass, 1=fail
if [ $FAIL -eq 0 ]; then
  exit 0
else
  exit 1
fi

