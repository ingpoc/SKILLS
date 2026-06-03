#!/bin/bash
# One-time setup for global Claude Code configuration
# Run: bash global-init.sh

set -e

GLOBAL_DIR="$HOME/.claude"
GLOBAL_CLAUDE="$GLOBAL_DIR/CLAUDE.md"

echo "=== Global Claude Code Configuration ==="
echo ""

# Create directory if not exists
mkdir -p "$GLOBAL_DIR"

# Check if already exists
if [ -f "$GLOBAL_CLAUDE" ]; then
    echo "⚠️  Global CLAUDE.md already exists at: $GLOBAL_CLAUDE"
    echo ""
    read -p "Backup and overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping. Existing file preserved."
        exit 0
    fi
    cp "$GLOBAL_CLAUDE" "$GLOBAL_CLAUDE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backed up existing file"
fi

# Create global CLAUDE.md with truly any time skills enforcement
cat > "$GLOBAL_CLAUDE" << 'GLOBAL_EOF'
---
name: global
description: Global preferences across all projects - token efficiency, skill enforcement, deterministic verification
keywords: global, token-efficiency, skills, enforcement, mcp
---

## Global Claude Code Guidelines

Sacrifice grammar for brevity.

## Core Principles

1. **Session Continuity**: Feature lists + progress tracking
2. **Token Efficiency**: On-demand loading (98%+ savings)
3. **Security Isolation**: Sandbox execution
4. **Progressive Disclosure**: 3-level loading
5. **Determinism**: Code verification > LLM judgment

---

## Token Scarcity

| Budget | 100K tokens |
|--------|-------------|
| Large data | Sandbox (99% savings) |
| Loading | Progressive disclosure (98% savings) |

---

## Truly Any Time Skills (Enforcement)

| Skill | Trigger | Must Execute Before |
|-------|---------|---------------------|
| **skill-creator** | Creating/updating any skill | ANY skill creation/update |
| **claude-md-creator** | Creating/updating CLAUDE.md | ANY CLAUDE.md edit |
| **token-efficient** | Data >50 items, CSV/logs, code exec | Loading raw data to context |
| **determinism** | Verification needed | LLM judgment ("I think tests passed") |
| **mcp-builder** | Building MCP servers | Starting MCP development |

---

## Token-Efficient MCP Tools

**Use these tools; NEVER load raw data into context:**

| Tool | Use For | Savings |
|------|---------|---------|
| `execute_code` | Python/Bash/Node in sandbox | 98%+ |
| `process_csv` | CSV with filters (price > 100) | 99% |
| `process_logs` | Log pattern matching (ERROR\|WARN) | 95% |
| `search_tools` | Find tools by keyword | 95% |
| `batch_process_csv` | Multiple CSVs | Batch |

**Usage:**
- CSV: `mcp__token-efficient__process_csv(file_path, filter_expr, limit)`
- Logs: `mcp__token-efficient__process_logs(file_path, pattern, limit)`
- Code: `mcp__token-efficient__execute_code(code, language)` (supports heredocs `<<EOF`)

---

## Determinism (Code > Judgment)

| Task | LLM (Bad) | Code (Good) |
|------|-----------|-------------|
| Tests passed? | "Tests appear to pass" | `pytest; echo $?` |
| Valid JSON? | "Looks like valid JSON" | `python -c "json.load(f)"` |
| Server running? | "Server should be up" | `curl -s localhost/health` |

**Rules:**
- Use exit codes (0/1), not text descriptions
- Version prompts with semantic versioning
- Hash-validate critical prompts

---

## CLAUDE.md Updates

**CRITICAL**: Execute `claude-md-creator` skill BEFORE any CLAUDE.md edits

| CLAUDE.md Type | Path | Size Target |
|---------------|------|-------------|
| Global | `~/.claude/CLAUDE.md` | 50-150 lines |
| Project | `CLAUDE.md` | 100-300 lines |
| Local | `.claude/CLAUDE.md` | Quick reference only |
| Rules | `.claude/rules/*.md` | 20-100 each |

**Format: Tables/bullets only, no examples/explanations**

---

## Context Graph (MCP Tools)

**Before decisions:** Query precedents
**After feedback:** Store outcomes

| Tool | Purpose |
|------|---------|
| `context_store_trace` | Store decision with category + outcome |
| `context_query_traces` | Semantic search for similar decisions |
| `context_update_outcome` | Mark success/failure |
| `context_list_categories` | Browse all categories |
| `context_list_traces` | List with pagination |

**Categories**: framework, architecture, api, error, testing, deployment

**Token efficiency**: Use `limit` parameter, `max_chars` for memory reads

---

## Execution Decision

| Scenario | Action |
|----------|--------|
| 1 task, <5 min | Do directly |
| 1 task, >5 min | Delegate |
| 2+ independent | Parallel agents |
| 2+ dependent | Sequential |
| Data >50 items | Use token-efficient MCP |
| Verification needed | Use determinism (code, not judgment) |

---

## Core Rules

- Read → Process → Summarize (never raw)
- One feature at a time
- Production quality each session
- Semantic IDs (not UUIDs)
- Heredocs supported in `execute_code`: `<<EOF`, `<<'EOF'`
- Localhost works: `execute_code` with curl for local APIs
- Agent outputs: `/tmp/summary/` (keeps project clean)
- **Skill creation**: Execute `skill-creator` first
- **CLAUDE.md updates**: Execute `claude-md-creator` first
- **Code verification**: Use scripts, not LLM judgment

---

## Never

- Return raw data
- Repeat context
- Verbose explanations
- Sequential when parallel possible
- Implement when should delegate
- Load >50 items to context (use token-efficient MCP)
- Use LLM judgment for verification (use determinism)
GLOBAL_EOF

echo "✅ Created: ~/.claude/CLAUDE.md"
echo ""
echo "=== Global Configuration Complete ==="
echo ""
echo "Your global preferences are now configured."
echo "Project-specific settings will be in each project's CLAUDE.md"
echo ""
