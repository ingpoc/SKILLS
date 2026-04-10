# Token-Efficient MCP Patterns for Implementation

Proactively use token-efficient MCP tools instead of loading data into context.

## Core Principle

**DON'T load data → DO process in sandbox**

| Approach | Token Cost | Speed | Use When |
|----------|-----------|-------|----------|
| Load file to context | 5000+ tokens | Slow | <50 lines, reading |
| Use execute_code | ~200 tokens | Fast | Any analysis, transformation |
| Use process_logs | ~200 tokens | Fast | Pattern search, >100 lines |
| Use process_csv | ~200 tokens | Fast | Filtering, aggregating, >50 rows |

**Savings**: 95-99% tokens vs loading raw data.

---

## 1. analyze-project-structure (execute_code)

**When**: After getting feature, before implementing
**Purpose**: Understand codebase layout, find relevant files
**Savings**: 98% vs reading 100+ files

```python
# Use execute_code to analyze structure
code = """
import os
import subprocess

# Find all Python files in relevant modules
result = subprocess.run(
    ["find", ".", "-name", "*.py", "-type", "f"],
    capture_output=True,
    text=True,
    cwd="/path/to/project"
)

files = result.stdout.strip().split('\n')

# Group by directory
from collections import defaultdict
by_dir = defaultdict(list)
for f in files:
    if '/test' not in f and '/__pycache__' not in f:
        dir_name = os.path.dirname(f)
        by_dir[dir_name].append(f)

# Show structure (top 10 dirs)
for dir_name in sorted(by_dir.keys())[:10]:
    print(f"{dir_name}: {len(by_dir[dir_name])} files")

# List files in relevant path
print("\nFiles in gateway/routes/:")
for f in sorted(by_dir.get("./gateway/routes", []))[:5]:
    print(f"  {f}")
"""

# Execute in sandbox (returns ~200 tokens vs 5000+ loading files)
result = execute_code(code, language="python")
```

**Output** (example):

```
./gateway: 15 files
./gateway/routes: 8 files
./gateway/tests: 12 files
./frontend/components: 24 files

Files in gateway/routes/:
  ./gateway/routes/__init__.py
  ./gateway/routes/auth.py
  ./gateway/routes/credentials.py
  ./gateway/routes/validators.py
```

---

## 2. find-similar-code (execute_code)

**When**: Implementing feature similar to existing code
**Purpose**: Find patterns to reuse
**Savings**: 98% vs reading entire files

```python
# Search for similar patterns
code = """
import os
import re

# Search for "validation" pattern in codebase
pattern = r"def.*validate.*\(|class.*Validator"

matches = []
for root, dirs, files in os.walk('.'):
    # Skip test dirs and caches
    dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]

    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            try:
                with open(path) as f:
                    for i, line in enumerate(f, 1):
                        if re.search(pattern, line):
                            matches.append((path, i, line.strip()))
            except:
                pass

# Show top matches (avoid loading entire files)
for path, line_no, line in matches[:10]:
    print(f"{path}:{line_no}: {line[:80]}")
"""

result = execute_code(code, language="python")
```

**Output** (example):

```
./gateway/routes/credentials.py:42: def validate_aadhaar(aadhaar_number):
./gateway/routes/validators.py:15: class AadhaarValidator:
./gateway/routes/validators.py:28: def validate_pan(pan_number):
./agents/document_validator/main.py:50: def validate_document(doc_type):
```

---

## 3. analyze-test-patterns (execute_code)

**When**: Writing tests for new feature
**Purpose**: Understand test structure, patterns, fixtures
**Savings**: 98% vs reading test files

```bash
# Count and analyze tests in project
code = """
import os
import re

test_stats = {
    'total_tests': 0,
    'test_files': 0,
    'frameworks': set(),
    'patterns': []
}

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
    for file in files:
        if 'test' in file and (file.endswith('.py') or file.endswith('.js')):
            test_stats['test_files'] += 1
            path = os.path.join(root, file)

            with open(path) as f:
                content = f.read()
                # Count test functions
                tests = len(re.findall(r'def test_|it\(|describe\(', content))
                test_stats['total_tests'] += tests

                # Identify framework
                if 'pytest' in content or 'import pytest' in content:
                    test_stats['frameworks'].add('pytest')
                if 'import unittest' in content:
                    test_stats['frameworks'].add('unittest')
                if 'describe(' in content or "it('" in content:
                    test_stats['frameworks'].add('jest')

print(f"Total test files: {test_stats['test_files']}")
print(f"Total tests: {test_stats['total_tests']}")
print(f"Frameworks used: {', '.join(sorted(test_stats['frameworks']))}")
"""

result = execute_code(code, language="python")
```

**Output** (example):

```
Total test files: 23
Total tests: 156
Frameworks used: jest, pytest
```

---

## 4. search-error-logs (process_logs)

**When**: Implementing fix or feature with known integration points
**Purpose**: Find related errors, patterns, context
**Savings**: 95% vs reading entire log files

```bash
# Use process_logs MCP
result = process_logs(
    file_path="logs/errors.log",
    pattern="validation|validator|Aadhaar",  # Search pattern
    limit=10,
    context_lines=2  # Show 2 lines before/after match
)
```

**Output** (example):

```
Line 342: [2025-12-28 10:15:23] ERROR Aadhaar validation failed
  Context (before): Processing document ID: doc-12345
  Context (after): Retrying with fallback validator

Line 678: [2025-12-28 11:42:01] WARNING Validator timeout after 5s
  Context (before): Initializing document processor
  Context (after): Falling back to cached validation

Line 1024: [2025-12-28 14:33:45] ERROR PAN validation rejected: invalid format
  Context (before): Extracting fields from document image
  Context (after): User notified, ticket opened
```

---

## 5. analyze-data-patterns (process_csv)

**When**: Feature involves data processing or integration
**Purpose**: Understand data format, values, edge cases
**Savings**: 99% vs loading entire CSV

```bash
# Use process_csv MCP with filters
result = process_csv(
    file_path="data/test_credentials.csv",
    columns=["aadhaar", "status", "provider"],
    filter_expr="status='rejected'",  # Only rejected records
    agg_func="count",
    aggregate_by="provider",
    limit=20
)
```

**Output** (example):

```
Summary:
  Total rows: 5000
  Matching filter: 342 rejected records
  Top providers (by rejection count):
    - apisetu: 156
    - manual_upload: 124
    - api_gateway: 62
```

---

## 6. validate-code-changes (execute_code)

**When**: After implementing feature
**Purpose**: Verify code syntax, imports, basic structure
**Savings**: 98% vs manual reading

```python
# Validate new code
code = """
import ast
import sys

# Parse Python file
file_path = 'gateway/routes/new_validator.py'
try:
    with open(file_path) as f:
        ast.parse(f.read())
    print(f"✓ {file_path}: Valid Python syntax")
except SyntaxError as e:
    print(f"✗ {file_path}: Syntax error at line {e.lineno}: {e.msg}")
    sys.exit(1)

# Check for required imports
with open(file_path) as f:
    content = f.read()
    required = ['logging', 'json']
    missing = [imp for imp in required if f'import {imp}' not in content]
    if missing:
        print(f"⚠ Missing imports: {', '.join(missing)}")
    else:
        print(f"✓ All required imports present")

# Check for test file
test_file = 'gateway/tests/test_new_validator.py'
if os.path.exists(test_file):
    print(f"✓ Test file exists: {test_file}")
else:
    print(f"✗ Test file missing: {test_file}")
"""

result = execute_code(code, language="python")
```

**Output** (example):

```
✓ gateway/routes/new_validator.py: Valid Python syntax
✓ All required imports present
✓ Test file exists: gateway/tests/test_new_validator.py
```

---

## 7. count-lines-of-code (execute_code)

**When**: Validating implementation scope
**Purpose**: Ensure code changes are reasonable size
**Savings**: 98% vs manual counting

```bash
# Analyze implementation size
code = """
import os

metrics = {
    'python_files': 0,
    'python_lines': 0,
    'test_lines': 0,
    'modified_files': []
}

# Count changes in implementation
for root, dirs, files in os.walk('gateway'):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path) as f:
                lines = len(f.readlines())
                metrics['python_lines'] += lines
                metrics['python_files'] += 1
                if 'test' in path:
                    metrics['test_lines'] += lines

print(f"Python files: {metrics['python_files']}")
print(f"Code lines: {metrics['python_lines'] - metrics['test_lines']}")
print(f"Test lines: {metrics['test_lines']}")
print(f"Test coverage ratio: {metrics['test_lines'] / metrics['python_lines'] * 100:.1f}%")
"""

result = execute_code(code, language="python")
```

**Output** (example):

```
Python files: 24
Code lines: 3400
Test lines: 2100
Test coverage ratio: 38.2%
```

---

## Workflow Integration

### Step 2: Analyze Codebase Context (Proactive)

```
Get Feature
    ↓
STEP 2: Analyze Context (Token-Efficient)
├─ execute_code: Analyze project structure
│  └─ Find relevant files, modules, patterns
├─ execute_code: Search for similar code
│  └─ Find patterns to reuse
├─ process_logs: Search error logs
│  └─ Understand integration points, known issues
└─ process_csv: Analyze data patterns (if needed)
    └─ Understand data structure, edge cases

RESULT: 95-99% token savings, full context of codebase
    ↓
Step 3: Query Context Graph
    ↓
Step 4: Implement Feature
```

---

## Common Patterns

### Pattern 1: Find Files by Type

```python
# Find all test files
code = """
import os
import glob

test_files = []
for pattern in ['**/test_*.py', '**/*_test.py', '**/*.test.ts']:
    test_files.extend(glob.glob(pattern, recursive=True))

print(f"Found {len(test_files)} test files")
for f in sorted(test_files)[:10]:
    print(f"  {f}")
"""
```

### Pattern 2: Count Pattern Occurrences

```python
# Count validation functions
code = """
import re
count = 0
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            with open(os.path.join(root, f)) as file:
                content = file.read()
                count += len(re.findall(r'def validate_|class.*Validator', content))

print(f"Total validators: {count}")
"""
```

### Pattern 3: Analyze Dependencies

```python
# Find imports of specific module
code = """
import os
import re

imports = {}
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            with open(os.path.join(root, f)) as file:
                for line in file:
                    if 'from apisetu' in line or 'import apisetu' in line:
                        path = os.path.join(root, f)
                        imports[path] = line.strip()

print(f"apisetu imports found: {len(imports)}")
for path, line in list(imports.items())[:5]:
    print(f"  {path}: {line}")
"""
```

---

## Token Savings Summary

| Task | Load Method | Token Cost | execute_code/process | Savings |
|------|-------------|-----------|----------------------|---------|
| Find relevant files | Read directory | 5000+ | execute_code + glob | 98% |
| Search code patterns | Load all files | 10000+ | execute_code + grep | 99% |
| Analyze test structure | Read test files | 3000+ | execute_code + parse | 95% |
| Search error logs | Load entire log | 5000+ | process_logs | 95% |
| Analyze CSV data | Load entire CSV | 8000+ | process_csv | 99% |
| Validate syntax | Manual reading | 2000+ | execute_code + ast | 95% |

**Total per feature**: 95-99% token savings vs traditional code reading approach.

---

## Best Practices

1. **Always proactive** - Use execute_code/process before reading files
2. **Chain analysis** - Combine multiple tools for comprehensive context
3. **Limit output** - Use `head`, `limit`, context_lines to reduce output size
4. **Exit on first** - Stop searching once you have enough context
5. **Sandbox only** - Never load raw data to context window
6. **Pattern first** - Search by pattern, then read matching files
