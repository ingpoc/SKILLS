---
name: initialization
description: "Use when starting a new session without feature-list.json, setting up project structure, or breaking down requirements into atomic features. Load in INIT state. Detects project type (Python/Node/Django/FastAPI), creates feature-list.json with priorities, initializes .claude/progress/ tracking."
keywords: init, setup, features, breakdown, project-detection, requirements
---

# Initialization

Project setup and feature breakdown for INIT state.

## Instructions

1. **Check MCP servers**: `check-dependencies.sh` runs mcp-setup verification first
2. Initialize project structure: `scripts/init-project.sh`
   - Creates `.claude/config/`, `.claude/progress/`
   - Creates `.claude/config/project.json` with detected project type
   - Creates `.claude/CLAUDE.md` with project quick reference
3. Detect project type: `scripts/detect-project.sh` (already run by init-project.sh)
4. Create init script: `scripts/create-init-script.sh`
5. Check dependencies: `scripts/check-dependencies.sh`
6. **Setup hooks**:
   - Check: `~/.claude/hooks/verify-state-transition.py` exists
   - If NO: Load `~/.claude/skills/global-hook-setup/SKILL.md` → Run `setup-global-hooks.sh`
   - Check: `.claude/hooks/verify-tests.py` exists
   - If NO: Load `.skills/project-hook-setup/SKILL.md` → Run `setup-project-hooks.sh`
   - Verify both complete before continuing
7. Analyze user requirements
8. Break down into atomic features (INVEST criteria)
9. Create feature-list.json: `scripts/create-feature-list.sh`
10. Initialize progress tracking: `scripts/init-progress.sh`

## Exit Criteria (Code Verified)

```bash
# Project structure initialized
[ -f ".claude/CLAUDE.md" ]              # Quick reference created
[ -f ".claude/config/project.json" ]    # Project config
[ -d ".claude/progress/" ]               # Tracking directory

# Feature list created
[ -f ".claude/progress/feature-list.json" ]
jq '.features | length > 0' .claude/progress/feature-list.json
jq '.features[0] | has("id", "description", "priority", "status")' .claude/progress/feature-list.json

# Dependencies verified
scripts/check-dependencies.sh --quiet

# Hooks installed
[ -x "~/.claude/hooks/verify-state-transition.py" ]  # Global hooks
[ -x ".claude/hooks/verify-tests.py" ]                 # Project hooks
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init-project.sh` | Initialize .claude/ structure, create CLAUDE.md |
| `scripts/detect-project.sh` | Detect Python/Node/Django/etc |
| `scripts/create-init-script.sh` | Generate init.sh for dev server |
| `scripts/check-dependencies.sh` | Verify env vars, services, ports |
| `scripts/create-feature-list.sh` | Generate feature-list.json |
| `scripts/init-progress.sh` | Initialize .claude/progress/ |

## References

| File | Load When |
|------|-----------|
| references/feature-breakdown.md | Breaking down requirements |
| references/project-detection.md | Detecting project type |
| references/mvp-feature-breakdown.md | MVP-first tiered feature generation (10/30/200) |

## Assets

| File | Purpose |
|------|---------|
| assets/feature-list.template.json | Template for new feature lists |
