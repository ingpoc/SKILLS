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
| Check state | `.claude/scripts/check-state.sh` |
| Run tests | `.claude/scripts/run-tests.sh` |
| Health check | `.claude/scripts/health-check.sh` |
| Restart server | `.claude/scripts/restart-servers.sh` |
| Get feature | `.claude/scripts/get-current-feature.sh` |
{{ADDITIONAL_COMMANDS}}

## State → Skill

| State | Skill |
|-------|-------|
| START | orchestrator |
| INIT | initialization |
| IMPLEMENT | implementation |
| TEST | testing-tracker → testing |
| COMPLETE | context-graph or cycle to IMPLEMENT |

## Config

| File | Purpose |
|------|---------|
| `.claude/config/project.json` | Project settings |
| `.claude/progress/state.json` | Current state |
| `.claude/progress/feature-list.json` | Features |
| `.claude/progress/testing-list.json` | Browser test status |
| `.mcp.json` | MCP servers |

## MCP Tools

**token-efficient**: `execute_code`, `process_csv`, `process_logs`
**context-graph**: `context_store_trace`, `context_query_traces`
