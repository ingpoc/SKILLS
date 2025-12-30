# MVP-First Feature Breakdown Pattern

**Source**: Validated by [autonomous-coding quickstart](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)

**Problem**: autonomous-coding generates 200 features (takes 20 min to generate, hours to implement)

**Solution**: Start with 10 core features for MVP, expand iteratively

---

## Feature Tiers

```
┌─────────────────────────────────────────────────────────────┐
│              FEATURE TIER STRATEGY                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  MVP (10 features)       ────► Core functionality           │
│     │                                                   │    │
│     │── Time: 2 min to generate                         │    │
│     │── Implement: ~2-4 hours                           │    │
│     │── Value: Working product                          │    │
│                                                              │
│  EXPANSION (30 features)  ────► Important features          │
│     │                                                   │    │
│     │── Time: 5 min to generate                         │    │
│     │── Implement: ~8-12 hours                          │    │
│     │── Value: Production-ready                         │    │
│                                                              │
│  POLISH (200 features)    ────► Comprehensive coverage       │
│     │                                                   │    │
│     │── Time: 20 min to generate                        │    │
│     │── Implement: ~40+ hours                           │    │
│     │── Value: Edge cases handled                        │    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Tier Comparison

| Tier | Features | Generate Time | Implement Time | Use Case |
|------|----------|---------------|----------------|----------|
| **MVP** | 10 | ~2 min | 2-4 hours | Proof of concept |
| **Expansion** | 30 | ~5 min | 8-12 hours | Production beta |
| **Polish** | 200 | ~20 min | 40+ hours | Full release |

**Recommendation**: Start with MVP, validate, then expand.

---

## MVP Feature Selection Criteria

### Core Functionality (Must Have)

```
┌─────────────────────────────────────────────────────────────┐
│  MVP FEATURES: What makes the product WORK?                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Primary user goal                                       │
│     └─ "What is the ONE thing user must accomplish?"        │
│                                                              │
│  2. Data persistence                                        │
│     └─ "Can user save and restore their work?"              │
│                                                              │
│  3. Basic validation                                         │
│     └─ "Are critical errors prevented?"                     │
│                                                              │
│  4. User feedback                                            │
│     └─ "Does user know what happened?"                      │
│                                                              │
│  5. Error handling                                           │
│     └─ "Can user recover from failures?"                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Example: Todo App MVP

| Feature | Why MVP? | Priority |
|---------|----------|----------|
| Create todo | Primary goal | P0 |
| List todos | View data | P0 |
| Mark complete | Basic workflow | P0 |
| Delete todo | Data management | P0 |
| Persistent storage | Data persistence | P0 |
| Input validation | Error prevention | P1 |
| Success messages | User feedback | P1 |
| Error messages | Error handling | P1 |
| Empty state | User guidance | P2 |
| Confirm delete | Safety | P2 |

**Total**: 10 features (6 P0, 2 P1, 2 P2)

**NOT in MVP**: Search, filter, tags, sharing, export, themes, etc.

---

## Expansion Tier (30 Features)

After MVP validation, add:

| Category | Features | Examples |
|----------|----------|----------|
| **Enhanced UX** | 5-8 | Search, filter, sort, pagination |
| **Collaboration** | 3-5 | Share, comments, multi-user |
| **Integrations** | 3-5 | Calendar, notifications, sync |
| **Analytics** | 2-3 | Usage stats, reports |
| **Polish** | 5-8 | Themes, keyboard shortcuts, undo/redo |

---

## Polish Tier (200 Features)

Comprehensive coverage for production:

- Edge cases
- Accessibility
- Performance optimization
- Advanced features
- Localization
- Security hardening
- Analytics dashboard
- Admin panel
- API for third parties
- Mobile optimization

---

## Feature Breakdown Prompt

### MVP Prompt Template

```markdown
# Feature Breakdown: MVP-First Strategy

## Application: {app_name}

## User Requirements
{user_requirements}

## Instructions

Generate **10 MVP features** following these criteria:

1. **Primary Goal Only**: Features essential for core user journey
2. **INVEST Criteria**:
   - Independent: Can implement separately
   - Negotiable: Could defer if needed
   - Valuable: User-facing value
   - Estimatable: Can estimate effort
   - Small: Completable in <4 hours
   - Testable: Can verify with tests

3. **Priority Distribution**:
   - P0: 6 features (critical path)
   - P1: 2 features (important but not blocking)
   - P2: 2 features (nice to have)

## Output Format

```json
{{
  "tier": "mvp",
  "total_features": 10,
  "features": [
    {{
      "id": "feat-001",
      "name": "Feature name",
      "description": "What user can do",
      "priority": "P0",
      "estimate_hours": 2,
      "dependencies": [],
      "acceptance_criteria": [" criterion 1", " criterion 2"],
      "test_cases": [
        {{"given": "context", "when": "action", "then": "result"}}
      ]
    }}
  ]
}}
```

## Focus

- **Completeness**: Can user achieve primary goal?
- **Validation**: Are errors caught?
- **Feedback**: Does user know what's happening?
- **Recovery**: Can user recover from failures?

DO NOT include:
- Advanced features
- Edge cases
- Nice-to-have UI
- Analytics/admin
```

---

## Progressive Expansion

### MVP → Expansion

```python
def expand_mvp_to_expansion(mvp_features: list) -> list:
    """
    After MVP is complete, generate expansion features.
    """
    # MVP should be validated by users first
    if not validate_mvp(mvp_features):
        return []

    # Generate 20 additional features
    expansion_features = generate_features(
        count=20,
        base_features=mvp_features,
        focus=["enhanced_ux", "collaboration", "integrations"]
    )

    return mvp_features + expansion_features
```

### Expansion → Polish

```python
def expand_to_polish(expansion_features: list) -> list:
    """
    After expansion is validated, generate polish features.
    """
    # Generate 170 additional features for comprehensive coverage
    polish_features = generate_features(
        count=170,
        base_features=expansion_features,
        focus=["edge_cases", "accessibility", "performance", "security"]
    )

    return expansion_features + polish_features
```

---

## Validation Gates

### MVP Validation

```python
def validate_mvp_complete() -> bool:
    """
    Verify MVP is ready for user testing.
    """
    checks = [
        all_p0_features_complete(),
        primary_user_goal_achievable(),
        basic_error_handling_works(),
        data_persists_correctly(),
        user_feedback_clear()
    ]

    return all(checks)
```

### Expansion Decision

```python
def should_expand_to_expansion() -> bool:
    """
    Decide whether to expand from MVP to Expansion tier.
    """
    # User validation
    user_feedback = collect_user_feedback()

    if user_feedback.satisfaction < 0.7:
        return False  # Fix MVP first

    # Technical validation
    if critical_bugs_exist():
        return False  # Fix bugs first

    # Business validation
    if not product_market_fit():
        return False  # Pivot, don't expand

    return True
```

---

## Time Comparison

### autonomous-coding Approach (200 features)

```
Session 1: Generate 200 features → 20 minutes
Sessions 2+: Implement 200 features → 40+ hours
──────────────────────────────────────────────
Total: 40+ hours to working product
```

### MVP-First Approach

```
Session 1: Generate 10 features → 2 minutes
Sessions 2+: Implement 10 features → 2-4 hours
──────────────────────────────────────────────
Total: 2-4 hours to working product

Validate with users → Decide to expand
Session N: Generate 20 more features → 5 minutes
Sessions N+: Implement expansion → 8-12 hours
──────────────────────────────────────────────
Expansion Total: 8-12 hours
```

**Time Savings**: 50%+ if MVP reveals need to pivot

---

## Feature Template

```json
{
  "tier": "mvp",
  "metadata": {
    "generated_at": "2025-12-28T16:30:00Z",
    "total_features": 10,
    "estimate_hours": 16
  },
  "features": [
    {
      "id": "feat-001",
      "name": "User authentication",
      "description": "User can sign up and login with email/password",
      "priority": "P0",
      "estimate_hours": 3,
      "dependencies": [],
      "acceptance_criteria": [
        "User can create account with email and password",
        "User receives confirmation email",
        "User can login with credentials",
        "Invalid credentials show error message"
      ],
      "test_cases": [
        {
          "given": "new user on signup page",
          "when": "submits valid email and password",
          "then": "account created and redirected to login"
        },
        {
          "given": "registered user on login page",
          "when": "submits invalid password",
          "then": "error message shown"
        }
      ]
    }
  ]
}
```

---

## Scripts

**Generate MVP features:**
```bash
#!/bin/bash
# .skills/initialization/scripts/generate-mvp-features.sh

APP_NAME="${1:-MyApp}"
REQUIREMENTS_FILE="${2:-requirements.txt}"

# Call AI to generate MVP features (10 features)
claude \
  --prompt "$(cat <<EOF
Generate 10 MVP features for: $APP_NAME

Requirements:
$(cat $REQUIREMENTS_FILE)

Follow MVP-first pattern in .skills/initialization/references/mvp-feature-breakdown.md
EOF
)" \
  --output .claude/progress/feature-list.json

# Verify output
jq '.tier == "mvp"' .claude/progress/feature-list.json
jq '.features | length == 10' .claude/progress/feature-list.json
```

**Expand to next tier:**
```bash
#!/bin/bash
# .skills/initialization/scripts/expand-features.sh

CURRENT_TIER="${1:-mvp}"
TARGET_COUNT="${2:-30}"

# Validate current tier is complete
./validate-tier-complete.sh "$CURRENT_TIER"

# Generate additional features
claude \
  --prompt "Expand $CURRENT_TIER features to $TARGET_COUNT following progressive expansion pattern" \
  --output .claude/progress/feature-list-expanded.json

# Merge features
jq -s '.[0].features + .[1].features | {tier: "expansion", total_features: $TARGET_COUNT, features: .}' \
  .claude/progress/feature-list.json \
  .claude/progress/feature-list-expanded.json \
  > .claude/progress/feature-list.json
```

---

## Decision Tree

```
                    Start Project
                         │
                         ▼
                  Generate MVP (10)
                         │
                    2 min, 2-4 hours
                         │
                         ▼
              ┌──────────────────────┐
              │   MVP Complete?      │
              └──────────────────────┘
                    │         │
                   Yes        No
                    │         │
                    ▼         ▼
            ┌──────────┐   Fix issues
            │ Validate │       │
            │ with     │       │
            │ Users    │       │
            └──────────┘       │
                    │         │
         ┌──────────┴─────────┘
         │
         ▼
  ┌──────────────────────┐
  │ Users satisfied?     │
  └──────────────────────┘
        │           │
       Yes          No
        │           │
        ▼           ▼
   Expand to   Pivot or
  Expansion   Improve
  (30 features)
        │
   5 min, 8-12 hours
        │
        ▼
  ┌──────────────────────┐
  │ Expansion validated? │
  └──────────────────────┘
        │           │
       Yes          No
        │           │
        ▼           ▼
   Expand to   Refine and
  Polish    revalidate
  (200 features)
        │
   20 min, 40+ hours
```

---

## Best Practices

1. **Start small**: 10 features MVP
2. **Validate early**: Get user feedback before expanding
3. **Iterative expansion**: Add features in tiers
4. **Pivot ready**: Don't invest 40+ hours if MVP reveals need to change
5. **Progressive disclosure**: Generate features as needed, not upfront

---

## Anti-Patterns

| ❌ Anti-Pattern | ✅ Correct Pattern |
|-----------------|-------------------|
| Generate 200 features upfront | Generate 10 MVP features |
| Implement all before testing | Test MVP after each feature |
| Fixed scope | Adaptive scope based on feedback |
| Time-based estimates | Complexity-based estimates |
| Assume success | Validate assumptions early |

---

*Added: 2025-12-28*
*Source: autonomous-coding quickstart analysis + MVP best practices*
*Time savings: 50%+ if MVP reveals need to pivot*
