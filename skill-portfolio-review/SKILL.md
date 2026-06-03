---
name: skill-portfolio-review
description: "Audit the entire skill portfolio for redundancy, misplacement, staleness, and context bloat. Use for /skill-portfolio-review, 'review my skills', 'clean up skills', 'are any skills redundant', or after adding 3+ new skills since last review. Produces DELETE/MERGE/REFRAME/KEEP recommendations per skill. NOT for auditing a single skill (/skill-quality-gate) or project quality (/audit)."
---

# Skill Portfolio Review

Portfolio-level audit of all skills as a collection. While `/skill-quality-gate` audits one skill's internal quality, this skill audits the fleet: are skills in the right surface, are any redundant, is context budget spent wisely?

## Gotchas

| Gotcha | What happens | Do instead |
|--------|-------------|------------|
| Recommending DELETE without checking dependencies | Hooks, cross-references, or CLAUDE.md triggers break silently | Always run dependency check (Step 3) before any DELETE recommendation |
| Counting imperative keywords in examples as railroading | A gotchas table containing "NEVER do X" inflates the imperative counter | Discount imperatives inside tables, examples, and quoted blocks |
| Classifying meta-skills as "doesn't fit taxonomy" without nuance | Some meta-skills (/operate) provide genuine value despite not fitting the 9 categories | Classify as "meta — justify keeping" rather than auto-DELETE |
| Merging skills that happen to overlap in description but differ in execution | save-session and introspect both mention "session" but do fundamentally different things | Read both SKILL.md files fully before recommending MERGE |

## Workflow

### Step 1: Collect fleet metrics

```bash
~/.claude/skills/skill-portfolio-review/scripts/portfolio-scan.sh
```

Captures per-skill: lines, imperatives, gotchas, references, scripts, description words, cross-references, stale references. Plus portfolio summary: total count, total lines, estimated index tokens.

### Step 2: Classify each skill

Load `references/taxonomy.md` for the decision tree. For each skill:

1. **Surface type test** — Is it a skill (judgment/branching) or a reference doc (pure knowledge)?
2. **Taxonomy fit** — Which of Anthropic's 9 categories does it fit? 0 = suspect, 1 = good, 2+ = too broad.
3. **Redundancy check** — Does another skill cover the same domain? Read both before recommending merge.
4. **Staleness check** — Does `stale_refs > 0` from the scan? If so, read the skill and identify what's stale.

### Step 3: Dependency safety check

Before any DELETE or MERGE recommendation, verify:

1. **CLAUDE.md triggers** — grep the global CLAUDE.md for references to the skill name
2. **Cross-skill references** — grep all SKILL.md files for the skill name
3. **Hook references** — check settings.json for the skill name
4. **Script consumers** — are other scripts calling this skill's scripts?

If dependencies exist, the recommendation becomes REFRAME (update references) rather than DELETE.

### Step 4: Context budget analysis

From the portfolio scan:
- `estimated_index_tokens` = skill_count × ~100 tokens
- Flag if total exceeds 2000 tokens (20+ skills)
- Identify skills with the longest descriptions (highest per-skill context cost)
- Flag skills that could be docs (zero context cost until triggered)

### Step 5: Produce recommendations

For each skill, assign one action:

| Action | Criteria | Output |
|--------|----------|--------|
| **KEEP** | Fits 1 category, no redundancy, no staleness | No action needed |
| **REFRAME** | Stale references, too broad, coupling issues | Specific changes to make |
| **MERGE** | Two skills overlap in domain and execution | Which skills, into what |
| **DELETE** | Wrong surface type, fully redundant, stale artifact | Where content goes (doc, CLAUDE.md, or nowhere) |

### Step 6: Output report

```
Skill Portfolio Review
──────────────────────
Skills: {count} | Index tokens: ~{estimate} | Last review: {date or "never"}

  Skill                  Category           Action    Reason
  ─────────────────────────────────────────────────────────────
  audit                  Code Quality       KEEP      Clean fit
  implementation         Code Scaffolding   REFRAME   2 stale refs to orchestrator
  context-budget         Infra Ops          KEEP      Clean fit
  ...

  Summary:
    KEEP: {n}  |  REFRAME: {n}  |  MERGE: {n}  |  DELETE: {n}

  Context savings if executed: ~{tokens} tokens ({percent}% reduction)

  Priority fixes:
  1. [DELETE] ... → convert to ...
  2. [MERGE] ... + ... → ...
  3. [REFRAME] ... — update stale references to ...
```

### Step 7: Offer to execute

After showing the report, offer to execute recommendations one at a time. For each:
- DELETE: verify dependencies clear, remove SKILL.md, convert content if needed
- MERGE: create combined skill, remove originals, update cross-references
- REFRAME: apply specific changes, re-run skill-quality-gate on the result

Follow the workflow doc creation process (`workflow summary workflow-doc-creation`) when converting skills to docs.

## When NOT to use this

- Auditing a single skill → `/skill-quality-gate`
- Checking project code quality → `/audit`
- Checking system setup health → `/harness-audit`

## References

| File | Load when |
|------|-----------|
| references/taxonomy.md | Classifying skills (Step 2) — 9 categories + decision tree |

## Scripts

| File | Purpose |
|------|---------|
| scripts/portfolio-scan.sh | Fleet-wide metrics collection (Step 1) |
