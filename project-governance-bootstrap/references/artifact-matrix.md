# Artifact Matrix

Use this matrix to decide what belongs in a workspace governance repo versus an implementation repo.

## Workspace Or Umbrella Repo

Use this scope when the project governs multiple child repos or owns cross-repo operating policy.

- `AGENTS.md`: canonical workspace instruction source with trigger lines
- `ROADMAP.md`: portfolio roadmap
- `docs/reference/MISSION.md`: why the workspace exists
- `docs/reference/WORKSPACE-SCOPE.md`: repo boundary and ownership rules
- `docs/operations/workflow-setup-responsibility-map.md`: routing map
- `docs/workflow/linear-issue-control-plane.md`: status and issue-update rules
- `docs/workflow/notion-memory-control-plane.md`: durable-memory policy
- `docs/workflow/mcp-auth-bootstrap.md`: auth and connector bootstrap
- `mcp/README.md`: MCP ownership and setup notes
- `rules/*`: concise cross-repo guardrails
- `workflows/*`: reusable templates

Do not put implementation-only runbooks or app-specific test details here.

## Implementation Repo

Use this scope when the repo ships one application or service.

- repo `AGENTS.md`: repo-local constraints only
- repo `ROADMAP.md`: repo roadmap only
- repo ADRs or architecture docs: implementation-specific decisions
- tests, build scripts, deployment docs: repo-local
- `JARVIS.md`: only if this repo is a target project with execution memory owned there

Do not duplicate workspace governance rules here. Add a pointer to the workspace owner when needed.

## Ownership Rules

- Linear owns active execution and status.
- Notion owns durable memory and decision logs.
- GitHub owns code and review history.
- Docs own the operating contract.

If two places are trying to own the same rule, remove one.
