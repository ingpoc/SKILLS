---
name: agentharness-audit
description: "Audits any agent harness codebase against 13 meta-principles of quality, scores each 0 to 10 with code citations, generates a self-contained HTML report for operators, and writes an agent-readable AGENTS.md improvement directive with file-level architecture recommendations to reach 9.5 or better. Use when the user wants to audit or rate an agent harness, evaluate harness quality, score an agent framework, get a roadmap for improving a harness, run agentharness-audit, audit this harness, rate Hermes, audit Codex, or audit a Claude Code harness. Not for individual skill audits or general code review."
allowed-tools: Read, Write, Edit, Bash
---

# agentharness-audit — score any agent harness against 13 quality principles

> **Self-validate after edits.** Any change to this skill's files must be followed by
> `./scripts/validate.sh` from the skill directory.

Audits an agent harness codebase against 13 evidence-based meta-principles derived from
comparative analysis of Hermes, Claude Code, Codex CLI, and OpenClaw. Each principle is
scored 0–10 with code citations. The operator receives a print-ready Tufte HTML report;
the harness itself receives a concrete self-improvement directive in AGENTS.md format.

## Procedure

Full step-by-step: [references/procedure.md](references/procedure.md)

1. **Discover** — map the codebase (system prompt, tool loading, memory, compaction, subagents, config)
2. **Score** — evaluate each of the 13 principles with file:line citations ([references/principles.md](references/principles.md))
3. **Report** — copy the bundled [`templates/audit.html.template`](templates/audit.html.template) to `docs/agentharness-audit/<name>-audit.html` and fill placeholders using [references/html-template.md](references/html-template.md). Do not regenerate the report from scratch or require loading another skill.
4. **Directive** — write `docs/agentharness-audit/<name>-AGENTS.md` ([references/agents-template.md](references/agents-template.md))
5. **Print** — output scores table to terminal

If no path is specified, audit the current working directory.

## Hard rules

1. **Evidence before score.** Every score requires a file:line citation or an explicit "not found" declaration.
2. **Both files always.** HTML report and AGENTS.md are both produced on every run.
3. **Concrete recommendations only.** AGENTS.md must name specific files and patterns — "implement Y at Z", never "improve X".
4. **Self-contained HTML path.** The bundled template is the required source of truth. `html-artifact` is provenance only; do not depend on loading it during an audit run.
5. **Not a harness → exit cleanly.** If no agent loop, tool dispatch, or model calls are found, say so and stop.

## Cross-references

- [references/procedure.md](references/procedure.md) — full audit procedure
- [references/principles.md](references/principles.md) — 13 principles with scoring rubric and 9.5 references
- [references/html-template.md](references/html-template.md) — fill guide + substitution helpers for the HTML report
- [templates/audit.html.template](templates/audit.html.template) — literal self-contained HTML scaffold; this is the source of truth for report generation. It was derived from html-artifact report-lane conventions but does not require loading html-artifact.
- [references/agents-template.md](references/agents-template.md) — AGENTS.md template and writing rules
- [references/architecture.md](references/architecture.md) — canonical patterns, anti-patterns, design rationale, and winner codebase references per principle

## Why this skill exists

Agent harnesses are evaluated on marketing claims, not the mechanisms that determine token
efficiency, self-improvement, and operator accessibility. This skill makes those mechanisms
legible and scoreable — enabling evidence-based harness selection and a concrete improvement
roadmap that the harness agent can execute autonomously.
