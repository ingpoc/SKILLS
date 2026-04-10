---
name: initialization
context: fork
agent: general-purpose
description: "Use when starting a new session without feature-list.json, setting up project structure, or breaking down requirements into atomic features. Load in INIT state. Detects project type (Python/Node/Django/FastAPI), creates feature-list.json with priorities and plan_references, initializes .claude/progress/ tracking. On successful completion, hands off to orchestrator skill for state-based skill management. CRITICAL: Run scripts in order - do NOT manually create files."
---

# Initialization

Project setup and feature breakdown for INIT state.

## Anti-Patterns (DO NOT)

| Anti-Pattern | Correct Approach |
|--------------|------------------|
| Manually create `.claude/` files | Run `init-project.sh` |
| Manually create `state.json` | Run `init-progress.sh` |
| Manually create scripts in `.claude/scripts/` | Run `copy-scripts.sh` |
| Manually create hooks | Run `setup-project-hooks.sh` |
| Skip verification steps | Run `verify-init.sh` after EVERY session |
| Proceed without 15/15 checks passing | Fix failures before implementation |

## Execution Checklist (MANDATORY)

**Run each script in order. Verify before proceeding.**

### Phase 1: Global Setup (once per machine)

```bash
# Step 1: Global CLAUDE.md
[ -f ~/.claude/CLAUDE.md ] || ~/.claude/skills/initialization/scripts/global-init.sh

# Step 2: Global hooks
[ -x ~/.claude/hooks/verify-state-transition.py ] || \
    ~/.claude/skills/global-hook-setup/scripts/setup-global-hooks.sh
```

**GATE 1:** Verify global setup

```bash
[ -f ~/.claude/CLAUDE.md ] && [ -x ~/.claude/hooks/verify-state-transition.py ] && echo "✅ Global setup OK"
```

### Phase 2: Project Structure

```bash
# Step 3: Initialize project structure
~/.claude/skills/initialization/scripts/init-project.sh
```

Creates:

- `.claude/config/project.json` - Project settings
- `CLAUDE.md` - Project documentation
- `.claude/CLAUDE.md` - Quick reference

```bash
# Step 4: Initialize progress tracking (creates state.json)
~/.claude/skills/initialization/scripts/init-progress.sh
```

Creates:

- `.claude/progress/state.json` - State tracking (INIT)
- `.claude/progress/file_history.json` - File tracking
- `.claude/progress/checkpoint.json` - Compression tracking

**GATE 2:** Verify project structure

```bash
[ -f ".claude/config/project.json" ] && [ -f ".claude/progress/state.json" ] && echo "✅ Project structure OK"
```

### Phase 3: Automation Setup

```bash
# Step 5: Copy automation scripts
~/.claude/skills/initialization/assets/copy-scripts.sh
```

Creates `.claude/scripts/`:

- `get-current-feature.sh` - Extract next pending feature
- `health-check.sh` - Verify app health
- `restart-servers.sh` - Restart servers
- `feature-commit.sh` - Commit with feature ID
- `mark-feature-complete.sh` - Update feature status
- `check-state.sh` - Get current state
- `validate-transition.sh` - Validate transitions
- `transition-state.sh` - Execute state transition
- `check-context.sh` - Monitor context
- `run-tests.sh` - Run project tests
- `README.md` - Script documentation

```bash
# Step 6: Install project hooks
~/.claude/skills/project-hook-setup/scripts/setup-project-hooks.sh --non-interactive
```

Creates `.claude/hooks/`:

- `verify-tests.py` - Verify tests pass
- `session-entry.sh` - Session entry protocol
- `verify-health.py` - Health verification
- `verify-files-exist.py` - File existence check
- `require-dependencies.py` - Dependency check

```bash
# Step 6.5: Execute mcp-setup skill
/mcp-setup
```

Creates:

- `.mcp.json` - MCP server configuration
- `mcp/` directory - MCP server installations
- Required API keys prompted

Verification happens in **Step 9** (check #15)

**GATE 3:** Verify automation

```bash
[ -f ".claude/scripts/health-check.sh" ] && [ -f ".claude/hooks/verify-tests.py" ] && echo "✅ Automation OK"
```

### Phase 4: Dependencies & Features

```bash
# Step 7: Check dependencies
~/.claude/skills/initialization/scripts/check-dependencies.sh
```

Fix any errors before proceeding.

```bash
# Step 8: Create feature list (from PRD/requirements)
# Analyze requirements → create .claude/progress/feature-list.json
```

Feature list requirements:

- Each feature has: `id`, `description`, `priority`, `status`, `tier`, `acceptance`
- Use MVP-first tiers: `mvp` (10), `core` (30), `full` (all)
- Status starts as `pending`

### Phase 5: Final Verification

```bash
# Step 9: MANDATORY - Run verification
~/.claude/skills/initialization/scripts/verify-init.sh
```

**Must pass ALL 15 checks:**

| # | Check | Created By |
|---|-------|------------|
| 1 | `.claude/CLAUDE.md` exists | `init-project.sh` |
| 2 | `.claude/config/project.json` exists | `init-project.sh` |
| 3 | `.claude/progress/` directory exists | `init-progress.sh` |
| 4 | `feature-list.json` exists | Manual/script |
| 5 | Feature list has features | Manual/script |
| 6 | Features have required fields | Manual/script |
| 7 | `state.json` exists | `init-progress.sh` |
| 8 | State is INIT | `init-progress.sh` |
| 9 | Global hooks directory exists | `setup-global-hooks.sh` |
| 10 | `verify-state-transition.py` installed | `setup-global-hooks.sh` |
| 11 | `require-commit-before-tested.py` installed | `setup-global-hooks.sh` |
| 12 | Project hooks directory exists | `setup-project-hooks.sh` |
| 13 | `verify-tests.py` installed | `setup-project-hooks.sh` |
| 14 | `session-entry.sh` installed | `setup-project-hooks.sh` |
| 15 | MCP servers configured | `Step 6.5 (mcp-setup)` |

**DO NOT proceed to IMPLEMENT until 15/15 pass.**

### Phase 5.5: Skill Handoff (Automatic)

**After verify-init.sh passes all 15 checks:**

```bash
# Orchestrator skill automatically loads to take over session management
# This happens at the end of verify-init.sh with no manual action needed

echo "✅ All INIT criteria met!"
echo "Loading orchestrator skill to manage session lifecycle..."

# Orchestrator will:
# 1. Check dev environment health
# 2. Check current state
# 3. Load appropriate skill:
#    - IMPLEMENT → implementation skill
#    - TEST → testing skill
#    - COMPLETE → context-graph skill
```

**Why automatic handoff:**

- ✅ Seamless workflow: No manual skill loading needed
- ✅ State enforced: Cannot skip to IMPLEMENT without passing INIT
- ✅ Context preserved: Orchestrator knows state from state.json
- ✅ User stays in flow: One command completes entire chain

---

## project.json Required Fields

The hooks verification requires these fields in `.claude/config/project.json`:

| Field | Required | Example |
|-------|----------|---------|
| `project_type` | Yes | `"typescript-monorepo"` |
| `test_command` | Yes | `"npm test"` |
| `health_check` | Yes | `"npm run build"` |
| `dev_server_port` | No | `3000` |
| `required_env` | No | `[]` |
| `required_services` | No | `[]` |

## Quick Reference

| Task | Script |
|------|--------|
| Full init (new project) | Run Steps 1-9 in order |
| Verify init complete | `verify-init.sh` |
| Check current state | `.claude/scripts/check-state.sh` |
| Get next feature | `.claude/scripts/get-current-feature.sh` |

## CLAUDE.md Hierarchy

| File | Scope | Purpose |
|------|-------|---------|
| `~/.claude/CLAUDE.md` | Global | User preferences |
| `CLAUDE.md` | Project | Project docs (100-300 lines) |
| `.claude/CLAUDE.md` | Local | Quick reference (<50 lines) |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/global-init.sh` | One-time ~/.claude/CLAUDE.md setup |
| `scripts/init-project.sh` | Initialize .claude/ structure |
| `scripts/init-progress.sh` | Create state.json and tracking files |
| `scripts/detect-project.sh` | Detect Python/Node/Django/etc |
| `scripts/check-dependencies.sh` | Verify MCP, env vars, services |
| `scripts/create-feature-list.sh` | Generate feature-list.json template |
| `scripts/verify-init.sh` | Verify all 15 INIT criteria |
| `assets/copy-scripts.sh` | Copy automation scripts to project |

## References

| File | Load When |
|------|-----------|
| references/feature-breakdown.md | Breaking down requirements |
| references/project-detection.md | Detecting project type |
| references/mvp-feature-breakdown.md | MVP-first tiered features |

## Assets

| File | Purpose |
|------|---------|
| templates/CLAUDE.project.template.md | Template for project CLAUDE.md |
| templates/CLAUDE.local.template.md | Template for .claude/CLAUDE.md |
| templates/framework-templates/*.md | Framework-specific templates |
| templates/*.sh | Automation script templates |
| assets/copy-scripts.sh | Script copier |
| assets/feature-list.template.json | Feature list template |
