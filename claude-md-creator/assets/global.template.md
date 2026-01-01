# Global Claude Code Guidelines

Sacrifice grammar for brevity.

## Core Principles

1. **Session Continuity**: Feature lists + progress tracking
2. **Token Efficiency**: On-demand loading (98% savings)
3. **Security Isolation**: Sandbox execution
4. **Progressive Disclosure**: 3-level loading
5. **Multi-Agent Coordination**: Orchestrate, don't implement
6. **Parallel > Sequential**: Independent tasks → parallel agents

## Token Scarcity

- Budget: 100K tokens
- Process large data in sandbox (99% savings)
- Use progressive disclosure (98.7% savings)
- Delegate to preserve context

## Execution Decision

| Scenario | Action |
|----------|--------|
| 1 task, <5 min | Do directly |
| 1 task, >5 min | Delegate |
| 2+ independent | Parallel agents |
| 2+ dependent | Sequential or single agent |
| Complex breakdown | Initializer agent |
| Code/data processing | `search_tools(query)` first |

## Core Rules

- Read → Process → Summarize (never raw)
- One feature at a time
- Production quality each session
- Semantic IDs (not UUIDs)
- Orchestrate > Implement

## Never

- Return raw data
- Repeat context
- Verbose explanations
- Sequential when parallel possible
- Implement when should delegate
