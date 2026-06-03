# Linear + Notion Bootstrap

Use this sequence when standing up a new governed repo or workspace.

## 1. Create the Linear project

Create a Linear project when the work is expected to span multiple issues, milestones, or repos.

Recommended initial issue set:

- architecture or governance anchor
- first implementation milestone
- first verification or test-hardening milestone
- explicit follow-ups for known risk areas

Each material issue should include:

- clear problem statement
- affected repo or repos
- desired outcome
- acceptance criteria
- constraints or risks
- link to Notion context if durable reasoning exists

Recommended issue lifecycle:

1. `Backlog`
2. `Planned`
3. `In Progress`
4. `In Review`
5. `Done`

Agent operating rule:

- Move to `In Progress` when the working branch exists.
- Comment with branch name, reviewable SHA, checks, browser mode, and blockers at meaningful checkpoints.
- Move to `In Review` only after the required validation passes.
- Move to `Done` only after merge and doc/memory sync.

## 2. Create the Notion control-plane surface

Create one top-level page for the project or workspace that links the durable artifacts.

Recommended sections:

- mission and scope
- governing ADRs
- research notes
- incident notes
- links to Linear project and key repos

Do not use this page as a task board. Task execution remains in Linear.

## 3. Create durable memory structures

For light-weight setups, page-based memory is enough:

- ADR pages
- research pages
- brief pages
- incident pages

For reusable cross-session retrieval, create a typed `Agent Memory` database with at least:

- title
- memory type
- scope
- repo
- status
- confidence
- summary
- details
- source type
- source link
- linked Linear issue
- linked GitHub PR
- validated-on date
- supersedes relation or field
- decision field

## 4. Link the systems together

- Linear issues should link to the governing Notion page or ADR when durable reasoning exists.
- Notion pages should link back to the relevant Linear issue and GitHub branch or PR when available.
- Repo docs should point to the governing workspace doc instead of duplicating it.

## 5. Anti-drift rules

- If a new ADR supersedes an older brief, candidate note, or architecture page, update the older artifact immediately with a superseded note and pointer.
- Do not let both Linear and Notion own execution state.
- Do not let the governance repo absorb repo-local implementation truth.
