# Canonical `.session` workspace

`$session-orchestrate` standardizes cross-session state under the current project root:

| File | Owner | Purpose |
|---|---|---|
| `.session/TRACKING.json` | `session_workspace.py` | Canonical derived program state, source fingerprints, ordered goals, statuses, evidence, and selected goal. |
| `.session/PLAN.md` | generated projection | Human-readable view of `TRACKING.json`; never edit directly. |
| `.session/CURRENT.md` | `save-session` | Exact tactical checkpoint and resumability metadata. |
| `.session/ORCHESTRATION.json` | `chain_state.py` | Chain id, hop bounds, nonce, successor, metrics, and stop state. |
| `.session/WORKSPACE.lock` | `session_workspace.py` | Atomic program-state writes. |
| `.session/ORCHESTRATION.lock` | `chain_state.py` | Atomic chain transitions. |

The folder is private local agent state and is added to `.git/info/exclude`. Product plans, architecture documents, and durable customer-facing project decisions remain in their repository-declared owners.

## Bootstrap and migration

Run before any other orchestration command:

```bash
python3 scripts/session_workspace.py ensure --root "$(git rev-parse --show-toplevel)"
```

When `.session/` does not exist, `ensure` creates it with mode `0700`. Existing legacy `.claude/session-data/CURRENT.md` and `ORCHESTRATION.json` are copied byte-for-byte only when the canonical targets are absent. Legacy files are retained but never consulted after `.session/` exists.

## Program input

After reading current product-plan owners and implementation evidence, write a temporary JSON file:

```json
{
  "completion_gate": "An operator completes the product loop with traceable evidence.",
  "phase_boundary": "Phase 5",
  "plan_sources": ["docs/PRODUCTPLAN.md"],
  "selected_goal_id": "actions-proof",
  "goals": [
    {
      "id": "actions-proof",
      "title": "Prove the Actions workflow",
      "status": "in_progress",
      "plan_ref": "PRODUCTPLAN Phase 5 exit gate",
      "prerequisites": [],
      "actions": ["Exercise the target interaction on desktop and mobile."],
      "verification": ["Trace every displayed value to retained evidence."],
      "evidence": [],
      "authority_gates": ["Stop before deployment without operator authority."]
    }
  ]
}
```

Goal ids are unique kebab-case. Actions and verification cannot be empty. A completed goal requires at least one evidence reference. Every prerequisite must name another goal in the same map. While work remains, `selected_goal_id` is required and cannot point to a completed goal.

Synchronize and render atomically:

```bash
python3 scripts/session_workspace.py sync \
  --root "$(git rev-parse --show-toplevel)" \
  --program-file /tmp/session-program.json
```

`sync` fingerprints every declared plan source. `status` returns `program_action: rebuild-plan` when a source changes, disappears, the generated projection is edited, or the next goal needs selection:

```bash
python3 scripts/session_workspace.py status --root "$(git rev-parse --show-toplevel)"
```

## Goal tracking

Mark the selected goal active:

```bash
python3 scripts/session_workspace.py mark \
  --root "$(git rev-parse --show-toplevel)" \
  --goal-id actions-proof \
  --status in_progress
```

Record completion only with evidence:

```bash
python3 scripts/session_workspace.py mark \
  --root "$(git rev-parse --show-toplevel)" \
  --goal-id actions-proof \
  --status completed \
  --evidence "tests/phase5-proof.json"
```

Completion clears the selected goal and returns `rebuild-plan` so the orchestrator rechecks current owners, records the next selection, or proves the product/phase gate complete.
