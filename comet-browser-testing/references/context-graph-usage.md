# Context Graph Integration

How to use the context graph MCP for learning loops in browser testing.

## Overview

Context graph stores decision traces with semantic embeddings, enabling:

- Query for similar past issues before debugging
- Store findings for future reference
- Update outcomes after fixes
- Build institutional knowledge

## Browser Testing Categories

| Category | Use For | Example Queries |
|----------|---------|-----------------|
| `frontend` | UI issues, component problems, rendering | "button not visible", "modal not opening" |
| `hydration` | React SSR mismatches, client/server diff | "hydration error", "useEffect issue" |
| `css` | Styling, layout, theme issues | "layout broken", "colors wrong" |
| `framework` | Architecture, patterns, routing | "navigation not working", "route error" |
| `testing` | Test automation, validation | "test failing", "e2e issue" |
| `deployment` | Build, server, environment | "build error", "server crash" |

## Workflow Integration

### Before Testing: Query Precedents

```
context_query_traces(
  query="login button not responding",
  category="frontend",
  limit=5
)
```

**What this returns:**

- Similar issues found in past sessions
- Solutions that were applied
- Outcomes (success/failure/pending)

**Benefits:**

- Avoid repeating same investigations
- Apply proven solutions immediately
- Learn from past patterns

### During Testing: Store Issues

```
context_store_trace(
  decision="Login button click does nothing. Console shows: 'TypeError: Cannot read property onClick of undefined'. Fix: Check button binding in component.",
  category="frontend",
  outcome="pending",
  feature_id="feat-001"
)
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| decision | string | Yes | Issue description and proposed/appplied fix |
| category | string | No | One of: frontend, hydration, css, framework, testing, deployment |
| outcome | string | No | pending, success, failure (default: pending) |
| feature_id | string | No | Link to specific feature for traceability |

**Best practices:**

- Include console error messages (exact text)
- Describe the fix applied or planned
- Set outcome to "pending" when first discovered
- Link to feature_id for project traceability

### After Fix: Update Outcome

```
context_update_outcome(
  trace_id="trace_abc123...",
  outcome="success"
)
```

**Outcome values:**

| Outcome | When to Use |
|---------|-------------|
| `pending` | Issue discovered, fix in progress |
| `success` | Fix applied and verified working |
| `failure` | Fix didn't work, need different approach |

## Example Patterns

### Pattern 1: Regression Prevention

```
# Before making changes
context_query_traces(
  query="button click handler",
  category="frontend"
)

# Found: "Button onClick undefined error - fixed by using useCallback"
# Apply same pattern to new code
```

### Pattern 2: Issue Documentation

```
# After finding issue in Comet test
context_store_trace(
  decision="PostCSS error: 'Missing field negated on ScannerOptions.sources'. Fixed by adding css.transformer: 'lightningcss' to vite.config.ts",
  category="deployment",
  outcome="success"
)

# Future queries will find this immediately
```

### Pattern 3: Multi-Session Debugging

```
# Session 1: Discover issue
context_store_trace(
  decision="Wallet connection fails on mobile. Desktop works. Suspect viewport/breakpoint issue.",
  category="frontend",
  outcome="pending"
)

# Session 2: After fix
context_update_outcome(
  trace_id="trace_abc123...",
  outcome="success"
)

# Session 3: Similar issue appears
context_query_traces(
  query="wallet mobile connection",
  category="frontend"
)
# Returns: Wallet connection fix from Session 2
```

## Query Tips

### Good Queries

| Query | Why It Works |
|-------|--------------|
| "button click not responding" | Specific action + problem |
| "hydration error in useEffect" | Specific error + location |
| "navigation router not working" | Specific feature + issue |
| "console shows undefined error" | Specific symptom |

### Poor Queries

| Query | Why It Fails |
|-------|--------------|
| "bug" | Too generic |
| "not working" | No specifics |
| "error" | Every issue is an error |
| "help" | Not a technical query |

### Semantic Search Examples

```
# Find similar button issues
context_query_traces(query="button", category="frontend", limit=10)

# Find all routing issues
context_query_traces(query="navigation routing", category="framework")

# Find deployment errors
context_query_traces(query="build error", category="deployment")

# Find hydration issues
context_query_traces(query="hydration mismatch", category="hydration")
```

## Integration with Comet Testing

### Full Workflow Example

```
# Phase 1: Server-side pre-check
context_query_traces(
  query="console errors buyer portal",
  category="frontend"
)
process_logs(file_path="buyer-portal.log", pattern="ERROR")

# Phase 2: Comet testing
comet_connect()
comet_ask(
  prompt="Navigate to http://localhost:3002 and check for console errors",
  newChat=true
)
comet_screenshot()

# Phase 3: Store findings
context_store_trace(
  decision="PostCSS error found in Comet test. Fixed with lightningcss transformer.",
  category="deployment",
  outcome="success"
)
```

### Common Issue Categories with Comet

| Comet Finding | Category | Example Decision |
|---------------|----------|------------------|
| Console error: "Cannot read property X" | frontend | Property access error - check null/undefined |
| Hydration mismatch | hydration | Server/client HTML diff - check useEffect/data fetching |
| Layout broken on mobile | css | Media query issue - check breakpoint styles |
| Navigation doesn't work | framework | Router config issue - check route definition |
| Build fails to start | deployment | Port conflict or missing dependency |

## Batch Operations

### Query Multiple Categories

```
# Search across all categories
context_query_traces(query="button", limit=15)
```

### List All Traces

```
# Browse all stored traces
context_list_traces(limit=20)
```

### List Categories

```
# See what categories have traces
context_list_categories()
```

## Best Practices

| Practice | Why |
|----------|-----|
| Query before investigating | Avoid repeating work |
| Store immediately after finding issue | Don't rely on memory |
| Include exact error messages | Enables precise matching |
| Update outcomes after fixes | Closes the loop |
| Use specific categories | Better organization |
| Link to feature_id | Project traceability |
| Review traces periodically | Pattern discovery |

## Token Efficiency

| Method | Savings |
|--------|---------|
| Query precedents first | Prevents repeated investigations |
| Store once, retrieve many | Don't re-document same issues |
| Semantic search vs manual search | 95% faster pattern matching |
| Category filtering | Reduces irrelevant results |
