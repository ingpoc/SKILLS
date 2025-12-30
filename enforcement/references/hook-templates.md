# Hook Code Templates

Ready-to-use Python hook templates for common enforcement patterns.

## Template 1: Block tested:true Without Evidence

**File**: `.claude/hooks/block-tested-true.py`
**Event**: PreToolUse

```python
#!/usr/bin/env python3
"""
PreToolUse hook: Blocks marking tested:true without test evidence.
"""

import json
import sys
import os

def main():
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only check Write/Edit tools
    if tool_name not in ["Write", "Edit"]:
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "") or tool_input.get("new_string", "")

    # Only check feature-list.json
    if "feature-list.json" not in file_path:
        sys.exit(0)

    # Check if marking tested:true
    if '"tested": true' in content or '"tested":true' in content:
        evidence_dir = "/tmp/test-evidence"
        has_evidence = os.path.exists(evidence_dir) and os.listdir(evidence_dir)

        if not has_evidence:
            print("BLOCKED: Cannot mark feature as tested without evidence.", file=sys.stderr)
            print("Required: Test logs, screenshots, or API responses in /tmp/test-evidence/", file=sys.stderr)
            sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

**settings.json**:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": { "tool_name": "Write" },
        "hooks": [
          { "type": "command", "command": "python3 .claude/hooks/block-tested-true.py" }
        ]
      },
      {
        "matcher": { "tool_name": "Edit" },
        "hooks": [
          { "type": "command", "command": "python3 .claude/hooks/block-tested-true.py" }
        ]
      }
    ]
  }
}
```

---

## Template 2: Force Tester Completion

**File**: `.claude/hooks/force-tester-completion.py`
**Event**: SubagentStop

```python
#!/usr/bin/env python3
"""
SubagentStop hook: Blocks tester-agent from stopping without running tests.
"""

import json
import sys
import os

def main():
    input_data = json.load(sys.stdin)

    # Agent identification via state file (SubagentStop has no agent_id field)
    agent_state_file = "/tmp/active-agent.json"
    if not os.path.exists(agent_state_file):
        sys.exit(0)

    with open(agent_state_file) as f:
        agent_state = json.load(f)

    # Only enforce for tester-agent
    if agent_state.get("agent") != "tester-agent":
        sys.exit(0)

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

    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Agent-side setup** (in tester-agent prompt):
```markdown
## On Start
```bash
echo '{"agent": "tester-agent", "started": "'$(date -Iseconds)'"}' > /tmp/active-agent.json
```

## On Test Execution
```bash
echo '{"tests_run": N, "tests_passed": M}' > /tmp/test-state.json
```
```

---

## Template 3: Enforce MCP for Large Files

**File**: `.claude/hooks/enforce-mcp-logs.py`
**Event**: PreToolUse

```python
#!/usr/bin/env python3
"""
PreToolUse hook: Blocks Read() on large log files, suggests MCP tool.
"""

import json
import sys
import os

def main():
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name != "Read":
        sys.exit(0)

    file_path = tool_input.get("file_path", "")

    # Check if log file
    if not file_path.endswith(".log"):
        sys.exit(0)

    # Check file size
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        if size > 1000:  # More than 1KB
            print(f"BLOCKED: Log file too large ({size} bytes).", file=sys.stderr)
            print("Use the MCP log processing tool instead:", file=sys.stderr)
            print(f"  mcp__token_efficient__process_logs(file_path='{file_path}')", file=sys.stderr)
            sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Template 4: Block Direct Edits by Orchestrator

**File**: `.claude/hooks/block-direct-edit.py`
**Event**: PreToolUse

```python
#!/usr/bin/env python3
"""
PreToolUse hook: Blocks main orchestrator from editing src/ directly.
Forces delegation to coding-agent.
"""

import json
import sys

def main():
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name not in ["Write", "Edit"]:
        sys.exit(0)

    file_path = tool_input.get("file_path", "")

    # Block edits to src/ directory
    if "/src/" in file_path or file_path.startswith("src/"):
        print("BLOCKED: Orchestrator should not edit src/ directly.", file=sys.stderr)
        print("Delegate to coding-agent instead.", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Template 5: Require Feature List

**File**: `.claude/hooks/require-feature-list.py`
**Event**: PreToolUse

```python
#!/usr/bin/env python3
"""
PreToolUse hook: Blocks coding-agent from starting without feature-list.json.
"""

import json
import sys
import os

def main():
    input_data = json.load(sys.stdin)
    tool_input = input_data.get("tool_input", {})

    # Only check for Write tool on source files
    if tool_input.get("file_path", "").startswith("src/"):
        if not os.path.exists("feature-list.json"):
            print("BLOCKED: No feature-list.json found.", file=sys.stderr)
            print("Run initializer-agent first to create feature list.", file=sys.stderr)
            sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Template 6: Auto-Rollback on Test Failure

**File**: `.claude/hooks/auto-rollback.py`
**Event**: PostToolUse

```python
#!/usr/bin/env python3
"""
PostToolUse hook: Auto-rolls back feature status on test failure.
"""

import json
import sys

def main():
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("tool_name", "")
    tool_result = input_data.get("tool_result", {})

    # Only check after test execution
    if tool_name != "Bash" or "pytest" not in str(tool_result):
        sys.exit(0)

    # Check if tests failed
    if "failed" in str(tool_result).lower() or tool_result.get("exit_code", 0) != 0:
        # Rollback feature-list.json
        try:
            with open("feature-list.json") as f:
                features = json.load(f)

            for feature in features:
                if feature["status"] == "testing":
                    feature["status"] = "coding"  # Rollback

            with open("feature-list.json", "w") as f:
                json.dump(features, f, indent=2)

            print("Auto-rollback: Testing feature marked as coding", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Could not rollback: {e}", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Hook Development Tips

### Testing Hooks

```bash
# Test hook manually
echo '{"tool_name": "Write", "tool_input": {"file_path": "feature-list.json", "content": "{\"tested\": true}"}}' | python3 .claude/hooks/block-tested-true.py
```

### Debugging Hooks

```python
# Add debug logging
import logging
logging.basicConfig(filename="/tmp/hook-debug.log", level=logging.DEBUG)
logging.debug(f"Hook input: {input_data}")
```

### Common Pitfalls

1. **Forgot sys.exit(0)** - Hook always blocks
2. **Wrong matcher** - Hook never runs
3. **Missing execute permissions** - `chmod +x hook.py`
4. **Parsing JSON wrong** - Use `json.load(sys.stdin)`

### Permissions

```bash
# Make hooks executable
chmod +x .claude/hooks/*.py
```

---

## settings.json Full Example

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": { "tool_name": "Write" },
        "hooks": [
          { "type": "command", "command": "python3 .claude/hooks/block-tested-true.py" },
          { "type": "command", "command": "python3 .claude/hooks/block-direct-edit.py" },
          { "type": "command", "command": "python3 .claude/hooks/require-feature-list.py" }
        ]
      },
      {
        "matcher": { "tool_name": "Read" },
        "hooks": [
          { "type": "command", "command": "python3 .claude/hooks/enforce-mcp-logs.py" }
        ]
      },
      {
        "matcher": { "tool_name": "Edit" },
        "hooks": [
          { "type": "command", "command": "python3 .claude/hooks/block-tested-true.py" }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          { "type": "command", "command": "python3 .claude/hooks/force-tester-completion.py" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          { "type": "command", "command": "python3 .claude/hooks/auto-rollback.py" }
        ]
      }
    ]
  }
}
```
