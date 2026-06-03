---
name: introspect
description: Legacy compatibility retrospective for the older `.claude` and eval-state workflow. Use only when maintaining that path. For Codex-first closeout, prefer session-introspection.
model: sonnet
effort: medium
---

# Introspect: Session Friction Analysis

Compatibility note: this skill is a `.claude`-era lifecycle surface. It is not part of the default Codex-first repo baseline.

**EXECUTE this skill now.** Follow the workflow steps below using the provided $ARGUMENTS. Do NOT describe, summarize, or explain this skill — run it.

Pause the current workflow. Analyze what happened in this session. Produce a structured assessment that gets encoded into the repo so the same friction never recurs.

The value isn't the report — it's the side effects: state updates, memory files, CLAUDE.md changes, and skill fixes that compound across sessions.

## When to Run

- You hit the same failure twice
- A workaround feels easier than fixing the root cause (that's the signal)
- User asks for session review
- Before ending a long session (>30 min of active work)

## Workflow

### Step 1: Gather Evidence

Read these files to understand current state and avoid repeating known issues:

- `eval/state.json` — completed actions, dead ends, priorities
- Project `CLAUDE.md` — current trigger lines, commands
- Recent `git log --oneline -10` — what was committed this session

Then review the conversation history for:
- Tool calls that failed or were retried
- Skills that produced wrong output
- Manual workarounds (agent did what a tool should have done)
- Corrections from the user (especially repeated ones)
- Patterns that succeeded on first try

### Step 2: Classify into 4 Quadrants

For each finding, assign exactly one quadrant:

```
KEEP   — Worked well. Should become a reusable pattern.
         Ask: would a new session benefit from knowing this?

FIX    — Failed or caused friction. Needs root cause + fix.
         Ask: what's missing — tool, guardrail, doc, script?

REMOVE — Redundant, stale, or wastes context/tokens.
         Ask: what happens if we delete this?

OPTIMIZE — Works but costs too much (tokens, time, steps).
           Ask: can a script replace agent work? can we reduce steps?
```

For each finding, also classify WHERE the fix goes using the harness framework:
- Rule (CLAUDE.md) — ≤3 lines, auto-fires
- Trigger (CLAUDE.md → doc) — reference on condition
- Skill — multi-step judgment workflow
- Script (bin/) — deterministic, repeatable

### Step 3: Output the Assessment

Present as a concise table. No prose. Lead with the action.

```
## Session Introspection — <date>

### KEEP (reuse these)
| Pattern | Encode as | Location |
|---------|-----------|----------|
| scan.py for deterministic work | script pattern | already in bin/ |

### FIX (broken, needs root cause)
| Issue | Root cause | Fix | Encode as |
|-------|-----------|-----|-----------|
| eval-score created junk files | no guardrail in SKILL.md | add "DO NOT create files" | rule in SKILL.md |

### REMOVE (delete these)
| Item | Why redundant | Action |
|------|--------------|--------|
| bin/scan.sh | replaced by scan.py | git rm |

### OPTIMIZE (works but wasteful)
| Item | Current cost | Proposed | Savings |
|------|-------------|----------|---------|
| scan on sonnet | ~28K tokens | script + haiku | ~27K tokens |
```

### Step 4: Encode the Findings

This is the critical step. The report is worthless without side effects.

For each finding, take the appropriate action:

**KEEP findings:**
- If it's a pattern another session should know → create a memory file in `memory/`
- If it's a working approach → ensure it's already committed

**FIX findings:**
- Fix the root cause now (edit the skill, script, or criteria)
- Add to `eval/state.json` dead_ends if it's an approach to never retry
- Add to `eval/state.json` completed_actions after fixing

**REMOVE findings:**
- Delete the file/section/rule
- If in CLAUDE.md, verify line count stays under budget after removal

**OPTIMIZE findings:**
- If "script should replace agent work" → create the script, simplify the skill
- If "context cost too high" → move from rules/ to docs/, add trigger line
- Update `eval/state.json` next_priorities with remaining optimizations

### Step 5: Verify Encoding

After all side effects, confirm:
- [ ] eval/state.json updated
- [ ] Memory files created for KEEP findings (if cross-session relevant)
- [ ] Dead ends recorded for FIX findings
- [ ] Stale items deleted for REMOVE findings
- [ ] CLAUDE.md still under line budget
- [ ] Changes committed with clear message

## Important

- Introspection that doesn't produce side effects is wasted tokens. Every finding must land somewhere persistent.
- Don't assess hypothetically. Only assess what actually happened in this session.
- Be honest about what failed — especially your own mistakes. The goal is to prevent recurrence, not to look good.
- If the session went smoothly with no friction, say so in one line and skip the rest. Don't fabricate findings.
