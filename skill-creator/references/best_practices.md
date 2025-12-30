# Skill Best Practices

## Critical: Description = Trigger

The `description` field determines when Claude triggers a skill. This is the most important field.

| Pattern | Example |
|---------|---------|
| Start with "Use when..." | `"Use when processing PDFs..."` |
| Include ALL trigger scenarios | `"...rotating, merging, splitting, or extracting..."` |
| Add context | `"Load for any PDF manipulation task."` |

**Good:**
```yaml
description: "Use when creating skills, updating existing skills, or learning skill best practices. Load for extending Claude's capabilities with specialized workflows."
```

**Bad:**
```yaml
description: "Skill creation toolkit"  # No trigger info!
```

## Frontmatter Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Kebab-case identifier |
| `description` | Yes | Trigger scenarios (start with "Use when...") |
| `keywords` | Recommended | Discovery tags |
| `license` | Optional | License reference |

## Writing Style

| Rule | Good | Bad |
|------|------|-----|
| Imperative form | "Run the script" | "You should run the script" |
| Objective tone | "Configure the setting" | "You need to configure" |
| Tables over prose | Use tables | Long paragraphs |

## Content Organization

| Location | What Goes Here | Token Cost |
|----------|----------------|------------|
| description | ALL trigger scenarios | ~100 (always loaded) |
| SKILL.md body | Instructions only | <5K (on trigger) |
| references/ | Detailed docs | On-demand |
| scripts/ | Executable code | **0** when run |
| assets/ | Templates, images | **0** (output) |

## Scripts = 0 Tokens

Scripts execute without loading into context.

```bash
# Good: 0 tokens
./scripts/validate.sh

# Bad: wastes tokens
cat scripts/validate.sh | # then process...
```

Use scripts for:
- Verification (deterministic results)
- Repeated operations
- Complex logic

## Avoid Duplication

| Principle | Action |
|-----------|--------|
| Single source of truth | Content in SKILL.md OR references/, not both |
| SKILL.md | Workflow + pointers to resources |
| references/ | Detailed schemas, APIs, examples |
| Large files (>10k) | Include grep patterns in SKILL.md |

## Checklist

**Frontmatter:**
- [ ] `name`: lowercase, hyphens
- [ ] `description`: starts with "Use when...", ALL triggers
- [ ] `keywords`: relevant discovery tags

**Body:**
- [ ] Under 5K words
- [ ] Tables for structured info
- [ ] References table at end
- [ ] Scripts documented with usage

**Resources:**
- [ ] scripts/ for executable code
- [ ] references/ for detailed docs
- [ ] assets/ for output templates
