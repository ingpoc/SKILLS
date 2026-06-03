# Context Placement Matrix

## Fast Rules
- If it applies to most projects, store globally.
- If it depends on this repository's architecture or product goals, store in repo.
- If Jarvis is operating on an external target app repo, store operational project memory in that target repo (`JARVIS.md`).

## What Goes Where
- `~/.codex/rules/AGENTS.md`
  - Global behavior and workflow expectations.
- `~/.codex/rules/principles.md`
  - Cross-project decision heuristics.
- `~/.codex/rules/soul.md`
  - Cross-project interaction style.
- `~/.codex/rules/default.rules`
  - Global tool/command policy defaults.
- `~/.codex/rules/ROADMAP.md`
  - Global improvement roadmap.
- `<repo>/AGENTS.md`
  - Repository-specific execution rules.
- `<repo>/ROADMAP.md`
  - Repository-specific implementation priorities.
- `<target-repo>/JARVIS.md`
  - Jarvis execution memory for that target project.

## Anti-Patterns
- Duplicating the same roadmap in global and project scopes.
- Storing repo-specific implementation details in global rules.
- Keeping target-project operational memory in the Jarvis core repository.

## Pre-Commit Check
- Is this change reusable across projects?
- Does this change mention repo-specific code paths or product constraints?
- Is this the single source of truth for this content type?
