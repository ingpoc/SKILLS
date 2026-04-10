---
name: implementation
description: "Use when implementing features from feature-list.json. Load in IMPLEMENT state for end-to-end feature development: code, tests, verification, commits. BLOCKING: If TEMPLATE-*.sh files exist in .claude/scripts/, customize and rename them first. After feature completion, performs session introspection to update scripts and prevent future issues. Covers coding patterns, test writing, context graph queries, health checks, and continuous improvement."
context: fork
agent: general-purpose
---

# Implementation

Feature development for IMPLEMENT state.

## When to Load

- State: IMPLEMENT
- Condition: Pending feature exists in feature-list.json

## Core Workflow

| Step | Action | Command/Tool |
|------|--------|--------------|
| 1 | Get feature | `.claude/scripts/get-current-feature.sh` |
| 2 | **BLOCKING:** Check for templates | `ls .claude/scripts/TEMPLATE-*.sh 2>/dev/null` |
| 3 | Analyze codebase | `mcp__token-efficient__execute_code` |
| 4 | Query past decisions | `context_query_traces(query=feature_description)` |
| 5 | **Implement feature** | See Step 5 detailed workflow below |
| 6 | Commit (ONLY after tests pass) | `.claude/scripts/feature-commit.sh feat-ID "desc"` |
| 7 | Mark complete | `.claude/scripts/mark-feature-complete.sh feat-ID implemented` |
| 8 | **Session introspection** | Detect issues → Update scripts → Commit separately |

## Step 2: TEMPLATE- Gate (Critical)

**If `TEMPLATE-*.sh` files exist → STOP**

| Action | Command |
|--------|---------|
| Read script purposes | `cat .claude/scripts/README.md` |
| Customize script | Edit for your project (ports, paths, commands) |
| Rename to activate | `mv TEMPLATE-script.sh script.sh` |
| Test script | Run and verify output |
| Commit | `git add .claude/scripts/ && git commit` |

**Only proceed when:** `ls .claude/scripts/TEMPLATE-*.sh` returns nothing

See `references/template-scripts.md` for detailed customization guide.

## Step 5: Feature Implementation Sub-Workflow (CRITICAL)

**NEVER commit until ALL verification steps pass.**

| Sub-step | Action | Details |
|----------|--------|---------|
| 5a | Write code | Follow project patterns, add types/error handling |
| 5b | Write tests | Unit tests (happy paths, error cases, edge cases) |
| 5c | **Verify ALL pass** | Run verification commands in order |
| 5d | Manual testing | Test functionality if automated tests unclear |

### 5c: Verification Commands (Run in Order)

Stop at first failure. Fix issue, then restart from top.

| Command | Purpose | Must Pass |
|---------|---------|-----------|
| Type check | Verify types (TS/typed languages) | ✅ Exit code 0 |
| Run tests | All unit/integration tests | ✅ Exit code 0 |
| Build | Project builds successfully | ✅ Exit code 0 |
| Health check | Servers/services healthy | ✅ Exit code 0 |

**Common commands by project type:**

| Project Type | Type Check | Run Tests | Build |
|--------------|------------|-----------|-------|
| TypeScript/Node | `pnpm typecheck` | `pnpm test` | `pnpm build` |
| Python | `mypy .` | `pytest` | `python -m build` |
| Go | `go vet ./...` | `go test ./...` | `go build` |
| Rust | `cargo check` | `cargo test` | `cargo build` |

**Golden Rule:** `git commit` ONLY when all commands exit with code 0.

### 5d: Manual Testing (When Needed)

| Scenario | Action |
|----------|--------|
| API endpoints | Test with curl/Postman |
| Web UI | Test in browser |
| CLI tool | Run with sample inputs |
| Automated tests timeout/fail | Verify functionality works manually |

**Purpose:** Confirm implementation works before committing.

## Token-Efficient Analysis (Step 3)

| Task | Tool | Savings |
|------|------|---------|
| Code execution | `mcp__token-efficient__execute_code` | 98% |
| Log parsing | `mcp__token-efficient__process_logs` | 95% |
| Large datasets | `mcp__token-efficient__process_csv` | 99% |

**Rule:** Never load raw logs/code into context.

## Exit Criteria (All Must Pass)

- [ ] No `TEMPLATE-*.sh` files remain
- [ ] Code written with proper types/error handling
- [ ] Tests written (unit tests for happy paths, errors, edge cases)
- [ ] **ALL verification commands pass (exit code 0)**
  - [ ] Type check passes
  - [ ] All tests pass
  - [ ] Build succeeds
  - [ ] Health check passes (if applicable)
- [ ] Manual testing confirms functionality (if needed)
- [ ] Committed with feature ID in message
- [ ] feature-list.json status updated
- [ ] **Session introspection complete** (Step 8)
  - [ ] Issues identified and documented
  - [ ] Scripts updated (if issues found)
  - [ ] Script updates committed separately (chore:)

**NEVER skip verification. Commit only after ALL checks pass.**

## Post-Implementation: Store Learnings

After successful feature completion, store key decisions in context-graph:

| Category | What to Store |
|----------|---------------|
| architecture | Design patterns, component reuse, state management |
| api | Endpoint patterns, error handling, response formats |
| testing | Test strategies, mock patterns, edge cases discovered |
| deployment | Build steps, server restart requirements, configuration |

**Example:**

```
context_store_trace(
  decision="Used StateStore for session management with 30min TTL",
  category="architecture",
  outcome="success",
  feature_id="FEATURE-001"
)
```

**Purpose:** Future features can query past decisions for consistency.

## Step 8: Session Introspection & Script Updates

**Purpose:** Create continuous improvement feedback loop. Detect friction points and update scripts to prevent future issues.

### When to Run

- After feature marked complete
- After learnings stored in context-graph
- Before session ends

### Detection Patterns

| Issue Pattern | Root Cause | Script Update |
|--------------|------------|---------------|
| Manual rebuilds | `node dist/index.js` vs `tsx watch` | restart-servers.sh: Use tsx watch |
| Tests not found | Vitest pattern missing nested packages | vitest.config.ts: Add `packages/*/*/src/**/*.test.ts` |
| Route collisions | Dynamic routes before static routes | Add comments to templates |
| Missing API tests | New endpoints not in run-tests.sh | run-tests.sh: Add endpoint checks |
| Repeated type errors | Missing type definitions | Update template imports |
| Libsodium/ESM issues | Direct imports failing | Document workaround in templates |

### Detection Methods

| Method | What to Check | Tool |
|--------|---------------|------|
| Command history | Repeated commands | `history \| grep -E "(build|restart|test)"` |
| Manual edits | Files changed outside feature | `git diff --stat` |
| Error patterns | Systemic issues | Session error logs |
| Frequency analysis | Commands run 3+ times | Count occurrences |

### Output Format

When issues detected:

```
🔧 Session Issues Detected:
- [Issue 1]: [Impact]
- [Issue 2]: [Impact]

📝 Recommended Script Updates:
- [script-name]: [Update description] (BEFORE → AFTER)

Apply updates? (y/n)
```

### Implementation Guidelines

| Rule | Why |
|------|-----|
| **NON-BLOCKING** | User can skip if unsure |
| **Explain WHY** | Context for the update |
| **Show BEFORE/AFTER** | Clear comparison |
| **Commit separately** | `chore:` prefix, not `feat:` |
| **Store in context-graph** | Future sessions can learn |

### Commit Format

```bash
git add .claude/scripts/
git commit -m "chore: Update scripts based on [FEATURE-ID] learnings

- [script-1]: [update description]
- [script-2]: [update description]

Prevents: [issue description]"
```

### Example from SDK-BUYER-CART-003

**Issues Detected:**

- Rebuilt api-server 5+ times manually
- Tests in nested packages not discovered
- New endpoints (cart, checkout) untested

**Updates Applied:**

1. `restart-servers.sh`: Use `tsx watch` for hot-reload
2. `vitest.config.ts`: Added `packages/*/*/src/**/*.test.ts`
3. `run-tests.sh`: Added POST /api/cart, PUT /api/cart/buyer, POST /api/checkout

**Result:** Future sessions have hot-reload, all tests discovered, endpoints validated

### Success Criteria

| Metric | Target |
|--------|--------|
| Manual work reduced | <10% of session time |
| Repeated issues | 0 in next 3 sessions |
| Script coverage | All common patterns automated |
| Learnings codified | Every feature updates at least 1 script |

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `get-current-feature.sh` | Extract next pending feature |
| `health-check.sh` | Verify implementation health |
| `feature-commit.sh` | Commit with feature ID |
| `mark-feature-complete.sh` | Update feature status |
| `run-tests.sh` | Run project tests |

### If Scripts Don't Exist

**When project scripts are missing** → Create minimal versions:

| Script | Minimal Template |
|--------|------------------|
| get-current-feature.sh | `jq '.features[] | select(.status=="pending")' feature-list.json | head -1` |
| feature-commit.sh | `git commit -m "feat: $1 $2"` |
| mark-feature-complete.sh | `jq --arg id "$1" '.features[] | select(.id==$id) | .status="$2"' feature-list.json` |
| run-tests.sh | Project test command (see verification table) |

## References

| File | Load When |
|------|-----------|
| references/template-scripts.md | Customizing TEMPLATE- scripts |
| references/token-efficient-mcp-patterns.md | Large dataset analysis |
| references/coding-patterns.md | Project-specific patterns |
