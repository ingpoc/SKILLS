#!/bin/bash
# TEMPLATE: health-check.sh
#
# Purpose: Fast health diagnosis - show the problem immediately
#
# ⚠️ CRITICAL: This script runs at the START of EVERY SESSION by orchestrator.
# NO TIME should be wasted finding root cause. Evolve this continuously.
#
# CUSTOMIZE THIS for your project:
# - Update ports for your services
# - Add/remove infrastructure checks (database, redis, etc.)
# - Add/remove log file locations
# - Adjust error patterns for your stack
# - Keep adding new failure patterns as you discover them
#
# Exit codes:
#   0 = healthy
#   1 = broken (shows error immediately)
#   2 = timeout

set -e

FRONTEND_PORT=3000
BACKEND_PORT=8000
LOG_DIR="logs"
ISSUES_FOUND=0

echo "=== Health Check ==="

# ============================================================================
# Check infrastructure FIRST (before services)
# This catches common issues BEFORE trying to check services
# ============================================================================

check_infrastructure() {
  echo ""
  echo "Checking infrastructure..."

  # 1. PostgreSQL database (uncomment if you use PostgreSQL)
  if command -v pg_isready >/dev/null 2>&1; then
    if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
      echo "✗ PostgreSQL not responding" >&2
      echo "" >&2
      echo "Fix:" >&2
      echo "  brew services start postgresql@15" >&2
      echo "  OR" >&2
      echo "  pg_ctl -D /opt/homebrew/var/postgresql@15 start" >&2
      ISSUES_FOUND=1
    else
      echo "✓ PostgreSQL is running"
    fi
  fi

  # 2. Redis (uncomment if you use Redis)
  # if command -v redis-cli >/dev/null 2>&1; then
  #   if ! redis-cli ping >/dev/null 2>&1; then
  #     echo "✗ Redis not responding" >&2
  #     echo "Fix: brew services start redis" >&2
  #     ISSUES_FOUND=1
  #   else
  #     echo "✓ Redis is running"
  #   fi
  # fi

  # 3. Disk space (prevent out-of-disk errors)
  local disk_usage=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
  if [ "$disk_usage" -gt 90 ]; then
    echo "✗ Disk space critically low: ${disk_usage}% used" >&2
    echo "Fix: Run 'docker system prune' or clean up node_modules" >&2
    ISSUES_FOUND=1
  elif [ "$disk_usage" -gt 80 ]; then
    echo "⚠ Disk space warning: ${disk_usage}% used" >&2
  else
    echo "✓ Disk space OK (${disk_usage}% used)"
  fi

  # 4. Required environment files
  echo ""
  echo "Checking environment files..."

  check_env_file() {
    local env_file=$1
    local example_file="$1.example"

    if [ ! -f "$env_file" ]; then
      echo "✗ Missing: $env_file" >&2
      if [ -f "$example_file" ]; then
        echo "Fix: cp $example_file $env_file" >&2
      fi
      ISSUES_FOUND=1
      return 1
    fi

    # Check for placeholder values
    if grep -qE "REPLACE_ME|your_key_here|TODO" "$env_file" 2>/dev/null; then
      echo "⚠ $env_file has unset placeholder values" >&2
    fi

    echo "✓ $(basename $env_file) exists"
  }

  # Customize these paths for your project
  check_env_file "gateway/.env"
  check_env_file "frontend/.env.local" 2>/dev/null || check_env_file "frontend/.env"

  # Exit if infrastructure issues found
  if [ $ISSUES_FOUND -eq 1 ]; then
    echo "" >&2
    echo "❌ Infrastructure check FAILED - fix above issues first" >&2
    exit 1
  fi
}

# Run infrastructure check
check_infrastructure

# ============================================================================
# Check service health (with immediate error diagnosis)
# ============================================================================

echo ""
echo "Checking services..."

check_service() {
  local url=$1
  local name=$2
  local log_file="$3"

  if curl -sf --max-time 2 "$url" > /dev/null 2>&1; then
    echo "✓ $name"
    return 0
  fi

  # Service is down - IMMEDIATELY show why
  echo "✗ $name is NOT responding" >&2

  # Show process status
  local process_name=""
  if [ "$name" = "Backend" ]; then
    process_name="uvicorn"
  elif [ "$name" = "Frontend" ]; then
    process_name="next dev"
  fi

  if [ -n "$process_name" ]; then
    if pgrep -f "$process_name" >/dev/null 2>&1; then
      echo "  Process '$process_name' is running but not responding on port" >&2
    else
      echo "  Process '$process_name' is NOT running" >&2
    fi
  fi

  # Show log errors RIGHT NOW if log exists
  if [ -f "$log_file" ]; then
    echo "" >&2
    echo "Recent errors from $log_file:" >&2
    echo "---" >&2
    tail -50 "$log_file" | grep -iE "error|fatal|exception|failed|refused|denied" | tail -10 >&2 || echo "  (no recent errors in log)" >&2
    echo "---" >&2
  fi

  # Suggest fix
  echo "" >&2
  if [ "$name" = "Backend" ]; then
    echo "Fix: cd gateway && uvicorn main:app --reload" >&2
    echo "Or:   ./.claude/scripts/restart-servers.sh" >&2
  else
    echo "Fix: cd frontend && npm run dev" >&2
    echo "Or:   ./.claude/scripts/restart-servers.sh" >&2
  fi

  return 1
}

# Check frontend
if ! check_service "http://localhost:$FRONTEND_PORT" "Frontend" "$LOG_DIR/frontend.log"; then
  echo "" >&2
  echo "❌ Health check FAILED" >&2
  exit 1
fi

# Check backend
if ! check_service "http://localhost:$BACKEND_PORT/api/health" "Backend" "$LOG_DIR/backend.log"; then
  echo "" >&2
  echo "❌ Health check FAILED" >&2
  exit 1
fi

# ============================================================================
# Scan logs for warnings (non-critical)
# ============================================================================

echo ""
echo "Checking logs for warnings..."

WARNINGS=0

check_warnings() {
  local log_file=$1
  local service_name=$2

  if [ ! -f "$log_file" ]; then
    return 0
  fi

  # Look for warnings (not errors - those would have caused failure)
  local warnings=$(grep -iE "warning|deprecated|slow" "$log_file" 2>/dev/null | tail -3 || true)

  if [ -n "$warnings" ]; then
    echo "⚠ $service_name has warnings:" >&2
    echo "$warnings" >&2
    WARNINGS=1
  fi
}

check_warnings "$LOG_DIR/frontend.log" "Frontend"
check_warnings "$LOG_DIR/backend.log" "Backend"

# ============================================================================
# Optional: Check Solana validator (uncomment if using Solana)
# ============================================================================

# echo ""
# echo "Checking Solana validator..."
# if ! solana ping -u localhost >/dev/null 2>&1; then
#   echo "⚠ Solana validator not running" >&2
#   echo "Fix: solana-test-validator" >&2
# fi

# ============================================================================
# Optional: Check MCP servers (if used in project)
# ============================================================================

echo ""
echo "Checking MCP servers..."

MCP_RUNNING=0
if pgrep -f "token-efficient-mcp" >/dev/null 2>&1; then
  echo "✓ token-efficient-mcp running"
  MCP_RUNNING=1
fi

if pgrep -f "context-graph-mcp" >/dev/null 2>&1; then
  echo "✓ context-graph-mcp running"
  MCP_RUNNING=1
fi

if [ $MCP_RUNNING -eq 0 ]; then
  echo "⚠ No MCP servers detected (may be OK if not needed)" >&2
fi

# ============================================================================
# Final result
# ============================================================================

echo ""
if [ $WARNINGS -eq 0 ]; then
  echo "✅ All systems healthy"
  exit 0
else
  echo "⚠️  Services running but warnings found"
  exit 0
fi
