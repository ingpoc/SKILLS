---
name: project-governance-bootstrap
description: Bootstrap organized project or workspace governance using Linear for execution, Notion for durable memory, AGENTS-triggered docs, MCP/auth setup, and no-drift workflow controls. Use when starting a new repo/workspace or retrofitting ad hoc project management into a governed operating model.
---

# Project Governance Bootstrap

## Overview

Use this skill to set up or retrofit a project with the governance stack behind this workspace: Linear for execution, Notion for durable memory, GitHub for delivery history, AGENTS-triggered docs for operational rules, and explicit MCP/auth bootstrap guidance.

Use it when a user asks to organize a repo or workspace, standardize project management, add Linear/Notion discipline, create governance docs, or make documentation and issue flow stop drifting.

Quality bar:

- Docs-first and system-of-record-driven, not generic template sprawl
- Fail loud on missing auth, MCP setup, or required verification sources
- No assumption default when the answer can be checked in code, config, repo docs, or primary documentation
- `AGENTS.md` should define an explicit agent behavior contract, not just trigger lines
- Root mission should usually be a pointer to the canonical mission document rather than a second full copy

Design lineage:

- This skill aligns with OpenAI's harness-engineering guidance, especially the principles that repository knowledge should be the system of record and `AGENTS.md` should act as a compact table of contents rather than a monolithic manual.

## Workflow

### 1. Classify the scope first

- If the rules span multiple repositories, the owner is the workspace or umbrella-governance repo.
- If the rules are implementation-specific, the owner is that repo.
- Keep one owner per rule. Add pointers, not duplicate policy copies.

Use [references/artifact-matrix.md](references/artifact-matrix.md) to choose the right artifact set.

### 2. Lock the systems of record

- Linear owns active work, status, blockers, and review readiness.
- Notion owns ADRs, research notes, durable memory, and superseded-document pointers.
- GitHub owns code, branches, PR review, and merge history.
- Docs own the operating contract: scope, routing, workflow, MCP setup, and anti-drift rules.

If any of these ownership lines are fuzzy, fix that before creating templates or issues.

Use [references/linear-notion-bootstrap.md](references/linear-notion-bootstrap.md) for the exact bootstrapping sequence.

### 3. Create the minimum governance surfaces

For a workspace or umbrella repo, create the root operating surfaces first:

- `AGENTS.md`
- `ROADMAP.md`
- `MISSION.md` pointer to the canonical mission doc
- `docs/reference/MISSION.md`
- `docs/reference/WORKSPACE-SCOPE.md`
- `docs/operations/workflow-setup-responsibility-map.md`
- `docs/workflow/portfolio-governance.md`
- `docs/workflow/linear-issue-control-plane.md`
- `docs/workflow/notion-memory-control-plane.md`
- `docs/workflow/mcp-auth-bootstrap.md`
- `docs/workflow/research-validation-loop.md`
- `docs/workflow/git-governance-control-plane.md` when branch, review, or verification discipline matters
- `docs/workflow/browser-testing-control-plane.md` when UI, auth, wallet, or browser-state validation matters
- `mcp/README.md`
- workflow or ADR templates if the project will reuse them

For an implementation repo, create only repo-local governance surfaces and point back to the workspace owner when needed.

Recommended implementation-repo set:

- `AGENTS.md`
- `ROADMAP.md`
- `MISSION.md` pointer
- `docs/reference/MISSION.md`
- `docs/reference/REPO-SCOPE.md`
- `docs/operations/workflow-setup-responsibility-map.md`
- `docs/workflow/repo-governance.md`
- `docs/workflow/linear-issue-control-plane.md`
- `docs/workflow/notion-memory-control-plane.md`
- `docs/workflow/mcp-auth-bootstrap.md`
- `docs/workflow/research-validation-loop.md`
- `docs/workflow/git-governance-control-plane.md` when branch and merge discipline matter
- `docs/workflow/browser-testing-control-plane.md` when the product depends on meaningful browser validation
- `docs/adrs/`

### 4. Add AGENTS triggers instead of bloated always-on instructions

- Keep `AGENTS.md` compressed.
- Add `BEFORE ... -> read ...` trigger lines only for real decision points.
- Route the agent to the owning docs rather than copying long procedures into `AGENTS.md`.
- Mirror only the critical repo-specific rules locally.
- Include an explicit `Agent Behavior Contract` section.

Recommended `Agent Behavior Contract` content:

- use independent technical judgment
- do not assume facts that can be checked
- verify uncertain architecture, API, protocol, security, and governance claims against primary or repo-grounded sources
- state what is known, inferred, and unverified when it matters
- fail loud on missing auth, tooling, or systems of record
- do not route around a broken primary path with a fallback and call the work complete

### 5. Wire the execution and memory loops

- Define Linear statuses and exact transition rules.
- Define what gets written to Notion and what stays out.
- Encode superseded-memory hygiene: when a new ADR or brief replaces an old one, update the old artifact to point to the new canonical owner in the same workstream.
- Keep issue comments factual: branch, SHA, checks, blockers, merge state.
- Create the initial Linear project or issue set before major implementation begins.
- Create the Notion control-plane page and durable memory surfaces before the workflow depends on them.
- Define how agent memory is written, retrieved, validated, and superseded.
- Create one planning workflow doc that encodes: repo inspection first, assumption logging, primary-doc verification, issue/memory sync, pushback requirement, and confidence standard.

Use [references/bootstrap-checklist.md](references/bootstrap-checklist.md) as the operational checklist.
Use [references/agent-memory-operations.md](references/agent-memory-operations.md) for the durable-memory loop.

### 6. Bootstrap MCP and auth before the project depends on them

- Document required MCP servers and who owns each configuration surface.
- Add auth/bootstrap instructions for Notion, Linear, or other required connectors.
- Fail loud on missing auth or stale sessions.
- If browser testing involves authenticated or wallet-backed flows, define the attach strategy before relying on browser automation results.
- If the operating model depends on MCP tools or primary-doc verification, missing access is a blocker to fix rather than a reason to guess.

### 6.5. Avoid low-quality boilerplate

- Do not emit placeholder docs with `unknown project`, `unknown framework`, or generic technology tables when the repo can be inspected.
- Inspect the repo first and write governance docs that reflect actual runtime shape and operating constraints.
- Prefer a smaller, accurate set of docs over a larger generic set.

### 7. Validate before calling the setup complete

- The ownership of each doc/rule is explicit.
- `AGENTS.md` trigger lines resolve to real docs.
- Linear and Notion responsibilities are non-overlapping.
- The repo or workspace stays clean after setup; child repos or local runtime directories are ignored when they are not owned by the governance repo.
- At least one issue template and one ADR or research capture path exist when the operating model depends on them.
- No doc set can drift silently because the superseded-document rule is encoded.

## Operational Playbooks

### Linear project setup

- Create a Linear project when the work spans multiple issues or more than a trivial one-off implementation.
- Seed the project with at least one architecture or governance anchor issue if the operating model is still being established.
- Use statuses that cleanly separate planning, execution, review, and done states.
- Require each material issue to carry: problem, repo scope, desired outcome, acceptance criteria, and linked Notion context when durable reasoning exists.

The project bootstrap sequence and issue-shape contract are in [references/linear-notion-bootstrap.md](references/linear-notion-bootstrap.md).

### Notion setup

- Create one control-plane page for the repo or workspace.
- Create or identify the durable-memory surfaces:
  - ADR path
  - research path
  - incident path
  - optional typed `Agent Memory` database when retrieval across sessions matters
- Keep Notion out of execution tracking; execution remains in Linear.
- When a new ADR supersedes a prior brief or candidate note, update the older artifact in the same workstream.

### Agent memory usage

- Store reusable knowledge only when it should shape later work.
- Use typed memory rather than ad hoc scratch pages when retrieval matters.
- Record source, scope, confidence, and decision state.
- Retrieve validated memory first; treat candidate memory as guidance, not truth.
- Mark stale or superseded entries explicitly rather than leaving multiple artifacts to imply authority.

Use [references/agent-memory-operations.md](references/agent-memory-operations.md) for the write and retrieval loop.

## Trigger Examples

Use this skill when the user asks for things like:

- "Set up organized project management for this repo."
- "Bootstrap governance with Linear and Notion."
- "Create AGENTS-triggered workflow docs for this workspace."
- "Standardize our governance across projects."
- "Make sure docs and issue tracking stop drifting."

## References

- [Artifact Matrix](references/artifact-matrix.md)
- [Bootstrap Checklist](references/bootstrap-checklist.md)
- [Linear + Notion Bootstrap](references/linear-notion-bootstrap.md)
- [Agent Memory Operations](references/agent-memory-operations.md)
- OpenAI: [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
