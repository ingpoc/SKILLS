# Delegation experiment contract

Use the same frozen task and success criteria for baseline and treatment. Official
Codex guidance says subagents are useful for independent read-heavy work and context
isolation, but consume more tokens than comparable single-agent work. Measure before
claiming a cost benefit.

Source: <https://learn.chatgpt.com/docs/agent-configuration/subagents.md>

## Unit of comparison

One JSON object represents one route over one frozen `task_class`:

```json
{
  "run_id": "portfolio-provenance-direct-1",
  "task_class": "portfolio-provenance-audit",
  "route": "baseline",
  "quality_pass": true,
  "timed_out": false,
  "actionable_findings": 1,
  "false_positives": 0,
  "stale_claims": 0,
  "files_read": 6,
  "duplicate_files": 0,
  "commands": 4,
  "wall_ms": 12000,
  "input_tokens": null,
  "cached_input_tokens": null,
  "output_tokens": null,
  "main_context_chars": 9000,
  "model": null,
  "agent_type": null,
  "unpinned": true,
  "notes": "token telemetry unavailable"
}
```

Required fields: `run_id`, `task_class`, `route`, `quality_pass`, `timed_out`,
`actionable_findings`, `false_positives`, `stale_claims`, `files_read`,
`duplicate_files`, and `commands`. `route` is `baseline` or `delegated`.

Optional numeric telemetry may be `null`: `wall_ms`, `input_tokens`,
`cached_input_tokens`, `output_tokens`, and `main_context_chars`.

For a delegated route, token fields are totals across the parent and every child, not
the selected worker alone. `main_context_chars` is attributable main-thread transcript
growth: direct command/log output for the baseline, or returned sidecar summaries plus
main-thread orchestration output for the treatment. Child-only logs are excluded.
`input_tokens` is total input and already includes its cached subset;
`cached_input_tokens` is diagnostic and must not be added again. Total tokens are
`input_tokens + output_tokens`; cost remains unproven without matched pricing telemetry.
Optional identity fields are `model`, `agent_type`, and `unpinned`. If the spawn surface
does not expose a selector, set the first two to `null` and `unpinned` to `true`; do not
infer them from a task label.

## Quality gate

- Reject a treatment with a lower quality-pass rate than its paired baseline.
- Reject a treatment that times out or returns no bounded evidence packet.
- Reject any treatment with a material false positive that the main thread acted on.
- Tune any treatment with stale claims, avoidable duplicate retrieval, or no paired
  baseline.
- Count a finding only when the main thread independently verifies it and it changes a
  decision, catches a defect, or closes a named proof gap.

## Efficiency gate

The summarizer compares route means only across task classes with matched route counts
and non-null values for that metric. Disjoint optional samples are reported as excluded,
not averaged together.

- `keep_candidate`: quality has no regression, false positives and stale claims are
  zero, and at least one of wall time, aggregate route tokens, or main-context
  characters is at or below the configured ratio of baseline.
- `tune`: quality is useful but duplication, staleness, or absent comparable
  efficiency telemetry prevents promotion.
- `reject`: quality regresses or false positives make the route unsafe.
- `insufficient`: no paired baseline/treatment task class exists.

The default ratio is `0.80`; override it only before the experiment.

## Multi-session promotion

Use `optimization-ledger` for standing changes. A reasonable proposed trial is ten
unique sessions with:

- quality pass in at least nine;
- zero acted-on false positives or destructive overlaps;
- no stale claim accepted without current-state recheck;
- median comparable cost or main-context load no more than 80% of baseline;
- median wall time no more than baseline when parallelism is the stated benefit.

These are proposed criteria, not a recorded ledger trial, until the operator accepts
them.
