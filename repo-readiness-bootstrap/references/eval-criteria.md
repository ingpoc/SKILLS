# Eval Criteria

Use these binary checks with `$autoresearch` to improve this skill without overfitting to one repo.

## Core Binary Evals

1. The report does not mark a repo `ready` unless required lanes are actually `verified`.
2. The report distinguishes `detected`, `configured`, `executed`, and `verified`.
3. The report detects mixed repos as web-facing when strong UI markers exist outside the root `package.json`.
4. The report prefers repo-owned commands over generic inferred commands when both exist.
5. The report emits an explicit parallel vs sequential execution plan.
6. The report names one strongest verification command and one strongest runtime proof lane.
7. The report does not treat `pytest` existence alone as verified runtime proof.
8. The report distinguishes repo-relevant integrations from globally configured integrations.
9. The report emits remediation steps with `validation_command` and `done_when`.
10. The report keeps browser proof as a first-class lane for web-facing repos.

## Stress Cases

Use at least one prompt from each category:

- mixed backend plus frontend repo
- backend-only service repo
- library repo with tests but no runtime
- repo missing `AGENTS.md`
- repo with docs and integrations but weak local scripts

## Failure Patterns To Watch

- collapsing discovery and proof into one status
- misclassifying repos from root-only signals
- claiming readiness from config presence alone
- blocking on optional integrations
- producing prose-only output with no remediation contract

## Success Signal

A strong run produces a manifest that a separate remediation agent can consume directly without asking what to fix first.
