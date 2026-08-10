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
| Successor authority | The trigger is the explicit request required to create one eligible same-project successor after `spawn_allowed: true`; do not ask again |
| Success evidence | owner-backed remaining-goal map, admitted acceptance gap, source-frozen scoped proof, durable product/evidence delta, exact goal round-trip, at most one successor, and a mechanical stop reason |
| Persistent state | project `.session/`: generated `PLAN.md`, canonical `TRACKING.json`, tactical `CURRENT.md`, and mechanical `ORCHESTRATION.json` |
| Default bound | remaining goals in the current authorized phase, capped at 12 task hops |
| Judgment surface | mapping plan gates to implementation evidence, ordering remaining goals, and deciding whether proof is sufficient |

## Main flow

Resolve the caller's current Git product root, then run `python3 ~/.codex/skills/session-orchestrate/scripts/entry.py --compact --root "$(git rev-parse --show-toplevel)"` once. When an authorized successor prompt supplies a nonce, add `--claim-nonce <nonce>`; this mechanically claims, canonicalizes, binds, and materializes the exact objective without shell extraction. Follow `route_receipt` until one of its listed invalidators changes. Run its `reference_command` once only when present, and its `goal_detail_argv` only when the selected goal's actions or routes are needed. A claimed handoff needs neither read—use its `goal_file`, call `create_goal` with that exact objective, settle with `set-goal`, execute `first_command`, then immediately record its returned hash with `consume-command`. Re-entry never replays a consumed command.

The helper refuses the global skills repository, creates or validates only the current product's `.session/`, delegates checkpoint eligibility to `resume-session`, checks plan and chain consistency, and returns a cheap owner/status inventory. Use deterministic owner reads first. If delegation is still plausible, let `codex-routing-policy` choose the lane, `subagent-playbook` choose the agent type, and `codex-efficient-delegation` decide whether the bounded treatment repays its overhead; a successor is continuity transfer, not subagent delegation. Rebuild only when `workspace.program_action` says so, and rebuild derived projections in place—never delete `.session` to recover staleness.

If a claimed handoff's owner sources changed, `revalidate-claimed-handoff` keeps its exact goal and restricts review to the changed owner slice; do not reopen broad planning or history.

Use [scripts/chain_state.py](scripts/chain_state.py) for every state transition, [scripts/validate_goal.py](scripts/validate_goal.py) before `create_goal`, and [scripts/checkpoint.py](scripts/checkpoint.py) for exact-goal closeout.

## Hard rules

1. **One substantive goal.** Split independent deliverables, but keep one accepted milestone's implementation, actual-target verification, and repository-required promotion/handoff stages in one `project-lifecycle`. Reconcile already-proven work inline without consuming a hop.
2. **Reuse deterministic receipts.** Refresh only after a receipt invalidator changes. Record proof by scope plus product and optional proof-environment fingerprints; a newer generation supersedes only that scope. A selector must match the admitted goal; a dynamic queue retains only its exact unfinished target.
3. **Preserve exact transactions.** Keep one canonical objective until completion or handoff, consume each admitted command once, and honor hop/nonce bounds. A same-goal successor requires a paused source Codex goal plus a genuine context, compaction, or operator-requested task boundary; a next-goal successor requires a completed source goal plus accepted evidence. Role switches, fixes, retests, and proof continuation stay in the same task or use the delegation owners. Reclaiming the same nonce is idempotent and never re-exposes a consumed command. "At most one successor" means zero only when no eligible goal remains, a phase/authority/max-hop stop applies, `spawn_allowed` is false, task creation is unavailable, or the operator opts out.
4. **Pause authority, stop phases.** Use `await-authority` for spend, deployment, sends, destructive work, secrets, or authentication. Resume the same goal only after explicit authority; never infer a new product phase.
5. **Keep owners separate.** Product owners define completion; `TRACKING.json` derives progress, `CURRENT.md` owns tactical resume, and `ORCHESTRATION.json` owns mechanics. A stale map regenerates only `TRACKING.json` and `PLAN.md`; preserve checkpoints, chain history, admitted/claimed goals, nonces, blockers, and successor ids. History and file presence are hints, not proof.
6. **Freeze before final proof.** Persist repository-owned lifecycle routes and repair/create a local skill only for proven repeated multi-step friction. Before expensive rendered or independent acceptance, freeze the acceptance contract, semantic proof-owner evidence, product fingerprint, and fingerprint-keyed artifact root with `chain_state.py freeze-proof`. Batch all findings from one review wave before editing. A later source mutation requires targeted repair, a new freeze, and only affected proof reruns; final acceptance uses `record-proof --final-acceptance`.
7. **Bound discovery and evidence.** A justified explorer may inspect at most three sessions. Keep inline proof within the receipt budget using paths, stable ids or hashes, and concise results—never raw logs, base64, or image batches.
8. **Avoid false blockers.** Status questions, authentication handoffs, repair prompts, and a bounded proof-campaign pause are not terminal blocker repeats. Persist an exact proof blocker and resume the same goal without a hop or successor. Skip broad `session-introspection` when a repository owner already provides the exact issue and next command.

## Cross-references

- [references/workflow.md](references/workflow.md) — source precedence, operator DNA, program mapping, goal selection, negative scenarios, handoff, and closeout
- [references/program-schema.md](references/program-schema.md) — canonical `.session` files, program JSON input, sync, status, and goal-update commands
- [scripts/session_workspace.py](scripts/session_workspace.py) — workspace bootstrap, legacy migration, source fingerprints, generated plan, and evidence tracking
- [scripts/project_inventory.py](scripts/project_inventory.py) — cheap owner/plan/status inventory by default; bounded history, commit, and skill hints only in explicit `explore` mode
- [scripts/entry.py](scripts/entry.py) — checkpoint, chain, and project-inventory entry resolver
- [scripts/chain_state.py](scripts/chain_state.py) — nonce-protected chain transaction state
- [scripts/validate_goal.py](scripts/validate_goal.py) — session-goal shape and size gate
- [scripts/checkpoint.py](scripts/checkpoint.py) — exact-goal `save-session` wrapper
- sibling skills: `save-session`, `resume-session`, `session-introspection`
