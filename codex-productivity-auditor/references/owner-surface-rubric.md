# Owner Surface Rubric

Use this reference before deciding where a productivity finding belongs.
Official Codex guidance treats AGENTS.md, memories, skills, MCP, and subagents
as complementary surfaces, not substitutes.

## Decision Order

1. Can an existing repo command, test, lint, or app feature solve it?
2. Is it an always-loaded rule that must apply before work starts?
3. Is it a repeatable method that benefits from progressive disclosure?
4. Is it a multi-step operating lane rather than a reusable capability?
5. Is it a deterministic guardrail?
6. Is it external-system access?
7. Is it noisy evidence gathering?
8. Is it stable recurring maintenance?
9. Is it only a memory-worthy lesson?

## Surface Map

| Signal | Primary owner | Use when | Avoid when |
|---|---|---|---|
| Always-on project rule | nearest `AGENTS.md` | repeated mistake or routing rule must load every time | long procedure or rare edge case |
| Cross-project doctrine | global workflow/reference doc | applies across repos | repo-specific behavior |
| Repo-specific precedent | repo memory | helps next agent avoid a local trap | should be enforced or always loaded |
| Reusable method | skill | repeated workflow with judgment, scripts, or references | one-off instruction |
| Multi-step operating lane | workflow doc | sequence, proof matrix, owner routing | deterministic command is enough |
| Stable check | script, lint, test, quality gate | objective pass/fail exists | model judgment is needed |
| Narrow unsafe boundary | hook | must block or continue at a lifecycle edge | review/skill/automation is enough |
| External capability | plugin or MCP | needs GitHub, browser, docs, Linear, Figma, etc. | local files are sufficient |
| Noisy evidence work | subagent | read-heavy exploration, logs, tests, browser proof | immediate blocker or edit coordination |
| Recurring stable task | automation | method is reliable manually | still needs frequent steering |
| Convenience command | Codex local environment action | repeated local run/test/log command | mutates product lifecycle invisibly or needs agent judgment |

## Tie Breakers

- Prefer skill/workflow over AGENTS.md when guidance is long.
- Prefer tests/lint over prose when behavior is deterministic.
- Prefer subagent over main context for noisy proof.
- Prefer automation only after manual workflow stability.
- Prefer plugin before custom MCP when an official plugin exists.
- Prefer Codex local environment actions over hooks for repeated local commands.

## Local Environment Action Rules

- Use for repeated project run, test, lint, build, server, log, or metric
  commands.
- Ground the recommendation in official Codex local-environment docs.
- Create the first action through Codex app settings and inspect the generated
  project `.codex` artifact before editing or committing more actions.
- Do not hand-write an unknown local-environment schema.
- Do not use actions for lifecycle steps that must remain product-visible or
  approval-driven.

## Rejection Rules

Do not create durable setup when:

- evidence is one-off
- the user preference conflicts with official docs and no exception is justified
- the owner surface would add more friction than the repeated problem
- the recommendation cannot name a validation path
