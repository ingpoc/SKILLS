# TEMPLATE- Scripts Customization Guide

## Why TEMPLATE- Prefix?

Scripts are copied during initialization with `TEMPLATE-` prefix to signal they need customization before use.

| State | Meaning |
|-------|---------|
| `TEMPLATE-health-check.sh` | Not customized - DO NOT USE |
| `health-check.sh` | Customized - safe to use |

## Customization Workflow

```bash
# 1. List uncustomized scripts
ls .claude/scripts/TEMPLATE-*.sh

# 2. Read README for purposes
cat .claude/scripts/README.md

# 3. For each TEMPLATE- script:
#    a. Review contents
cat .claude/scripts/TEMPLATE-health-check.sh

#    b. Edit for your project
#       - Update ports, paths, commands
#       - Match your project architecture

#    c. Rename to activate
mv .claude/scripts/TEMPLATE-health-check.sh .claude/scripts/health-check.sh

#    d. Test it works
.claude/scripts/health-check.sh

# 4. Commit all customized scripts
git add .claude/scripts/
git commit -m "customize: project scripts for [project-name]"
```

## Scripts Quick Reference

| Template | Customized | What to Change |
|----------|------------|----------------|
| `TEMPLATE-health-check.sh` | `health-check.sh` | Ports, services, health endpoints |
| `TEMPLATE-run-tests.sh` | `run-tests.sh` | Test framework, commands |
| `TEMPLATE-restart-servers.sh` | `restart-servers.sh` | Build commands, services |
| `TEMPLATE-get-current-feature.sh` | `get-current-feature.sh` | Usually works as-is |
| `TEMPLATE-mark-feature-complete.sh` | `mark-feature-complete.sh` | Usually works as-is |
| `TEMPLATE-feature-commit.sh` | `feature-commit.sh` | Commit message format |
| `TEMPLATE-check-state.sh` | `check-state.sh` | Usually works as-is |
| `TEMPLATE-validate-transition.sh` | `validate-transition.sh` | Custom state machine |
| `TEMPLATE-transition-state.sh` | `transition-state.sh` | Usually works as-is |
| `TEMPLATE-check-context.sh` | `check-context.sh` | Compression thresholds |

## Customization Priority

Customize in this order (most critical first):

1. **health-check.sh** - Runs every session
2. **run-tests.sh** - Needed for verification
3. **restart-servers.sh** - Needed for development
4. **Others** - Usually work as-is

## Common Customizations by Project Type

### TypeScript Monorepo

```bash
# health-check.sh
pnpm typecheck
pnpm build

# run-tests.sh
pnpm test -- --run

# restart-servers.sh
pnpm build && pnpm typecheck
```

### Python FastAPI

```bash
# health-check.sh
curl -s localhost:8000/api/health

# run-tests.sh
pytest -v

# restart-servers.sh
uvicorn app.main:app --reload
```

### Next.js + Express

```bash
# health-check.sh
curl -s localhost:3000 && curl -s localhost:8000/api/health

# run-tests.sh
npm test

# restart-servers.sh
# Kill ports, start frontend/backend
```

## Verification

After customization, verify no TEMPLATE- files remain:

```bash
# Should return nothing
ls .claude/scripts/TEMPLATE-*.sh 2>/dev/null

# If files listed, continue customizing
```

## Troubleshooting

**Script not found when running?**

```bash
# Check if still has TEMPLATE- prefix
ls .claude/scripts/TEMPLATE-*.sh
# Rename if found
```

**Script not executable?**

```bash
chmod +x .claude/scripts/*.sh
```

**Script fails after rename?**

- Check paths match your project structure
- Check ports match your services
- Check commands match your tooling
