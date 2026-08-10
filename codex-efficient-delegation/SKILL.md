---
name: codex-efficient-delegation
description: Measure and tune bounded Codex subagent workflows for quality, speed, context efficiency, and token or cost efficiency. Use when deciding whether independent repo scans, evidence audits, browser proof, role-based customer or UI reviews, test analysis, or other separable work should run in parallel; when replacing microtask agents with complete outcome missions; when comparing direct main-thread work with explorer or verifier sidecars; or when turning delegation observations into a repeatable experiment without surrendering main-thread judgment.
---

# Codex Efficient Delegation

Run delegation as a falsifiable optimization. Keep requirements, decisions, edits,
and final verification on the main thread; use sidecars only for independent bounded
work whose isolation or parallelism can repay its overhead.

## Ownership boundary

1. Load `workflow summary codex-routing-policy` to choose `scan|deep|build|verify`.
2. Load `workflow summary subagent-playbook` for agent-type and prompt rules.
3. Use this skill only to design, execute, measure, and tune the delegation experiment.
4. Use `optimization-ledger` when promoting a pattern through a multi-session trial.

Do not duplicate routing policy here. Model choice is surface-aware: prefer
`gpt-5.6-terra` for light, read-heavy workers only when the spawn surface exposes an
agent/model selector. Otherwise record `model=null`, `agent_type=null`, and
`unpinned=true`; call the worker parallel or context-isolating, never cheap.

## Gate

Work directly when the task is one or two deterministic steps, is the immediate
blocking decision, or needs tightly coupled judgment. Delegate only when all are true:

- the subtask is independent and has a concrete proof target;
- exact owner files, URLs, or commands can bound retrieval;
- every delegated command is repo-declared or preflighted non-mutatively on the main
  thread; do not invent package/import entrypoints;
- the main thread has useful non-overlapping work while it runs;
- the output can be a compact evidence packet rather than raw logs;
- current state can be rechecked before acting on the result.

Prefer one or two read-only sidecars. Use `explorer` for repo/doc evidence only when
that agent type is actually selectable, `browser_verifier` only for live visual proof,
and a sharper specialist when its tool or policy isolation is material. When the
surface has no selector, leave the worker unpinned and report that fact.

Keep `agents.max_depth=1` for experiments. Recursive fan-out requires an explicit task
need and a separate measurement because it raises token, latency, and predictability
risk. Keep writes on the main thread unless every write worker has a proven disjoint
file owner and a deterministic merge/verification step before spawning.

Use two sidecars only for a fragile shared control primitive or another high-cost miss,
and split them by risk question. For example: one traces the failure mechanism and the
other attacks the proposed safety contract. Two generic audits of the same files are
duplication, not a token-efficiency win.

## Complete-outcome review variant

Use this variant when isolation provides independent customer, operator, UI/UX, or
accessibility judgment rather than a narrow file-based proof:

1. Keep environment readiness, authentication, fixtures, source freezing, cleanup,
   diagnosis, edits, and acceptance accounting on the main thread. Start the measured
   mission only after the actor reaches the proved signed-in landing surface.
2. Give each selected profile one coherent outcome. Never spawn by page, control,
   checklist row, repaired step, or expected finding. Add at most one specialist when
   the changed surface specifically requires expertise such as authentication,
   payments, voice, mobile, destructive operations, or accessibility conformance.
3. Use `fork_turns="none"` and disclose only the role, starting surface, natural goal,
   wall-time budget, permitted actions, and compact report schema. Do not disclose
   fixes, internals, source history, tool names, fixture identifiers, known defects,
   locators, or another reviewer's report.
4. Group missions by shared setup or authenticated audience. Prepare that audience
   once, then run its actors sequentially unless browser storage and backend state are
   independently isolated. Separate visible windows are observability, not proof that
   concurrent mutations are safe and not an inefficiency by themselves.
5. During the actor's budget, do not send status pings or checklist follow-ups. At the
   deadline, send one freeze-and-close instruction. Require one verdict—`Pass`,
   `App Fail`, `Tooling Blocked`, or `Not Tested`—before diagnostics.
6. Freeze customer pass 1 and the affected UI/UX or specialist smoke on the same source
   before spending stability pass 2. If either finds a release issue, consolidate one
   owner fix pass, refreeze, and repeat only the affected complete outcomes.
7. After every mutating mission, including failed or tooling-blocked work, retain its
   evidence, remove only the snapshotted data delta, prove the next starting state, and
   close the owned lease. Allow one bounded tooling recovery; a repeated identical
   failure ends the campaign with the exact blocker.

Measure completed outcomes, unique verified findings, setup repetitions, audience
switches, invalidated reruns, tooling blocks, cleanup failures, wall time, and main
context growth. Do not use agent count, click count, or hidden/headless execution as a
proxy for efficiency. More actors are justified only when their independent profile or
risk question changes a decision.

## Experiment

Read [references/experiment-contract.md](references/experiment-contract.md) before
claiming an efficiency gain.

1. Freeze one task packet: goal, exact owner paths, constraints, deliverable, and
   success criteria, plus a wall-time budget. Resolve every owner path or URL against
   current state before spawning; repair a stale manifest first. Do not give the
   treatment agent the expected answer.
2. Record the direct baseline from the same frozen state, or mark it missing. Never
   substitute impressions for telemetry.
3. Spawn the smallest useful treatment, normally one unpinned read-only worker.
   Use `fork_turns="none"` or the fewest recent turns that preserve the contract.
4. Continue useful main-thread work. Do not wait immediately after spawning.
5. Collect compact results: files and commands inspected, findings, duplicates,
   unknowns, exact evidence references, and a final file hash or state stamp when the
   main thread is editing concurrently.
6. Re-read every material cited fact from current state. Treat a raced or stale claim
   as a tuning failure even when it was true when sampled.
7. Record available quality, latency, context, and token metrics. Preserve unavailable
   fields as `null`; do not call them savings. Delegated token telemetry must aggregate
   the parent plus every child. `main_context_chars` is attributable main-thread
   transcript growth, including returned sidecar summaries but excluding child-only
   logs.
8. Run the summarizer and follow its `keep_candidate|tune|reject|insufficient` verdict.

```bash
python3 "$HOME/.codex/skills/codex-efficient-delegation/scripts/summarize_experiment.py" \
  /tmp/direct.json /tmp/delegated.json --json
```

`keep_candidate` is only an immediate experiment result. Require a live-session trial
before changing standing agent or model defaults.

## Treatment prompt

```text
Read-only bounded verification. Prove or disprove <claim> using only <owner paths>.
Do not edit, browse beyond scope, or reread broad project history. Return <=500 words:
files/commands inspected, 3-7 findings, duplicates, unknowns, exact evidence refs,
and the smallest next action. Recheck current state immediately before returning.
```

For a complete-outcome review, use this shape instead:

```text
You are a fresh <profile> using the already-ready <surface>. Complete <natural goal>
within <budget> using only the visible product and its semantic UI. Do not inspect
source, logs, APIs, hidden state, fixes, or prior reports. Return one verdict, the first
friction, <=5 prioritized findings, <=3 personally inspected evidence captures, final
state, and owned-session closeout. Do not ask for progress guidance.
```

## Tuning rules

- Broad retrieval or full transcript forks -> shrink to exact owners and raw artifacts.
- Invalid delegated command -> treat it as a planning defect, replace it with the
  repo-owned entrypoint or a proven discovery form, and count the failed attempt.
- Worker exceeds its budget or returns no packet -> interrupt it, record
  `timed_out=true` and `quality_pass=false`, and do not recycle the whole task.
- Whole-goal audit bounded away from a proof owner -> do not accept `incomplete` as a
  finding. Supply an owner manifest or allow one bounded `rg --files`/registry discovery
  step, then freeze the resulting paths for the evidence pass.
- Duplicate main-thread work -> split by risk question, not by generic role.
- Stale result after concurrent progress -> require final state stamp or recheck.
- Reviewer repeats the contract -> skip it; rely on deterministic proof.
- Missing token/cost telemetry -> judge quality only and leave efficiency unresolved.
- A spawn surface without an explicit model selector -> call the treatment unpinned,
  not cheap. Do not infer model or price from an agent label.
- Disjoint optional telemetry -> exclude that task class for that metric. Never compare
  route-wide means built from different samples.
- Two independent audits find the same issue -> count confidence as useful quality,
  but count overlapping file retrieval as duplication unless their risk questions differ.
- Cheap agent returns `unknown` on a material claim -> escalate that claim once; do not
  rerun the entire scan.
- Parallel writes overlap -> stop; move the blocking edit back to the main thread.
- Checklist-sized review agents -> merge them into one profile-owned complete outcome.
- Repeated preflight, login, fixture creation, or audience switching -> move setup to
  the main thread and batch by the shared audience.
- Stability pass 2 starts before design or specialist smoke clears the source -> stop,
  run the missing smoke, and avoid knowingly invalidating two passes with one late fix.

## Closeout

Report what delegation uniquely added, what it duplicated, which metrics remain
unknown, and whether the pattern should be tuned, rejected, or entered into a
multi-session optimization trial. Never present one successful sidecar as a universal
cost improvement.
