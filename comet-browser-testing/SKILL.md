---
name: comet-browser-testing
description: "Use when testing web apps with Perplexity/Comet browser automation, debugging with real browsers, verifying authenticated flows, or when client-side visual verification is needed. Load for dynamic content testing, form automation, console error checking, or when server-side logs alone are insufficient. This skill provides a 3-phase token-efficient methodology: (1) Server-side checks via process_logs MCP and curl, (2) Client-side verification via Comet MCP with specific prompts, (3) Learning loop via context graph storage."
context: fork
agent: general-purpose
---

# Comet Browser Testing

3-phase token-efficient methodology for web application testing using Comet/Perplexity MCP.

## Overview

| Phase | Purpose | Token Savings | Tools |
|-------|---------|---------------|-------|
| 1: Server-Side | Quick health check, known issues | 99% | context_query_traces, process_logs, curl |
| 2: Client-Side | Visual verification, console errors | N/A (required) | comet_connect, comet_ask, comet_screenshot |
| 3: Learning Loop | Store findings for future | N/A | context_store_trace, context_update_outcome |

## Prerequisites

| Requirement | How to Verify |
|-------------|---------------|
| Comet MCP installed | Check `.mcp.json` for `comet-bridge` |
| Context graph MCP | Check for `context-graph` server |
| Token-efficient MCP | Check for `token-efficient` server |

## Fallback Options (When Comet MCP Unavailable)

If `mcp__comet-bridge__` tools are NOT available, use these alternatives:

| Alternative | When to Use | Tools |
|-------------|-------------|-------|
| **dev-browser** skill | Browser automation with persistent state | `dev-browser:dev-browser` skill |
| **mcp__ide__executeCode** | Run Playwright/Puppeteer scripts | `execute_code` with browser automation |
| **testing** skill | Standard browser testing | `mcp__claude_in_chrome__` if available |

### Fallback Workflow (No Comet MCP)

```python
# Option 1: Use dev-browser skill
Skill: dev-browser

# Option 2: Execute Playwright script via execute_code
execute_code("""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:3000")
    page.screenshot(path="/tmp/test.png")
    print(page.content())
""")
```

**Critical**: If no browser automation tools available, fall back to:

1. Phase 1 (server-side only) - parse logs, check curl endpoints
2. Report that client-side verification requires browser automation MCP

## Quick Reference

| Task | Command/Tool |
|------|--------------|
| Connect to Comet | `mcp__comet-bridge__comet_connect` |
| Send test task | `mcp__comet-bridge__comet_ask(prompt="...", newChat=true)` |
| Check progress | `mcp__comet-bridge__comet_poll()` |
| Take screenshot | `mcp__comet-bridge__comet_screenshot()` |
| Query known issues | `mcp__context-graph__context_query_traces(query, category)` |
| Parse server logs | `mcp__token-efficient__process_logs(file, pattern)` |
| Store finding | `mcp__context-graph__context_store_trace(decision, category, outcome)` |

## 3-Phase Workflow

### Phase 1: Server-Side Pre-Check (Optional but Fast)

Purpose: Catch known issues and server errors before browser testing.

```bash
# 1. Check context graph for similar issues
context_query_traces(query="error description", category="frontend")

# 2. Parse server logs for errors (99% token savings)
process_logs(file_path="app.log", pattern="ERROR|WARN", limit=20)

# 3. Quick health check
curl -s http://localhost:3000/api/health
```

**Exit codes:** 0=proceed to Phase 2, 1=block (fix server issues first)

### Phase 2: Client-Side Testing (Required)

Purpose: Visual verification, console errors, functionality testing.

**Connect:**

```
comet_connect()
```

**Test with specific prompts** (see Testing Patterns below):

```
comet_ask(prompt="Navigate to URL and test X", newChat=true, timeout=30000)
```

**Monitor progress** (limit to 10-15 polls):

```
comet_poll()  # Repeat until complete or timeout
```

**Capture evidence:**

```
comet_screenshot()
```

### Phase 3: Learning Loop

Purpose: Store findings for future reference and continuous improvement.

**Store issues found:**

```
context_store_trace(
  decision="Issue description and fix applied",
  category="frontend|hydration|css|framework|testing|deployment",
  outcome="pending"  # Update to "success" after fix
)
```

**Update after fixes:**

```
context_update_outcome(trace_id="trace_abc123...", outcome="success")
```

## Testing Patterns (Critical)

**Key insight:** Generic prompts like "does it work?" produce false positives. Use specific prompts that ask for evidence.

### Initial Load Check

```
Navigate to {URL} and report:
1. Does the page fully load? (yes/no)
2. Any console errors? (list them)
3. What specific elements are visible? (describe 3-5 elements)
4. Is there a loading state that doesn't resolve? (describe)
```

### Styling Verification

```
Navigate to {URL} and check styling:
1. Are there any obvious layout breaks? (describe)
2. Do colors/theme appear consistent? (yes/no with details)
3. Are there any unstyled elements? (describe)
4. Is text readable against backgrounds? (yes/no)
```

### Functionality Test

```
Navigate to {URL} and test functionality:
1. Can you click {button/element}? (yes/no)
2. What happens when you click? (describe)
3. Any console errors on interaction? (list them)
4. Does the action complete? (describe result)
```

### Multi-Page Check

```
Navigate to {URL} and test navigation:
1. Click on {navigation element}
2. Does the URL change? (yes/no, what to)
3. Does the new page load? (yes/no)
4. Any errors during navigation? (describe)
```

### Visual Completeness

```
Navigate to {URL} and verify:
1. Are all expected sections visible? (describe)
2. Any broken images or icons? (describe)
3. Is content truncated or hidden? (describe)
4. Any obvious visual bugs? (describe)
```

### Feature Behavior

```
Navigate to {URL} and test {feature}:
1. What specific action did you take? (describe)
2. What was the expected behavior? (describe)
3. What actually happened? (describe)
4. Any console errors during test? (list them)
```

## Feature Testing Templates

### Authentication/Authorization

```
Test authentication on {URL}:
1. Is there a login button/form visible? (yes/no, describe)
2. Click the login button - what happens? (describe)
3. Any auth-related console errors? (list)
4. Does the page indicate authenticated state? (describe)
```

### Form Submission

```
Test form on {URL}:
1. Fill in the form with test data (describe fields)
2. Click submit - what happens? (describe)
3. Any validation errors? (list)
4. Does submission complete? (describe result)
```

### Navigation/Routing

```
Test navigation on {URL}:
1. Click {navigation item} - what happens?
2. Does URL change? (to what)
3. Does new page load correctly? (describe)
4. Any console errors during navigation? (list)
```

### Data Display

```
Test data display on {URL}:
1. Is data visible on the page? (describe what data)
2. Does data appear complete? (yes/no with details)
3. Any loading states or skeletons? (describe)
4. Any console errors related to data fetching? (list)
```

### User Interactions

```
Test {interaction} on {URL}:
1. What element did you interact with? (describe)
2. What was the expected result? (describe)
3. What actually happened? (describe)
4. Any console errors during interaction? (list)
```

## MCP Tools Reference

### Comet MCP Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `comet_connect` | Connect to Comet browser | Call once per session |
| `comet_ask` | Send task to Comet | Use `newChat=true` for fresh session |
| `comet_poll` | Check progress | Limit to 10-15 polls |
| `comet_screenshot` | Capture visual state | Use for evidence |
| `comet_stop` | Stop running task | If going off track |
| `comet_mode` | Switch search mode | search/research/labs/learn |

### Token-Efficient MCP Tools

| Tool | Purpose | Savings |
|------|---------|---------|
| `process_logs` | Parse log files | 99% |
| `execute_code` | Run code in sandbox | 98% |
| `context_query_traces` | Search context graph | 95% |

### Context Graph MCP Tools

| Tool | Purpose | Category |
|------|---------|----------|
| `context_store_trace` | Store decision/fix | frontend, hydration, css, framework, testing, deployment |
| `context_query_traces` | Search precedents | Query by semantic similarity |
| `context_update_outcome` | Mark fix success | pending → success |
| `context_list_categories` | Browse categories | Discover patterns |

## Resource Loading Guide

| When | Load What |
|------|-----------|
| Starting browser testing | SKILL.md (this file) |
| Need prompt templates | `references/testing-prompts.md` |
| Need Comet API details | `references/comet-mcp-reference.md` |
| Need context graph usage | `references/context-graph-usage.md` |
| Automating checks | `scripts/pre-check.sh` |
| Running Comet tests | `scripts/browser-test.sh` |
| Storing findings | `scripts/store-findings.sh` |

## Common Workflows

### Quick Health Check (Phase 1 only)

```bash
# Use when: Just checking if apps are running
scripts/pre-check.sh my-app
```

### Full Browser Test (All phases)

```bash
# Use when: Comprehensive testing needed
scripts/pre-check.sh my-app && \
scripts/browser-test.sh visual http://localhost:3000 && \
scripts/store-findings.sh frontend "Issue description"
```

### Regression Test (Phase 1 + 3)

```bash
# Use when: Verifying fixed issue
context_query_traces(query="original issue", category="frontend")
# Then run Phase 2 to verify fix
context_update_outcome(trace_id="...", outcome="success")
```

## Best Practices

| Practice | Why |
|----------|-----|
| Always query context first | Avoid repeating past mistakes |
| Use specific prompts | Generic prompts = false positives |
| Limit comet_poll to 10-15 | Avoid infinite loops |
| Store findings immediately | Don't batch for end of session |
| Use process_logs for logs | 99% token savings vs reading raw |
| Take screenshots for evidence | Visual proof of issues |
| Mark outcomes after fixes | Close the learning loop |

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| MCP tool not found | Comet MCP not installed | Use fallback: `dev-browser` skill or `execute_code` with Playwright |
| Connection failed | Comet MCP not running | Check `.mcp.json` or use fallback |
| Poll limit reached | Task stuck | Use `comet_stop()` and retry with clearer prompt |
| Timeout | Task too complex | Break into smaller steps, increase timeout |

## Token Efficiency Summary

| Method | Tokens Saved |
|--------|--------------|
| Phase 1 server-side checks | 99% (avoid browser when possible) |
| process_logs vs Read tool | 99% (log parsing) |
| Specific prompts vs iterative | 80% (fewer round trips) |
| Context graph queries | Prevents repeated investigations |
