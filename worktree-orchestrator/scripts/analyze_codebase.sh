#!/usr/bin/env bash
# analyze_codebase.sh - Detect codebase type and recommend agents
# Usage: analyze_codebase.sh [repo-path]
# Output: JSON with detected features and recommended agents

set -eo pipefail

REPO_PATH="${1:-$(git rev-parse --show-toplevel)}"
cd "$REPO_PATH"

# Detection results
DETECTED_FEATURES=()
RECOMMENDED_AGENTS=()
CONFIDENCE_SCORES=()

echo "=== Analyzing Codebase ===" >&2
echo "Path: $REPO_PATH" >&2
echo "" >&2

# Detect Python
if [[ -f "pyproject.toml" ]] || [[ -f "setup.py" ]] || [[ -f "requirements.txt" ]]; then
    DETECTED_FEATURES+=("python")
    echo "✓ Python project detected" >&2

    # Check for Claude Agent SDK
    if grep -q "claude-agent-sdk" pyproject.toml 2>/dev/null || \
       grep -q "claude-agent-sdk" requirements.txt 2>/dev/null; then
        DETECTED_FEATURES+=("claude-sdk")
        RECOMMENDED_AGENTS+=("sdk-verify:agent-sdk-verifier:sdk:high")
        echo "  ✓ Claude Agent SDK detected" >&2
    fi
fi

# Detect TypeScript/JavaScript
if [[ -f "package.json" ]] || [[ -f "tsconfig.json" ]]; then
    DETECTED_FEATURES+=("typescript")
    echo "✓ TypeScript/JavaScript project detected" >&2

    # Check for React
    if grep -q "react" package.json 2>/dev/null; then
        DETECTED_FEATURES+=("react")
        RECOMMENDED_AGENTS+=("review-performance:code-review:performance:high")
        echo "  ✓ React detected" >&2
    fi

    # Check for Next.js
    if grep -q "next" package.json 2>/dev/null; then
        DETECTED_FEATURES+=("nextjs")
        echo "  ✓ Next.js detected" >&2
    fi

    # Check for SDK
    if grep -q "@anthropic-ai/claude-code-sdk" package.json 2>/dev/null; then
        DETECTED_FEATURES+=("claude-sdk-ts")
        RECOMMENDED_AGENTS+=("sdk-verify:agent-sdk-verifier-ts:sdk:high")
        echo "  ✓ Claude Code SDK (TS) detected" >&2
    fi
fi

# Detect Swift (macOS apps)
if [[ -f "Package.swift" ]] || ls *.xcodeproj 2>/dev/null | head -1 | grep -q .; then
    DETECTED_FEATURES+=("swift")
    RECOMMENDED_AGENTS+=("review-performance:code-review:performance:medium")
    echo "✓ Swift/macOS project detected" >&2
fi

# Detect Go
if [[ -f "go.mod" ]]; then
    DETECTED_FEATURES+=("go")
    echo "✓ Go project detected" >&2
fi

# Detect Rust
if [[ -f "Cargo.toml" ]]; then
    DETECTED_FEATURES+=("rust")
    echo "✓ Rust project detected" >&2
fi

# Check for tests
if [[ -d "tests" ]] || [[ -d "test" ]] || [[ -d "__tests__" ]] || [[ -d "spec" ]]; then
    DETECTED_FEATURES+=("has-tests")
    RECOMMENDED_AGENTS+=("testing:testing:coverage:high")
    echo "✓ Tests detected" >&2
fi

# Check for API/endpoints
if grep -rq "router\|endpoint\|@app\.(get|post|put|delete)\|FastAPI\|express" src/ 2>/dev/null || \
   grep -rq "router\|endpoint\|@app\.(get|post|put|delete)\|FastAPI\|express" . --include="*.py" --include="*.ts" --include="*.js" 2>/dev/null; then
    DETECTED_FEATURES+=("has-api")
    echo "✓ API endpoints detected" >&2
fi

# Check for authentication code
if grep -rq "auth\|token\|session\|jwt\|oauth" src/ 2>/dev/null || \
   grep -rq "auth\|token\|session\|jwt\|oauth" . --include="*.py" --include="*.ts" --include="*.js" 2>/dev/null | head -5 | grep -q .; then
    DETECTED_FEATURES+=("has-auth")
    echo "✓ Authentication code detected" >&2
fi

# Check for database
if grep -rq "database\|postgres\|mysql\|mongodb\|sqlite\|prisma\|sqlalchemy" . --include="*.py" --include="*.ts" --include="*.js" 2>/dev/null | head -3 | grep -q .; then
    DETECTED_FEATURES+=("has-database")
    echo "✓ Database usage detected" >&2
fi

# Check for MCP servers
if [[ -d "mcp" ]] || grep -rq "mcp\|model.context.protocol" . --include="*.py" --include="*.ts" 2>/dev/null | head -3 | grep -q .; then
    DETECTED_FEATURES+=("has-mcp")
    echo "✓ MCP server code detected" >&2
fi

# Check for documentation
if [[ -d "docs" ]] || ls *.md 2>/dev/null | head -3 | grep -q .; then
    DETECTED_FEATURES+=("has-docs")
    echo "✓ Documentation detected" >&2
fi

# Count source files
PYTHON_FILES=$(find . -name "*.py" -not -path "./.*" -not -path "*/\.*" 2>/dev/null | wc -l | tr -d ' ')
TS_FILES=$(find . -name "*.ts" -not -path "./.*" -not -path "*/\.*" -not -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
SWIFT_FILES=$(find . -name "*.swift" -not -path "./.*" -not -path "*/\.*" 2>/dev/null | wc -l | tr -d ' ')
TOTAL_FILES=$((PYTHON_FILES + TS_FILES + SWIFT_FILES))

echo "" >&2
echo "File counts: Python=$PYTHON_FILES, TS=$TS_FILES, Swift=$SWIFT_FILES" >&2
echo "" >&2

# Determine which agents to always include
# Security review - always include for codebases with API, auth, or database
if [[ " ${DETECTED_FEATURES[*]} " =~ " has-api " ]] || \
   [[ " ${DETECTED_FEATURES[*]} " =~ " has-auth " ]] || \
   [[ " ${DETECTED_FEATURES[*]} " =~ " has-database " ]]; then
    RECOMMENDED_AGENTS+=("review-security:code-review:security:high")
else
    RECOMMENDED_AGENTS+=("review-security:code-review:security:medium")
fi

# Architecture review - include for larger projects
if [[ $TOTAL_FILES -gt 20 ]]; then
    RECOMMENDED_AGENTS+=("architecture:plan:architecture:high")
    echo "✓ Architecture review recommended (project size: $TOTAL_FILES files)" >&2
else
    RECOMMENDED_AGENTS+=("architecture:plan:architecture:low")
    echo "  Architecture review optional (small project: $TOTAL_FILES files)" >&2
fi

# Performance review - include for frontend or high-scale backend
if [[ " ${DETECTED_FEATURES[*]} " =~ " react " ]] || \
   [[ " ${DETECTED_FEATURES[*]} " =~ " nextjs " ]] || \
   [[ $TOTAL_FILES -gt 50 ]]; then
    if [[ -z "${RECOMMENDED_AGENTS[*]}" ]] || ! echo "${RECOMMENDED_AGENTS[*]}" | grep -q "review-performance"; then
        RECOMMENDED_AGENTS+=("review-performance:code-review:performance:high")
    fi
fi

# Output JSON
echo ""
echo "=== Analysis Complete ===" >&2

# Build JSON output
FEATURES_JSON=$(printf '%s\n' "${DETECTED_FEATURES[@]}" | jq -R . | jq -s .)
AGENTS_JSON=$(printf '%s\n' "${RECOMMENDED_AGENTS[@]}" | jq -R . | jq -s .)

jq -n \
    --arg repo "$REPO_PATH" \
    --argjson features "$FEATURES_JSON" \
    --argjson agents "$AGENTS_JSON" \
    --arg total_files "$TOTAL_FILES" \
    '{
        repo: $repo,
        total_files: ($total_files | tonumber),
        features: $features,
        recommended_agents: $agents
    }'
