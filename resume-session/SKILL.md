---
name: resume-session
description: "Inspect `.session/CURRENT.md`, surface the tactical handoff, and restore only an eligible explicit Codex goal. Triggers: `/resume-session`, `resume session`, `continue where I left off`, `pick up where we left off`. Use when a prior session may contain useful intent, but first reject stale, malformed, branch-diverged, commit-diverged, route-invalid, or reference-only checkpoints. Read legacy `.claude/session-data/CURRENT.md` only before `.session/` exists."
allowed-tools: Read, Bash, get_goal, create_goal
---

# resume-session — tactical-first session entry

> **Self-validate after edits.** Any change to this skill's files (SKILL.md, scripts/, references/, templates/, assets/) must be followed by `./scripts/validate.sh` from the skill directory. Hard findings → create-skill Optimize lane.

This skill exists to surface the most recent tactical checkpoint before doing broader repo discovery. It is a thin recovery layer, not a replacement for normal AGENTS, workflow, or validation loading.

## Operating contract

| Field | Decision |
|---|---|
| Primary archetype | deterministic script workflow |
| Secondary archetypes | reference workflow |
| Operator trigger | `/resume-session`, `resume session`, `continue where I left off`, `pick up where we left off` |
| Output | the contents of canonical `.session/CURRENT.md` plus restored goal state and a concise tactical synthesis |
| Success evidence | inspector classifies checkpoint eligibility; only a fresh, consistent explicit goal is matched or created without replacing another unfinished goal |
| Deterministic surface | the global shell command `resume-session` |
| Judgment surface | deciding how much of the checkpoint is still relevant before acting |
| Context loading | read checkpoint first, then continue with normal repo/workflow loading |

## Main flow

### Preflight

1. Honor `RESUME_SESSION_ROOT`, then search the current directory and its
   ancestors for the checkpoint. Only then use `git rev-parse`; never let a
   home-directory Git root displace a nested workspace checkpoint.
2. Look for `.session/CURRENT.md`. Use legacy `.claude/session-data/CURRENT.md` only before the canonical workspace exists.
3. Run `resume-session --inspect-json`. Its inspector is the sole owner of checkpoint freshness and consistency.
4. Treat `ensure-active` as a candidate, not permanent authority. Automatic restoration requires `eligibility: fresh`; `review-checkpoint` requires current owner-plan and repo evidence before selecting any goal.
5. A `reference-only`, missing, invalid, expired, future-dated, wrong-root, branch-diverged, commit-diverged, route-invalid, or chain-conflicting checkpoint must not auto-create a goal.

### Do

```bash
resume-session --inspect-json
resume-session
```

If the file exists, synthesize a short `From prior session` block with:

- where work left off
- saved Codex goal state, when explicitly present
- next action
- route owner, first command, and stop condition, if a `route_contract` is present
- blockers, if any
- notable learnings, if any

Before running any saved route command, restore only when the inspector returns
`mode: resume-exact-goal`:

1. Call `get_goal`.
2. If the current task already has the same unfinished objective, reuse it.
3. If the current task has no unfinished goal, call `create_goal` with the exact
   saved objective. Do not infer or shorten its completion criteria.
4. If a different unfinished goal exists, do not replace it. Report the
   conflict and wait for operator direction.
5. For `mode: choose-next-goal`, use the current owner plan instead of the checkpoint.
6. For `mode: review-checkpoint`, treat the saved objective as evidence only. Verify it against current owner and repo state; if still current, select it through the normal new-goal path rather than silently restoring it.

Goal restoration does not authorize resuming provider calls, deployment,
external sends, destructive actions, or any other gated saved next action.

If `route_contract.first_command` is present, verify it is still plausible for the current repo and run or inspect that command before broad workflow discovery. Otherwise continue with the repo’s normal retrieval path: AGENTS, workflow docs, validation docs, and current file state.

### Closeout

1. If the checkpoint is missing, say so plainly and fall back to normal repo discovery.
2. If the checkpoint is clearly stale or contradicted by the current repo state, call that out before continuing.
3. Do not auto-execute the saved next action without checking current repo evidence.
4. Do not mark a restored goal complete merely because the checkpoint was read;
   completion still requires the saved stop condition to be satisfied.

#### Friction introspection

| Friction source | Action |
|---|---|
| Missing checkpoint | Fall back cleanly; do not invent prior context |
| Checkpoint stale or misleading | Do not create its goal; prefer current owner/repo evidence and write a fresh checkpoint only after current intent is established |
| Checkpoint has known route fields | Use the saved first command as the narrowest starting point before broad retrieval |
| Explicit saved goal is absent in the current task | Create the exact saved objective before running the saved route |
| A different unfinished goal already exists | Preserve it, report the conflict, and do not replace it automatically |
| Read path broken | Fix the global wrapper in `~/.local/bin/` and keep this skill aligned |

## Hard rules

1. **Read first, verify second.** Use the checkpoint as a starting point, not as truth over the repo.
2. **No repository writes.** Inspection is read-only except for an optional private temporary exact-goal file used by orchestration.
3. **Be honest about staleness.** If the checkpoint conflicts with the repo, say so.
4. **Keep retrieval layered.** Tactical checkpoint first, then normal project context.
5. **Known route before generic retrieval.** A saved first command is a routing hint, not truth, but it should be checked before loading broad docs.
6. **Explicit goals only.** Restore the exact checkpointed objective; never
   manufacture a goal from ordinary `working_on` or `next_action` prose.
7. **Never replace unfinished work silently.** A different unfinished goal is
   a blocking conflict that requires operator direction.
8. **Freshness is deterministic.** Do not override inspector rejection merely because the operator opened a fresh task or invoked orchestration.

## Cross-references

- [scripts/validate.sh](scripts/validate.sh) — audit wrapper for this skill
- [scripts/resume-session](scripts/resume-session) — source of truth for the installed wrapper
- [scripts/inspect_checkpoint.py](scripts/inspect_checkpoint.py) — freshness, repo-consistency, route, and exact-goal classifier
- [scripts/test_checkpoint_inspector.py](scripts/test_checkpoint_inspector.py) — positive and negative eligibility cases
- [scripts/test_resume_session.sh](scripts/test_resume_session.sh) — deterministic root-resolution test
- `~/.local/bin/resume-session` — deterministic read implementation
- sibling skill: `save-session`

## Why this skill exists

This prevents the first few minutes of a resumed session from being wasted on reconstructing tactical intent from git status and filenames alone. A quick checkpoint read makes the next agent faster without pretending it replaces normal validation and repo discovery.
