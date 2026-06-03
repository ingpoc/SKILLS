#!/bin/bash
# Phase 1: Server-Side Pre-Check
# Executes fast server-side checks before browser testing
# Exit codes: 0=pass, 1=fail, 2=timeout

set -e

APP_NAME="${1:-app}"
LOG_PATH="${2:-logs/$APP_NAME.log}"
HEALTH_URL="${3:-http://localhost:3000/api/health}"

echo "=== Phase 1: Server-Side Pre-Check for $APP_NAME ==="

# Check if log file exists
if [ ! -f "$LOG_PATH" ]; then
  echo "Warning: Log file not found at $LOG_PATH"
  echo "Proceeding with health check only..."
else
  echo "Checking logs for errors..."

  # Check for critical errors (last 50 lines)
  ERROR_COUNT=$(tail -50 "$LOG_PATH" | grep -c "ERROR" || true)
  WARN_COUNT=$(tail -50 "$LOG_PATH" | grep -c "WARN" || true)

  echo "Errors: $ERROR_COUNT, Warnings: $WARN_COUNT"

  if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "Recent errors found:"
    tail -50 "$LOG_PATH" | grep "ERROR" | tail -5
    echo "Exit code: 1 (fix server issues first)"
    exit 1
  fi
fi

# Health check
echo "Checking health endpoint: $HEALTH_URL"
if command -v curl &> /dev/null; then
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" || echo "000")

  if [ "$HTTP_CODE" = "200" ]; then
    echo "Health check: PASSED (200)"
    echo "Exit code: 0 (proceed to Phase 2)"
    exit 0
  elif [ "$HTTP_CODE" = "000" ]; then
    echo "Health check: TIMEOUT (connection failed)"
    echo "Exit code: 2 (server not responding)"
    exit 2
  else
    echo "Health check: FAILED ($HTTP_CODE)"
    echo "Exit code: 1 (server unhealthy)"
    exit 1
  fi
else
  echo "Warning: curl not found, skipping health check"
  echo "Exit code: 0 (proceed to Phase 2)"
  exit 0
fi
