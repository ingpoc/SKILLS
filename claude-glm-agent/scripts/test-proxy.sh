#!/bin/bash
# Test z.ai proxy connection
# Usage: ~/.claude/skills/claude-glm-agent/scripts/test-proxy.sh [--token=TOKEN]

set -e

# Parse arguments
TOKEN=""
for arg in "$@"; do
    case $arg in
        --token=*)
            TOKEN="${arg#*=}"
            shift
            ;;
    esac
done

BASE_URL="${ANTHROPIC_BASE_URL:-https://api.z.ai/api/anthropic}"

echo "=== z.ai Proxy Connection Test ==="
echo ""

# === 1. Get token if not provided ===
if [ -z "$TOKEN" ]; then
    # Try to load from .env files
    if [ -f ".env.local" ]; then
        TOKEN=$(grep "ANTHROPIC_AUTH_TOKEN=" .env.local | cut -d'=' -f2)
    elif [ -f ".env" ]; then
        TOKEN=$(grep "ANTHROPIC_AUTH_TOKEN=" .env | cut -d'=' -f2)
    fi

    if [ -z "$TOKEN" ]; then
        echo "Usage: $0 [--token=YOUR_ZAI_TOKEN]"
        echo ""
        echo "Token can be provided via:"
        echo "  - --token flag"
        echo "  - .env.local or .env file with ANTHROPIC_AUTH_TOKEN"
        exit 1
    fi
fi

# === 2. Test endpoint ===
echo "1. Testing connection to: $BASE_URL"
echo ""

# Test with a minimal messages API call
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/v1/messages" \
    -H "Content-Type: application/json" \
    -H "x-api-key: $TOKEN" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
        "model": "glm-4.7",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Hi"}]
    }' 2>/dev/null)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo "Response code: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo "✓ Connection successful!"
    echo ""
    echo "Response:"
    echo "$BODY" | head -c 500
    echo ""
    exit 0
elif [ "$HTTP_CODE" = "401" ]; then
    echo "❌ Authentication failed"
    echo ""
    echo "The provided token is invalid or expired."
    echo "Please check your z.ai token and try again."
    exit 1
elif [ "$HTTP_CODE" = "404" ]; then
    echo "❌ Endpoint not found"
    echo ""
    echo "The proxy endpoint may have changed."
    echo "Current BASE_URL: $BASE_URL"
    exit 1
elif [ "$HTTP_CODE" = "000" ]; then
    echo "❌ Connection failed"
    echo ""
    echo "Could not reach the proxy server."
    echo "Please check:"
    echo "  - Internet connection"
    echo "  - BASE_URL is correct: $BASE_URL"
    echo "  - Firewall/proxy settings"
    exit 1
else
    echo "⚠️  Unexpected response"
    echo ""
    echo "Response body:"
    echo "$BODY"
    exit 1
fi
