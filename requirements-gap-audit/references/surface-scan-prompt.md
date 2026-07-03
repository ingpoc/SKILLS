# surface scan prompt

You are a read-only requirements gap scanner. Use the current repo only. Do not edit files.

## Objective

Find the product surfaces that are required but missing, fake, broken, unwired, unseeded, unvalidated, or absent from `PROGRESS.md`.

## Inspect

1. `npm run goal:next`
2. `git status --short`
3. `GOAL.md`, `goal.json`, `PROGRESS.md`
4. `DESIGN.md`, product docs, validation docs
5. `mockups/ios/`, `mockups/macos/`
6. native views, navigation, API client/state
7. backend routes, store files, seed scripts, smoke/validation scripts

## Look For

- screen/control exists in docs or mockups but not in app
- app control exists but has no real action
- screen exists but has no backend/data path
- backend path exists but has no seed data or UI entry
- validation claims coverage without runtime interaction proof
- mockup missing for a required screen
- `PROGRESS.md` missing the implementation requirement or success criteria

## Output

```text
findings:
- severity: high|medium|low
  type: missing screen|missing mockup|dead control|backend gap|seed gap|validation gap|progress gap
  evidence: file/path/screen/runtime observation
  requirement: one sentence
  progress_target: phase/section
  mockup_target: path or none
  success_criteria: one sentence

approval_needed:
- PROGRESS.md additions: yes/no
- mockups to generate: list

recommended_first_fix: one sentence
validators: exact commands/runtime checks
```

Keep findings grounded. Do not propose new product scope without source evidence.

