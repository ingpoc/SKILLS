# Quick Reference

Full orchestrator instructions are in `~/.claude/prompts/orchestrator.md`

## Common Commands

```bash
# Check current state
~/.claude/skills/orchestrator/scripts/check-state.sh

# Run tests (reads test_command from .claude/config/project.json)
~/.claude/skills/testing/scripts/run-unit-tests.sh

# Health check (reads health_check from config)
~/.claude/skills/implementation/scripts/health-check.sh

# Browser smoke test (reads dev_server_port from config)
~/.claude/skills/browser-testing/scripts/smoke-test.sh
```

## Session Entry

Run: `~/.claude/skills/orchestrator/scripts/session-entry.sh`

## State → Skill Mapping

| State | Skill |
|-------|-------|
| INIT | initialization/ |
| IMPLEMENT | implementation/ |
| TEST | testing/ |
| COMPLETE | context-graph/ |

## Config Files

- `.claude/config/project.json` - Project settings
- `.claude/progress/state.json` - Current state
- `.claude/progress/feature-list.json` - Features
