---
name: learning-recommendations
description: "Use when presenting learning recommendations from background analysis, reviewing pending pattern suggestions, or approving automation scripts from traces. Load when learning-agent has findings to present."
---

# Learning Recommendations

Review and act on recommendations from the background learning agent.

## Use When

| Trigger | When |
|---------|------|
| Agent completes analysis | Background learning-agent.py finishes |
| Weekly review | Check accumulated recommendations |
| Pending actions exist | Stored in ~/.claude/learning-recommendations/ |

## Workflow

| Step | Action |
|------|--------|
| 1 | List pending recommendations |
| 2 | Present to user via AskUserQuestion |
| 3 | Execute approved actions |
| 4 | Clear processed recommendations |

## Commands

### List Pending

```bash
# List all pending recommendations
python3 ~/.claude/skills/learning-loop/scripts/learning-agent.py --list-pending

# Check if any exist
ls ~/.claude/learning-recommendations/recommendations_*.json 2>/dev/null
```

### Process Recommendation

For each recommendation, use `AskUserQuestion`:

```python
AskUserQuestion(
    questions=[{
        "question": "New Pattern Detected: {pattern}\n\nFound {count} occurrences. Add to skill references?",
        "header": "Learning",
        "options": [
            {"label": "Add to skill refs", "description": "Update skill with new pattern"},
            {"label": "Skip", "description": "Don't add now"},
            {"label": "Reject", "description": "Not a valid pattern"}
        ],
        "multiSelect": false
    }]
)
```

### Clear Processed

```bash
# Clear all processed recommendations
python3 ~/.claude/skills/learning-loop/scripts/learning-agent.py --clear
```

## Recommendation Types

| Type | Description | Actions |
|------|-------------|---------|
| `pattern` | Repeated successful decision | Add to skill refs, Skip, Reject |
| `automation` | Repeated workflow detected | Create script, Skip |
| `skill` | New skill domain candidate | Create skill, Skip |

## Storage

**Directory**: `~/.claude/learning-recommendations/`

**Format**: `recommendations_YYYYMMDD_HHMMSS.json`

```json
{
  "timestamp": "2026-01-03T22:42:27",
  "recommendations": [
    {
      "type": "pattern",
      "title": "Pattern: deployment",
      "description": "Found 3 occurrences...",
      "data": {...},
      "actions": [...]
    }
  ]
}
```
