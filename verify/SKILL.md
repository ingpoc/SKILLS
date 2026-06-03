---
name: verify
description: Run structured quality gate against current project. Use for /verify, "verify the build", "run quality checks". NOT for eval scoring (/eval-score) or auditing (/audit).
model: haiku
effort: low
allowed-tools: Read, Bash, Glob, Grep
---

# Verify: Run Quality Gate

**EXECUTE this skill now.** Follow the workflow steps below using the provided $ARGUMENTS. Do NOT describe, summarize, or explain this skill — run it.

## Arguments

- (none) — runs `standard` mode (phases 1-5)
- `quick` — phases 1-3 only (build, types, lint)
- `full` — all 6 phases
- `pre-commit` — phases 1-4 (build, types, lint, tests)
- `pre-pr` — all 6 phases with stricter thresholds

## Workflow

### Step 0: Detect Stack

Check for:
- `package.json` → Node/TypeScript stack
- `pyproject.toml` or `requirements.txt` → Python stack
- `Cargo.toml` → Rust stack
- `go.mod` → Go stack

Use the detected stack to select the right commands below.

### Phase 1: Build

| Stack | Command |
|-------|---------|
| Node/TS | `npm run build` or `tsc --noEmit` |
| Python | `python -m py_compile $(find . -name "*.py" -not -path "*/.*")` |
| Rust | `cargo build` |
| Go | `go build ./...` |

Result: PASS / FAIL (capture first 20 lines of errors if FAIL)

### Phase 2: Type Check

| Stack | Command |
|-------|---------|
| Node/TS | `tsc --noEmit` (skip if no tsconfig.json) |
| Python | `pyright .` or `mypy .` (skip if neither installed) |
| Rust | included in Phase 1 |
| Go | included in Phase 1 |

Result: PASS / SKIP / FAIL

### Phase 3: Lint

| Stack | Command |
|-------|---------|
| Node/TS | `npx eslint . --max-warnings 0` or `npx biome check .` |
| Python | `ruff check .` or `flake8` |
| Rust | `cargo clippy -- -D warnings` |
| Go | `golangci-lint run` (skip if not installed) |

Result: PASS / SKIP / FAIL (capture warning/error count)

### Phase 4: Tests

| Stack | Command |
|-------|---------|
| Node/TS | `npm test` or `npx jest --passWithNoTests` |
| Python | `pytest` or `python -m pytest` |
| Rust | `cargo test` |
| Go | `go test ./...` |

Result: PASS / FAIL (capture test count and failures)

### Phase 5: Security Scan

Check for common issues without external tools:
```bash
# Check for secrets patterns
grep -r --include="*.ts" --include="*.js" --include="*.py" \
  -E "(password|secret|api_key|apikey|token)\s*=\s*['\"][^'\"]{8,}" \
  . --exclude-dir=node_modules --exclude-dir=.git -l 2>/dev/null
```
Also check: no `console.log` in production paths (TS/JS), no bare `print()` debugging (Python).

Result: PASS / WARN (list files with findings)

### Phase 6: Diff Review (full / pre-pr only)

```bash
git diff --stat HEAD
git diff --name-only HEAD
```

Report: files changed, insertions, deletions. Flag files > 500 lines changed as "large diff".

Result: INFO (no pass/fail)

### Final Report

```
## Verification Report — <project> (<mode>)

| Phase | Result | Details |
|-------|--------|---------|
| 1. Build | ✓ PASS / ✗ FAIL | <brief> |
| 2. Type Check | ✓ PASS / — SKIP | |
| 3. Lint | ✓ PASS / ✗ FAIL | <N warnings> |
| 4. Tests | ✓ PASS / ✗ FAIL | <N passed, N failed> |
| 5. Security | ✓ PASS / ⚠ WARN | <files with findings> |
| 6. Diff | — INFO | <N files, +N -N lines> |

**Verdict: READY / NOT READY**

<If NOT READY: list blocking issues in priority order>
```

Stop after the first FAIL in phases 1-2 (build/types must pass before other checks are meaningful). Continue through all phases for phases 3-6.
