# Unit Testing Patterns

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
