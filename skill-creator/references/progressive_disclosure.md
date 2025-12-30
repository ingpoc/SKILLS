# Progressive Disclosure in Skills

## Critical: Description = Trigger

Claude decides whether to trigger a skill based on the `description` field in frontmatter.

| Location | Visible To Claude | Timing |
|----------|-------------------|--------|
| `description` | Always | Before trigger decision |
| SKILL.md body | Only after triggered | Too late for trigger |
| references/ | Only when loaded | On-demand |

**Implication:** Put ALL "when to use" scenarios in description, not body.

## Three-Level Loading System

| Level | What | Tokens | When Loaded |
|-------|------|--------|-------------|
| 1. Metadata | name + description + keywords | ~100 | Always in context |
| 2. SKILL.md body | Instructions, tables | <5k | When skill triggers |
| 3. Resources | scripts, references, assets | Varies | As needed |

## Resource Token Costs

| Resource | Token Cost | Reason |
|----------|------------|--------|
| scripts/ (execute) | **0** | Runs without loading to context |
| scripts/ (read for patch) | ~500-2K | Only when modifying script |
| references/ | ~1-5K | Loaded on-demand |
| assets/ | **0** | Used in output, never loaded |

**Key insight:** Scripts execute WITHOUT loading into context.

```bash
# 0 tokens - just runs and returns result
./scripts/validate.sh

# Wastes tokens - loads script to context
cat scripts/validate.sh  # Don't do this!
```

## Context Efficiency Rules

| Rule | Token Impact |
|------|--------------|
| Description contains triggers | Skill triggers correctly |
| SKILL.md under 5k words | Fast loading |
| Tables over prose | 30-50% savings |
| Details in references/ | Load only when needed |
| Scripts for verification | 0 tokens (deterministic) |

## Example: Token-Efficient Skill

```
pdf-editor/
├── SKILL.md (600 words)           # Triggers + instructions only
├── scripts/
│   ├── rotate.py                  # 0 tokens when executed
│   └── merge.py                   # 0 tokens when executed
├── references/
│   └── advanced-api.md            # ~2K tokens if loaded
└── assets/
    └── template.pdf               # 0 tokens (output only)
```

**Trigger scenario:**

```yaml
---
name: pdf-editor
description: "Use when rotating, merging, splitting, or extracting from PDFs. Load for any PDF manipulation task requiring programmatic changes."
keywords: pdf, rotate, merge, split, extract
---
```

## Token Comparison

| Approach | On Trigger | During Use | Total |
|----------|------------|------------|-------|
| Monolithic (all in body) | 8K | 0 | 8K |
| Progressive (optimized) | 1.2K | +2K if refs loaded | 1.2-3.2K |
| With scripts | 1.2K | +0 (scripts execute) | 1.2K |
| **Savings** | - | - | **85-98%** |
