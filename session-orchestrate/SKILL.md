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

Resolve the caller's current Git product root, then run `python3 ~/.codex/skills/session-orchestrate/scripts/entry.py --compact --root "$(git rev-parse --show-toplevel)"` once. When an authorized successor prompt supplies a nonce, add `--claim-nonce <nonce>`; this mechanically claims, canonicalizes, binds, and materializes the exact objective without shell extraction. Follow `route_receipt` until one of its listed invalidators changes. Run its `reference_command` once only when present, and its `goal_detail_argv` only when the selected goal's actions or routes are needed. A claimed handoff needs neither read—use its `goal_file`, call `create_goal` with that exact objective, settle with `set-goal`, then execute `first_command`.

The helper refuses the global skills repository, creates or validates only the current product's `.session/`, delegates checkpoint eligibility to `resume-session`, checks plan and chain consistency, and returns a cheap owner/status inventory. Use deterministic owner reads first, invoke a read-only explorer only when `exploration.action` still has clear ROI, and rebuild only when `workspace.program_action` says so.

If a claimed handoff's owner sources changed, `revalidate-claimed-handoff` keeps its exact goal and restricts review to the changed owner slice; do not reopen broad planning or history.

Use [scripts/chain_state.py](scripts/chain_state.py) for every state transition, [scripts/validate_goal.py](scripts/validate_goal.py) before `create_goal`, and [scripts/checkpoint.py](scripts/checkpoint.py) for exact-goal closeout.

## Hard rules

1. **One substantive goal.** Split independent deliverables, but keep one accepted milestone's implementation, actual-target verification, and repository-required promotion/handoff stages in one `project-lifecycle`. Reconcile already-proven work inline without consuming a hop.
2. **Reuse deterministic receipts.** Refresh only after a receipt invalidator changes. A selector must match the admitted goal; a dynamic queue retains only its exact unfinished target.
3. **Preserve exact transactions.** Keep one canonical objective until completion or handoff, honor hop/nonce bounds, and create at most one same-project successor. Reclaiming the same nonce is idempotent.
4. **Pause authority, stop phases.** Use `await-authority` for spend, deployment, sends, destructive work, secrets, or authentication. Resume the same goal only after explicit authority; never infer a new product phase.
5. **Keep owners separate.** Product owners define completion; `TRACKING.json` derives progress, `CURRENT.md` owns tactical resume, and `ORCHESTRATION.json` owns mechanics. History and file presence are hints, not proof.
6. **Keep recipes local.** Persist repository-owned lifecycle routes and repair/create a local skill only for proven repeated multi-step friction. Complete source changes before final proof; rerun affected evidence after any later mutation.
7. **Bound discovery and evidence.** A justified explorer may inspect at most three sessions. Keep inline proof within the receipt budget using paths, stable ids or hashes, and concise results—never raw logs, base64, or image batches.
8. **Avoid false blockers.** Status questions, authentication handoffs, and repair prompts are not blocker repeats. Skip broad `session-introspection` when a repository owner already provides the exact issue and next command.

## Cross-references

- [references/workflow.md](references/workflow.md) — source precedence, program mapping, goal selection, negative scenarios, handoff, and closeout
- [references/program-schema.md](references/program-schema.md) — canonical `.session` files, program JSON input, sync, status, and goal-update commands
- [scripts/session_workspace.py](scripts/session_workspace.py) — workspace bootstrap, legacy migration, source fingerprints, generated plan, and evidence tracking
- [scripts/project_inventory.py](scripts/project_inventory.py) — cheap owner/plan/status inventory by default; bounded history, commit, and skill hints only in explicit `explore` mode
- [scripts/entry.py](scripts/entry.py) — checkpoint, chain, and project-inventory entry resolver
- [scripts/chain_state.py](scripts/chain_state.py) — nonce-protected chain transaction state
- [scripts/validate_goal.py](scripts/validate_goal.py) — session-goal shape and size gate
- [scripts/checkpoint.py](scripts/checkpoint.py) — exact-goal `save-session` wrapper
- sibling skills: `save-session`, `resume-session`, `session-introspection`
