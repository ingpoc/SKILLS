---
name: session-orchestrate
description: "Run an explicit, bounded experiment that splits a long project outcome across fresh Codex tasks in the same project. Use when the operator asks to orchestrate sessions, continue autonomously across tasks, avoid repeated compaction, set a session-sized Codex goal from the current product plan or checkpoint, or test whether save-session and resume-session improve continuity. Do not invoke implicitly: task creation must be explicitly authorized."
allowed-tools: Read Bash get_goal create_goal update_goal codex_app__list_projects codex_app__create_thread
---

# session-orchestrate — bounded fresh-task chaining

> **Self-validate after edits.** Any change to this skill's files must be followed by `./scripts/validate.sh` from the skill directory.

This is an opt-in experiment, not an infinite autonomous loop. It chooses one substantial, verifiable goal that should fit a fresh task, preserves exact goal state through `save-session` and `resume-session`, and creates at most one successor task per completed handoff.

## Operating contract

| Field | Decision |
|---|---|
| Primary archetype | agent orchestration with deterministic transaction helpers |
| Operator trigger | explicit `$session-orchestrate` invocation or an explicit request to create a successor task |
| Success evidence | exact goal round-trip, one same-project successor, no duplicate spawn, and a mechanically recorded stop reason |
| Persistent state | project `.claude/session-data/ORCHESTRATION.json`; tactical work remains in `CURRENT.md` |
| Default bound | three task hops; extension requires fresh operator authorization |
| Judgment surface | choosing the next session-sized goal and deciding whether its stop conditions are truly met |

## Main flow

Read [references/workflow.md](references/workflow.md) and follow the matching entry or closeout lane. Use [scripts/chain_state.py](scripts/chain_state.py) for every state transition and [scripts/validate_goal.py](scripts/validate_goal.py) before calling `create_goal`.

## Gotchas

| Failure | Control |
|---|---|
| A broad phase objective causes repeated compaction | Split at one product-plan deliverable plus its narrow verification gate; reject goals outside the validator's size envelope. |
| Two tasks create the same successor | `prepare-handoff` issues one nonce and refuses another spawn while a handoff is pending. |
| A completed goal is accidentally recreated | Save completed goals as `reference-only`; only unfinished emergency handoffs use `ensure-active`. |
| A chain crosses deployment, spend, auth, or phase gates | Stop the chain and checkpoint the authority requirement instead of creating a successor. |
| A hook guesses context from transcript bytes | The only hook runs after an actual automatic compaction and only when an active orchestration state exists. |

## Hard rules

1. **Explicit consent owns task creation.** The skill may create a successor only when the operator explicitly authorized this chain because a skill cannot broaden task-creation authority by itself.
2. **One task, one goal.** Keep the exact objective stable until it is completed, blocked, or handed off unfinished because silent goal drift invalidates the experiment.
3. **Deterministic bounds win.** Never exceed `max_hops`, bypass a pending nonce, or let model judgment declare a mechanical check passed because those controls prevent runaway and duplicate work.
4. **Authority gates stop the chain.** Provider spend, deployment, external sends, destructive operations, secrets, and new product-phase authorization require the operator.
5. **Same project is mandatory.** Resolve the exact project root with `codex_app__list_projects`; do not create a projectless successor because projectless tasks lose the intended workspace contract.
6. **No broad rediscovery.** Resume from `CURRENT.md`, verify its first command, then load only the owner section needed for the next goal.

## Cross-references

- [references/workflow.md](references/workflow.md) — entry, goal selection, handoff, and keep/drop criteria
- [scripts/chain_state.py](scripts/chain_state.py) — nonce-protected chain transaction state
- [scripts/validate_goal.py](scripts/validate_goal.py) — session-goal shape and size gate
- [scripts/postcompact_nudge.py](scripts/postcompact_nudge.py) — active-chain-only fallback after automatic compaction
- sibling skills: `save-session`, `resume-session`, `session-introspection`

## Why this skill exists

Long Codex tasks can spend context repeatedly reconstructing tactical state after compaction. This experiment tests whether bounded fresh tasks with exact checkpoints are cheaper and more reliable. If repeated trials do not improve continuity or the handoff overhead exceeds the saved rediscovery, remove this skill and its `PostCompact` hook.
