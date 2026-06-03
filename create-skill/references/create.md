# Create lane — scaffold a new skill

Loaded on demand when the operator picks the Create lane (or types "create / scaffold / add a skill for X").

## Preflight

1. **Name not taken** — `ls .codex/skills/<name>` returns nothing.
2. **Name is kebab-case** — passes `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`. See [spec.md § Name validation](spec.md).
3. **Real use case named** — per agentskills.io best practices, prefer extracting from a hands-on task or synthesizing from existing project artifacts over generic theory. If the operator can't name a concrete trigger phrase + concrete output, ask via `AskUserQuestion` before scaffolding.
4. **Infer before asking** — classify the requested skill from the operator's wording and local artifacts first. Ask only when the answer changes the scaffold, validation strategy, runtime contract, or operator workflow. Do not ask about standard layout, validation wrapper, or other decisions the Create lane already owns.

## Intake — inference first, ask only for material unknowns

Before scaffolding, write down the inferred operating contract:

| Item | Required inference |
|---|---|
| Primary archetype | The dominant skill shape. Pick one; add secondary archetypes only when they change validation or required files. |
| Operator trigger | The concrete phrase or situation that should activate the skill. |
| Output / success evidence | What proves one run worked. Prefer observable evidence over prose claims. |
| Deterministic surface | What belongs in `scripts/` because it can run without model judgment. |
| Judgment surface | What remains agent reasoning in `SKILL.md` or `references/`. |
| Context loading | What loads by default, what is progressively disclosed, and what is only loaded on failure/deeper need. |

Use these archetypes as global structure, not domain-specific behavior:

| Archetype | Use when | Scaffold / validation implication |
|---|---|---|
| **Reference workflow** | The skill mainly guides judgment-heavy work. | Router body + `references/workflow.md`; validation focuses on activation, references, and closeout. |
| **Deterministic script workflow** | The skill transforms files, checks state, or runs repeatable commands. | `scripts/preflight.*`, `scripts/closeout.*`, and at least one deterministic smoke test. |
| **Browser / UI workflow** | Success depends on visible UI behavior. | Browser acceptance criteria and explicit screenshot/DOM evidence in closeout. |
| **Server / API workflow** | The skill starts a server, webhook, queue, background runtime, or API. | Port/env preflight, server lifecycle, API smoke, and read-only closeout status. |
| **Artifact generator** | The skill creates HTML, docs, reports, slides, spreadsheets, or similar outputs. | Template/example strategy and output validation criteria. |
| **Agent orchestration** | The skill routes work across subagents, queues, workers, or context handoffs. | Routing contract, context tiers, worker ownership, cancellation/release semantics. |
| **External service** | The skill depends on GitHub, OpenAI, Gmail, Drive, Vercel, or other service auth/API. | Auth/config preflight, official-source docs where needed, and graceful degraded behavior. |

If a material choice remains unclear, ask at most three short questions. Each question must put the best inferred answer first and label it `(Recommended)`. Ask about outcomes and tradeoffs, not implementation trivia.

Good questions:

- "Primary archetype?" when multiple archetypes would produce different scaffolds.
- "What proves a successful first run?" when the output is subjective or underspecified.
- "Should processing be push-triggered or manually invoked?" when that changes scripts/runtime.

Bad questions:

- Asking whether to include `scripts/validate.sh`; every skill gets it.
- Asking about folder names when the standard layout applies.
- Asking about details the prompt already answered.

## Do

```bash
SKILL_NAME="<kebab-case-name>"
mkdir -p ".codex/skills/${SKILL_NAME}/scripts" \
         ".codex/skills/${SKILL_NAME}/references"
cp .codex/skills/create-skill/templates/SKILL.md.template \
   ".codex/skills/${SKILL_NAME}/SKILL.md"

# Every skill must carry its own self-validation wrapper. Single source of
# truth — do not customize per-skill; the wrapper resolves the canonical
# audit.py via repo-root lookup.
cp .codex/skills/create-skill/templates/validate.sh \
   ".codex/skills/${SKILL_NAME}/scripts/validate.sh"
chmod +x ".codex/skills/${SKILL_NAME}/scripts/validate.sh"
```

Then `Edit` the placeholders. Required edits:

| Field | What to write |
|---|---|
| `name:` | kebab-case, must equal the directory name |
| `description:` | See [description.md](description.md) for the project style guide. Lead with what the skill does, list trigger phrases explicitly, include "Use when …" phrasing, name what it touches and what it returns. |
| `allowed-tools:` | Minimum needed; remove the line entirely if the skill is pure prose guidance. |
| Body sections | Replace stubs with real procedure. |

The generated procedure must reflect the inferred archetype. Keep `SKILL.md` as the activation router and first-page operating contract; move long archetype details into `references/`, deterministic operations into `scripts/`, reusable examples into `examples/`, and reusable starter files into `templates/`.

## Closeout

```bash
# 1. Self-validate via the skill's own wrapper — must exit 0.
".codex/skills/${SKILL_NAME}/scripts/validate.sh"

# 2. Cross-runtime portability check — optional, only if the skill should work outside this repo
#    (Codex / Gemini / Cursor / etc.). Promotes spec-soft warnings to hard.
".codex/skills/${SKILL_NAME}/scripts/validate.sh" --strict
```

Every skill carries `scripts/validate.sh` — a thin wrapper around the canonical `create-skill/scripts/audit.py`. The wrapper is identical in every skill (do not customize); it just makes self-validation one command away no matter which skill you're in.

If the skill auto-fires on operator phrases (`/start`, `/save-session`, `/goal-audit` precedent), add a row to the Skill Triggers table in `AGENTS.md`. **Do not** edit `AGENTS.md` before running `workflow quality-gate agents-md` per the project's AGENTS.md required-triggers contract.

## Author principles (specific to Create lane)

- **Start from real expertise** (agentskills.io best practice). The most effective skills are extracted from a real task you've already done with an agent — complete it, correct it, then crystallize the pattern. Generic-best-practice skills age poorly.
- **Infer first, ask only for material forks.** The agent should choose obvious defaults from the requirement. If it asks, the first answer is the recommended scaffold path and explains the tradeoff.
- **Archetypes shape validation, not domain behavior.** Use archetypes to decide required sections, scripts, and evidence. Do not bake one skill's domain lessons into the global Create lane.
- **One purpose per skill.** Multi-lane skills exist (this one, autoresearch) but the lanes must share a single operator-vocabulary noun. If you're stretching to find a shared noun, it's two skills.
- **Body is a router, not a content dump.** Lane Preflight/Do/Closeout content goes in `references/<lane>.md`; the body links to it. This skill demonstrates the pattern — see `SKILL.md` (router) + this file (lane detail).
- **Scripts must be deterministic.** Anything in `scripts/` runs without model judgment. If the operation needs judgment, that's body or reference content, not a script.
- **Optimize from friction, not preference.** During closeout, update the skill only when a reusable activation, workflow, context, validation, or preflight/closeout gap caused friction. Fix target code, scripts, environment, or project docs when the failure belongs there.
