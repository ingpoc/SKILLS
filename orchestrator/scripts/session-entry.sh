#!/bin/bash
# Session Entry Protocol - Merged from Skills + Anthropic Effective Harnesses
# Source: .skills/orchestrator/references/session-management.md

set -e

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR"

echo "=== SESSION ENTRY PROTOCOL ==="

# ─────────────────────────────────────────────────────────────────
# PHASE 1: Safety Validation (from Anthropic)
# ─────────────────────────────────────────────────────────────────

echo ""
echo "Phase 1: Safety Validation"

# 1.1 Verify working directory
echo -n "  [1/4] Directory: "
CURRENT_DIR=$(pwd)
if [ ! -f ".claude/progress/state.json" ] && [ ! -f "package.json" ] && [ ! -f "pyproject.toml" ] && [ ! -f "Cargo.toml" ]; then
    echo "WARNING - No project markers found in $CURRENT_DIR"
    echo "  Tip: Run from project root or pass path as argument"
else
    echo "OK ($CURRENT_DIR)"
fi

# 1.2 Git context (recent commits)
echo -n "  [2/4] Git context: "
if [ -d ".git" ]; then
    RECENT_COMMITS=$(git log --oneline -5 2>/dev/null || echo "none")
    echo "OK"
    echo "$RECENT_COMMITS" | sed 's/^/       /'
else
    echo "SKIP (not a git repo)"
fi

# 1.3 Load project config (if exists)
echo -n "  [3/4] Project config: "
if [ -f ".claude/config/project.json" ]; then
    HEALTH_CMD=$(jq -r '.health_check // empty' .claude/config/project.json)
    INIT_SCRIPT=$(jq -r '.init_script // empty' .claude/config/project.json)
    echo "OK (.claude/config/project.json)"
else
    HEALTH_CMD=""
    INIT_SCRIPT=""
    echo "SKIP (no project.json)"
fi

# 1.4 External dependencies check
echo -n "  [4/5] Dependencies: "
DEP_STATUS="OK"
DEP_CHECK_SCRIPT=".skills/initialization/scripts/check-dependencies.sh"

if [ -f "$DEP_CHECK_SCRIPT" ]; then
    DEP_RESULT=$("$DEP_CHECK_SCRIPT" --quiet 2>/dev/null || echo '{"status":"skipped"}')
    DEP_CHECK=$(echo "$DEP_RESULT" | tail -1 | jq -r '.status // "skipped"')

    if [ "$DEP_CHECK" = "failed" ]; then
        DEP_STATUS="MISSING"
        MISSING_ENV=$(echo "$DEP_RESULT" | tail -1 | jq -r '.error_list | join(", ")')
        echo "FAILED"
        echo ""
        echo "  ⚠️  Missing dependencies: $MISSING_ENV"
        echo "  Set required env vars before feature work"
        echo ""
    elif [ "$DEP_CHECK" = "warnings" ]; then
        DEP_STATUS="WARNINGS"
        echo "OK (with warnings)"
    else
        echo "OK"
    fi
else
    echo "SKIP (no check script)"
fi

# 1.5 Health check (verify app not broken)
echo -n "  [5/5] Health check: "
HEALTH_STATUS="UNKNOWN"

if [ -n "$HEALTH_CMD" ]; then
    # Use configured health check
    if eval "$HEALTH_CMD" > /dev/null 2>&1; then
        HEALTH_STATUS="HEALTHY"
        echo "OK (configured check passed)"
    else
        HEALTH_STATUS="BROKEN"
        echo "FAILED"
        echo ""
        echo "  ⚠️  APP IS BROKEN - Fix before starting new work"
        echo "  Health command: $HEALTH_CMD"
        echo ""
    fi
elif [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
    # Python: try smoke test
    if python -c "import sys; sys.exit(0)" 2>/dev/null; then
        HEALTH_STATUS="HEALTHY"
        echo "OK (Python imports work)"
    else
        HEALTH_STATUS="BROKEN"
        echo "FAILED (Python broken)"
    fi
elif [ -f "package.json" ]; then
    # Node: try syntax check
    if node -e "process.exit(0)" 2>/dev/null; then
        HEALTH_STATUS="HEALTHY"
        echo "OK (Node works)"
    else
        HEALTH_STATUS="BROKEN"
        echo "FAILED (Node broken)"
    fi
else
    echo "SKIP (no health check configured)"
fi

# ─────────────────────────────────────────────────────────────────
# PHASE 2: State Management (from Skills)
# ─────────────────────────────────────────────────────────────────

echo ""
echo "Phase 2: State Management"

# 2.1 Create progress directory
mkdir -p .claude/progress
mkdir -p .claude/config

# 2.2 Initialize state if not exists
echo -n "  [1/3] State: "
if [ ! -f .claude/progress/state.json ]; then
    cat > .claude/progress/state.json << EOF
{
  "state": "START",
  "entered_at": "$(date -Iseconds)",
  "health_status": "$HEALTH_STATUS",
  "history": []
}
EOF
    echo "CREATED (START)"
else
    CURRENT_STATE=$(jq -r '.state' .claude/progress/state.json)
    # Update health status
    jq --arg status "$HEALTH_STATUS" '.health_status = $status' .claude/progress/state.json > /tmp/state.tmp && mv /tmp/state.tmp .claude/progress/state.json
    echo "EXISTS ($CURRENT_STATE)"
fi

# 2.3 Check for feature list
echo -n "  [2/3] Features: "
if [ ! -f .claude/progress/feature-list.json ]; then
    echo "NONE (need INIT)"
    FEATURE_STATUS="NO_FEATURE_LIST"
else
    TOTAL=$(jq '.features | length' .claude/progress/feature-list.json)
    PENDING=$(jq '[.features[] | select(.status=="pending")] | length' .claude/progress/feature-list.json)
    COMPLETED=$(jq '[.features[] | select(.status=="tested" or .status=="completed")] | length' .claude/progress/feature-list.json)

    if [ "$PENDING" -gt 0 ]; then
        echo "PENDING ($PENDING of $TOTAL remaining)"
        FEATURE_STATUS="HAS_PENDING_FEATURES"
    else
        echo "COMPLETE ($COMPLETED of $TOTAL done)"
        FEATURE_STATUS="ALL_COMPLETE"
    fi
fi

# 2.4 Determine initial state
echo -n "  [3/3] Next state: "
CURRENT_STATE=$(jq -r '.state' .claude/progress/state.json 2>/dev/null || echo "START")

if [ "$HEALTH_STATUS" = "BROKEN" ]; then
    echo "FIX_BROKEN (health check failed)"
    NEXT_STATE="FIX_BROKEN"
elif [ "$FEATURE_STATUS" = "NO_FEATURE_LIST" ]; then
    echo "INIT (no features)"
    NEXT_STATE="INIT"
elif [ "$FEATURE_STATUS" = "HAS_PENDING_FEATURES" ]; then
    echo "IMPLEMENT (pending features)"
    NEXT_STATE="IMPLEMENT"
else
    echo "COMPLETE (all done)"
    NEXT_STATE="COMPLETE"
fi

# ─────────────────────────────────────────────────────────────────
# PHASE 3: Context Loading
# ─────────────────────────────────────────────────────────────────

echo ""
echo "Phase 3: Context Loading"

# 3.1 Load session summary (if exists)
echo -n "  [1/3] Summary: "
LATEST_SUMMARY=$(ls -t /tmp/summary/session_*.md 2>/dev/null | head -1)
if [ -n "$LATEST_SUMMARY" ]; then
    echo "FOUND ($LATEST_SUMMARY)"
else
    echo "NONE"
fi

# 3.2 Recent files
echo -n "  [2/3] Recent files: "
if [ -f ".claude/progress/file_history.json" ]; then
    RECENT_COUNT=$(jq 'length' .claude/progress/file_history.json)
    echo "TRACKED ($RECENT_COUNT files)"
elif [ -d ".git" ]; then
    RECENT_FILES=$(git diff --name-only HEAD~5 2>/dev/null | head -5 | tr '\n' ', ')
    echo "GIT (${RECENT_FILES%,})"
else
    echo "NONE"
fi

# 3.3 Skill to load
echo -n "  [3/3] Skill: "
case "$NEXT_STATE" in
    "INIT") echo "initialization/" ;;
    "IMPLEMENT") echo "implementation/" ;;
    "TEST") echo "testing/" ;;
    "FIX_BROKEN") echo "enforcement/ (fix broken app first)" ;;
    "COMPLETE") echo "context-graph/" ;;
    *) echo "orchestrator/" ;;
esac

# ─────────────────────────────────────────────────────────────────
# Output summary
# ─────────────────────────────────────────────────────────────────

echo ""
echo "=== ENTRY COMPLETE ==="
echo ""

# Return JSON for programmatic use
cat << EOF
{
  "directory": "$CURRENT_DIR",
  "health_status": "$HEALTH_STATUS",
  "dependency_status": "$DEP_STATUS",
  "feature_status": "$FEATURE_STATUS",
  "current_state": "$CURRENT_STATE",
  "next_state": "$NEXT_STATE",
  "latest_summary": "$LATEST_SUMMARY"
}
EOF
