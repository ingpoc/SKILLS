# Friction Risk Rubric

Use this reference before recommending a setup change. The goal is leverage
without turning Codex into a noisy control system.

## Risk Levels

| Setup | Friction | Main risk | Default stance |
|---|---|---|---|
| Local environment action | low | toolbar clutter | recommend for repeated commands |
| Workflow doc | low | stale docs | recommend for multi-step lanes |
| Skill | low/medium | over-triggering or too much context | recommend for reusable methods |
| Subagent recipe | low/medium | token cost or summary loss | recommend for noisy read-heavy work |
| Memory | medium | stale or overgeneralized lesson | use only for reusable patterns |
| AGENTS.md rule | medium | always-loaded context cost | use for repeated always-on behavior |
| Automation | medium/high | inbox noise or unsafe local edits | use after manual workflow is stable |
| MCP/plugin | medium/high | permissions and external side effects | use when local repo is insufficient |
| Hook | high | context pollution or blocked flow | use only for narrow lifecycle edges |

Local environment actions are the default answer for repeated commands that
the user or agent keeps typing manually. They should be configured through the
Codex app settings first because the public docs define behavior and placement,
not a stable hand-written schema.

## Scoring

Score each proposed setup from 0-2:

- Evidence strength: 0 one-off, 1 plausible, 2 repeated with proof
- Friction cost: 0 high, 1 medium, 2 low
- Validation clarity: 0 unclear, 1 manual, 2 deterministic
- Reversibility: 0 hard, 1 moderate, 2 easy

Recommend immediately only when total score is 6 or higher. For 4-5, recommend
a probe. Below 4, do not set it up yet.

## Hook Rules

Hooks require extra scrutiny:

- Prefer `UserPromptSubmit` for routing/context hints.
- Prefer `Stop` for final validation nudges.
- Use `PreToolUse` only for narrow unsafe action boundaries.
- Fail open when evidence is ambiguous.
- Delegate noisy cleanup proof to a subagent.

Do not use hooks to compensate for unclear docs, unstable workflows, or missing
tests unless the hook guards a specific unsafe edge.

## Automation Rules

Automations are for stable recurring work:

- method already works manually
- output can be triaged compactly
- worktree execution is available for edits
- inbox noise is expected to be low

If the task still needs frequent steering, make or improve a skill first.
