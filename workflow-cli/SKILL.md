---
name: workflow-cli
description: Reference for modifying workflow.py or managing ~/.codex/docs/. Use when the user asks about workflow CLI commands, adding or updating docs, alias registration, workflow registry or lint issues, or fixing workflow command behavior. NOT for general CLI design principles (/cli-for-agents).
model: haiku
effort: low
allowed-tools: Read, Glob, Grep
---

# Workflow CLI

**EXECUTE this skill now.** Follow the workflow steps below using the provided $ARGUMENTS. Do not summarize the skill itself.

The `workflow` CLI is the global context retrieval tool for AI agents and humans. It serves owner docs from `~/.codex/docs/` with progressive disclosure so the reader gets the minimum context needed at the point of need.

## Canonical Sources

Use the live CLI and implementation as source of truth when command behavior matters:

- `workflow --help`
- `workflow knowledge --help`
- `workflow read workflow-cli`
- `~/.codex/bin/workflow.py`

If you edit `workflow.py`, also load `workflow summary workflow-cli-quality-gate` before changing it.

## Why This Exists

Agents waste context by loading whole docs when only a small slice is relevant. The previous direct-read pattern in entry docs was all-or-nothing. The workflow CLI inserts a retrieval layer between the agent and the docs:

- `list` to see what exists
- `summary` to triage relevance
- `read --section` to load only what is needed
- `read` for the full document as a last resort

## Architecture

```text
~/.codex/bin/workflow.py        Single-file CLI
~/.local/bin/workflow           PATH wrapper
~/.codex/docs/                  Owner docs served by the CLI
~/.codex/pyproject.toml         Ruff config
~/.codex/.rumdl.toml            Markdown lint config
```

The CLI is intentionally low-dependency and supports both human-readable output and `--json` output for agent use.

## Commands

Use the retrieval ladder:

```text
workflow doctor
workflow list
workflow summary <doc>
workflow read <doc> --section <heading>
workflow read <doc>
```

For knowledge:

```text
workflow knowledge list
workflow knowledge search "query" --tag <domain>
workflow knowledge summary <article>
workflow knowledge read <article>
```

For maintenance:

```text
workflow add <type> <name>
workflow update <doc> --section <heading>
workflow registry
workflow lint
workflow version
```

Knowledge maintenance:

```text
workflow knowledge ingest <path>
workflow knowledge reindex
workflow knowledge stats
```

Global options:

```text
workflow --no-input ...
workflow --docs-dir <path> ...
```

`workflow context <task>` returns the compact pack by default; use `workflow context <task> --full` when you need the full bundled docs.

## Adding or Updating Docs

1. Decide the right doc type first: principle, workflow, reference, or pattern.
2. Scaffold with `workflow add <type> <name>` or create the file directly in `~/.codex/docs/`.
3. Ensure the doc has a `## Control Owner` section.
4. Register an alias in `~/.codex/bin/workflow.py` only when the doc should be a first-class short-name target such as `workflow summary <name>`.
5. Add or update the trigger in `AGENTS.md` only after the target exists.
6. Run `workflow registry` and `workflow lint`.

Docs do not use a reindex step. They are discovered from the filesystem. `reindex` is only for the knowledge base via `workflow knowledge reindex`.

Every doc should have a `## Control Owner` section with:
- `Owner for:`
- `Should contain:`
- `Should not contain:`

## Common Issues

- No doc match: check `workflow list` or `workflow search`
- Section not found: use the exact `##` heading shown by `workflow summary`
- Missing alias after a rename: update `ALIASES` in `workflow.py`
- Doc exists but no short name works: either use the direct discovered name/path or add an alias in `workflow.py`
- Confusing docs vs knowledge maintenance: docs use `workflow registry`; knowledge uses `workflow knowledge reindex`
- Lint failures: run `workflow lint --full` and fix the surfaced file

## Design Principles

- progressive disclosure
- dual-audience output
- context window protection
- deterministic, non-interactive commands
- actionable errors with next steps
- reference doc for command details, skill for execution workflow
