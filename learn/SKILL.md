---
name: learn
description: Save a reusable pattern from this session to the knowledge base. Use for /learn, "remember this", "save this pattern". NOT for session state (/save-session) or full session review (/introspect).
model: haiku
effort: low
allowed-tools: Read, Write, Glob, Bash
---

# Learn: Save an Operational Instinct

**EXECUTE this skill now.** Follow the workflow steps below using the provided $ARGUMENTS. Do NOT describe, summarize, or explain this skill — run it.

## Constants

- `INSTINCTS_DIR`: `C:/Users/gurusharan.gupta/Agents/Claude Code/instincts`

## Arguments

`$ARGUMENTS` — optional description of the pattern to save. If empty, infer it from recent conversation context.

---

## Workflow

### Step 1: Identify the Pattern

If `$ARGUMENTS` is provided, use it as the pattern description.

Otherwise, infer from session context:
- What non-obvious technique was just used?
- What error was resolved in a way worth remembering?
- What approach was validated and should be repeated?

**Only save instincts that are:**
- Non-obvious (not derivable from docs in 30 seconds)
- Reusable (applies beyond this specific project)
- Validated (it worked — not a hypothesis)

Skip if the pattern is trivial, project-specific, or already covered by a golden principle.

### Step 2: Classify the Instinct

Assign:

- **domain** (pick one): `context-management` | `skill-design` | `model-routing` | `debugging` | `testing` | `security` | `git` | `tooling` | `api` | `general`
- **confidence** (0.3–0.9):
  - 0.3–0.5: Worked once, uncertain if general
  - 0.6–0.7: Worked 2–3 times, likely general
  - 0.8–0.9: Confirmed across multiple contexts
- **trigger**: One-line description of when to apply this instinct

### Step 3: Check for Duplicates

```bash
ls ~/Agents/Claude\ Code/instincts/*.md 2>/dev/null | head -20
```

Read any instinct files with similar titles/domains. If an existing instinct covers the same pattern, update it instead of creating a new file.

### Step 4: Write the Instinct File

Filename: `<domain>-<slug>.md` (e.g., `context-management-fork-on-exploration.md`)

```markdown
---
title: <short title>
domain: <domain>
confidence: <0.3–0.9>
trigger: <one-line: when to apply this>
date: <YYYY-MM-DD>
source: <project or "general">
---

## Pattern

<2–4 sentences describing the pattern. What to do, not why.>

## Why It Works

<1–3 sentences: the mechanism behind it.>

## Example

<concrete example — command, code snippet, or scenario>

## When NOT to Apply

<edge cases or conditions where this instinct breaks down>
```

### Step 5: Update the Instinct Index

Check if `instincts/_index.md` exists. If not, create it with a header.
Append one line to `instincts/_index.md`:
```
- [<title>](<filename>) — <trigger>
```

### Step 6: Confirm

Report:
```
Instinct saved: instincts/<filename>
Domain: <domain> | Confidence: <score> | Trigger: <trigger>
```
