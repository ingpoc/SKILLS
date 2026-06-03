---
name: project
description: $PROJECT_NAME - $PROJECT_TYPE project
keywords: $PROJECT_TYPE, $FRAMEWORK, claude
project_type: $PROJECT_TYPE
framework: $FRAMEWORK
---

# $PROJECT_NAME

**Purpose**: $PROJECT_TYPE project built with $FRAMEWORK.

---

## Project Overview

| Aspect | Details |
|--------|---------|
| **Type** | $PROJECT_TYPE |
| **Framework** | $FRAMEWORK |
| **Language** | $LANGUAGE |
| **Package Manager** | $PKG_MGR |

---

## Commands

| Task | Command |
|------|---------|
| Health check | `.claude/scripts/health-check.sh` |
| Restart server | `.claude/scripts/restart-servers.sh` |
| Run tests | `.claude/scripts/run-tests.sh` |
| Check state | `.claude/scripts/check-state.sh` |
| Get feature | `.claude/scripts/get-current-feature.sh` |
| Mark complete | `.claude/scripts/mark-feature-complete.sh <id> implemented` |

---

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `.claude/` | Agent configuration |
| `.claude/config/` | Project settings |
| `.claude/progress/` | State & feature tracking |
| `.claude/scripts/` | Automation scripts |
| `.claude/hooks/` | Project hooks |
| `src/` | Source code |
| `public/` | Static assets |

---

## State Machine

| State | Next | Skill |
|-------|------|-------|
| START | INIT | orchestrator |
| INIT | IMPLEMENT | initialization |
| IMPLEMENT | TEST | implementation |
| TEST | COMPLETE | testing-tracker → testing |
| COMPLETE | IMPLEMENT | context-graph (if done) |

---

## MCP Tools

| Server | Tools |
|--------|-------|
| token-efficient | execute_code, process_csv, process_logs |
| context-graph | context_store_trace, context_query_traces |

---

## Features

See `.claude/progress/feature-list.json` for implementation status.
