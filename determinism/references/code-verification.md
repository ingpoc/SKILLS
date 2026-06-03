# Code Verification Patterns

## Core Principle

From [Anthropic Engineering](https://www.anthropic.com/engineering/claude-code-best-practices):

> "Claude can run scripts without loading either the script or the PDF into context. And because code is deterministic, this workflow is consistent and repeatable."

## LLM Judgment vs Code Verification

| Task | LLM Judgment (Non-Deterministic) | Code Verification (Deterministic) |
|------|----------------------------------|-----------------------------------|
| Tests passed? | "The tests appear to pass" | `pytest; echo $?` → 0 or 1 |
| Feature complete? | "I believe this is done" | Script checks required files exist |
| Valid JSON? | "This looks like valid JSON" | `python -c "json.load(f)"` |
| Server running? | "The server should be up" | `curl -s localhost:8000/health` |
| Code quality? | "The code looks clean" | `ruff check . && mypy .` |
| Database migrated? | "Migrations seem applied" | `alembic check` |

## Verification Script Patterns

### Pattern 1: Exit Code Verification

```bash
#!/bin/bash
# scripts/verify-build.sh
# Returns: 0 = pass, non-zero = fail

npm run build

# Exit code propagates
# 0 = success, 1+ = failure
```

### Pattern 2: Boolean Output

```python
#!/usr/bin/env python3
# scripts/verify-feature.py
# Outputs: true/false as JSON

import json
import os

def verify():
    checks = {
        "file_exists": os.path.exists("src/feature.py"),
        "test_exists": os.path.exists("tests/test_feature.py"),
        "no_syntax_errors": check_syntax("src/feature.py")
    }

    all_passed = all(checks.values())

    print(json.dumps({
        "passed": all_passed,
        "checks": checks
    }))

    return all_passed

if __name__ == "__main__":
    exit(0 if verify() else 1)
```

### Pattern 3: Structured Evidence

```python
#!/usr/bin/env python3
# scripts/verify-with-evidence.py
# Outputs: JSON with evidence for audit

import json
import subprocess
from datetime import datetime

def collect_evidence():
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "checks": []
    }

    # Check 1: Build
    build = subprocess.run(["npm", "run", "build"], capture_output=True)
    evidence["checks"].append({
        "name": "build",
        "passed": build.returncode == 0,
        "output": build.stdout.decode()[-500:]
    })

    # Check 2: Tests
    tests = subprocess.run(["npm", "test"], capture_output=True)
    evidence["checks"].append({
        "name": "tests",
        "passed": tests.returncode == 0,
        "output": tests.stdout.decode()[-500:]
    })

    # Check 3: Lint
    lint = subprocess.run(["npm", "run", "lint"], capture_output=True)
    evidence["checks"].append({
        "name": "lint",
        "passed": lint.returncode == 0,
        "output": lint.stdout.decode()[-500:]
    })

    evidence["all_passed"] = all(c["passed"] for c in evidence["checks"])

    # Save evidence
    with open("/tmp/test-evidence/verification.json", "w") as f:
        json.dump(evidence, f, indent=2)

    return evidence["all_passed"]

if __name__ == "__main__":
    exit(0 if collect_evidence() else 1)
```

## Common Verification Scripts

### File Existence

```bash
#!/bin/bash
# scripts/verify-files-exist.sh

REQUIRED_FILES=(
    "src/main.py"
    "tests/test_main.py"
    "requirements.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "FAIL: Missing required file: $file"
        exit 1
    fi
done

echo "PASS: All required files exist"
exit 0
```

### API Health

```bash
#!/bin/bash
# scripts/verify-api-health.sh

URL="${1:-http://localhost:8000/health}"
TIMEOUT=5

STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$URL")

if [ "$STATUS" = "200" ]; then
    echo "PASS: Health check returned 200"
    exit 0
else
    echo "FAIL: Health check returned $STATUS"
    exit 1
fi
```

### Database Migration

```bash
#!/bin/bash
# scripts/verify-migrations.sh

# For Alembic (Python)
if command -v alembic &> /dev/null; then
    alembic check 2>&1 | grep -q "No new upgrade operations"
    if [ $? -eq 0 ]; then
        echo "PASS: All migrations applied"
        exit 0
    else
        echo "FAIL: Pending migrations exist"
        exit 1
    fi
fi

# For Django
if [ -f "manage.py" ]; then
    python manage.py migrate --check
    exit $?
fi

echo "WARN: No migration framework detected"
exit 0
```

### Code Quality

```bash
#!/bin/bash
# scripts/verify-code-quality.sh

ERRORS=0

# Python
if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
    echo "Checking Python code..."

    # Ruff
    ruff check . --quiet || ((ERRORS++))

    # Mypy (if configured)
    if grep -q "mypy" pyproject.toml 2>/dev/null; then
        mypy . --quiet || ((ERRORS++))
    fi
fi

# Node.js
if [ -f "package.json" ]; then
    echo "Checking Node.js code..."

    # ESLint
    npm run lint --silent || ((ERRORS++))

    # TypeScript
    if [ -f "tsconfig.json" ]; then
        npx tsc --noEmit || ((ERRORS++))
    fi
fi

if [ $ERRORS -eq 0 ]; then
    echo "PASS: Code quality checks passed"
    exit 0
else
    echo "FAIL: $ERRORS quality checks failed"
    exit 1
fi
```

## Integration with Hooks

### PreToolUse Hook for Verification

```python
#!/usr/bin/env python3
# .claude/hooks/verify-before-complete.py
# Blocks marking complete without passing verification

import json
import sys
import subprocess

input_data = json.load(sys.stdin)
tool_input = input_data.get("tool_input", {})
content = tool_input.get("content", "")

# Check if marking feature as complete
if '"status": "completed"' not in content:
    sys.exit(0)

# Run verification script
result = subprocess.run(
    ["bash", "scripts/verify-feature.sh"],
    capture_output=True
)

if result.returncode != 0:
    print("BLOCKED: Verification failed", file=sys.stderr)
    print(result.stderr.decode(), file=sys.stderr)
    sys.exit(2)

sys.exit(0)
```

## Verification vs Judgment Checklist

When writing verification logic, ask:

| Question | If Yes | If No |
|----------|--------|-------|
| Can a script check this? | Use script | Reconsider requirement |
| Does it return boolean? | Use exit code | Convert to boolean |
| Is output deterministic? | Safe to use | Add constraints |
| Can it be audited? | Save evidence | Add logging |

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| "Looks correct" | Subjective | Use concrete check |
| "Should work" | Uncertainty | Actually run it |
| "Tests seem to pass" | Guessing | Check exit code |
| "I believe it's done" | Opinion | Verify with script |
| "The output appears valid" | Interpretation | Parse and validate |
