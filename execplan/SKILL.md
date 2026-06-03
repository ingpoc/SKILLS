---
name: execplan
description: Create living execution documents for complex multi-step tasks. Use for /execplan, "create a plan". NOT for quick tasks or code reviews — only structured phased planning.
model: opus
effort: high
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep
---

# ExecPlan: Living Execution Documents

**EXECUTE this skill now.** Follow the workflow steps below using the provided $ARGUMENTS. Do NOT describe, summarize, or explain this skill — run it.

Generate, manage, and complete ExecPlans — self-contained, outcome-focused design documents that guide agents through complex tasks.

## Constants

- `TEMPLATE_PATH`: `C:/Users/gurusharan.gupta/Agents/Claude Code/templates/execplan.md`
- `PRINCIPLES_DIR`: `C:/Users/gurusharan.gupta/Agents/Claude Code/principles`
- `MANIFEST_PATH`: `C:/Users/gurusharan.gupta/Agents/Claude Code/manifest.json`

## Commands

Parse $ARGUMENTS to determine action:
- `/execplan <description>` — Generate a new ExecPlan for the described task
- `/execplan list` — Show active and recently completed plans across all projects
- `/execplan complete <plan-file>` — Mark a plan as complete, fill Outcomes & Retrospective
- `/execplan` (no args) — Show usage help

## Workflow: Generate ExecPlan

### Step 1: Determine Project Context

Identify the current project. Read its CLAUDE.md if it exists. Understand:
- Tech stack (from package.json, requirements.txt, etc.)
- Directory structure
- Existing architecture patterns
- Active exec-plans (check `docs/exec-plans/active/`)

### Step 2: Read Template and Principles

Read the ExecPlan template from TEMPLATE_PATH.
Read `PRINCIPLES_DIR/_index.json` to know which golden principles apply.

### Step 3: Research the Task

Before writing the plan, thoroughly research:
- Which files will be affected? Read them.
- What existing patterns should be followed?
- What dependencies are involved?
- What tests exist that might be affected?
- Are there related exec-plans (active or completed)?

### Step 4: Generate the ExecPlan

Fill in the template with:

**Purpose / Big Picture**: What the user can do after this change that they can't do now. How to see it working. User-visible behavior.

**Context and Orientation**: Current state described for someone who knows nothing. Full paths to key files. Define all terms. No references to external docs — embed everything needed.

**Plan of Work**: Prose description of edits. Break into milestones if >1 logical phase. Each milestone must be independently verifiable.

**Concrete Steps**: Exact commands, working directories, expected outputs.

**Validation and Acceptance**: Observable behavior, not internal attributes.
- "After running X, observe Y"
- "Test Z fails before, passes after"

**Interfaces and Dependencies**: Prescriptive. Name libraries, types, function signatures.

**Idempotence**: Steps can be repeated safely. Include recovery for risky steps.

Initialize living sections:
- Progress: Empty checkboxes for each milestone step
- Surprises & Discoveries: "(none yet)"
- Decision Log: "(none yet)"
- Outcomes & Retrospective: "(to be filled at completion)"

### Step 5: Ensure Self-Containment

**Critical check**: Could a novice agent with ONLY this ExecPlan file execute the work end-to-end? If not, add missing context. Do not reference external docs, prior plans, or assumed knowledge.

Key rules:
- Every term of art must be defined in plain language
- Every file path must be full repository-relative
- Every command must include working directory
- Every expected output must be shown
- No "as described previously" or "see the architecture doc"

### Step 6: Save

Create directory if needed: `docs/exec-plans/active/`

Save to: `docs/exec-plans/active/{YYYY-MM-DD}-{slugified-title}.md`

Filename max 80 characters, lowercase, hyphens.

### Step 7: Report

```
ExecPlan created: docs/exec-plans/active/{filename}
Purpose: {1-sentence summary}
Milestones: {N}
Estimated scope: {files to modify}

Next: An agent can now execute this plan by reading the file and following the milestones.
```

## Workflow: List Plans

When the user runs `/execplan list`:

1. Read the manifest to get all registered projects
2. For each project, check for `docs/exec-plans/active/*.md` and `docs/exec-plans/completed/*.md`
3. Display:

```
Active Plans:
  Project       Plan                                  Created     Milestones
  ───────────────────────────────────────────────────────────────────────────
  powers        add-api-authentication                2026-03-26  3/5 done
  presentation  migrate-to-typescript                 2026-03-25  0/4 done

Recently Completed:
  powers        setup-test-infrastructure             2026-03-24  5/5 done
```

## Workflow: Complete Plan

When the user runs `/execplan complete <plan-file>`:

1. Read the plan file
2. Verify all Progress checkboxes are checked
3. If not all done, ask: "Plan has incomplete steps. Mark as complete anyway?"
4. Fill in Outcomes & Retrospective section:
   - What was achieved vs. original purpose
   - What remains (if anything)
   - Lessons learned
   - Time from first to last progress timestamp
5. Move the file from `docs/exec-plans/active/` to `docs/exec-plans/completed/`
6. Report the move

## Important

- ExecPlans are SELF-CONTAINED. A novice with only the plan can execute it.
- ExecPlans are LIVING DOCUMENTS. Update Progress, Surprises, Decision Log as work proceeds.
- ExecPlans are OUTCOME-FOCUSED. Define observable behavior, not code attributes.
- When implementing an ExecPlan: do not prompt for next steps — proceed to the next milestone. Resolve ambiguities autonomously. Commit frequently.
- One ExecPlan per significant task. Don't over-plan trivial changes.
- Plans must be idempotent: steps can be re-run safely.
