# Browser Testing Patterns

Test scenarios and debugging strategies for browser automation.

## Test Scenario Patterns

### Pattern 1: Local Development Testing

**Flow**: Navigate → Interact → Verify → Report

```
1. Navigate to localhost:3000
2. Interact with element (click, type, submit)
3. Verify expected result (error message, redirect, state change)
4. Report findings
```

**Example prompt**:
```
I just updated the login form validation. Open localhost:3000,
try submitting with invalid data, and check if error messages
appear correctly.
```

**When to use**: After code changes, during development iteration

---

### Pattern 2: Console Debugging

**Flow**: Navigate → Read console → Filter patterns → Diagnose

```
1. Navigate to page
2. Read console messages with pattern filter
3. Identify errors/warnings
4. Diagnose root cause
```

**Example prompts**:
```
# General errors
Open the dashboard and check console for errors on load.

# Specific pattern
Check console for ERROR or CRITICAL messages after clicking submit.

# API failures
Look for failed network requests in console when loading the user profile.
```

**Console filtering patterns**:
| Pattern | Purpose |
|---------|---------|
| `ERROR` | All errors |
| `ERROR|WARN` | Errors and warnings |
| `404|500` | HTTP status codes |
| `TypeError|ReferenceError` | JavaScript errors |
| `myApp` | Application-specific logs |

---

### Pattern 3: Form Validation Testing

**Flow**: Navigate → Fill form → Submit → Verify

```
1. Navigate to form URL
2. Find form fields
3. Fill with test data (valid/invalid)
4. Submit form
5. Verify validation (error messages, success state)
```

**Test cases**:
| Test | Input | Expected |
|------|-------|----------|
| Empty required field | Leave blank | Error message |
| Invalid email | `test@` | Format error |
| Short password | `abc` | Min length error |
| Valid data | Complete form | Success/redirect |

---

### Pattern 4: UI Verification

**Flow**: Reference design → Navigate → Compare → Report

```
1. Reference design/Figma mock
2. Navigate to implementation
3. Compare visual elements
4. Report differences
```

**Example prompt**:
```
I built this login page based on the Figma mock. Open localhost:3000/login
and verify it matches: button placement, field labels, error message styles.
```

---

### Pattern 5: Authenticated Workflow

**Flow**: Use browser login → Navigate → Test

```
1. Use existing browser session (already logged in)
2. Navigate to authenticated page
3. Test functionality
4. Verify permissions/state
```

**Example prompt**:
```
Go to my Google Doc at docs.google.com/document/d/abc123,
read the content, and add a summary paragraph at the end.
```

**Works with**: Gmail, Notion, Google Docs, any site you're logged into

---

### Pattern 6: Data Extraction

**Flow**: Navigate → Read content → Extract structure → Save

```
1. Navigate to target page
2. Read page content
3. Extract structured data
4. Save as CSV/JSON
```

**Example prompt**:
```
Go to the product listings page, extract name, price, availability
for each item, and save results as products.csv.
```

---

### Pattern 7: Multi-Site Workflow

**Flow**: Site A → Gather data → Site B → Use data

```
1. Navigate to site A
2. Extract information
3. Navigate to site B
4. Use extracted data
```

**Example prompt**:
```
Check my calendar for meetings tomorrow, then for each external attendee,
look up their company on LinkedIn and add a note about what they do.
```

---

## Debugging Strategies

### Strategy 1: Console Pattern Filtering

**Problem**: Console logs are verbose (1000+ lines)
**Solution**: Filter by specific pattern

```
# Instead of:
"Read all console logs"

# Use:
"Read console logs, filter for ERROR patterns only"
"Check console for TypeError or ReferenceError"
"Show console messages matching 'api' or 'fetch'"
```

### Strategy 2: Network Request Analysis

**Use when**: API calls failing, unexpected responses

```
"Check network requests for failed API calls when loading the dashboard"
"Look for 4xx or 5xx responses in network requests after form submission"
```

### Strategy 3: Element Finding

**Problem**: Don't know element selector
**Solution**: Natural language search

```
# Instead of:
"Click #submit-button-12345"

# Use:
"Find the submit button and click it"
"Locate the email input field"
"Search for the 'Sign Up' button"
```

### Strategy 4: Screenshot Verification

**Use when**: Visual regression, state confirmation

```
"Take a screenshot after clicking submit to verify the success message"
"Screenshot the page and confirm the modal appeared"
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | Solution |
|--------------|--------------|----------|
| Triggering alerts | JavaScript alerts block all browser events | Avoid elements that trigger alerts/prompts/confirms |
| Reading all logs | 1000+ lines, overwhelms context | Filter by pattern: `pattern: "ERROR|WARN"` |
| No tab ID | Commands fail without context | Always call `tabs_context_mcp` first |
| Testing while developing | Race conditions with file changes | Stop dev server, test stable build |
| Fragile selectors | `#button-12345` breaks with changes | Use natural language: "find submit button" |

---

## Test Organization

### Test Categories

| Category | Focus | Example |
|----------|-------|---------|
| **Smoke tests** | Critical paths | Login, checkout, signup |
| **Regression tests** | Recent bugs | Verify fix still works |
| **Validation tests** | Form rules | Email format, required fields |
| **Console tests** | Error-free load | No 404s, no JS errors |
| **Network tests** | API calls | Successful responses |

### Test Evidence

For `tested:true` verification, collect:

| Evidence Type | How to Collect |
|---------------|----------------|
| Screenshots | `computer: screenshot` action |
| Console output | `read_console_messages` with pattern |
| Network logs | `read_network_requests` |
| GIF recording | `gif_creator` for demo |
| Page text | `get_page_text` or `read_page` |

---

## Integration with Agent Harness

### Tester-Agent Workflow

```
[Coding Agent]
    │
    │ "Feature implemented, ready for testing"
    │
    ▼
[Tester Agent - Browser Testing]
    │
    │ 1. Navigate to localhost:3000
    │ 2. Execute test scenarios
    │ 3. Collect evidence (screenshots, console logs)
    │ 4. Report findings
    │
    ▼
[Decision]
    │
    ├─ Pass → Update feature-list.json: tested:true
    └─ Fail → Report bugs → Resume coding agent
```

### Quality Gates

| Gate | Verification |
|------|-------------|
| No console errors | `read_console_messages(pattern: "ERROR")` returns empty |
| Forms validate | Test with invalid data, verify errors appear |
| API calls succeed | `read_network_requests` shows 200 responses |
| UI matches design | Screenshot compared to mock |

---

## Prompt Templates

### Template 1: Basic Page Test
```
Navigate to {URL}, check console for errors, and report if the page loads correctly.
```

### Template 2: Form Validation
```
Go to {URL}, find the {form_name} form, submit with {invalid_data},
and verify error messages appear.
```

### Template 3: Console Debug
```
Open {URL}, trigger the {action} action, then check console for
{pattern} messages.
```

### Template 4: Regression Test
```
Test the fix for {bug_description}: Go to {URL}, perform {steps},
and verify {expected_result}.
```

### Template 5: Data Extraction
```
Navigate to {URL}, extract {fields} from {items}, and save as {format}.
```

---

## Sources

- [Claude Code Chrome Documentation](https://code.claude.com/docs/en/chrome)
- Chrome extension: Claude in Chrome v1.0.36+
