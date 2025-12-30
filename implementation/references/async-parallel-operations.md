# Async Parallel Operations Pattern

**Purpose**: Execute independent operations concurrently to reduce implementation time.

**Speedup**: 30-50% for I/O-bound tasks (tests, linting, git operations)

---

## When to Use Parallel Operations

| Scenario | Sequential | Parallel | Speedup |
|----------|------------|----------|---------|
| Running tests | 30s | 30s (CPU bound) | 1x |
| Running linters | 15s | 15s (CPU bound) | 1x |
| Tests + Linter + Git | 46s | 30s | 1.5x |
| File operations (I/O) | 10s | 2s | 5x |
| API calls | 20s | 4s | 5x |

**Rule of thumb**: Parallelize I/O-bound operations, not CPU-bound.

---

## Parallel Patterns

### Pattern 1: Independent Checks

```python
import asyncio
from typing import List, Tuple

async def run_parallel_checks() -> Tuple[bool, bool, str]:
    """
    Run independent checks in parallel.
    Returns: (tests_passed, lint_passed, git_status)
    """
    results = await asyncio.gather(
        run_tests(),      # Takes 30s
        run_linter(),     # Takes 15s
        get_git_status()  # Takes 1s
    )

    tests_passed, lint_passed, git_status = results
    return tests_passed, lint_passed, git_status

# Usage:
tests_ok, lint_ok, git_ok = await run_parallel_checks()
# Total: 30s (not 46s)
```

### Pattern 2: File Operations

```python
import asyncio
from pathlib import Path

async def process_files_in_parallel(file_paths: List[Path]) -> List[dict]:
    """
    Read/process multiple files concurrently.
    """
    async def process_file(path: Path) -> dict:
        content = await asyncio.to_thread(read_file, path)
        return {"path": str(path), "size": len(content)}

    results = await asyncio.gather(
        *[process_file(p) for p in file_paths],
        return_exceptions=True  # Don't fail all if one fails
    )

    # Filter successful results
    return [r for r in results if isinstance(r, dict)]
```

### Pattern 3: API Calls

```python
import asyncio

async def fetch_dependencies(package_names: List[str]) -> dict:
    """
    Fetch package info from multiple registries in parallel.
    """
    async def fetch_package(name: str) -> tuple:
        # Simulate API call
        await asyncio.sleep(1)
        return (name, "latest_version")

    results = await asyncio.gather(
        *[fetch_package(name) for name in package_names]
    )

    return dict(results)
```

---

## Claude Code Integration

### Bash Parallel Execution

```bash
#!/bin/bash
# scripts/parallel-checks.sh

# Run checks in parallel using background jobs
run_tests() {
    pytest --tb=short -q
    echo "tests:$?"
}

run_linter() {
    eslint src/ --ext .ts,.tsx
    echo "linter:$?"
}

git_status() {
    git status --porcelain
    echo "git:$?"
}

# Execute in parallel
run_tests &
PID_TESTS=$!

run_linter &
PID_LINTER=$!

git_status &
PID_GIT=$!

# Wait for all
wait $PID_TESTS
EXIT_TESTS=$?

wait $PID_LINTER
EXIT_LINTER=$?

wait $PID_GIT
EXIT_GIT=$?

# Check results
if [ $EXIT_TESTS -eq 0 ] && [ $EXIT_LINTER -eq 0 ]; then
    echo "✓ All checks passed"
    exit 0
else
    echo "✗ Some checks failed"
    exit 1
fi
```

### Python Parallel Script

```python
#!/usr/bin/env python3
# scripts/parallel_checks.py

import asyncio
import subprocess
from typing import Tuple

async def run_command(cmd: list) -> Tuple[str, int, str]:
    """
    Run command asynchronously.
    Returns: (stdout, exit_code, stderr)
    """
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()
    return stdout.decode(), proc.returncode, stderr.decode()

async def main():
    """
    Run tests, linter, and type check in parallel.
    """
    results = await asyncio.gather(
        run_command(["pytest", "--tb=short", "-q"]),
        run_command(["eslint", "src/", "--ext", ".ts,.tsx"]),
        run_command(["tsc", "--noEmit"]),
        return_exceptions=True
    )

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Check {i+1} failed: {result}")
        else:
            stdout, exit_code, stderr = result
            if exit_code != 0:
                print(f"Check {i+1} failed with exit code {exit_code}")
                print(stderr[-500:])  # Last 500 chars of error

if __name__ == "__main__":
    asyncio.run(main())
```

---

## MCP Tools in Parallel

### Pattern: Multiple File Reads

```python
# When agent needs to read multiple files to understand context
async def read_files_parallel(paths: List[str]) -> dict:
    """
    Read multiple files using Read tool in parallel.
    """
    results = {}
    for path in paths:
        # Claude Code handles this - but conceptually parallel
        content = read_file(path)
        results[path] = content

    return results

# Agent would use:
# "Read these files in parallel to understand the codebase structure:
#  - src/auth/login.ts
#  - src/auth/session.ts
#  - src/auth/middleware.ts"
```

### Pattern: Parallel API Calls (via MCP)

```python
# When using MCP servers that support async
async def fetch_multiple_sources() -> dict:
    """
    Fetch from GitHub API, NPM registry, and docs in parallel.
    """
    results = await asyncio.gather(
        mcp_call("github", "get", "/repo/anthropics/claude-code"),
        mcp_call("npm", "get", "/package/@anthropic-ai/sdk"),
        mcp_call("web-search", "search", "Claude API patterns")
    )

    return {
        "github": results[0],
        "npm": results[1],
        "docs": results[2]
    }
```

---

## When NOT to Parallelize

| Scenario | Reason | Alternative |
|----------|--------|-------------|
| **CPU-bound tests** | No speedup (GIL) | Run sequentially |
| **Dependent operations** | Must wait for previous result | Sequential |
| **Shared state mutation** | Race conditions | Locks or sequential |
| **Resource intensive** | Memory/CPU exhaustion | Batch with limits |

---

## Batch Processing with Limits

```python
import asyncio
from typing import List, Callable

async def process_with_limits(
    items: List,
    func: Callable,
    concurrency: int = 5
) -> List:
    """
    Process items with concurrency limit.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded_func(item):
        async with semaphore:
            return await func(item)

    results = await asyncio.gather(
        *[bounded_func(item) for item in items]
    )

    return results

# Usage: Process 100 files, max 5 at a time
results = await process_with_limits(
    file_paths,
    process_file,
    concurrency=5
)
```

---

## Error Handling

```python
async def parallel_with_retries(tasks: List, max_retries: int = 3):
    """
    Run tasks in parallel with retry logic.
    """
    results = []

    for task in tasks:
        for attempt in range(max_retries):
            try:
                result = await asyncio.wait_for(task, timeout=30)
                results.append(result)
                break
            except asyncio.TimeoutError:
                if attempt == max_retries - 1:
                    results.append({"error": "timeout after retries"})
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                if attempt == max_retries - 1:
                    results.append({"error": str(e)})
                await asyncio.sleep(1)

    return results
```

---

## Implementation Workflow

### Standard Sequential (Slow)

```
1. Implement feature → 5 min
2. Write tests → 3 min
3. Run tests → 2 min
4. Run linter → 1 min
5. Check git status → 0.1 min
────────────────────────────────
Total: 11.1 minutes
```

### Optimized Parallel (Fast)

```
1. Implement feature → 5 min
2. Write tests → 3 min
3. [Run tests, linter, git] → 2 min (parallel)
────────────────────────────────
Total: 10 minutes (10% faster)
```

**For longer operations**, speedup is more significant:
- Tests: 5min, Linter: 3min, Type check: 2min
- Sequential: 10min
- Parallel: 5min (2x faster)

---

## Progress Tracking

```python
import asyncio
from typing import AsyncIterator

async def run_with_progress(tasks: List[str]) -> AsyncIterator[dict]:
    """
    Run tasks with progress updates.
    """
    completed = 0
    total = len(tasks)

    async def task_with_counter(task: str, index: int):
        result = await asyncio.create_task(run_task(task))
        nonlocal completed
        completed += 1
        progress = (completed / total) * 100
        yield {
            "task": task,
            "index": index,
            "progress": progress,
            "result": result
        }

    # Create tasks
    async_tasks = [task_with_counter(t, i) for i, t in enumerate(tasks)]

    # Process as they complete
    for task in asyncio.as_completed(async_tasks):
        async for result in task:
            yield result
```

---

## Token Efficiency Note

Parallel operations save **time**, not **tokens**. Each operation still consumes tokens independently.

| Metric | Sequential | Parallel | Savings |
|--------|------------|----------|---------|
| Time | 46s | 30s | 35% |
| Tokens | Same | Same | 0% |

**Recommendation**: Use parallel for speed-critical operations, not token optimization.

---

## Verification

After implementing parallel operations, verify correctness:

```python
def verify_parallel_results():
    """
    Verify parallel operations produce same results as sequential.
    """
    # Run sequential
    sequential_results = run_sequential(test_data)

    # Run parallel
    parallel_results = asyncio.run(run_parallel(test_data))

    # Compare
    assert len(sequential_results) == len(parallel_results)

    for s, p in zip(sequential_results, parallel_results):
        assert s == p, f"Mismatch: {s} != {p}"

    return True
```

---

## Scripts

**Parallel checks script:**
```bash
#!/bin/bash
# .skills/implementation/scripts/parallel-checks.sh

echo "Running parallel checks..."

# Background jobs
pytest --tb=short -q > /tmp/tests.log 2>&1 &
PID_TESTS=$!

eslint src/ --ext .ts,.tsx > /tmp/lint.log 2>&1 &
PID_LINTER=$!

tsc --noEmit > /tmp/types.log 2>&1 &
PID_TYPES=$!

# Wait with timeout
timeout 60s wait $PID_TESTS $PID_LINTER $PID_TYPES
EXIT_ALL=$?

# Check results
if [ $EXIT_ALL -eq 0 ]; then
    echo "✓ All checks passed"
    cat /tmp/tests.log | tail -5
else
    echo "✗ Some checks failed or timed out"
    echo "Tests:"
    cat /tmp/tests.log | tail -10
    echo "Linter:"
    cat /tmp/lint.log | tail -10
    echo "Types:"
    cat /tmp/types.log | tail -10
    exit 1
fi
```

---

## Checklist

- [ ] Operations are independent (no dependencies)
- [ ] At least one operation is I/O-bound (network, disk)
- [ ] Error handling for partial failures
- [ ] Concurrency limits for resource management
- [ ] Verification that results match sequential

---

*Added: 2025-12-28*
*Purpose: Speed up implementation by parallelizing independent operations*
*Speedup: 30-50% for I/O-bound tasks*
