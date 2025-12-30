# Learning Loop Patterns

Patterns for agents to learn from experience and improve over time.

## Three Key Patterns

| Pattern | Source | Purpose |
|---------|--------|---------|
| **Reflexion** | Shinn et al., NeurIPS 2023 | Verbal reinforcement learning |
| **OODA Loop** | Military strategy → AI agents | Real-time adaptation |
| **Verification Loops** | Spotify production systems | Quality gates with veto power |

---

## Reflexion Pattern (Two-Phase Reflection)

**Architecture**: Actor → Evaluator → Self-Reflection → Memory

### Key Mechanism

Separate error analysis from solution generation (two LLM calls).

```
1. Agent generates action
2. Receive feedback (test results, errors)
3. REFLECT: "What assumption failed?" (LLM call #1)
4. GENERATE: "How to prevent this?" (LLM call #2)
5. Store reflection in episodic memory
6. Retrieve on next attempt
```

### Critical Design

`LAST_ATTEMPT_AND_REFLEXION` context injection on next attempt.

### Result

Dramatic improvement on tasks requiring multi-step reasoning.

---

## OODA Loop (Within-Trial Adaptation)

### Four Stages

| Stage | Action | Agent Context |
|-------|--------|---------------|
| **Observe** | Gather tool outputs, test results | Raw data |
| **Orient** | Apply past reflections + current context | Retrieved memories |
| **Decide** | Select action based on understanding | Planning |
| **Act** | Execute → generates new observations | Tool calls |

### Key Insight

OODA handles **within-trial** adaptation; Reflexion handles **across-trial** learning. Layer both for complete system.

---

## Spotify Verification Loops (Production Quality Gates)

### Architecture

- **Deterministic verifiers**: Maven/npm/build/test tools
- **LLM Judge**: Evaluates diff + prompt (prevents scope creep)
- **Stop hooks**: Run all verifiers before PR creation

### Metrics

- Judge vetoes ~25% of agent sessions
- 50% of vetoed sessions successfully course-correct

### Safety Principle

Agent doesn't know what verifiers do internally—only that they can be called. Prevents prompt injection attacks.

---

## Complete Learning Loop (Synthesized)

```
┌─────────────────────────────────────────────────────────────┐
│                    OUTER LOOP (Across Trials)                │
│                                                               │
│  Agent executes → Feedback → REFLEXION → Store → Validate    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    INNER LOOP (Within Trial)                 │
│                                                               │
│  OBSERVE → ORIENT → DECIDE → ACT → repeat                   │
└─────────────────────────────────────────────────────────────┘
```

---

## When to Update vs Keep Existing Behavior

| KEEP Existing | UPDATE Behavior |
|---------------|-----------------|
| Predictability critical | Data distribution shifts |
| Limited labeled feedback | Performance degradation detected |
| Preventing catastrophic forgetting | New capabilities needed |
| Regulatory/safety requirements | Environment changes |
| Core features stable | Tool use optimization needed |

---

## Staged Promotion (Production Pattern)

```
[EXPERIMENT] → [VALIDATE] → [PRODUCTION]
     ↓              ↓               ↓
  Test suite    Auto-rollback   Versioned memory
```

### Anti-Patterns to Avoid

| Anti-Pattern | Symptom | Fix |
|--------------|---------|-----|
| Reflection without action | Stored reflections never retrieved | Ensure retrieval surfaces relevant reflections |
| Over-indexing recent failures | Rapid oscillation between strategies | Balance recent with proven strategies |
| Generic reflections | "Reflect on performance" → useless | Use structured: "What assumption failed?" |
| Self-scoring without validation | Agent rates itself highly while failing | Compare self-assessment against external KPIs |
| Overthinking | Excessive planning without acting | Set max reflection iteration limits |

---

## Implementation Checklist

### Reflexion
- [ ] Separate error analysis (LLM call #1) from solution generation (LLM call #2)
- [ ] Store reflections in episodic memory
- [ ] Retrieve relevant reflections on next attempt
- [ ] Inject `LAST_ATTEMPT_AND_REFLEXION` into context

### OODA
- [ ] Observe: Gather tool outputs, test results
- [ ] Orient: Apply past reflections + current context
- [ ] Decide: Select action based on understanding
- [ ] Act: Execute, generates new observations

### Verification Loops
- [ ] Deterministic verifiers (build, test, lint)
- [ ] LLM Judge evaluates changes
- [ ] Stop hooks run all verifiers before state transition
- [ ] Veto power ~25% of sessions

### Staged Promotion
- [ ] EXPERIMENT: New patterns in test suite
- [ ] VALIDATE: Auto-rollback on failure
- [ ] PRODUCTION: Versioned memory, gradual rollout
