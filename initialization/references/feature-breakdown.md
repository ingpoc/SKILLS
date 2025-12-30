# Feature Breakdown Patterns

## Principles

From [Anthropic Long-Running Harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents):

> "Break work into atomic, testable features. Each feature should be completable in a single session."

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
  "id": "API-001",
  "description": "Create GET /api/users endpoint",
  "type": "api",
  "tests": [
    "Returns 200 with user list",
    "Returns 401 if unauthorized",
    "Supports pagination"
  ],
  "files": ["src/routes/users.py", "tests/test_users.py"],
  "dependencies": ["API-000"],
  "priority": "P0"
}
```

### UI Component Feature

```json
{
  "id": "UI-001",
  "description": "Create UserCard component",
  "type": "ui",
  "tests": [
    "Renders user name and avatar",
    "Shows loading state",
    "Handles missing avatar"
  ],
  "files": ["src/components/UserCard.tsx", "tests/UserCard.test.tsx"],
  "dependencies": ["API-001"],
  "priority": "P1"
}
```

### Database Feature

```json
{
  "id": "DB-001",
  "description": "Create users table with migration",
  "type": "database",
  "tests": [
    "Migration runs successfully",
    "Rollback works",
    "Indexes created"
  ],
  "files": ["migrations/001_users.sql"],
  "dependencies": [],
  "priority": "P0"
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
  "created_at": "2025-12-28T10:00:00Z",
  "features": [
    {
      "id": "PT-001",
      "description": "Feature description",
      "type": "api|ui|database|integration|config",
      "priority": "P0|P1|P2",
      "status": "pending|in_progress|completed|blocked",
      "tested": false,
      "dependencies": ["PT-000"],
      "tests": ["test description 1", "test description 2"],
      "files": ["expected/file/paths.py"],
      "notes": "Optional implementation notes"
    }
  ]
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
- [ ] Dependencies are mapped
- [ ] No circular dependencies
- [ ] Priority assigned (P0/P1/P2)
- [ ] Ordered by dependency + priority
- [ ] No feature > 2 hours estimated
