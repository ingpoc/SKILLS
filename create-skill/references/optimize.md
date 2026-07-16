# Optimize lane — apply targeted fixes

Loaded on demand when the operator picks the Optimize lane (or types "optimize / shrink / fix / repair skill", or after an Audit lane surfaces hard findings).

## Preflight

1. **Audit first** — `python3 ~/.codex/skills/create-skill/scripts/audit.py <skill>`. **Never edit blind.** The audit JSON is the input to this lane.
2. **Identify the dominant failure class** from the findings. See [checklist.md](checklist.md) for severity → fix mapping.
3. **Confirm scope with the operator** if the fix would change observable behavior (a description rewrite that narrows activation; a body restructure that moves anchors other docs link to).

## Do — by finding class

| Finding ID | Fix |
|---|---|
| `name_kebab_case` fails | Rename directory + update `name:` in frontmatter + grep + update every cross-reference in other skills / AGENTS.md / docs. Single commit. |
| `name_matches_dir` warns | Pick one as canonical. If renaming the directory, treat as the `name_kebab_case` fix above. |
| `description_present` fails | Author a description from scratch using [description.md](description.md). |
| `description_length` warns (≤ 8000 chars) | Either tighten to ≤ 1024 (spec portability) OR keep verbose if activation precision earns it. Multi-lane skills (autoresearch, goal-audit, knowledge-base, create-skill itself) deliberately exceed the cap. Decide intentionally — don't fix reflexively. |
| `description_length` fails (> 8000 chars) | Hard ceiling breached — wall-of-text description. Move detail into the body; description is for activation, not exhaustive documentation. |
| `description_has_triggers` warns | Add "Use when …" / "Triggers: …" phrasing with the actual operator words. See [description.md § Trigger word brainstorming](description.md). Read the result aloud — would the agent recognize "I want to do X" as a match? |
| `body_token_budget` warns (> 5000 tokens) | Move bulk into `references/<topic>.md` files; replace inline content with a one-line summary + link. Body should be a router/index. This skill (`create-skill`) is the canonical demonstration — SKILL.md is pure routing; lane procedures live here. |
| `body_token_budget` fails (> 15000 tokens) | Hard ceiling breached. Body restructure is mandatory before any further additions. See `autoresearch/SKILL.md` for an example of a body that pushed past this and how to split it. |
| `progressive_disclosure` warns — **multi-lane case** (Preflight / Do / Closeout repeat) | The body is a content dump masquerading as a router. **This is the principle the entire skill enforces, even when body_token_budget passes.** For each lane: (1) create `references/<lane>.md`, (2) move the lane's Preflight/Do/Closeout content there verbatim, (3) replace the body section with a one-line summary + table-row link in the entry router. After: only the lane the operator picks loads its procedure. See [the create-skill refactor](optimize.md#worked-example-create-skill-self-refactor) below for the canonical execution. |
| `progressive_disclosure` warns — **monolith case** (body > 4000 tokens, no references/ links) | Single-flow skill still over budget. Identify the largest deep-procedure block — usually evidence-gathering, gate-checking, or per-step worked examples — and extract those to `references/`. The body keeps the entry, universal rules, and pointers. |
| `self_validate_directive` warns | Insert the canonical blockquote right after the H1 (or after frontmatter if the skill has no H1): `> **Self-validate after edits.** Any change to this skill's files (SKILL.md, scripts/, references/, templates/, assets/) must be followed by \`./scripts/validate.sh\` from the skill directory. Hard findings → create-skill Optimize lane.` Then re-run `scripts/validate.sh` on the skill to confirm. |
| `referenced_files_exist` warns | Either create the missing file, fix the path, or remove the dangling link. Usually a typo or a file renamed without updating refs. |
| `allowed_tools_shape` warns | Fix the YAML — space-separated string `"Read Write Bash"` or list `[Read, Write, Bash]`. |

## Closeout

```bash
# Re-audit — must come back cleaner than before.
python3 ~/.codex/skills/create-skill/scripts/audit.py <skill-path>

# Diff the before/after finding counts and report to the operator.
```

If the optimization is a generalizable pattern (e.g., "always include a `## Hard rules` numbered list"), capture it via `builder memory add --type pattern` per AGENTS.md § Memory And Closeout.

If the optimization changed activation behavior (new trigger phrases, removed trigger phrases, lane restructure), note it in `docs/goal/STATUS.md` Recent Decisions per AGENTS.md memory rule.

## Order of operations (highest-leverage first)

When an audit returns multiple findings, work through them in this order — each fix often clears subsequent findings or makes them cheaper:

1. **`name_*` failures first.** Renaming is invasive (cross-references everywhere). Get it done before other edits create new references that also need fixing.
2. **`description_present` / `description_has_triggers` next.** These directly affect activation — a skill nobody can activate is invisible regardless of body quality.
3. **`progressive_disclosure` and `body_token_budget` hard failures.** Restructure the body into router + `references/` before adding any new content. Progressive disclosure is the most important architectural property — every wasted activation token compounds across every future invocation.
4. **`description_length` warnings — decide, don't reflexively fix.** Verbose descriptions are intentional for multi-lane skills. Tighten only when the verbosity isn't earning its activation precision.
5. **`referenced_files_exist`.** Cheap fixes — usually a typo.
6. **`name_matches_dir` cosmetic warnings.** Pay down when you're already in the area.

After every fix: re-run audit. Each finding count should drop.

## Lane-specific hard rules (apply only when optimizing)

1. **Never edit a SKILL.md without auditing first.** The audit JSON IS the input to this lane.
2. **Cross-runtime portability is opt-in.** This repo's local style deliberately exceeds the 1024-char description cap for activation precision. Use `--strict` only when a skill must work outside this repo (Codex / Gemini / Cursor / etc.).
3. **Body restructure preserves anchors.** When moving content from body to `references/`, keep the body's section headers — other docs and skills may link to them.
4. **One refactor at a time.** Rename + description rewrite + body restructure in one commit makes review impossible. Sequence them.

## Worked example — fixing `hallmark` (real finding)

The Audit lane found `hallmark` failing `body_token_budget` (~15.7k tokens > 15k sanity ceiling). Optimize lane procedure:

1. Read the target `SKILL.md` to understand its lane structure.
2. Group body content by phase / lane / topic.
3. For each group, create `references/<topic>.md` and move content verbatim.
4. Replace the body section with a one-line summary + link to the new reference file.
5. Preserve `## Hard rules` and the entry router in the body.
6. Re-audit; target `body_token_budget` ≤ 5000 tokens (soft pass) ideally; ≤ 15000 (hard pass) minimum.

## Worked example — `create-skill` self-refactor

The audit's `progressive_disclosure` check was *added* after the first version of `create-skill` shipped with three lanes inline (Preflight/Do/Closeout × 3 = 9 procedural sections in body). Body was 2828 tokens — under the 5000 soft cap, so `body_token_budget` passed. But ~60% of those tokens were lane-specific procedures only one chosen lane would ever use. The audit didn't catch it; the operator did.

The refactor:

1. Created `references/create.md`, `references/audit.md`, `references/optimize.md`.
2. Moved each lane's Preflight/Do/Closeout content verbatim into its file.
3. Replaced the body lane sections with one-row table entries linking to the new files.
4. Tightened description from 1748 → 933 chars (now ≤ 1024 spec cap).
5. Deleted the "Why this skill exists" paragraph (description carries that information).

Result: body 2828 → 993 tokens (−65%). Default audit clean; `--strict` audit clean. Every activation now loads ~1800 fewer tokens.

**The lesson encoded in `progressive_disclosure`:** body size below the cap is necessary but not sufficient. Multi-lane skills must store lane procedure progressively or they're paying the cost on every activation regardless of which lane runs.
