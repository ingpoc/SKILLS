# API Testing Patterns

## API Test Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    API TEST SEQUENCE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. SETUP                                                    │
│     └── Start server, prepare test data                     │
│                                                              │
│  2. REQUEST                                                  │
│     └── Send HTTP request (GET, POST, PUT, DELETE)          │
│                                                              │
│  3. VALIDATE                                                 │
│     ├── Status code correct                                 │
│     ├── Response body matches schema                        │
│     ├── Headers correct                                     │
│     └── Side effects occurred (DB updated, etc.)            │
│                                                              │
│  4. CLEANUP                                                  │
│     └── Reset test data, stop server                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Testing with curl

### Basic Patterns

```bash
# GET request
curl -s http://localhost:8000/api/users | jq .

# POST with JSON body
curl -s -X POST http://localhost:8000/api/users \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "name": "Test"}' | jq .

# PUT request
curl -s -X PUT http://localhost:8000/api/users/123 \
    -H "Content-Type: application/json" \
    -d '{"name": "Updated"}' | jq .

# DELETE request
curl -s -X DELETE http://localhost:8000/api/users/123

# With authentication
curl -s http://localhost:8000/api/protected \
    -H "Authorization: Bearer $TOKEN" | jq .
```

### Validation with Exit Codes

```bash
#!/bin/bash
# scripts/test-api-endpoint.sh

URL=$1
EXPECTED_STATUS=$2

RESPONSE=$(curl -s -w "\n%{http_code}" "$URL")
BODY=$(echo "$RESPONSE" | head -n -1)
STATUS=$(echo "$RESPONSE" | tail -n 1)

if [ "$STATUS" = "$EXPECTED_STATUS" ]; then
    echo "PASS: $URL returned $STATUS"
    exit 0
else
    echo "FAIL: $URL returned $STATUS (expected $EXPECTED_STATUS)"
    echo "Body: $BODY"
    exit 1
fi
```

## API Test Script

```bash
#!/bin/bash
# scripts/run-api-tests.sh

set -e

BASE_URL="http://localhost:8000"
PASS=0
FAIL=0

test_endpoint() {
    local METHOD=$1
    local ENDPOINT=$2
    local EXPECTED_STATUS=$3
    local DATA=$4

    if [ -n "$DATA" ]; then
        RESPONSE=$(curl -s -w "\n%{http_code}" -X "$METHOD" "$BASE_URL$ENDPOINT" \
            -H "Content-Type: application/json" \
            -d "$DATA")
    else
        RESPONSE=$(curl -s -w "\n%{http_code}" -X "$METHOD" "$BASE_URL$ENDPOINT")
    fi

    STATUS=$(echo "$RESPONSE" | tail -n 1)

    if [ "$STATUS" = "$EXPECTED_STATUS" ]; then
        echo "✓ $METHOD $ENDPOINT → $STATUS"
        ((PASS++))
    else
        echo "✗ $METHOD $ENDPOINT → $STATUS (expected $EXPECTED_STATUS)"
        ((FAIL++))
    fi
}

echo "=== API Tests ==="

# Health check
test_endpoint "GET" "/health" "200"

# List users (empty)
test_endpoint "GET" "/api/users" "200"

# Create user
test_endpoint "POST" "/api/users" "201" '{"email": "test@example.com", "name": "Test"}'

# Get user
test_endpoint "GET" "/api/users/1" "200"

# Update user
test_endpoint "PUT" "/api/users/1" "200" '{"name": "Updated"}'

# Delete user
test_endpoint "DELETE" "/api/users/1" "204"

# Not found
test_endpoint "GET" "/api/users/999" "404"

# Validation error
test_endpoint "POST" "/api/users" "422" '{"email": "invalid"}'

echo ""
echo "Results: $PASS passed, $FAIL failed"

if [ $FAIL -gt 0 ]; then
    exit 1
fi
exit 0
```

## Python API Testing

### Using httpx

```python
# tests/test_api.py
import pytest
from httpx import AsyncClient

@pytest.fixture
async def client():
    from src.main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
class TestUsersAPI:

    async def test_list_users(self, client):
        response = await client.get("/api/users")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_user(self, client):
        response = await client.post("/api/users", json={
            "email": "test@example.com",
            "name": "Test User"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data

    async def test_create_user_validation(self, client):
        response = await client.post("/api/users", json={
            "email": "invalid-email"
        })

        assert response.status_code == 422
        assert "email" in response.text.lower()

    async def test_get_user(self, client):
        # Create first
        create_response = await client.post("/api/users", json={
            "email": "test@example.com",
            "name": "Test"
        })
        user_id = create_response.json()["id"]

        # Get
        response = await client.get(f"/api/users/{user_id}")

        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"

    async def test_get_user_not_found(self, client):
        response = await client.get("/api/users/nonexistent")

        assert response.status_code == 404

    async def test_delete_user(self, client):
        # Create first
        create_response = await client.post("/api/users", json={
            "email": "test@example.com",
            "name": "Test"
        })
        user_id = create_response.json()["id"]

        # Delete
        response = await client.delete(f"/api/users/{user_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = await client.get(f"/api/users/{user_id}")
        assert get_response.status_code == 404
```

## Response Validation

### JSON Schema Validation

```python
from jsonschema import validate

USER_SCHEMA = {
    "type": "object",
    "required": ["id", "email", "name"],
    "properties": {
        "id": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "name": {"type": "string", "minLength": 1}
    }
}

def test_user_response_schema(client):
    response = client.post("/api/users", json={
        "email": "test@example.com",
        "name": "Test"
    })

    validate(response.json(), USER_SCHEMA)  # Raises if invalid
```

### Status Code Reference

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Authenticated but not allowed |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable | Validation errors |
| 500 | Server Error | Unexpected error |

## Evidence Collection

```bash
#!/bin/bash
# scripts/collect-api-evidence.sh

EVIDENCE_DIR="/tmp/test-evidence"
mkdir -p "$EVIDENCE_DIR"

# Run tests and capture output
./scripts/run-api-tests.sh > "$EVIDENCE_DIR/api-tests.log" 2>&1
EXIT_CODE=$?

# Create JSON summary
cat > "$EVIDENCE_DIR/api-tests.json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "exit_code": $EXIT_CODE,
  "passed": $([ $EXIT_CODE -eq 0 ] && echo "true" || echo "false"),
  "log_file": "api-tests.log"
}
EOF

exit $EXIT_CODE
```
