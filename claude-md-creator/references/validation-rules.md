# Validation Rules Reference

## Rule Categories

### Frontmatter Rules

| Rule | Level | Why |
|------|-------|-----|
| Has YAML fence | error | Required for metadata parsing |
| Has name field | warning | Identifies file type |
| Has description field | warning | Explains purpose |
| No angle brackets | warning | Security risk (HTML injection) |

### Structure Rules

| Rule | Level | Why |
|------|-------|-----|
| Has section headings (##) | warning | Organizes content |
| Required sections present | warning | Type-specific essentials |
| No empty sections | warning | Removes clutter |

### Best Practices Rules

| Rule | Level | Why |
|------|-------|-----|
| Line count within target | warning | Keeps files focused |
| Tables for lists | info | 30-50% token savings |
| Commands use code blocks | info | Clear copy-paste |

### Content Rules

| Rule | Level | Why |
|------|-------|-----|
| Referenced paths exist | info | Avoids broken references |
| Commands exist in project | info | Accuracy of docs |

## Type-Specific Requirements

### Global CLAUDE.md
- **Required sections**: None
- **Line target**: 50-150
- **Focus**: Personal preferences

### Project CLAUDE.md
- **Required sections**: None (recommended: Common Commands)
- **Line target**: 100-300
- **Focus**: Team instructions

### Local CLAUDE.md
- **Required sections**: None
- **Line target**: <50
- **Focus**: Personal overrides

### Rules
- **Required sections**: Purpose
- **Line target**: 20-100
- **Focus**: Single topic

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Valid (no errors) |
| 1 | Warnings only |
| 2 | Errors found |

## Adding Custom Rules

To add custom validation rules:

1. Define function in `validate-claude-md.py`:
```python
def validate_custom_rule(content, issues):
    # Your validation logic
    if problem_detected:
        issues.append(ValidationIssue(
            "custom", "warning",
            "Description of issue",
            "location"
        ))
```

2. Call in main validation flow:
```python
validate_custom_rule(content, issues)
```

3. Document rule in this file
