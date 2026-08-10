# Install Workflow

Use this skill when a repo needs a local context graph that can:
- ingest ordered session traces
- extract candidate decisions
- validate before trust
- expose active durable decisions at session start

## Generated surface

The installer writes:

```text
tools/project-context/
  pyproject.toml
  README.md
  src/project_context/
  tests/
script/project_context.sh
docs/workflows/context-graph.md
```

If the target repo already has these files, the installer leaves them unchanged unless they still contain the generated marker block.

## Repo patch behavior

When these files exist, the installer appends or inserts bounded updates:

- `AGENTS.md`
  - add a trigger for the context graph workflow
  - add a repo rule pointing validation updates through the new workflow
  - use the target repo's absolute `docs/` path in generated `workflow --docs-dir ...` commands
- `docs/README.md`
  - add `context-graph` to the docs inventory
- `docs/references/project-context.md`
  - record the installed local CLI and wrapper
- `docs/workflows/validation.md`
  - add commands for project-context validation

## Generated command contract

Use the repo wrapper for all normal operations:

```bash
./script/project_context.sh init
./script/project_context.sh doctor
./script/project_context.sh import-session /path/to/session.json
./script/project_context.sh import-rollout-summary /path/to/summary.md
./script/project_context.sh pending-mining
./script/project_context.sh source-inventory
./script/project_context.sh resolve-source <source-ref> --resolution <resolution> --reason "<evidence>"
./script/project_context.sh resolve-sources resolutions.json
./script/project_context.sh session-start
./script/project_context.sh review-queue --run-id <id>
./script/project_context.sh review-run --run-id <id> --approve <candidate-id> [--reject <candidate-id> ...]
./script/project_context.sh active
./script/project_context.sh history --decision-key some.key
./script/project_context.sh trace --decision-key some.key
./script/project_context.sh related --decision-key some.key
./script/project_context.sh render-html
```

The wrapper prefers:
1. `uv run --project tools/project-context project-context`
2. fallback `PYTHONPATH=tools/project-context/src python3 -m project_context.cli`

## Validation contract

From the target repo:

```bash
./script/project_context.sh init
./script/project_context.sh doctor
./script/project_context.sh pending-mining
./script/project_context.sh source-inventory
./script/project_context.sh render-html
rg -q "nodeSearchText|MAX_RENDERED_NODES|replaceChildren" .context-graph/artifacts/context-graph.html
rg -q 'Active decision graph|Task query preview|Decision trace|Inputs considered|detail-reveal' .context-graph/artifacts/context-graph.html
if rg -q "candidate_reviews" .context-graph/artifacts/context-graph.html; then exit 1; fi
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tools/project-context/tests -q
```

`render-html` writes `.context-graph/artifacts/context-graph.html`. Graph-mutating commands refresh that artifact automatically.
`pending-mining` must compare imported graph sessions with raw Codex/session source inventory. Treat `source_inventory_gap` as unresolved readiness until missing source sessions are imported, summarized, or persistently excluded. Use `resolve-sources` for multiple evidence-backed exclusions so inventory is scanned once and resolution writes are atomic.
The generated viewer should stay compact and operator-facing: no unused review payloads, precomputed search text, capped node rendering, DOM-safe text rendering, and decision traces behind node selection instead of default prompt injection.

## Generated decision markup

The deterministic v1 extractor promotes only explicit decision events:

```text
[decision key=workflow.validation.subagent-output type=rule scope=project] Subagent-updated context stays untrusted until validation.
```

This is intentional. The installer provides the trustworthy base shape first; model-driven extraction can be added later without changing the trust boundary.

During review, the pinned miner should classify each candidate as one of:
- `already_owned_no_change`
- `owner_surface_edit_needed`
- `graph_precedent_keep`
- `reject_not_durable`

Only `graph_precedent_keep` candidates should remain eligible for graph promotion after owner-surface review.
