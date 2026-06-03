# Project Automation Scripts

## ⚠️ TEMPLATE- Prefix Convention

Scripts are copied with a `TEMPLATE-` prefix to signal they need customization.

**You cannot use a script until you customize and rename it.**

### Workflow

```bash
# 1. Check for uncustomized scripts
ls .claude/scripts/TEMPLATE-*.sh

# 2. For each TEMPLATE- script:
#    a. Review the script
#    b. Customize for your project
#    c. Rename to remove prefix
mv .claude/scripts/TEMPLATE-health-check.sh .claude/scripts/health-check.sh

# 3. Test the script works
.claude/scripts/health-check.sh

# 4. Commit customized scripts
git add .claude/scripts/
git commit -m "customize: project scripts for [your-project]"
```

### Why This Convention?

- **Prevents using uncustomized scripts** - TEMPLATE- prefix means "not ready"
- **Forces review** - You must read and understand each script
- **Clear status** - Easy to see which scripts still need work
- **No silent failures** - Running `TEMPLATE-*.sh` will fail (file not found)

---

## Overview

These scripts customize the Claude Code workflow for this project. They are copied during initialization and should be customized to match your project architecture.

## Scripts

### get-current-feature.sh

**Purpose:** Extract the next pending feature from `.claude/progress/feature-list.json`

**Output:** JSON with feature details

```json
{
  "id": "feat-013",
  "description": "Feature description",
  "priority": "P0",
  "status": "pending",
  "acceptance_criteria": [...]
}
```

**Customize for:**

- Monorepo structure (multiple feature lists)
- Custom feature ordering logic
- Filtering by priority, phase, or tags

**Default:** Returns first pending feature from feature-list.json

---

### health-check.sh

**Purpose:** Fast health diagnosis - show root cause immediately

**⚠️ CRITICAL:** This script runs at the START of EVERY SESSION by orchestrator.
**NO TIME should be wasted finding root cause.** Evolve this continuously.

**Exit codes:**

- `0` = All systems healthy
- `1` = Infrastructure/service failed (shows error immediately)
- `2` = Timeout

**Checks (in order - fails fast on infrastructure):**

1. **Infrastructure FIRST** (before services):
   - PostgreSQL database running
   - Disk space (prevent out-of-disk errors)
   - Required environment files exist

2. **Services:**
   - Frontend health endpoint (:3000)
   - Backend health endpoint (:8000/api/health)
   - Process status (running vs not responding)

3. **Logs:**
   - Recent errors from log files
   - Warnings (non-critical)

4. **Optional:**
   - MCP servers running

**Examples:**

```bash
# All healthy
./.claude/scripts/health-check.sh
# ✅ All systems healthy

# Database down - IMMEDIATE diagnosis
./.claude/scripts/health-check.sh
# ✗ PostgreSQL not responding
#
# Fix:
#   brew services start postgresql@15
# ❌ Infrastructure check FAILED

# Backend failed - shows WHY instantly
./.claude/scripts/health-check.sh
# ✗ Backend is NOT responding
#   Process 'uvicorn' is NOT running
#
# Recent errors from logs/backend.log:
# ---
# ConnectionRefusedError: [Errno 61] Connection refused
# Database initialization failed
# ---
```

**Customize for:**

- Your infrastructure (Redis, Solana validator, etc.)
- Your services (ports, health endpoints)
- Your log file locations
- Your environment file paths
- **Keep evolving this - add new failure patterns as you discover them**

---

### run-tests.sh

**Purpose:** Run project tests (unit tests, API tests, etc.)

**Usage:**

```bash
./.claude/scripts/run-tests.sh                    # Run all tests
./.claude/scripts/run-tests.sh --coverage         # With coverage
./.claude/scripts/run-tests.sh --watch            # Watch mode
```

**Exit codes:**

- `0` = All tests passed
- `1` = One or more tests failed

**⚠️ REQUIRES CUSTOMIZATION:**

Template is generic. Customize for your test framework:

- **Jest/Vitest:** `pnpm test -- --run`
- **Pytest:** `pytest -v`
- **Go:** `go test ./...`
- **API tests:** Add endpoint testing

**Customize for:**

- Your test framework and commands
- Coverage requirements
- Test file patterns
- CI/CD integration

---

### restart-servers.sh

**Purpose:** Build/restart development servers

**Usage:**

```bash
./.claude/scripts/restart-servers.sh              # Full restart
./.claude/scripts/restart-servers.sh --build-only # Just build
```

**⚠️ REQUIRES CUSTOMIZATION:**

Different project types need different commands:

- **Monorepo:** `pnpm build && pnpm typecheck`
- **Frontend/Backend:** Kill ports, start servers
- **Docker:** `docker-compose restart`

**Customize for:**

- Your build commands
- Your service ports
- Your start commands
- Log file locations

---

### feature-commit.sh

**Purpose:** Commit changes with feature ID in commit message

**Usage:**

```bash
.claude/scripts/feature-commit.sh feat-013 "Implemented DID registry"
```

**Customize for:**

- Commit message format (conventional commits, etc.)
- Git hooks (pre-commit hooks, signing, etc.)
- Branch naming conventions
- Linking to issue trackers

**Default format:**

```text
[feat-013] Implemented DID registry

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

### mark-feature-complete.sh

**Purpose:** Update feature status in `.claude/progress/feature-list.json`

**Usage:**

```bash
.claude/scripts/mark-feature-complete.sh feat-013 implemented
.claude/scripts/mark-feature-complete.sh feat-013 tested
```

**Customize for:**

- Custom status values (e.g., "review", "deployed")
- Additional metadata (completion time, tester, etc.)
- State transitions (only allow tested → completed)

**Default:** Sets `status` field to provided value (default: "implemented")

---

### check-state.sh

**Purpose:** Get current state from `.claude/progress/state.json`

**Output:** Human-readable or JSON state

**Usage:**

```bash
.claude/scripts/check-state.sh          # Human-readable
.claude/scripts/check-state.sh --json   # JSON format
```

**Customize for:**

- Additional state information
- Custom state fields
- Integration with other tools

---

### validate-transition.sh

**Purpose:** Validate state machine transitions

**Usage:**

```bash
.claude/scripts/validate-transition.sh FROM TO
# Exit 0 = valid, Exit 1 = invalid
```

**Customize for:**

- Custom state machines
- Additional transition rules
- Project-specific constraints

**Default:** Enforces standard state machine (START → INIT → IMPLEMENT → TEST → COMPLETE)

---

### transition-state.sh

**Purpose:** Execute state transition with validation

**Usage:**

```bash
.claude/scripts/transition-state.sh TO_STATE [REASON]
```

**What it does:**

1. Validates state name (valid: START, INIT, IMPLEMENT, TEST, COMPLETE)
2. Calls validate-transition.sh to ensure transition is allowed
3. Adds entry to history array with timestamp and reason
4. Preserves health_status, feature_id, and attempts
5. Updates state, entered_at, and last_updated timestamps

**Customize for:**

- Additional state machine states
- Custom validation rules
- Additional metadata fields
- State transition side effects

---

### check-context.sh

**Purpose:** Monitor token usage and trigger compression

**Output:** Compression level (none, remove_raw, summarize, full, emergency)

**Usage:**

```bash
.claude/scripts/check-context.sh 0.75  # Pass usage percentage
```

**Customize for:**

- Custom thresholds
- Project-specific compression strategies
- Integration with context management tools

---

## Customization Checklist

When you first set up a project, customize scripts in this order:

1. **health-check.sh** - Most critical, runs every session
2. **run-tests.sh** - Needed for verification
3. **restart-servers.sh** - Needed for development
4. **get-current-feature.sh** - Usually works as-is
5. **mark-feature-complete.sh** - Usually works as-is
6. **feature-commit.sh** - Customize commit format if needed
7. **State scripts** - Usually work as-is

---

## Template Location

Original templates are maintained in:

```text
~/.claude/skills/initialization/templates/
```

When in doubt, refer to templates for examples and best practices.

To re-copy templates (will add TEMPLATE- prefix):

```bash
~/.claude/skills/initialization/assets/copy-scripts.sh
```

---

## Troubleshooting

**Script not found?**

Check if it still has TEMPLATE- prefix:

```bash
ls .claude/scripts/TEMPLATE-*.sh
# If found, customize and rename
```

**Script not executable?**

```bash
chmod +x .claude/scripts/*.sh
```

**Script uses wrong paths?**

- Update paths to match your project structure
- Use relative paths from project root

**Health check failing?**

- Verify services are running
- Check ports and endpoints match your setup
- Increase timeout if services start slowly

**Feature list not found?**

- Ensure `.claude/progress/feature-list.json` exists
- Run initialization skill if missing
