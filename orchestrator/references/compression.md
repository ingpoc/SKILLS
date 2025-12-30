# Context Compression Patterns

## When to Compress

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Context capacity | Progressive (see below) | Level-based compression |
| Tool output | > 5K tokens | Summarize before adding |
| State transition | After TEST | Clear test artifacts |
| Session duration | > 30 min active | Proactive compression |

---

## Progressive Compression Checkpoints

**From autonomous-coding analysis**: Multi-level checkpoints prevent overflow and maximize token efficiency.

```
┌─────────────────────────────────────────────────────────────┐
│           PROGRESSIVE COMPRESSION LEVELS                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  50% ─────────────────────────────────────────────────────   │
│     Checkpoint: Save state + summary (lightweight)           │
│                                                              │
│  70% ─────────────────────────────────────────────────────   │
│     Checkpoint: Remove raw outputs, keep summaries           │
│                                                              │
│  80% ─────────────────────────────────────────────────────   │
│     Level 1: Remove raw tool outputs                        │
│                                                              │
│  85% ─────────────────────────────────────────────────────   │
│     Level 2: Summarize historical context                    │
│                                                              │
│  90% ─────────────────────────────────────────────────────   │
│     Level 3: Full compression to 2K tokens                   │
│                                                              │
│  95% ─────────────────────────────────────────────────────   │
│     Emergency: Preserve only current state                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Checkpoint Strategy

| Threshold | Action | Target Tokens | Preserves |
|-----------|--------|---------------|-----------|
| **50%** | Save checkpoint | 0 (metadata) | State + decisions |
| **70%** | Pre-compression | Current | Remove raw outputs |
| **80%** | Level 1 | Current - 10% | Remove raw tool outputs |
| **85%** | Level 2 | Current - 30% | Summarize old conversations |
| **90%** | Level 3 | ~2K | Full compression |
| **95%** | Emergency | ~1K | Current state only |

**Key insight**: Compressing gradually at 80/85/90% is more efficient than waiting for emergency at 95%.

## Compression Strategy

From [Cognition AI](https://cognition.ai/blog/dont-build-multi-agents):

> "Introduce a specialized compression model that distills conversation history into key details, events, and decisions."

### What to Preserve

| Category | Examples | Priority |
|----------|----------|----------|
| **Decisions** | Architecture choices, API design | Critical |
| **Current state** | Active feature, test status | Critical |
| **Recent files** | Last 5 files modified | High |
| **Unresolved issues** | Bugs, blockers, TODOs | High |
| **User preferences** | Stated requirements | Medium |

### What to Discard

| Category | Examples | When |
|----------|----------|------|
| **Raw tool output** | Full file contents | After processed |
| **Verbose logs** | Build output, stack traces | After analyzed |
| **Historical context** | Old conversations | After summarized |
| **Redundant reads** | Same file read multiple times | Keep latest |
| **Failed attempts** | Code that didn't work | After lesson extracted |

## Compression Prompt

```markdown
Compress the conversation to essential context:

## Required Output (target: 2000 tokens)

### Current State
- State: [INIT/IMPLEMENT/TEST/COMPLETE]
- Feature: [ID and description]
- Progress: [What's done, what remains]

### Key Decisions Made
1. [Decision 1 with rationale]
2. [Decision 2 with rationale]

### Files Recently Modified
- [file1.py] - [what was changed]
- [file2.py] - [what was changed]

### Unresolved Issues
- [ ] [Issue 1]
- [ ] [Issue 2]

### Next Action
[Specific next step]

## Discard
- Raw file contents (reference by path instead)
- Build/test output (keep only summary)
- Superseded attempts
- Verbose explanations
```

## Progressive Compression

```
Checkpoint 50%: Save state + summary (lightweight, no compression)
Checkpoint 70%: Remove raw outputs, keep summaries
Level 1 (80%): Remove raw tool outputs
Level 2 (85%): Summarize historical context
Level 3 (90%): Full compression to 2K tokens
Emergency (95%): Preserve only current state
```

## Implementation

```python
def should_compress(context_usage: float) -> str:
    """
    Determine compression level based on context usage.
    Returns compression action or None.
    """
    if context_usage > 0.95:
        return "emergency"
    elif context_usage > 0.90:
        return "full"
    elif context_usage > 0.85:
        return "summarize"
    elif context_usage > 0.80:
        return "remove_raw"
    elif context_usage > 0.70:
        return "pre_compress"
    elif context_usage > 0.50:
        return "checkpoint"
    return None

def compress_context(level: str) -> str:
    if level == "checkpoint":
        # Save lightweight checkpoint (no compression)
        return save_checkpoint(
            summary=generate_lightweight_summary(),
            state=get_current_state()
        )

    elif level == "pre_compress":
        # Remove raw outputs early (pre-compression)
        return remove_raw_outputs(context)

    elif level == "remove_raw":
        # Remove raw tool outputs, keep summaries
        return remove_raw_outputs(context)

    elif level == "summarize":
        # Summarize old conversations
        return summarize_history(context, keep_recent=5)

    elif level == "full":
        # Full compression to 2K tokens
        return llm_compress(context, target_tokens=2000)

    elif level == "emergency":
        # Preserve only current state
        return extract_current_state(context)

def save_checkpoint(summary: str, state: dict) -> None:
    """
    Save lightweight checkpoint at 50% context.
    """
    checkpoint = {
        "timestamp": datetime.now().isoformat(),
        "context_usage": get_context_usage(),
        "summary": summary,
        "state": state,
        "recent_files": get_recent_files(n=5)
    }
    write_file(".claude/progress/checkpoint.json", json.dumps(checkpoint))
```

**Usage:**
```python
# Monitor context usage periodically
usage = get_context_usage()
action = should_compress(usage)

if action:
    result = compress_context(action)
    print(f"Compressed: {action} → saved {result['tokens_saved']} tokens")
```

## Token Tracking

Track compression effectiveness with built-in scripts:

```bash
# Before compression: record current token count
./.claude/progress/compress-context.sh full 85000

# After compression: record savings
./.claude/progress/track-tokens.sh 85000 12000 "full_compression"

# View summary statistics
./.claude/progress/token-summary.sh
```

**Output:**
```json
{
  "label": "full_compression",
  "tokens_before": 85000,
  "tokens_after": 12000,
  "tokens_saved": 73000,
  "savings_percent": 85.88
}
```

**Summary shows:**
- Total compression events
- Aggregate before/after/saved
- Average savings percentage
- Recent history

**Bonus**: Prompt caching provides 90% cache discount (via `prompt-caching-2024-07-31` beta).

## Compression Verification

After compression, verify essential context preserved:

```python
def verify_compression(compressed: str) -> bool:
    required = [
        "Current State",
        "Feature",
        "Next Action"
    ]
    return all(r in compressed for r in required)
```

## State-Specific Compression

| State | Preserve | Discard |
|-------|----------|---------|
| INIT | Feature list, project structure | Setup logs |
| IMPLEMENT | Current feature, file changes | Previous features |
| TEST | Test results, failures | Passing test output |
| COMPLETE | Summary, blockers | All intermediate |

## Token Budget Allocation

```
Total Context: 100K tokens

Reserved:
- System prompt: 5K
- Orchestrator: 2K
- Current skill: 2K
- Tools: 5K (with defer_loading)
- Safety buffer: 10K

Available for work: 76K tokens
Compression trigger: 60K tokens (80% of available)
```

---

## API-Based Context Management (Alternative)

**Note:** This is for direct API usage (Python/TypeScript SDK), NOT Claude Code CLI.

### Built-in `context_management` Parameter

The Messages API supports automatic context clearing:

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    messages=messages,
    context_management={
        "edits": [
            {
                "type": "clear_tool_uses_20250919",
                "trigger": {
                    "type": "input_tokens",
                    "tokens": 5000
                },
                "keep": {
                    "type": "tool_uses",
                    "value": 1
                },
                "clear_at_least": {
                    "type": "input_tokens",
                    "value": 50
                }
            }
        ]
    }
)
```

### Available Edit Types

| Type | Purpose |
|------|---------|
| `clear_tool_uses_20250919` | Clear tool results from context |
| `clear_thinking_20251015` | Clear thinking blocks |

### Triggers

| Trigger Type | When it Activates |
|--------------|-------------------|
| `input_tokens` | Context exceeds X tokens |
| `tool_uses` | After X tool uses |

### Comparison: Manual vs API

| Aspect | Manual Scripts | API `context_management` |
|--------|----------------|--------------------------|
| **Works in** | Claude Code CLI | Direct API calls only |
| **Effort** | Manual trigger | Automatic |
| **Control** | Full custom logic | Predefined patterns |
| **Token tracking** | Built-in scripts | Usage reports |
| **Best for** | Claude Code users | API-based agents |

### Bonus: Prompt Caching (90% Discount)

```python
response = client.messages.create(
    model="claude-sonnet-4-5",
    messages=messages,
    system=[{
        "type": "text",
        "text": "You are a helpful assistant.",
        "cache_control": {"type": "ephemeral"}
    }],
    betas=["prompt-caching-2024-07-31"]
)

# Cache effectiveness
cache_read = response.usage.cache_read_input_tokens
total_input = response.usage.input_tokens
savings = (cache_read / total_input) * 100
```

**Cache discount:** 90% off on cached tokens (read from `cache_read_input_tokens`).
