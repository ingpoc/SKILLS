# Context Graph Storage

Storage options for decision traces with semantic search.

## Storage Options Comparison

| Option | Semantic Search | Setup | MCP Native | Best For |
|--------|-----------------|-------|------------|----------|
| **Qdrant Local** | Best | Medium | Official | Production, needs best search |
| **sqlite-vec** | Good | Low | Community (Memento) | Simple setup, good search |
| **Cipher** | Good | Medium | Yes | Integrated solution |
| **File-based** | Text only | Zero | N/A | Prototyping, no search needed |

## Recommendation

**Qdrant Local** or **sqlite-vec** embedded in token-efficient MCP server.

## Three-Tier Architecture

| Tier | Type | Size | Access |
|------|------|------|--------|
| **Hot** | In-context | ~10K tokens | Immediate |
| **Warm** | Vector search | On-demand | Semantic query |
| **Cold** | Full traces | Never direct load | By ID only |

## Production Memory Patterns

| System | Approach |
|--------|----------|
| Cursor/Windsurf | Static index + vector embeddings + dependency graph |
| ByteRover/Cipher | System 1 (knowledge) + System 2 (reasoning) + Workspace |
| Mem0 | Vector store + LLM extraction (90% lower tokens) |
| Claude-mem | SQLite + Chroma, auto-capture + summarization |
| Strands Agents | STM + LTM strategies (summary, preference, semantic) |

## Storage Schema

### Trace Record

```json
{
  "id": "trace_20241227_003",
  "timestamp": "2024-12-27T10:30:00Z",
  "agent": "coding-agent",
  "session_id": "session_123",
  "outcome": "success",
  "metadata": {
    "feature_id": "PT-003",
    "files_changed": ["src/feature.py"],
    "tests_pass": true
  },
  "summary": "Implemented feature PT-003 with test coverage 85%. Fixed 2 bugs during implementation.",
  "full_trace": {
    "decisions": [...],
    "actions": [...],
    "corrections": [...]
  },
  "embedding": [0.123, 0.456, ...],
  "tags": ["feature", "success", "bug-fix"],
  "pattern_matches": ["empty_data_rule_violation"]
}
```

### Query Interface

```python
def store_trace(trace: dict) -> str:
    """Store trace, return trace ID"""

def query_traces(query: str, level: str = "metadata", limit: int = 10) -> list:
    """Semantic search for similar traces"""

def get_trace(trace_id: str, level: str = "full") -> dict:
    """Retrieve specific trace by ID"""

def extract_patterns(min_occurrences: int = 3) -> list:
    """Find repeated patterns across traces"""
```

## Token Economics

| Operation | Cost | ROI |
|-----------|------|-----|
| Store trace | ~50 tokens | Foundation |
| Query traces | ~100 tokens | Prevention |
| Load summaries (top 3) | ~600 tokens | Context |
| **Total per decision** | ~750 tokens | 12x ROI vs rework |

## Implementation Notes

1. **Store only high-signal traces** - Not every interaction
2. **Use progressive disclosure** - metadata → summary → full
3. **Apply compaction** - When context approaches limits
4. **Sub-agents return distilled summaries** - Not full context
