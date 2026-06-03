---
name: testing-tracker
description: Legacy compatibility tracker for repos already using the older `.claude` TEST-state workflow. Use only when maintaining that lifecycle. NOT for the Codex-first default baseline.
---

# Testing Tracker

Compatibility note: this skill is a `.claude`-era lifecycle surface. It is not part of the default Codex-first repo baseline.

Track browser testing progress across sessions. Reads feature-list.json, creates browser testing checklist with acceptance criteria, and tracks tested vs pending status.

**Automatic Behavior:** When executed, this skill automatically:

1. Shows testing status
2. If pending features exist → marks first pending as `in_progress`
3. Loads **testing skill** immediately
4. Never requires manual intervention to start testing

## Skill Execution Hierarchy (IMPORTANT)

testing-tracker → testing skill → browser-testing skill

| Skill | Loads | Purpose |
|-------|-------|---------|
| **testing-tracker** | testing skill | Manage test list, show status |
| **testing** | browser-testing skill | Run tests (unit + browser) |
| **browser-testing** | None | Execute browser automation |

**Rules:**

- testing-tracker NEVER loads browser-testing skill directly
- browser-testing skill is ONLY loaded by testing skill
- testing-tracker ONLY loads testing skill

## Core Workflow (Automatic)

| Step | Action | Skill Used |
|------|--------|------------|
| 1 | Show current testing status | testing-tracker |
| 2 | Find first pending feature | testing-tracker |
| 3 | **Automatically mark as `in_progress`** | testing-tracker |
| 4 | **Automatically load testing skill** | testing-tracker → testing |
| 5 | testing skill loads browser-testing skill | testing → browser-testing |
| 6 | Update status after testing | testing-tracker |

**No manual intervention required.** When you invoke testing-tracker, it immediately finds the next pending feature, marks it in_progress, and loads the testing skill.

## Autonomous Loop

After testing skill completes and returns:

1. Update feature status in testing-list.json (passed/failed)
2. Check testing-list.json for remaining pending features
3. If pending features exist:
   - Mark next pending as in_progress
   - Load testing skill again
   - LOOP (no human intervention needed)
4. If no pending features:
   - Show final testing summary
   - Transition state to COMPLETE
   - END (all features tested autonomously)

**Max features per session**: Process until context budget hits 70%, then checkpoint and stop.

**This is the control return path** — testing-tracker must regain control after each feature is tested to continue the autonomous loop.

## Scripts

| Script | Purpose |
|--------|---------|
| `initialize-testing-list.sh` | Create testing-list.json from feature-list.json |
| `get-next-to-test.sh` | Get next feature for browser testing |
| `start-next-test.sh` | Mark in_progress AND load testing skill |
| `mark-tested.py` | Mark feature as browser tested (Python - robust file handling) |
| `mark-in-progress.py` | Mark feature as in_progress (Python - robust file handling) |
| `show-testing-status.sh` | Show testing progress summary |

## Browser Test Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Not yet tested in browser |
| `in_progress` | Currently being tested |
| `passed` | Browser tests passed |
| `failed` | Browser tests failed |
| `skipped` | Intentionally skipped |

## Files (Project-Level Paths)

| File | Location | Purpose |
|------|----------|---------|
| `testing-list.json` | `.claude/progress/` | Browser testing status tracking |
| `feature-list.json` | `.claude/progress/` | Source of features to test |
| `state.json` | `.claude/progress/` | Current project state |

**Important:** All scripts use relative paths from the **project root** (current working directory). They operate on the **project-level** `.claude/progress/testing-list.json`, not the skill directory.
