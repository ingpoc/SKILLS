# Blocking Hook Mechanisms

Technical patterns for hooks that block invalid actions.

## Research Confirmed: Hooks CAN Block Actions

Verified mechanisms from Claude Code docs and testing:

| Mechanism | How | Effect | Hook Events |
|-----------|-----|--------|-------------|
| **Exit code 2** | `exit 2` + stderr message | Blocks action, feeds stderr to Claude | PreToolUse, SubagentStop |
| **JSON decision** | `"permissionDecision": "deny"` | Structured blocking with reason | SubagentStop |
| **Parameter modification** | `updatedInput` field (v2.0.10+) | Modify tool params before execution | PreToolUse |
| **Stop blocking** | `"decision": "block"` | Forces agent to continue working | SubagentStop |

## Hook Timing Points

| Event | Can Block? | Use Case |
|-------|------------|----------|
| **PreToolUse** | ✅ Yes | Block writes, validate state changes |
| **PermissionRequest** | ✅ Yes | Custom approval logic |
| **Stop/SubagentStop** | ✅ Yes | Force continuation until quality gates pass |
| **PostToolUse** | ❌ No | Feedback only (tool already ran) |

**Limitation**: Cannot stop mid-execution. Hooks fire at decision points only.

---

## Exit Code 2 Pattern

Most common blocking pattern for PreToolUse hooks.

### How It Works

```python
#!/usr/bin/env python3
import sys

# Block action
print("BLOCKED: Reason for blocking", file=sys.stderr)
sys.exit(2)  # Exit code 2 = blocking error
```

### Example: Block tested:true Without Evidence

```python
#!/usr/bin/env python3
# .claude/hooks/block-tested-true.py
# PreToolUse hook - blocks marking tested:true without evidence

import json
import sys
import os

input_data = json.load(sys.stdin)
tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})

# Only check Write/Edit to feature files
if tool_name not in ["Write", "Edit"]:
    sys.exit(0)

file_path = tool_input.get("file_path", "")
content = tool_input.get("content", "") or tool_input.get("new_string", "")

if "feature-list.json" not in file_path:
    sys.exit(0)

# Check if marking tested:true
if '"tested": true' in content or '"tested":true' in content:
    # Look for test evidence in session
    evidence_dir = "/tmp/test-evidence"
    has_evidence = os.path.exists(evidence_dir) and os.listdir(evidence_dir)

    if not has_evidence:
        print("BLOCKED: Cannot mark feature as tested without evidence.", file=sys.stderr)
        print("Required: Test logs, screenshots, or API responses in /tmp/test-evidence/", file=sys.stderr)
        sys.exit(2)  # Exit 2 = blocking error

sys.exit(0)
```

### settings.json Configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": { "tool_name": "Write" },
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/block-tested-true.py"
          }
        ]
      }
    ]
  }
}
```

---

## JSON Decision Pattern

Structured blocking with reason for SubagentStop hooks.

### Challenge: SubagentStop Has No Agent ID

SubagentStop input fields:
- ✅ session_id, transcript_path, permission_mode, stop_hook_active
- ❌ agent_id, agent_name, agent_type (missing!)

### Solution: State File Handshake

Agents write identity on start, hooks read it.

```python
#!/usr/bin/env python3
# .claude/hooks/force-tester-completion.py
# SubagentStop hook - blocks tester from stopping without results

import json
import sys
import os

input_data = json.load(sys.stdin)

# Agent identification via state file
agent_state_file = "/tmp/active-agent.json"
if not os.path.exists(agent_state_file):
    sys.exit(0)  # No agent state, allow stop

with open(agent_state_file) as f:
    agent_state = json.load(f)

# Only enforce for tester-agent
if agent_state.get("agent") != "tester-agent":
    sys.exit(0)  # Not tester, allow stop

# Check test evidence
test_state_file = "/tmp/test-state.json"
if os.path.exists(test_state_file):
    with open(test_state_file) as f:
        test_state = json.load(f)
else:
    test_state = {"tests_run": 0, "tests_passed": 0}

# Block if no tests were actually run
if test_state.get("tests_run", 0) == 0:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SubagentStop",
            "decision": "block",
            "reason": "No tests executed. Run at least one test before stopping."
        }
    }
    print(json.dumps(output))
    sys.exit(0)

# Allow stop if tests ran
sys.exit(0)
```

### Agent-Side Requirement

```markdown
## On Start
Write agent identity:
```bash
echo '{"agent": "tester-agent", "started": "'$(date -Iseconds)'"}' > /tmp/active-agent.json
```

## On Test Execution
Update test state:
```bash
echo '{"tests_run": N, "tests_passed": M}' > /tmp/test-state.json
```
```

---

## Parameter Modification Pattern (v2.0.10+)

Modify tool parameters before execution.

```python
#!/usr/bin/env python3
# .claude/hooks/enforce-safe-paths.py
# PreToolUse hook - modifies file paths to safe locations

import json
import sys
import os

input_data = json.load(sys.stdin)
tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})

if tool_name == "Write":
    file_path = tool_input.get("file_path", "")

    # Force summaries to /tmp/summary/
    if "summary" in file_path.lower() and not file_path.startswith("/tmp/"):
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": "Redirecting summary to /tmp/summary/",
                "updatedInput": {
                    "file_path": f"/tmp/summary/{os.path.basename(file_path)}"
                }
            }
        }
        print(json.dumps(output))
        sys.exit(0)

sys.exit(0)
```

---

## Common Hook Patterns

| Hook | Event | Trigger | Action |
|------|-------|---------|--------|
| `block-tested-true.py` | PreToolUse | Write with tested:true | Verify evidence exists |
| `force-tester-completion.py` | SubagentStop | tester tries to stop | Block until tests pass |
| `enforce-mcp-logs.py` | PreToolUse | Read() on large log file | Deny, suggest MCP |
| `block-direct-edit.py` | PreToolUse | Opus edits src/ directly | Deny, suggest coding-agent |
| `require-feature-list.py` | PreToolUse | coding-agent starts | Check feature-list exists |
