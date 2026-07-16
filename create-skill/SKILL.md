---
name: create-skill
description: "Compatibility and deterministic maintenance layer for locally authored skills. Use when the official skill-creator has drafted a skill, or when the operator asks to audit, validate, optimize, shrink, repair, or diagnose activation of an existing skill. Owns local schema, reference, and progressive-disclosure checks; it does not own first-draft authoring or portfolio-level duplicate routing."
allowed-tools: Read Write Bash
---

# create-skill — compatibility audit and optimization

> **Self-validate after edits.** Any change to this skill's files (SKILL.md, scripts/, references/, templates/, assets/) must be followed by `./scripts/validate.sh` from the skill directory. Hard findings → create-skill Optimize lane.

Router skill. Body holds only what's needed at every activation: lane selection, universal invariants, and pointers. Lane procedure loads on demand from `references/`.

## Entry — pick a lane

Infer the lane from the operator's request. Ask a concise question only when the intended observable behavior cannot be determined safely:

| Lane | When to choose | Procedure |
|---|---|---|
| **Create** | New skill | Use the official `$skill-creator`, then return here only for local validation |
| **Audit** | Inspect existing skill(s) — deterministic checks | [references/audit.md](references/audit.md) |
| **Optimize** | Hard finding from audit OR activation failure OR oversized body | [references/optimize.md](references/optimize.md) |

Skip the question when the typed prompt names a lane unambiguously:

| Phrase pattern | Lane |
|---|---|
| "create / scaffold / add a skill for X" | Delegate the draft to `$skill-creator`; audit the result here |
| "audit / check / validate skill(s)" | Audit |
| "optimize / shrink / fix / repair / why isn't X activating" | Optimize |
| anything ambiguous ("work on a skill", "review skills") | **Ask.** |

## Spec at a glance

| Field | Required | Constraint |
|---|---|---|
| `name` | yes | kebab-case `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`, equals directory name |
| `description` | yes | ≤ 1024 chars (spec); local style permits longer for activation precision |
| `allowed-tools` | no | space-separated string or list; minimize |

Full spec + name validation rules + progressive-disclosure budgets: [references/spec.md](references/spec.md).
Description authoring guide + trigger brainstorming: [references/description.md](references/description.md).
Per-check rationale + finding→fix mapping: [references/checklist.md](references/checklist.md).

## Audit at a glance

```bash
python3 ~/.codex/skills/create-skill/scripts/audit.py --all
python3 ~/.codex/skills/create-skill/scripts/audit.py <skill> --strict
python3 ~/.codex/skills/create-skill/scripts/audit.py <skill> --json
```

Exit 0 = clean or soft-only. Exit 1 = hard findings → switch to Optimize lane.

## Hard rules (universal — apply to every lane)

1. **Audit before edit.** Never modify a SKILL.md without running `scripts/audit.py` first. Audit output IS the input to Optimize lane.
2. **Name == directory.** Renaming is coordinated: dir + frontmatter + every cross-reference in one commit.
3. **Body is a router, not a content dump.** Bulk → `references/`. ≤ 5000 tokens (soft warn), ≤ 15000 (hard fail). This skill is the canonical demonstration.
4. **Trigger words are operator words.** Descriptions activate on the vocabulary operators actually type, not internal jargon. See [references/description.md](references/description.md).
5. **`scripts/` is deterministic.** No model-in-the-loop. If the operation needs judgment, it belongs in the body or a reference, not a script.
6. **Use the current scope owner.** User-global skills default to `$HOME/.agents/skills`; repository skills live under `.agents/skills`. Keep a skill under `$HOME/.codex/skills` only while a live Codex-specific compatibility caller requires that path.

## Cross-references

- [references/audit.md](references/audit.md) — Audit lane (commands, output format, JSON shape)
- [references/optimize.md](references/optimize.md) — Optimize lane (per-finding fixes, order of operations, worked example)
- [references/spec.md](references/spec.md) — frontmatter spec + name validation + progressive disclosure
- [references/description.md](references/description.md) — description authoring + trigger brainstorming
- [references/checklist.md](references/checklist.md) — every audit check ID ↔ remediation
- [scripts/audit.py](scripts/audit.py) — deterministic audit; `--all`, `--strict`, `--json`
- External: [agentskills.io/specification](https://agentskills.io/specification), [agentskills.io/skill-creation/best-practices](https://agentskills.io/skill-creation/best-practices).
