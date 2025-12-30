# State Machine Patterns

## States

```
┌─────────────────────────────────────────────────────────────┐
│                    SESSION STATE MACHINE                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [START] ──────────────────────────────────────────────────▶│
│     │                                                        │
│     ▼                                                        │
│  ┌──────────────┐                                           │
│  │ CHECK STATE  │                                           │
│  └──────┬───────┘                                           │
│         │                                                    │
│    ┌────┴────┐                                              │
│    │         │                                              │
│    ▼         ▼                                              │
│  [INIT]   [IMPLEMENT] ◀─────────────────┐                   │
│    │         │                          │                   │
│    │         ▼                          │                   │
│    │      [TEST] ───────────────────────┤                   │
│    │         │         (failed)         │                   │
│    │         ▼                          │                   │
│    │    ┌────────┐                      │                   │
│    │    │ PASS?  │──── NO ──────────────┘                   │
│    │    └────┬───┘                                          │
│    │         │ YES                                          │
│    │         ▼                                              │
│    └───▶ [COMPLETE]                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## State Definitions

| State | Entry Condition | Skill Loaded | Exit Condition |
|-------|-----------------|--------------|----------------|
| **START** | Session begins | orchestrator/ | State checked |
| **INIT** | No feature-list.json | initialization/ | feature-list.json created |
| **IMPLEMENT** | Pending feature exists | implementation/ | Code complete, tests written |
| **TEST** | Implementation complete | testing/ | All tests pass (code verified) |
| **COMPLETE** | All features tested | - | Session ends |

## Valid Transitions

```python
VALID_TRANSITIONS = {
    "START": ["INIT", "IMPLEMENT"],      # INIT if no feature-list, else IMPLEMENT
    "INIT": ["IMPLEMENT"],                # Must implement after init
    "IMPLEMENT": ["TEST"],                # Must test after implement
    "TEST": ["IMPLEMENT", "COMPLETE"],    # Back to fix, or complete
    "COMPLETE": []                        # Terminal state
}
```

## Invalid Transitions (Blocked by Hooks)

| From | To | Why Blocked |
|------|-----|-------------|
| INIT | COMPLETE | Skips implementation and testing |
| IMPLEMENT | COMPLETE | Skips testing |
| TEST | COMPLETE | Without passing tests (code verified) |
| Any | START | Cannot restart |

## State File Schema

```json
// .claude/progress/state.json
{
  "state": "IMPLEMENT",
  "feature_id": "PT-003",
  "entered_at": "2025-12-28T10:00:00Z",
  "attempts": 1,
  "context": {
    "files_changed": ["src/feature.py"],
    "tests_written": ["tests/test_feature.py"]
  },
  "history": [
    {"state": "START", "at": "2025-12-28T09:55:00Z"},
    {"state": "INIT", "at": "2025-12-28T09:56:00Z"}
  ]
}
```

## Transition Protocol

```markdown
## Before Transition
1. Verify exit conditions met (code execution, not judgment)
2. Update state.json with new state
3. Hook validates transition is allowed

## After Transition
1. Load skill for new state
2. Read any context from previous state
3. Begin state procedures
```

## State Entry Scripts

```bash
# scripts/enter-init.sh
#!/bin/bash
echo '{"state": "INIT", "entered_at": "'$(date -Iseconds)'"}' > .claude/progress/state.json

# scripts/enter-implement.sh
#!/bin/bash
FEATURE_ID=$(jq -r '.features[] | select(.status=="pending") | .id' .claude/progress/feature-list.json | head -1)
echo '{"state": "IMPLEMENT", "feature_id": "'$FEATURE_ID'", "entered_at": "'$(date -Iseconds)'", "attempts": 1}' > .claude/progress/state.json

# scripts/enter-test.sh
#!/bin/bash
CURRENT=$(cat .claude/progress/state.json)
echo "$CURRENT" | jq '.state = "TEST" | .entered_at = "'$(date -Iseconds)'"' > .claude/progress/state.json
```

## Retry Logic

| Condition | Action |
|-----------|--------|
| TEST failed, attempts < 3 | Return to IMPLEMENT, increment attempts |
| TEST failed, attempts >= 3 | Mark feature blocked, move to next |
| IMPLEMENT stuck > 30 min | Trigger compression, continue |

```python
# Retry decision
if state == "TEST" and not tests_passed:
    attempts = state_data.get("attempts", 1)
    if attempts < 3:
        transition_to("IMPLEMENT", attempts=attempts + 1)
    else:
        mark_feature_blocked(feature_id)
        transition_to("IMPLEMENT", feature_id=next_pending())
```
