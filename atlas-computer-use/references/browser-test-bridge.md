# Browser Test Bridge

Use this when Atlas is the only browser and the task needs browser-internal evidence that Computer Use cannot provide.

## When To Add It

Add a dev-only bridge when all are true:

- the app is owned by the user or this workspace
- the task needs console, network, error, storage, route, DOM, or app-state evidence
- Chrome DevTools/CDP is unavailable or not allowed
- repeated screenshots/accessibility snapshots would be noisy or expensive

Do not add it for third-party websites. Do not leave it enabled in production.

## Minimal Contract

Expose:

```text
GET /__debug/browser-state
GET /__debug/browser-events
POST /__debug/clear
window.__CODEX_TEST__.snapshot()
```

Validate with:

```bash
python /Users/gurusharan/.codex/skills/atlas-computer-use/scripts/validate_browser_bridge.py --base-url http://127.0.0.1:<port>
```

## What To Capture

Keep output compact and task-relevant:

- console warnings/errors
- `window.onerror`
- `unhandledrejection`
- fetch/XHR method, URL, status, duration, and error
- route changes
- selected DOM facts
- app state/store summary
- relevant localStorage/sessionStorage keys

## Browser Snippet

Use this as the client-side core, adapted to the app framework:

```js
(function installCodexTestBridge() {
  if (window.__CODEX_TEST__) return;
  const events = [];
  const push = (event) => {
    const item = { t: Date.now(), ...event };
    events.push(item);
    if (events.length > 200) events.shift();
    try {
      navigator.sendBeacon?.("/__debug/event", JSON.stringify(item));
    } catch {}
  };

  const originalError = console.error;
  const originalWarn = console.warn;
  console.error = (...args) => {
    push({ type: "console.error", args: args.map(String) });
    originalError.apply(console, args);
  };
  console.warn = (...args) => {
    push({ type: "console.warn", args: args.map(String) });
    originalWarn.apply(console, args);
  };

  window.addEventListener("error", (event) => {
    push({
      type: "window.onerror",
      message: event.message,
      source: event.filename,
      line: event.lineno,
    });
  });
  window.addEventListener("unhandledrejection", (event) => {
    push({ type: "unhandledrejection", reason: String(event.reason) });
  });

  const originalFetch = window.fetch;
  window.fetch = async (...args) => {
    const started = performance.now();
    const url = String(args[0]);
    try {
      const response = await originalFetch(...args);
      push({
        type: "fetch",
        url,
        status: response.status,
        ok: response.ok,
        durationMs: Math.round(performance.now() - started),
      });
      return response;
    } catch (error) {
      push({
        type: "fetch.error",
        url,
        error: String(error),
        durationMs: Math.round(performance.now() - started),
      });
      throw error;
    }
  };

  window.__CODEX_TEST__ = {
    events,
    clear: () => {
      events.length = 0;
    },
    snapshot: () => ({
      url: location.href,
      title: document.title,
      eventCount: events.length,
      latest: events.slice(-20),
      localStorageKeys: Object.keys(localStorage),
      sessionStorageKeys: Object.keys(sessionStorage),
    }),
  };
})();
```

## Server Endpoints

The server side can be framework-specific. The behavior should be:

- `POST /__debug/event`: append one JSON event to an in-memory ring buffer
- `GET /__debug/browser-events`: return `{ "events": [...] }`
- `GET /__debug/browser-state`: return a compact summary with `eventCount` and recent events
- `POST /__debug/clear`: clear the buffer and return `204`

Production guard examples:

- only register routes when `NODE_ENV !== "production"`
- or require `ENABLE_CODEX_BROWSER_BRIDGE=1`
- never include secrets, cookies, authorization headers, or full response bodies
