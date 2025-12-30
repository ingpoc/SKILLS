#!/bin/bash
# Detect project type from file markers
# Usage: ./detect-project.sh [path]
# Returns: JSON with project_type, framework, language

set -e

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR"

# Default values
PROJECT_TYPE="unknown"
FRAMEWORK="none"
LANGUAGE="unknown"
PACKAGE_MANAGER="none"
TEST_COMMAND=""
DEV_COMMAND=""
PORT=""

# ─────────────────────────────────────────────────────────────────
# Detect by file markers
# ─────────────────────────────────────────────────────────────────

# Python projects
if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ] || [ -f "setup.py" ]; then
    LANGUAGE="python"
    PACKAGE_MANAGER="pip"
    TEST_COMMAND="pytest -q --tb=short"

    # Check for specific frameworks
    if grep -q "fastapi" pyproject.toml requirements.txt 2>/dev/null; then
        FRAMEWORK="fastapi"
        PROJECT_TYPE="api"
        DEV_COMMAND="uvicorn main:app --reload"
        PORT="8000"
    elif grep -q "django" pyproject.toml requirements.txt 2>/dev/null; then
        FRAMEWORK="django"
        PROJECT_TYPE="web"
        DEV_COMMAND="python manage.py runserver"
        PORT="8000"
    elif grep -q "flask" pyproject.toml requirements.txt 2>/dev/null; then
        FRAMEWORK="flask"
        PROJECT_TYPE="web"
        DEV_COMMAND="flask run"
        PORT="5000"
    elif grep -q "streamlit" pyproject.toml requirements.txt 2>/dev/null; then
        FRAMEWORK="streamlit"
        PROJECT_TYPE="app"
        DEV_COMMAND="streamlit run app.py"
        PORT="8501"
    else
        PROJECT_TYPE="library"
    fi

    # Check for poetry
    if [ -f "poetry.lock" ]; then
        PACKAGE_MANAGER="poetry"
    fi

# Node.js projects
elif [ -f "package.json" ]; then
    LANGUAGE="javascript"
    PACKAGE_MANAGER="npm"

    # Check for TypeScript
    if [ -f "tsconfig.json" ]; then
        LANGUAGE="typescript"
    fi

    # Check for yarn/pnpm
    if [ -f "yarn.lock" ]; then
        PACKAGE_MANAGER="yarn"
    elif [ -f "pnpm-lock.yaml" ]; then
        PACKAGE_MANAGER="pnpm"
    fi

    # Parse package.json for framework detection
    if grep -q '"next"' package.json; then
        FRAMEWORK="nextjs"
        PROJECT_TYPE="web"
        DEV_COMMAND="npm run dev"
        TEST_COMMAND="npm test"
        PORT="3000"
    elif grep -q '"react"' package.json && grep -q '"vite"' package.json; then
        FRAMEWORK="vite-react"
        PROJECT_TYPE="web"
        DEV_COMMAND="npm run dev"
        TEST_COMMAND="npm test"
        PORT="5173"
    elif grep -q '"express"' package.json; then
        FRAMEWORK="express"
        PROJECT_TYPE="api"
        DEV_COMMAND="npm run dev"
        TEST_COMMAND="npm test"
        PORT="3000"
    else
        PROJECT_TYPE="library"
        TEST_COMMAND="npm test"
    fi

# Rust projects
elif [ -f "Cargo.toml" ]; then
    LANGUAGE="rust"
    PACKAGE_MANAGER="cargo"
    PROJECT_TYPE="library"
    TEST_COMMAND="cargo test"

# Go projects
elif [ -f "go.mod" ]; then
    LANGUAGE="go"
    PACKAGE_MANAGER="go"
    PROJECT_TYPE="library"
    TEST_COMMAND="go test ./..."
    DEV_COMMAND="go run ."
fi

# ─────────────────────────────────────────────────────────────────
# Detect entry points
# ─────────────────────────────────────────────────────────────────

ENTRY_POINTS=()
[ -f "main.py" ] && ENTRY_POINTS+=("main.py")
[ -f "app.py" ] && ENTRY_POINTS+=("app.py")
[ -f "manage.py" ] && ENTRY_POINTS+=("manage.py")
[ -f "index.js" ] && ENTRY_POINTS+=("index.js")
[ -f "index.ts" ] && ENTRY_POINTS+=("index.ts")
[ -f "src/index.ts" ] && ENTRY_POINTS+=("src/index.ts")

ENTRY_JSON=$(printf '%s\n' "${ENTRY_POINTS[@]}" | jq -R . | jq -s .)

# ─────────────────────────────────────────────────────────────────
# Output JSON
# ─────────────────────────────────────────────────────────────────

cat << EOF
{
  "project_type": "$PROJECT_TYPE",
  "framework": "$FRAMEWORK",
  "language": "$LANGUAGE",
  "package_manager": "$PACKAGE_MANAGER",
  "test_command": "$TEST_COMMAND",
  "dev_command": "$DEV_COMMAND",
  "dev_port": ${PORT:-null},
  "entry_points": $ENTRY_JSON
}
EOF
