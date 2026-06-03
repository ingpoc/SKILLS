---
name: cli-for-agents
description: >-
  Design or review CLIs so both coding agents and humans can use them reliably:
  dual-audience output, non-interactive paths, layered help, machine-readable
  data, predictable flags, safe mutations, and actionable errors. Use when
  building a CLI, adding commands, writing --help, or when the user mentions
  agents, terminals, automation-friendly CLIs, JSON output, or headless usage.
---

# CLI For Agents

Build CLIs as one engine with two renderers:
- human mode: readable text or TUI
- agent mode: deterministic JSON or NDJSON

Do not maintain separate doctrine for the two audiences. Keep one command model and one source of truth, then render it differently.

## Use When

- designing a new CLI
- reviewing an existing CLI for agent compatibility
- adding commands, flags, or help text
- building watch/status/list commands that must work for both humans and agents
- tightening tests or guardrails around CLI output shape

## Core Model

### Dual-audience design

- Separate data production from presentation.
- The same command should support both human-readable and machine-readable output.
- Prefer `--json` for bounded results and `--ndjson` for streams or watch modes.
- If a TUI exists, provide a non-TUI path for the same command.

Examples:

```bash
# Human
mycli watch --task abc123

# Agent
mycli watch --task abc123 --ndjson --no-tui
```

### Canonical behavior

- The machine-readable mode is not a second implementation.
- Do not let TUI logic become the only place where important state transitions exist.
- The CLI should emit the same underlying facts in both modes.

### Stable contract model

- Treat `--json` as the stable contract for agents, scripts, and tests.
- Human-formatted output may change as wording, spacing, and styling improve.
- If a command is consumed programmatically, say so explicitly in help:
  - script against `--json`
  - human output may change

## Bounded default output

### Protect the context window

- Default output must be the minimum useful response, not the maximum available data.
- Pre-sort items so the most important rows appear first.
- Truncate long fields by default.
- Require explicit opt-in such as `--full`, `--verbose`, or `--raw` for large payloads.
- Preserve critical head and tail context when truncating command output.

Bad:

```bash
mycli list
# dumps every row and every field
```

Good:

```bash
mycli list
# top items only, scoped fields only

mycli list --full
# full payload
```

### Progressive disclosure

Prefer graduated retrieval over one-shot dumps:

- `list` or `search` for routing
- `summary` for bounded orientation
- `show --section <name>` for targeted expansion
- `show --full` only by explicit opt-in
- Discovery responses should stay routing-sized. A good default JSON envelope is:
  - `status`
  - `query`
  - `count`
  - `results`
  - `schema_version`
  - `next_step` when it makes the cheapest follow-up obvious
- Bounded reads should report how resolution happened when the command accepted natural input.
  Use fields such as `matched_on` or `resolved_from` so agents know whether they are operating on an exact ID or a search-resolved target.

If a CLI owns rich documents, logs, or traces, build commands around:

```text
summary -> section -> full
```

This is better for both humans and agents than dumping the entire surface by default.

## Structured discoverability

- Root help should group commands by job, not alphabetically.
- Mark likely entry points with hints like `start here`.
- Prefer command families that separate:
  - discovery
  - resolve
  - read
  - write
- Every command should define:
  - short summary: 5-10 words, starts with an action verb
  - long description: what it does, when to use it, how it differs from nearby commands
  - examples: 3-5 concrete copy-pasteable invocations
- Examples matter more than prose. Agents infer flag shape from examples.

Example layout:

```text
Task Management:
  send        Send a message to start or continue a task (start here)
  watch       Subscribe to live updates for a running task
  get         Retrieve the current state of a task

Discovery:
  describe    Inspect identity, skills, and capabilities
```

For repeated external-service, archive, or admin workflows, aim for:

```text
doctor      Verify setup, auth, version, and reachability
discover    Find top-level resources or containers
resolve     Turn names, URLs, or slugs into stable IDs
read        Fetch exact objects or bounded lists
write       Perform one named mutation with preview or dry-run support
request     Raw escape hatch
```

## Metadata quality is routing quality

- Titles, summaries, tags, and identifiers determine what an agent loads next.
- Short descriptions must be specific, not generic boilerplate.
- Result-card summaries and longer detail summaries should be distinct.
- Tags should be deterministic and meaningful, not inferred freeform when routing quality matters.
- Cross-links between related entities or docs should be deliberate, not opportunistic.

If the CLI returns knowledge-like records, every item should have:

- a strong title
- a bounded short summary
- optional deeper summary or section handles
- useful tags or categories
- adjacent links or next-hop identifiers when available

## Agent-first interoperability

### `doctor` is first-class

- Durable agent-facing CLIs should expose a `doctor` or equivalent command.
- `doctor --json` should verify config, auth source, version, endpoint reachability, and missing setup.
- If offline or fixture mode exists, `doctor --json` should report that explicitly instead of failing ambiguously.
- Later tasks should be able to run `tool-name --json doctor` first without reading docs.

### Non-interactive first

- Every required input must be expressible as a flag, stdin, or positional argument.
- Interactive prompts are fallback only, never the default requirement.
- Respect `NO_COLOR` and `[APP]_NO_TUI` environment variables.
- When stdout is piped, suppress TUI, prompts, spinners, and decorative color.

### `--json` on everything that returns data

- Commands that return data should support `--json`.
- Keep machine output bounded too; large structured payloads still need scoping.
- Prefer `--ndjson` for streaming or watch commands.
- Never force agents to scrape tables or prose when the command already knows the schema.
- Do not return silent false-positive success payloads for misses. If resolution fails, return a deterministic error shape with retry guidance and, when possible, ranked suggestions.

### Pipelines and stdin

- Accept stdin when composition is natural.
- Support `-` as stdin where appropriate.
- Let one command feed the next without requiring temp files.

Examples:

```bash
mycli search "stalled tasks" --json | mycli rerank --stdin
mycli build --json | mycli deploy --spec-json -
```

### Discover, then resolve, then read

- Discovery commands should return bounded lists with stable handles.
- Resolve commands should convert human input such as names, URLs, slugs, or permalinks into canonical IDs.
- Read commands should accept those stable IDs directly.
- Do not force agents to repeat broad searches when an exact read can follow a resolve step.
- If a command accepts natural-language input directly, let `summary` or `read` auto-resolve obvious first-try matches and expose the resolution mode in machine output.
- Multi-word natural queries should not require brittle quoting if the command intent is retrieval rather than mutation.

## Headless authentication

- Agents cannot complete browser auth flows reliably.
- Support headless auth such as env vars, tokens, service accounts, or pre-authenticated config.
- If interactive auth is unavoidable, fail immediately with a clear actionable hint.
- Never hang waiting for a browser login when running in no-TUI or machine-readable mode.

## Mutative safety

- Mutating commands should support `--dry-run`.
- Commands with confirmations should offer `--yes` or `--force`.
- Default behavior should remain safe for humans.
- Repeat successful operations safely: no-op or explicit `already done` beats duplicate side effects.

## Error guidance

- Fail fast on invalid flags, missing config, missing auth, or missing prerequisites.
- Print exact next-step commands in errors.
- Emit errors to stderr.
- Return deterministic exit codes:
  - `0` success
  - `1` general failure
  - `2` invalid usage
  - `3` auth or connectivity failure

Example:

```text
Error: database not initialized
Hint: run 'mycli init' to create the local database
```

## Success output

- Successful commands should return machine-useful identifiers and next-hop values.
- Plain text is fine for human mode, but avoid decorative output as the only success signal.

Example:

```text
deployed v1.2.3 to staging
url: https://staging.myapp.com
deploy_id: dep_abc123
duration: 34s
```

## Config and environment

- Prefer standard config locations and explicit environment selection.
- Support named environments like `--env local|staging|prod`.
- Let agents switch environments without knowing raw URLs or tokens.

## Visual design

- Color should communicate state, not decorate prose.
- Prefer semantic colors:
  - accent: headers, landmarks
  - command: command names and flags
  - pass: success
  - warn: warnings or pending
  - fail: errors
  - muted: metadata
  - id: identifiers
- Whitespace and alignment should carry hierarchy more than color.
- When formatting tables with ANSI colors, pad before styling or use a layout engine that handles colored strings safely.

## Enforcement inside the CLI

These are the highest-value behaviors to enforce in code, not just document:

- stdout piped or `--json`:
  - disable TUI, prompts, spinners, and progress animation
- bounded defaults:
  - limit rows, truncate long fields, and require `--full` or `--verbose` for expansion
- stable machine mode:
  - return one documented `--json` schema per command
- deterministic exit codes:
  - keep success, usage, auth, and runtime failures separated
- mutative safety:
  - require `--yes` or `--force` for dangerous actions
  - expose `--dry-run` for previewable mutations
- explicit errors:
  - always return a `Hint:` line with the exact next command when recovery is obvious

## Enforcement around the CLI

These should be enforced through tests, quality gates, or CI:

- snapshot or schema tests for `--json` output on agent-consumed commands
- tests proving human output can change without breaking `--json`
- tests for piped stdout behavior: no TUI, no prompts, no spinner leakage
- tests for bounded default output vs `--full`
- tests for summary/section/full retrieval flows where the CLI returns rich documents
- tests for `doctor --json` setup and auth reporting
- tests proving the installed command works from outside the source folder
- tests for `discover -> resolve -> read` flows using stable IDs
- tests for headless auth failure paths
- tests for deterministic exit codes and `Hint:` guidance
- help-text checks: grouped commands, examples present, start-here hints where needed
- regression tests for metadata quality:
  - titles
  - summaries
  - tags
  - related links

If drift keeps recurring, add a gate instead of repeating cleanup.

## Review checklist

- non-interactive path exists
- `--json` or `--ndjson` exists where needed
- TUI has a non-TUI equivalent
- help is grouped and example-rich
- outputs are scoped, sorted, and bounded by default
- `summary -> section -> full` exists where the CLI exposes large documents or traces
- `--json` is treated as the stable contract
- `doctor --json` exists for durable CLIs
- command families are separated into discover, resolve, read, and write where the domain needs them
- short summaries are specific, not generic boilerplate
- tags and adjacent links are useful routing metadata when the CLI returns knowledge-like records
- auth works headlessly or fails clearly
- mutative commands have `--dry-run`
- confirmations have `--yes` or `--force`
- exit codes are deterministic
- errors include exact next steps
- command shape and shorthand usage are consistent
- success output exposes IDs, URLs, durations, and next useful values
- tests enforce the important invariants above

## When reviewing an existing CLI

Check:
- discoverability
- examples
- machine-readable output
- doctor/setup surface
- no-TUI behavior
- stdin and pipeline support
- headless auth
- bounded default output
- discover/resolve/read/write separation
- summary/section/full retrieval shape where relevant
- metadata quality for routing
- mutative safety
- deterministic errors
- consistent flags
- semantic output
- idempotency
- tests or gates covering the contract

## Companion skill expectations

If the CLI is meant for repeated use across threads, pair it with a companion skill that records:

- when to use the CLI instead of ad hoc shell or browser work
- which command to run first, usually `doctor`, `discover`, or `summary`
- how to keep output bounded
- where file downloads or exports land
- which write commands require explicit user approval

The CLI is the executable surface. The companion skill is the routing memory for future agents.
