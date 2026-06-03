# Session Analysis Rubric

Use this reference before turning transcripts or user prompts into durable
Codex setup.

## Evidence Tiers

| Tier | Signal | Action |
|---|---|---|
| Strong | repeated correction plus matching project evidence | recommend durable setup |
| Medium | repeated correction without project evidence | recommend a probe or lightweight owner |
| Weak | one-off prompt or preference | mention only if relevant |
| Conflict | user steering conflicts with official docs or repo contracts | correct the assumption and suggest safer path |

## What To Extract

Use raw Codex JSONL as the only canonical scoring source:

- scan `~/.codex/sessions` and `~/.codex/archived_sessions`
- extract only user-role messages
- exclude spawned subagent transcripts unless the user explicitly asks to audit
  delegated-agent prompts
- filter instruction dumps, hook prompts, environment context, and turn-aborted
  system notices
- retain file paths and line numbers as evidence pointers

Do not use Obsidian Markdown exports or `qmd` to score repeated steering or make
recommendations. Use them only for explicit human-readable lookup requests.

Look for:

- repeated `do not`, `never`, `use X`, or `do X instead`
- user asking for the same proof path repeatedly
- tool substitutions the user rejects
- recurring cleanup or stale-surface complaints
- recurring context-pollution complaints
- repeated commands that could become local actions
- model behavior the user corrects more than once

Do not treat assistant summaries as evidence unless they quote or reference the
user's prompt. User prompts and explicit corrections are stronger evidence than
assistant interpretation.

## Interpretation Rules

- Repetition means "investigate setup," not automatically "the user is right."
- Check official docs when the repeated preference is about Codex features,
  models, hooks, plugins, browser behavior, or subagents.
- Check repo contracts when the repeated preference is about a project workflow.
- Separate tool preference from product contract. Example: "use Chrome" may be a
  project validation contract, not a universal browser rule.
- Separate symptoms from causes. Example: repeated cleanup requests may indicate
  duplicate owner surfaces, not a need for more hooks.

## Recommendation Threshold

Recommend durable setup only when at least one is true:

- same correction appears in multiple turns or sessions
- the user explicitly asks to make it default
- the repo has a matching owner-surface gap
- a deterministic validation can prevent recurrence

Otherwise recommend a lightweight probe or no action.

## Privacy And Context Hygiene

- Do not paste long transcript excerpts.
- Prefer counts, turn identifiers, file paths, and compact paraphrases.
- Move noisy transcript analysis to a subagent when available.
- Keep the main answer to recommendations and evidence summary.
