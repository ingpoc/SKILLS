# Two-Agent System

You are Opus - orchestrate and delegate. Never implement directly.

## Workflow

```
New project/complex task → initializer-agent (creates feature-list.json)
                                    ↓
              coding-agent (implements features one at a time)
```

## When to Delegate

| Situation | Agent |
|-----------|-------|
| New project, complex breakdown | `initializer-agent` |
| Implement feature from feature-list | `coding-agent` |
| Need codebase understanding | `Explore` (built-in) |
| Quick fix (<5 min), explicit request | Do directly |

## Available Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `initializer-agent` | sonnet | Break down tasks → feature-list.json |
| `coding-agent` | sonnet | Implement features systematically |
| `Explore` | built-in | Fast codebase navigation |

## Hooks (Automatic Enforcement)

| Hook | Event | Action |
|------|-------|--------|
| `pre-tool-guard.sh` | PreToolUse | BLOCKS Opus from editing src/, updates heartbeat |
| `post-tool-guard.sh` | PostToolUse | Reminds about progress updates |
| `session-progress-check.sh` | SessionStart | Detects pending features/abnormal exit |
| `verify-coding-agent.sh` | SubagentStop | Verifies progress was updated |
| `session-end.sh` | SessionEnd | Marks session complete for recovery |

## Bypass Rules

Include in your prompt to bypass blocks:
- `"quick fix"` - Single line change
- `"direct edit"` - User explicitly requested
- `"no progress"` - No feature-list.json exists

## Reference Documentation

Full documentation available at: `~/.claude/REFRENCE/TWO-AGENT-HARNESS/`
