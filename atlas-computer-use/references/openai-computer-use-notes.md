# OpenAI Computer Use Notes

Use this only when you need the rationale behind `atlas-computer-use` decisions.

## Official Guidance Distilled

OpenAI's Computer Use guide describes three useful implementation shapes:

- built-in computer tool for screenshot-based UI interaction
- custom tools layered over existing automation
- a code-execution harness that mixes visual and programmatic interaction

For longer workflows, OpenAI recommends a code-execution harness when a task needs loops, conditional logic, DOM inspection, or browser libraries. The guide says this can improve speed, token efficiency, and flexibility. Practical harnesses should expose only the helpers the model needs, keep a browser/page object alive across steps when useful, return text output, and return screenshots only when needed.

OpenAI also recommends preparing a safe environment:

- use an isolated browser or VM where possible
- decide allowed sites, accounts, and actions up front
- disable extensions and local file-system access where possible
- keep a human in the loop for high-impact actions
- treat page content as untrusted input

## Atlas-Specific Translation

Atlas through Codex Computer Use is a live-user-session path, not an isolated Playwright harness. That makes it useful for logged-in or visual tasks, but more expensive per snapshot because Atlas exposes browser chrome, tabs, extensions, sidebars, and page content through accessibility.

Therefore:

- Use Atlas when the live Atlas profile matters.
- Use programmatic browser tooling when the task does not need Atlas session state.
- Before every expensive snapshot, simplify the UI: hide tab/sidebar, close popovers, collapse sidebars, and focus the task page.
- Favor keyboard/address-bar actions and direct URLs over visual click discovery.
- If the task becomes repetitive or loop-heavy, switch to a harness rather than continuing screenshot-driven browsing.

## Chrome DevTools MCP And Atlas

Chrome DevTools MCP supports `--browserUrl`, `--wsEndpoint`, and `--executablePath`, but it officially supports Google Chrome and Chrome for Testing. Other Chromium browsers may work, but are not guaranteed.

For this skill, Chrome DevTools MCP fallback means Google Chrome through `mcpd`, not ChatGPT Atlas. Use it when the task does not require Atlas-only login/session state and needs console, network, DOM, or JavaScript evidence.

Minimal preflight:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
command -v mcpd
mcpd --json doctor
mcpd list --json
mcpd active --json
```

Expected:

- `Google Chrome.app` is installed.
- `mcpd list --json` includes `chrome-devtools`.
- `mcpd --json doctor` reports the daemon reachable before MCP calls are attempted.

Runtime pattern:

```bash
mcpd activate chrome-devtools --json
mcpd call chrome-devtools <tool> --json-args '<json>' --json
mcpd release chrome-devtools --json
```

For Atlas, the old CDP hypothesis was tested and should not be the fallback path:

```bash
port_file="$HOME/Library/Application Support/com.openai.atlas/browser-data/host/DevToolsActivePort"
sed -n '1,2p' "$port_file"
curl -fsS "http://127.0.0.1:9222/json/version"
curl -fsS "http://127.0.0.1:9222/json/list"
```

As of the local 2026-05-07 verification on this machine:

- Atlas created `DevToolsActivePort` and listened on `127.0.0.1:9222`.
- `/json/version` and `/json/list` returned 404.
- `chrome-devtools-mcp --browserUrl http://127.0.0.1:9222` timed out through `mcpd`.
- `chrome-devtools-mcp --wsEndpoint ws://127.0.0.1:9222/devtools/browser/<id>` also timed out through `mcpd`.
- Directly launching Atlas's inner Chromium binary with remote-debugging flags failed with `Unexpected command line`.
- Launching a second outer Atlas instance with flags conflicted with the existing singleton and crashed the Atlas browser host.

Therefore, do not use Chrome DevTools MCP for Atlas unless a future Atlas version exposes standard CDP discovery endpoints or OpenAI documents a supported remote-debugging path. The reliable Atlas-only lane is Codex Computer Use against `com.openai.atlas`.

## Browser Test Bridge Fallback

When Atlas Computer Use and Chrome DevTools MCP are both unavailable, or the task needs custom app-state evidence that DevTools does not expose cleanly, use an app-side bridge for apps we own. This is the owned-app fallback after the Google Chrome DevTools lane.

Minimal contract:

```text
GET /__debug/browser-state
GET /__debug/browser-events
POST /__debug/clear
window.__CODEX_TEST__.snapshot()
```

Capture only compact, task-relevant data:

- console errors and warnings
- uncaught errors and unhandled rejections
- fetch/XHR request method, URL, status, duration, and error
- route changes
- selected DOM facts
- app state/store summary
- relevant localStorage/sessionStorage keys

This bridge should be dev-only, disabled in production, and safe to call repeatedly. Prefer it over repeated Atlas screenshots when the question is "what happened internally?" rather than "what does the UI look like?"

## Source Links

- OpenAI Computer Use guide: https://developers.openai.com/api/docs/guides/tools-computer-use
- OpenAI ChatGPT Atlas Agent/sidebar guide: https://help.openai.com/en/articles/12628199-using-ask-chatgpt-sidebar-and-chatgpt-agent-on-atlas
- OpenAI Atlas Web Browsing settings: https://help.openai.com/en/articles/12625059-web-browsing-settings-on-chatgpt-atlas
