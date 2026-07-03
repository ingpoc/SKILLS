---
name: requirements-gap-audit
description: "Use when the operator asks what is pending, whether the app is complete, which screens/flows/buttons are missing or broken, whether PROGRESS.md tracks requirements, or whether missing mockups should be generated. Defaults to scan mode; apply mode updates PROGRESS.md and may generate/store mockups only after explicit user approval."
allowed-tools: Bash
---

# requirements-gap-audit

> **Self-validate after edits.** Any change to this skill's files must be followed by `./scripts/validate.sh`.

Find what is still missing before agents keep polishing the same known screens.

## Modes

- **scan** default: read-only. Produce gaps, proposed `PROGRESS.md` additions, missing mockup targets, and image prompts. Do not edit or generate.
- **apply**: only after explicit user approval. Update `PROGRESS.md`; generate approved mockups through `imagegen`; save them under the repo mockup folders.

If the user says "create/update the backlog", "generate the missing mockups", "apply", or approves your scan proposal, switch to apply. Otherwise stay scan.

## Inputs

Load the narrowest current route first:

1. `npm run goal:next`
2. `git status --short`
3. `GOAL.md`, `goal.json`, `PROGRESS.md`
4. `DESIGN.md`, `docs/product-direction.md`, `docs/workflows/validation.md`
5. `mockups/ios/`, `mockups/macos/`
6. native app source, API client/state, backend routes, seed scripts, validation scripts

For Like-minded-style repos, also run the repo entrypoint if present:

```sh
./script/project_context.sh query --task "requirements gap audit"
```

## Scan Flow

1. Build an expected surface map from `GOAL.md`, `DESIGN.md`, product docs, mockups, existing controls, and user request.
2. Build an implemented surface map from app views, navigation, API clients, backend routes, seed data, and validation scripts.
3. Runtime-test representative critical paths when tools are available:
   - open tabs/screens
   - tap visible buttons/cards
   - type into fields
   - open sheets/details
   - verify backend-backed state changes where possible
4. Classify every gap:
   - missing screen
   - missing mockup/reference
   - present but static/fake
   - present but broken at runtime
   - missing backend wiring
   - missing seed data
   - missing validation
   - missing `PROGRESS.md` requirement
5. Compare gaps against `PROGRESS.md`. If a required item is not tracked, propose the smallest phase/location and success criteria.

Use exactly one `explorer` or project subagent per disjoint scan slice when useful:
- native surface/runtime interactions
- backend/data/seed wiring
- validation/release coverage

Main agent owns judgment and any apply edits.

## Mockup Policy

Missing mockups are requirements, not permission to invent product.

In scan mode:
- list missing mockups
- propose target paths, for example `mockups/ios/21-privacy-settings.png`
- propose concise `imagegen` prompts
- stop for approval

In apply mode:
- use `imagegen` only for approved missing mockups
- save outputs into `mockups/ios/` or `mockups/macos/`
- never overwrite existing mockups; use the next numbered filename
- never leave project-referenced assets only under `$CODEX_HOME/generated_images`
- update `PROGRESS.md` with the mockup path and implementation success criteria

Before using `imagegen`, load the `imagegen` skill and follow its save-path rules.

## PROGRESS.md Additions

Add only requirements grounded in at least one source:
- `GOAL.md`
- `DESIGN.md`
- product docs
- existing app controls
- existing mockups
- explicit user request

Each added item must include success criteria:
- screen exists
- key controls are tappable
- backend/API/DB wiring exists when the feature persists or loads data
- seed data exists when validation needs realistic state
- validation command or manual runtime proof is named
- mockup path is named when visual reference is required

Do not add a giant backlog. Group adjacent tiny gaps under the smallest coherent phase/surface.

## Output

Scan mode output:

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

Apply mode closeout:
- files changed
- mockups saved
- validators run
- remaining gaps

## Hard Rules

1. Default to scan. Ask before editing `PROGRESS.md` or generating mockups.
2. Do not invent scope. Ground every requirement in source evidence.
3. Runtime evidence beats static screenshots for controls and flows.
4. Static build success is insufficient for buttons, fields, sheets, custom cards, and backend state.
5. Keep one roadmap owner: update `PROGRESS.md`; do not create a competing backlog doc.
6. Stop at the smallest useful diff in apply mode.

## References

- [references/surface-scan-prompt.md](references/surface-scan-prompt.md)
- [scripts/requirements_surface_grep.sh](scripts/requirements_surface_grep.sh)
