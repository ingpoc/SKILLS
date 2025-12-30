# Token-Efficient Tool Examples

Concrete code examples for token-efficient MCP tools.

## Tool Invocation

All token-efficient tools are prefixed with `mcp__token-efficient__`:

```python
# Basic invocation
mcp__token-efficient__execute_code(code="print('hello')", language="python")
mcp__token-efficient__process_csv(file_path="data.csv", filter_expr="price > 100")
mcp__token-efficient__process_logs(file_path="app.log", pattern="ERROR")
```

---

## execute_code Examples

### Python: Data Analysis

```python
# Process data in sandbox (98%+ savings)
mcp__token-efficient__execute_code(code="""
import pandas as pd
import json

# Load and process data
df = pd.read_csv('sales.csv')
result = {
    'total': df['price'].sum(),
    'mean': df['price'].mean(),
    'count': len(df)
}
print(json.dumps(result))
""", language="python", response_format="json")
```

### Bash: Heredoc Multi-line Script

```python
# Heredoc support for complex bash scripts
mcp__token-efficient__execute_code(code="""
# Create script with heredoc
cat <<'EOF' > setup.sh
#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -q pandas numpy

echo "Running tests..."
pytest tests/ -v

echo "Done!"
EOF

# Execute the script
bash setup.sh
""", language="bash", timeout=60)
```

### Node.js: Quick Calculation

```python
# JavaScript in sandbox
mcp__token-efficient__execute_code(code="""
const data = [1, 2, 3, 4, 5];
const sum = data.reduce((a, b) => a + b, 0);
const mean = sum / data.length;
console.log(JSON.stringify({sum, mean}));
""", language="node")
```

---

## process_csv Examples

### Basic Filtering

```python
# Get expensive items only (99% savings vs reading all)
mcp__token-efficient__process_csv(
    file_path="products.csv",
    filter_expr="price > 100",
    columns=["name", "price", "category"],
    limit=50,
    response_format="summary"
)
```

### Aggregation

```python
# Total sales by category
mcp__token-efficient__process_csv(
    file_path="sales.csv",
    filter_expr="quantity > 0",
    aggregate_by="category",
    agg_func="sum",
    columns=["category", "revenue"],
    response_format="summary"
)
```

### Pagination for Large Files

```python
# Page 1: First 100 rows
page1 = mcp__token-efficient__process_csv(
    file_path="huge.csv",
    offset=0,
    limit=100
)

# Page 2: Next 100 rows
page2 = mcp__token-efficient__process_csv(
    file_path="huge.csv",
    offset=100,
    limit=100
)

# Page 3: Next 100 rows
page3 = mcp__token-efficient__process_csv(
    file_path="huge.csv",
    offset=200,
    limit=100
)
```

### Complex Filter

```python
# Multiple conditions
mcp__token-efficient__process_csv(
    file_path="orders.csv",
    filter_expr="price > 50 AND category == 'electronics' AND status == 'shipped'",
    columns=["id", "customer", "price"],
    limit=20
)
```

### Statistics

```python
# Get statistics on a column
mcp__token-efficient__process_csv(
    file_path="data.csv",
    columns=["price"],
    filter_expr="price > 0",
    aggregate_by="category",
    agg_func="mean"
)
```

---

## process_logs Examples

### Find Errors

```python
# Find all ERROR and CRITICAL entries
mcp__token-efficient__process_logs(
    file_path="application.log",
    pattern="ERROR|CRITICAL",
    context_lines=2,
    limit=50,
    response_format="summary"
)
```

### API Request Analysis

```python
# Find slow API calls (> 1 second)
mcp__token-efficient__process_logs(
    file_path="api.log",
    pattern="duration.*[1-9][0-9]{3,}ms",
    context_lines=1,
    limit=100
)
```

### Paginate Large Logs

```python
# First 100 error matches
errors_page1 = mcp__token-efficient__process_logs(
    file_path="huge.log",
    pattern="ERROR",
    offset=0,
    limit=100
)

# Next 100 error matches
errors_page2 = mcp__token-efficient__process_logs(
    file_path="huge.log",
    pattern="ERROR",
    offset=100,
    limit=100
)
```

### IP Address Extraction

```python
# Find all IP addresses in logs
mcp__token-efficient__process_logs(
    file_path="access.log",
    pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
    limit=200
)
```

### Specific Error Code

```python
# Find HTTP 500 errors
mcp__token-efficient__process_logs(
    file_path="server.log",
    pattern="HTTP/1.1\" 500",
    context_lines=3,
    limit=50
)
```

---

## batch_process_csv Examples

### Multiple Files, Same Filter

```python
# Process quarterly sales files (80% savings vs individual calls)
mcp__token-efficient__batch_process_csv(
    file_paths=["q1.csv", "q2.csv", "q3.csv", "q4.csv"],
    filter_expr="revenue > 1000",
    columns=["date", "product", "revenue"],
    aggregate=True,
    agg_func="sum",
    response_format="summary"
)
```

### Compare Multiple Sources

```python
# Aggregate data from different sources
mcp__token-efficient__batch_process_csv(
    file_paths=["source_a.csv", "source_b.csv", "source_c.csv"],
    filter_expr="status = 'active'",
    columns=["category", "value"],
    aggregate_by="category",
    agg_func="mean"
)
```

---

## search_tools Examples

### Find CSV Tools

```python
# Quick tool discovery (95% savings vs loading all)
mcp__token-efficient__search_tools(
    query="csv",
    level="summary"
)
```

### Find Execution Tools

```python
# Find tools in specific category
mcp__token-efficient__search_tools(
    query="execute",
    category="execution",
    level="full"
)
```

### List All Tools (Progressive)

```python
# Level 1: Just names
mcp__token-efficient__list_token_efficient_tools(level="names_only")

# Level 2: With descriptions
mcp__token-efficient__list_token_efficient_tools(level="summary")

# Level 3: Complete details
mcp__token-efficient__list_token_efficient_tools(level="full")
```

---

## Real-World Patterns

### Pattern 1: E-commerce Analytics

```python
# Daily sales summary
mcp__token-efficient__process_csv(
    file_path="orders.csv",
    filter_expr="date = '2025-12-28'",
    aggregate_by="product_category",
    agg_func="sum",
    columns=["product_category", "total_amount"]
)
```

### Pattern 2: Log Monitoring

```python
# Check for recent errors
mcp__token-efficient__process_logs(
    file_path="/var/log/app.log",
    pattern="ERROR|WARN",
    context_lines=1,
    limit=20,
    response_format="summary"
)
```

### Pattern 3: Data Validation

```python
# Find data quality issues
mcp__token-efficient__process_csv(
    file_path="users.csv",
    filter_expr="email IS NULL OR email = ''",
    columns=["id", "name"],
    limit=100
)
```

### Pattern 4: Batch Report Generation

```python
# Generate monthly reports from daily files
daily_files = [f"sales_{i:02d}.csv" for i in range(1, 32)]

mcp__token-efficient__batch_process_csv(
    file_paths=daily_files,
    filter_expr="status = 'completed'",
    columns=["date", "revenue"],
    aggregate_by="date",
    agg_func="sum"
)
```

### Pattern 5: Test Log Analysis

```python
# Find failed tests
mcp__token-efficient__process_logs(
    file_path="test_results.log",
    pattern="FAILED|ERROR",
    context_lines=2,
    limit=50
)
```

---

## Response Format Examples

### Summary Format (Human-Readable)

```python
# Best for human consumption
mcp__token-efficient__process_csv(
    file_path="data.csv",
    filter_expr="price > 100",
    response_format="summary"  # Default
)
# Returns: "Filtered 50 rows from 1000. Showing 5 samples..."
```

### JSON Format (Programmatic)

```python
# Best for further processing
mcp__token-efficient__process_csv(
    file_path="data.csv",
    filter_expr="price > 100",
    response_format="json"
)
# Returns: {"data": [...], "stats": {...}}
```

---

## Token Savings Comparison

| Operation | Without Token-Efficient | With Token-Efficient | Savings |
|-----------|------------------------|---------------------|---------|
| Read 10K CSV, filter | Read all → 10K tokens | process_csv → 100 tokens | 99% |
| Search 100K logs | Read all → 100K tokens | process_logs → 5K tokens | 95% |
| Process 5 CSVs | 5 × Read = 50K tokens | batch_process_csv = 10K | 80% |
| Execute Python | Load env = 5K tokens | execute_code = 100 tokens | 98% |
| Find tools | Load all = 150K tokens | search_tools = 2K tokens | 98.7% |

---

## Tips

1. **Always use filter_expr** for CSV - don't load all rows
2. **Use limit** to prevent overwhelming output
3. **Use offset** for pagination on large files
4. **Use summary format** unless you need raw JSON
5. **Use batch_process_csv** for 2+ files with same filter
6. **Use heredocs** for multi-line bash scripts
7. **Monitor response stats** - they show token savings
