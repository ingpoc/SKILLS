#!/bin/bash
# Check external dependencies before starting work
# Reads from .claude/config/project.json
# Usage: ./check-dependencies.sh [--quiet]

set -e

QUIET="${1:-}"
CONFIG_FILE=".claude/config/project.json"

# Output helper
log() {
    if [ "$QUIET" != "--quiet" ]; then
        echo "$1"
    fi
}

log "=== DEPENDENCY CHECK ==="

# ─────────────────────────────────────────────────────────────────
# 0. Check MCP servers first (agent-harness requires token-efficient + context-graph)
# ─────────────────────────────────────────────────────────────────

log ""
log "Checking MCP servers..."

# Find and run mcp-setup verification if available
MCP_VERIFY_SCRIPT=""
for path in \
    "$HOME/.claude/skills/mcp-setup/scripts/verify-setup.sh" \
    "../../.skills/mcp-setup/scripts/verify-setup.sh" \
    ".skills/mcp-setup/scripts/verify-setup.sh"
do
    if [ -f "$path" ]; then
        MCP_VERIFY_SCRIPT="$path"
        break
    fi
done

if [ -n "$MCP_VERIFY_SCRIPT" ]; then
    log "  Running MCP setup verification..."
    # Temporarily disable set -e for command substitution
    set +e
    MCP_OUTPUT=$(bash "$MCP_VERIFY_SCRIPT" 2>&1)
    MCP_EXIT_CODE=$?
    set -e

    # Just show all output from MCP verification
    echo "$MCP_OUTPUT" | while IFS= read -r line; do
        log "    $line"
    done

    # Check if MCP verification passed (exit code 0 = success)
    if [ $MCP_EXIT_CODE -ne 0 ]; then
        ERRORS+=("MCP servers verification failed - run mcp-setup skill")
    fi
else
    log "  Note: mcp-setup skill not found - skipping MCP check"
fi

# Check if config exists
if [ ! -f "$CONFIG_FILE" ]; then
    log "No project.json found - skipping dependency check"
    echo '{"status": "skipped", "reason": "no config"}'
    exit 0
fi

ERRORS=()
WARNINGS=()

# ─────────────────────────────────────────────────────────────────
# 1. Check required environment variables
# ─────────────────────────────────────────────────────────────────

log ""
log "Checking environment variables..."

REQUIRED_ENV=$(jq -r '.required_env // [] | .[]' "$CONFIG_FILE" 2>/dev/null)

for VAR in $REQUIRED_ENV; do
    if [ -z "${!VAR:-}" ]; then
        ERRORS+=("Missing env var: $VAR")
        log "  ✗ $VAR - NOT SET"
    else
        # Check if it looks like a placeholder
        VALUE="${!VAR}"
        if [[ "$VALUE" == *"your_"* ]] || [[ "$VALUE" == *"TODO"* ]] || [[ "$VALUE" == *"changeme"* ]]; then
            WARNINGS+=("Env var looks like placeholder: $VAR")
            log "  ⚠ $VAR - SET (but looks like placeholder)"
        else
            log "  ✓ $VAR - SET"
        fi
    fi
done

# ─────────────────────────────────────────────────────────────────
# 2. Check init script exists
# ─────────────────────────────────────────────────────────────────

log ""
log "Checking init script..."

INIT_SCRIPT=$(jq -r '.init_script // empty' "$CONFIG_FILE")

if [ -n "$INIT_SCRIPT" ]; then
    if [ -f "$INIT_SCRIPT" ]; then
        if [ -x "$INIT_SCRIPT" ]; then
            log "  ✓ $INIT_SCRIPT - exists and executable"
        else
            WARNINGS+=("Init script not executable: $INIT_SCRIPT")
            log "  ⚠ $INIT_SCRIPT - exists but not executable"
        fi
    else
        ERRORS+=("Init script not found: $INIT_SCRIPT")
        log "  ✗ $INIT_SCRIPT - NOT FOUND"
    fi
else
    log "  - No init script configured"
fi

# ─────────────────────────────────────────────────────────────────
# 3. Check dev server port availability
# ─────────────────────────────────────────────────────────────────

log ""
log "Checking port availability..."

DEV_PORT=$(jq -r '.dev_server_port // empty' "$CONFIG_FILE")

if [ -n "$DEV_PORT" ]; then
    if lsof -i ":$DEV_PORT" > /dev/null 2>&1; then
        # Port in use - might be our dev server already running
        WARNINGS+=("Port $DEV_PORT already in use")
        log "  ⚠ Port $DEV_PORT - IN USE (dev server running?)"
    else
        log "  ✓ Port $DEV_PORT - available"
    fi
else
    log "  - No dev server port configured"
fi

# ─────────────────────────────────────────────────────────────────
# 4. Check database connectivity (if configured)
# ─────────────────────────────────────────────────────────────────

log ""
log "Checking database..."

DB_URL="${DATABASE_URL:-}"

if [ -n "$DB_URL" ]; then
    # Try to parse and check connectivity
    if [[ "$DB_URL" == postgresql://* ]] || [[ "$DB_URL" == postgres://* ]]; then
        if command -v pg_isready > /dev/null 2>&1; then
            if pg_isready -d "$DB_URL" > /dev/null 2>&1; then
                log "  ✓ PostgreSQL - connected"
            else
                WARNINGS+=("PostgreSQL not reachable")
                log "  ⚠ PostgreSQL - not reachable (may need to start)"
            fi
        else
            log "  - PostgreSQL URL set (pg_isready not available for check)"
        fi
    elif [[ "$DB_URL" == sqlite://* ]] || [[ "$DB_URL" == *.db ]] || [[ "$DB_URL" == *.sqlite* ]]; then
        # SQLite - check if file exists
        DB_PATH="${DB_URL#sqlite:///}"
        if [ -f "$DB_PATH" ]; then
            log "  ✓ SQLite - file exists: $DB_PATH"
        else
            log "  - SQLite - file will be created: $DB_PATH"
        fi
    else
        log "  - Database URL configured"
    fi
else
    log "  - No DATABASE_URL configured"
fi

# ─────────────────────────────────────────────────────────────────
# 5. Check external services (optional)
# ─────────────────────────────────────────────────────────────────

log ""
log "Checking external services..."

REQUIRED_SERVICES=$(jq -r '.required_services // [] | .[]' "$CONFIG_FILE" 2>/dev/null)

for SERVICE in $REQUIRED_SERVICES; do
    # Extract host:port from service URL
    HOST=$(echo "$SERVICE" | sed -E 's|.*://||' | cut -d'/' -f1 | cut -d':' -f1)
    PORT=$(echo "$SERVICE" | sed -E 's|.*://||' | cut -d'/' -f1 | cut -d':' -f2)

    if [ -n "$PORT" ]; then
        if nc -z "$HOST" "$PORT" 2>/dev/null; then
            log "  ✓ $SERVICE - reachable"
        else
            WARNINGS+=("Service not reachable: $SERVICE")
            log "  ⚠ $SERVICE - not reachable"
        fi
    else
        log "  - $SERVICE (no port to check)"
    fi
done

if [ -z "$REQUIRED_SERVICES" ]; then
    log "  - No required services configured"
fi

# ─────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────

log ""
log "=== SUMMARY ==="

ERROR_COUNT=${#ERRORS[@]}
WARNING_COUNT=${#WARNINGS[@]}

if [ $ERROR_COUNT -gt 0 ]; then
    log ""
    log "ERRORS ($ERROR_COUNT):"
    for err in "${ERRORS[@]}"; do
        log "  ✗ $err"
    done
fi

if [ $WARNING_COUNT -gt 0 ]; then
    log ""
    log "WARNINGS ($WARNING_COUNT):"
    for warn in "${WARNINGS[@]}"; do
        log "  ⚠ $warn"
    done
fi

log ""

# Output JSON
if [ $ERROR_COUNT -gt 0 ]; then
    STATUS="failed"
    EXIT_CODE=1
elif [ $WARNING_COUNT -gt 0 ]; then
    STATUS="warnings"
    EXIT_CODE=0
else
    STATUS="passed"
    EXIT_CODE=0
fi

log "Status: $STATUS"

# JSON output for programmatic use
cat << EOF
{
  "status": "$STATUS",
  "errors": $ERROR_COUNT,
  "warnings": $WARNING_COUNT,
  "error_list": $(printf '%s\n' "${ERRORS[@]}" | jq -R . | jq -s .),
  "warning_list": $(printf '%s\n' "${WARNINGS[@]}" | jq -R . | jq -s .)
}
EOF

exit $EXIT_CODE
