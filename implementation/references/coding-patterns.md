# Coding Patterns

## Implementation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  IMPLEMENTATION WORKFLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. READ FEATURE                                             │
│     └── Get next pending from feature-list.json             │
│                                                              │
│  2. UNDERSTAND CONTEXT                                       │
│     ├── Read related existing code                          │
│     ├── Query past similar implementations                  │
│     └── Identify patterns to follow                         │
│                                                              │
│  3. IMPLEMENT                                                │
│     ├── Write code following project conventions            │
│     ├── Add inline comments for complex logic               │
│     └── Handle edge cases                                   │
│                                                              │
│  4. WRITE TESTS                                              │
│     ├── Unit tests for new functions                        │
│     ├── Integration tests for API endpoints                 │
│     └── Match tests to feature.tests list                   │
│                                                              │
│  5. VERIFY                                                   │
│     ├── Run health check                                    │
│     ├── Run linter                                          │
│     └── Confirm no regressions                              │
│                                                              │
│  6. UPDATE STATUS                                            │
│     └── Mark feature as "completed" (not "tested")          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Code Quality Standards

### Naming Conventions

| Type | Python | TypeScript |
|------|--------|------------|
| Variables | snake_case | camelCase |
| Functions | snake_case | camelCase |
| Classes | PascalCase | PascalCase |
| Constants | UPPER_SNAKE | UPPER_SNAKE |
| Files | snake_case.py | kebab-case.ts |

### Function Guidelines

```python
# Good: Single responsibility, clear name, typed
def calculate_order_total(items: list[OrderItem], tax_rate: float) -> Decimal:
    """Calculate total with tax for order items."""
    subtotal = sum(item.price * item.quantity for item in items)
    return subtotal * (1 + tax_rate)

# Bad: Multiple responsibilities, unclear, untyped
def process(data):
    # Does too many things...
    pass
```

### Error Handling

```python
# Good: Specific exceptions, meaningful messages
def get_user(user_id: str) -> User:
    user = db.users.find_one({"id": user_id})
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    return User(**user)

# Bad: Generic exceptions, no context
def get_user(user_id):
    try:
        return db.users.find_one({"id": user_id})
    except:
        raise Exception("Error")
```

## Implementation Patterns

### API Endpoint (FastAPI)

```python
# src/routes/users.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    email: str
    name: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db = Depends(get_db)):
    """Create a new user."""
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(400, "Email already registered")

    user_data = user.model_dump()
    user_data["id"] = generate_id()
    await db.users.insert_one(user_data)

    return UserResponse(**user_data)
```

### React Component (TypeScript)

```typescript
// src/components/UserCard.tsx
import { FC } from 'react';

interface UserCardProps {
  user: {
    id: string;
    name: string;
    avatar?: string;
  };
  onSelect?: (id: string) => void;
}

export const UserCard: FC<UserCardProps> = ({ user, onSelect }) => {
  return (
    <div
      className="user-card"
      onClick={() => onSelect?.(user.id)}
    >
      <img
        src={user.avatar ?? '/default-avatar.png'}
        alt={user.name}
      />
      <h3>{user.name}</h3>
    </div>
  );
};
```

### Database Migration

```python
# migrations/001_create_users.py
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

def downgrade():
    op.drop_table('users')
```

## Test Writing

### Unit Test Pattern

```python
# tests/test_order_total.py
import pytest
from decimal import Decimal
from src.orders import calculate_order_total, OrderItem

class TestCalculateOrderTotal:
    def test_single_item(self):
        items = [OrderItem(price=Decimal("10.00"), quantity=1)]
        result = calculate_order_total(items, tax_rate=0.1)
        assert result == Decimal("11.00")

    def test_multiple_items(self):
        items = [
            OrderItem(price=Decimal("10.00"), quantity=2),
            OrderItem(price=Decimal("5.00"), quantity=1),
        ]
        result = calculate_order_total(items, tax_rate=0.1)
        assert result == Decimal("27.50")

    def test_zero_tax(self):
        items = [OrderItem(price=Decimal("10.00"), quantity=1)]
        result = calculate_order_total(items, tax_rate=0.0)
        assert result == Decimal("10.00")

    def test_empty_items(self):
        result = calculate_order_total([], tax_rate=0.1)
        assert result == Decimal("0.00")
```

### API Test Pattern

```python
# tests/test_users_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post("/users/", json={
        "email": "test@example.com",
        "name": "Test User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient):
    # Create first user
    await client.post("/users/", json={
        "email": "test@example.com",
        "name": "First"
    })
    # Try duplicate
    response = await client.post("/users/", json={
        "email": "test@example.com",
        "name": "Second"
    })
    assert response.status_code == 400
```

## Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| God function | Too many responsibilities | Split into smaller functions |
| Magic numbers | Unclear intent | Use named constants |
| Nested callbacks | Hard to read | Use async/await |
| Copy-paste | Duplication | Extract common logic |
| No error handling | Silent failures | Add try/catch with logging |
| Tight coupling | Hard to test | Use dependency injection |

## Pre-Commit Checklist

Before marking feature complete:

- [ ] Code follows project conventions
- [ ] All new functions have docstrings
- [ ] Edge cases handled
- [ ] Tests written for each feature.test
- [ ] No linter errors
- [ ] No type errors (if TypeScript/typed Python)
- [ ] Health check passes
