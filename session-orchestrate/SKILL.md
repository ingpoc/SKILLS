---
name: session-orchestrate
description: "Orchestrate product-plan completion across substantive Codex tasks. Use when the operator invokes $session-orchestrate, asks to continue eligible saved work, derive implementation goals from a roadmap, coordinate work across sessions, or avoid repeated compaction. A bare invocation reuses a fresh source-fingerprinted program map, rebuilding only when stale; it resumes saved work only when resume-session proves the checkpoint fresh and consistent and the current owner plan still permits it."
allowed-tools: Read Bash Grep Glob get_goal create_goal update_goal update_plan spawn_agent codex_app__list_projects codex_app__create_thread
---

# session-orchestrate — product-plan completion across bounded tasks

> **Self-validate after edits.** Run `./scripts/validate.sh` from this skill directory after any change.

This skill reads the repository's product-plan owner, assesses implementation against live evidence, maintains a source-fingerprinted program map in the repo's `.session/` workspace, executes one goal, and creates at most one same-project successor per handoff. It preserves exact unfinished work through `save-session` and `resume-session`. Running `$session-orchestrate` authorizes orchestration now; it does not make old checkpoint or session-history details true.

## Operating contract

| Field | Decision |
|---|---|
| Primary archetype | product-program orchestration with deterministic transaction helpers |
| Operator trigger | explicit `$session-orchestrate` invocation or explicit successor-task request |
| Success evidence | owner-backed remaining-goal map, admitted acceptance gap, durable product/evidence delta, exact goal round-trip, at most one successor, and a mechanical stop reason |
| Persistent state | project `.session/`: generated `PLAN.md`, canonical `TRACKING.json`, tactical `CURRENT.md`, and mechanical `ORCHESTRATION.json` |
| Default bound | remaining goals in the current authorized phase, capped at 12 task hops |
| Judgment surface | mapping plan gates to implementation evidence, ordering remaining goals, and deciding whether proof is sufficient |

## Main flow

Resolve the product root first, then run `python3 ~/.codex/skills/session-orchestrate/scripts/entry.py --root "$(git rev-parse --show-toplevel)"` before broad retrieval. The helper refuses the global skills repository, creates or validates the product's `.session/`, performs one-way legacy migration from `.claude/session-data/` when needed, delegates checkpoint eligibility to `resume-session`, checks plan-source freshness and chain consistency, and returns a cheap owner/plan/status inventory plus `exploration.action`. Read [references/workflow.md](references/workflow.md), use deterministic owner reads first, invoke the configured read-only `cost_scan` sidecar only when the returned trigger still has clear ROI, rebuild only when `workspace.program_action` says so, and follow the returned mode.

Use [scripts/chain_state.py](scripts/chain_state.py) for every state transition, [scripts/validate_goal.py](scripts/validate_goal.py) before `create_goal`, and [scripts/checkpoint.py](scripts/checkpoint.py) for exact-goal closeout.

## Gotchas

| Failure | Control |
|---|---|
| A broad phase objective causes repeated compaction | Split at one plan deliverable plus its narrow integration seam and verification gate. |
| A tiny goal spends a task proving work already done | Probe the current acceptance gap before goal creation. Reconcile proven items inline, select the next real gap in the same task, and create no hop for reconciliation-only work. |
| Two tasks create the same successor | `prepare-handoff` issues one nonce and refuses another spawn while pending. |
| A successor repeats product-plan discovery | Prepare and validate its exact next objective and first command before spawning; reuse the fresh source-fingerprinted map. |
| Claim succeeds but the successor is interrupted before `create_goal` | The claimed handoff retains the exact objective and first command until `set-goal` settles it; reclaiming the nonce is idempotent. |
| The helper is invoked from `~/.codex/skills` | Refuse the root before creating `.session`; rerun with the product repository root. |
| A completed goal is recreated | Save completed goals as `reference-only`; only unfinished handoffs use `ensure-active`. |
| A chain crosses an authority or phase gate | Stop and record the requirement instead of creating a successor. |
| A fresh task contains an old `CURRENT.md` | `entry.py` returns `review-checkpoint`; never auto-create its saved goal. |
| Past sessions look more complete than the repository | History and skill mentions are hints; current owners and live acceptance evidence win. |
| File or commit counts look like progress | Never manufacture a completion percentage; score only explicit, evidenced plan gates. |
| The derived goal map becomes another product owner | `TRACKING.json` stores source hashes and evidence only; owner changes make it stale, while `PLAN.md` is a generated projection. |
| Legacy and canonical state drift | Once `.session/` exists, every tool uses it; legacy files are retained only as non-authoritative migration evidence. |
| The agent keeps designing after the route is known | After the map and goal pass, make the smallest concrete attempt in the next tool action. |
| A scan sidecar costs more context than it saves | Keep history, commit, and skill mining out of the cheap path; delegate only bounded noisy discovery with a compact result contract. |
| The runtime cannot select `cost_scan` | Work directly for small scans or use an honestly labeled built-in read-only explorer; never claim the custom model pin or recurse through `codex exec` by default. |

## Hard rules

1. **Refresh only when stale.** Always run entry and honor source fingerprints. Reuse a fresh program map; read the changed owner slice and rebuild only when stale or missing.
2. **One task, one substantive goal.** A new goal must close a currently failing acceptance gap and produce both an implementation/runtime delta and retained evidence. Keep its exact objective stable until completion, a real blocker, or an unfinished handoff.
3. **Two planning levels.** `.session/TRACKING.json` names all ordered remaining goals; `create_goal` receives only the selected session goal and its concrete actions.
4. **Deterministic bounds win.** Never exceed `max_hops`, bypass a pending nonce, or replace a mechanical failure with model judgment.
5. **Authority gates stop the chain.** Spend, deployment, external sends, destructive operations, secrets, authentication, and new product phases require their normal authority.
6. **Same project is mandatory.** Resolve the exact project root before creating a successor.
7. **Bounded discovery.** Read the declared route first, then minimal plan/status slices and live proof. Session history is off by default; a justified `cost_scan` may inspect at most three relevant sessions.
8. **One owner per fact.** Product plan owns intended completion; `.session/TRACKING.json` owns derived cross-session progress; generated `PLAN.md` is read-only; `CURRENT.md` owns tactical handoff; `ORCHESTRATION.json` owns chain mechanics.
9. **History is not truth.** Git history, past sessions, file presence, and prior skills may route investigation but cannot prove completion or grant authority.
10. **Reconciliation is not a goal.** If a bounded preflight proves the candidate already complete, record the evidence and select again inline. Never initialize a chain, consume a hop, or spawn a successor solely for reconciliation.

## Cross-references

- [references/workflow.md](references/workflow.md) — source precedence, program mapping, goal selection, negative scenarios, handoff, and closeout
- [references/program-schema.md](references/program-schema.md) — canonical `.session` files, program JSON input, sync, status, and goal-update commands
- [scripts/session_workspace.py](scripts/session_workspace.py) — workspace bootstrap, legacy migration, source fingerprints, generated plan, and evidence tracking
- [scripts/project_inventory.py](scripts/project_inventory.py) — cheap owner/plan/status inventory by default; bounded history, commit, and skill hints only in explicit `explore` mode
- [scripts/entry.py](scripts/entry.py) — checkpoint, chain, and project-inventory entry resolver
- [scripts/chain_state.py](scripts/chain_state.py) — nonce-protected chain transaction state
- [scripts/validate_goal.py](scripts/validate_goal.py) — session-goal shape and size gate
- [scripts/checkpoint.py](scripts/checkpoint.py) — exact-goal `save-session` wrapper
- [scripts/postcompact_nudge.py](scripts/postcompact_nudge.py) — active-chain-only fallback after automatic compaction
- [scripts/test_project_inventory.py](scripts/test_project_inventory.py) — discovery bounds and no-session-message-echo assertions
- [scripts/test_session_orchestrate.py](scripts/test_session_orchestrate.py) — transaction, entry, freshness, conflict, hook, and checkpoint assertions
- [scripts/test_session_workspace.py](scripts/test_session_workspace.py) — workspace, migration, stale-source, projection, and evidence assertions
- sibling skills: `save-session`, `resume-session`, `session-introspection`
