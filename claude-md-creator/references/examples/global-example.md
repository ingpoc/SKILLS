# Global Claude Code Guidelines

Sacrifice grammar for brevity.

## Core Principles

1. **Session Continuity**: Feature lists + progress tracking
2. **Token Efficiency**: On-demand loading (98.7% savings)
3. **Security Isolation**: Sandbox execution
4. **Progressive Disclosure**: 3-level loading
5. **Multi-Agent Coordination**: Orchestrate, don't implement
6. **Parallel > Sequential**: Independent tasks → parallel agents

## Token Scarcity

- Budget: 100K tokens
- Process large data in sandbox (99% savings)
- Use progressive disclosure (98.7% savings)
- Delegate to preserve context

**Use token-efficient MCP when**: processing >50 items, CSV/logs analysis, or code execution

**Progressive Disclosure:**
- `search_tools(query)` first (95% savings)
- `list_token_efficient_tools(level="names_only")` (99% savings)

## Before Acting

1. Check if done
2. Independent tasks? → Parallel agents
3. Will load >10K to context? → Delegate
4. Atomic changes only
5. Update progress immediately

## Execution Decision

| Scenario | Action |
|----------|--------|
| 1 task, <5 min | Do directly |
| 1 task, >5 min | Delegate |
| 2+ independent | Parallel agents |
| 2+ dependent | Sequential or single agent |
| Complex breakdown | Initializer agent |
| Browser UI testing | `dev-browser` skill (needs network) |
| Code/data processing | `search_tools(query)` first (saves tokens) |

## Data Processing

| Size | Action |
|------|--------|
| <50 items | In-context |
| 50-10K | `search_tools("csv")` → find tool |
| >10K | Use pagination (offset/limit) |

## Tool Selection

| Purpose | Tool | Notes |
|---------|------|-------|
| Code/data processing | `search_tools(query)` | Use first (95% savings) |

## Core Rules

- Read → Process → Summarize (never raw)
- One feature at a time
- Production quality each session
- Semantic IDs (not UUIDs)
- Orchestrate > Implement
- **Heredocs supported** - Use `<<EOF` syntax in `execute_code` for multi-line bash scripts
- **Localhost works** - `execute_code` with curl can test local APIs
- **Agent outputs** - All summaries/reports go to `/tmp/summary/` (keeps project clean)
- **Skill updates**: Execute `skill-creator` skill before creating/updating any skill

## Never

- Return raw data
- Repeat context
- Verbose explanations
- Sequential when parallel possible
- Implement when should delegate

## Context Graph Workflow

  Before making decisions about code patterns, naming, or architecture:

  1. **Query precedents**:
     - `list_memories()` → see available categories
     - `read_memory("category_name", max_chars=500)` → get relevant precedents

  2. **Search codebase**:
     - `search_for_pattern("pattern", relative_path="target_dir")` → find similar code
     - `find_symbol("ClassName", depth=1)` → get structure (not full body)

  3. **Apply learned patterns** from context graph + codebase

  After user feedback:

  4. **Store trace**:
     - Accepted: `write_memory("success_XXX", "...")` → confirms pattern
     - Corrected: `write_memory("correction_XXX", "{what, correct, why}")` → teaches agent

  5. **Link traces**: `edit_memory("category", add_relation="new_trace")`

  **Token efficiency**: Always use `max_chars` parameter, load only top-3 relevant memories

  **Memory categories**: naming, architecture, error_handling, api_design, testing

**Token limit**: Load top-3 memories only, use `max_chars` parameter

---

**Updating CLAUDE.md**: Tables/bullets only, no examples/explanations, max token efficiency
