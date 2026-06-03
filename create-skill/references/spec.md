# Agent Skills spec — frontmatter + naming + progressive disclosure

Canonical contract from [agentskills.io/specification](https://agentskills.io/specification). Single source of truth for what a SKILL.md must contain. `scripts/audit.py` enforces this.

## Directory layout

```
.codex/skills/<name>/
├── SKILL.md          # REQUIRED — frontmatter + body
├── scripts/          # optional — deterministic executables (Python, Bash, etc.)
├── references/       # optional — deeper docs the body links to
├── templates/        # optional — file scaffolds
└── assets/           # optional — non-code resources
```

Only `SKILL.md` is required. Everything else loads on demand per progressive disclosure.

## Frontmatter fields

| Field | Required | Type | Constraint |
|---|---|---|---|
| `name` | yes | string | kebab-case (see § Name validation). Must match the parent directory name. |
| `description` | yes | string | Per spec: ≤ 1024 chars. **This repo permits longer for activation precision** — see [description.md](description.md). |
| `allowed-tools` | no | string or list | Whitelist of tools the skill may invoke. Space-separated string OR YAML list. Omit when the skill is pure guidance. Constrain to the minimum surface. |
| `license` | no | string | SPDX identifier. Optional. |
| `compatibility` | no | string or list | Free-text or list of runtime / dependency constraints. |
| `metadata` | no | mapping | Free-form. Common keys: `author`, `version`. |

Project-specific extensions seen in this repo (not in the agentskills.io spec, but consumed by Claude Agent SDK runtime configuration):

| Field | Type | Effect |
|---|---|---|
| `model` | string | Override default model for the skill (`sonnet`, `haiku`, `opus`). |
| `effort` | string | Reasoning effort hint (`low`, `medium`, `high`). |

These are tolerated by `scripts/audit.py` but not validated against an enum.

## Name validation

Canonical regex: `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`

Rules:

- Lowercase only.
- Must start with a letter.
- Hyphens separate segments — no leading hyphen, no trailing hyphen, no consecutive hyphens (`--`).
- Digits allowed within segments.

Examples:

| Name | Valid? | Reason |
|---|---|---|
| `pdf-processing` | yes | |
| `data-analysis` | yes | |
| `code-review` | yes | |
| `autoresearch` | yes | single segment is fine |
| `gh-fix-ci` | yes | three segments |
| `PDF-Processing` | **no** | uppercase |
| `-pdf` | **no** | leading hyphen |
| `pdf-` | **no** | trailing hyphen |
| `pdf--processing` | **no** | consecutive hyphens |
| `pdf_processing` | **no** | underscore not allowed |
| `1pdf` | **no** | must start with a letter |

The directory name and `name:` field must match. Renaming is a coordinated three-step: directory + frontmatter + cross-references.

## Progressive disclosure — the three load stages

Skills are loaded incrementally to keep agent context small:

| Stage | What loads | Budget | Audited as |
|---|---|---|---|
| **Discovery** | `name` + `description` only, for every skill in the registry | ~100 tokens per skill | `description_length` |
| **Activation** | The full `SKILL.md` body, when description matches operator intent | ≤ 5000 tokens recommended; ≤ 15000 sanity ceiling | `body_token_budget` |
| **Execution** | Scripts, references, assets — loaded only when the body explicitly invokes them | unbounded (loaded sparingly) | n/a |

Implications:

1. The body should be a router/index, not a content dump.
2. Bulk content goes in `references/<topic>.md`, linked from the body with a one-line summary.
3. Scripts in `scripts/` should be deterministic — no model judgment required to interpret their output.

## Body structure (project convention)

Not strictly mandated by the spec, but every skill in this repo follows it. Audit doesn't check for these but operators expect them:

```markdown
---
<frontmatter>
---

# <skill-name> — <one-line summary>

<opening paragraph: what this skill is for>

## Entry — <how the lane is chosen>

<AskUserQuestion table if multi-lane; otherwise omit>

## <Lane 1 name>

### Preflight
### Do
### Closeout

## <Lane 2 name>
...

## Hard rules

1. ...
2. ...

## Cross-references

- [references/foo.md](references/foo.md) — ...
- [scripts/bar.py](scripts/bar.py) — ...

## Why this skill exists

<one paragraph: the problem this skill solves that nothing else does>
```

Anchors that pay off later:

- `## Hard rules` — numbered, terse. Read once, enforced everywhere.
- `## Cross-references` — pointers, not duplication.
- `## Why this skill exists` — single paragraph. Catches future-you wondering "do we still need this?"

## Cross-runtime portability

Per agentskills.io's client showcase, the SKILL.md format is supported by Claude / Claude Code, OpenAI Codex, Gemini CLI, Cursor, GitHub Copilot, Goose, OpenCode, Letta, and ~30 other agent runtimes. To keep a skill portable, run `audit.py --strict` — this treats spec-soft items (description > 1024 chars, body > 5000 tokens) as hard. Skills that pass `--strict` work anywhere; skills that pass only the default mode are this-repo-only.
