# Comet MCP Reference

Reference documentation for the Comet/Perplexity MCP bridge tools.

## Overview

Comet MCP provides browser automation through Perplexity's browser capabilities. It's useful for testing web applications, verifying UI implementations, and debugging browser-specific issues.

## Available Tools

### comet_connect

Connect to the Comet browser session.

**Parameters:** None

**Usage:**

```
mcp__comet-bridge__comet_connect()
```

**When to use:**

- Once per session before running tests
- If connection was lost

**Returns:** Connection status

---

### comet_ask

Send a task to the Comet browser to execute autonomously.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| prompt | string | Yes | - | Task description for Comet to execute |
| newChat | boolean | No | false | Start fresh session (clears context) |
| timeout | number | No | 15000 | Max wait time in milliseconds |

**Usage:**

```
# Fresh session for clean test
mcp__comet-bridge__comet_ask(
  prompt="Navigate to http://localhost:3000 and verify X",
  newChat=true,
  timeout=30000
)

# Continue existing session
mcp__comet-bridge__comet_ask(
  prompt="Now click the login button",
  timeout=15000
)
```

**Best practices:**

- Use `newChat=true` for independent tests
- Use specific prompts (see testing-prompts.md)
- Set timeout based on task complexity
- 30s for simple navigation, 60s for complex flows

**Returns:** Task completion result

---

### comet_poll

Check the status of a running Comet task.

**Parameters:** None

**Usage:**

```
# Poll until complete (limit to 10-15 polls)
for i in {1..15}; do
  mcp__comet-bridge__comet_poll
  # Check if complete, break if done
done
```

**Best practices:**

- Limit to 10-15 polls max
- Add 1-2 second delays between polls
- Break early if task completes
- Timeout after ~30 seconds total

**Returns:** Current task status and progress

---

### comet_screenshot

Capture a screenshot of the current browser state.

**Parameters:** None

**Usage:**

```
mcp__comet-bridge__comet_screenshot()
```

**When to use:**

- After navigation to verify page load
- After interactions to verify UI changes
- For bug evidence and documentation
- When console output is unclear

**Returns:** Screenshot image data

---

### comet_stop

Stop the currently running Comet task.

**Parameters:** None

**Usage:**

```
mcp__comet-bridge__comet_stop()
```

**When to use:**

- Task is going off track
- Infinite loop detected
- Need to abort and retry

**Returns:** Stop confirmation

---

### comet_mode

Switch Perplexity search mode.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mode | string | No | Mode: search, research, labs, learn |

**Modes:**

| Mode | Use For |
|------|---------|
| search | Basic web queries |
| research | Deep research with multiple sources |
| labs | Analytics and visualization |
| learn | Educational content |

**Usage:**

```
mcp__comet-bridge__comet_mode(mode="research")
```

**When to use:**

- Default (search) is fine for most testing
- Use research for complex debugging
- Use labs for performance analysis

**Returns:** Current mode

---

## Common Workflows

### Basic Page Load Test

```
# 1. Connect
comet_connect()

# 2. Navigate and test
comet_ask(
  prompt="Navigate to http://localhost:3000 and report: page load status, console errors, visible elements",
  newChat=true,
  timeout=30000
)

# 3. Capture screenshot
comet_screenshot()
```

### Multi-Step Interaction Test

```
# 1. Connect and navigate
comet_connect()
comet_ask(
  prompt="Navigate to http://localhost:3000/login",
  newChat=true,
  timeout=30000
)

# 2. Poll for completion
comet_poll()

# 3. Continue interaction (no newChat)
comet_ask(
  prompt="Click the login button and describe what happens",
  timeout=30000
)

# 4. Screenshot result
comet_screenshot()
```

### Debug Session

```
# 1. Connect
comet_connect()

# 2. Navigate to error state
comet_ask(
  prompt="Navigate to http://localhost:3000/page-with-error",
  newChat=true,
  timeout=30000
)

# 3. Check console
comet_ask(
  prompt="Open browser console and list all errors",
  timeout=15000
)

# 4. Screenshot for evidence
comet_screenshot()

# 5. If needed, stop and retry
comet_stop()
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Connection failed | Comet not running | Check MCP server status |
| Timeout expired | Task too long | Increase timeout or simplify task |
| Poll limit reached | Task not completing | Stop and retry with clearer prompt |
| Vague response | Prompt too generic | Use specific prompt templates |

## Integration with Other MCPs

### With token-efficient MCP

```
# Parse server logs first (99% savings)
process_logs(file_path="app.log", pattern="ERROR", limit=20)

# Then use Comet for visual verification
comet_ask(prompt="Navigate and check for specific errors")
```

### With context-graph MCP

```
# Check for similar issues first
context_query_traces(query="login button not working", category="frontend")

# Run Comet test
comet_ask(prompt="Test login button functionality")

# Store findings
context_store_trace(
  decision="Login button issue: {details}",
  category="frontend",
  outcome="pending"
)
```

## Limitations

| Limitation | Workaround |
|------------|------------|
| No direct JavaScript execution | Use prompts to ask Comet to run JS |
| Cannot access browser extensions | Test without extensions or note limitation |
| Limited to web content | Cannot test local files directly |
| Session state not persistent | Use newChat=false to maintain state |

## Tips

1. **Be specific in prompts**: Generic prompts produce vague results
2. **Use newChat strategically**: true for independent tests, false for related steps
3. **Limit polling**: 10-15 polls max to avoid infinite loops
4. **Capture screenshots**: Essential for bug evidence and documentation
5. **Check console**: Always ask for console errors when debugging
6. **Combine with server logs**: Use process_logs MCP for comprehensive view
