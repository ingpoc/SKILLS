#!/bin/bash
# session-entry.sh
#
# Session entry protocol for DESIGN-v2.
# Runs 3 phases: Safety → State → Context
# Outputs JSON for orchestrator to consume.

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-.}"
PROGRESS_DIR="$PROJECT_ROOT/.claude/progress"
CONFIG_FILE="$PROJECT_ROOT/.claude/config/project.json"

# Initialize outputs
HEALTH_STATUS="healthy"
CURRENT_STATE="START"
SESSION_SUMMARY=""
RECENT_FILES=()
UNCOMMITTED=false
BRANCH=""

# Phase 1: Safety
echo "=== Phase 1: Safety ===" >&2

# pwd
echo "Working directory: $PROJECT_ROOT" >&2

# git log
if git rev-parse --git-dir >/dev/null 2>&1; then
    BRANCH=$(git branch --show-current)
    echo "Git branch: $BRANCH" >&2
    git log -5 --oneline >&2 || true

    # Check for uncommitted changes
    if ! git diff --quiet || ! git diff --cached --quiet; then
        UNCOMMITTED=true
    fi
fi

# Health check from config
if [[ -f "$CONFIG_FILE" ]]; then
    HEALTH_CHECK=$(jq -r '.health_check // empty' "$CONFIG_FILE" 2>/dev/null)
    if [[ -n "$HEALTH_CHECK" ]]; then
        echo "Running health check..." >&2
        if eval "$HEALTH_CHECK" >/dev/null 2>&1; then
            echo "✓ Health check passed" >&2
        else
            echo "✗ Health check failed" >&2
            HEALTH_STATUS="broken"
        fi
    fi
fi

# Phase 2: State
echo "" >&2
echo "=== Phase 2: State ===" >&2

if [[ -f "$PROGRESS_DIR/state.json" ]]; then
    CURRENT_STATE=$(jq -r '.state // "START"' "$PROGRESS_DIR/state.json")
    echo "Current state: $CURRENT_STATE" >&2
else
    echo "No state file found, assuming START" >&2
fi

if [[ -f "$PROGRESS_DIR/feature-list.json" ]]; then
    PENDING=$(jq '[.features[] | select(.status=="pending")] | length' "$PROGRESS_DIR/feature-list.json")
    echo "Pending features: $PENDING" >&2
fi

# Phase 3: Context
echo "" >&2
echo "=== Phase 3: Context ===" >&2

if [[ -f "$PROGRESS_DIR/session-state.json" ]]; then
    SESSION_SUMMARY=$(jq -r '.session_summary // ""' "$PROGRESS_DIR/session-state.json")
    echo "Last session: $SESSION_SUMMARY" >&2
fi

# Recent files
if git rev-parse --git-dir >/dev/null 2>&1; then
    mapfile -t RECENT_FILES < <(git status --short | awk '{print $2}' | head -5)
    echo "Recent files: ${RECENT_FILES[*]}" >&2
fi

# Output JSON
jq -n \
    --arg health "$HEALTH_STATUS" \
    --arg state "$CURRENT_STATE" \
    --arg summary "$SESSION_SUMMARY" \
    --arg branch "$BRANCH" \
    --argjson files "$(printf '%s\n' "${RECENT_FILES[@]}" | jq -R 'split("\n") | map(select(length > 0))')" \
    --argjson uncommitted "$UNCOMMITTED" \
    '{
        health_status: $health,
        current_state: $state,
        session_summary: $summary,
        branch: $branch,
        recent_files: $files,
        uncommitted_changes: $uncommitted
    }'
