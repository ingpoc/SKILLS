---
name: project-context-installer
description: "Install a project-local context graph into a repo. Use when the operator asks to set up, scaffold, install, or wire a project context graph, durable decision graph, session-mining memory graph, or `project-context` CLI. This skill creates a deterministic local Python CLI, root wrapper script, docs/workflow wiring, and validation hooks inside the target project while keeping global doctrine in `~/.codex` and repo-specific behavior in the repo."
allowed-tools: Read Write Edit Bash
---

# project-context-installer — scaffold a project-local context graph

> **Self-validate after edits.** Any change to this skill's files (SKILL.md, scripts/, references/, templates/, assets/) must be followed by `./scripts/validate.sh` from the skill directory. Hard findings -> create-skill Optimize lane.

Install a repo-local context graph that mines ordered sessions into validated durable decisions and exposes them through a local `project-context` CLI. This skill is for setup and wiring, not for mining live decisions by hand.

## Operating contract

| Field | Decision |
|---|---|
| Primary archetype | deterministic script workflow |
| Secondary archetypes | reference workflow |
| Operator trigger | "set up project context graph", "install project-context", "scaffold durable decision graph", "wire session-mining context graph" |
| Output | Installed `tools/project-context` CLI, repo wrapper script, pinned miner agent, local docs, and repo routing updates |
| Success evidence | installer report, repo files created, local validation commands pass |
| Deterministic surface | `scripts/install.py`, generated local CLI, generated tests, `scripts/validate.sh` |
| Judgment surface | deciding whether repo docs/AGENTS need additional routing beyond the default install |
| Context loading | load this body, then `references/install.md`; inspect local repo `AGENTS.md` and docs only if present |

## Main flow

### Preflight

1. Confirm the target repo path exists.
2. If the repo has a local `AGENTS.md`, retrieve the `agents-md` quality gate before editing it.
3. If the repo has `docs/`, inspect current reference/workflow surfaces before adding new ones.
4. Keep the install project-local. Do not move repo-specific graph semantics into global `AGENTS.md`.

### Do

Run the installer:

```bash
python3 ~/.codex/skills/project-context-installer/scripts/install.py --target /abs/path/to/repo
```

The installer:
- writes `tools/project-context/` with a deterministic Python CLI
- writes `script/project_context.sh` as the stable repo entrypoint
- updates repo docs and local `AGENTS.md` with marker-safe inserts when those files exist
- writes tests and validation guidance

### Closeout

1. Run the generated validation commands in the target repo.
2. If local `AGENTS.md` changed, run `workflow lint` from the target repo.
3. Report created files, commands run, and any gaps.

#### Friction introspection

At closeout, classify friction before changing this skill:

| Friction source | Action |
|---|---|
| Missing installer behavior, patch rule, or validation wiring | Update this skill |
| Generated project-context code bug | Fix the generated scaffold and reinstall or patch target |
| Source coverage or exclusion state is not durable | Add source inventory, watermark, and persisted resolution behavior to the generated scaffold |
| Repeated source-resolution operations are slow | Add a batch command or cached deterministic path to the generated scaffold |
| Repo-specific docs/structure mismatch | Fix the target repo docs or add a bounded installer branch if reusable |
| Environment dependency issue | Improve installer diagnostics only if reusable |
| One-off local preference | Do not widen the skill unless it becomes repeatable |

## Hard rules

1. Keep `workflow` as control-plane routing; install repo-local graph semantics into the target repo.
2. Never let subagent-mined context become trusted without validation and promotion boundaries.
3. Do not bloat local `AGENTS.md`; deep graph behavior belongs in repo docs and generated local tooling.
4. Treat raw source-session inventory as part of graph readiness; unresolved source gaps block trust until imported, summarized, or persistently resolved.
5. Prefer marker-safe inserts over broad rewrites when patching repo docs.

## Cross-references

- [references/install.md](references/install.md) - installer behavior, generated surface, and validation contract
- [scripts/install.py](scripts/install.py) - deterministic installer
- [scripts/validate.sh](scripts/validate.sh) - skill self-validation wrapper

## Why this skill exists

Without a reusable installer, every project-local context graph becomes a bespoke chat-only pattern with inconsistent trust boundaries, file placement, and validation. This skill creates one repeatable repo-local shape: ordered session mining, validator-gated promotion, and compact retrieval surfaces that future agents can actually depend on.
