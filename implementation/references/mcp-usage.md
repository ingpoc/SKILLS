# MCP Usage Patterns

## Token Efficiency Principle

From [Anthropic Code Execution](https://www.anthropic.com/engineering/code-execution-with-mcp):

> "Process data in sandbox, return summary. Never load raw data into context."

## When to Use MCP vs Direct Tools

| Task | Direct Tool | MCP Tool | Why |
|------|-------------|----------|-----|
| Read small file (<100 lines) | Read | - | Direct is simpler |
| Read large file (>100 lines) | - | execute_code | Token savings |
| Search code | Grep | - | Grep is optimized |
| Process CSV | - | process_csv | 99% token savings |
| Analyze logs | - | process_logs | Filter in sandbox |
| Run tests | Bash | - | Need full output |
| Health check | Bash | - | Simple output |

## MCP Tool Patterns

### 1. CSV Processing

```python
# BAD: Load all data into context
data = read_file("users.csv")  # 10K rows = 50K tokens
analyze(data)

# GOOD: Process in sandbox
result = mcp__token_efficient__process_csv(
    file_path="users.csv",
    columns=["email", "status"],
    filter_expr="status == 'active'",
    limit=10,
    response_format="summary"
)
# Returns: ~200 tokens with stats + sample
```

### 2. Log Analysis

```python
# BAD: Read entire log
logs = read_file("app.log")  # 100K lines = disaster

# GOOD: Filter in sandbox
result = mcp__token_efficient__process_logs(
    file_path="app.log",
    pattern="ERROR|CRITICAL",
    context_lines=2,
    limit=20,
    response_format="summary"
)
# Returns: Error patterns + sample matches
```

### 3. Code Execution

```python
# BAD: Multiple tool calls
file1 = read_file("data1.json")
file2 = read_file("data2.json")
# Now analyze both in context...

# GOOD: Single execution
result = mcp__token_efficient__execute_code(
    language="python",
    code="""
import json

with open('data1.json') as f:
    data1 = json.load(f)
with open('data2.json') as f:
    data2 = json.load(f)

# Analyze in sandbox
common_keys = set(data1.keys()) & set(data2.keys())
print(f"Common keys: {len(common_keys)}")
print(f"Sample: {list(common_keys)[:5]}")
""",
    response_format="summary"
)
```

### 4. Heredoc Support

```python
# Complex bash scripts with heredocs
result = mcp__token_efficient__execute_code(
    language="bash",
    code="""
cat <<EOF > config.json
{
  "server": "localhost",
  "port": 8000
}
EOF

cat config.json | jq '.port'
"""
)
```

## Tool Search Pattern (defer_loading)

From [Anthropic Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use):

### Configuration

```json
{
  "tools": [
    {"name": "Read", "defer_loading": false},
    {"name": "Write", "defer_loading": false},
    {"name": "Edit", "defer_loading": false},
    {"name": "Bash", "defer_loading": false},
    {"name": "Grep", "defer_loading": false},

    {"name": "mcp__browser__screenshot", "defer_loading": true},
    {"name": "mcp__browser__click", "defer_loading": true},
    {"name": "mcp__csv__process", "defer_loading": true},
    {"name": "mcp__logs__analyze", "defer_loading": true}
  ]
}
```

### Usage Flow

```
1. Start with core tools only (~2K tokens)
2. When browser testing needed:
   - Search: "browser screenshot click"
   - Load: browser tools (~500 tokens)
3. When CSV needed:
   - Search: "csv process filter"
   - Load: csv tools (~300 tokens)

Total: ~3K tokens vs ~20K (85% savings)
```

## Response Format Guidelines

| Format | Use When | Output |
|--------|----------|--------|
| `summary` | Discovery, quick check | Stats + 5 sample rows |
| `full` | Need all data for processing | All matching data |
| `json` | Structured processing | Parsed JSON |
| `markdown` | Human-readable report | Formatted tables |

## Pagination for Large Results

```python
# First call: Get overview
result1 = mcp__token_efficient__process_csv(
    file_path="large.csv",
    limit=100,
    offset=0,
    response_format="summary"
)
# Shows: Total 50K rows, first 100

# Second call: Get specific range
result2 = mcp__token_efficient__process_csv(
    file_path="large.csv",
    filter_expr="status == 'error'",
    limit=50,
    offset=0
)
# Shows: Only errors, first 50
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Read large file directly | Context bloat | Use execute_code |
| Load all CSV data | Token waste | Use filter + limit |
| Multiple file reads | Slow, expensive | Batch in sandbox |
| No response_format | Verbose output | Specify "summary" |
| Ignore pagination | Miss data | Use offset/limit |

## MCP Tool Quick Reference

| Tool | Purpose | Key Params |
|------|---------|------------|
| `execute_code` | Run Python/Bash/Node | language, code, timeout |
| `process_csv` | Filter/aggregate CSV | file_path, filter_expr, columns |
| `process_logs` | Search log patterns | file_path, pattern, context_lines |
| `search_tools` | Find available tools | query, category |
| `batch_process_csv` | Multiple files | file_paths, aggregate |
