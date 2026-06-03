---
name: code-quality-audit
description: Use for read-only code quality, correctness, security, maintainability, observability, and operational audits that produce a ranked PROGRESS.md backlog in an isolated audit worktree.
metadata:
  short-description: Audit code quality into PROGRESS.md
---

# Code Quality Audit

Use this skill when the user asks to audit code quality, code smells,
maintainability, correctness, security, complexity hotspots, observability,
operational risk, or agentic/LLM risk without editing code.

## Method

1. Run `scripts/audit-start.sh` from the target repo or pass `--repo <path>`.
2. The script creates an audit branch, a Git worktree, `GOAL.md`, and
   `PROGRESS.md`.
3. Start Codex in the audit worktree and set the active goal from `GOAL.md`.
4. During audit mode, only `PROGRESS.md` may be written.
5. Use read-only subagents only for bounded exploration in large or unfamiliar
   repos.
6. The main thread owns synthesis, deduping, ranking, and the final
   `PROGRESS.md` write.

## Commands

Setup and print the Codex launch command:

```bash
~/.codex/skills/code-quality-audit/scripts/audit-start.sh --repo .
```

Setup and launch Codex immediately:

```bash
~/.codex/skills/code-quality-audit/scripts/audit-start.sh --repo . --launch
```

Continue later with one fix item:

```bash
~/.codex/skills/code-quality-audit/scripts/audit-next.sh /path/to/audit-worktree --launch
```

If you are already inside an active Codex session, do not launch nested Codex.
Use the printed prompt directly, or set the current thread goal from
`GOAL.md`.

## Audit Rules

- Setup may create branch, worktree, `GOAL.md`, and `PROGRESS.md`.
- Audit may write only `PROGRESS.md`.
- Audit must not edit, refactor, format, or fix code.
- Audit should avoid commands that mutate repo state, including formatters,
  generators, snapshot updates, package installs, and test commands known to
  write artifacts.
- If a finding needs code, write a checklist item instead.
- Preserve `## Completed` and `## Rejected` in existing `PROGRESS.md`.
- Subagents must be read-only and must not write files.

## Subagent Policy

Use subagents when the repo is large, unfamiliar, has many modules, or has
files over 1000 lines. Do not require subagents for small repos.

Recommended read-only splits:

- architecture and test map
- correctness and failure modes
- security and agentic/LLM risk
- complexity hotspots and performance
- maintainability, observability, and operations

Each subagent returns concise findings with path, line range, severity,
evidence, proposed fix, verification, and affected files. The main thread
waits for them, removes duplicates, resolves contradictions, and writes the
ranked checklist to `PROGRESS.md`.

## Complexity Hotspot Handling

Treat complexity analysis as an audit lens, not a separate backlog owner. Raw
scanner output or subagent notes must be normalized into the existing
`PROGRESS.md` sections:

- `DEFECTS` for confirmed timeouts, memory blowups, UI freezes, or production
  failures.
- `RISKS` for material `O(n^2)`, `O(n*m)`, N+1, repeated lookup, or
  render-heavy paths on user-sized data.
- `SMELLS` for local low-risk inefficiencies.
- `CROSS-CUTTING` for repeated complexity patterns across modules.

Every complexity item must include the data-size assumption, before/after
complexity estimate, risk level, and tests needed. The main thread decides
whether the item belongs in `PROGRESS.md`.

## References

- `templates/GOAL.md` - full audit-only goal contract.
- `templates/PROGRESS.md` - durable audit backlog schema.
- `scripts/audit-start.sh` - deterministic audit environment setup.
- `scripts/audit-next.sh` - one-item executor launch helper.
