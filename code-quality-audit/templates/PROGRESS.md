# PROGRESS.md

> Last audit: {{ISO_TIMESTAMP}}
> Auditor turn: {{AUDITOR_TURN}}
> Commit: {{COMMIT}}
> Status: partial

## Audit Summary

- Files scanned: 0
- Defects (must fix): 0
- Risks (should fix): 0
- Smells (nice to fix): 0
- Cross-cutting issues: 0
- Highest-risk module: `unknown` - audit not run yet

## System Map

Audit not run yet.

## Current Audit - Checklist for Next Turn

Ranked by impact times likelihood. Execute top-down. Do not skip ahead.

### DEFECTS

No findings recorded yet.

### RISKS

No findings recorded yet.

### SMELLS

No findings recorded yet.

### CROSS-CUTTING

No findings recorded yet.

## Execution Rules for Next Turn

The next agent reads this section before touching any code.

1. Work top-down. Do not skip items.
2. One checklist item per change unit. Small, reviewable commits.
3. Items marked `requires-approval` or `migration-needed` - stop and ask the
   human before editing.
4. After completing an item: move it to `## Completed` with commit hash, date,
   and actual verification result. Do not just check the box.
5. If a fix surfaces new findings, append them to `## Current Audit` with
   prefix `[discovered-{{AUDITOR_TURN}}]`. Do not silently expand the scope of
   the current item.
6. If an item turns out to be wrong, unreachable, or out-of-scope, move it to
   `## Rejected` with a one-line reason. Never delete.
7. Re-run the auditor prompt after every 5 completed items, or immediately
   after any cross-cutting fix.

## Completed

{{COMPLETED_SECTION}}

## Rejected

{{REJECTED_SECTION}}
