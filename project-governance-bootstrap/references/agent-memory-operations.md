# Agent Memory Operations

This reference defines how to use durable agent memory as part of project governance rather than as a generic note dump.

## What belongs in agent memory

Good candidates:

- cross-repo architecture decisions
- research conclusions that should affect future work
- integration constraints
- governance rules that future sessions must remember
- user corrections that materially change the operating model

Bad candidates:

- transient debugging notes
- raw chat transcript
- execution status
- code details already obvious from the repo

## Memory shape

Each durable memory entry should capture:

- title
- memory type
- scope
- owning repo or `shared`
- status
- confidence
- reusable summary
- durable details
- source type
- source link when available
- related Linear issue
- related GitHub PR
- validation or review date
- supersedes link or field
- decision state such as `adopt`, `avoid`, `monitor`, or `superseded`

## Write loop

1. Decide whether the knowledge is reusable.
2. If yes, either create a new memory entry or update the governing one.
3. Summarize the reasoning rather than dumping session transcript.
4. Link the issue and code change if they exist.
5. If this replaces older guidance, mark the old artifact as superseded in the same workstream.

## Retrieval loop

Retrieve in this order:

1. validated memory
2. candidate memory if nothing validated exists
3. superseded memory only for historical context

Treat stale memory as warning-only until revalidated.

## Governance rule

Agent memory supports decisions and recurring context. It does not replace:

- repo docs for technical truth
- Linear for execution
- GitHub for delivery history
