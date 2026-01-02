---
name: local
description: Quick reference for {{PROJECT_NAME}}
keywords: quick-ref, commands, state
---

# Quick Reference

## Purpose

{{PROJECT_PURPOSE_ONE_LINER}}

## Commands

| Task | Command |
|------|---------|
| Check state | `~/.claude/skills/orchestrator/scripts/check-state.sh` |
| Run tests | `~/.claude/skills/testing/scripts/run-unit-tests.sh` |
| Health check | `~/.claude/skills/implementation/scripts/health-check.sh` |
| Session entry | `~/.claude/skills/orchestrator/scripts/session-entry.sh` |
{{ADDITIONAL_COMMANDS}}

## State → Skill

| State | Skill |
|-------|-------|
| INIT | initialization/ |
| IMPLEMENT | implementation/ |
| TEST | testing/ |
| COMPLETE | context-graph/ |

## Config

| File | Purpose |
|------|---------|
| `.claude/config/project.json` | Project settings |
| `.claude/progress/state.json` | Current state |
| `.claude/progress/feature-list.json` | Features |
| `.mcp.json` | MCP servers |

## MCP Tools

**token-efficient**: `execute_code`, `process_csv`, `process_logs`
**context-graph**: `context_store_trace`, `context_query_traces`
