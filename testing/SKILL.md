---
name: testing
description: "Legacy compatibility testing surface for repos already using the older `.claude` lifecycle. Use only when maintaining that TEST-state workflow. NOT for the Codex-first default baseline — prefer repo-owned test commands, verify, and repo-readiness-bootstrap."
context: fork
agent: general-purpose
---

# Testing

Compatibility note: this skill is a `.claude`-era lifecycle surface. It is not part of the default Codex-first repo baseline.

Comprehensive testing for TEST state. Adapts to project structure automatically.

---

## Workflow: Detect Project Type, Then Test

**Adaptive path detection:**

1. Check if `.claude/scripts/run-tests.sh` exists → use it
2. Else if `package.json` has `test` script → use `pnpm test` / `npm test`
3. Else → check for vitest/jest config files

```
┌─────────────────────────────────────────────────────────────┐
│              DETECT PROJECT TEST SCRIPT                     │
│  .claude/scripts/run-tests.sh? → use it                    │
│  package.json test script? → pnpm test                     │
│  vitest/jest config? → run directly                        │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Run: typecheck + unit tests                    │
│         (pnpm typecheck && pnpm test)                      │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
    ┌─────────┐
    │ Exit 0? │
    └────┬────┘
         │
    ┌────┴────┐
    │         │
   YES       NO
    │         │
    │         ▼
    │    ┌──────────────────────┐
    │    │ FIX BRANCH           │
    │    │ 1. Count errors      │
    │    │ 2. Analyze patterns  │
    │    │ 3. Fix (batch/manual)│
    │    │ 4. Rebuild cascade   │
    │    │ 5. Re-run tests      │
    │    └──────────────────────┘
    │         │ (loop until exit 0)
    │         ▼
    │    Exit 0 ──────┐
    │                 │
    └─────────────────┘
                      │
                      ▼
               ┌──────────────┐
               │ Browser Test │
               │ (if needed)  │
               └──────────────┘
```

---

## Phase 1: Detect and Run Tests

```
┌─────────────────────────────────────────────────────────────┐
│           .claude/scripts/restart-servers.sh                 │
│              (ensure clean server state)                     │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              .claude/scripts/run-tests.sh                    │
│         (typecheck + unit tests + API tests)                 │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
    ┌─────────┐
    │ Exit 0? │
    └────┬────┘
         │
    ┌────┴────┐
    │         │
   YES       NO
    │         │
    │         ▼
    │    ┌──────────────────────┐
    │    │ FIX BRANCH           │
    │    │ 1. Context graph     │
    │    │ 2. Count errors      │
    │    │ 3. Fix (batch/manual)│
    │    │ 4. Rebuild cascade   │
    │    │ 5. Re-run tests      │
    │    └──────────────────────┘
    │         │ (loop until exit 0)
    │         ▼
    │    Exit 0 ──────┐
    │                 │
    └─────────────────┘
                      │
                      ▼
               ┌──────────────┐
               │ Browser Test │
               │ Load skill   │
               └──────────────┘
                      │
                      ▼
               ┌──────────────┐
               │  Return to   │
               │testing-trackr│
               └──────────────┘
---

## Phase 2: Fix Branch (IF Exit 1)

### Fix Step 1: Analyze Errors

```bash
# Check error patterns - look for common issues
pnpm typecheck 2>&1 | head -30

# Check for specific patterns
ERRORS=$(pnpm typecheck 2>&1)
echo "$ERRORS" | grep -c "error" || echo "0"
```

### Fix Step 2: Count Errors

```bash
# Count errors to determine strategy
ERROR_COUNT=$(pnpm typecheck 2>&1 | grep -c "error" || echo "0")
echo "Error count: $ERROR_COUNT"
```

### Fix Step 3: Choose Strategy

| Error Count | Strategy |
|-------------|----------|
| 1-20 | Manual fix |
| 20+ | Batch fix script (98% token savings vs individual edits) |

**Batch fix template**:

```bash
# Fix repetitive pattern across all files
find packages/website -name "*.tsx" -exec sed -i '' \
  's/oldPattern/newPattern/g' {} +

# Rebuild cascade
cd packages/website/shared && pnpm build && cd ../.. && pnpm typecheck
```

### Fix Step 4: Rebuild Type System (if applicable)

```bash
# Rebuild shared types first
cd packages/website/shared && pnpm build
cd ../..

# Verify typecheck passes
pnpm typecheck
```

### Fix Step 5: Re-run Tests

```bash
.claude/scripts/run-tests.sh
```

**Loop**: If still failing (exit 1), return to Fix Step 1. **Max 3 attempts per feature.**

After 3 failed attempts:

- Mark feature as `failed` (not `passed`)
- Store failure trace in context graph
- Continue to next feature (do NOT block the pipeline)

```bash
MAX_ATTEMPTS=3
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  ATTEMPT=$((ATTEMPT + 1))
  echo "Fix attempt $ATTEMPT/$MAX_ATTEMPTS"
  
  # Fix Branch steps 1-4...
  
  .claude/scripts/run-tests.sh
  if [ $? -eq 0 ]; then
    echo "✅ Tests pass on attempt $ATTEMPT"
    break
  fi
done

if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
  echo "❌ Fix branch exhausted after $MAX_ATTEMPTS attempts"
  # Mark failed if testing-tracker exists
  if [ -f ~/.claude/skills/testing-tracker/scripts/mark-tested.py ]; then
    python3 ~/.claude/skills/testing-tracker/scripts/mark-tested.py $FEATURE_ID failed \
      --evidence "Fix attempts exhausted after $MAX_ATTEMPTS tries"
  fi
fi
```

If passing (exit 0), continue to Phase 4.

### Fix Step 6: Store Failure (After Exhausted)

If Fix Branch is exhausted (max attempts reached):

```bash
# Mark feature as failed (if testing-tracker exists)
if [ -f ~/.claude/skills/testing-tracker/scripts/mark-tested.py ]; then
  python3 ~/.claude/skills/testing-tracker/scripts/mark-tested.py FEATURE_ID failed \
    --evidence "Fix attempts exhausted: $ERROR_COUNT errors"
fi

# Store failure in context graph
context_store_trace({
  decision: "Testing failed for [feature] after $attempts attempts",
  category: "testing",
  outcome: "failure",
  feature_id: "FEATURE_ID"
})
```

---

## Phase 4: Browser Testing (IF Exit 0)

**Sequence** (one app fully at a time):

| App | URL | Tests |
|-----|-----|-------|
| Buyer | localhost:3000 | Search, product details, cart, checkout, orders |
| Seller | localhost:3002 | Catalog, orders, fulfillment, config |
| Integration | both | Buyer places order -> seller receives -> status sync |

**Action**: Load `browser-testing` skill (WebMCP-first).

**Mandatory browser evidence before PASS**:

- `navigator.modelContext` is available
- `navigator.modelContextTesting` is available
- `listTools()` returns at least 1 tool
- At least 1 deterministic `executeTool()` call succeeds
- Task-specific browser flows pass

If WebMCP prerequisites fail, mark as `BLOCKED` with root cause and return to Phase 3 to fix instrumentation/runtime issues before continuing.

---

## After Browser Testing Returns

When browser-testing skill completes and returns evidence:

### 1. Check WebMCP Evidence First

Review structured browser evidence (not screenshot-only claims):

- WebMCP runtime availability (`modelContext`, `modelContextTesting`)
- Registered tool inventory (`tool_count`, tool names)
- `executeTool()` results (success/failure + error text)
- Product behavior verdict for each tested flow

### 2. If Issues Found: Re-enter Fix Branch

- Treat browser issues same as test failures
- Return to Phase 3 (Fix Branch)
- Fix, rebuild, re-test

### 3. If All Passed: Mark Success

```bash
# Mark feature as passed (if testing-tracker exists)
if [ -f ~/.claude/skills/testing-tracker/scripts/mark-tested.py ]; then
  python3 ~/.claude/skills/testing-tracker/scripts/mark-tested.py FEATURE_ID passed \
    --evidence "Unit tests passed" "WebMCP browser testing passed"
fi

# Store success in context graph
context_store_trace({
  decision: "Testing passed for [feature/test]",
  category: "testing",
  outcome: "success",
  feature_id: "FEATURE_ID"
})
```

### 4. Update Context Graph Outcomes

After fix attempts and re-testing:

```bash
# Get traces with pending outcome for this feature
PENDING_TRACES=$(context_query_traces(
  query="${FEATURE_ID}",
  outcome="pending"
))

# Update outcomes based on fix results
if [ "$TEST_RESULT" == "passed" ]; then
  for trace in $PENDING_TRACES; do
    context_update_outcome(
      trace_id=$trace,
      outcome="success"
    )
  done
else
  for trace in $PENDING_TRACES; do
    context_update_outcome(
      trace_id=$trace,
      outcome="failure"
    )
  done
fi
```

**Critical**: Only testing skill updates outcomes (after fix verification), not browser-testing.

### 5. Return to Caller

Return control to the calling context. If testing-tracker skill exists, return to it for autonomous loop continuation.

---

## Token-Efficient Testing

| Tool | Use Case | Savings |
|------|----------|---------|
| `execute_code` | Run pytest/jest in sandbox | 98% |
| `process_logs` | Parse test output for failures | 95% |
| `process_csv` | Test coverage reports | 99% |
| `batch_process_csv` | Multiple test result files | Batch |

**When to use:**

- Large test suites → `execute_code` (sandbox execution, return summary)
- Log analysis → `process_logs` (filter at source, not after load)
- Coverage reports → `process_csv` (filter by file/coverage %)

### Output Truncation Patterns

```bash
# For large test outputs - get summary only
pnpm test 2>&1 | tail -n 50  # Last 50 lines
ERROR_COUNT=$(pnpm typecheck 2>&1 | grep -c "error")

# Count without loading all errors
TEST_RESULTS=$(pnpm test 2>&1)
if echo "$TEST_RESULTS" | grep -q "failed"; then
    echo "$TEST_RESULTS" | tail -n 20
fi
```

### Progressive Disclosure for References

**Load reference files ONLY when needed:**

| Reference | Load When |
|-----------|-----------|
| unit-testing.md | Pre-flight checks, batch fixes |
| api-testing.md | Server issues, endpoint failures |
| browser-testing.md | UI testing only |
| database-testing.md | DB verification issues |

Don't preload all references - load on-demand based on test failure type.

---

## Key Rules

1. **Servers first** - Always restart servers before running tests (prevents `ECONNREFUSED` failures)
2. **Then run tests** - Execute `run-tests.sh` (typecheck, unit, API)
3. **Exit code verification** - Use `$?` not LLM judgment
4. **Fix Branch before browser** - Unit tests must pass before browser testing
5. **WebMCP gate before pass** - Browser pass requires `modelContext` + `listTools` + `executeTool` evidence
6. **Batch fix for >20 errors** - Use sed scripts, not manual edits
7. **Store verified results only** - Never store untested fixes
8. **Return to caller** - Return control after marking status
