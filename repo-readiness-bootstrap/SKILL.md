---
name: repo-readiness-bootstrap
description: Bootstrap or assess a Codex-first day-one readiness baseline for an unfamiliar repo. Use when entering a repo for the first time, making a repo agent-runnable, or needing one canonical readiness report before implementation.
metadata:
  short-description: Codex-first repo readiness bootstrap
---

# Repo Readiness Bootstrap

Use this skill to answer the harder question, not the shallow one:

- not just "does a command exist?"
- but "can an agent operate like a day-one engineer here and prove its work?"

This skill is a project-agnostic orchestrator. It separates:

- parallel discovery
- sequential proof
- final reduction into a remediation-ready report

## Owns

- repo-readiness assessment for arbitrary repos
- repo classification and lane applicability detection
- canonical readiness manifest generation
- ordered remediation output for follow-on fix agents

## Does Not Own

- creating repo-local `AGENTS.md` from scratch
- governance-heavy workspace setup
- broad auth policy decisions
- applying the remediation itself

Use `init-project` when the repo is missing repo-local agent entry surfaces.
Use `project-governance-bootstrap` when the user wants organization-layer governance.

## Required Path

1. Run the readiness manifest script.
2. Prefer writing durable artifacts to a repo-local path under `artifacts/readiness/` instead of relying on stdout alone.
3. When a browser view is needed, serve a temporary copy from `/tmp` instead of serving the durable artifact directory directly.
4. Read required blocked lanes first.
5. Treat `detected` and `configured` as weaker than `executed` and `verified`.
6. Run read-only discovery lanes in parallel when subagents are available.
7. Keep shared-state proof lanes sequential by default.
8. Do not claim the repo is ready until required lanes are actually verified.

## Preferred Command

```bash
python3 "$HOME/.codex/skills/repo-readiness-bootstrap/scripts/report.py" \
  --repo /abs/path/to/repo \
  --output-dir /abs/path/to/repo/artifacts/readiness/current \
  --serve \
  --format markdown
```

Use `--format json` when another tool or agent should consume the manifest.
Use `--format html` only when you explicitly want the HTML on stdout.

## Execution Model

Sequential:

1. preflight classification
2. environment start
3. verification execution
4. runtime evidence
5. browser proof
6. final reduction

Parallel:

- repo contract
- integration discovery
- guardrails
- DX primitives
- browser applicability
- command discovery

Default rule:

- if a check mutates shared state, depends on a started process, or may contend for the same cache, DB, port, or lockfile, keep it sequential

## Canonical Lanes

- `repo_contract`
- `verification`
- `environment_start`
- `runtime_evidence`
- `browser_proof` when the repo is web-facing
- `integrations`
- `guardrails`
- `dx_primitives`

Each lane must answer fixed questions in structured form:

- `applicable`
- `status`
- `confidence`
- `detected`
- `configured`
- `executed`
- `verified`
- `evidence`
- `blocker`
- `next_action`
- `validation_command`
- `done_when`
- `owner_surface`

The crucial distinction is:

- `detected` means the lane was found
- `configured` means the lane appears wired
- `executed` means a real check ran
- `verified` means the check proved the intended thing

## Subagent Guidance

Use subagents only for bounded read-only discovery lanes. Do not hand shared-state proof work to parallel agents by default.

Good subagent asks:

- "Classify repo contract and owner docs"
- "Inventory repo-owned verification commands"
- "Detect whether a browser lane applies"
- "Infer repo-relevant external systems from local docs and config"
- "Detect deterministic guardrails and onboarding primitives"

Keep these sequential in the main rollout unless you have explicit isolation:

- environment bootstrap
- dev server start
- test or smoke execution
- runtime proof against a started environment
- browser proof against a started environment

## Reporting Contract

The final report must name:

- repo path
- detected stacks
- repo class
- overall readiness
- whether the agent can proceed now
- strongest verification command
- strongest runtime proof lane
- browser proof status when applicable
- ordered next actions
- explicit parallel vs sequential execution plan

When `--output-dir` is provided, the script must write:

- `repo-readiness-report.md`
- `repo-readiness-report.json`
- `index.html`

When `--serve` is provided, the script must stage a temporary served copy under `/tmp` and include the served URL in the JSON manifest.

The JSON manifest is intended to feed remediation agents directly.

## Skill Rules

- Prefer repo-owned commands over inferred defaults.
- Prefer runtime proof over tool presence.
- Prefer browser proof over config-level UI claims.
- Prefer repo-relevant integrations over global integration inventory.
- Do not mark required lanes ready unless they are actually verified.
- If a repo is mixed backend plus frontend, keep that classification visible instead of collapsing to non-web.

## References

- [Report Schema](references/report-schema.md)
- [Eval Criteria](references/eval-criteria.md)
- `workflow summary repo-readiness-bootstrap`
- `workflow context repo-orient`
- `workflow context env-bootstrap`
- `workflow context ui-verify`
- `workflow context runtime-debug`
