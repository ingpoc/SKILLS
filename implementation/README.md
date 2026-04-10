# Implementation Skill - Project Setup Guide

## Overview

Implementation skill is **template-based and project-agnostic**. It provides:

1. **Workflow structure** (all projects follow same steps)
2. **Script templates** (customize for your project)
3. **Fallback behavior** (manual steps if scripts don't exist)

## For Projects WITHOUT Custom Scripts

If you don't create `.claude/scripts/`, the implementation skill has built-in fallback:

| Step | Fallback Behavior |
|------|-------------------|
| Get feature | Read `.claude/progress/feature-list.json` directly |
| Query context | Use MCP: `context_query_traces(query=...)` |
| Implement | Follow project patterns from `CLAUDE.md` |
| Test | Write tests alongside code |
| Health check | Manual verification (no automated check) |
| Commit | Manual: `git commit -m "[feat-id] description"` |
| Mark complete | Manual: Update feature-list.json |

**This works fine** for simple projects or during initial setup.

## For Projects WITH Custom Scripts

Create `.claude/scripts/` directory and customize scripts for your specific project architecture.

### 3-Step Setup

#### Step 1: Create Directory

```bash
mkdir -p .claude/scripts
cd .claude/scripts
```

#### Step 2: Copy and Customize Templates

Copy templates from skill and adjust for your project:

```bash
# Copy all templates
for template in /path/to/implementation/templates/*.example; do
  cp "$template" "$(basename "$template" .example)"
done

# Make executable
chmod +x *.sh

# Edit each script to match your project
# Examples:
# - health-check.sh: Check all your services
# - get-current-feature.sh: Match your feature-list format
# - feature-commit.sh: Enforce your commit convention
# - mark-feature-complete.sh: Handle your feature status updates
```

#### Step 3: Document Your Scripts

Create `README.md` in `.claude/scripts/`:

```markdown
# .claude/scripts - Project Scripts

Scripts for automating implementation workflow in this project.

## Scripts

| Script | What It Does | Customized For |
|--------|--------------|----------------|
| `get-current-feature.sh` | Extracts next pending feature | This project's feature-list format |
| `health-check.sh` | Verifies all services healthy | Frontend (port 3000), Gateway (port 8000), Services |
| `feature-commit.sh` | Commits with feature ID | Uses [FEAT-XXX] format |
| `mark-feature-complete.sh` | Updates feature status | Updates feature-list.json |

## When to Customize

Create/customize scripts when:
- [ ] Project has multiple services (need multi-check health)
- [ ] Feature list has custom format
- [ ] Commit process needs special handling
- [ ] Feature completion logic is complex

## Testing Scripts

Before relying on scripts:

```bash
# Test get-current-feature
./.claude/scripts/get-current-feature.sh

# Test health check
./.claude/scripts/health-check.sh

# Test commit (with --dry-run if available)
./.claude/scripts/feature-commit.sh feat-001 "Test"

# Test mark-complete
./.claude/scripts/mark-feature-complete.sh feat-001
```

```

## Project Types: Examples

### Example 1: Monolithic Backend (FastAPI)

**Single service, single health check:**

```bash
# .claude/scripts/health-check.sh
#!/bin/bash
set -e

# Check server is running
curl -sf http://localhost:8000/health > /dev/null || exit 1

# Run tests
pytest --tb=short -q || exit 1

echo "✓ All checks passed"
exit 0
```

### Example 2: Frontend + Backend Monorepo

**Two independent services:**

```bash
# .claude/scripts/health-check.sh
#!/bin/bash
set -e

# Frontend (Next.js)
curl -sf http://localhost:3000 > /dev/null || { echo "Frontend down"; exit 1; }

# Backend (FastAPI)
curl -sf http://localhost:8000/health > /dev/null || { echo "Backend down"; exit 1; }

# Tests
pytest --tb=short -q || exit 1

echo "✓ All services healthy"
exit 0
```

### Example 3: Multi-Service (Identity Platform)

**Complex: frontend, API, blockchain, agents, MCP servers:**

```bash
# .claude/scripts/health-check.sh
#!/bin/bash
set -e

echo "Checking all services..."

# Frontend
curl -sf http://localhost:3000 > /dev/null || { echo "Frontend down"; exit 1; }

# Gateway API
curl -sf http://localhost:8000/health > /dev/null || { echo "Gateway down"; exit 1; }

# Solana validator (if local)
if pgrep -f "solana-test-validator" > /dev/null; then
  solana ping -u localhost > /dev/null || { echo "Solana validator down"; exit 1; }
fi

# MCP servers (check processes)
if ! pgrep -f "mcp-" > /dev/null; then
  echo "Warning: No MCP servers running"
  # Don't exit, might be optional
fi

# Unit tests
pytest --tb=short -q gateway/tests || exit 1
cd frontend && npm test -- --passWithNoTests || exit 1

echo "✓ All services healthy"
exit 0
```

### Example 4: Get Current Feature (Multi-Format Support)

**Different feature-list formats:**

```bash
# .claude/scripts/get-current-feature.sh
#!/bin/bash
set -e

FEATURE_FILE=".claude/progress/feature-list.json"

[ -f "$FEATURE_FILE" ] || { echo "feature-list.json not found"; exit 1; }

# Get first pending feature
FEATURE=$(jq '.features[] | select(.status=="pending") | .' "$FEATURE_FILE" 2>/dev/null | head -1)

[ -z "$FEATURE" ] && { echo "No pending features"; exit 1; }

# Output as JSON
echo "$FEATURE"
exit 0
```

### Example 5: Feature Commit (Custom Format)

**Project uses [FEAT-XXX] in commits:**

```bash
# .claude/scripts/feature-commit.sh
#!/bin/bash
set -e

FEATURE_ID=$1
MESSAGE=${2:-"Implementation"}

[ -z "$FEATURE_ID" ] && { echo "Usage: feature-commit.sh <feat-id> [message]"; exit 1; }

# Check for changes
[ -z "$(git status --porcelain)" ] && { echo "No changes to commit"; exit 0; }

# Commit with feature ID
git add -A
git commit -m "[$FEATURE_ID] $MESSAGE"

exit 0
```

## Fallback Behavior

If script doesn't exist, implementation skill uses fallback:

| Missing Script | Fallback Action |
|---|---|
| `get-current-feature.sh` | Read feature-list.json directly using jq |
| `health-check.sh` | Agent performs manual verification |
| `feature-commit.sh` | Agent does manual: `git commit -m "[feat-id] msg"` |
| `mark-feature-complete.sh` | Agent manually edits feature-list.json |

**Design principle**: Scripts are optional optimizations, not requirements.

## Versioning Scripts

Keep scripts in git (they're part of project setup):

```bash
# Good: Commit scripts
git add .claude/scripts/
git commit -m "chore: Add implementation automation scripts"

# These are deterministic, version-controlled helpers
```

## Common Issues

### Issue: Script returns exit code 1 but no error message

**Fix**: Add helpful error messages:

```bash
#!/bin/bash
set -e  # Exit on error

# BAD
curl http://localhost:8000/health || exit 1

# GOOD
curl -sf http://localhost:8000/health > /dev/null || {
  echo "ERROR: Gateway health check failed (port 8000)" >&2
  echo "Start with: cd gateway && uvicorn app.main:app --reload" >&2
  exit 1
}
```

### Issue: Script works locally but fails in agent context

**Fix**: Use absolute paths or check working directory:

```bash
#!/bin/bash
set -e

# Ensure we're in project root
cd "$(git rev-parse --show-toplevel)" || exit 1

# Now paths work consistently
pytest ./tests/ || exit 1
```

### Issue: Different services have different startup times

**Fix**: Add retry logic:

```bash
#!/bin/bash
set -e

# Retry logic for slow-starting services
retry_until_healthy() {
  local url=$1
  local retries=10

  for i in $(seq 1 $retries); do
    if curl -sf "$url" > /dev/null; then
      return 0
    fi
    [ $i -lt $retries ] && sleep 1
  done

  return 1
}

retry_until_healthy "http://localhost:8000/health" || {
  echo "Gateway failed to start"
  exit 1
}
```

## Next Steps

1. Copy templates from `implementation/templates/`
2. Customize for your project
3. Test each script independently
4. Document in `.claude/scripts/README.md`
5. Commit to git
6. Implementation skill will auto-detect and use them
