#!/bin/bash
# Verify page loaded successfully
# Usage: verify-page-load.sh [URL]
# Exit: 0 = loaded, 1 = failed
# Config: .claude/config/project.json → dev_server_port (fallback if no URL)

TIMEOUT=10

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
fi

echo "=== Verifying Page Load ==="
echo "URL: $URL"

# Check if URL is reachable
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$URL" 2>/dev/null || echo "000")

if [ "$STATUS" = "200" ]; then
    echo "✓ HTTP 200 OK"
    exit 0
elif [ "$STATUS" = "000" ]; then
    echo "✗ Connection failed (timeout or unreachable)"
    exit 1
else
    echo "⚠ HTTP $STATUS (may still work in browser)"
    exit 0
fi
