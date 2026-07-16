---
name: mcp-setup
description: "Add, inspect, authenticate, or remove MCP server registrations for the current Codex runtime. Use when the operator asks to configure an MCP server or diagnose whether a registered server is available. Do not clone server code into projects, assume every project needs the same servers, or manage app-specific business workflows."
allowed-tools: Bash Read
---

# MCP Setup

Use the Codex MCP registry as the configuration owner.

## Procedure

1. Inspect before changing: `codex mcp list`, then `codex mcp get <name>` when present.
2. Read `codex mcp add --help` for the installed runtime before constructing a registration.
3. Prefer a hosted HTTPS MCP endpoint when the provider supports it; otherwise register the smallest stable local command.
4. Reference secrets through environment variables. Never write raw credentials into a repository or print their values.
5. Register only the server requested or required by a verified workflow.
6. Verify with `codex mcp list` and a narrow capability call when available. Registration alone does not prove authentication or tool health.
7. Use `codex mcp login`, `logout`, or `remove` only for the named server and only within the operator's requested scope.

## Boundary

This skill owns Codex MCP registration and health checks. Individual MCP-backed skills own how their tools are used. Plugin installation and app connector setup use their own owners.
