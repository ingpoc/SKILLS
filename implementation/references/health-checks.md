# Health Check Patterns

## Purpose

Verify system is operational before transitioning to TEST state. Health checks are **code-verified**, not LLM-judged.

## Health Check Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    HEALTH CHECK SEQUENCE                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. PROCESS CHECK                                            │
│     └── Is server/app running?                              │
│                                                              │
│  2. ENDPOINT CHECK                                           │
│     └── Does /health return 200?                            │
│                                                              │
│  3. DEPENDENCY CHECK                                         │
│     └── Is database connected?                              │
│                                                              │
│  4. LINT CHECK                                               │
│     └── No syntax/type errors?                              │
│                                                              │
│  5. BUILD CHECK                                              │
│     └── Does it compile/bundle?                             │
│                                                              │
│  ALL PASS → Ready for TEST state                            │
│  ANY FAIL → Fix before proceeding                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Project-Specific Checks

### Python (FastAPI)

```bash
#!/bin/bash
# scripts/health-check-fastapi.sh

set -e

echo "=== FastAPI Health Check ==="

# 1. Lint check
echo "Checking lint..."
ruff check . --quiet || { echo "FAIL: Lint errors"; exit 1; }

# 2. Type check (if using mypy)
if [ -f "pyproject.toml" ] && grep -q "mypy" pyproject.toml; then
    echo "Checking types..."
    mypy . --quiet || { echo "FAIL: Type errors"; exit 1; }
fi

# 3. Start server (background)
echo "Starting server..."
uvicorn main:app --port 8000 &
SERVER_PID=$!
sleep 3

# 4. Health endpoint
echo "Checking /health..."
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HEALTH" != "200" ]; then
    kill $SERVER_PID 2>/dev/null
    echo "FAIL: Health endpoint returned $HEALTH"
    exit 1
fi

# 5. Cleanup
kill $SERVER_PID 2>/dev/null

echo "=== All checks passed ==="
exit 0
```

### Python (Django)

```bash
#!/bin/bash
# scripts/health-check-django.sh

set -e

echo "=== Django Health Check ==="

# 1. Check migrations
echo "Checking migrations..."
python manage.py migrate --check || { echo "FAIL: Unapplied migrations"; exit 1; }

# 2. System check
echo "Running system check..."
python manage.py check || { echo "FAIL: System check failed"; exit 1; }

# 3. Collect static (dry run)
echo "Checking static files..."
python manage.py collectstatic --dry-run --noinput || { echo "FAIL: Static collection"; exit 1; }

echo "=== All checks passed ==="
exit 0
```

### Node.js (Next.js)

```bash
#!/bin/bash
# scripts/health-check-nextjs.sh

set -e

echo "=== Next.js Health Check ==="

# 1. Type check
echo "Checking types..."
npx tsc --noEmit || { echo "FAIL: Type errors"; exit 1; }

# 2. Lint
echo "Checking lint..."
npm run lint --quiet || { echo "FAIL: Lint errors"; exit 1; }

# 3. Build
echo "Building..."
npm run build || { echo "FAIL: Build failed"; exit 1; }

echo "=== All checks passed ==="
exit 0
```

### Node.js (Express)

```bash
#!/bin/bash
# scripts/health-check-express.sh

set -e

echo "=== Express Health Check ==="

# 1. Lint
echo "Checking lint..."
npm run lint --quiet || { echo "FAIL: Lint errors"; exit 1; }

# 2. Start server
echo "Starting server..."
npm start &
SERVER_PID=$!
sleep 3

# 3. Health check
echo "Checking /health..."
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/health)
if [ "$HEALTH" != "200" ]; then
    kill $SERVER_PID 2>/dev/null
    echo "FAIL: Health endpoint returned $HEALTH"
    exit 1
fi

# 4. Cleanup
kill $SERVER_PID 2>/dev/null

echo "=== All checks passed ==="
exit 0
```

## Database Connectivity Check

```python
# scripts/check-db.py
import sys
import os

def check_postgres():
    import psycopg2
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()
        cur.execute("SELECT 1")
        conn.close()
        return True
    except Exception as e:
        print(f"FAIL: Database connection: {e}")
        return False

def check_mongodb():
    from pymongo import MongoClient
    try:
        client = MongoClient(os.environ["MONGODB_URI"], serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        return True
    except Exception as e:
        print(f"FAIL: MongoDB connection: {e}")
        return False

def check_redis():
    import redis
    try:
        r = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost"))
        r.ping()
        return True
    except Exception as e:
        print(f"FAIL: Redis connection: {e}")
        return False

if __name__ == "__main__":
    db_type = sys.argv[1] if len(sys.argv) > 1 else "postgres"

    checks = {
        "postgres": check_postgres,
        "mongodb": check_mongodb,
        "redis": check_redis
    }

    if checks.get(db_type, lambda: False)():
        print(f"OK: {db_type} connected")
        sys.exit(0)
    else:
        sys.exit(1)
```

## Health Check JSON Output

```bash
#!/bin/bash
# scripts/health-check-json.sh

OUTPUT='{"checks": ['
PASSED=0
FAILED=0

run_check() {
    NAME=$1
    CMD=$2

    if eval "$CMD" > /dev/null 2>&1; then
        OUTPUT+='{"name": "'$NAME'", "status": "pass"},'
        ((PASSED++))
    else
        OUTPUT+='{"name": "'$NAME'", "status": "fail"},'
        ((FAILED++))
    fi
}

run_check "lint" "ruff check . --quiet"
run_check "types" "mypy . --quiet"
run_check "server" "curl -s localhost:8000/health"
run_check "database" "python scripts/check-db.py"

# Remove trailing comma and close
OUTPUT=${OUTPUT%,}
OUTPUT+='], "passed": '$PASSED', "failed": '$FAILED'}'

echo $OUTPUT

if [ $FAILED -gt 0 ]; then
    exit 1
fi
exit 0
```

## Integration with State Machine

```python
def can_transition_to_test() -> bool:
    """Check if ready to transition to TEST state"""

    # Run health check script
    result = subprocess.run(
        ["bash", "scripts/health-check.sh"],
        capture_output=True
    )

    if result.returncode != 0:
        print(f"Health check failed: {result.stderr.decode()}")
        return False

    # Update state with health check timestamp
    update_state({
        "last_health_check": now(),
        "health_status": "passed"
    })

    return True
```

## Failure Recovery

| Failure | Cause | Fix |
|---------|-------|-----|
| Lint errors | Code style | Run formatter, fix issues |
| Type errors | Wrong types | Fix type annotations |
| Build fails | Syntax/deps | Check imports, install deps |
| Server won't start | Port conflict | Kill existing process |
| DB not connected | Wrong URL | Check env vars |
| Health endpoint 404 | Route missing | Add /health route |
