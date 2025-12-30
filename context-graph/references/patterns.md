# Context Graph Patterns

Core patterns for context engineering in multi-agent systems.

## Progressive Disclosure

From Anthropic Agent Skills and Code Execution MCP articles.

### Three-Tier Loading

| Level | Content | When to Use | Token Cost |
|-------|---------|-------------|------------|
| `name_only` | Just tool/trace names | Discovery phase | ~100 |
| `with_description` | Name + metadata | Filtering relevance | ~500 |
| `full_schema` | Complete details | Actual usage | ~2K-5K |

### Token Impact

**Before**: 150,000 tokens (all traces loaded)
**After**: 2,000 tokens (metadata only, load on demand)
**Savings**: 98.7%

### Implementation Pattern

```python
def query_traces(query, level="metadata"):
    if level == "metadata":
        return [t.metadata for t in traces if match(query, t)]
    elif level == "summary":
        return [t.summary for t in traces if match(query, t)]
    elif level == "full":
        return [t for t in traces if match(query, t)]
```

---

## Compaction Strategy

From Anthropic Context Engineering article.

### Sub-Agent Distillation

Specialized agents return condensed summaries (1K-2K tokens), not full context.

| Agent | Returns | Token Budget |
|-------|---------|--------------|
| coding-agent | Files changed, tests run, issues | ~1K |
| tester-agent | Test results, evidence, pass/fail | ~1K |
| initializer-agent | Feature list, setup, next steps | ~1.5K |

### Preserve vs Discard

| Preserve | Discard |
|----------|---------|
| Architectural decisions | Redundant tool outputs |
| Unresolved bugs | Raw results (once used) |
| Implementation details | Verbose logs |
| Recent 5 files | Historical context |

### When to Apply Compaction

| Use Case | Pattern |
|----------|---------|
| Extensive back-and-forth | Compaction |
| Iterative development | Note-taking |
| Complex research | Multi-agent |

---

## Handoff Protocols

From multi-agent coordination research.

### Command Object Schema

```json
{
  "command": {
    "agent": "tester-agent",
    "task": "validate_feature",
    "context": {
      "feature_id": "PT-003",
      "files_changed": ["src/feature.py"],
      "previous_state": "coding",
      "artifacts": {
        "implementation": "/tmp/impl/",
        "test_config": "/tmp/tests/"
      }
    },
    "success_criteria": {
      "tests_pass": true,
      "coverage_min": 80
    },
    "next_agent": "main"
  }
}
```

### Handoff Elements

| Element | Description | Example |
|---------|-------------|---------|
| Precondition | What must be complete | Code written, linted |
| Artifacts | What's passed along | File paths, test results |
| Postcondition | What next agent expects | Ready-to-test state |
| Rollback | How to handle failures | Return to previous state |

### Best Practices

1. **Explicit context** - Pass command objects, not implicit state
2. **Verification** - Next agent validates preconditions
3. **Idempotency** - Handoff safe to retry
4. **Observability** - Log every handoff with context
5. **Timeout** - Fail fast if agent unresponsive

---

## Context Window Management

### Attention Budget

Every token depletes attention budget. n² pairwise relationships for n tokens creates "context rot."

### Decision Framework

| Use This When | Pattern |
|---------------|---------|
| Extensive back-and-forth required | Compaction |
| Iterative development with milestones | Note-taking |
| Complex research/analysis with parallel exploration | Multi-agent |

### State Persistence Pattern

```json
{
  "checkpoint": {
    "timestamp": "2025-12-27T10:30:00Z",
    "state": "testing",
    "agent": "tester-agent",
    "feature": "PT-003",
    "context": {
      "files": ["src/feature.py"],
      "test_artifacts": ["/tmp/test-1.json"]
    },
    "resume_command": "python3 test_feature.py PT-003"
  }
}
```
