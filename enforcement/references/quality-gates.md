# Quality Gates and Verification Loops

Production patterns for enforcing quality at state transitions.

## Spotify Verification Loops

**Source**: [Spotify Engineering - Background on AI Agents Part 3](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3)

### Architecture

- **Deterministic verifiers**: Maven/npm/build/test tools
- **LLM Judge**: Evaluates diff + prompt (prevents scope creep)
- **Stop hooks**: Run all verifiers before PR creation

### Metrics

- Judge vetoes ~25% of agent sessions
- 50% of vetoed sessions successfully course-correct

### Safety Principle

Agent doesn't know what verifiers do internally—only that they can be called. Prevents prompt injection attacks.

---

## tested:true Quality Gate

Block marking feature as tested without evidence.

### Problem

Agents can mark `"tested": true` without running any tests.

### Solution: PreToolUse Hook

```python
#!/usr/bin/env python3
# .claude/hooks/block-tested-true.py

import json
import sys
import os

input_data = json.load(sys.stdin)
tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})

if tool_name not in ["Write", "Edit"]:
    sys.exit(0)

content = tool_input.get("content", "") or tool_input.get("new_string", "")

# Check if marking tested:true
if '"tested": true' in content:
    evidence_dir = "/tmp/test-evidence"
    has_evidence = os.path.exists(evidence_dir) and os.listdir(evidence_dir)

    if not has_evidence:
        print("BLOCKED: Cannot mark tested without evidence", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
```

### Evidence Requirements

| Evidence Type | Acceptable Forms |
|---------------|-----------------|
| Test logs | `/tmp/test-evidence/*.log` |
| Screenshots | `/tmp/test-evidence/*.png` |
| API responses | `/tmp/test-evidence/*.json` |
| Coverage reports | `/tmp/test-evidence/coverage.json` |

---

## State Transition Guards

Block invalid state transitions.

### Guard Functions

```python
def can_transition(from_state, to_state, context):
    """Validate state transition"""

    guards = {
        ("IDLE", "INITIALIZING"): lambda: not has_feature_list(),
        ("INITIALIZING", "CODING"): lambda: has_feature_list() and has_pending_features(),
        ("CODING", "TESTING"): lambda: implementation_complete() and local_tests_pass(),
        ("TESTING", "VERIFYING"): lambda: all_tests_pass() and has_test_evidence(),
        ("TESTING", "CODING"): lambda: tests_failed() and retry_count < 2,
        ("VERIFYING", "COMPLETE"): lambda: all_health_checks_pass(),
    }

    return guards[(from_state, to_state)]()
```

### Implementation in Hooks

```python
#!/usr/bin/env python3
# .claude/hooks/guard-state-transition.py

import json
import sys

input_data = json.load(sys.stdin)

# Read current state
with open(".claude/progress/session-state.json") as f:
    state = json.load(f)

from_state = state["current_state"]
to_state = state["next_state"]

if not can_transition(from_state, to_state, state):
    print(f"BLOCKED: Cannot transition from {from_state} to {to_state}", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
```

---

## Handoff Quality Gates

Verify conditions before agent-to-agent handoff.

### Handoff Checklist

| Element | Verification |
|---------|--------------|
| Preconditions | Files exist, tests pass |
| Artifacts | All required files present |
| Context | Command object valid |

### Implementation

```python
#!/usr/bin/env python3
# .claude/hooks/validate-handoff.py

def validate_handoff(from_agent, to_agent, context):
    """Validate handoff conditions"""

    checks = {
        ("coding", "testing"): [
            lambda: files_exist(context["files"]),
            lambda: tests_pass(context["local_tests"]),
        ],
        ("testing", "verifying"): [
            lambda: all_tests_pass(context["test_results"]),
            lambda: has_evidence(context["evidence_dir"]),
        ],
    }

    for check in checks[(from_agent, to_agent)]:
        if not check():
            return False, check.__doc__

    return True, "OK"
```

---

## Rollback Gates

Automatic rollback on failure detection.

### Rollback Triggers

| Trigger | Action |
|---------|--------|
| Test failure | Return to CODING state |
| Coverage drop | Revert last commit |
| Health check fail | Block deployment |

### Implementation

```python
#!/usr/bin/env python3
# .claude/hooks/auto-rollback.py

import json
import sys
import subprocess

input_data = json.load(sys.stdin)
tool_input = input_data.get("tool_input", {})

# After test run
if "test" in tool_input.get("command", ""):
    result = subprocess.run(["pytest", "--coverage-report"], capture_output=True)

    if result.returncode != 0:
        # Rollback feature-list.json
        with open("feature-list.json") as f:
            features = json.load(f)

        for feature in features:
            if feature["status"] == "testing":
                feature["status"] = "coding"  # Rollback

        with open("feature-list.json", "w") as f:
            json.dump(features, f, indent=2)

sys.exit(0)
```

---

## Quality Gate Checklist

### Orchestration
- [ ] State machine defined with states and transitions
- [ ] Auto-spawning based on state (no user prompt)
- [ ] Feature list or equivalent progress tracker
- [ ] Checkpoint mechanism for session resumption

### Enforcement
- [ ] Quality gates at each transition
- [ ] Hooks that block invalid actions (not just warn)
- [ ] Explicit handoff protocols
- [ ] Output verification before state change
- [ ] Rollback capability on failures

### Anti-Pattern Prevention
- [ ] Progress tracking (prevent no-op loops)
- [ ] Verification requirements (prevent ghosting)
- [ ] Runtime guards (prevent quality drift)
- [ ] Clear state ownership (prevent state explosion)
- [ ] Timeouts (prevent deadlocks)

---

## Key Principle

> **Verification > Trust**

Quality gates prevent cascading failures. All production systems use them.

Sources:
- Spotify Engineering: Verification loops with veto power
- Anthropic: Multi-Agent Research System (enforcement hooks)
