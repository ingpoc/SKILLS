# Session Resumption Patterns

**Source**: Validated by [autonomous-coding quickstart](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)

---

## Problem: Context Continuity vs Token Efficiency

| Approach | Pros | Cons |
|----------|------|------|
| **Single continuous context** | Full history, decisions preserved | Token overflow in long sessions |
| **Fresh context each session** | Zero token bloat | Loses context, re-discovers decisions |
| **Hybrid (recommended)** | Best of both | Requires smart resumption logic |

---

## Hybrid Resumption Pattern

```
┌─────────────────────────────────────────────────────────────┐
│              HYBRID SESSION RESUMPTION                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Session 1 (Fresh Start)                                     │
│  ├─ Full context: orchestrator + skills                     │
│  ├─ Execute: INIT → IMPLEMENT → TEST                        │
│  └─ At checkpoint: Save summary + state                     │
│                                                              │
│  Session 2 (Resumption)                                      │
│  ├─ Load checkpoint: summary (2K) + state (1K)              │
│  ├─ Load recent files: last 5 touched                       │
│  ├─ Continue: IMPLEMENT → TEST                              │
│  └─ At checkpoint: Save summary + state                     │
│                                                              │
│  Session N (Continue until COMPLETE)                         │
│  └─ Repeat resumption pattern                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## When to Resume Fresh vs Continue

```python
def resumption_strategy(context_usage: float) -> str:
    """
    Determine resumption strategy based on context state.
    """
    if context_usage >= 0.80:
        return "fresh_with_summary"    # Load summary + recent files
    elif context_usage >= 0.60:
        return "compress_and_continue"  # Compress, then continue
    else:
        return "continue"               # Keep existing context
```

| Context Usage | Strategy | Tokens Loaded | Continuity |
|---------------|----------|---------------|------------|
| < 60% | Continue | 0 (existing) | 100% |
| 60-79% | Compress + Continue | ~2K (compressed) | 95% |
| ≥ 80% | Fresh + Summary | ~3K (summary + files) | 80% |

---

## Fresh with Summary Pattern

**From autonomous-coding quickstart** - validated by Anthropic:

```python
async def resume_session(project_dir: Path):
    """
    Resume session with fresh context but load checkpoint summary.
    """
    # 1. Check for existing session
    tests_file = project_dir / "feature_list.json"
    is_first_run = not tests_file.exists()

    if is_first_run:
        # Fresh start: full context
        prompt = load_prompt("prompts/initializer_prompt.md")
        return "fresh", prompt

    # 2. Load checkpoint summary
    summary_file = project_dir / ".claude/progress/checkpoint_summary.md"
    if summary_file.exists():
        summary = read_file(summary_file)
    else:
        summary = generate_session_summary()

    # 3. Load recent files (last 5)
    recent_files = get_recent_files(project_dir, n=5)

    # 4. Construct resumption prompt
    prompt = f"""
# Session Resumption

## Previous Session Summary
{summary}

## Recent Files (Last 5)
{format_file_list(recent_files)}

## Current State
{read_state_json()}

## Continue From
Pick up where previous session left off. Do NOT re-analyze decisions.
"""

    return "resumed", prompt
```

---

## Checkpoint Summary Template

```markdown
# Session Checkpoint - {timestamp}

## Current State
- State: {INIT/IMPLEMENT/TEST/COMPLETE}
- Feature: {ID} - {name}
- Feature Status: {pending/implementing/testing/completed}

## Session Progress
- Features completed this session: {N}
- Total features completed: {X}/{Y}

## Key Decisions Made
1. {Decision 1}: {Rationale}
2. {Decision 2}: {Rationale}

## Files Modified (Last 5)
| File | Change |
|------|--------|
| {file1.py} | {summary} |
| {file2.py} | {summary} |
| {file3.tsx} | {summary} |
| {file4.md} | {summary} |
| {file5.json} | {summary} |

## Unresolved Issues
- [ ] {Issue 1} - {Suggested resolution}
- [ ] {Issue 2} - {Suggested resolution}

## Next Action
1. {Specific step 1}
2. {Specific step 2}

## Context State
- Context usage at checkpoint: {X}%
- Total tokens used: {N}
- Session duration: {X min}

---
**Do NOT**: Re-analyze previous decisions, re-read full history
**DO**: Continue from current state, use recent files as context
```

---

## Auto-Continue Between Sessions

**From autonomous-coding**: 3-second delay between sessions

```python
AUTO_CONTINUE_DELAY_SECONDS = 3

async def run_autonomous_loop(project_dir: Path):
    """
    Run autonomous agent with auto-continue.
    """
    iteration = 0
    while True:
        iteration += 1

        # 1. Determine resumption strategy
        usage = get_context_usage()
        strategy = resumption_strategy(usage)

        # 2. Load appropriate context
        if strategy == "fresh_with_summary":
            prompt = load_checkpoint_summary(project_dir)
            # Clear context (fresh session)
            clear_context()
        elif strategy == "compress_and_continue":
            compress_context()
            prompt = get_current_prompt()
        else:
            prompt = get_current_prompt()

        # 3. Run session
        async with create_client(project_dir) as client:
            await client.query(prompt)
            async for msg in client.receive_response():
                # Process messages...
                pass

        # 4. Save checkpoint
        save_checkpoint(project_dir)

        # 5. Check if complete
        if is_complete(project_dir):
            break

        # 6. Auto-continue delay
        print(f"Auto-continuing in {AUTO_CONTINUE_DELAY_SECONDS}s...")
        await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)
```

---

## Recent Files Tracking

```python
def get_recent_files(project_dir: Path, n: int = 5) -> List[Path]:
    """
    Get last N files modified (for context loading).
    """
    history_file = project_dir / ".claude/progress/file_history.json"

    if history_file.exists():
        history = json.loads(read_file(history_file))
        return history[-n:]  # Last N entries
    else:
        # Fallback: find recently modified files
        return find_recent_files(project_dir, n=n)
```

```python
def track_file_access(file_path: Path):
    """
    Record file access for recent files tracking.
    """
    history_file = Path(".claude/progress/file_history.json")

    if history_file.exists():
        history = json.loads(read_file(history_file))
    else:
        history = []

    # Add entry (deduplicate)
    entry = {
        "path": str(file_path),
        "timestamp": datetime.now().isoformat(),
        "operation": "read"  # or "write", "edit"
    }

    # Remove existing entry for same file
    history = [h for h in history if h["path"] != str(file_path)]
    history.append(entry)

    # Keep last 20
    history = history[-20:]

    write_file(history_file, json.dumps(history, indent=2))
```

---

## State-Based Resumption

```python
def resume_from_state():
    """
    Resume based on current state in state.json.
    """
    state = read_json(".claude/progress/state.json")
    current_state = state.get("state", "START")

    # Load appropriate skill
    if current_state == "INIT":
        load_skill("initialization")
    elif current_state == "IMPLEMENT":
        load_skill("implementation")
        # Load feature context
        feature = get_current_feature()
        load_feature_context(feature)
    elif current_state == "TEST":
        load_skill("testing")
        # Load test results
        load_test_evidence()
    elif current_state == "COMPLETE":
        load_skill("context-graph")
        # Prepare learning loop
```

---

## Compression + Resumption Integration

```python
def resumption_with_compression(context_usage: float):
    """
    Combine compression and resumption strategies.
    """
    if context_usage >= 0.90:
        # Emergency: fresh start with minimal summary
        return "emergency_fresh", load_minimal_summary()

    elif context_usage >= 0.80:
        # High: fresh start with full summary + recent files
        return "fresh_with_context", load_checkpoint_summary()

    elif context_usage >= 0.70:
        # Medium: compress + continue
        compress_context(level="summarize")
        return "compress_continue", None

    elif context_usage >= 0.50:
        # Low: remove raw outputs
        compress_context(level="remove_raw")
        return "remove_raw", None

    else:
        # No compression needed
        return "continue", None
```

---

## Session Handoff File

```json
// .claude/progress/session-handoff.json
{
  "session_id": "uuid",
  "timestamp": "2025-12-28T16:30:00Z",
  "state": "IMPLEMENT",
  "feature": {
    "id": "feat-001",
    "name": "User authentication",
    "status": "implementing"
  },
  "checkpoint_summary": "session_checkpoint_20251228_163000.md",
  "recent_files": [
    "src/auth/login.ts",
    "src/auth/session.ts",
    "src/auth/middleware.ts",
    "tests/auth.test.ts",
    "package.json"
  ],
  "decisions": [
    "Using JWT for session management",
    "Cookie-based auth with httpOnly flag"
  ],
  "next_actions": [
    "Complete middleware implementation",
    "Add session refresh logic"
  ],
  "context_usage": 0.72,
  "resumption_strategy": "compress_continue"
}
```

---

## Comparison: Resumption Strategies

| Strategy | When to Use | Token Cost | Context Continuity | Implementation |
|----------|-------------|------------|-------------------|----------------|
| **Continue** | Context < 60% | 0 | 100% | Built-in |
| **Compress + Continue** | Context 60-79% | ~2K | 95% | Medium |
| **Fresh + Summary** | Context ≥ 80% | ~3K | 80% | Medium |
| **Emergency Fresh** | Context ≥ 90% | ~1K | 50% | Simple |

**Recommended**: Implement all 4 strategies with automatic selection based on `context_usage`.

---

## Verification

After resumption, verify continuity:

```python
def verify_resumption():
    """
    Verify session resumed correctly.
    """
    state = read_json(".claude/progress/state.json")

    # Check 1: State is consistent
    assert state["state"] in ["INIT", "IMPLEMENT", "TEST", "COMPLETE"]

    # Check 2: Feature context loaded
    if state["state"] in ["IMPLEMENT", "TEST"]:
        assert "current_feature" in state

    # Check 3: Recent files accessible
    recent_files = get_recent_files(n=5)
    assert all(f.exists() for f in recent_files)

    # Check 4: No duplicate work
    # Verify we're not re-implementing completed features

    return True
```

---

## Scripts

**Session resumption script:**
```bash
#!/bin/bash
# .skills/orchestrator/scripts/resume-session.sh

PROJECT_DIR="${1:-.}"
CONTEXT_CHECK="$(./check-context.sh)"

if [ "$CONTEXT_CHECK" -ge 80 ]; then
    echo "fresh_with_summary"
    cat ".claude/progress/checkpoint_summary.md"
    ls -t "$PROJECT_DIR"/**/*.py "$PROJECT_DIR"/**/*.ts 2>/dev/null | head -5
elif [ "$CONTEXT_CHECK" -ge 60 ]; then
    echo "compress_and_continue"
    ../compress-context.sh summarize
else
    echo "continue"
fi
```

---

*Added: 2025-12-28*
*Source: autonomous-coding quickstart + DESIGN-v2.md hybrid approach*
*Token savings: 50-80% vs fresh context per session*
