---
name: resume-session
description: Legacy compatibility resume flow for sessions stored by the older `.claude` lifecycle. Use only when maintaining that save/resume path. NOT for the Codex-first default baseline.
model: sonnet
effort: low
allowed-tools: Read, Glob, Bash
---

# Resume Session: Load Prior State

Compatibility note: this skill is a `.claude`-era lifecycle surface. It is not part of the default Codex-first repo baseline.

**EXECUTE this skill now.** Follow the workflow steps below using the provided $ARGUMENTS. Do NOT describe, summarize, or explain this skill — run it.

Read a saved session file and produce a structured briefing. Do NOT start work automatically — wait for user direction.

## Constants

- `SESSION_DIR`: `/tmp/session-data`

## Workflow

### Step 1: Determine Current Project Scope

Identify the current project before searching for saved sessions:

- `repo_scope`: `git rev-parse --show-toplevel` if in git; else cwd
- `project_display_name`: repo basename by default; prefer cwd `CLAUDE.md` identity if clear
- `repo_scope` is the canonical identity. `project_display_name` is only a fallback display/name aid.
- Treat `$ARGUMENTS` as an explicit override when provided. It may be an exact repo path, repo name, project directory name, or project display name. Treat filename fragments only as a last-resort fallback when stronger matches do not exist.

Default behavior must be project-scoped. Do NOT default to the most recent save across unrelated projects.

### Step 2: Find Candidate Session Files

List session files:
```bash
find /tmp/session-data -mindepth 2 -maxdepth 2 -type f -name '*.md' -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null
```

If no files exist, report: "No saved sessions found. Use `/save-session` to create one."

Filter candidates in this order:

1. Read each candidate file enough to inspect the embedded `## Project` block, especially `- **Repo:** <absolute path>`.
2. If `$ARGUMENTS` is provided, keep only files whose saved `Repo:` path exactly matches the argument, or whose project directory/display name exactly matches the argument. Only use filename-fragment matching as a last-resort fallback.
3. If `$ARGUMENTS` is not provided, keep only files whose saved `Repo:` path exactly matches `repo_scope`. If `Repo:` is missing, fall back to current project directory/display-name matching.
4. Prefer exact `Repo:` matches over project-name or directory-name matches, even if another file is newer overall.
5. Filter first, then choose the newest matching file. Do not truncate the global file list before project filtering.

If there are no same-project matches, report that no saved session was found for the current project. Do NOT silently fall back to another project's session file.

If a candidate is malformed or missing required headings, skip it.

### Step 3: Select Session

- If only one file: use it
- If multiple same-project matches exist: use the most recent exact `Repo:` match
- If no exact `Repo:` match exists but strong fallback matches do, use the most recent of those fallback matches
- If argument matches a project name/path: use the most recent matching save for that project/path
- "Latest session data" means the latest saved session for the same project you are currently working on since the last time you worked on it, not the latest saved session anywhere under `/tmp/session-data`

`save-session` owns the writer contract. This skill is a strict reader of that contract. If the session path convention, filename shape, or required headings change there, update this skill in the same edit.

Expected saved note contract:
- `# Session: <project_display_name> — <timestamp>`
- `## Project`
- `- **Repo:** <absolute path>`
- `- **Branch:** <branch>`
- `- **Goal:** <one-sentence goal>`
- `## Current State`
- `## What Worked`
- `## What Did NOT Work (Do Not Retry)`
- `## Open Questions`
- `## Next Step`

### Step 4: Read and Brief

Read the session file and output this exact briefing structure:

```
## Session Briefing: <project> — <timestamp>

**GOAL:** <what we were trying to accomplish>

**CURRENT STATE**
<what was in progress when session was saved>

**WHAT WORKED**
<bullet list of successful approaches>

**DO NOT RETRY**
<bullet list of failed approaches — these are dead ends>

**OPEN QUESTIONS**
<unresolved questions, if any>

**NEXT STEP**
<the specific action to take — ready to execute on user's go>
```

### Step 5: Wait

After outputting the briefing, say:
"Ready. Confirm to proceed with the next step, or tell me what to do differently."

Do NOT begin executing the next step without explicit user confirmation.
