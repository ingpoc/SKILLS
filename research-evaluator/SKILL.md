---
name: research-evaluator
description: "Use when user shares a research paper, article, blog post, or URL for evaluation. Load for phrases like 'what do you think of this', 'should we integrate this', 'process this article', 'distill this research', 'add to docs', 'is this worth using', or any time a URL or document is shared for expert judgment on integration into our workflow. Replaces agent-context-repo. Produces a scored verdict with explicit evidence, mechanism, constraint match, and adversarial judgment."
keywords: [research, evaluation, integration, verdict, article, paper, workflow, agent-context-repo]
---

# Research Evaluator

Judgment first. Filing only when it is actually useful.

---

## Decision Framework

| Total Score | Verdict | Default Action |
|-------------|---------|----------------|
| ≥ 8 | Adopt / Adapt | Return a direct verdict. File only if the user asked for docs or durable capture is clearly useful. |
| 4–7 | Ambiguous | Return a direct verdict with uncertainty. Use a deeper adversarial pass only if ambiguity materially remains. |
| ≤ 3 | Skip | Return a skip verdict. File only if the user asked to preserve the evaluation. |

### Scoring Rubric (0–3 each, max 12)

| Dimension | 0 | 1 | 2 | 3 |
|-----------|---|---|---|---|
| **Novelty** | We already do this | Minor variant of existing | Meaningfully new approach | Completely new capability |
| **Relevance** | We don't have this problem | Tangential to our work | Related to active problems | Directly solves a current pain |
| **Claim validity** | Benchmarks inapplicable at our scale | Weak/anecdotal evidence | Reasonable evidence | Strong evidence at our scale |
| **Implementation cost** | Months / replaces core / risky | Weeks / extends existing | Days / additive | Hours / drop-in |

---

## Phase 1: Intake

Fetch the article. Try WebFetch first. If it fails (403/empty/truncated), use fallback in this order: (1) Exa MCP if available (`mcp__exa__web_search_exa`, `livecrawl: "preferred"`), (2) WebSearch + WebFetch on returned sources. Never proceed with missing content. Extract:

- Core claims (3–7 max)
- Proposed patterns / anti-patterns
- Metrics and benchmarks cited
- What problem it claims to solve

Then form **initial views before researching** — do I believe each claim? Why / why not?

---

## Phase 2: Research & Validate

Do enough validation to materially test the important claims. Do not optimize for query count.

For each key claim, choose the most relevant tools:

| Tool | When |
|------|------|
| `WebSearch` | General claims, benchmarks, industry trends |
| `WebFetch` | Source article, linked papers |
| `deepwiki` | Claim references a repo's architecture |
| `context7` | Claim involves a library/framework |
| Context graph (`context_query_traces`) | Has this come up before? Past outcome? |

For each important claim: look for supporting evidence and counter-evidence where possible. Note caveats.

Guidance:
- for straightforward primary-source interpretation, the source plus one meaningful validating check may be enough
- for broad performance claims, benchmark claims, or workflow adoption claims, use multiple meaningful checks
- do not add queries that do not change the judgment

Before you score or recommend anything, explicitly separate:
- **Sourced facts** — statements directly grounded in the source or validating references
- **Inferences** — your interpretation, extrapolation, or repo-specific application of those facts

Do not blur these together. The user should be able to tell which parts are reported evidence and which parts are your judgment.

---

## Phase 3: Score

Apply the rubric. Be honest — a paper that solves a problem we don't have scores 0 on Relevance regardless of quality.

Check against our setup specifically:

- Does our codebase already do this? → scan `docs/`, recent git log
- Are their benchmarks at our scale? (Token counts, team size, infra)
- Does it conflict with existing rules in `.claude/rules/`, `CLAUDE.md`?
- What operating constraints made this work for the author, and which of those do or do not match our repository?

Make this comparison explicit. Do not just imply applicability. State the source constraints and our local constraints clearly enough that a reader can see why the verdict follows.

Also force an adversarial pass before finalizing:
- state the **strongest counterargument** to adopting the idea
- name what we **already have** that makes the source partially redundant, if anything
- state a concrete **revisit trigger** for what new evidence or changed condition would justify revisiting the verdict

Output the score table:

```text
| Dimension           | Score | Notes                        |
|---------------------|-------|------------------------------|
| Novelty             |  /3   |                              |
| Relevance           |  /3   |                              |
| Claim validity      |  /3   |                              |
| Implementation cost |  /3   |                              |
| Total               |  /12  |                              |
```

---

## Phase 4a: Clear Verdict (score ≤ 3 or ≥ 8)

Output structured verdict and proceed directly to Phase 5.

```text
Verdict: [Adopt / Adapt / Skip]
Rationale: [1–2 sentences grounded in score]
Adopt/Adapt: [what exactly to take, what to modify]
Skip: [what would need to change for this to be worth revisiting]
```

---

## Phase 4b: Ambiguous Verdict (score 4–7)

Do not default to extra process just because the score is mid-range.

First, return the best direct judgment you can with:
- explicit uncertainty
- strongest counterargument
- redundancy check
- revisit trigger

Only run a deeper adversarial pass if:
- the source is high-stakes
- the ambiguity materially affects a decision
- or the user explicitly wants a deeper challenge process

If you do a deeper adversarial pass, keep it lightweight and focused on the unresolved question. Do not turn ambiguity into ceremony.

---

## Phase 5: Integrate or Skip

### If Skip

Document reasoning — prevents re-evaluating the same paper:

```markdown
# [Title] — Skipped

**Source**: [URL]
**Date**: YYYY-MM-DD
**Score**: X/12
**Why skipped**: [1–2 sentences]
**Revisit if**: [what would change the verdict]
```

Do not file by default. Only create a skipped note if the user asked to preserve the result or the evaluation is likely to matter again.

### If Adopt / Adapt

Check overlap first:

| Location | Check for |
|----------|-----------|
| `docs/workflow/` | Already distilled? |
| `docs/principles/` | Conflicts with core principles? |
| `.claude/rules/` | Contradicts existing rules? |
| `CLAUDE.md` / `AGENTS.md` | Already captured? |

Do not file by default. File only when:
- the user explicitly asked to add docs
- the result is durable enough to benefit future work
- and the write is worth the maintenance burden

If you file:
- use the output template
- keep it scoped
- never update `CLAUDE.md` from this skill

### Output Template

```markdown
# [Title] (Distilled)

**Source**: [URL]
**Date**: YYYY-MM-DD
**Score**: X/12 — [Adopt / Adapt]

## Verdict

**Rationale**: [2–3 sentences with evidence]

## Sourced Facts

- [Fact directly supported by the source or validation query]

## Inferences

- [Interpretation, extrapolation, or repo-specific judgment derived from the facts]

## Mechanism

- [How the workflow/system actually works, not just what it claims]

## Constraint Match

- **Source constraints:** [What assumptions, infrastructure, team shape, or task conditions made the source approach work]
- **Our constraints:** [What is true in this repository or workflow]
- **Match assessment:** [Where the fit is strong, weak, or partial]

## Strongest Counterargument

- [The strongest serious objection to adoption, not a generic caveat]

## Redundancy Check

- [What we already have that overlaps with or reduces the value of this source]

## Revisit If

- [What new evidence, changed condition, or missing implementation detail would justify revisiting the verdict]

| Dimension           | Score | Notes |
|---------------------|-------|-------|
| Novelty             |  /3   |       |
| Relevance           |  /3   |       |
| Claim validity      |  /3   |       |
| Implementation cost |  /3   |       |

## Claims Analysis

| Claim | Agree? | Evidence | Notes |
|-------|--------|----------|-------|
| ...   | Yes/No/Partial | [source] | |

## What to Take

[Specific patterns, principles, or techniques — not a summary, actual actionable items]

## What to Modify / Watch Out For

[Caveats, where their approach doesn't fit us, what we'd adapt]

## Integration Notes

**Tier**: 1 (Reference)
**Sessions Used**: 0
**Promotion Status**: Pending validation
**Debate**: [Yes/No — if Yes, summarize Advocate/Skeptic outcome]
```

---

## Quick Reference

| Trigger | Action |
|---------|--------|
| URL or paper shared | Full workflow focused on judgment first |
| "What do you think of this?" | Phases 1–4 only, no filing |
| "Should we use this?" | Full workflow with explicit verdict |
| "Add this to docs" | Score first, then file only if the result is durable enough to keep |

| Score | Next step |
|-------|-----------|
| ≥ 8 | Return direct adopt/adapt verdict; file only if useful |
| 4–7 | Return direct verdict with uncertainty; deepen only if needed |
| ≤ 3 | Return skip verdict; file only if preservation is useful |
