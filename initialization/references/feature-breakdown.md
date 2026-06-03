# Feature Breakdown Patterns

## Principles

From [Anthropic Long-Running Harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents):

> "Break work into atomic, testable features. Each feature should be completable in a single session."

## Plan References

Each feature should have a `plan_reference` indicating its origin:

| Type | Value | When to Use |
|------|-------|-------------|
| AI-generated | `~/.claude/plans/xxx.md` | Feature from initialization skill plan |
| User plan | User-specified path | Feature from user-provided plan document |
| User-generated | `null` | Ad-hoc feature from brainstorming |

### Project-level plan_reference

```json
{
  "project": "my-project",
  "plan_reference": "~/.claude/plans/plan-name.md",  // Optional overall plan
  "features": [...]
}
```

### Feature-level plan_reference

```json
{
  "id": "F001",
  "plan_reference": "~/.claude/plans/plan-name.md",  // or null
  "plan_section": "## Phase 1 > Task 1"  // Optional section reference
}
```

### Determining plan_reference

| Scenario | plan_reference |
|----------|----------------|
| User provided detailed plan | Path to user's plan |
| Initialization skill created plan | Path to generated plan |
| Feature mentioned during chat | `null` (user-generated) |
| No clear plan exists | `null` |

### Atomic Feature Criteria

| Criterion | Good | Bad |
|-----------|------|-----|
| Scope | Single responsibility | Multiple concerns |
| Testable | Clear pass/fail | Subjective quality |
| Independent | Minimal dependencies | Tightly coupled |
| Estimable | 1-2 hour implementation | "It depends" |
| Valuable | Delivers user value | Internal refactoring only |

## Breakdown Process

```
┌─────────────────────────────────────────────────────────────┐
│                 FEATURE BREAKDOWN FLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [REQUIREMENTS]                                              │
│       │                                                      │
│       ▼                                                      │
│  1. Identify user-facing capabilities                       │
│       │                                                      │
│       ▼                                                      │
│  2. Decompose into atomic features                          │
│       │                                                      │
│       ▼                                                      │
│  3. Identify dependencies between features                  │
│       │                                                      │
│       ▼                                                      │
│  4. Prioritize (P0 > P1 > P2)                               │
│       │                                                      │
│       ▼                                                      │
│  5. Order by dependencies + priority                        │
│       │                                                      │
│       ▼                                                      │
│  [FEATURE LIST]                                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Feature Categories

| Category | Description | Example |
|----------|-------------|---------|
| **Foundation** | Must exist before others | Database schema, API setup |
| **Core** | Main functionality | User authentication, CRUD |
| **Enhancement** | Improves core | Caching, validation |
| **Polish** | User experience | Error messages, loading states |

## Feature Size Guidelines

| Size | Time | Scope |
|------|------|-------|
| XS | < 30 min | Single function, simple change |
| S | 30-60 min | Single file, few functions |
| M | 1-2 hours | Multiple files, one feature |
| L | 2-4 hours | Should be broken down |
| XL | > 4 hours | Must be broken down |

## Breakdown Templates

### API Endpoint Feature

```json
{
  "id": "F001",
  "description": "Create GET /api/users endpoint",
  "priority": 1,
  "status": "pending",
  "phase": "api",
  "plan_reference": null,
  "dependencies": [],
  "acceptance_criteria": [
    "Returns 200 with user list",
    "Returns 401 if unauthorized",
    "Supports pagination"
  ]
}
```

### UI Component Feature

```json
{
  "id": "F002",
  "description": "Create UserCard component",
  "priority": 2,
  "status": "pending",
  "phase": "ui",
  "plan_reference": null,
  "dependencies": ["F001"],
  "acceptance_criteria": [
    "Renders user name and avatar",
    "Shows loading state",
    "Handles missing avatar"
  ]
}
```

### Database Feature

```json
{
  "id": "F003",
  "description": "Create users table with migration",
  "priority": 1,
  "status": "pending",
  "phase": "database",
  "plan_reference": "~/.claude/plans/my-plan.md",
  "plan_section": "## Database Schema",
  "dependencies": [],
  "acceptance_criteria": [
    "Migration runs successfully",
    "Rollback works",
    "Indexes created"
  ]
}
```

## Dependency Ordering

```python
def order_features(features: list) -> list:
    """Order features by dependencies, then priority"""
    ordered = []
    remaining = features.copy()

    while remaining:
        # Find features with no unmet dependencies
        ready = [
            f for f in remaining
            if all(d in [o["id"] for o in ordered] for d in f.get("dependencies", []))
        ]

        if not ready:
            raise ValueError("Circular dependency detected")

        # Sort ready features by priority
        ready.sort(key=lambda f: f.get("priority", "P2"))

        # Add first ready feature
        ordered.append(ready[0])
        remaining.remove(ready[0])

    return ordered
```

## Feature List Schema

```json
{
  "$schema": "feature-list-schema.json",
  "version": "1.0.0",
  "project": "project-name",
  "description": "Project description",
  "plan_reference": "~/.claude/plans/plan-name.md",  // Optional
  "created": "2025-12-28",
  "updated": "2025-12-28",
  "features": [
    {
      "id": "PT-001",
      "description": "Feature description",
      "priority": 1,
      "status": "pending",
      "phase": "foundation",
      "plan_reference": "~/.claude/plans/plan-name.md",  // or null
      "plan_section": "## Phase 1 > Task 1",  // Optional
      "dependencies": ["PT-000"],
      "acceptance_criteria": [
        "Testable criteria 1",
        "Testable criteria 2"
      ]
    }
  ],
  "phases": {
    "foundation": "PT-001-PT-010",
    "core": "PT-011-PT-030"
  }
}
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Too large | Can't complete in session | Break into smaller pieces |
| Too vague | "Improve performance" | Define specific metric |
| Missing tests | Can't verify completion | Add concrete test cases |
| Hidden deps | Blocked unexpectedly | Map dependencies first |
| Wrong order | Foundation missing | Sort by dependencies |

## Breakdown Checklist

Before finalizing feature list:

- [ ] Each feature has unique ID
- [ ] Each feature has clear description
- [ ] Each feature has at least one test
- [ ] plan_reference assigned (path or null)
- [ ] Dependencies are mapped
- [ ] No circular dependencies
- [ ] Priority assigned (1-12, lower = higher)
- [ ] Ordered by dependency + priority
- [ ] No feature > 2 hours estimated
