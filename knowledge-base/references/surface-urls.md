# Surface URL Map

Canonical per-feature docs URLs for the six surfaces this skill maintains. Used by Phase A (delta detection — fetch overview/whats-new) and Phase B (per-article source_url citation).

**Verified against:** Python SDK 0.2.85, Claude CLI 2.1.148, Codex CLI 0.133.0 on 2026-05-22.

When URLs move, update this file FIRST, then re-run the skill. Stale URLs in this map will propagate to article frontmatter and break re-verification.

## Surface 1 — Claude Code

**Surface overview:** `https://code.claude.com/docs/en/overview`
**What's New (delta source):** `https://code.claude.com/docs/en/whats-new`
**Rubric slug:** `claude-code-rubric`

| Feature | Canonical URL |
|---|---|
| Hooks | `/docs/en/hooks` |
| Sub-agents | `/docs/en/sub-agents` |
| MCP | `/docs/en/mcp` |
| Permission modes | `/docs/en/permission-modes` |
| Memory / CLAUDE.md | `/docs/en/memory` |
| Auto memory | `/docs/en/memory#auto-memory` |
| Routines | `/docs/en/routines` |
| Skills | `/docs/en/skills` |
| Plugins | `/docs/en/plugins` |
| Sessions | `/docs/en/sessions` |
| Context window | `/docs/en/context-window` |
| Prompt caching | `/docs/en/prompt-caching` |
| Agent view (`claude agents`) | `/docs/en/agent-view` |
| CLI reference | `/docs/en/cli-reference` |
| Monitor tool | `/docs/en/monitor` |
| Computer use | `/docs/en/computer-use` |
| Ultrareview | `/docs/en/ultrareview` |
| Ultraplan | `/docs/en/ultraplan` |
| Auto mode | `/docs/en/auto-mode` |
| Sandboxing | `/docs/en/sandboxing` |
| Worktrees | `/docs/en/worktrees` |
| Checkpointing / rewind | `/docs/en/checkpointing` |
| Output styles | `/docs/en/output-styles` |
| Effort level | `/docs/en/effort` |
| Channels | `/docs/en/channels` |
| Agent teams | `/docs/en/agent-teams` |
| Managed MCP | `/docs/en/managed-mcp` |
| GitHub actions | `/docs/en/github-actions` |
| Slash commands | `/docs/en/slash-commands` |
| `/goal` command | `/docs/en/whats-new` (Week 20 section — may move) |

Prefix all relative paths with `https://code.claude.com`.

## Surface 2 — Claude Agent SDK (Python + TypeScript)

**Surface overview:** `https://code.claude.com/docs/en/agent-sdk/overview`
**Python CHANGELOG (delta source):** `https://raw.githubusercontent.com/anthropics/claude-agent-sdk-python/main/CHANGELOG.md`
**TypeScript CHANGELOG (delta source):** `https://raw.githubusercontent.com/anthropics/claude-agent-sdk-typescript/main/CHANGELOG.md`
**Rubric slug:** `claude-agent-sdk-rubric`

| Feature | Canonical URL |
|---|---|
| Quickstart | `/docs/en/agent-sdk/quickstart` |
| Python reference | `/docs/en/agent-sdk/python` |
| TypeScript reference | `/docs/en/agent-sdk/typescript` |
| Hooks | `/docs/en/agent-sdk/hooks` |
| Subagents | `/docs/en/agent-sdk/subagents` |
| MCP servers | `/docs/en/agent-sdk/mcp` |
| Permissions / `can_use_tool` | `/docs/en/agent-sdk/permissions` |
| Sessions / resume | `/docs/en/agent-sdk/sessions` |
| Skills | `/docs/en/agent-sdk/skills` |
| Slash commands | `/docs/en/agent-sdk/slash-commands` |
| System prompts | `/docs/en/agent-sdk/modifying-system-prompts` |
| Plugins | `/docs/en/agent-sdk/plugins` |
| AskUserQuestion / user-input | `/docs/en/agent-sdk/user-input` |
| Cost tracking | `/docs/en/agent-sdk/cost-tracking` |
| Custom tools | `/docs/en/agent-sdk/custom-tools` |
| File checkpointing | `/docs/en/agent-sdk/file-checkpointing` |
| Hosting / deployment | `/docs/en/agent-sdk/hosting` |
| Session storage | `/docs/en/agent-sdk/session-storage` |
| Tool search | `/docs/en/agent-sdk/tool-search` |
| Troubleshooting | `/docs/en/agent-sdk/troubleshooting` |

Prefix all relative paths with `https://code.claude.com`.

**Recent SDK additions to watch (as of 0.2.85, 2026-05-22):** Track CHANGELOG for new options, callbacks, message types, and error literals. Specifically watch for additions to: `ClaudeAgentOptions`, `AgentDefinition`, `ResultMessage`, `AssistantMessage`, `RateLimitEvent`, hook event types, `AssistantMessageError` literals.

## Surface 3 — Claude Managed Agents

**Surface overview:** `https://platform.claude.com/docs/en/managed-agents/overview`
**Rubric slug:** `claude-managed-agents-rubric`

| Capability | Canonical URL |
|---|---|
| Overview + 4-concept model | `/docs/en/managed-agents/overview` |
| Quickstart | `/docs/en/managed-agents/quickstart` |
| Sessions API | `/docs/en/managed-agents/sessions` |
| Self-hosted sandboxes | `/docs/en/managed-agents/self-hosted-sandboxes` |
| Environments | `/docs/en/managed-agents/environments` |
| Tools | `/docs/en/managed-agents/tools` |
| Events / SSE streaming | `/docs/en/managed-agents/sessions` (events section) |
| Webhooks | `/docs/en/managed-agents/webhooks` |
| Memory store | `/docs/en/managed-agents/memory` |
| Dreaming | `/docs/en/managed-agents/dreams` |
| MCP tunnels | `/docs/en/agents-and-tools/mcp-tunnels/overview` |
| Vaults (OAuth) | `/docs/en/managed-agents/vaults` |
| Multi-agent | `/docs/en/managed-agents/multi-agent` |
| Define outcomes | `/docs/en/managed-agents/define-outcomes` |
| Skills (Managed flavor) | `/docs/en/managed-agents/skills` |
| Rate limits | `/docs/en/api/rate-limits` |

Prefix all relative paths with `https://platform.claude.com`.

**Beta header:** All requests to Managed Agents require `managed-agents-2026-04-01`. SDKs set automatically. May change at GA.

## Surface 4 — OpenAI Codex SDK / Codex CLI

**Surface overview:** `https://developers.openai.com/codex`
**GitHub releases (delta source):** `https://github.com/openai/codex/releases` (or `.../releases.atom` for feed)
**GitHub README:** `https://github.com/openai/codex/blob/main/README.md`
**Rubric slug:** `codex-sdk-rubric`

| Capability | Canonical URL |
|---|---|
| CLI install & setup | `https://github.com/openai/codex/blob/main/README.md` (install section) |
| Authentication | `https://developers.openai.com/codex/auth` |
| CLI overview | `https://developers.openai.com/codex/cli` |
| CLI command reference | `https://developers.openai.com/codex/cli/reference` |
| Slash commands | `https://developers.openai.com/codex/cli/slash-commands` |
| Config file | `https://developers.openai.com/codex/config` |
| IDE extensions | `https://developers.openai.com/codex/ide` |
| Enterprise access tokens | `https://developers.openai.com/codex/enterprise/access-tokens` |
| Use cases | `https://developers.openai.com/codex/use-cases` |
| Cookbook (Codex recipes) | `https://developers.openai.com/cookbook/topic/codex` |
| `codex exec` non-interactive | `https://developers.openai.com/codex/cli/reference` (exec section) |
| MCP support | `https://developers.openai.com/codex/config` (mcp section) |
| Credential storage | `https://developers.openai.com/codex/auth` (credential cache section) |

URLs at `developers.openai.com/codex/...` move occasionally. Re-verify when ingesting; check GitHub README for canonical pointers.

**Watch for:** new releases land roughly weekly; the autonomous-agent-builder Codex SDK lane uses bundled Codex binary, so version pin matters.

## Surface 5 — OpenAI API platform (Responses API + GPT-5.x)

**Surface overview:** `https://developers.openai.com/api/docs`
**Rubric slug:** `openai-api-rubric`

The OpenAI model API *beneath* Codex — the autonomous-agent-builder `codex_sdk` lane runs on it. Codex-CLI/SDK-specific features stay in Surface 4; this surface is the model API, Responses API, and platform features.

| Feature | Canonical URL |
|---|---|
| Prompt guidance (GPT-5.x, `reasoning_effort`, `text.verbosity`, `phase`) | `/api/docs/guides/prompt-guidance` |
| Computer use tool | `/api/docs/guides/tools-computer-use` |
| WebSocket mode (Responses API) | `/api/docs/guides/websocket-mode` |
| Webhooks | `/api/docs/guides/webhooks` |
| Cost optimization (Batch, Flex, model selection) | `/api/docs/guides/cost-optimization` |

Prefix all relative paths with `https://developers.openai.com`.

**Watch for:** GPT-5.x model controls evolve; the Responses API (`/v1/responses`) is the primary agentic endpoint. No automated delta source wired yet — audit manually against the overview page.

## Surface 6 — Agent Skills (open SKILL.md format)

**Surface overview:** `https://agentskills.io/specification`
**Docs index (delta source):** `https://agentskills.io/llms.txt`
**Reference library:** `https://github.com/agentskills/agentskills` (`skills-ref validate`)
**Rubric slug:** `agent-skills-rubric`

The vendor-neutral Agent Skills standard — the `SKILL.md` format itself, portable across Claude Code, OpenAI Codex, and GitHub Copilot. This surface owns the *format and authoring discipline*; product-specific skill hosting stays in the respective product rubric.

| Page | Canonical URL |
|---|---|
| Specification (SKILL.md format) | `/specification` |
| Quickstart | `/skill-creation/quickstart` |
| Best practices | `/skill-creation/best-practices` |
| Optimizing descriptions | `/skill-creation/optimizing-descriptions` |
| Evaluating skills | `/skill-creation/evaluating-skills` |
| Using scripts | `/skill-creation/using-scripts` |

Prefix all relative paths with `https://agentskills.io`.

**Watch for:** `https://agentskills.io/llms.txt` lists all pages — diff it against ingested articles to spot new guides. No version feed; audit manually.

## Maintenance

If any URL 404s during a refresh:

1. Try the surface overview page (may have moved the section).
2. Try GitHub README anchor for OpenAI surfaces; search the docs site for Anthropic surfaces.
3. If genuinely removed: mark `not-found` in the audit notes, exclude from this run's gap list, and update this map.
4. Don't ingest articles with broken URLs — fix or skip.
