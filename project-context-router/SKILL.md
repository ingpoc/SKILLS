---
name: project-context-router
description: Decide where instructions, memory, plans, and artifacts should live between global Codex baseline and project-specific files. Use when creating/updating AGENTS/ROADMAP/memory docs, introducing new workflow rules, or deciding whether content belongs in ~/.codex/rules versus a repository.
---

# Project Context Router

## Overview
Apply a deterministic routing workflow so each update is stored once, in the correct scope, with minimal duplication.

## Routing Workflow
1. Identify the content type.
2. Determine the scope (`global`, `project`, or `target-project`).
3. Write/update only the owning file.
4. Add a one-line cross-reference only if discoverability is required.
5. Reject duplicate copies in multiple scopes.

## Scope Decision Matrix
- Global (`~/.codex/rules`):
  - Cross-project behavior, operating principles, tool policy, global roadmap.
  - Examples: `AGENTS.md`, `principles.md`, `soul.md`, `default.rules`, global `ROADMAP.md`.
- Project (current repository):
  - Repo-specific product goals, architecture, implementation roadmap, diagnostics, tests.
  - Examples: repository `AGENTS.md`, repository `ROADMAP.md`, task-specific docs.
- Target project operated by Jarvis (cloned app repos):
  - `JARVIS.md` and project execution memory for that target app.
  - Do not place target-project operational memory into global rules.

## Content-Type Routing Rules
- Principles/identity:
  - Global unless explicitly tied to one repository.
- Workflow policy:
  - Global if reusable across projects; project if tied to one codebase/toolchain.
- Roadmaps:
  - Keep one global roadmap in `~/.codex/rules/ROADMAP.md`.
  - Keep one roadmap per repository in `<repo>/ROADMAP.md`.
- Memory:
  - Global memory only for cross-project durable learnings.
  - Project memory for repo-specific regressions and decisions.
- Agent instructions:
  - Codex global instructions in `~/.codex/rules/AGENTS.md`.
  - Repo instructions in `<repo>/AGENTS.md`.
  - `JARVIS.md` only inside non-core target repos where Jarvis executes work.

## Conflict Resolution
When the same rule appears in multiple places:
1. Keep the most specific owner.
2. Remove duplicates from broader scopes.
3. Add a short pointer from broader scope to owner if needed.

## Update Checklist
- Confirm owner scope before editing.
- Edit only owner file(s).
- Avoid copying full policy text between scopes.
- Verify no contradictory rules remain.
- Record what changed and why in commit/task summary.

## Reference
- For canonical examples and quick mapping, read `references/context-placement-matrix.md`.
