# Context Graph

Workflow for the repo-local durable decision graph.

## Control Owner

Owner for:
- source inventory, mining, review, promotion, retrieval, and structural health
- `pending-mining` and `source_inventory_gap` recovery

Should not contain:
- global Codex routing doctrine owned by `~/.codex/AGENTS.md`
- reusable `save-session` or `resume-session` skill behavior
- beta tracking policy owned by the global beta registry
- generated viewer, export, or reporting artifacts

## Minimum System

Keep:
- `./script/project_context.sh` as the only repo entrypoint
- `tools/project-context/` as the CLI implementation
- `.context-graph/graph.db` as the only canonical database
- `.context-graph/schema.sql` as the schema reference
- `.context-graph/state/checkpoints.json` only for mining checkpoints
- `.context-graph/state/latest_validated_run.json` only for validation handoff
- this workflow doc as the only context-graph operating route
- `tools/project-context/tests/` as regression proof

Do not add required HTML viewers, exports, project-specific miner agents, local beta wrappers, or duplicate DB files.

## Decision

| Situation | Action |
|---|---|
| Agent is already in a repo lane and needs precedent | Run `./script/project_context.sh query --task "<current task>"` |
| Agent intentionally audits graph readiness | Run `./script/project_context.sh pending-mining` and `./script/project_context.sh source-inventory` |
| `source_inventory_gap` exists | Import, summarize, or persistently resolve each `unimported_source_sessions` item |
| Imported sessions are unmined | Run `./script/project_context.sh mine` |
| A run is mined | Run `./script/project_context.sh validate --run-id <id>` |
| A run needs review | Run `review-queue`, then `review-run` with explicit approve/reject ids |
| A run is reviewed | Run `promote --run-id <id>` |
| Agent needs complete active corpus for audit | Run `./script/project_context.sh active` |
| Agent needs precedence or override history | Run `history --decision-key <key>` |
| Agent needs the why behind a decision | Run `trace --decision-key <key>` |
| Agent needs explicit links around a decision | Run `related --decision-key <key>` |

SessionStart, if enabled, may run `pending-mining` only. It must not mine, validate, review, promote, render artifacts, or run beta logic.

## Trust Rules

- `pending-mining: false` is not sufficient by itself; source inventory must also show no unresolved source gaps.
- Promoted state is useful only when every raw source session is imported or durably resolved.
- Deterministic mining stages candidates only; promotion requires explicit review.
- Do not promote duplicate control-surface doctrine that already belongs in global `AGENTS.md`, local `AGENTS.md`, workflow docs, reference docs, reusable skills, or hooks.
- If a mined rule has a better owner, move it there and stop treating the graph entry as active control context.

## Validation

Use:

```sh
./script/project_context.sh doctor
./script/project_context.sh pending-mining
./script/project_context.sh source-inventory
./script/project_context.sh categories
./script/project_context.sh query --task "current task"
./script/project_context.sh trace --decision-key <key>
./script/project_context.sh related --decision-key <key>
./script/project_context.sh audit-active
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tools/project-context/tests -q
```

## Output Contract

Report:
- source inventory gap count
- unmined or unresolved source refs
- mining run id, when created
- validation outcome
- reviewed approval/rejection outcome
- promoted count
- task query and relevant active decisions returned
