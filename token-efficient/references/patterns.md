# Token-Efficient Tool Patterns

Decision patterns for choosing the right token-efficient tool.

## Tool Selection Decision Tree

```
Need to process data?
│
├─ CSV files?
│  ├─ Single file?
│  │  ├─ < 10K rows → process_csv (no pagination needed)
│  │  └─ > 10K rows → process_csv with offset/limit (pagination)
│  │
│  └─ Multiple files?
│     └─ batch_process_csv (consistent filter across all)
│
├─ Log files?
│  └─ process_logs with pattern matching + offset
│
├─ Execute code?
│  └─ execute_code (Python/Bash/Node, supports heredocs)
│
└─ Find tools?
   └─ search_tools (progressive disclosure)
```

---

## When to Use Each Tool

### execute_code

**Use when**:
- Running Python, Bash, or Node.js code
- Need sandboxed execution environment
- Using heredoc syntax for multi-line scripts
- Processing data with 98%+ token savings

**When NOT to use**:
- Just reading files (use Read tool)
- Simple bash commands (use Bash directly)
- File operations (use dedicated tools)

### process_csv

**Use when**:
- Analyzing CSV files > 50 rows
- Need filtering (filter_expr)
- Need aggregation (groupby, sum, mean, min, max)
- Working with large files (> 10K rows)

**Parameters**:
| Parameter | Purpose | Example |
|-----------|---------|---------|
| file_path | Path to CSV | `"data.csv"` |
| filter_expr | Filter rows | `"price > 100"` |
| columns | Select columns | `["name", "price"]` |
| limit | Max rows (default: 100) | `1000` |
| offset | Skip N rows (pagination) | `100` |
| aggregate_by | Group by column | `"category"` |
| agg_func | Aggregation function | `"sum"` |
| response_format | Output format | `"summary"` or `"json"` |

**Pagination pattern for large files**:
```python
# First page
process_csv(file_path="large.csv", offset=0, limit=100)

# Second page
process_csv(file_path="large.csv", offset=100, limit=100)
```

### process_logs

**Use when**:
- Analyzing log files > 50 lines
- Need pattern matching with regex
- Need context around matches (context_lines)
- Working with large logs (use offset)

**Parameters**:
| Parameter | Purpose | Example |
|-----------|---------|---------|
| file_path | Path to log file | `"app.log"` |
| pattern | Regex pattern | `"ERROR\|CRITICAL"` |
| limit | Max matches (default: 100) | `500` |
| offset | Skip previous matches | `100` |
| context_lines | Lines before/after | `2` |

### batch_process_csv

**Use when**:
- Processing 2-5 CSV files
- Need consistent filtering across all
- Want 80% savings vs individual calls

**Parameters**:
| Parameter | Purpose | Example |
|-----------|---------|---------|
| file_paths | List of CSV paths | `["file1.csv", "file2.csv"]` |
| filter_expr | Applied to all files | `"price > 100"` |
| columns | Select from all files | `["name", "price"]` |
| aggregate | Combine results | `true` |

### search_tools

**Use when**:
- Don't know which tool to use
- Want 95% savings vs loading all definitions
- Finding tools by keyword or category

**Levels**:
| Level | Content | When to Use |
|-------|---------|-------------|
| `names_only` | Just tool names | Quick discovery |
| `summary` | Name + description | Deciding relevance |
| `full` | Complete details | Before using tool |

**Categories**:
- `execution` - Code execution tools
- `data_processing` - CSV, log processing
- `discovery` - Search, list tools
- `utility` - Reports, configuration

---

## Token Savings by Pattern

| Pattern | Before | After | Savings |
|---------|--------|-------|---------|
| Load all tools | 150K tokens | 2K tokens | 98.7% |
| Process 10K CSV | Read all → 10K tokens | Filter → 100 tokens | 99% |
| Search 100K logs | Read all → 100K tokens | Pattern → 5K tokens | 95% |
| Multiple CSVs | 5 calls × 2K = 10K | 1 batch = 2K | 80% |

---

## Common Patterns

### Pattern 1: Filter + Aggregate

```python
# Get total sales by category (where price > 100)
process_csv(
    file_path="sales.csv",
    filter_expr="price > 100",
    aggregate_by="category",
    agg_func="sum"
)
```

### Pattern 2: Paginate Large Files

```python
# Page through 100K rows, 100 at a time
for page in range(0, 1000, 100):
    results = process_csv(
        file_path="huge.csv",
        offset=page,
        limit=100
    )
    # Process page...
```

### Pattern 3: Search Logs with Context

```python
# Find errors with 2 lines before/after
process_logs(
    file_path="app.log",
    pattern="ERROR|CRITICAL",
    context_lines=2,
    limit=50
)
```

### Pattern 4: Heredoc Bash Scripts

```python
# Multi-line script via heredoc
execute_code(code="""
cat <<'EOF' > script.sh
#!/bin/bash
echo "Line 1"
echo "Line 2"
echo "Line 3"
EOF
bash script.sh
""", language="bash")
```

### Pattern 5: Batch Multiple Files

```python
# Apply same filter to 3 files
batch_process_csv(
    file_paths=["q1.csv", "q2.csv", "q3.csv"],
    filter_expr="revenue > 1000",
    columns=["date", "revenue"],
    aggregate=True
)
```

---

## Best Practices

1. **Use summary format** for human consumption
2. **Apply filters early** to reduce data volume
3. **Use aggregation** for statistical analysis
4. **Leverage progressive disclosure** for tool discovery
5. **Monitor token metrics** in responses
6. **Use heredocs** for multi-line bash scripts
7. **Use offset/limit** for large file pagination
8. **Use batch processing** for multiple files

---

## Anti-Patterns to Avoid

| Anti-Pattern | Symptom | Fix |
|--------------|---------|-----|
| Load full CSV | `Read("large.csv")` → 50K tokens | Use `process_csv` with filter |
| Read entire log | `Read("app.log")` → 100K tokens | Use `process_logs` with pattern |
| Individual file calls | 5 × `process_csv` = 10K tokens | Use `batch_process_csv` |
| No pagination | Timeout on huge files | Use offset/limit |
| Wrong format | `json` for humans | Use `summary` format |
