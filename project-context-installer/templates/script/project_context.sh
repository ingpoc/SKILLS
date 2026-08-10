#!/usr/bin/env bash
set -eu

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_DIR="$REPO_ROOT/tools/project-context"

if command -v uv >/dev/null 2>&1; then
  exec uv run --project "$PROJECT_DIR" project-context --root "$REPO_ROOT" "$@"
fi

export PYTHONPATH="$PROJECT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m project_context.cli --root "$REPO_ROOT" "$@"
