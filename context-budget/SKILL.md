---
name: context-budget
description: Analyze and report what is consuming the 200K context window. Use when the user says /context-budget, "what's eating my context", "how much context am I using", or wants to optimize token usage.
model: haiku
effort: low
allowed-tools: Read, Glob, Bash
---

# Context Budget: Audit Context Window Consumption

**EXECUTE this skill now.** Follow the workflow steps below using the provided $ARGUMENTS. Do NOT describe, summarize, or explain this skill — run it.

## Constants

- `CONTEXT_LIMIT`: 200,000 tokens
- `CLAUDE_DIR`: `C:/Users/gurusharan.gupta/.claude`
- `REGISTRY_DIR`: `C:/Users/gurusharan.gupta/Agents/Claude Code`

## Workflow

### Step 1: Scan Always-Loaded Components

These are loaded in every session:

1. **Global CLAUDE.md** — read `~/.claude/CLAUDE.md`, count words × 1.3
2. **Project CLAUDE.md** — check for CLAUDE.md in the current working directory if present

### Step 2: Scan Installed Skills

List all installed skills and their sizes:
```bash
wc -w ~/.claude/skills/*/SKILL.md 2>/dev/null
```

Note which have `context: fork` (safe — only final output enters main ctx) vs those without (full content enters main ctx on trigger).

### Step 3: Scan MCP Servers

Read `~/.claude/.mcp.json` if it exists. Each active MCP server contributes tool definitions to the context. Estimate 200-500 tokens per MCP server for tool schema overhead.

### Step 4: Scan Memory Files

Check for auto-memory files:
```bash
ls ~/.claude/projects/*/memory/*.md 2>/dev/null | head -20
```
Count words × 1.3 for any that exist.

### Step 5: Scan Active Plugins

List enabled plugins from `~/.claude/settings.json`. Estimate 100-300 tokens per plugin for description overhead.

### Step 6: Produce Report

Output:

```
## Context Budget Report

**Context Limit:** 200,000 tokens

### Always-Loaded Components
| Component | Est. Tokens | Notes |
|-----------|-------------|-------|
| Global CLAUDE.md | <n> | Always loaded |
| Project CLAUDE.md | <n> / N/A | If present |
| Memory files | <n> | Auto-memory entries |
| **Subtotal** | **<n>** | |

### Skills (on-trigger)
| Skill | Est. Tokens | context:fork? | Risk |
|-------|-------------|---------------|------|
| <skill> | <n> | Yes/No | Low/High |
...

### MCP Servers (tool schema overhead)
| Server | Est. Tokens |
|--------|-------------|
| <name> | ~200-500 |
...

### Active Plugins
| Plugin | Est. Tokens |
|--------|-------------|
...

### Summary
- **Always-loaded baseline:** <n> tokens (<n>% of limit)
- **Highest-risk skills (no context:fork):** <list>
- **MCP overhead:** <n> tokens across <count> servers

### Top 3 Optimizations
1. <highest-impact action> — saves ~<n> tokens
2. <second action> — saves ~<n> tokens
3. <third action> — saves ~<n> tokens
```
