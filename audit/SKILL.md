---
name: audit
description: Audit project against golden principles, produce scorecard. Use for /audit, "check project quality". NOT for system setup health (/harness-audit) or eval scoring (/eval-score).
model: sonnet
effort: medium
allowed-tools: Read, Bash, Glob, Grep
---

# Audit: Project Quality Scorecard

**EXECUTE this skill now.** Follow the workflow steps below using the provided $ARGUMENTS. Do NOT describe, summarize, or explain this skill — run it.

## Constants

- `PRINCIPLES_DIR`: `C:/Users/gurusharan.gupta/Agents/Claude Code/principles`
- `PRINCIPLES_INDEX`: `C:/Users/gurusharan.gupta/Agents/Claude Code/principles/_index.json`
- `MANIFEST_PATH`: `C:/Users/gurusharan.gupta/Agents/Claude Code/manifest.json`

## Commands

Parse $ARGUMENTS to determine action:
- `/audit` — Audit the current project
- `/audit <project-id>` — Audit a specific registered project by ID
- `/audit all` — Audit all active projects in the manifest
- `/audit principles` — List all golden principles with descriptions

## Workflow: Audit a Project

### Step 1: Identify Target

If no argument, use the current working directory.
If a project-id is given, look it up in the manifest to get the path.
If `all`, iterate over all active projects.

### Step 2: Read Principles

Read `PRINCIPLES_INDEX` to get the list of all principles with severity and enforcement method.

### Step 3: Check Each Principle

For each principle, run the appropriate check against the project directory:

**claude-md-required** (critical):
- Check: `CLAUDE.md` or `.claude/CLAUDE.md` exists
- Check: File is under 150 lines
- Check: Contains "## Commands" and "## Architecture" sections

**formatting-configured** (critical):
- Check for JS/TS: `.prettierrc`, `.prettierrc.json`, `prettier` in package.json, `.eslintrc*`, `eslint.config.*`
- Check for Python: `pyproject.toml` with `[tool.black]` or `[tool.ruff]`, `.flake8`, `setup.cfg` with flake8
- Check for Rust: `rustfmt.toml` or `.rustfmt.toml`
- Check for Go: always passes (gofmt built-in)
- If no recognized tech stack: SKIP (not applicable)

**tests-required** (critical):
- Check for JS/TS: `jest.config.*`, `vitest.config.*`, `*.test.*` or `*.spec.*` files exist, `"test"` script in package.json
- Check for Python: `pytest.ini`, `pyproject.toml` with `[tool.pytest]`, `tests/` directory, `test_*.py` files
- Check for Rust: `#[test]` in source files or `tests/` directory
- If no recognized tech stack: check for any `test` directory

**parse-at-boundaries** (critical):
- Cannot be mechanically checked fully. Check proxy indicators:
- For JS/TS: Zod, joi, yup, or io-ts in dependencies
- For Python: Pydantic in requirements
- Otherwise: MANUAL (flag for human review)

**semantic-file-naming** (recommended):
- Check: No files named `helpers.*`, `utils.*`, `common.*`, `misc.*`, `shared.*` at any level
- Use glob to find violations

**no-utils-helpers-dirs** (recommended):
- Check: `find $PROJECT -type d -name "utils" -o -name "helpers" -o -name "misc" -o -name "common" -o -name "shared"`
- Exclude `node_modules/`, `venv/`, `.git/`

**structured-logging** (recommended):
- Check proxy: structured logging library in dependencies (winston, pino, bunyan for JS; structlog, python-json-logger for Python)
- If no dependencies found: MANUAL

### Step 4: Check Additional Quality Signals

Beyond principles, check:
- `docs/` directory exists with exec-plans/, design-docs/ subdirectories
- `.claude/` directory exists
- `.git/` initialized
- Active exec-plans present and not stale (>30 days since last progress update)

### Step 5: Calculate Quality Score

Scoring:
- Start at 100 points
- Each FAILED critical principle: -20 points
- Each FAILED recommended principle: -10 points
- Each FAILED suggested principle: -5 points
- Missing docs/ structure: -10
- Missing .git/: -10
- Stale exec-plans: -5

Grade:
- A: 90-100
- B: 75-89
- C: 60-74
- D: 40-59
- F: 0-39

### Step 6: Output Scorecard

```
╔══════════════════════════════════════════════════╗
║  Audit: {project_name}                           ║
║  Path:  {project_path}                           ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  Golden Principles:                              ║
║    ✓ parse-at-boundaries          PASS           ║
║    ✗ claude-md-required           FAIL (missing) ║
║    ✗ tests-required               FAIL (no config)║
║    ✗ formatting-configured        FAIL           ║
║    ✓ semantic-file-naming         PASS           ║
║    ✓ no-utils-helpers-dirs        PASS           ║
║    ~ structured-logging           MANUAL         ║
║                                                  ║
║  Infrastructure:                                 ║
║    docs/ structure                MISSING        ║
║    .claude/ config                PRESENT        ║
║    .git/ initialized              MISSING        ║
║    Active exec-plans              NONE           ║
║                                                  ║
║  Score: 40/100                                   ║
║  Grade: D                                        ║
║                                                  ║
║  Critical issues (fix first):                    ║
║    1. Run /init-project to create CLAUDE.md      ║
║    2. Add test framework for Python              ║
║    3. Add formatter (black/ruff) config          ║
║                                                  ║
╚══════════════════════════════════════════════════╝
```

### Step 7: Update Manifest (optional)

If the user wants to persist the score, update the project's entry in manifest.json with:
```json
"quality_score": {
  "grade": "D",
  "score": 40,
  "last_audit": "2026-03-26",
  "critical_failures": 3,
  "recommended_failures": 0
}
```

## Workflow: List Principles

When the user runs `/audit principles`:

Read all principle files and display:

```
Golden Principles (7):

  CRITICAL:
    parse-at-boundaries      All external data parsed at boundary into typed representations
    tests-required           All new code must have tests, target 100% coverage
    formatting-configured    Automated formatting/linting configured before agent work
    claude-md-required       CLAUDE.md must exist following table-of-contents pattern

  RECOMMENDED:
    semantic-file-naming     Files/dirs use domain-specific names, not generic labels
    no-utils-helpers-dirs    No utils/, helpers/, misc/ directories
    structured-logging       Structured logging (JSON/key-value) in production code
```

## Important

- Audit is read-only. Never modify project files during an audit.
- MANUAL checks should be flagged clearly — they require human judgment.
- Always suggest specific remediation actions for each failure.
- The /init-project skill can fix most infrastructure-level failures.
- Quality scores are informational. They help prioritize cleanup, not block work.
