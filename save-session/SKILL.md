---
name: save-session
description: Legacy compatibility save flow for the older `.claude` session-data model. Use only when maintaining that path. NOT for the Codex-first default baseline.
metadata:
  model: haiku
  effort: low
allowed-tools: Read, Write, Bash, Glob
---

# Save Session: Persist Current State

Compatibility note: this skill is a `.claude`-era lifecycle surface. It is not part of the default Codex-first repo baseline.

**EXECUTE this skill now.** Follow the workflow steps below using the provided $ARGUMENTS. Do NOT describe, summarize, or explain this skill — run it.

## Gotchas

- Saving session state is not the same as saving project precedent. Capture only `.memory/` candidates that would prevent rediscovery; do not turn transient progress into memory.
- Auto-write memory only when the candidate clearly belongs in `.memory/` and you can populate every required field from evidence in the session. If the title, type, phase, entity, tags, or required sections would be guesswork, skip it.
- Create memory entries sequentially. `workflow memory add` updates `.memory/INDEX.md` and `routing.json`, so concurrent writes can race and corrupt the index.
- Do not overwrite the latest save from the same day. Each save must produce a new timestamped filename so resume order stays trustworthy.
- If the repo name is unclear, prefer the current directory's `CLAUDE.md` project identity over parent directories or unrelated recent sessions.
- “Biggest learning” is a candidate-generation prompt, not a journaling requirement. If it does not clear the memory/doc/enforcement gate, record nothing and move on.

## Constants

- `SESSION_DIR`: `/tmp/session-data`

## Workflow

### Step 1: Determine Project and Timestamp

- `repo_scope`: `git rev-parse --show-toplevel` if in git; else cwd
- `project_display_name`: cwd `CLAUDE.md` identity if clear; else basename of `repo_scope`; else basename of cwd
- timestamp: local `YYYY-MM-DD-HHMMSS`

`repo_scope` is the canonical identity for resume. `project_display_name` is only for directory and filename readability.

Filename: `<project_display_name>-<YYYY-MM-DD-HHMMSS>.md`
Do not reuse or overwrite an earlier save from the same day; each save should produce a new timestamped file.

### Step 2: Gather State

Ask yourself (or infer from context):
1. **What project/repo is this?** — name, path, active branch
2. **What was the goal of this session?** — one sentence
3. **Current state** — what milestone was reached, what is in progress
4. **What worked** — approaches, commands, patterns that succeeded (with evidence)
5. **What did NOT work** — failed approaches, dead ends (critical: prevents retrying)
6. **Next step** — the single most important action to take next session

### Step 2.4: Extract the Biggest Learning, Then Gate It Hard

Before the memory pass, ask:

- What was the single biggest learning from this session?

Treat the answer as a candidate only. Do **not** encode it anywhere unless it clearly passes a promotion gate.

Promotion gate: only continue if the learning is at least one of:

- a repeated failure mode or rediscovery risk
- a stable owner-surface rule
- a deterministic policy that should become lint, hook, runtime guard, or deny rule
- a reusable workflow or pattern likely to matter again
- a stale-doc or stale-code mismatch proven against code, runtime behavior, CLI help, or vendor docs
- a cross-session clarification that a fresh agent would likely miss

Reject by default when it is:

- session progress or status
- an isolated one-off observation
- obvious from the current code or config
- collaboration preference rather than project precedent
- too vague to route to one owner surface

If it passes, route it deliberately:

- short always-on rule -> `AGENTS.md`
- reusable workflow or detailed method -> owner doc or `skills/SKILL.md`
- session-earned precedent -> `.memory/`
- deterministic policy -> enforcement surface first, prose second if needed

Before writing docs or memory for the learning, check whether the same guidance already exists in the KB, reference docs, skill, or `AGENTS.md`. If the existing guidance is already correct, do not add a second copy. If it is stale and the owning surface is clear, correct that surface instead of creating a duplicate.

Canonical-owner rule:

- If the learning is worthy of a durable instruction update and the owning surface is clear, update the canonical owner first instead of saving the lesson only as memory.
- Use memory for the rediscovery-prevention trace only when that precedent still adds value after the canonical owner has been corrected.
- Do not let save-session create a parallel owner lane; prefer one corrected owner surface over a new note plus a stale doc.

Examples:

- Promote: “This repo keeps recreating parallel KB collections when `builder kb extract --output-dir` is used; the canonical local collection must be fixed and enforced.” This is a repeated failure mode, an owner-surface rule, and a deterministic policy candidate.
- Reject: “Today I learned the architecture doc was easier to read after regenerating it.” This is session progress, not durable precedent.

### Step 2.5: Assess and Create Passing Memories

Before writing the session file, do a narrow memory pass using the project memory rules:

- Look only for project-specific `decision`, `correction`, or `pattern` candidates
- Skip transient progress, collaboration feedback, cross-project guidance, and facts obvious from code/config
- Prefer items that would prevent rediscovery, repeated mistakes, or repeated design drift
- Require a searchable title with at least 4 significant words and a concrete noun
- Require the full memory metadata up front: `type`, `phase`, `entity`, and `tags`
- Require the exact section structure for the chosen type:
  - `decision`: `## Decision` and `## Trace`
  - `correction`: `## Constraint`, `## What Went Wrong`, and `## What To Do Instead`
  - `pattern`: `## Approach`, `## When To Reuse`, and `## Evidence`
- If there are no strong candidates that satisfy those constraints, record `- None`

When a candidate clearly passes that gate, create it immediately with `workflow memory add`, supplying the full body on stdin so the memory is complete on first write. Create memories one at a time, never in parallel.

After each creation:

- run `workflow memory summary <slug>` or `workflow memory read <slug>` to confirm it exists
- record the created memory slug under `## Memory Saved`
- do not create duplicate or near-duplicate memories for the same session fact

### Step 2.55: Distinguish Reference Docs vs Memory

Use this boundary before deciding whether to write memory or correct docs:

- Reference doc: current shared truth for the repo. Use it for stable commands, flags, auth/setup steps, owner-surface rules, workflow order, and anti-patterns when the preferred path is now clear.
- Memory: session-earned precedent. Use it for non-obvious decisions, corrections, tradeoffs, exceptions, and validated patterns that would otherwise be rediscovered.

Decision test:

- If it should be true for any reader of the repo right now, it belongs in the owning reference doc.
- If it mainly captures what was learned from experience in this session and why it mattered, it belongs in memory.
- If both are true, put the canonical instruction in the reference doc and the rediscovery-prevention rationale in memory only if that rationale clears the memory gate.

Reference docs are for present-state instruction. Memory is for precedent and rediscovery prevention.

### Step 2.6: Apply Small Reference-Doc Corrections When the Gate Is Met

Before writing the session file, decide whether a reference doc should be updated immediately.

Only update a reference or workflow doc during save-session when **all** of these are true:

- the stale guidance or anti-pattern was directly validated in this session against code, runtime behavior, CLI help, or vendor docs
- the owning reference surface is clear (for example a single repo doc, workflow doc, or skill doc)
- the fix is narrow, factual, and low-risk
- the correction prevents likely repeat confusion in the next session
- the edit does not expand into a broader redesign, research pass, or implementation task

Good candidates:

- stale flags, commands, env var guidance, or auth/setup steps
- incorrect owner-surface claims
- outdated workflow sequencing or removed paths
- a small anti-pattern note where the preferred path is now clear

Do **not** update docs during save-session when:

- the owning surface is ambiguous
- the change needs restructuring or broad rewriting
- the session evidence is incomplete or inferential
- the edit would turn save-session into a new workstream

If the gate is met, update the owning doc before saving the session and summarize that correction in `## Current State` or `## What Worked`. If the gate is not met, leave the docs unchanged and record the follow-up in `## Next Step`.

When the correction is instruction-level rather than workflow-level, prefer the smallest canonical owner that already governs that behavior:

- runtime contract or repo operating rule -> `CLAUDE.md`
- always-on routing or trigger rule -> `AGENTS.md`
- detailed procedure or sequencing -> workflow/reference doc or `skills/SKILL.md`
- enforcement-worthy deterministic policy -> lint, hook, deny rule, or guard first when feasible

### Step 3: Create the Session File

This file is the canonical writer contract for `resume-session`. If you change the session path convention, filename shape, or headings here, update `resume-session` in the same edit.

Create the directory first if it does not exist:

`/tmp/session-data/<project_display_name>/`

Then create:

`/tmp/session-data/<project_display_name>/<project_display_name>-<YYYY-MM-DD-HHMMSS>.md`

Directory and filename are for organization only. The canonical resume key is the embedded `## Project` -> `- **Repo:** <absolute path>` field.

Saved note contract read by `resume-session`:
- `# Session: <project_display_name> — <YYYY-MM-DD-HHMMSS>`
- `## Project`
- `- **Repo:** <absolute path from repo_scope>`
- `- **Branch:** <branch>`
- `- **Goal:** <one-sentence goal>`
- `## Current State`
- `## What Worked`
- `## What Did NOT Work (Do Not Retry)`
- `## Open Questions`
- `## Next Step`

```
# Session: <project_display_name> — <YYYY-MM-DD-HHMMSS>

## Project
- **Repo:** <absolute path from repo_scope>
- **Branch:** <branch>
- **Goal:** <one-sentence goal>

## Current State
<what milestone was reached; what is in-flight>

## What Worked
- <approach/command> — <why it worked>
- ...

## What Did NOT Work (Do Not Retry)
- <approach> — <why it failed>
- ...

## Open Questions
- <unresolved question, if any>

## Memory Saved
- <slug> — <type/phase/entity, or `None`>

## Memory Candidates
- <strong candidate left unsaved because the memory gate was not met, or `None`>

## Next Step
<single most important action to take next session — be specific>
```

### Step 3.5: Reflection Status For Close-Out

Before the final confirmation, compute and report these statuses from the gates above:

- `Memory entries`: how many were actually created
- `Biggest learning`: `promoted`, `rejected`, or `already encoded`, with the owner surface if promoted/encoded
- `OpenAI docs guidance needed`: `yes` only when the session required or should have required current official OpenAI documentation; otherwise `no`
- `Stale workflow/reference-doc update needed`: `yes`, `no`, or `updated now`
- `Unresolved follow-up`: `yes` or `no`

Keep these statuses short and factual. Do not invent positive status just to fill the space.

### Step 4: Confirm

Report in this shape:

- `Session saved to /tmp/session-data/<project-name>/<filename>.`
- `Memory entries: <N>`
- `Biggest learning: <status>`
- `OpenAI docs guidance needed: <yes/no>`
- `Stale workflow/reference-doc update needed: <status>`
- `Unresolved follow-up: <yes/no>`
- `Resume with /resume-session.`
