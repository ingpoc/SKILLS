# Report Schema

The readiness manifest is the contract between:

- the readiness skill
- validation subagents
- remediation agents

## Top-Level Fields

- `repo`
- `stacks`
- `repo_class`
- `web_facing`
- `overall`
- `can_agent_proceed_now`
- `strongest_verification_command`
- `strongest_runtime_proof_lane`
- `browser_proof_status`
- `execution_plan`
- `repo_relevant_integrations`
- `commands`
- `runtime_markers`
- `lanes`
- `next_actions`
- `artifacts` when an output directory is requested
- `served` when HTML serving is requested

## Lane Schema

Each lane object must contain:

- `lane_id`
- `title`
- `phase`
- `applicable`
- `required`
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
- `questions`
- `details`

## Status Semantics

- `ready`: the lane is applicable and sufficiently proven
- `degraded`: the lane exists but is not yet proven strongly enough
- `blocked`: the lane is required or important and the agent cannot trust it yet
- `not_applicable`: the lane does not apply to this repo

## Proof Ladder

- `detected`: the lane was found
- `configured`: the lane appears wired and usable in principle
- `executed`: a check ran
- `verified`: the check proved the intended thing

Never collapse these into one boolean.

## Execution Plan

`execution_plan.parallel` is for read-only discovery lanes.

`execution_plan.sequential` is for shared-state proof lanes.

Default rule:

- if a lane needs a started process, a real browser session, mutable caches, ports, DB state, or lockfiles, keep it sequential

## Artifact Contract

When `--output-dir` is provided, the script writes:

- `repo-readiness-report.md`
- `repo-readiness-report.json`
- `index.html`

When `--serve` is provided, the manifest also includes:

- `served.host`
- `served.port`
- `served.pid`
- `served.url`
- `served.staged_dir`
- `served.pid_file`
- `served.log`

The served directory should be a temporary staging area under `/tmp`, not the durable artifact directory itself.

## Remediation Use

A remediation agent should:

1. fix blocked required lanes first
2. rerun only affected validation commands
3. promote degraded lanes only after real proof
