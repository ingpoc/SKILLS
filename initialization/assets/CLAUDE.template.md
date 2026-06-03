# Quick Reference

Full orchestrator instructions are in `~/.claude/prompts/orchestrator.md`

## Common Commands

```bash
# Check current state
~/.claude/skills/orchestrator/scripts/check-state.sh

# Run tests (reads test_command from .claude/config/project.json)
~/.claude/skills/testing/scripts/run-unit-tests.sh

# Health check (reads health_check from config)
~/.claude/skills/implementation/scripts/health-check.sh

# Browser smoke test (reads dev_server_port from config)
~/.claude/skills/browser-testing/scripts/smoke-test.sh
```

## Session Entry

Run: `~/.claude/skills/orchestrator/scripts/session-entry.sh`

## State → Skill Mapping

| State | Skill |
|-------|-------|
| INIT | initialization/ |
| IMPLEMENT | implementation/ |
| TEST | testing/ |
| COMPLETE | context-graph/ |

## MCP Servers (Token Efficiency & Learning)

This project has two MCP servers configured in `.mcp.json`:

### token-efficient MCP
**Use for**: Large data processing (CSV, logs), code execution in sandbox

| Situation | Tool | Benefit |
|-----------|------|---------|
| File >50 lines | `process_logs` with pattern | 98% token savings |
| CSV files | `process_csv` with filter | Returns summary, not raw data |
| Multiple files | `batch_process_csv` | Batch processing |
| Execute code | `execute_code` | Sandbox execution |

**Examples**:
```python
# Instead of reading entire file
process_logs(file_path="file.txt", pattern="error", limit=10)

# Instead of reading CSV
process_csv(file_path="data.csv", filter_expr="price > 100", limit=5)
```

### context-graph MCP
**Use for**: Storing decisions, querying precedents, learning from history

| Situation | Tool | Benefit |
|----------|------|---------|
| Made technical decision | `context_store_trace` | Build institutional memory |
| Facing similar problem | `context_query_traces` | Find past decisions by meaning |
| Session complete | `context_list_categories` | Extract patterns |
| Repeating error | `context_query_traces` | Find how it was fixed |

**Examples**:
```python
# After choosing framework
context_store_trace(
    decision="Chose FastAPI over Flask for async support",
    category="framework"
)

# Before making decision
context_query_traces(query="web framework for high load API")
```

**Priority Rule**: Think before reading/executing - Can I use MCP servers instead?

## Config Files

- `.claude/config/project.json` - Project settings
- `.claude/progress/state.json` - Current state
- `.claude/progress/feature-list.json` - Features
- `.mcp.json` - MCP server configuration
