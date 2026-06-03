---
name: session-introspection
description: Close meaningful sessions by capturing only preventable friction, choosing the narrowest durable control that would stop recurrence, routing it to one owner, and applying obvious safe controls immediately.
metadata:
  short-description: Anti-recurrence control audit
---

# Session Introspection

This skill is not a session recap. It exists to convert preventable friction into the narrowest durable control that would stop the same failure from happening again.

If a session ended successfully but exposed avoidable wasted time, retries, misleading verification, wrong sequencing, or missing guardrails, this skill identifies the prevention control and its owner. If there is no durable anti-recurrence learning, say so briefly and stop.

## Use When

- before the final response after meaningful work that exposed avoidable friction
- after a blocker, retry loop, misleading check, stale test, missing prerequisite, or recovery path revealed something likely to recur
- after PR-to-green work, CI triage, deploy work, migration work, or benchmark work when the session exposed a reusable prevention move
- after a doctrine or routing miss where a script, lint, hook, workflow doc, or AGENTS trigger would have prevented wasted work

Skip it for trivial chat, simple lookups, friction-free sessions, one-time external outages, or sessions where nothing durable should change.

## Trigger Conditions

Use the full workflow only when all of these are true:

1. The task is complete or the session is ending.
2. The session encountered material friction or a process/doctrine miss.
3. The friction was at least partly preventable.
4. The same friction could plausibly recur.
5. A concrete prevention control and owner can be named.

If any of those are false, output `no preventable friction worth promoting` and stop.

## Inputs

- intended outcome and actual outcome
- concrete friction and evidence it occurred
- how the friction was resolved this time
- what would have prevented it
- applicable local owner docs from the repo `AGENTS.md`
- applicable global owner docs from `~/.codex/AGENTS.md`
- next recommended move, if one remains

## Allowed Control Types

For each friction item, choose exactly one of:

- `script`
- `lint`
- `hook`
- `workflow-doc`
- `AGENTS-trigger`
- `none`

Use `none` only when the friction is real but no durable prevention control is justified.

## Prevention Decision

Prefer the narrowest effective control:

1. If the failure is deterministic and checkable, prefer `script` or `lint`.
2. If the failure should be blocked before execution, prefer a narrow `hook`.
3. If the problem was wrong sequence, missing prerequisite, or missing degraded path, prefer `workflow-doc`.
4. If the problem was fresh-agent routing or forgetting an already-known repo control, prefer `AGENTS-trigger`.
5. Do not use docs to compensate for a deterministic check that should be mechanical.
6. Do not use hooks when a cheap script or lint would be enough.

## Workflow

1. State intended outcome vs actual outcome in 1-2 lines.
2. List only the concrete friction items that were preventable.
3. For each item, record:
   - evidence
   - friction category
   - root cause
   - chosen control type
   - exact owner surface
   - whether it should be applied now
4. Justify why that control is stronger than the alternatives.
5. Audit applicable doctrine lanes only if they materially affected the session.
6. Apply obvious safe controls immediately when possible.
7. End with the highest-value remaining prevention move, if any.

## Friction Categories

1. unclear next step
2. missing prerequisite or setup expectation
3. misleading verification step
4. discovery timing too late
5. repeated retry or workaround
6. missing degraded path or recovery path
7. owner-surface ambiguity
8. deterministic misuse that should be blocked mechanically
9. stale doctrine or over-broad instruction

## Output Shape

- session outcome:
  - intended vs actual outcome
- preventable friction:
  - friction
  - evidence
  - category
  - root cause
  - best control: `script|lint|hook|workflow-doc|AGENTS-trigger|none`
  - owner
  - apply now: `yes|no`
  - why this control
- doctrine audit:
  - only the lanes that were actually required
  - `followed` or `missed`
  - exact fix only if a miss should become durable doctrine
- highest-value next control:
  - one item, or `none`

## Guardrails

- Do not summarize what was implemented unless the implementation itself is the anti-recurrence control.
- Do not produce a changelog, victory lap, or broad keep/remove/fix/improve recap.
- Do not include items that only describe what happened; every item must reduce future friction.
- Do not recommend a workflow doc when a deterministic script or lint would prevent the issue more directly.
- Do not recommend a hook unless pre-execution blocking is materially safer than post-hoc checking.
- Do not widen repo-local friction into a global baseline without cross-repo evidence.
- Do not output more than a few strong items; prefer one strong control over many weak notes.
- If no durable prevention exists, say so briefly and stop.

## Expected Result

- sessions close with an anti-recurrence control audit rather than a recap
- only preventable friction is recorded
- every durable item maps to one control type and one owner
- scripts/lints/hooks are preferred over prose when the failure is deterministic
- workflow docs and AGENTS triggers are used only for sequence, routing, and prerequisite gaps
- obvious safe controls are applied immediately when possible
