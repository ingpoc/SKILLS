# CLAUDE.md Best Practices

## Line Count Targets

| Type | Min | Max | When to Split |
|------|-----|-----|--------------|
| Global | 50 | 150 | Use global only for cross-project preferences |
| Project | 100 | 300 | Split into .claude/rules/ if exceeded |
| Local | 0 | 50 | Keep minimal - personal overrides only |
| Rules | 20 | 100 | One topic per file |

## When to Use Each Type

### Global CLAUDE.md (~/.claude/CLAUDE.md)
**Use for**: Personal coding preferences that apply to ALL projects

**Content**:
- Token efficiency habits
- Core work principles
- Tool preferences
- Personal productivity patterns

**Avoid**:
- Project-specific commands
- Framework-specific patterns
- Team conventions

### Project CLAUDE.md (.claude/CLAUDE.md)
**Use for**: Team-shared project instructions

**Content**:
- Common commands (test, build, dev)
- Project structure
- Architecture overview
- Technology stack

**Include**:
- Commands extracted from package.json/Makefile
- Actual file paths that exist
- Config file locations

### Local CLAUDE.md (CLAUDE.local.md)
**Use for**: Your personal overrides for THIS project only

**Content**:
- Local port preferences
- Personal test data
- Local environment overrides
- Workflow shortcuts

**Note**: Auto-gitignored, never shared with team

### Rules (.claude/rules/*.md)
**Use for**: Modular, topic-specific instructions

**When to create**:
- Project CLAUDE.md exceeds 300 lines
- Distinct topics (testing, API, deployment)
- Team wants modular docs

**Naming**: `{topic}.md` (e.g., `testing.md`, `api-guidelines.md`)

## Table Format Guidelines

Use tables for:

| Content Type | Example |
|--------------|---------|
| Commands | `| Purpose | Command |` |
| Configs | `| File | Purpose |` |
| Mappings | `| State | Skill |` |
| Options | `| Choice | Description |` |

Convert lists to tables when:
- List has 3+ items with consistent structure
- Items have multiple attributes
- Quick reference is needed

## Command Extraction

**Always** extract real commands from:
- `package.json` → `scripts` section
- `Makefile` → `targets`
- `pyproject.toml` → `[tool.pytest]`
- `.github/workflows` → `jobs`

**Format**:
```bash
# Purpose
actual_command_here
```

## Path References

When referencing paths:
- Use relative paths from project root
- Verify path exists before documenting
- Use `.claude/` prefix for project config

**Good**: `.claude/config/project.json`
**Bad**: `~/project/config.json`

## Section Organization

Standard project CLAUDE.md structure:
1. Purpose (1-2 sentences)
2. Common Commands (most-used)
3. Project Structure (tree or table)
4. Config Files (list with descriptions)
5. Development Notes (framework, language)

## Progressive Disclosure

Keep SKILL.md concise (<5k words):
- Metadata → always visible
- SKILL.md body → on trigger
- references/ → on-demand
- assets/ → never loaded (output only)

**Result**: 98% token savings vs monolithic docs
