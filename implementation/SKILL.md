---
name: implementation
description: "Implement the next pending feature from feature-list.json. Lean loop: pick feature, implement with tests, verify all checks pass, commit, mark done. Use when features are pending and you're ready to build. Also use when user says 'build next feature', 'implement', 'start coding', 'what's next', or after /init-project has created the feature list."
model: sonnet
effort: medium
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Implementation

Pick the next feature. Build it. Verify it. Ship it.

## Gotchas

| Gotcha | What happens | Do instead |
|--------|-------------|------------|
| Committing before verify passes | Broken code lands in history, needs revert or fixup | Always run verify.sh first — commit only on exit 0 |
| Reading full feature-list.json | Burns context tokens as feature list grows (33+ features) | Use `feature.py next` to get just the one feature you need |
| Script fails, agent rewrites it | Loses project-specific customizations from /init-project | Read the script, fix the broken command — never recreate |
| Forgetting to update AGENTS.md | Architecture/Key Files drift from actual codebase | Check if you added/removed modules — update if so |

## Workflow

### 1. Pick Feature

```bash
python .codex/scripts/feature.py next
```

Returns the highest-priority pending feature whose dependencies are resolved. If no features ready, stop and tell the user.

### 2. Implement

- Read the project AGENTS.md for architecture, key files, and conventions
- Read existing code before modifying — understand the patterns in use
- Write the implementation following project conventions
- Write tests — happy path + at least one error path

The goal is working code with tests, not perfect code. Ship, then iterate.

### 3. Verify

```bash
bash .codex/scripts/verify.sh
```

Runs lint → test → build in order, stops at first failure. Fix the issue, rerun from top. Only proceed to commit when exit code is 0.

If `verify.sh` is missing or stale, run the checks from AGENTS.md Commands table manually.

### 4. Commit

Stage only the files you changed. Commit with the feature ID:

```
feat(FT-XXX): short description of what was built
```

### 5. Update & Mark Done

- If you added/removed modules, models, or key files → update AGENTS.md (Architecture, Key Files, Commands)
- If the feature revealed new verification needs → update `.codex/scripts/verify.sh`
- Mark done:

```bash
python .codex/scripts/feature.py done FT-XXX
```

## Scripts Reference

Scripts live in `.codex/scripts/`. Created by `/init-project`, tailored per project.

| Script | What it does | When to update |
|--------|-------------|----------------|
| `feature.py` | Feature CRUD: `next`, `get`, `done`, `add`, `list`, `summary`. Reads/writes `.codex/progress/feature-list.json`. | Never — project-agnostic |
| `verify.sh` | Runs lint → test → build in order, `set -e` stops at first failure. Exit 0 = all pass. | When a feature adds a new check (e.g., type check, new linter, integration test command) |
| `dev-server.sh` | Installs deps + starts dev server. | When dependencies change, entry point moves, or a new service is added |

**If a script fails:** read it, fix the broken command, do NOT delete and rewrite. The structure (set -e, echo headers, command order) is intentional and project-specific.

## Rules

- **Never commit with failing checks** — broken commits create revert churn that wastes more time than the fix
- **Never skip tests for production code** — untested code is unverified code, and the agent can't self-correct without tests
- **Read files before editing** — modifying code you haven't read produces wrong assumptions and wasted iterations
- **One feature per cycle** — context switching mid-feature leads to half-finished work in both
- **Never recreate scripts from scratch** — they contain project-specific customizations from /init-project that you can't rederive
