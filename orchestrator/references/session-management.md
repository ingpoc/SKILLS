# Session Management Patterns

**Source**: Merged from Skills patterns + [Anthropic Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## Session Entry Protocol (Merged)

```
┌─────────────────────────────────────────────────────────────────┐
│  SESSION ENTRY PROTOCOL                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 1: Safety Validation (from Anthropic)                   │
│  ├── pwd → Verify in correct project directory                 │
│  ├── git log -5 → Load recent commit context                   │
│  └── Health check → Verify app not broken                      │
│       └── If broken → STOP, fix first (don't start new work)  │
│                                                                 │
│  PHASE 2: State Management (from Skills)                       │
│  ├── mkdir -p .claude/progress                                 │
│  ├── Initialize state.json if missing                          │
│  ├── Check feature-list.json                                   │
│  └── Determine initial state (START/INIT/IMPLEMENT/TEST)       │
│                                                                 │
│  PHASE 3: Context Loading (Merged)                             │
│  ├── Load session summary (if resuming)                        │
│  ├── Load recent files (last 5 from git or file_history.json)  │
│  └── Load appropriate skill for current state                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Entry Script (Complete)

```bash
#!/bin/bash
# scripts/session-entry.sh
# Merged: Anthropic safety validation + Skills state management

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

# 1.4 Health check (verify app not broken)
echo -n "  [4/4] Health check: "
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
  "feature_status": "$FEATURE_STATUS",
  "current_state": "$CURRENT_STATE",
  "next_state": "$NEXT_STATE",
  "latest_summary": "$LATEST_SUMMARY"
}
EOF
```

---

## Session Lifecycle (Updated)

```
┌─────────────────────────────────────────────────────────────────┐
│                    SESSION LIFECYCLE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [SESSION ENTRY] ← NEW: Run session-entry.sh                    │
│       │                                                          │
│       ├── Phase 1: Safety (pwd, git, health)                    │
│       ├── Phase 2: State (init files, check features)           │
│       ├── Phase 3: Context (summary, recent files, skill)       │
│       │                                                          │
│       └── If BROKEN → Fix first, don't start features           │
│                                                                  │
│  [ACTIVE SESSION]                                                │
│       │                                                          │
│       ├── Execute state procedures                               │
│       ├── Monitor context usage                                  │
│       ├── Compress when needed                                   │
│       ├── Git commit after each feature                         │
│       └── Transition states as conditions met                    │
│                                                                  │
│  [SESSION END]                                                   │
│       │                                                          │
│       ├── Update state.json (dirty: false)                      │
│       ├── Git commit with descriptive message                   │
│       ├── Write session summary                                  │
│       ├── Capture traces for learning                           │
│       └── Clean up temp files                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Configuration

Create `.claude/config/project.json` for project-specific settings:

```json
{
  "project_type": "fastapi",
  "init_script": "./scripts/dev-server.sh",
  "health_check": "curl -sf http://localhost:8000/health",
  "test_command": "pytest -q --tb=short",
  "smoke_test": "pytest tests/smoke/ -q",
  "dev_server_port": 8000,
  "required_env": ["DATABASE_URL"],
  "timeout_seconds": {
    "health_check": 5,
    "smoke_test": 60,
    "full_test": 300
  }
}
```

| Field | Purpose | Example |
|-------|---------|---------|
| `project_type` | Detected or specified | `fastapi`, `nextjs`, `django` |
| `init_script` | Dev server startup | `./init.sh` |
| `health_check` | Quick validation | `curl localhost:8000/health` |
| `smoke_test` | Pre-feature validation | `pytest tests/smoke/` |
| `test_command` | Full test suite | `pytest -q` |

---

## Broken State Handling

From Anthropic article: *"Verify app hasn't been left in broken state"*

```python
def handle_broken_state():
    """
    When health check fails, prioritize fixing over new features.
    """
    # 1. Don't start new feature work
    block_feature_work()

    # 2. Load last known good state
    last_commit = get_last_passing_commit()

    # 3. Show what broke
    print("App is broken. Recent changes:")
    show_git_diff(last_commit)

    # 4. Options
    print("Options:")
    print("  1. git reset --hard {last_commit}  # Rollback")
    print("  2. Fix the issue manually")
    print("  3. Skip health check (--force)")
```

### Hook: Block Feature Work When Broken

```python
#!/usr/bin/env python3
# .claude/hooks/block-if-broken.py
"""
Block new feature implementation if health check failed.
"""

import json
import sys
import os

def main():
    # Check if state shows broken
    state_file = ".claude/progress/state.json"
    if not os.path.exists(state_file):
        sys.exit(0)

    with open(state_file) as f:
        state = json.load(f)

    if state.get("health_status") == "BROKEN":
        input_data = json.load(sys.stdin)
        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")

        # Block edits to src/ when broken
        if "/src/" in file_path or file_path.startswith("src/"):
            print("BLOCKED: App is broken - fix health check first", file=sys.stderr)
            print("Run: ./scripts/session-entry.sh to see status", file=sys.stderr)
            sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Session State Recovery

When resuming a session:

```python
def recover_session():
    state = read_json(".claude/progress/state.json")

    # Check if previous session ended cleanly
    if state.get("dirty", False):
        # Crashed mid-operation
        rollback_to_last_known_good(state)

    # Check health before resuming
    if not run_health_check():
        state["health_status"] = "BROKEN"
        return "FIX_BROKEN"

    # Resume from current state
    return state.get("state", "START")
```

---

## Session Summary Generation

At session end, generate summary for continuity:

```markdown
# Session Summary - {timestamp}

## State
- Final state: [STATE]
- Health status: [HEALTHY/BROKEN]
- Features completed: [N]
- Features remaining: [M]

## Work Done
1. [Feature X] - Implemented and tested
2. [Feature Y] - Implementation complete, testing pending

## Git Commits
- abc1234: Implement user authentication
- def5678: Add login form validation

## Decisions Made
- [Decision 1]: [Rationale]
- [Decision 2]: [Rationale]

## Blockers
- [ ] [Blocker 1] - [Suggested resolution]

## Next Session
1. Run session-entry.sh first
2. Resume from state: [STATE]
3. Continue with feature: [FEATURE_ID]
4. Address blockers: [LIST]

## Files Modified
- [file1.py] - [summary]
- [file2.py] - [summary]
```

---

## Session Files

| File | Purpose | Lifetime |
|------|---------|----------|
| `state.json` | Current state, health status | Persistent |
| `feature-list.json` | All features with status | Persistent |
| `project.json` | Project configuration | Persistent |
| `file_history.json` | Recent file access | Persistent |
| `session-summary.md` | Last session summary | Per session |
| `/tmp/test-evidence/` | Test artifacts | Per session |

---

## Session Handoff (Cross-Session Continuity)

```python
def prepare_handoff():
    """Prepare context for next session"""

    # 1. Update state file
    update_state({
        "dirty": False,
        "last_action": get_last_action(),
        "timestamp": now()
    })

    # 2. Git commit (if changes)
    if has_uncommitted_changes():
        git_commit("Session checkpoint: " + get_session_summary())

    # 3. Generate summary
    summary = generate_session_summary()
    write_file("/tmp/summary/session_{timestamp}.md", summary)

    # 4. Capture learning traces
    capture_session_traces()

    # 5. Clean temp files (keep evidence)
    cleanup_temp_except(["test-evidence", "summary"])
```

---

## Auto-Save Checkpoints

```python
CHECKPOINT_INTERVAL = 300  # 5 minutes

def checkpoint():
    """Create recovery checkpoint"""
    save_state({
        "checkpoint_at": now(),
        "context_snapshot": get_context_summary(),
        "pending_actions": get_pending_actions()
    }, ".claude/progress/checkpoint.json")
```

---

## Session Metrics

Track for optimization:

| Metric | What to Track | Use |
|--------|---------------|-----|
| Duration | Total session time | Efficiency |
| States visited | Count per state | Flow analysis |
| Compressions | Count and triggers | Context management |
| Retries | Failed attempts | Quality issues |
| Tokens used | Total consumption | Cost optimization |
| Health checks | Pass/fail count | Stability |

```json
{
  "session_id": "uuid",
  "started_at": "2025-12-28T10:00:00Z",
  "ended_at": "2025-12-28T11:30:00Z",
  "health_status": "HEALTHY",
  "states_visited": ["START", "INIT", "IMPLEMENT", "TEST", "COMPLETE"],
  "compressions": 2,
  "retries": 1,
  "tokens_used": 45000,
  "features_completed": 3
}
```

---

## Error Recovery

| Error Type | Detection | Recovery |
|------------|-----------|----------|
| App broken | Health check fails | Fix before new work |
| Crash mid-state | `dirty: true` in state.json | Rollback to checkpoint |
| Hook rejection | Exit code 2 | Log, adjust, retry |
| Context overflow | 95% capacity | Emergency compression |
| Tool failure | Exception | Retry with backoff |
| Test timeout | No response > 5min | Kill, mark blocked |

```python
def recover_from_error(error_type: str):
    if error_type == "broken":
        # Health check failed
        show_recent_changes()
        suggest_rollback()

    elif error_type == "crash":
        state = load_checkpoint()
        log_recovery("Recovered from crash to checkpoint")

    elif error_type == "context_overflow":
        compress_context("emergency")
        log_recovery("Emergency compression applied")

    elif error_type == "tool_failure":
        retry_with_backoff(max_retries=3)
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./scripts/session-entry.sh` | Run full entry protocol |
| `./scripts/session-entry.sh /path/to/project` | Entry for specific project |
| `jq '.health_status' .claude/progress/state.json` | Check health status |
| `jq '.state' .claude/progress/state.json` | Check current state |

---

*Updated: 2025-12-28*
*Source: Merged from Skills + Anthropic Effective Harnesses article*
*Key addition: Safety validation phase (pwd, git, health check)*
