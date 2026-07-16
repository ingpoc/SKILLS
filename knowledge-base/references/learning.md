# Session Learning Operation

Use this reference only for `$knowledge-base learning`. Convert hard-won, reusable discoveries from the active session into global KB articles; do not archive progress, decisions, or ordinary documentation.

## L1 — Extract candidate lessons

Review user corrections, failed attempts, diagnostics, diffs, research, and final validation. Require every gate:

| Gate | Required evidence |
|---|---|
| Novel | The conclusion is absent from authoritative docs and has no close KB article. |
| Transferable | It changes how another agent should approach a similar task. |
| Evidenced | The session contains a failure → cause → fix → verification chain. |
| Atomic | One article teaches one reusable lever or failure mode. |
| Sanitized | No secrets, private data, ephemeral coordinates, or user-specific identifiers. |

Reject project status, generic advice, unverified theories, successful first-try steps, and facts already owned by a skill or upstream documentation. If nothing passes, report a clean no-op.

## L2 — Prove novelty and establish the source boundary

Run two KB searches per candidate: the direct mechanism and a synonym or failure-mode query. Read suspicious top results.

Research the narrowest authoritative upstream documentation, repository file, or implementation page. Its URL may establish the substrate even when the session-derived conclusion is new. Explicitly separate upstream facts from live session evidence; never imply the source published the empirical conclusion. Defer the candidate when no stable, verifiable source URL exists.

## L3 — Compose the smallest useful article

Read `frontmatter-schema.md`, then write a 200–400 word draft to `/tmp/kb-drafts/<date>-<slug>.md`.

- Title the durable takeaway, not the session or project.
- State the behavior change and when it applies in `## Insight`.
- Record failure, root cause, fix, and concrete verification in `## Evidence`.
- Give a reproducible route, validation condition, and use/don't-use boundary in `## Applicability`.
- Use existing tags and the narrowest verified `source_url`.

Split different mechanisms. Do not pad a weak lesson.

## L4 — Gate, deduplicate, and ingest

For every draft, run strict lint and both novelty searches:

```bash
workflow knowledge lint <draft.md> --strict --json
workflow knowledge search "<title mechanism keywords>" --json
workflow knowledge search "<failure-mode synonyms>" --json
```

Require zero errors and warnings. If an existing article owns the lesson, improve that owner and reindex. Otherwise ingest with frontmatter tags as in I3.

## L5 — Verify retrieval and close out

Rebuild the browser. Search with the phrase a future agent is likely to use when stuck; require the new or updated article in the top three. Report created, updated, rejected, and deferred candidates with one-line reasons.
