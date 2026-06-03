---
name: sample-app-benchmark
description: Run a reusable fresh-app benchmark for a new idea, tool, or control-plane challenger by comparing a clean `main` baseline against a committed challenger branch in separate top-level Codex sessions with isolated benchmark environments.
---

# Sample App Benchmark

Use this skill when the question is whether a new system, workflow CLI, or instruction layer actually helps on real app work.

This skill standardizes the benchmark shape:
- one clean source repo
- `main` as the committed baseline
- one committed challenger branch
- one top-level Codex session per arm
- one isolated benchmark `CODEX_HOME` per arm using the `sample_app_eval` profile
- one normalized post-run verifier for both arms
- no benchmark residue in the source repo

## Use When

- benchmarking a new agent aid on a fresh sample app
- comparing docs-first guidance vs a challenger branch
- testing whether a workflow CLI improves discovery on real implementation work
- creating reusable benchmark evidence for multiple systems with the same method

Do not use this skill for:
- pure retrieval benchmarks without real app work
- ad hoc app implementation that is not meant to be compared as an eval
- runs where the source repo will be edited manually between arms
- benchmarks that are actually meant to test multi-agent Codex behavior

## Required Inputs

- sample app repo path
- benchmark task prompt and acceptance criteria
- baseline branch, normally `main`
- challenger branch, normally `codex/<challenger-name>`
- fixed model, reasoning effort, and timeout
- whether the run is single-prompt or same-session multi-turn
- benchmark Codex profile, default `sample_app_eval`

## Workflow

### 1. Prepare the benchmark repo

- Keep the source repo plausible as a normal governed app workspace.
- Put the clean benchmark baseline on `main`.
- Put the challenger setup on a separate committed branch.
- Do not benchmark from dirty source state.

Recommended source shape:
- `AGENTS.md`
- `README.md`
- `docs/workflow/`
- `benchmarks/tasks/`

If the challenger is workflow-CLI based, follow the sparse pattern proven in:
- `/Users/gurusharan/Documents/remote-claude/active/apps/workflow-cli-benchmark-idea-board`

That means:
- local wrapper in the app repo
- sparse repo-local catalog only
- no full copy of the Organization trigger map
- strict split:
  - incumbent `AGENTS.md` points directly to `docs/workflow/*.md`
  - challenger `AGENTS.md` is mostly CLI-first and points to `./scripts/workflow`
  - canonical docs remain in the repo, but challenger discovery should happen through workflow packets

### 2. Freeze the benchmark contract

- Define one task with:
  - the exact user prompt
  - acceptance criteria
  - time cap
  - verification requirement
  - non-goals
- Keep the same task contract for incumbent and challenger.
- Put the required visible flow directly in the prompt, not only in acceptance criteria.
- If the task expects `add`, `mark done`, and `persist across refresh`, state that exact flow in the prompt.

### 3. Prepare the benchmark environment

- Use the dedicated benchmark Codex profile `sample_app_eval`.
- Materialize it into an isolated benchmark `CODEX_HOME`.
- Prefer a runner-owned benchmark home instead of mutating your normal Codex home.
- Use `codex exec --profile sample_app_eval` as the primary runner entrypoint.
- Avoid scattering equivalent behavior across many one-off `--config` and `--sandbox` flags.

Parallel execution rule:
- run incumbent and challenger as separate top-level Codex sessions
- if you parallelize, parallelize the two arms, not the implementation work inside one arm
- keep each arm on its own committed branch tip and its own isolated `CODEX_HOME`
- do not let one arm observe or reuse the other arm's thread state

### 4. Run the arms

- Default measured topology: one single-agent Codex session per arm.
- Do not use subagents inside the scored app-building arms unless the benchmark goal is specifically to test multi-agent Codex.
- Use the same prompt, same profile, same timeout, same verifier, and same model posture for both arms.

Preferred execution order:
- if you want the cleanest evidence and fastest wall-clock time, use the parallel orchestrator
- if you are debugging the harness, run one arm first and inspect the artifacts before comparing

### 5. Capture the minimum evidence

Every arm should produce:
- preflight result
- profile name and effective config summary
- prompt or prompt schedule used
- transcript or structured run log
- final response
- git diff summary
- test output
- verification proof for the visible flow
- timing metadata
- token usage from the isolated `CODEX_HOME/sessions/...jsonl`
- context-discovery timeline showing what relevant context was loaded first and when

After the run:
- rerun the documented or discovered local test command
- independently launch the app through the documented run path
- verify the required visible flow in a real browser

This catches cases where the agent claims verification but the real browser path is still broken.

### 6. Compare the arms

Score these five things explicitly:
- `context_relevance_timing`
- `context_efficiency_tokens`
- `time_to_verified_result`
- `result_quality`
- `verification_quality`

Also record:
- same-session continuity when applicable
- whether challenger actually used `./scripts/workflow`
- context churn
- policy or source drift
- dominant miss owner

### 7. Close out cleanly

- keep the source repo clean on both committed branches
- store evidence in the Organization eval surfaces, not in ad hoc notes
- route one dominant learning to one owner only
- if the challenger loses, keep the challenger branch as evidence but do not promote it

## Guardrails

- No hidden evaluator hints.
- Do not rescue a run mid-flight.
- Do not benchmark from dirty source state.
- Do not hand-edit the source repo between arms to simulate cleanup.
- Do not call a run reproducible unless it can be rerun from committed branch tips.
- Do not claim same-session evidence unless the runner actually preserved one thread.
- Do not use subagents inside the measured arms unless the benchmark goal is specifically multi-agent Codex.
- Do not score usage-limit, auth-refresh, or transport failures as product evidence; classify them as `invalid_environment`.
- Do not treat stronger verification as a loss for the challenger when it exposes a real app bug; fix the app and rerun the benchmark.
- Do not claim context efficiency in tokens unless the runner parsed usage from saved session files, not just turn JSONL.
- Do not accept in-session browser interaction alone as final proof; use the independent verifier for both arms.

## Example Requests

- "Benchmark this new workflow CLI on a fresh sample app."
- "Compare main vs a challenger branch on the same app-building task."
- "Run the incumbent and challenger in parallel and compare them."
- "Set up a reusable sample-app benchmark for this new system."

## Local References

- Workflow contract basis:
  `/Users/gurusharan/Documents/Organization/docs/workflow/sample-app-benchmark.md`
- Same-session runner:
  `/Users/gurusharan/Documents/Organization/scripts/run_sample_app_benchmark_session.py`
- Parallel orchestrator:
  `/Users/gurusharan/Documents/Organization/scripts/run_parallel_sample_app_benchmark.py`
- Benchmark preflight:
  `/Users/gurusharan/Documents/Organization/scripts/sample_app_benchmark_preflight.py`
- Independent browser verifier:
  `/Users/gurusharan/Documents/Organization/scripts/verify_sample_app_benchmark_result.py`
- Comparison report generator:
  `/Users/gurusharan/Documents/Organization/scripts/compare_sample_app_benchmark_runs.py`
- CLI design guidance:
  `/Users/gurusharan/Documents/Organization/skills/cli-for-agents/SKILL.md`
- Proven branch-based benchmark repo:
  `/Users/gurusharan/Documents/remote-claude/active/apps/workflow-cli-benchmark-idea-board`
