# Browser Testing Patterns

## Prerequisites

| Requirement | Minimum Version |
|-------------|-----------------|
| Chrome extension | 1.0.36+ |
| Claude Code CLI | 2.0.73+ |
| Plan | Pro, Team, or Enterprise |

## Browser Test Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   BROWSER TEST SEQUENCE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. SETUP                                                    │
│     ├── Get tab context (tabs_context_mcp)                  │
│     └── Create new tab (tabs_create_mcp)                    │
│                                                              │
│  2. NAVIGATE                                                 │
│     └── Go to URL (navigate)                                │
│                                                              │
│  3. INTERACT                                                 │
│     ├── Find elements (find)                                │
│     ├── Fill forms (form_input)                             │
│     ├── Click/type (computer)                               │
│     └── Wait for state                                      │
│                                                              │
│  4. VERIFY                                                   │
│     ├── Check console (read_console_messages)               │
│     ├── Screenshot (computer: screenshot)                   │
│     ├── Read page content (read_page, get_page_text)        │
│     └── Check network (read_network_requests)               │
│                                                              │
│  5. EVIDENCE                                                 │
│     └── Save screenshots, logs to /tmp/test-evidence/       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Test Patterns

### Pattern 1: Page Load Test

**Verify page loads without errors**

```
1. Navigate to URL
2. Wait for load
3. Check console for errors (pattern: "ERROR")
4. Screenshot the result
5. Report findings
```

```
Prompt: "Navigate to localhost:3000, check console for errors,
and screenshot the result"
```

### Pattern 2: Form Validation Test

**Verify form validates correctly**

```
1. Navigate to form page
2. Submit with invalid data
3. Verify error messages appear
4. Submit with valid data
5. Verify success state
```

| Test Case | Input | Expected |
|-----------|-------|----------|
| Empty required | Leave blank | "Required" error |
| Invalid email | `test@` | "Invalid email" error |
| Short password | `abc` | "Min 8 chars" error |
| Valid data | Complete form | Success/redirect |

### Pattern 3: Console Debug Test

**Find and diagnose JavaScript errors**

```
1. Navigate to page
2. Trigger action (click, submit)
3. Read console with pattern filter
4. Report errors found
```

**Filter patterns:**

| Pattern | Purpose |
|---------|---------|
| `ERROR` | All errors |
| `ERROR\|WARN` | Errors and warnings |
| `TypeError\|ReferenceError` | JS errors |
| `404\|500` | HTTP errors |

### Pattern 4: UI Verification Test

**Compare implementation to design**

```
1. Reference design (Figma, mockup)
2. Navigate to implementation
3. Screenshot
4. Compare visual elements
5. Report differences
```

### Pattern 5: Authenticated Test

**Test with existing browser session**

```
1. Use browser (already logged in)
2. Navigate to authenticated page
3. Verify access
4. Test functionality
```

**Works with:** Gmail, Notion, Google Docs, any logged-in site

## Available MCP Tools

| Tool | Purpose |
|------|---------|
| `tabs_context_mcp` | Get tab context (required first) |
| `tabs_create_mcp` | Create new tab |
| `navigate` | Go to URL |
| `computer` | Click, type, screenshot, scroll |
| `find` | Find element by description |
| `form_input` | Fill form field |
| `read_page` | Read DOM/accessibility tree |
| `get_page_text` | Extract text content |
| `read_console_messages` | Debug with pattern filter |
| `read_network_requests` | Monitor API calls |
| `gif_creator` | Record session |

## Evidence Collection

### Screenshot

```python
# Take screenshot
result = mcp__claude_in_chrome__computer(
    action="screenshot",
    tabId=tab_id
)
# Save to evidence directory
```

### Console Logs

```python
# Read errors only
result = mcp__claude_in_chrome__read_console_messages(
    tabId=tab_id,
    pattern="ERROR|WARN",
    limit=50
)
```

### Network Requests

```python
# Check for failed requests
result = mcp__claude_in_chrome__read_network_requests(
    tabId=tab_id,
    urlPattern="/api/"
)
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Triggering alerts | JS alerts block browser | Avoid alert-triggering elements |
| Reading all logs | Context overflow | Filter by pattern |
| No tab context | Commands fail | Always call tabs_context_mcp first |
| Fragile selectors | Break with changes | Use natural language find |
| Testing during hot reload | Race conditions | Test stable build |

## Test Script

```bash
#!/bin/bash
# scripts/run-browser-tests.sh

# Start server
npm start &
SERVER_PID=$!
sleep 5

# Run browser tests (via Claude)
echo "Browser tests require manual Claude interaction"
echo "Server running at localhost:3000"
echo "Press Enter when tests complete..."
read

# Cleanup
kill $SERVER_PID

# Check for evidence
if [ -f "/tmp/test-evidence/browser-test.json" ]; then
    cat /tmp/test-evidence/browser-test.json
    exit 0
else
    echo "No browser test evidence found"
    exit 1
fi
```

## Quality Gates

| Gate | How to Verify |
|------|---------------|
| No console errors | `read_console_messages(pattern: "ERROR")` returns empty |
| Forms validate | Submit invalid data, verify errors |
| API calls succeed | `read_network_requests` shows 200s |
| UI matches design | Screenshot comparison |
| Actions complete | Expected state after interaction |

## Integration with Agent Harness

```
[Implementation Complete]
        │
        ▼
[Load testing/ skill]
        │
        ├── Run unit tests (unit-testing.md)
        ├── Run API tests (api-testing.md)
        └── Run browser tests (this file)
        │
        ▼
[Collect Evidence]
        │
        ├── /tmp/test-evidence/unit-tests.json
        ├── /tmp/test-evidence/api-tests.json
        ├── /tmp/test-evidence/browser-test.json
        └── /tmp/test-evidence/screenshots/
        │
        ▼
[All Pass] → Mark tested:true
[Any Fail] → Return to IMPLEMENT
```

## Sources

- [Claude Code Chrome Documentation](https://code.claude.com/docs/en/chrome)
- Chrome extension: Claude in Chrome v1.0.36+
