---
name: session-orchestrate
description: "Orchestrate product-plan completion across bounded Codex tasks. Use when the operator invokes $session-orchestrate, asks to continue eligible saved work, derive implementation goals from a roadmap, coordinate work across sessions, or avoid repeated compaction. A bare invocation rebuilds current product and implementation state; it resumes saved work only when resume-session proves the checkpoint fresh and consistent and the current owner plan still permits it."
allowed-tools: Read Bash Grep Glob get_goal create_goal update_goal update_plan codex_app__list_projects codex_app__create_thread
---

# session-orchestrate — product-plan completion across bounded tasks

> **Self-validate after edits.** Run `./scripts/validate.sh` from this skill directory after any change.

This skill reads the repository's product-plan owner, assesses implementation against live evidence, derives the ordered remaining session goals, executes one goal, and creates at most one same-project successor per handoff. It preserves exact unfinished work through `save-session` and `resume-session`. Running `$session-orchestrate` authorizes orchestration now; it does not make old checkpoint or session-history details true.

## Operating contract

| Field | Decision |
|---|---|
| Primary archetype | product-program orchestration with deterministic transaction helpers |
| Operator trigger | explicit `$session-orchestrate` invocation or explicit successor-task request |
| Success evidence | owner-backed remaining-goal map, verified session goal, exact goal round-trip, one successor, no duplicate spawn, and a mechanical stop reason |
| Persistent state | project `.claude/session-data/ORCHESTRATION.json`; tactical work remains in `CURRENT.md` |
| Default bound | remaining goals in the current authorized phase, capped at 12 task hops |
| Judgment surface | mapping plan gates to implementation evidence, ordering remaining goals, and deciding whether proof is sufficient |

## Main flow

Run `python3 scripts/entry.py` before broad retrieval. It delegates checkpoint eligibility to `resume-session`, checks chain consistency, and returns a bounded inventory of owner routes, plan/status candidates, git evidence, local skills, and recent project-session hints. Read [references/workflow.md](references/workflow.md), rebuild the program map from current owners, and follow the returned mode.

Use [scripts/chain_state.py](scripts/chain_state.py) for every state transition, [scripts/validate_goal.py](scripts/validate_goal.py) before `create_goal`, and [scripts/checkpoint.py](scripts/checkpoint.py) for exact-goal closeout.

## Gotchas

| Failure | Control |
|---|---|
| A broad phase objective causes repeated compaction | Split at one plan deliverable plus its narrow integration seam and verification gate. |
| Two tasks create the same successor | `prepare-handoff` issues one nonce and refuses another spawn while pending. |
| A completed goal is recreated | Save completed goals as `reference-only`; only unfinished handoffs use `ensure-active`. |
| A chain crosses an authority or phase gate | Stop and record the requirement instead of creating a successor. |
| A fresh task contains an old `CURRENT.md` | `entry.py` returns `review-checkpoint`; never auto-create its saved goal. |
| Past sessions look more complete than the repository | History and skill mentions are hints; current owners and live acceptance evidence win. |
| File or commit counts look like progress | Never manufacture a completion percentage; score only explicit, evidenced plan gates. |
| The derived goal map becomes another roadmap | Keep it disposable in the task plan; update only the repo-declared implementation owner. |
| The agent keeps designing after the route is known | After the map and goal pass, make the smallest concrete attempt in the next tool action. |

## Hard rules

1. **Rebuild current state.** Read the product-plan owner and implementation evidence on every invocation. Resume saved work only when it is mechanically eligible and still permitted by the current plan.
2. **One task, one goal.** Keep the exact objective stable until completion, a real blocker, or an unfinished handoff.
3. **Two planning levels.** The program map names all ordered remaining goals; `create_goal` receives only the selected session goal and its concrete actions.
4. **Deterministic bounds win.** Never exceed `max_hops`, bypass a pending nonce, or replace a mechanical failure with model judgment.
5. **Authority gates stop the chain.** Spend, deployment, external sends, destructive operations, secrets, authentication, and new product phases require their normal authority.
6. **Same project is mandatory.** Resolve the exact project root before creating a successor.
7. **Bounded discovery.** Read the declared route first, then minimal plan/status slices and live proof. Inspect no more than three recent project sessions for conventions, friction, or relevant skills.
8. **One owner per fact.** Product plan owns intended completion; the repo status surface owns durable progress; `CURRENT.md` owns tactical handoff; `ORCHESTRATION.json` owns chain mechanics.
9. **History is not truth.** Git history, past sessions, file presence, and prior skills may route investigation but cannot prove completion or grant authority.

## Cross-references

- [references/workflow.md](references/workflow.md) — source precedence, program mapping, goal selection, negative scenarios, handoff, and closeout
- [scripts/project_inventory.py](scripts/project_inventory.py) — bounded read-only owner, plan, status, git, local-skill, and project-session inventory
- [scripts/entry.py](scripts/entry.py) — checkpoint, chain, and project-inventory entry resolver
- [scripts/chain_state.py](scripts/chain_state.py) — nonce-protected chain transaction state
- [scripts/validate_goal.py](scripts/validate_goal.py) — session-goal shape and size gate
- [scripts/checkpoint.py](scripts/checkpoint.py) — exact-goal `save-session` wrapper
- [scripts/postcompact_nudge.py](scripts/postcompact_nudge.py) — active-chain-only fallback after automatic compaction
- [scripts/test_project_inventory.py](scripts/test_project_inventory.py) — discovery bounds and no-session-message-echo assertions
- [scripts/test_session_orchestrate.py](scripts/test_session_orchestrate.py) — transaction, entry, freshness, conflict, hook, and checkpoint assertions
- sibling skills: `save-session`, `resume-session`, `session-introspection`
