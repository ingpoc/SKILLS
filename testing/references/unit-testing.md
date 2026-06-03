# Unit Testing Patterns

## Pre-Flight Checklist (Before Testing)

**Before running tests**, check context graph and error count:

```bash
# 1. Check context graph for similar past issues
context_query_traces("keyword from expected error")

# 2. Count errors to determine strategy
ERROR_COUNT=$(pnpm typecheck 2>&1 | grep -c "error" || echo "0")

# 3. If errors > 20, use batch fixes (see below)
#    If errors < 20, fix manually
```

| Error Count | Strategy |
|-------------|----------|
| 0 | Proceed with tests |
| 1-20 | Manual fix |
| 20+ | Batch fix script (below) |

---

## Type System Foundation

**Before testing type errors**, verify build state:

```bash
# Rebuild cascade (if types changed)
cd packages/website/shared && pnpm build
cd ../..

# Verify typecheck passes
pnpm typecheck
```

**Type hierarchy rule**:

```
Source of Truth: packages/shared/src/types/
↓
Re-export in packages/website/shared/src/types/
↓
Import in components: @ondc-website/shared
```

---

## Batch Fix Patterns

**For repetitive errors (>10 instances)**, use batch scripts:

### Pattern 1: Property Access Fallback

```bash
# Fix optional property access pattern
# Before: price.value
# After: price.value ?? price.amount
find packages/website -name "*.tsx" -exec sed -i '' \
  's/price\.value/price.value ?? price.amount/g' {} +
```

### Pattern 2: Add Optional Chaining

```bash
# Add optional chaining to nested properties
# Before: object.property.nested
# After: object.property?.nested
find packages/website -name "*.tsx" -exec sed -i '' \
  's/\([a-zA-Z_]\)\.\([a-zA-Z_]\)/\1?.\2/g' {} +
```

### Pattern 3: Replace Import Paths

```bash
# Replace old import paths with new ones
find packages/website -name "*.tsx" -exec sed -i '' \
  's|from.*old/path|from @new/package|g' {} +
```

### Pattern 4: Type Cast Addition

```bash
# Add type assertions for unknown types
# Before: const value = response.data
# After: const value = response.data as DataType
find packages/website -name "*.ts" -exec sed -i '' \
  's/const \(.*\) = \(.*\)\.data/const \1 = \2.data as \1Type/g' {} +
```

**After batch fix, always rebuild**:

```bash
# Rebuild affected packages
cd packages/website/shared && pnpm build
cd ../..

# Verify typecheck passes
pnpm typecheck
```

---

## Test Frameworks

| Language | Framework | Config File |
|----------|-----------|-------------|
| Python | pytest | pytest.ini, pyproject.toml |
| TypeScript | Jest | jest.config.js |
| TypeScript | Vitest | vitest.config.ts |
| Rust | cargo test | Cargo.toml |
| Go | go test | *_test.go |

## Pytest Patterns

### Basic Test Structure

```python
# tests/test_users.py
import pytest
from src.users import create_user, get_user, UserNotFoundError

class TestCreateUser:
    """Tests for user creation"""

    def test_creates_user_with_valid_data(self, db):
        """Should create user and return with ID"""
        result = create_user(email="test@example.com", name="Test")

        assert result.id is not None
        assert result.email == "test@example.com"

    def test_rejects_duplicate_email(self, db):
        """Should raise error for duplicate email"""
        create_user(email="test@example.com", name="First")

        with pytest.raises(ValueError, match="already exists"):
            create_user(email="test@example.com", name="Second")

    def test_validates_email_format(self):
        """Should reject invalid email format"""
        with pytest.raises(ValueError, match="invalid email"):
            create_user(email="not-an-email", name="Test")


class TestGetUser:
    """Tests for user retrieval"""

    def test_returns_user_by_id(self, db):
        """Should return user when found"""
        created = create_user(email="test@example.com", name="Test")
        result = get_user(created.id)

        assert result.email == "test@example.com"

    def test_raises_when_not_found(self, db):
        """Should raise UserNotFoundError"""
        with pytest.raises(UserNotFoundError):
            get_user("nonexistent-id")
```

### Fixtures

```python
# tests/conftest.py
import pytest
from src.database import Database

@pytest.fixture
def db():
    """Provide clean database for each test"""
    database = Database(":memory:")
    database.migrate()
    yield database
    database.close()

@pytest.fixture
def client(db):
    """Provide test client"""
    from src.app import create_app
    app = create_app(database=db)
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Provide authenticated headers"""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
```

### Parametrized Tests

```python
@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("user@example.co.uk", True),
    ("user@localhost", False),
    ("not-an-email", False),
    ("@example.com", False),
    ("user@", False),
])
def test_email_validation(email, valid):
    if valid:
        assert validate_email(email) is True
    else:
        with pytest.raises(ValueError):
            validate_email(email)
```

## Jest/Vitest Patterns

### Basic Test Structure

```typescript
// tests/users.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { createUser, getUser, UserNotFoundError } from '../src/users';

describe('createUser', () => {
  beforeEach(() => {
    // Reset database
  });

  it('should create user with valid data', async () => {
    const result = await createUser({
      email: 'test@example.com',
      name: 'Test'
    });

    expect(result.id).toBeDefined();
    expect(result.email).toBe('test@example.com');
  });

  it('should reject duplicate email', async () => {
    await createUser({ email: 'test@example.com', name: 'First' });

    await expect(
      createUser({ email: 'test@example.com', name: 'Second' })
    ).rejects.toThrow('already exists');
  });
});

describe('getUser', () => {
  it('should return user by id', async () => {
    const created = await createUser({
      email: 'test@example.com',
      name: 'Test'
    });

    const result = await getUser(created.id);
    expect(result.email).toBe('test@example.com');
  });

  it('should throw when not found', async () => {
    await expect(getUser('nonexistent')).rejects.toThrow(UserNotFoundError);
  });
});
```

### Mocking

```typescript
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { sendEmail } from '../src/email';
import { processOrder } from '../src/orders';

// Mock email module
vi.mock('../src/email', () => ({
  sendEmail: vi.fn()
}));

describe('processOrder', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should send confirmation email', async () => {
    await processOrder({ id: '123', email: 'test@example.com' });

    expect(sendEmail).toHaveBeenCalledWith({
      to: 'test@example.com',
      template: 'order-confirmation',
      data: expect.objectContaining({ orderId: '123' })
    });
  });
});
```

## Test Execution Scripts

### Python Test Runner

```bash
#!/bin/bash
# scripts/run-unit-tests.sh

set -e

echo "=== Running Unit Tests ==="

# Run pytest with coverage
pytest tests/ \
    --tb=short \
    -q \
    --cov=src \
    --cov-report=term-missing \
    --cov-fail-under=80

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "PASS: All unit tests passed"
else
    echo "FAIL: Unit tests failed"
fi

exit $EXIT_CODE
```

### Node Test Runner

```bash
#!/bin/bash
# scripts/run-unit-tests.sh

set -e

echo "=== Running Unit Tests ==="

npm test -- --coverage --passWithNoTests

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "PASS: All unit tests passed"
else
    echo "FAIL: Unit tests failed"
fi

exit $EXIT_CODE
```

## Test Evidence Collection

```python
# scripts/collect-test-evidence.py
import json
import subprocess
import os
from datetime import datetime

EVIDENCE_DIR = "/tmp/test-evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def run_tests():
    result = subprocess.run(
        ["pytest", "tests/", "--tb=short", "-q", "--json-report"],
        capture_output=True,
        text=True
    )

    evidence = {
        "timestamp": datetime.now().isoformat(),
        "exit_code": result.returncode,
        "passed": result.returncode == 0,
        "stdout": result.stdout[-2000:],  # Last 2000 chars
        "stderr": result.stderr[-1000:]
    }

    with open(f"{EVIDENCE_DIR}/unit-tests.json", "w") as f:
        json.dump(evidence, f, indent=2)

    return result.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    print(f"Tests {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1)
```

## Test Coverage Requirements

| Coverage Type | Minimum | Target |
|---------------|---------|--------|
| Line coverage | 70% | 85% |
| Branch coverage | 60% | 75% |
| Function coverage | 80% | 90% |

## Common Test Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Testing implementation | Brittle tests | Test behavior/outcomes |
| No assertions | Tests always pass | Add meaningful assertions |
| Shared mutable state | Tests interfere | Use fixtures, reset state |
| Testing external services | Slow, unreliable | Mock external calls |
| Giant test functions | Hard to debug | One assertion per test |
