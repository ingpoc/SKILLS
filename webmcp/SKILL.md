---
name: webmcp
description: Use when a web app should expose browser-native WebMCP tools and you need to integrate, verify, troubleshoot, or directly operate that app through Chrome's WebMCP early-preview runtime. Trigger for requests like "enable WebMCP", "integrate WebMCP into this dashboard", "why is navigator.modelContext missing", "why can tools register but not execute", "test WebMCP", or "operate this app through WebMCP".
---

# WebMCP

Use this skill when the goal is browser-native tool registration and direct in-browser tool execution, not just external browser control.

## Use When

- integrating WebMCP into a dashboard, app, or workflow surface
- proving a page is WebMCP-ready in a real Chrome session
- debugging why tools register but cannot be directly executed
- validating browser-native operation before treating the page as an operator surface
- designing tool contracts, readiness gates, or troubleshooting paths for WebMCP-backed apps

## Do Not Use When

- the task only needs DOM control, screenshots, console logs, or network inspection
- the page does not need browser-native tools
- the task is headless-only
- the page should mutate durable state directly instead of routing through audited backend actions

## Capability Model

Treat WebMCP as two separate lanes:

- `navigator.modelContext`
  - registration surface
  - use it to detect support and register tools
- `navigator.modelContextTesting`
  - early-preview testing and direct execution surface
  - use it to list registered tools and execute them directly during validation

Do not assume registration implies invocation.

WebMCP has two implementation styles:

- imperative API
  - register tools in JavaScript with `registerTool(...)`
  - best for dashboards, app actions, and broker-backed operations
- declarative API
  - annotate forms with `toolname`, `tooldescription`, and optionally `toolautosubmit`
  - best for stateful form workflows where the browser should fill fields and submit through the existing UI contract

## Browser Requirements

1. Chrome 146+.
2. WebMCP testing enabled in the actual browser session being used.
   - enable `chrome://flags/#enable-webmcp-testing` and relaunch Chrome
   - or launch Chrome with `--enable-features=WebMCPTesting`
3. The page must load in that same browser session.
4. The app must feature-detect `navigator.modelContext?.registerTool`.

Important:

- browser context is required
- do not assume headless operation exists
- isolated Chrome sessions do not reliably inherit flag state from the normal profile

## Fresh Chrome Launcher

Use the bundled launcher at `scripts/start_webmcp_chrome.sh` when you need a repeatable session.

Minimum launcher requirements:

- dedicated `--user-data-dir`
- `--enable-features=WebMCPTesting`
- remote debugging if an external controller will attach
- deterministic initial page such as `about:blank`
- cleanup of the temporary profile after the run

## Integration Contract

An app is not WebMCP-ready just because the browser exposes `navigator.modelContext`.

Require all of these:

- feature detection for `navigator.modelContext?.registerTool`
- explicit tool registration after required app state is loaded
- tool handlers that route through existing backend actions or audited scripts
- visible readiness state in the UI
- at least one safe non-destructive action that can prove the tool bridge works
- direct testing-path proof through `navigator.modelContextTesting`

Recommended UI states:

- `WEBMCP unavailable`
- `WEBMCP available`
- `WEBMCP ready (N)`

Use `ready` only after registration succeeds and the testing surface can see the registered tool set.

## Tool Design

Follow these design rules:

- use atomic, composable tools
- avoid overlapping tools with subtle semantic differences
- accept raw user intent where possible
- prefer explicit types and enums in schemas
- validate in code, not only in schema
- return descriptive errors so the caller can correct and retry
- return after UI state has been updated
- register tools only when they make sense for the current page state

Prefer positive descriptions. Name tools for what they do, not for what they are not.

For declarative forms:

- keep labels and parameter descriptions explicit
- use `toolparamdescription` when labels are insufficient
- use `toolautosubmit` only when automatic submission is actually safe
- if agent-driven submission needs custom results, handle `SubmitEvent.agentInvoked` and `respondWith(...)`

## Verification Workflow

1. Start the app.
2. Open it in a Chrome session with WebMCP testing enabled.
3. Verify registration support:

```js
() => ({
  hasModelContext: !!navigator.modelContext,
  hasRegisterTool: !!navigator.modelContext?.registerTool,
})
```

4. Verify direct testing support:

```js
() => ({
  hasModelContextTesting: !!navigator.modelContextTesting,
  hasListTools: !!navigator.modelContextTesting?.listTools,
  hasExecuteTool: !!navigator.modelContextTesting?.executeTool,
})
```

5. List tools:

```js
() => navigator.modelContextTesting.listTools()
```

6. Execute one safe tool directly:

```js
() => navigator.modelContextTesting.executeTool("tool_name", "{}")
```

Important:

- `executeTool(...)` expects a JSON string argument like `"{}"`
- do not pass a raw JavaScript object such as `{}`

7. If the tool mutates state, verify the owning backend artifact or UI state changed as expected.

## Proof Of Readiness

Treat a session as truly ready only if all of these are true:

- `navigator.modelContext` exists
- `navigator.modelContext.registerTool` exists
- `navigator.modelContextTesting` exists
- `navigator.modelContextTesting.listTools` exists
- `navigator.modelContextTesting.executeTool` exists
- the page completed registration without throwing
- the UI shows a truthful ready state such as `WEBMCP ready (N)`
- `listTools()` returns a non-zero tool count
- at least one safe direct execution succeeds end-to-end

If any one of these is missing, the page is not operationally ready for WebMCP-backed control.

## Dashboard And Operator Guidance

For dashboards and operator apps:

- keep mutations script-backed and auditable
- expose only allowlisted actions
- mirror those allowlisted actions into WebMCP tools
- include one safe probe tool
- surface readiness and failure states in the UI
- treat direct execution as the gate for operator use

Good operator pattern:

- backend action broker owns mutations
- page registers matching WebMCP tools
- readiness gate proves both registration and direct execution
- operator only acts through the page after that gate passes

## Troubleshooting

- `navigator.modelContext` missing:
  - the current Chrome session does not have WebMCP testing enabled
  - the browser was not relaunched after enabling the flag
  - the launcher did not pass `--enable-features=WebMCPTesting`
- `navigator.modelContext` exists but `navigator.modelContextTesting` does not:
  - registration support is visible, but the testing/execution surface is not
  - do not claim direct operability
- `WEBMCP ready (N)` shown but direct execution fails:
  - inspect `navigator.modelContextTesting`, not only `navigator.modelContext`
  - the page may be registering tools while the testing surface is unavailable or broken
- `listTools()` returns `0`:
  - the page did not actually register tools in the current session
- `executeTool(...)` fails with parse errors:
  - pass a JSON string like `"{}"` instead of a raw object
- browser control works but WebMCP does not:
  - Chrome DevTools/browser automation is not the same thing as WebMCP

## Early Preview Caution

Do not trust docs alone. Chrome's early-preview runtime can drift from the public write-up.

Example:

- docs may say some methods were removed
- your live runtime may still expose them

Always capability-check the active browser session before making claims about readiness.

## Expected Result

- the app registers tools deterministically
- readiness is truthful and runtime-proven
- direct execution is validated through `navigator.modelContextTesting`
- dashboards can be safely operated through WebMCP once the gate passes
- troubleshooting follows runtime evidence, not assumptions
