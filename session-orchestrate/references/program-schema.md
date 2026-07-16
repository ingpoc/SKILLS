# Canonical `.session` workspace

`$session-orchestrate` standardizes cross-session state under the current project root:

| File | Owner | Purpose |
|---|---|---|
| `.session/TRACKING.json` | `session_workspace.py` | Canonical derived program state, source fingerprints, ordered goals, statuses, evidence, and selected goal. |
| `.session/PLAN.md` | generated projection | Human-readable view of `TRACKING.json`; never edit directly. |
| `.session/CURRENT.md` | `save-session` | Exact tactical checkpoint and resumability metadata. |
| `.session/CLAIMED_GOAL.md` | `chain_state.py` / `entry.py` | Private canonical objective materialized for an authorized claimed handoff or authority resume. |
| `.session/ORCHESTRATION.json` | `chain_state.py` | Chain id, exact canonical objective and hash, hop bounds, nonce, authority pause, successor, metrics, and stop state. |
| `.session/WORKSPACE.lock` | `session_workspace.py` | Atomic program-state writes. |
| `.session/ORCHESTRATION.lock` | `chain_state.py` | Atomic chain transitions. |

The folder is private local agent state and is added to `.git/info/exclude`. Product plans, architecture documents, and durable customer-facing project decisions remain in their repository-declared owners.

## Bootstrap and migration

Run before any other orchestration command:

```bash
python3 "$SESSION_ORCHESTRATE_SKILL/scripts/session_workspace.py" ensure --root "$SESSION_ORCHESTRATE_ROOT"
```

When `.session/` does not exist, `ensure` creates it with mode `0700`. Existing legacy `.claude/session-data/CURRENT.md` and `ORCHESTRATION.json` are copied byte-for-byte only when the canonical targets are absent. Legacy files are retained but never consulted after `.session/` exists.

## Program input

After reading current product-plan owners and implementation evidence, write a temporary JSON file:

```json
{
  "completion_gate": "An operator completes the product loop with traceable evidence.",
  "phase_boundary": "Phase 5",
  "plan_sources": ["docs/PRODUCTPLAN.md"],
  "selected_goal_id": "phase5-milestone",
  "goals": [
    {
      "id": "phase5-milestone",
      "title": "Complete the Phase 5 accepted milestone",
      "status": "in_progress",
      "delivery_unit": "project-lifecycle",
      "plan_ref": "PRODUCTPLAN Phase 5 exit gate",
      "prerequisites": [],
      "lifecycle_stages": [
        {
          "id": "implementation",
          "kind": "implementation",
          "title": "Accepted implementation",
          "action": "complete the plan-owned scope and integration seam",
          "route": "repository-declared implementation owner",
          "acceptance": "the intended product behavior exists"
        },
        {
          "id": "target-proof",
          "kind": "verification",
          "title": "Actual-target proof",
          "action": "exercise the real repository-defined acceptance surface",
          "route": "repository-local test, runtime, or visual-proof route",
          "acceptance": "the owner-plan exit gate accepts the result"
        }
      ],
      "verification": ["Prove every declared lifecycle stage or preserve its exact authority gate."],
      "evidence": [],
      "authority_gates": ["Repository-declared runtime, promotion, authentication, spend, and external-action gates retain their normal authority."]
    }
  ]
}
```

Goal ids are unique kebab-case. `delivery_unit` defaults to `bounded-deliverable`; use `project-lifecycle` when several repository-defined stages serve one accepted milestone or exit gate. A project lifecycle contains two to eight ordered `lifecycle_stages`. Each stage has a unique id, a kind (`implementation`, `verification`, `promotion`, `handoff`, or `hardening`), one action, its exact repository route, stage acceptance, and an optional authority gate. It must contain implementation plus later verification. Promotion, handoff, and hardening are included only when the current repository requires them; the global skill never invents those stages. For a project lifecycle, omit top-level `actions` because the structured stages own them. A bounded deliverable instead uses non-empty `actions`. A completed goal requires evidence. Every prerequisite must name an earlier goal in the same map. While work remains, `selected_goal_id` is required and cannot point to a completed goal.

When the repository declares a deterministic work selector, add:

```json
{
  "selection_probe": {
    "scope": "dynamic-queue",
    "route": "repository-declared read-only next-work command",
    "target": "exact normalized target returned by that command",
    "source_refs": ["path/to/queue-owner.json"]
  }
}
```

The selected goal then requires an `admission_target` exactly equal to `selection_probe.target`. Every `source_refs` path must also be in `plan_sources` so owner changes stale the map. For `dynamic-queue`, retain completed evidence if useful but include only the admitted unfinished goal; refresh the selector after completion. `static-plan` may retain later ordered goals. Entry exposes the probe on every reuse so the agent can rerun that one read-only route before activating the goal.

Synchronize and render atomically:

```bash
python3 "$SESSION_ORCHESTRATE_SKILL/scripts/session_workspace.py" sync \
  --root "$SESSION_ORCHESTRATE_ROOT" \
  --program-file /tmp/session-program.json
```

`sync` fingerprints every declared plan source and records the current program-policy version. `status` returns `program_action: rebuild-plan` when a source changes, disappears, the generated projection is edited, the policy version changes, or the next goal needs selection:

```bash
python3 "$SESSION_ORCHESTRATE_SKILL/scripts/session_workspace.py" status --root "$SESSION_ORCHESTRATE_ROOT"
```

Read only the selected goal contract when the compact entry receipt requires its actions or lifecycle routes:

```bash
python3 "$SESSION_ORCHESTRATE_SKILL/scripts/session_workspace.py" goal --root "$SESSION_ORCHESTRATE_ROOT"
```

## Goal tracking

Mark the selected goal active:

```bash
python3 "$SESSION_ORCHESTRATE_SKILL/scripts/session_workspace.py" mark \
  --root "$SESSION_ORCHESTRATE_ROOT" \
  --goal-id phase5-milestone \
  --status in_progress
```

Record completion only with evidence:

```bash
python3 "$SESSION_ORCHESTRATE_SKILL/scripts/session_workspace.py" mark \
  --root "$SESSION_ORCHESTRATE_ROOT" \
  --goal-id phase5-milestone \
  --status completed \
  --evidence "tests/phase5-proof.json"
```

Completion clears the selected goal and returns `rebuild-plan` so the orchestrator rechecks current owners, records the next selection, or proves the product/phase gate complete.
