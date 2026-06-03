---
name: skill-quality-gate
description: "Audit a skill against Anthropic's production best practices (9-point scorecard). Use after creating or improving any skill via /skill-creator. Also use when user says 'audit skill', 'check skill quality', 'review my skill', or wants to validate a skill before distribution. NOT for project-level audits (/audit) or harness health (/harness-audit)."
---

# Skill Quality Gate

9-point audit based on how Anthropic builds skills in production (hundreds in active use). Run after `/skill-creator` finishes, or standalone on any skill directory.

## Usage

`/skill-quality-gate <path-to-skill-directory>`

If no path provided, ask which skill to audit. Accept skill name and resolve to `~/.codex/skills/<name>/`.

## Gotchas

| Gotcha | What happens | Do instead |
|--------|-------------|------------|
| Imperative counter has false positives | `audit.sh` counts MUST/NEVER inside markdown tables, examples, and quoted text — not just instructions. A skill with "Example of bad: NEVER do X" gets penalized for demonstrating an anti-pattern. | When imperative count seems high, read the SKILL.md and manually discount imperatives in examples, tables, and quoted blocks before scoring. |
| `inline_bash_lines` conflates documentation with execution | Bash blocks that document what the agent *should do* (pseudocode, workflow description) inflate the count the same as actual scripts to execute. | Check whether inline bash is meant to be run literally or is illustrative. Only flag literal execution blocks as candidates for the `scripts` directory. |
| `set -euo pipefail` kills grep pipelines on zero matches | If extending `audit.sh`, any `grep pattern \| wc -l` pipeline will fail when grep finds no matches (exit 1 + pipefail). The script uses `gmatch()` wrapper to handle this. | Always use the `gmatch()` or `gcount()` helpers when adding new grep-based metrics. Never pipe raw grep with pipefail enabled. |
| Quick validation is the frontmatter source of truth | `audit.sh` can count suspicious keys and compatibility hints, but `quick_validate.py` is the canonical schema validator. A skill can look fine by heuristics and still be invalid. | Run `quick_validate.py` first. If it fails, Environment compatibility cannot score PASS even if the other metrics look healthy. |
| Asset-reference checks are heuristic | `audit.sh` only catches literal local asset paths mentioned in `SKILL.md`. Dynamic paths or prose-only references can evade the check. | Treat missing-asset counts as hard failures, but treat zero missing assets as necessary-not-sufficient and still inspect the workflow manually. |
| Scoring weights are opinionated | The 15%/10%/5% weights reflect subjective priority from Anthropic's article. Gotchas/Railroading/Env-compat are weighted highest because they cause the most real-world failures. Storage is 5% because most skills are stateless. | If a dimension weight feels wrong for a specific skill type, note it in the scorecard rather than silently adjusting. |

## Workflow

### Step 1: Run deterministic checks

```bash
python3 /Users/gurusharan/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-path>
~/.codex/skills/skill-quality-gate/scripts/audit.sh <skill-path>
```

`quick_validate.py` is the canonical frontmatter/schema validation pass.

`audit.sh` captures: line count, section count, workflow-step count, gotcha item count, imperative density, why-explanation count, frontmatter flags, inline bash blocks and lines, asset counts, and missing local asset references. Output is JSON — read it, don't show it raw.

### Step 2: Read the SKILL.md

Read the skill's SKILL.md to assess the subjective dimensions (category fit, gotchas quality, obvious knowledge, description trigger quality).

### Step 3: Score each dimension

Load `references/audit-criteria.md` for detailed pass/fail thresholds per dimension.

Score each of the 9 dimensions:

| # | Dimension | Source | Weight |
|---|-----------|--------|--------|
| 1 | Category classification | Subjective — does it fit one of 9 types? | 10% |
| 2 | Gotchas section | Script (`has_gotchas_section`, `gotcha_item_count`) + subjective quality | 15% |
| 3 | Script audit | Script (`script_count`, `inline_bash_blocks`, `inline_bash_lines`, `missing_script_references`) | 10% |
| 4 | Progressive disclosure | Script (`total_lines`, `section_count`, `workflow_step_count`, `reference_count`) | 10% |
| 5 | Railroading check | Script (`imperative.total`, `imperative_density_pct`, `why_explanations`) | 15% |
| 6 | Obvious knowledge | Subjective — is content mostly things Claude knows? | 10% |
| 7 | Environment compatibility | `quick_validate.py` + script (`unexpected_frontmatter_keys`, `missing_local_asset_references`) + manual | 15% |
| 8 | Storage audit | Subjective — where does skill persist data? | 5% |
| 9 | Description trigger quality | Script (`description_words`) + subjective | 10% |

Scoring: PASS (full weight), WARN (half weight), FAIL (zero).

### Step 4: Output scorecard

```
Skill Quality Gate: <skill-name>
Path: <skill-path>
Category: <best-fit category from the 9>

  #  Dimension              Score   Notes
  ─────────────────────────────────────────────
  1  Category fit           PASS    Code Scaffolding & Templates
  2  Gotchas section        WARN    2 real gotchas; needs at least 3
  3  Script audit           WARN    3 inline blocks, 24 inline bash lines, 1 script
  4  Progressive disclosure PASS    187 lines, 8 sections, 4 references
  5  Railroading            WARN    12 imperatives (4.2%), 3 why explanations
  6  Obvious knowledge      PASS    Content is project-specific
  7  Environment compat     FAIL    quick_validate failed: unexpected frontmatter key
  8  Storage audit          PASS    Uses .claude/progress/
  9  Description trigger    PASS    42 words, trigger-focused

  Overall: 7.5/10 (weighted)

  Priority fixes:
  1. [FAIL] Add Gotchas section — seed with 3+ real failure patterns
  2. [FAIL] Remove invalid frontmatter or missing assets until quick_validate passes
  3. [WARN] Move health-check inline bash into a dedicated script under `scripts/`
  4. [WARN] Railroading — rewrite 4 MUST/NEVER as "why" explanations
```

### Step 5: Offer to fix

After showing the scorecard, offer to fix FAIL items. Apply fixes one at a time, re-running the script audit after each to confirm the score improved. Don't batch — each fix should be verifiable.

## Scoring Thresholds

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 9-10 | Production-ready, follows Anthropic best practices |
| B | 7-8.9 | Good, minor improvements needed |
| C | 5-6.9 | Functional but has structural issues |
| D | 3-4.9 | Needs significant rework |
| F | 0-2.9 | Broken or hostile to the environment |

## References

| File | Load when |
|------|-----------|
| references/audit-criteria.md | Scoring each dimension (Step 3) |

## Scripts

| File | Purpose |
|------|---------|
| scripts/audit.sh | Deterministic metrics extraction (Step 1) |
| `python3 /Users/gurusharan/.codex/skills/.system/skill-creator/scripts/quick_validate.py` | Canonical frontmatter/schema validation (Step 1) |
