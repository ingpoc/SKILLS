---
name: agent-feedback-artifact
description: Add, remove, serve, test, and operate a server-backed in-page agent feedback capability for HTML artifacts, static pages, or local app builds. Use when the user wants Browser-style annotation inside the artifact/app itself, marker-local chat, comment-triggered agent work, queued marker processing, deterministic install/remove scripts, preflight/closeout checks, browser acceptance evidence, or progressive-disclosure access to marker context.
---

# Agent Feedback Artifact

> **Self-validate after edits.** Any change to this skill's files (`SKILL.md`, `scripts/`, `references/`, `templates/`, `assets/`) must be followed by `./scripts/validate.sh` from the skill directory. Hard findings require optimizing the skill before closeout.

This skill turns an HTML artifact or local app page into an interaction space between the operator and an agent. It injects a managed annotation widget, serves the page through a local feedback server, queues marker-scoped user comments as agent work items, and lets agents fetch only the context tier they need.

## Operating Contract

| Field | Decision |
|---|---|
| Primary archetype | Server / API workflow |
| Secondary archetypes | Browser / UI workflow, deterministic script workflow, artifact modifier, agent orchestration |
| Operator trigger | The user wants in-page feedback, annotation, or marker chat inside an HTML artifact/app instead of screenshot/chat-window feedback. |
| Output | The target page is served with the feedback capability; marker comments are queued, processed, and replied to inside marker-local chat. |
| Success evidence | Browser-visible marker flow works; server queue/status confirms processing; closeout reports no unexpected queued/processing work. |
| Deterministic surface | Add/remove/preflight/closeout/server/next/details/mark/routing/dispatch scripts and validation checks. |
| Judgment surface | Deciding whether a marker needs direct main-agent handling, a cheap marker worker, or a deeper context worker. |
| Context loading | Default packet first; marker details on demand; full artifact/app/source context only when the marker requires it. |

## When To Use

Use this skill when the user asks for:

- annotation or commenting directly inside an HTML artifact or app
- Browser-style targeted feedback without screenshot copying
- per-marker chat that queues feedback while the agent works
- deterministic add/remove/toggle of the capability
- operator comments to trigger agent processing
- progressive disclosure so agents do not ingest full UI/app context by default
- preflight and closeout evidence for safe handoff

Do not use this for a plain static HTML artifact that does not need in-page feedback, server APIs, marker state, or agent processing.

## Workflow

### Preflight

1. Run:

```bash
node scripts/agent-feedback-preflight.mjs <artifact.html> --port <port>
```

2. Confirm:

- target exists and contains `</body>`
- widget install state is known
- server script exists
- selected port is available or consciously reused
- local queue is readable/writable when present
- webhook config is reported when comment-triggered processing is required

3. If the target is an app build, identify whether this is a prototype static injection or a durable app integration. For React/Next/Vite prototypes, static injection into built HTML is acceptable. Durable product integrations should wrap the same client behavior as an app component while keeping the server/API contract stable.

### Add And Serve

```bash
node scripts/add-agent-feedback.mjs <artifact.html>
AGENT_FEEDBACK_WEBHOOK_URL=http://127.0.0.1:<worker-port>/hook \
  node scripts/artifact-feedback-server.mjs <serve-root> <port>
```

The managed block is bounded by `AGENT_FEEDBACK_WIDGET_START` and `AGENT_FEEDBACK_WIDGET_END`. Do not hand-edit the injected block. Use `remove-agent-feedback.mjs` when removal is requested.

The target must be served by `artifact-feedback-server.mjs`; `file://` cannot submit feedback.

### Browser Acceptance

Browser verification is mandatory before calling the capability working. Use Chrome when the user asks for Chrome-backed testing.

Minimum browser checks:

- selecting without comment creates no marker
- first comment creates one marker
- multiple messages stay in one marker thread
- abandoned composer does not leave an empty marker
- UI tab shows selected element context
- queued message delete removes the message and removes the marker when empty
- processed message shows a done indicator and marker-local agent reply
- marker trash deletes/releases that marker thread
- global trash clears all markers
- reload preserves processed marker status and replies

Comment-triggered processing acceptance:

- submit at least one marker comment from the page
- verify the server emits webhook or otherwise creates a queued work item
- verify processing moves through `queued` -> `processing` -> `done`/`blocked`/`canceled`
- verify the agent reply appears inside that marker's chat
- do not manually poll and fix as a substitute for trigger verification

Multi-marker acceptance:

- submit at least three marker comments rapidly without waiting for the first to finish
- verify three distinct marker ids
- verify each marker receives its own reply
- verify concurrent processing does not merge markers or overwrite same-artifact edits

## Marker Work Protocol

Use the progressive-disclosure scripts instead of loading the whole artifact by default:

```bash
node scripts/agent-feedback-next.mjs
node scripts/agent-feedback-details.mjs <work-id>
node scripts/agent-feedback-mark.mjs <work-id> processing
node scripts/agent-feedback-mark.mjs <work-id> done "Agent-visible reply"
```

Default work packets should include only:

- work id
- marker id
- artifact path/title/version
- latest user message
- target selector
- visible text
- status
- compact thread summary when present

Fetch full details only when the marker requires geometry, viewport, selected text, UI snapshot, raw payload, source, data, or broader artifact context.

## Processing Model

- The main agent owns final edits, conflict resolution, and browser verification.
- Marker workers diagnose, propose, and reply through marker-scoped work packets.
- Do not keep a live subagent per marker by default. Persist compact `threadSummary` and spawn or resume work only when new marker feedback arrives.
- Same-marker follow-up should reuse the marker summary and use a cheaper worker when possible.
- Distinct markers may be diagnosed in parallel, but writes to the same artifact/app must be serialized or merged through the main agent.
- Deleting a marker releases its marker thread and cancels queued work where possible.

Routing expectations:

- simple visual/typography/copy edits can route to `no_worker_main_agent_direct`
- data/dependency/root-cause comments route to `deep_marker_worker` with narrow context first
- same-marker follow-up with enough summary can route to a cheap summary worker
- selectors are evidence, not intent; do not classify data work merely because a selector contains `data-*`

## Script Inventory

| Script | Owns |
|---|---|
| `scripts/add-agent-feedback.mjs` | Deterministic install into target HTML. |
| `scripts/remove-agent-feedback.mjs` | Deterministic removal of only the managed block/meta. |
| `scripts/artifact-feedback-server.mjs` | Static serving, feedback APIs, queue storage, webhook dispatch. |
| `scripts/agent-feedback-preflight.mjs` | Readiness checks and exact next commands. |
| `scripts/agent-feedback-closeout.mjs` | Read-only state/evidence report by default. |
| `scripts/agent-feedback-next.mjs` | Next queued marker packet. |
| `scripts/agent-feedback-details.mjs` | Full marker payload on demand. |
| `scripts/agent-feedback-mark.mjs` | Status updates and marker-visible replies. |
| `scripts/agent-feedback-routing.mjs` | Context-efficient route selection. |
| `scripts/agent-feedback-dispatch.mjs` | Direct/worker processing decision. |
| `scripts/test-agent-feedback-webhook-receiver.mjs` | Webhook delivery smoke receiver. |
| `scripts/test-agent-feedback-auto-runtime.mjs` | Event-triggered processing harness for acceptance testing. |

## Design Guidance

The widget should feel like a capability layer, not page content. Use a permanent small top-right launcher icon, similar in weight to a light/dark mode toggle. When toggled on, reveal small standalone annotate/count/trash/menu icons next to it with transparent chrome and soft hover states. Do not use a large capsule or persistent panel for the idle state. When toggled off, only the launcher remains visible.

The marker popover should stay compact by default. The configure icon expands it into `Agent` and `UI` tabs. Agent replies stay attached to the marker. The `UI` tab shows selected element identity and UI snapshot. Marker trash releases that marker; global trash clears all markers.

## Verification

Run the skill validation wrapper:

```bash
./scripts/validate.sh
```

Minimum manual checks when changing scripts:

```bash
node --check scripts/add-agent-feedback.mjs
node --check scripts/remove-agent-feedback.mjs
node --check scripts/artifact-feedback-server.mjs
node --check scripts/agent-feedback-preflight.mjs
node --check scripts/agent-feedback-closeout.mjs
node --check scripts/agent-feedback-next.mjs
node --check scripts/agent-feedback-details.mjs
node --check scripts/agent-feedback-mark.mjs
node --check scripts/agent-feedback-routing.mjs
node --check scripts/agent-feedback-dispatch.mjs
node --check scripts/test-agent-feedback-webhook-receiver.mjs
node --check scripts/test-agent-feedback-auto-runtime.mjs
```

For deterministic removal:

```bash
cp original.html roundtrip.html
node scripts/add-agent-feedback.mjs roundtrip.html
node scripts/remove-agent-feedback.mjs roundtrip.html
cmp -s original.html roundtrip.html
```

For comment-triggered processing, start `test-agent-feedback-auto-runtime.mjs`, start the artifact server with `AGENT_FEEDBACK_WEBHOOK_URL`, submit marker comments in Chrome, and verify queue status plus marker-local replies.

## Closeout

Always run:

```bash
node scripts/agent-feedback-closeout.mjs <artifact.html> --port <port>
```

Report:

- widget installed/not installed
- server listening state
- webhook configured/signing state when used
- queue counts for the artifact
- browser acceptance evidence
- whether any queued/processing work remains
- cleanup commands, without mutating by default

Stop any temporary test servers you started and verify their ports are clear.

### Friction Introspection

Before updating this skill, classify any friction:

| Friction source | Action |
|---|---|
| Agent bypassed comment-triggered processing, missed preflight/closeout, over-loaded context, or lacked browser acceptance criteria | Update this skill. |
| Add/remove/server/routing/overlay/test script bug | Fix the script and add/adjust validation. |
| Target artifact/app bug or page-specific request | Fix the target, not this skill. |
| Chrome/plugin flake, auth, provider error, or rate limit | Improve diagnostics only when the check is reusable. |
| One-off operator preference | Do not update the skill unless it becomes repeated workflow need. |

## Hard Rules

1. **Use scripts for install/remove.** The managed block must remain deterministic and reversible.
2. **Serve the page.** Feedback APIs do not work from `file://`.
3. **Treat operator comments as the trigger.** Do not replace trigger verification with manual polling and direct fixes.
4. **Load context progressively.** Fetch full details only when the marker packet is insufficient.
5. **Keep main-agent ownership of writes.** Marker workers can diagnose/propose, but same-artifact edits must be conflict-safe.
6. **Browser-test before success.** UI capability is not complete until the served page proves the marker workflow.
7. **Close out read-only by default.** Cleanup or queue clearing requires explicit operator intent or a test-only flag.

## Cross-References

- [Overlay client](references/overlay.html)
- [Add script](scripts/add-agent-feedback.mjs)
- [Remove script](scripts/remove-agent-feedback.mjs)
- [Server](scripts/artifact-feedback-server.mjs)
- [Preflight](scripts/agent-feedback-preflight.mjs)
- [Closeout](scripts/agent-feedback-closeout.mjs)
- [Routing](scripts/agent-feedback-routing.mjs)
- [Dispatch](scripts/agent-feedback-dispatch.mjs)
- [Auto runtime test](scripts/test-agent-feedback-auto-runtime.mjs)

## Why This Skill Exists

Agent feedback on visual artifacts is otherwise lossy: operators describe screen regions in chat, agents guess the target, and context balloons. This skill makes the artifact itself the feedback surface, captures marker-scoped intent at the source, and gives agents a small default packet with deeper context available only when needed.
