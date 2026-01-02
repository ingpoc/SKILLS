---
name: project
description: {{PROJECT_DESCRIPTION}}
keywords: {{KEYWORDS}}
project_type: {{PROJECT_TYPE}}
framework: {{FRAMEWORK}}
---

# {{PROJECT_NAME}}

**Purpose**: {{PROJECT_PURPOSE}}

---

## Project Overview

| Aspect | Details |
|--------|---------|
| **Type** | {{PROJECT_TYPE}} |
| **Framework** | {{FRAMEWORK}} |
| **Language** | {{LANGUAGE}} |
| **Testing** | {{TEST_FRAMEWORK}} |

---

## Architecture

### Tech Stack

| Layer | Technology |
|-------|------------|
{{TECH_STACK_ROWS}}

### Project Structure

| Directory | Purpose |
|-----------|---------|
{{PROJECT_STRUCTURE_ROWS}}

---

## Common Commands

| Task | Command |
|------|---------|
{{COMMAND_ROWS}}

---

## Config Files

| File | Purpose |
|------|---------|
| `.claude/config/project.json` | Project settings |
| `.claude/progress/state.json` | Current state |
| `.claude/progress/feature-list.json` | Features |
| `.mcp.json` | MCP server configuration |
{{ADDITIONAL_CONFIG_FILES}}

---

## MCP Servers

{{MCP_SERVERS_SECTION}}

---

## Development Workflow

{{WORKFLOW_SECTION}}
