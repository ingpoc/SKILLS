---
name: eval
description: Scaffold PoC projects, test workflows against eval criteria. Use for /eval, "test this workflow". NOT for scoring (/eval-score) or improving (/autoimprove).
model: sonnet
effort: medium
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Eval: Test Workflows Against Fresh Agent Sessions

**EXECUTE this skill now.** Follow the workflow steps below using the provided $ARGUMENTS. Do NOT describe, summarize, or explain this skill — run it.

## Constants

- `EVAL_DIR`: `C:/Users/gurusharan.gupta/Agents/Claude Code/eval`
- `SCAFFOLDS_DIR`: `C:/Users/gurusharan.gupta/Agents/Claude Code/eval/scaffolds`
- `CRITERIA_DIR`: `C:/Users/gurusharan.gupta/Agents/Claude Code/eval/criteria`
- `HISTORY_PATH`: `C:/Users/gurusharan.gupta/Agents/Claude Code/eval/history/eval-history.json`
- `DEFAULT_TARGET`: `C:/Users/gurusharan.gupta/Agents/eval-poc`

## Commands

Parse $ARGUMENTS to determine action:
- `/eval scaffold <template> [target-path]` — Copy scaffold to target, init git
- `/eval criteria <workflow-name>` — Display eval checklist + prompts
- `/eval list` — List all criteria files with latest scores
- `/eval` (no args) — Show usage help

For scoring and history, use `/eval-score` (separate skill).

## Workflow: Scaffold

### `/eval scaffold <template> [target-path]`

1. Validate template exists in `SCAFFOLDS_DIR/<template>/`
   - Available templates: `node-api`, `python-cli`
2. Target path defaults to `DEFAULT_TARGET` if not specified
3. If target exists, ask: "Target exists. Delete and recreate? (y/n)"
4. Copy all files from scaffold to target:
   ```bash
   cp -r SCAFFOLDS_DIR/<template>/* <target>/
   cp -r SCAFFOLDS_DIR/<template>/.* <target>/ 2>/dev/null  # hidden files if any
   ```
5. Initialize git repo in target:
   ```bash
   cd <target> && git init && git add -A && git commit -m "Initial scaffold from eval/<template>"
   ```
6. Report:
   ```
   Scaffold created: <target>
   Template: <template>

   Deliberately missing: CLAUDE.md, .claude/, docs/, tests, formatting config

   Next steps:
     1. Open a NEW Claude Code session:  cd <target> && claude
     2. Use one of these prompts:
        Cold start:   "<prompt from criteria>"
        Explicit:     "<prompt from criteria>"
        Adversarial:  "<prompt from criteria>"
     3. After the agent finishes, return here and run:
        /eval score <workflow-name> <target>
   ```

## Workflow: Criteria

### `/eval criteria <workflow-name>`

1. Read `CRITERIA_DIR/<workflow-name>.json`
2. Display formatted checklist:
   ```
   Eval Criteria: <name>
   <description>

   Checks (N total, max score: 100):

     #  Weight  Severity     Type            Description
     ────────────────────────────────────────────────────────────────
     1    20    critical     file_exists     CLAUDE.md was created
     2     5    critical     file_contains   CLAUDE.md contains Commands section
     3    10    recommended  dir_exists      docs/exec-plans/active/ exists
     ...

   Test Prompts:
     Cold start:   "I have a Node.js API project..."
     Explicit:     "Run /init-project on this project..."
     Adversarial:  "This codebase is a mess..."
   ```

## Workflow: List

### `/eval list`

1. List all JSON files in `CRITERIA_DIR/` (exclude _template.json)
2. For each, read the file and find the latest score from history
3. Display:
   ```
   Available Eval Criteria:

     Name                Checks  Latest Score  Latest Grade  Runs
     ──────────────────────────────────────────────────────────────
     init-project        13      90/100        A             3
     golden-principles   8       —             —             0
     code-review         8       —             —             0
   ```

## Important

- Scaffolds are TEMPLATES — always copy, never modify the originals
- Each eval run should use a FRESH scaffold copy (no accumulated state)
- The key test is the COLD START — agent discovers workflow from global CLAUDE.md alone
- Score automated checks first, then ask for manual checks — minimize user effort
- Eval history is append-only — never delete or modify past entries
- When glob patterns are comma-separated, check each pattern independently and combine results
