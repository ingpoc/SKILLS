---
name: execplan
description: "Create or maintain one repository-local living execution plan for a complex implementation that cannot be safely completed from a short task plan. Use when the operator asks for an ExecPlan, a durable phased implementation plan, or a self-contained plan another agent can execute. Do not use for product-roadmap ownership, cross-session program selection, or simple tasks."
allowed-tools: Read Write Bash
---

# ExecPlan

An ExecPlan is a durable, self-contained execution document for one complex implementation. It complements the transient task plan; it does not replace the product plan or `session-orchestrate` program tracking.

## Create

1. Read the repo's product/architecture owner and existing plan convention before choosing a path.
2. Reuse the declared ExecPlan directory. If none exists, use `docs/exec-plans/active/`.
3. Research only the files, dependencies, tests, and constraints needed to make the plan executable.
4. Write a plan containing:
   - user-visible purpose and observable success;
   - current-state orientation and exact owner paths;
   - scoped non-goals and authorization boundaries;
   - ordered milestones with commands and expected evidence;
   - progress checklist, decision log, surprises, and outcomes;
   - idempotency and recovery notes for risky steps.
5. Keep product roadmap status in its existing owner. Link to it rather than copying it.

## Maintain

- Update progress and decisions as implementation proceeds.
- Record discovered constraints where they change execution.
- Move a completed plan to the repo's completed-plan location only after its observable success criteria are verified.
- Do not mark incomplete milestones complete to make the document look current.

## Boundary

- `execplan`: one complex implementation document.
- `session-orchestrate`: chooses and advances session-sized goals across the product plan.
- product/implementation owner docs: define roadmap scope and status.
- transient task plan: coordinates the current agent turn.
