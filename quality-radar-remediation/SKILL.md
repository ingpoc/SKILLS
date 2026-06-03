---
name: quality-radar-remediation
description: Run a bounded quality audit across a repo or control plane, split the scan into 3-5 evidence lanes, consolidate overlapping findings, and remediate the highest-leverage issues with one main-agent owner. Use when a user wants a broad hygiene pass, drift audit, regression triage, control-plane review, or a parallel analysis followed by direct remediation.
---

# Quality Radar Remediation

Use this skill to turn a broad, fuzzy quality pass into a disciplined sequence:

1. retrieve the owning docs, tests, hooks, and scripts
2. split the audit into bounded lanes
3. collect evidence in parallel only when the user explicitly authorizes subagents or parallel agent work
4. merge overlaps into one ranked finding set
5. remediate only the concrete, highest-leverage issues
6. rerun the proof bundle

This skill is for one-owner remediation. Subagents are evidence collectors, not patch owners.

## Inputs

- target surface: repo, control plane, toolchain, or docs surface
- stated goal: audit only, audit plus remediation, or enforcement hardening
- applicable owner docs and triggers
- current tests, lint, hooks, scripts, and validation commands
- explicit permission for subagents if parallel lane analysis is desired

## Pick Lanes

Use 3-5 lanes. Do not hardcode five when fewer lanes cover the problem.

Preferred lane types:

- `mechanical-drift`: lint, hooks, config drift, broken scripts, deterministic contract regressions
- `surface-ownership`: misplaced guidance, stale aliases, wrong owner surface, duplicated doctrine
- `evidence-gaps`: missing or misleading tests, weak proof paths, stale validation claims
- `cleanup-backlog`: stale or redundant surfaces, oversized docs, low-signal artifacts, expected-empty vs real drift
- `hot-path-ux`: cheap command behavior, help output, no-input behavior, install hints, direct-path misuse

Add a custom lane only when the target surface has a clear domain-specific contract.

## Choose Execution Mode

If the user explicitly asked for subagents, delegation, or parallel agent work:

- assign one lane per subagent
- keep each lane read-only
- require compact outputs with findings, evidence, owner surface, confidence, and cheapest enforcement target
- keep the main agent local and immediately work on retrieval, dedupe preparation, or proof planning instead of waiting

If the user did not explicitly authorize subagents:

- run the same lanes serially yourself
- keep the lane structure and output contract unchanged

## Lane Contract

Every lane must return only bounded, actionable findings:

- no more than 5-8 findings
- each finding includes:
  - status: `pass|warn|fail`
  - concrete evidence
  - impacted surface
  - likely owner
  - cheapest correct fix target: `lint|hook|config|test|doc|memory|runtime`
  - confidence
- include a short `do not retry` note for dead ends or misleading checks

Reject lane output that is vague, duplicative, or not grounded in code, docs, tests, or command output.

## Consolidate Findings

Before editing anything:

1. merge duplicates across lanes
2. separate deterministic failures from doctrine cleanup
3. rank by leverage:
   - broken proof or failing contract first
   - cheap enforcement wins over prose
   - broad doctrine cleanup only after mechanical issues are stable
4. choose one fix batch that can be verified cleanly

Do not mix a large ownership refactor into the same batch as a small deterministic regression unless the two are inseparable.

## Remediation Rules

- the main agent is the only writer unless the user explicitly asks for distributed implementation
- prefer the owning enforcement surface over narrative guidance
- patch the narrowest durable control:
  - failing deterministic rule -> test, lint, or script
  - unsafe pre-execution misuse -> narrow hook
  - owner confusion or sequencing gap -> owner doc or AGENTS trigger
- avoid speculative cleanups during the first fix pass
- if a finding is real but not fix-now, record it as residual risk instead of half-fixing it

## Proof Bundle

Always rerun the strongest cheap proofs that match the touched surfaces. Prefer a compact bundle such as:

- full lint for the owned surface
- targeted regression tests for changed contracts
- direct script or CLI smoke checks
- registry or ownership validation commands
- cleanup or GC dry-run commands when relevant

Do not claim success from static edits alone.

## Output Shape

When the audit phase ends, produce:

- chosen lanes
- consolidated top findings in ranked order
- fix batch chosen now
- deferred findings, if any, with reason

When remediation ends, produce:

- what changed
- exact proof bundle run
- what remains open

## Guardrails

- do not create parallel writers by default
- do not let subagents decide final priority
- do not treat weak stylistic complaints as equal to broken tests or contracts
- do not widen a repo-local issue into a global rule without cross-surface evidence
- do not keep feeder automations when the durable asset is the skill itself
- do not stop after analysis if the user asked for remediation and the fix is feasible now

## Expected Result

- broad audits become bounded and reproducible
- parallel analysis, when allowed, stays read-only and non-overlapping
- remediation is applied by one owner with clear priority
- proof commands close the loop
- recurring drift gets converted into enforcement instead of repeated manual rediscovery
