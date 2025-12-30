#!/bin/bash
# prompt-project-config.sh
#
# Interactive script for creating .claude/config/project.json
# Prompts user for project-specific settings.

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-.}"
CONFIG_FILE="$PROJECT_ROOT/.claude/config/project.json"
CONFIG_DIR="$PROJECT_ROOT/.claude/config"

mkdir -p "$CONFIG_DIR"

echo "=== Project Configuration ==="
echo ""

# Project type
echo "Project type:"
echo "  1. fastapi"
echo "  2. django"
echo "  3. node/express"
echo "  4. python (other)"
echo "  5. other"
read -p "Select (1-5): " -r
echo

case $REPLY in
    1) PROJECT_TYPE="fastapi" ;;
    2) PROJECT_TYPE="django" ;;
    3) PROJECT_TYPE="node" ;;
    4) PROJECT_TYPE="python" ;;
    5) PROJECT_TYPE="other" ;;
    *) PROJECT_TYPE="other" ;;
esac

# Dev server port
read -p "Dev server port [8000]: " -r PORT
PORT=${PORT:-8000}

# Health check
DEFAULT_HEALTH="curl -sf http://localhost:$PORT/health"
read -p "Health check command [$DEFAULT_HEALTH]: " -r HEALTH
HEALTH=${HEALTH:-$DEFAULT_HEALTH}

# Test command
if [[ "$PROJECT_TYPE" == "python" || "$PROJECT_TYPE" == "fastapi" || "$PROJECT_TYPE" == "django" ]]; then
    DEFAULT_TEST="pytest"
elif [[ "$PROJECT_TYPE" == "node" ]]; then
    DEFAULT_TEST="npm test"
else
    DEFAULT_TEST="echo 'No tests configured'"
fi

read -p "Test command [$DEFAULT_TEST]: " -r TEST
TEST=${TEST:-$DEFAULT_TEST}

# Required env vars
echo ""
read -p "Required env vars (comma-separated, or press to skip): " -r ENVS
ENVS=${ENVS:-""}

# Required services
echo ""
read -p "Required services (e.g., 'redis://localhost:6379', or press to skip): " -r SERVICES
SERVICES=${SERVICES:-""}

# Build JSON arrays
if [[ -n "$ENVS" ]]; then
    ENV_ARRAY=$(echo "$ENVS" | tr ',' '\n' | jq -R 'split(",") | map(select(length > 0))')
else
    ENV_ARRAY="[]"
fi

if [[ -n "$SERVICES" ]]; then
    SERVICE_ARRAY=$(echo "$SERVICES" | tr ',' '\n' | jq -R 'split(",") | map(select(length > 0))')
else
    SERVICE_ARRAY="[]"
fi

# Create config
jq -n \
    --arg type "$PROJECT_TYPE" \
    --arg port "$PORT" \
    --arg health "$HEALTH" \
    --arg test "$TEST" \
    --argjson env "$ENV_ARRAY" \
    --argjson services "$SERVICE_ARRAY" \
    '{
        project_type: $type,
        dev_server_port: ($port | tonumber),
        health_check: $health,
        test_command: $test,
        required_env: $env,
        required_services: $services
    }' > "$CONFIG_FILE"

echo ""
echo "✅ Config created: $CONFIG_FILE"
cat "$CONFIG_FILE"
