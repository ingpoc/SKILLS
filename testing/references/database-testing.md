# Database Testing Patterns

## Database Test Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  DATABASE TEST SEQUENCE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. SETUP                                                    │
│     ├── Create test database/schema                         │
│     ├── Run migrations                                      │
│     └── Seed test data                                      │
│                                                              │
│  2. EXECUTE                                                  │
│     └── Run operation (insert, update, query)               │
│                                                              │
│  3. VERIFY                                                   │
│     ├── Check row exists/updated                            │
│     ├── Verify constraints enforced                         │
│     └── Check indexes used                                  │
│                                                              │
│  4. CLEANUP                                                  │
│     └── Rollback or drop test data                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Database Verification Scripts

### PostgreSQL

```bash
#!/bin/bash
# scripts/verify-postgres.sh

DB_URL="${DATABASE_URL:-postgresql://localhost/testdb}"

echo "=== PostgreSQL Verification ==="

# 1. Connection test
echo "Testing connection..."
psql "$DB_URL" -c "SELECT 1" > /dev/null 2>&1 || {
    echo "FAIL: Cannot connect to database"
    exit 1
}
echo "✓ Connection OK"

# 2. Check migrations
echo "Checking migrations..."
PENDING=$(psql "$DB_URL" -t -c "SELECT COUNT(*) FROM alembic_version" 2>/dev/null)
if [ -z "$PENDING" ]; then
    echo "WARN: No migration tracking found"
fi

# 3. Check required tables
echo "Checking tables..."
TABLES=("users" "orders" "products")
for TABLE in "${TABLES[@]}"; do
    EXISTS=$(psql "$DB_URL" -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '$TABLE')")
    if [[ "$EXISTS" == *"t"* ]]; then
        echo "✓ Table '$TABLE' exists"
    else
        echo "FAIL: Table '$TABLE' missing"
        exit 1
    fi
done

echo "=== All checks passed ==="
exit 0
```

### SQLite

```bash
#!/bin/bash
# scripts/verify-sqlite.sh

DB_PATH="${SQLITE_PATH:-./data.db}"

echo "=== SQLite Verification ==="

# 1. File exists
if [ ! -f "$DB_PATH" ]; then
    echo "FAIL: Database file not found: $DB_PATH"
    exit 1
fi
echo "✓ Database file exists"

# 2. Check tables
echo "Checking tables..."
TABLES=$(sqlite3 "$DB_PATH" ".tables")
echo "Tables: $TABLES"

# 3. Check required tables
REQUIRED=("users" "orders")
for TABLE in "${REQUIRED[@]}"; do
    if echo "$TABLES" | grep -q "$TABLE"; then
        echo "✓ Table '$TABLE' exists"
    else
        echo "FAIL: Table '$TABLE' missing"
        exit 1
    fi
done

echo "=== All checks passed ==="
exit 0
```

### MongoDB

```python
#!/usr/bin/env python3
# scripts/verify-mongodb.py
import os
import sys
from pymongo import MongoClient

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/testdb")

def verify_mongodb():
    print("=== MongoDB Verification ===")

    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client.get_database()

        # 1. Connection test
        client.admin.command('ping')
        print("✓ Connection OK")

        # 2. Check collections
        collections = db.list_collection_names()
        print(f"Collections: {collections}")

        # 3. Check required collections
        required = ["users", "orders"]
        for coll in required:
            if coll in collections:
                count = db[coll].count_documents({})
                print(f"✓ Collection '{coll}' exists ({count} documents)")
            else:
                print(f"FAIL: Collection '{coll}' missing")
                return False

        # 4. Check indexes
        for coll in required:
            indexes = list(db[coll].list_indexes())
            print(f"  Indexes on {coll}: {[i['name'] for i in indexes]}")

        print("=== All checks passed ===")
        return True

    except Exception as e:
        print(f"FAIL: {e}")
        return False

if __name__ == "__main__":
    success = verify_mongodb()
    sys.exit(0 if success else 1)
```

## Data Verification Patterns

### Row Existence Check

```python
def verify_user_created(user_id: str) -> bool:
    """Verify user was created in database"""
    result = db.execute(
        "SELECT id, email, created_at FROM users WHERE id = %s",
        (user_id,)
    )
    row = result.fetchone()

    if row is None:
        print(f"FAIL: User {user_id} not found")
        return False

    print(f"✓ User {user_id} exists")
    return True
```

### Constraint Verification

```python
def verify_unique_email():
    """Verify email uniqueness constraint works"""
    try:
        db.execute(
            "INSERT INTO users (email, name) VALUES (%s, %s)",
            ("test@example.com", "First")
        )
        db.execute(
            "INSERT INTO users (email, name) VALUES (%s, %s)",
            ("test@example.com", "Second")  # Should fail
        )
        print("FAIL: Duplicate email was allowed")
        return False
    except IntegrityError:
        print("✓ Unique constraint enforced")
        return True
```

### Cascade Delete Verification

```python
def verify_cascade_delete():
    """Verify cascading deletes work"""
    # Create user with orders
    user_id = create_user(email="test@example.com")
    order_id = create_order(user_id=user_id)

    # Delete user
    db.execute("DELETE FROM users WHERE id = %s", (user_id,))

    # Verify order also deleted
    result = db.execute(
        "SELECT id FROM orders WHERE id = %s", (order_id,)
    )

    if result.fetchone() is None:
        print("✓ Cascade delete worked")
        return True
    else:
        print("FAIL: Order still exists after user deleted")
        return False
```

## Migration Verification

```bash
#!/bin/bash
# scripts/verify-migrations.sh

echo "=== Migration Verification ==="

# Check for pending migrations
if command -v alembic &> /dev/null; then
    PENDING=$(alembic check 2>&1)
    if echo "$PENDING" | grep -q "No new upgrade"; then
        echo "✓ All migrations applied"
    else
        echo "FAIL: Pending migrations"
        echo "$PENDING"
        exit 1
    fi
fi

# Verify migration can rollback
echo "Testing rollback..."
alembic downgrade -1
alembic upgrade head
echo "✓ Rollback test passed"

exit 0
```

## Test Data Management

### Fixtures

```python
# tests/fixtures/users.py
import pytest

@pytest.fixture
def sample_users(db):
    """Create sample users for testing"""
    users = [
        {"email": "user1@example.com", "name": "User One"},
        {"email": "user2@example.com", "name": "User Two"},
    ]

    created = []
    for user in users:
        result = db.execute(
            "INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id",
            (user["email"], user["name"])
        )
        created.append(result.fetchone()[0])

    yield created

    # Cleanup
    for user_id in created:
        db.execute("DELETE FROM users WHERE id = %s", (user_id,))
```

### Reset Script

```bash
#!/bin/bash
# scripts/reset-test-db.sh

echo "=== Resetting Test Database ==="

# Drop and recreate
psql -c "DROP DATABASE IF EXISTS testdb"
psql -c "CREATE DATABASE testdb"

# Run migrations
alembic upgrade head

# Seed data
python scripts/seed_test_data.py

echo "✓ Test database reset"
```

## Evidence Collection

```python
# scripts/collect-db-evidence.py
import json
import os

EVIDENCE_DIR = "/tmp/test-evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def collect_db_evidence():
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "database": os.environ.get("DATABASE_URL", "unknown"),
        "checks": []
    }

    # Run verification
    checks = [
        ("connection", verify_connection()),
        ("migrations", verify_migrations()),
        ("tables", verify_tables()),
        ("constraints", verify_constraints())
    ]

    all_passed = True
    for name, passed in checks:
        evidence["checks"].append({
            "name": name,
            "passed": passed
        })
        if not passed:
            all_passed = False

    evidence["passed"] = all_passed

    with open(f"{EVIDENCE_DIR}/database-tests.json", "w") as f:
        json.dump(evidence, f, indent=2)

    return all_passed
```
