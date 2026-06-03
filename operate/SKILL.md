---
name: operate
description: Run the autonomous control plane loop — orient, identify, act, verify, update, introspect. Use for /operate, "run the loop", "what needs doing". NOT for single-task work — use specific skills instead.
model: sonnet
effort: high
allowed-tools: Read, Write, Bash, Glob, Grep, WebSearch, WebFetch, Agent
---

# Operate: Autonomous Control Plane Loop

**EXECUTE this skill now.** Follow the workflow steps below using the provided $ARGUMENTS. Do NOT describe, summarize, or explain this skill — run it.

You are the operator of a Claude Code control plane. Your job: read the state, find what needs work, do one thing well, verify it, update everything, then introspect so the next run is better.

This skill runs headless — no browser, no dashboard UI. You read `manifest.json` and `eval/state.json` directly. The dashboard is rebuilt at the end for human inspection later.

## Constants

- `REGISTRY`: `C:/Users/gurusharan.gupta/Agents/Claude Code`
- `MANIFEST`: `C:/Users/gurusharan.gupta/Agents/Claude Code/manifest.json`
- `STATE`: `C:/Users/gurusharan.gupta/Agents/Claude Code/eval/state.json`
- `HISTORY`: `C:/Users/gurusharan.gupta/Agents/Claude Code/eval/history/eval-history.json`
- `CRITERIA_DIR`: `C:/Users/gurusharan.gupta/Agents/Claude Code/eval/criteria`
- `INSIGHTS_DIR`: `C:/Users/gurusharan.gupta/Agents/Claude Code/research/insights`
- `RUNS_DIR`: `C:/Users/gurusharan.gupta/Agents/Claude Code/eval/runs`

## The Loop

### Step 1: ORIENT

Read `MANIFEST` and `STATE`. Extract:

```
- generated_at: when was manifest last rebuilt?
- skills: count by scope (global/plugin), list names
- eval_scores: latest score per workflow, any below 80?
- eval_state.skill_baselines: which skills scored, which null?
- eval_state.next_priorities: the priority queue
- eval_state.dead_ends: approaches to never retry
- eval_state.completed_actions: recent history (last 5)
- research_insights: count, date of most recent
- projects: active vs archived
```

Print a 10-line status summary. This is your situational awareness.

### Step 2: IDENTIFY

Pick exactly **one** action for this run. Decision tree:

1. If `next_priorities` is non-empty → take the first item. This is the highest-signal work.
2. If `next_priorities` is empty, scan for:
   - **Regressions**: any workflow whose latest score is lower than its baseline in `skill_baselines` → fix it
   - **Low scores**: any workflow scoring below 80 → improve it
   - **Unscored skills**: skills in `skill_baselines` with `score: null` that have no criteria file in `CRITERIA_DIR` → create criteria
   - **Stale research**: if the newest insight file in `INSIGHTS_DIR` is older than 30 days → research new articles
   - **Cleanup**: archived projects still referenced in state, dead files, stale entries → clean up
3. If nothing needs work → print "Control plane healthy. No action needed." and skip to Step 6.

Print: `ACTION: <what you're going to do and why>`

Before acting, check `dead_ends` — if your planned approach is listed there, pick a different approach or skip.

### Step 3: ACT

Execute based on the action type. Each action type has a bounded scope.

#### Research
- Use WebSearch to find 1-2 relevant engineering articles or blog posts about the topic
- For each article, use WebFetch to get the content
- Extract insights following the research skill pattern:
  - Create `INSIGHTS_DIR/{date}-{slug}.md` with frontmatter (title, source_url, tags) and sections (Insight, Evidence, Applicability)
  - Update `research/sources.json` with the new entry
- Max 2 articles per run

#### Create Criteria
- Read the target skill's SKILL.md to understand what it does, its allowed-tools, and output artifacts
- Create `CRITERIA_DIR/<name>.json` with a mix of automatable checks (file_exists, file_contains, command_passes) and manual checks
- Aim for 50%+ automatable checks
- Run `python3 bin/eval-score.py <name>` to validate the criteria work

#### Optimize Skill
- Read the skill's current SKILL.md and its latest eval scores
- Identify one specific improvement (clearer instructions, better constraints, missing edge case)
- Make the change
- Score before and after — keep only if score improves or holds

#### Fix
- Read the error or issue description from the priority
- Diagnose root cause by reading relevant files
- Apply the minimal fix
- Verify the fix resolves the issue

#### Cleanup
- Remove stale references, archive old data, prune state.json
- Never delete user projects — only move to `_archive/`
- Never modify managed config files

### Step 4: VERIFY

After acting, verify the change didn't break anything:

```bash
python3 bin/eval-score.py <affected-workflow>
```

Compare the new score to the prior score (from `skill_baselines`).

- **Score improved or held** → proceed to Step 5
- **Score regressed** → revert the change, log the approach as a `dead_end` in state.json, print `REGRESSION: <workflow> dropped from <old> to <new>. Reverted.`

If the action was research or cleanup (no eval workflow), skip scoring — verify by checking the files exist and are valid.

### Step 5: UPDATE

Rebuild everything so the changes are visible:

```bash
cd "C:/Users/gurusharan.gupta/Agents/Claude Code" && python3 bin/scan.py
```

This rebuilds manifest.json, auto-syncs skill baselines in state.json, and copies manifest to dashboard/public/.

Then rebuild the dashboard:

```bash
cd "C:/Users/gurusharan.gupta/Agents/Claude Code/dashboard" && npx vite build
```

Finally, update `STATE` directly:
- Move the completed priority from `next_priorities` to `completed_actions` with today's date and a result summary
- Add any new `dead_ends` discovered during this run
- If new priorities were discovered, append them to `next_priorities`

### Step 6: INTROSPECT

Run `/introspect` skill now. It handles quadrant classification, side effects (memory files, dead_ends, CLAUDE.md fixes), and the summary table. Do not re-implement inline.

### Step 7: REPORT & LOG

Write the run report to a log file **and** print it. This is the persistent record of what happened.

**Log path:** `REGISTRY/eval/runs/{YYYY-MM-DD}T{HH-MM}.md`

Use the current UTC timestamp for the filename. Write this exact structure:

```markdown
# Operate Run — {date} {time} UTC

## Status at Start
{the 10-line orient summary from Step 1}

## Action
**Priority:** {what was picked and why}
**Type:** {research|create-criteria|optimize-skill|fix|cleanup|none}
**Details:** {what was actually done — files created, edits made, commands run}

## Verification
**Workflow:** {name}
**Score before:** {N}
**Score after:** {N}
**Result:** {improved|held|regressed|skipped}

## State Changes
- completed_actions: +1 ({action name})
- dead_ends: +{N} ({names if any})
- next_priorities: {count remaining}
- skill_baselines: {any score changes}

## Introspection
| Finding | Quadrant | Action Taken |
|---------|----------|-------------|
| {description} | {KEEP/FIX/REMOVE/OPTIMIZE} | {what was done} |

## Summary
{1-2 sentence takeaway}
```

Also print this report to stdout so it appears in the conversation.

## Constraints

These are hard limits. Do not exceed them.

- **One priority per run.** Finish it fully before stopping. Don't start a second.
- **Research: max 2 articles.** Quality over quantity. Extract actionable insights, not summaries.
- **Experiments: 1 mutation → score → keep/revert.** No multi-step changes without verification between each.
- **Never delete user projects.** Move to `_archive/` only. Escalate if unsure.
- **Never modify managed config.** `~/.claude/settings.json`, `~/.claude/remote-settings.json`, and hook configurations are off-limits.
- **Log everything.** Every action goes into `state.json` `completed_actions`. Every failed approach goes into `dead_ends`.
- **Check dead_ends before acting.** If your planned approach is listed, don't retry it.
- **Uncertain? Skip and note.** Add to `next_priorities` with a `?:` prefix explaining what's unclear. Don't guess on high-stakes changes.
