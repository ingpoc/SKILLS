# Model Routing Rubric

Use this reference before recommending subagent model settings. Model guidance
can drift; check official OpenAI Codex model and subagent docs when freshness
matters.

## Core Rule

Choose the smallest model that can reliably complete the delegated task.

- Mini for bounded evidence gathering.
- Frontier for risky judgment, integration, and ambiguous multi-step work.
- Main thread owns decisions and final output.
- Subagents return compact findings, not raw logs.

## Routing Table

| Use case | Model | Reasoning | Notes |
|---|---|---|---|
| Main implementation or root-cause owner | `gpt-5.5` | medium/high | Use for ambiguous, multi-step work with integration risk. |
| Architecture or owner-boundary review | `gpt-5.4` or `gpt-5.5` | high | Use stronger reasoning when correctness depends on boundaries. |
| Cleanup auditor | `gpt-5.4-mini` | low/medium | Search, lint, stale-reference checks, compact summary. |
| Code mapper or repo explorer | `gpt-5.4-mini` | low/medium | Read-heavy, bounded, low write risk. |
| Test or log triage | `gpt-5.4-mini` | medium | Upgrade only when failures require deep causality. |
| Browser verifier | `gpt-5.4` | medium/high | Needs visual evidence and careful repro reporting. |
| Official docs or vendor freshness | `gpt-5.4-mini` first | low/medium | Upgrade to `gpt-5.4` if docs conflict or interpretation is ambiguous. |
| Security or correctness reviewer | `gpt-5.4` or `gpt-5.5` | high | Higher cost is justified by risk. |
| Bulk list or CSV-style processing | `gpt-5.4-mini` | low | Throughput and compact output matter most. |
| Near-instant text-only iteration | `gpt-5.3-codex-spark` if available | low | Use only when latency matters more than broad capability. |

## Upgrade Triggers

Upgrade from mini to a frontier model when:

- the task needs cross-file causal reasoning
- browser or runtime evidence conflicts with code evidence
- the output will drive a risky edit, hook, security, or architecture change
- the subagent must decide owner boundaries, not just gather evidence
- the first pass returns uncertainty or contradictory findings

## Downgrade Triggers

Use mini or lower reasoning when:

- the task is search, inventory, lint, or summarization
- the output is advisory and will be reviewed by the main agent
- the task has a deterministic command or checklist
- failure is low cost and easy to retry

## Do Not Use Subagents

Keep work in the main thread when:

- the subtask is the immediate blocker
- the task requires tight edit coordination
- the subagent would need hidden conversation context
- the cost of summarizing back exceeds the parallelism benefit

## Confidence Check

Before final recommendation, ask:

1. Is this task mostly evidence gathering or decision making?
2. What is the cost of a wrong answer?
3. Can a deterministic command verify the result?
4. Will the subagent output stay compact?
5. Does official Codex model guidance need a freshness check?

If any answer is unclear, choose a conservative model or recommend a probe
instead of a durable setup.
