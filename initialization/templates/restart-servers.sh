#!/bin/bash
# TEMPLATE: restart-servers.sh
#
# Purpose: Kill processes on specified ports and restart frontend/backend servers
#
# CUSTOMIZE THIS for your project:
# - Update ports for your services
# - Update start commands for your stack
# - Add additional services as needed
#
# Usage: ./restart-servers.sh [--no-frontend|--no-backend]

set -e

FRONTEND_PORT=3000
BACKEND_PORT=8000
NO_FRONTEND=false
NO_BACKEND=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --no-frontend)
      NO_FRONTEND=true
      shift
      ;;
    --no-backend)
      NO_BACKEND=true
      shift
      ;;
    *)
      echo "Usage: $0 [--no-frontend] [--no-backend]"
      exit 1
      ;;
  esac
done

echo "=== Restarting Servers ==="

# ============================================================================
# Kill existing processes
# ============================================================================

kill_port() {
  local port=$1
  local pid=$(lsof -ti:$port 2>/dev/null || true)

  if [ -n "$pid" ]; then
    echo "Killing process on port $port (PID: $pid)"
    kill -9 $pid 2>/dev/null || true
    sleep 1
  else
    echo "No process found on port $port"
  fi
}

if [ "$NO_FRONTEND" = false ]; then
  kill_port $FRONTEND_PORT
fi

if [ "$NO_BACKEND" = false ]; then
  kill_port $BACKEND_PORT
fi

# ============================================================================
# Start backend (FastAPI)
# ============================================================================

if [ "$NO_BACKEND" = false ]; then
  echo ""
  echo "Starting backend on port $BACKEND_PORT..."

  if [ -d "gateway" ]; then
    cd gateway
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend started (PID: $BACKEND_PID, logs: logs/backend.log)"
    cd ..
  else
    echo "Warning: gateway/ directory not found, skipping backend" >&2
  fi
fi

# ============================================================================
# Start frontend (Next.js)
# ============================================================================

if [ "$NO_FRONTEND" = false ]; then
  echo ""
  echo "Starting frontend on port $FRONTEND_PORT..."

  if [ -d "frontend" ]; then
    cd frontend
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend started (PID: $FRONTEND_PID, logs: logs/frontend.log)"
    cd ..
  else
    echo "Warning: frontend/ directory not found, skipping frontend" >&2
  fi
fi

# ============================================================================
# Wait for servers to be ready
# ============================================================================

echo ""
echo "Waiting for servers to start..."

wait_for_service() {
  local url=$1
  local name=$2
  local max_wait=30
  local count=0

  while [ $count -lt $max_wait ]; do
    if curl -sf "$url" > /dev/null 2>&1; then
      echo "✓ $name is ready"
      return 0
    fi
    sleep 1
    count=$((count + 1))
    echo -n "."
  done

  echo ""
  echo "✗ $name failed to start within ${max_wait}s" >&2
  return 1
}

if [ "$NO_FRONTEND" = false ]; then
  wait_for_service "http://localhost:$FRONTEND_PORT" "Frontend" || exit 1
fi

if [ "$NO_BACKEND" = false ]; then
  wait_for_service "http://localhost:$BACKEND_PORT/api/health" "Backend" || exit 1
fi

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "=== Servers restarted successfully ==="
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "Backend:  http://localhost:$BACKEND_PORT/api/health"
echo "Logs:     logs/frontend.log, logs/backend.log"

exit 0
