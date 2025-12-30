#!/bin/bash
# Run health check for dev server
# Exit: 0 = healthy, 1 = unhealthy
# Config: .claude/config/project.json → health_check, dev_server_port

# ─────────────────────────────────────────────────────────────────
# Config helper (self-contained)
# ─────────────────────────────────────────────────────────────────
CONFIG="$PWD/.claude/config/project.json"
get_config() { jq -r ".$1 // empty" "$CONFIG" 2>/dev/null || echo "$2"; }

# ─────────────────────────────────────────────────────────────────
# Get health check command from config
# ─────────────────────────────────────────────────────────────────
PORT=$(get_config "dev_server_port" "3000")
HEALTH_CMD=$(get_config "health_check" "")

if [ -z "$HEALTH_CMD" ]; then
    # Default: try /health then /
    HEALTH_CMD="curl -sf http://localhost:$PORT/health || curl -sf http://localhost:$PORT/"
fi

# ─────────────────────────────────────────────────────────────────
# Run health check
# ─────────────────────────────────────────────────────────────────
echo "=== Health Check ==="
echo "Command: $HEALTH_CMD"

if eval "$HEALTH_CMD" > /dev/null 2>&1; then
    echo "✓ Server healthy on port $PORT"
    exit 0
else
    echo "✗ Server not responding on port $PORT"
    exit 1
fi
