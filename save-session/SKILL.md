---
name: save-session
description: "Snapshot only resume-relevant tactical context and an explicitly resumable Codex goal to `.claude/session-data/CURRENT.md`. Triggers: `/save-session`, `save session`, `save progress`, `checkpoint`. Use when the next agent needs a compact, time-bounded handoff with the exact goal, first action, validation, blockers, route, and context to avoid. Do not capture noisy recent files or treat the checkpoint as permanent truth. Use the shell command `save-session` for the deterministic write path."
allowed-tools: Bash, get_goal
---

# save-session — tactical checkpoint

> **Self-validate after edits.** Any change to this skill's files (SKILL.md, scripts/, references/, templates/, assets/) must be followed by `./scripts/validate.sh` from the skill directory. Hard findings → create-skill Optimize lane.

This skill exists to preserve the transient context that durable docs usually omit: what the operator was actively doing, what should happen first next time, what was already verified, and which small set of local files or commits matter at handoff.

When the session exposed preventable friction, use `session-introspection` before writing the checkpoint. Save the highest-value prevention control in the checkpoint so the next agent can continue from the control decision instead of rediscovering the same inefficiency.

## Operating contract

| Field | Decision |
|---|---|
| Primary archetype | deterministic script workflow |
| Secondary archetypes | reference workflow |
| Operator trigger | `/save-session`, `save session`, `save progress`, `checkpoint` |
| Output | `.claude/session-data/CURRENT.md` written at the git root or current directory |
| Success evidence | command prints the checkpoint path; the file exists with a fresh timestamp and an explicit `codex_goal` section |
| Deterministic surface | the global shell command `save-session` |
| Judgment surface | deciding what the next agent needs and what should be omitted |
| Context loading | run `session-introspection` first only when preventable friction occurred; otherwise no prior file read required |

## Main flow

### Preflight

1. Resolve the target root with `git rev-parse --show-toplevel` when inside a repo; otherwise use the current working directory.
2. If the current session had material, preventable friction, run `session-introspection` first and keep only its highest-value finding/control for the checkpoint.
3. Prefer the installed `save-session` shell command. If it is unavailable, reproduce its behavior with Bash only.
4. Call `get_goal`. If the current task has an unfinished goal that should
   continue in a fresh task, pass its exact objective as
   `SAVE_SESSION_GOAL_OBJECTIVE` with
   `SAVE_SESSION_GOAL_RESUME_POLICY=ensure-active`. Do not infer a goal from
   `working_on` prose, and do not checkpoint completed or blocked goals as work
   to reactivate. Use `reference-only` when the objective is useful history but
   must not be recreated.
5. If the current session has any nuance, pass curated context via environment variables before invoking the command. Prefer explicit handoff content over inferred filesystem recency:
   - `SAVE_SESSION_ROOT` — explicit project root when an unrelated ancestor (for example `$HOME`) is also a Git worktree
   - `SAVE_SESSION_GOAL_OBJECTIVE` — exact objective returned by `get_goal`; never a shortened paraphrase
   - `SAVE_SESSION_GOAL_RESUME_POLICY` — `ensure-active` or `reference-only`
   - `SAVE_SESSION_RESUME_WINDOW_HOURS` — automatic-resume eligibility window, 1–168 hours; defaults to 24
   - `SAVE_SESSION_HANDOFF_FOCUS`
   - `SAVE_SESSION_WORKING_ON`
   - `SAVE_SESSION_NEXT_ACTION`
   - `SAVE_SESSION_BLOCKERS`
   - `SAVE_SESSION_LEARNINGS`
   - `SAVE_SESSION_VERIFICATION_STATE`
   - `SAVE_SESSION_INTROSPECTION`
   - `SAVE_SESSION_RELEVANT_FILES`
   - `SAVE_SESSION_RELEVANT_COMMITS`
   - `SAVE_SESSION_AVOID`
   - `SAVE_SESSION_USEFUL_COMMANDS`
   - `SAVE_SESSION_ROUTE_ID`
   - `SAVE_SESSION_ROUTE_OWNER`
   - `SAVE_SESSION_FIRST_COMMAND`
   - `SAVE_SESSION_STOP_CONDITION`
   - `SAVE_SESSION_ALLOWED_BEFORE_FIRST_COMMAND`
   - `SAVE_SESSION_AVOID_BEFORE_FIRST_COMMAND`
6. Raw `git status` is intentionally omitted by default. Set `SAVE_SESSION_INCLUDE_GIT_STATUS=1` only when the raw status itself is useful to the next agent.

### Do

```bash
save-session
```

Optional richer invocation:

```bash
SAVE_SESSION_HANDOFF_FOCUS="Resume from the last validated result, not from broad repo discovery." \
SAVE_SESSION_GOAL_OBJECTIVE="Complete the exact accepted objective without shrinking its exit gate." \
SAVE_SESSION_GOAL_RESUME_POLICY="ensure-active" \
SAVE_SESSION_WORKING_ON="Tightening save/resume checkpoint quality so next-session context stays small and actionable." \
SAVE_SESSION_NEXT_ACTION="Run the save-session validation script, regenerate CURRENT.md once, inspect it for noise, then commit the skill change in ~/.codex." \
SAVE_SESSION_BLOCKERS="None." \
SAVE_SESSION_LEARNINGS="Recent-file inference polluted checkpoints with cache/db artifacts; require curated relevant files instead." \
SAVE_SESSION_VERIFICATION_STATE="Wrapper patched; validation still pending." \
SAVE_SESSION_INTROSPECTION="session-introspection: prevent future noisy checkpoints by preferring curated handoff fields over filesystem recency." \
SAVE_SESSION_RELEVANT_FILES=$'/Users/gurusharan/.codex/skills/save-session/SKILL.md\n/Users/gurusharan/.local/bin/save-session' \
SAVE_SESSION_AVOID="Do not include cache files, generated DB files, broad untracked status, or historical discussion not needed for the next action." \
save-session
```

### What To Capture

Capture only context that changes the next agent's first 5 minutes:

- the active objective and why it matters now
- the exact unfinished Codex goal and whether resume should ensure it is active
- a bounded resume window appropriate for tactical state; old checkpoints must be reviewed, not auto-restored
- the first concrete next action
- a known route owner, first command, and stop condition when the next lane is already known
- validation already run and validation still pending
- the `session-introspection` finding/control when this session exposed preventable friction
- unresolved blockers or decisions
- files, docs, commits, branches, or commands that are directly relevant
- caveats that prevent the next agent from following stale or tempting-but-wrong context

### What To Omit

Omit anything the next agent can cheaply retrieve or should not trust without rechecking:

- generated caches, databases, build outputs, logs, and broad recent-file lists
- raw git status for large dirty repos unless status ordering itself matters
- long prose history, old alternatives, and completed debate
- durable doctrine that belongs in context graph, workflow docs, AGENTS.md, project docs, or memory
- speculative conclusions that were not verified

### Closeout

1. If the session produced an accepted durable repo decision and the repo has a context-graph recorder such as `./script/project_context.sh record-decision`, record that decision before saving the tactical checkpoint.
2. If the session touched multiple docs, routing surfaces, AGENTS files, workflows, skills, or durable decisions, run a cheap read-only subagent or equivalent scan for stale prose, stale routing, duplicate routing, and owner conflicts. The scan returns only candidate file/line/reason; the main agent decides edits. Skip this for small single-surface handoffs.
3. Remove or demote confirmed stale/duplicate routing before writing the checkpoint, then run the narrowest available validator for touched surfaces.
4. Include the durable decision key in `SAVE_SESSION_LEARNINGS`, `SAVE_SESSION_NEXT_ACTION`, or `SAVE_SESSION_ROUTE_OWNER` when it changes what the next agent should retrieve first.
5. Confirm the command reported the output path.
6. Inspect `## codex_goal`: its objective must exactly match `get_goal`, or be
   explicitly empty/reference-only. Never silently shorten completion criteria.
7. If useful, mention the path in the final response so the next session can `resume-session`.
8. Do not treat the checkpoint as durable project memory; it is tactical handoff only.

#### Friction introspection

| Friction source | Action |
|---|---|
| Missing command or broken write path | Fix the global wrapper in `~/.local/bin/` and keep this skill aligned |
| Checkpoint content too generic for repeated work | Supply curated environment variables or improve the wrapper defaults |
| Session exposed preventable friction | Run `session-introspection` first and save the highest-value control in `SAVE_SESSION_INTROSPECTION` |
| Known next lane still resumes through broad discovery | Set `SAVE_SESSION_FIRST_COMMAND`, `SAVE_SESSION_ROUTE_OWNER`, and `SAVE_SESSION_STOP_CONDITION` |
| Active goal would be lost in a fresh task | Pass the exact `get_goal` objective with `SAVE_SESSION_GOAL_RESUME_POLICY=ensure-active` |
| Multi-surface closeout risks stale or duplicate routing | Use a cheap read-only subagent/scan; main agent owns any cleanup and validation |
| Checkpoint contains cache/generated files | Treat it as a wrapper defect; do not rely on filesystem recency as handoff context |
| Repo needs durable decisions, not tactical notes | Use the repo's durable owner first: context graph when present, otherwise project docs or memory |

## Hard rules

1. **Write tactically, not permanently.** This skill is for handoff context, not long-term doctrine.
2. **Prefer repo root.** Store the checkpoint at the git root when one exists so future sessions find it predictably.
3. **Stay concise.** The checkpoint should guide the next move, not recreate the entire session.
4. **Use Bash for the actual write.** The deterministic command is the source of truth for file creation.
5. **Prefer curated context over inferred context.** Auto-detected files and raw status are fallback diagnostics, not handoff content.
6. **Known routes need first commands.** When the next lane is known, save the route owner and first command instead of prose like "run normal repo retrieval."
   If `SAVE_SESSION_FIRST_COMMAND` is set and no explicit `SAVE_SESSION_NEXT_ACTION` is supplied, the wrapper must derive `next_action` from that first command instead of using generic retrieval prose.
   If `SAVE_SESSION_HANDOFF_FOCUS` is also absent, derive `handoff_focus` from the first command so resume starts narrow.
7. **Prevent recurrence before handoff.** When the session found avoidable friction, run `session-introspection` before writing the checkpoint and keep only its compact control decision.
8. **Do not delegate checkpoint judgment.** Subagents may only scan for stale or duplicate context; the main agent records durable decisions, edits owner surfaces, validates, and writes the checkpoint.
9. **Goals are explicit and exact.** Save only a goal returned by `get_goal` or
   explicitly supplied by the operator. Never derive, summarize, or expand it.
10. **Completion state matters.** Use `ensure-active` for incomplete work intentionally eligible for continuation, including a blocked goal that may resume after its external gate changes. Use `reference-only` for completed, abandoned, or superseded work.
11. **Resumability expires.** `ensure-active` is only a candidate within `SAVE_SESSION_RESUME_WINDOW_HOURS`; it never makes tactical state permanently authoritative.

## Cross-references

- [scripts/validate.sh](scripts/validate.sh) — audit wrapper for this skill
- [scripts/save-session](scripts/save-session) — committed source for the deterministic write implementation
- [scripts/test_save_session.sh](scripts/test_save_session.sh) — deterministic goal-checkpoint tests
- `~/.local/bin/save-session` — deterministic write implementation
- sibling skill: `resume-session`

## Why this skill exists

This prevents a common failure mode at session boundaries: the next agent can see the files and git diff, but not the exact tactical intent or the first best next step. A compact repo-local checkpoint is cheaper and more reliable than reconstructing that context from scratch.
