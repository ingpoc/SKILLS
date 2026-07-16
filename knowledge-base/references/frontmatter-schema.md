# KB Article Schema Reference

Source of truth: `~/.claude/bin/workflow_knowledge.py` — `GLOBAL_KB_REQUIRED_FRONTMATTER` constant.

## Required frontmatter fields

```yaml
---
title: <full sentence, ~10-15 words, durable takeaway not just feature name>
source_url: <per-feature URL, must resolve at ingest time>
source_title: <e.g., "Claude Agent SDK Documentation", "Codex Documentation">
source_author: <"Anthropic" or "OpenAI">
date_published: <YYYY-MM-DD or "unknown" — required even if unknown>
date_processed: <YYYY-MM-DD when article was written>
tags: [<2-4 from existing taxonomy>]
---
```

**All seven fields are required.** Lint `--strict` fails articles missing any of them. The most-commonly-omitted field is `date_published: unknown` (writers assume it's optional because the value is "unknown").

## Required sections

The body MUST have exactly these three section headers, in this order:

```markdown
## Insight

<1-2 sentences. What is this lever? WHEN does it apply? Concrete, not abstract.>

## Evidence

<1-3 sentences. Cite the source with quoted/specific content. Show option keys/method names inline.>

## Applicability

<2-4 sentences. How should a coding agent change behavior? Tie to use cases where relevant. End with use-when/don't-use-when guideline.>
```

### Optional sub-section for consolidated changelog articles

For articles that consolidate multiple releases (e.g., "Changelog 2.1.174–2.1.191"), an additional `## Security & Breaking Changes` section MAY be inserted between `## Evidence` and `## Applicability`:

```markdown
## Security & Breaking Changes

**Breaking:** <List any removed APIs, changed defaults, or workflow-breaking changes.>

**Security additions:** <List new security features, permission changes, or guardrails.>
```

This section is OPTIONAL and should only be used when the consolidated period contains security or breaking changes that operators must act on.

Legacy aliases accepted (don't use in new articles):
- `## Application` → aliased to `## Applicability`
- `## Application to Control Plane` → aliased to `## Applicability`

## Tag taxonomy (existing 18 tags as of 2026-05-22)

Pick 2–4 tags per article from this list. Do NOT introduce new tags without user confirmation.

| Tag | Use for |
|---|---|
| `agents` | Anything about agent behavior, runtime, orchestration. Default tag for most KB articles. |
| `architecture` | System design patterns, foundational concepts, structural decisions. |
| `tools` | Tool/skill design, MCP, integrations, CLI tooling. |
| `workflows` | Multi-step procedures, automation, process design. |
| `context-engineering` | Context window, prompt design, retrieval, cache strategy. |
| `performance` | Latency, throughput, token efficiency, optimization. |
| `evaluation` | Eval design, metrics, rubrics, success criteria. |
| `safety` | Security, guardrails, permissions, sandboxing, auth. |
| `coding-agents` | Code generation, manipulation, IDE integration agents. Use for SDK articles. |
| `prompting` | Prompt engineering techniques. |
| `multi-agent` | Multi-agent orchestration, coordinator patterns, agent teams. |
| `session-persistence` | Session state management, resume, cross-session memory. |
| `mcp` | Model Context Protocol specifics. |
| `process` | Team/workflow processes (less common). |
| `quality-gates` | Quality gate design (less common). |
| `harness-design` | Harness/eval infrastructure (less common). |
| `eval-design` | Evaluation infrastructure (less common). |

**Per-surface tag combinations that work well:**

- Claude Agent SDK lever article → `[agents, coding-agents, <one more: tools | safety | architecture | mcp | performance>, <optional 4th>]`
- Claude Code feature article → `[tools, agents, <one more: architecture | safety | workflows | context-engineering>]`
- Managed Agents capability article → `[agents, <safety | architecture | mcp | multi-agent | workflows>, ...]`
- Codex SDK article → `[agents, coding-agents, <tools | safety | architecture | mcp | workflows>]`

## Title patterns

**Good titles** state the durable takeaway as a full sentence:

- ✅ "ClaudeSDKClient maintains session context across multiple query() calls — use for multi-turn agent workflows"
- ✅ "can_use_tool callback gates tool execution at the SDK boundary with typed permission decisions"
- ✅ "RateLimitEvent in message stream provides typed rate-limit status without string parsing"
- ✅ "Codex `exec` runs non-interactively for CI/CD and scripted automation"

**Bad titles** are just feature names:

- ❌ "ClaudeSDKClient"
- ❌ "can_use_tool"
- ❌ "RateLimitEvent"
- ❌ "Codex exec"

## Title length and slug derivation

Ingest derives the article slug from the title:

- Lowercases, replaces non-alphanumeric with `-`, deduplicates `-`, truncates to ~55 chars after date prefix.
- "Claude Agent SDK lever rubric — first-stop index of every option..." → `claude-agent-sdk-lever-rubric-first-stop-index-of-every-opti` (truncated).
- "Claude Agent SDK rubric" → `claude-agent-sdk-rubric` (predictable).

**For rubric articles, use short titles** so the slug is predictable (triggers in `~/.claude/CLAUDE.md` reference these slugs):

- `Claude Agent SDK rubric`
- `Claude Code rubric`
- `Claude Managed Agents rubric`
- `Codex SDK rubric`

For lever articles, descriptive long titles are fine — the slug will be auto-truncated but search-discoverable.

## Length target

200–600 words per article. The vast majority should be 250–400.

- `## Insight` — 50–100 words
- `## Evidence` — 50–150 words
- `## Applicability` — 80–200 words

If you can't say it in 600 words, you're trying to cover two levers in one article. Split.

## Example complete article

```markdown
---
title: can_use_tool callback gates tool execution at the SDK boundary with typed permission decisions
source_url: https://code.claude.com/docs/en/agent-sdk/permissions
source_title: Claude Agent SDK Documentation
source_author: Anthropic
date_published: unknown
date_processed: 2026-05-22
tags: [agents, coding-agents, safety, tools]
---

## Insight

The `can_use_tool: CanUseTool` callback in `ClaudeAgentOptions` is called by the SDK when a tool use is not auto-approved by allow rules or permission modes. Return `PermissionResultAllow(updated_input=...)` to approve (optionally modifying the input), or `PermissionResultDeny(message="...", interrupt=False)` to block. This is a type-safe, synchronous gate that enforces tool permissions stronger than prompt constraints — Claude cannot override or bypass it.

## Evidence

The SDK documentation specifies: "If not resolved by any of the [permission checks], call your `canUseTool` callback for a decision." The callback receives the tool name, input arguments, and session context. Return type is `PermissionResult`, with typed variants: `PermissionResultAllow` for approval (with optional `updated_input`), `PermissionResultDeny` for rejection (with required `message` and optional `interrupt` flag). The callback is only called if the tool is not auto-approved by earlier checks (allowed_tools, permission modes, hooks).

## Applicability

In autonomous-agent-builder, use `can_use_tool` to serialize parallel subagent dispatch — gate certain tool combinations or workspace states at the SDK boundary before they reach the model. Example: deny Bash in code-gen phase if linters aren't installed, or deny Edit on locked files. This is more reliable than relying on tool-use prompts, which Claude may negotiate. Use it when you need to enforce preconditions (e.g., "only allow Write if the file is in a writable directory") or to prevent tool combinations that could deadlock. Don't use it for every tool call — that's what `allowed_tools` and `permission_mode="dontAsk"` are for. Pair with hooks when you need to modify input or log decisions.
```
