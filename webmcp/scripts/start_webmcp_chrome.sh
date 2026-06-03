#!/usr/bin/env bash
set -euo pipefail

PORT="${CHROME_REMOTE_DEBUG_PORT:-9223}"
HOST="${CHROME_REMOTE_DEBUG_HOST:-127.0.0.1}"
START_URL="${WEBMCP_START_URL:-about:blank}"
BASE_DIR="${WEBMCP_SESSION_BASE:-${HOME}/.codex/webmcp-testing}"
SESSIONS_DIR="${BASE_DIR}/sessions"
LOGS_DIR="${BASE_DIR}/logs"

mkdir -p "$SESSIONS_DIR" "$LOGS_DIR"

session_dir="$(mktemp -d "${SESSIONS_DIR}/session-XXXXXXXX")"
chrome_log="${LOGS_DIR}/chrome-${PORT}.log"

find_chrome() {
  local candidate
  for candidate in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"
  do
    if [[ -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

cleanup() {
  if [[ -n "${chrome_pid:-}" ]] && kill -0 "${chrome_pid}" 2>/dev/null; then
    kill "${chrome_pid}" 2>/dev/null || true
    wait "${chrome_pid}" 2>/dev/null || true
  fi
  rm -rf "$session_dir"
}

trap cleanup EXIT INT TERM

if ! chrome_bin="$(find_chrome)"; then
  echo "Could not find a Chrome binary on this machine." >&2
  exit 1
fi

"$chrome_bin" \
  --user-data-dir="$session_dir" \
  --remote-debugging-address="$HOST" \
  --remote-debugging-port="$PORT" \
  --enable-features=WebMCPTesting \
  --no-first-run \
  --no-default-browser-check \
  --new-window \
  "$START_URL" >"$chrome_log" 2>&1 &
chrome_pid=$!

ready=0
for _ in $(seq 1 60); do
  if curl -fsS "http://${HOST}:${PORT}/json/version" >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 1
done

if [[ "$ready" -ne 1 ]]; then
  echo "WebMCP Chrome session failed to expose DevTools at http://${HOST}:${PORT}." >&2
  echo "Chrome log: ${chrome_log}" >&2
  exit 1
fi

printf 'session_dir=%s\n' "$session_dir"
printf 'chrome_log=%s\n' "$chrome_log"
printf 'browser_url=http://%s:%s\n' "$HOST" "$PORT"
printf 'start_url=%s\n' "$START_URL"
printf 'status=ready\n'

wait "${chrome_pid}"
