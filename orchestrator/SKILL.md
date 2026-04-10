---
name: orchestrator
description: "State machine management for session lifecycle. Auto-loads on session start via hook. Ensures dev environment is healthy (runs health-check + auto-restart). Use for state transitions, compression triggers, and skill handoff: automatically loads implementation/testing/context-graph skills based on state. Load at end of initialization skill completion."
context: fork
agent: general-purpose
---

# Orchestrator

Session lifecycle management. **Auto-loaded via UserPromptSubmit hook** - no manual invocation needed.

## Session Entry Protocol (MANDATORY)

**Every session MUST verify dev environment before starting work. Fully autonomous — no human prompts.**

```bash
# 0. Check prerequisites
command -v jq >/dev/null 2>&1 || { echo "Error: jq required but not installed"; exit 1; }

# 1. Health check first (check if script exists first)
if [ -f ".claude/scripts/health-check.sh" ]; then
  if ! .claude/scripts/health-check.sh; then
    echo "Health check failed - attempting auto-fix..."

    # 2. Common auto-fixes (try in order)
    # Missing deps
    [ -f "package.json" ] && [ ! -d "node_modules" ] && npm install
    [ -f "requirements.txt" ] && pip install -r requirements.txt -q

    # Port conflict
    PORT=$(jq -r '.dev_server_port // 3000' .claude/config/project.json 2>/dev/null)
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true

    # Restart servers (check if script exists)
    [ -f ".claude/scripts/restart-servers.sh" ] && .claude/scripts/restart-servers.sh 2>/dev/null || true

    # 3. Re-check after auto-fix
    if ! .claude/scripts/health-check.sh; then
      echo "⚠️ Auto-fix failed — transitioning to FIX_BROKEN state"
      ~/.claude/skills/orchestrator/scripts/enter-state.sh FIX_BROKEN
      # Agent will diagnose and fix based on health-check error output
      # After fixing, transition to INIT or IMPLEMENT
    fi
  fi
else
  echo "⚠️ No health-check.sh found - skipping health check"
fi

echo "✅ Dev environment healthy - proceeding with session"
```

## Template Gate (Autonomous)

Before any state-based work, verify scripts are customized:

```bash
# Check if there are any template scripts to customize
TEMPLATES=$(ls .claude/scripts/TEMPLATE-*.sh 2>/dev/null)
if [ -n "$TEMPLATES" ]; then
  echo "⚠️  Uncustomized template scripts detected:"
  echo "$TEMPLATES"

  # Check if project.json exists
  if [ ! -f ".claude/config/project.json" ]; then
    echo "Error: project.json not found - cannot auto-customize templates"
  else
    echo "Auto-customizing based on project.json..."

    # Auto-customize using project.json values (check jq availability)
    if command -v jq >/dev/null 2>&1; then
      PROJECT_TYPE=$(jq -r '.project_type' .claude/config/project.json)
      TEST_CMD=$(jq -r '.test_command' .claude/config/project.json)
      PORT=$(jq -r '.dev_server_port // 3000' .claude/config/project.json)
      HEALTH=$(jq -r '.health_check // ""' .claude/config/project.json)

      for tmpl in .claude/scripts/TEMPLATE-*.sh; do
        base=$(basename "$tmpl" | sed 's/TEMPLATE-//')
        sed -e "s|__TEST_CMD__|$TEST_CMD|g" \
            -e "s|__PORT__|$PORT|g" \
            -e "s|__HEALTH_CHECK__|$HEALTH|g" \
            "$tmpl" > ".claude/scripts/$base"
        chmod +x ".claude/scripts/$base"
        rm "$tmpl"
      done
      echo "✅ Scripts auto-customized"
    else
      echo "Error: jq required but not installed"
    fi
  fi
fi
```

**Why**: For autonomous operation, templates must be auto-customized — no human to rename them.

**Auto-fix strategy (no human prompts):**

| Problem | Auto-fix |
|---------|----------|
| Server down | Kill port conflict + restart-servers.sh |
| Missing deps | `npm install` / `pip install` |
| Missing .env | Copy from .env.example if exists |
| Disk full | `docker system prune` / clean node_modules |

**Scripts used:**

| Script | Purpose | Source |
|--------|---------|--------|
| `health-check.sh` | Verify dev servers running | `.claude/scripts/` (customized per project) |
| `restart-servers.sh` | Restart dev servers | `.claude/scripts/` (customized per project) |

## State Machine

| State | Next | Trigger |
|-------|------|---------|
| START | INIT, FIX_BROKEN, IMPLEMENT | First session, broken env, or feature-list exists |
| FIX_BROKEN | INIT, IMPLEMENT | Environment fixed after auto-repair |
| INIT | IMPLEMENT | feature-list.json created |
| IMPLEMENT | TEST | Feature code complete + all checks pass |
| TEST | IMPLEMENT or COMPLETE | Tests pass/fail |
| COMPLETE | IMPLEMENT | Next feature cycle (if pending features remain) |

## Handling Broken Environment (Autonomous)

When health check fails after auto-fix attempt, agent enters FIX_BROKEN state:

```bash
# In FIX_BROKEN state, agent autonomously:
# 1. Read health-check.sh output to identify specific error
# 2. Query context graph for similar past failures
# 3. Apply fix based on error pattern
# 4. Re-run health check
# 5. If fixed → transition to INIT or IMPLEMENT
# 6. If still broken after 3 attempts → log failure trace and halt

MAX_FIX_ATTEMPTS=3
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_FIX_ATTEMPTS ]; do
  ATTEMPT=$((ATTEMPT + 1))
  echo "Fix attempt $ATTEMPT/$MAX_FIX_ATTEMPTS"
  
  # Capture error output
  ERROR=$(.claude/scripts/health-check.sh 2>&1) || true
  
  # Auto-diagnose and fix based on error patterns
  case "$ERROR" in
    *"Address already in use"*)
      lsof -ti:$PORT | xargs kill -9 2>/dev/null ;;
    *"Module not found"*|*"node_modules"*)
      npm install 2>/dev/null || pip install -r requirements.txt 2>/dev/null ;;
    *"Connection refused"*)
      .claude/scripts/restart-servers.sh ;;
    *"Missing"*".env"*)
      [ -f ".env.example" ] && cp .env.example .env ;;
  esac
  
  if .claude/scripts/health-check.sh; then
    echo "✅ Fixed on attempt $ATTEMPT"
    # Transition to appropriate state (check if enter-state.sh exists)
    if [ -f "~/.claude/skills/orchestrator/scripts/enter-state.sh" ]; then
      if [ -f ".claude/progress/feature-list.json" ]; then
        ~/.claude/skills/orchestrator/scripts/enter-state.sh IMPLEMENT
      else
        ~/.claude/skills/orchestrator/scripts/enter-state.sh INIT
      fi
    else
      echo "Error: enter-state.sh not found"
    fi
    break
  fi
done

if [ $ATTEMPT -ge $MAX_FIX_ATTEMPTS ]; then
  echo "❌ Environment unfixable after $MAX_FIX_ATTEMPTS attempts"
  # Store failure trace for future learning
  context_store_trace(
    decision="Environment broken: $ERROR. Auto-fix failed after $MAX_FIX_ATTEMPTS attempts",
    category="troubleshooting",
    outcome="failure"
  )
fi
```

## Manual Actions (Rare)

| Action | Command |
|--------|---------|
| Check state | `cat .claude/progress/state.json` |
| Force transition | `~/.claude/skills/orchestrator/scripts/enter-state.sh NEW_STATE` |
| Run session entry | `~/.claude/skills/orchestrator/scripts/session-entry.sh` |

## Maintaining CLAUDE.md

**⚠️ CRITICAL: If you need to update CLAUDE.md files after initial creation, always use the `claude-md-creator` skill.**

| Scenario | Action |
|----------|--------|
| Update project architecture | Run `claude-md-creator` skill |
| Customize quick reference | Run `claude-md-creator` skill |
| Add framework-specific docs | Run `claude-md-creator` skill |
| Manual edits | ❌ Never - use `claude-md-creator` instead |

**Why**: claude-md-creator validates structure, enforces line count targets, and maintains consistency across all CLAUDE.md files.

---

## State-Based Skill Loading

At end of orchestrator session, check state and load appropriate skill:

| Current State | Load Skill | Purpose |
|---------------|-----------|---------|
| FIX_BROKEN | (auto-repair) | Diagnose and fix environment |
| IMPLEMENT | implementation/ | Feature development workflow |
| TEST | testing/ | Test execution and verification |
| COMPLETE | context-graph/ | Extract patterns and learning |
| START or INIT | initialization/ | Project setup |

### Implementation

**At end of orchestrator workflow:**

```bash
# 1. Get current state (check if state file exists first)
if [ -f ".claude/progress/state.json" ]; then
  CURRENT_STATE=$(jq -r '.state' .claude/progress/state.json)
else
  CURRENT_STATE="START"
fi

# 2. Load appropriate skill based on state
case "$CURRENT_STATE" in
  FIX_BROKEN)
    echo "State is FIX_BROKEN - running auto-repair..."
    # Agent diagnoses and fixes environment (see Handling Broken Environment above)
    # After fix, transitions to INIT or IMPLEMENT automatically
    ;;
  INIT)
    echo "State is INIT - running initialization skill..."
    Skill: initialization
    ;;
  IMPLEMENT)
    echo "State is IMPLEMENT - running implementation skill..."
    Skill: implementation
    ;;
  TEST)
    echo "State is TEST - running testing skill..."
    Skill: testing
    ;;
  COMPLETE)
    # Check if more pending features exist
    if [ -f ".claude/progress/feature-list.json" ]; then
      PENDING=$(jq '[.features[] | select(.status=="pending")] | length' .claude/progress/feature-list.json 2>/dev/null)
    else
      PENDING=0
    fi
    if [ "$PENDING" -gt 0 ]; then
      echo "State is COMPLETE but $PENDING features pending - cycling to IMPLEMENT..."
      # Transition back to IMPLEMENT for next feature
      ~/.claude/skills/orchestrator/scripts/enter-state.sh IMPLEMENT
      Skill: implementation
    else
      echo "State is COMPLETE - all features done. Running context-graph skill..."
      Skill: context-graph
    fi
    ;;
  *)
    echo "State: $CURRENT_STATE - manual action required"
    ;;
esac
```

**Why this matters:**

- ✅ Seamless workflow: Each skill hands off to next
- ✅ State machine enforced: Cannot skip phases
- ✅ Zero context waste: Skills load already knowing the state
- ✅ User stays in flow: No manual skill invocation needed

---

## Compression Triggers

| Context % | Action |
|-----------|--------|
| 50% | Checkpoint to /tmp/summary/ |
| 70% | Compress completed work |
| 80% | Aggressive compression |
| 85%+ | Emergency: summarize and checkpoint |

## References

| File | When |
|------|------|
| references/state-machine.md | State transition rules |
| references/compression.md | Context management |
| references/session-resumption.md | Resume from summary |
