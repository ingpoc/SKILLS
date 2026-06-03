---
name: mcp-setup
description: "Use when setting up MCP servers for the first time or verifying MCP configuration. Runtime-aware: writes Claude .mcp.json or Codex .codex/config.toml, referencing central mcp-servers only (no per-project cloning)."
---

# MCP Setup

Configure required MCP servers with a single global server codebase and project-local config.

## Required MCP Servers

| Server | Purpose | API Key |
|--------|---------|---------|
| `token-efficient` | CSV/log processing, sandbox execution (98% token savings) | None |
| `context-graph` | Semantic decision trace search | Voyage AI |

## Design Rules

- Do **not** clone MCP servers into each project.
- Use one central server root (default: `$HOME/Documents/remote-claude/mcp-servers`).
- Write runtime-specific config in project:
  - Claude: `.mcp.json`
  - Codex: `.codex/config.toml`
- Keep state local to project (e.g., context-graph project_dir -> `<project>/.traces`).
- Never write raw secrets into project config; use env placeholders.

## Quick setup

```bash
cd /path/to/project
bash ~/.claude/skills/mcp-setup/scripts/setup-all.sh
```

## Verification

```bash
bash ~/.claude/skills/mcp-setup/scripts/verify-setup.sh
```

## Optional environment

- `MCP_SERVERS_ROOT` (default: `$HOME/Documents/remote-claude/mcp-servers`)
- `MCP_RUNTIME` (`codex` or `claude`; auto-detected if unset)

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/setup-all.sh` | Runtime-aware setup without cloning |
| `scripts/verify-setup.sh` | Verify config and server paths |
| `scripts/install-token-efficient.sh` | Legacy helper (optional) |
