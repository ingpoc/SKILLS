# Context Graph Research Sources

Academic and industry sources backing context graph patterns.

## Foundation Sources

| Article | Key Insight |
|---------|-------------|
| [Context Graphs](https://foundationcapital.com/context-graphs-ais-trillion-dollar-opportunity/) | Decision traces = trillion-dollar layer |
| Foundation Capital Report | Living record of decision traces makes precedent searchable |

### Core Concepts

- **Rules vs Traces**: Rules = general behavior; Traces = specific instances with approvals, exceptions, reasoning
- **Decision event emission**: Capture inputs, policies evaluated, exceptions, approvals, state changes
- **Entity-time linkage**: Connect business entities with temporal sequences for searchable lineage
- **Cross-system synthesis**: Orchestration layer sees full context before decisions

### Implementation Approaches

1. Replace at scale - Rebuild systems as agentic-native with event-sourced state
2. Module replacement - Target exception-heavy subworkflows
3. New system of record - Start as orchestration, persist decision lineage until graph becomes authoritative

---

## Anthropic Engineering Articles

### Context Engineering

Source: [Anthropic - Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**Definition**: The art and science of curating what goes into the limited context window from constantly evolving possible information.

> "Context, therefore, must be treated as a finite resource with diminishing marginal returns."

**Key Concepts**:

| Concept | Description |
|----------|-------------|
| Attention Budget | n² pairwise relationships for n tokens creates "context rot" |
| Context Engineering vs Prompt Engineering | Managing all context (tools, history, data) vs just system prompt |
| Just-in-Time Retrieval | Lightweight identifiers (file paths, links) → load at runtime |
| Progressive Disclosure | Agents incrementally discover relevant context through exploration |

**Long-Horizon Task Strategies**:

| Strategy | Use Case | Token Target |
|----------|----------|--------------|
| **Compaction** | Extensive back-and-forth | Summarize + recent 5 files |
| **Structured Note-Taking** | Iterative development | External memory (NOTES.md, to-do lists) |
| **Sub-Agent Architectures** | Complex research/analysis | 1K-2K token returns |

**Sub-Agent Distillation Pattern**:

> "Specialized sub-agents can handle focused tasks with clean context windows. Each subagent might explore extensively, using tens of thousands of tokens, but returns only a condensed, distilled summary (often 1,000-2,000 tokens)."

**Preserve vs Discard** (Compaction):

| Preserve | Discard |
|----------|---------|
| Architectural decisions | Redundant tool outputs |
| Unresolved bugs | Raw results (once used) |
| Implementation details | Verbose logs |
| Recent 5 files | Historical context |

### Agent Skills

Source: [Anthropic - Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

| Pattern | Description |
|---------|-------------|
| Progressive Disclosure | 3-tier: metadata (always) → SKILL.md (when relevant) → references (on demand) |
| Code Execution | Skills can include scripts for deterministic operations |
| Metadata-Driven Triggering | Name + description determines when skill activates |
| Unbounded Context | Skills can reference unlimited files, loaded only as needed |

### Code Execution with MCP

Source: [Anthropic - Code Execution](https://www.anthropic.com/engineering/code-execution-with-mcp)

| Pattern | Token Savings |
|---------|---------------|
| On-demand tool loading | 98.7% (150K → 2K tokens) |
| Data filtering in sandbox | Process 10K rows, return 5 |
| search_tools with detail levels | name_only → with_description → full_schema |

**Token Impact**: 150,000 → 2,000 tokens = **98.7% savings**

### Long-Running Harness

Source: [Anthropic - Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

| Pattern | Purpose |
|---------|---------|
| Two-agent architecture | Initializer (once) + Coding (repeated) |
| Feature list as contract | JSON with passes:false, prevents premature completion |
| Progress files | claude-progress.txt + git + init.sh bridge sessions |
| Incremental work | One feature per session, explicit verification |

### Context Engineering

Source: [Anthropic - Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**Definition**: The art and science of curating what goes into the limited context window.

> "Context, therefore, must be treated as a finite resource with diminishing marginal returns."

**Context Management Patterns**:

| Pattern | Purpose | Trade-off |
|---------|---------|-----------|
| Just-in-time retrieval | Load data at runtime via tools | Slower but more accurate |
| Progressive disclosure | Incremental discovery through exploration | Requires good tools |
| Compaction | Summarize + reset context window | Risk of losing subtle context |
| Structured note-taking | External memory, pull when needed | Minimal overhead |
| Sub-agent architectures | Specialized agents return distilled summaries | Coordination complexity |

---

## Academic Research

### Memory Taxonomy

Source: [arXiv - Memory in the Age of AI Agents](https://arxiv.org/abs/2512.13564)

| Memory Type | Description |
|-------------|-------------|
| Factual | Storing explicit knowledge and information |
| Experiential | Retaining past interactions and experiences |
| Working | Managing current task context and intermediate states |

**Design Dimensions**: Formation → Evolution → Retrieval

### Reflexion Pattern

Source: [Reflexion Paper (NeurIPS 2023)](https://arxiv.org/abs/2303.11366)

Two-phase reflection for verbal reinforcement learning:
1. REFLECT: "What assumption failed?"
2. GENERATE: "How to prevent this?"

### Learning Loop Research

| Source | Focus | Key Finding |
|--------|-------|-------------|
| [OODA Loop Analysis](https://tao-hpu.medium.com/agent-feedback-loops-from-ooda-to-self-reflection-92eb9dd204f6) | Military strategy applied to AI | Real-time adaptation pattern |
| [Spotify Engineering](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3) | Production verification loops | Quality gates with veto power |

---

## Production Memory Systems

| System | Approach |
|--------|----------|
| Cursor/Windsurf | Static index + vector embeddings + dependency graph |
| ByteRover/Cipher | System 1 (knowledge) + System 2 (reasoning) + Workspace |
| Mem0 | Vector store + LLM extraction (90% lower tokens) |
| Claude-mem | SQLite + Chroma, auto-capture + summarization |
| Strands Agents | STM + LTM strategies (summary, preference, semantic) |

---

## Multi-Agent Research (Related)

| Source | Focus |
|--------|-------|
| [Anthropic Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) | 4-agent sequence, enforcement hooks |
| [Databricks Supervisor Architecture](https://www.databricks.com/blog/multi-agent-supervisor-architecture-orchestrating-enterprise-ai-scale) | Supervisor pattern at scale |
| [Azure Agent Orchestration Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) | Pattern catalog |
| [Multi-Agent Collaboration Survey](https://arxiv.org/abs/2501.06322) | Academic survey (2025) |

---

*See also: `.skills/coordination/` for multi-agent coordination patterns*
