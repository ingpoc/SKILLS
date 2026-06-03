# Bootstrap Checklist

Run this checklist before declaring a governance setup complete.

## Control Plane

- Scope is classified correctly: workspace versus implementation repo
- Source-of-truth systems are explicit
- No rule is duplicated across multiple owners

## Docs

- `AGENTS.md` exists and is compressed
- `AGENTS.md` contains an explicit agent behavior contract
- Trigger lines point to real documents
- Mission and scope docs exist when the project needs them
- Root `MISSION.md` points to the canonical mission doc when a pointer pattern is used
- Workflow docs exist for Linear, Notion, and MCP/auth if those systems are used
- Research-validation workflow exists when the agent must make grounded recommendations under uncertainty
- Git governance workflow exists when branch/review/verification discipline matters
- Browser testing workflow exists when UI validation depends on browser or auth state
- Routing and ownership are documented

## Issue And Memory Workflow

- Linear statuses are defined
- Ready-for-review updates include branch, SHA, and verification state
- Notion write rules are defined
- Superseded documents are updated to point to their canonical replacements

## Operational Setup

- Required MCP servers and auth flows are documented
- Browser testing strategy is defined if the product depends on authenticated, wallet, or extension-backed flows
- Failure mode for missing auth/tooling is explicit
- Missing required verification sources are treated as blockers, not details to route around

## Acceptance Gate

The setup is complete only when all of the following are true:

- another engineer could tell where to put a new rule, ADR, issue update, or MCP note without guessing
- another engineer could tell how the agent is expected to behave under uncertainty, failure, and architectural disagreement
- docs do not silently drift because superseded-memory hygiene is encoded
- the governance repo or workspace root stays clean in normal use
- repo-local implementation details are not leaking into the workspace governance layer
