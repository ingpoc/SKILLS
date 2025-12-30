#!/bin/bash
# Run basic smoke test on URL
# Usage: smoke-test.sh [URL]
# Exit: 0 = pass, 1 = fail
# Config: .claude/config/project.json → dev_server_port (fallback if no URL)

EVIDENCE_DIR="/tmp/test-evidence"
mkdir -p "$EVIDENCE_DIR"

# ─────────────────────────────────────────────────────────────────
# Config helper (self-contained)
# ─────────────────────────────────────────────────────────────────
CONFIG="$PWD/.claude/config/project.json"
get_config() { jq -r ".$1 // empty" "$CONFIG" 2>/dev/null || echo "$2"; }

# ─────────────────────────────────────────────────────────────────
# Get URL (param → config → default)
# ─────────────────────────────────────────────────────────────────
URL=$1

if [ -z "$URL" ]; then
    PORT=$(get_config "dev_server_port" "3000")
    URL="http://localhost:$PORT"
    echo "No URL provided, using config: $URL"
fi

echo "=== Smoke Test: $URL ==="
ERRORS=0

# 1. Check HTTP reachability
echo "1. Checking HTTP..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$URL" 2>/dev/null || echo "000")
if [ "$STATUS" = "200" ]; then
    echo "   ✓ HTTP 200"
else
    echo "   ✗ HTTP $STATUS"
    ((ERRORS++))
fi

# 2. Check response time
echo "2. Checking response time..."
TIME=$(curl -s -o /dev/null -w "%{time_total}" --max-time 10 "$URL" 2>/dev/null || echo "0")
if (( $(echo "$TIME < 3.0" | bc -l 2>/dev/null || echo 1) )); then
    echo "   ✓ Response time: ${TIME}s"
else
    echo "   ⚠ Slow response: ${TIME}s"
fi

# 3. Check for basic HTML
echo "3. Checking content..."
CONTENT=$(curl -s --max-time 10 "$URL" 2>/dev/null | head -c 1000)
if echo "$CONTENT" | grep -q "<html\|<!DOCTYPE"; then
    echo "   ✓ Valid HTML response"
else
    echo "   ⚠ Non-HTML or empty response"
fi

# Save results
cat > "$EVIDENCE_DIR/smoke-test.json" << EOF
{
  "url": "$URL",
  "http_status": "$STATUS",
  "response_time": "$TIME",
  "passed": $([ $ERRORS -eq 0 ] && echo true || echo false)
}
EOF

[ $ERRORS -eq 0 ] && echo "=== PASSED ===" && exit 0
echo "=== FAILED ===" && exit 1
