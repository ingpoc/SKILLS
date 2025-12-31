---
name: initialization
description: "Use when starting a new session without feature-list.json, setting up project structure, or breaking down requirements into atomic features. Load in INIT state. Detects project type (Python/Node/Django/FastAPI), creates feature-list.json with priorities, initializes .claude/progress/ tracking."
keywords: init, setup, features, breakdown, project-detection, requirements
---

# Initialization

Project setup and feature breakdown for INIT state.

## Instructions

1. Initialize project structure: `scripts/init-project.sh`
   - Creates `.claude/config/`, `.claude/progress/`
   - Creates `.claude/config/project.json` with detected project type
   - Creates `.claude/CLAUDE.md` with project quick reference

2. Detect project type: `scripts/detect-project.sh` (already run by init-project.sh)

3. Check dependencies: `scripts/check-dependencies.sh`
   - Checks MCP servers (calls verify-setup.sh)
   - Checks environment variables, init script, ports, database, external services
   - **If MCP verification fails**: Load `~/.claude/skills/mcp-setup/SKILL.md` → Run `scripts/setup-all.sh`
   - Re-run check-dependencies.sh after fixing

4. Create init script: `scripts/create-init-script.sh`

5. **Setup hooks**:
   - Check: `~/.claude/hooks/verify-state-transition.py` exists
   - If NO: Load `~/.claude/skills/global-hook-setup/SKILL.md` → Run `setup-global-hooks.sh`
   - Check: `.claude/hooks/verify-tests.py` exists
   - If NO: Load `.skills/project-hook-setup/SKILL.md` → Run `setup-project-hooks.sh`
   - Verify both complete before continuing

6. Analyze user requirements

7. Break down into atomic features (INVEST criteria)

8. Create feature-list.json: `scripts/create-feature-list.sh`

9. Initialize progress tracking: `scripts/init-progress.sh`

10. **Verify INIT complete**: `scripts/verify-init.sh`
    - Must pass all 14 checks before transitioning to IMPLEMENT

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
| `scripts/init-project.sh` | Initialize .claude/ structure, copy CLAUDE.md from template |
| `scripts/detect-project.sh` | Detect Python/Node/Django/etc |
| `scripts/check-dependencies.sh` | Verify MCP, env vars, services, ports (runs verify-setup.sh for MCP) |
| `scripts/create-init-script.sh` | Generate init.sh for dev server |
| `scripts/create-feature-list.sh` | Generate feature-list.json |
| `scripts/init-progress.sh` | Initialize .claude/progress/ |
| `scripts/verify-init.sh` | Verify all INIT criteria met (14 checks) |

## References

| File | Load When |
|------|-----------|
| references/feature-breakdown.md | Breaking down requirements |
| references/project-detection.md | Detecting project type |
| references/mvp-feature-breakdown.md | MVP-first tiered feature generation (10/30/200) |

## Assets

| File | Purpose |
|------|---------|
| assets/CLAUDE.template.md | Template for .claude/CLAUDE.md (includes MCP section) |
| assets/feature-list.template.json | Template for new feature lists |
