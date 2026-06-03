# GOAL.md

> Created: {{ISO_TIMESTAMP}}
> Source repo: `{{REPO_ROOT}}`
> Base branch: `{{BASE_BRANCH}}`
> Audit branch: `{{AUDIT_BRANCH}}`
> Base commit: `{{COMMIT}}`
> Audit worktree: `{{WORKTREE}}`

# Code Quality Audit Goal

Perform a read-only senior staff engineer audit of this repository. Produce and
maintain `PROGRESS.md` as the durable handoff artifact.

# AUDIT-ONLY MODE - DO NOT MODIFY CODE

Your only writable artifact during audit mode is `PROGRESS.md` in the repo
root. Do not edit, refactor, format, generate, or fix code. Treat the codebase
as immutable.

## Hard Constraints

- No edits to any file except `PROGRESS.md`.
- No new code files, even for reference.
- No inline patches in the checklist. Use line references and prose only.
- If you want to write code, stop and add it as a checklist item.
- If `PROGRESS.md` already exists, read it first.
- Preserve `## Completed` and `## Rejected`; do not re-add resolved items.
- If the full audit cannot fit in one turn, write what is ready and set
  `Status: partial`.
- Do not run commands that mutate repo state, except writing `PROGRESS.md`.

## Phase 1 - System Map

Do this silently. Do not write exploration notes to chat.

1. Walk the repo. Identify entry points, core modules, and external boundaries
   such as HTTP, DB, filesystem, subprocess, LLM/tool calls, queues, and
   schedulers.
2. For every file over 500 lines, build a structural map: top-level constructs,
   line ranges, and apparent responsibility.
3. Build the module-level dependency graph. Note cycles.
4. Identify module-level test coverage gaps by inspecting tests and test
   commands, not by running mutating commands.

## Phase 2 - Audit Lenses

Apply each lens, highest-risk modules first. Capture findings as you go.

1. Correctness - silent failures, swallowed exceptions, unenforced invariants,
   edge cases.
2. Failure modes - external dependency failures, retry, timeout, idempotency,
   blast radius.
3. Security - input validation, injection vectors, secret handling, trust
   boundaries.
4. Concurrency and state - races, shared mutable state, atomicity, ordering
   assumptions.
5. Agentic and LLM-specific - trusted LLM output, prompt injection surface,
   tool-call schema validation, malformed-output handling, load-bearing
   non-determinism.
6. Performance and complexity hotspots - N+1s, unbounded growth, hot-path
   allocations, sync-in-async, `O(n^2)`, `O(n*m)`, repeated scans, repeated
   lookups, render-heavy paths, and places where complexity can be reduced
   without changing behavior.
7. Maintainability - files over 1000 lines, functions over 100 lines,
   misleading names, mixed abstraction levels, dead code.
8. Testability - hardwired dependencies, untested boundaries, tests asserting
   implementation instead of behavior.
9. Observability - actionable errors, structured logs, traces at boundaries,
   log-level honesty.
10. Operational - config-as-code violations, health checks, deployability,
    secrets in repo.

## Subagent Policy

You may spawn read-only subagents for large or unfamiliar repos.

Subagents must:

- inspect only
- not edit files
- not create files
- not update `PROGRESS.md`
- return concise findings with path, line range, severity, evidence, proposed
  fix, verification, and affected files

The main thread must:

- wait for subagents before final synthesis
- dedupe overlapping findings
- resolve contradictions
- rank by impact times likelihood
- write only `PROGRESS.md` during audit mode

Suggested splits:

- architecture and test map
- correctness and failure modes
- security and agentic/LLM risk
- complexity hotspots and performance
- maintainability, observability, and operations

## Complexity Hotspot Contract

Complexity analysis is a lens inside this audit, not a separate report owner.
Do not create `COMPLEXITY.md` unless the human explicitly asks for a supporting
artifact. Do not paste raw scanner output into `PROGRESS.md`.

Normalize complexity findings into the existing checklist:

- `DEFECTS` - confirmed timeout, memory blowup, UI freeze, or production
  failure.
- `RISKS` - likely material issue on user-sized data, including `O(n^2)`,
  `O(n*m)`, N+1, repeated lookup, repeated scan, or render-heavy paths.
- `SMELLS` - low-risk local inefficiency.
- `CROSS-CUTTING` - repeated complexity pattern spanning multiple modules.

Every complexity item must include:

- data-size assumption
- before/after complexity estimate
- safe optimization approach in prose
- risk level
- tests needed to preserve behavior and prevent regression

## Phase 3 - Write PROGRESS.md

Use the exact schema already present in `PROGRESS.md`. Overwrite
`## Current Audit`. Preserve `## Completed` and `## Rejected`.

Checklist items must include:

- stable ID: `D1`, `R1`, `S1`, or `X1`
- path and line range
- one-sentence issue summary
- why it matters
- proposed fix in prose, not code
- verification method
- touched files/functions
- reversibility: `safe`, `requires-approval`, or `migration-needed`

For complexity items, also include data-size assumption, before/after
complexity estimate, risk level, and tests needed.

## Phase 4 - Handoff

End the audit turn with exactly two lines:

1. The ID and one-sentence summary of the top item the next turn should start
   with.
2. Nothing else.

The next agent reads `PROGRESS.md`, not chat output.

## Execute-Next Contract

Later executor turns should read `PROGRESS.md`, execute exactly the next
unchecked item, update `## Completed` or `## Rejected`, and stop. Items marked
`requires-approval` or `migration-needed` require human approval before code
edits.
