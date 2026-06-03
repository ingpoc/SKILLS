# Writing skill descriptions — the highest-leverage field

The `description:` is loaded into context **for every conversation** as part of the discovery pass. It is the single field that decides whether your skill activates. Get it wrong and the skill is invisible. Get it right and the agent picks it without prompting.

Source guidance: [agentskills.io/skill-creation/optimizing-descriptions](https://agentskills.io/skill-creation/optimizing-descriptions). This doc adds project-local style notes.

## The four rules

1. **Imperative phrasing.** Address the agent. "Use this skill when X" — not "This skill is for X."
2. **User intent, not internal mechanics.** Describe what the user is trying to do, not how the skill implements it.
3. **List trigger contexts explicitly.** Including the ones where the user *doesn't* use your domain vocabulary.
4. **Stay within budget.** Strict spec: ≤ 1024 chars. Local style: longer is permitted *when activation precision justifies it* (see § Local style).

## Before / after — the canonical example

From the agentskills.io docs. Both edits move the description in the right direction:

```yaml
# Before — too narrow, too sparse, hard to activate.
description: Process CSV files.

# After — broader scope, explicit triggers, intent-led.
description: >
  Analyze CSV and tabular data files — compute summary statistics,
  add derived columns, generate charts, and clean messy data. Use this
  skill when the user has a CSV, TSV, or Excel file and wants to
  explore, transform, or visualize the data, even if they don't
  explicitly mention "CSV" or "analysis."
```

What the rewrite does:

| Move | Why |
|---|---|
| Broadens scope: CSV → "CSV, TSV, or Excel" | Catches the user who uploads a `.tsv` and doesn't say "CSV" |
| Adds intent verbs: "explore, transform, or visualize" | Matches operator vocabulary |
| Adds explicit trigger: "even if they don't explicitly mention CSV" | Tells the agent to activate on intent, not jargon |
| Imperative: "Use this skill when…" | Direct address to the agent |

## Good vs bad — one more pair

```yaml
# Good — concrete capabilities + explicit triggers.
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.

# Bad — vague, no triggers, won't activate reliably.
description: Helps with PDFs.
```

## Trigger word brainstorming

Before writing the description, list:

| List | Example for a "create-skill" skill |
|---|---|
| **What the operator literally types** | "create a skill for X", "new skill", "scaffold a skill", "add a SKILL.md" |
| **Adjacent verbs they might use** | "set up", "register", "build", "make", "author" |
| **What they call the artifact** | "skill", "SKILL.md", ".claude/skills entry", "command", "tool" |
| **What they're trying to accomplish (no jargon)** | "automate a thing I keep doing", "package this workflow", "save this as a reusable command" |
| **Negation / proxy phrases** | "this would be useful as a skill", "could we turn this into a skill?" |

Then pour as many as fit into the description, joined with "or any variant pairing X / Y / Z language with A or B or C."

This is the project's verbose-description pattern — see `autoresearch/SKILL.md` and `goal-audit/SKILL.md` for full examples.

## Local style — when verbose descriptions are OK

The agentskills.io spec caps descriptions at 1024 chars. This repo deliberately exceeds that cap for skills where activation precision is critical. Precedent:

| Skill | Description length | Why it's verbose |
|---|---|---|
| `autoresearch` | ~1300 chars | Three-lane skill — each lane has different trigger phrases. Ambiguous activation = wasted operator time. |
| `goal-audit` | ~1100 chars | Lists multiple proactive-fire conditions ("after >2-day gap", "after major framework change") in addition to operator phrases. |
| `knowledge-base` | ~1680 chars | Seven distinct operations (REFRESH / MAINTAIN / INGEST / AUDIT / SEARCH / DEDUPE / RUBRIC) each needing its own trigger surface. |
| `save-session` | ~480 chars | Single-purpose skill — no lanes to disambiguate. |
| `implementation` | ~350 chars | Single linear flow. |

Rule of thumb:

- **Single-purpose skill, one flow** → aim for ≤ 1024 chars. No reason to bloat.
- **Multi-lane skill** → as long as needed to disambiguate, capped by the 8000-char sanity bound.
- **Proactive-fire skill** (auto-activates on conditions, not just operator phrases) → include those conditions explicitly.

When `--strict` audit fails on length, decide:

- Make it cross-runtime portable → tighten to ≤ 1024.
- Keep activation precision → leave it, accept the soft warn, document the choice in the "Why this skill exists" footer.

## Common failure modes the audit catches

| Symptom in audit | Likely cause | Fix |
|---|---|---|
| `description_present: fail` | Missing or empty `description:` field | Author one — see § Trigger word brainstorming |
| `description_length: warn` (≤ 8000) | Spec cap exceeded; permitted locally | Verify the verbosity is earning its keep; otherwise tighten |
| `description_length: fail` (> 8000) | Wall-of-text description | Move detail into the body; description should be discoverable, not exhaustive |
| `description_has_triggers: warn` | No "Use when …" / "Triggers:" phrasing | Add explicit trigger phrases — the agent doesn't infer them |

## Self-test — read it aloud

Before committing a description, read it aloud and ask: *"Would the agent recognize 'I want to do X' as a match for this?"* If the description uses your internal jargon but the operator says it in plain English, activation fails. Bias every word toward operator vocabulary.

## Anti-patterns

- **"This skill provides …"** — passive, not addressed to the agent. Use "Use this skill to …".
- **Listing implementation details** — "Uses regex to parse the body" is not a trigger. The operator doesn't care.
- **Vague abstractions** — "Handles tasks related to …" matches everything and nothing. Be specific or omit.
- **Trigger phrases the operator would never type** — "audits frontmatter integrity" sounds clean but no operator says it. They say "check my skill" or "is my skill broken?"
- **Forgetting the "even if they don't say …" clause** — this is the highest-leverage single sentence. It catches proxy phrasing.
