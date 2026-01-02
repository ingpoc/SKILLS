#!/bin/bash
# Initialize .claude/ structure for a new project
# Usage: init-project.sh [project-dir]
# Creates: project.json, state.json, CLAUDE.md (project), .claude/CLAUDE.md (quick ref)

set -e

PROJECT_DIR="${1:-$PWD}"
cd "$PROJECT_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../templates"

echo "=== Initializing Project: $PROJECT_DIR ==="

# ─────────────────────────────────────────────────────────────────
# Create directory structure
# ─────────────────────────────────────────────────────────────────
mkdir -p .claude/config
mkdir -p .claude/progress

# ─────────────────────────────────────────────────────────────────
# Auto-detect project type
# ─────────────────────────────────────────────────────────────────
detect_project() {
    # Check for plan files first (highest priority)
    PLAN_FILE=$(find ~/.claude/plans -name "*.md" -type f 2>/dev/null | head -1)
    if [ -n "$PLAN_FILE" ] && [ -f "$PLAN_FILE" ]; then
        # Detect from plan file content
        if grep -qi "next.js\|nextjs" "$PLAN_FILE" 2>/dev/null; then
            if grep -qi "solana\|anchor" "$PLAN_FILE" 2>/dev/null; then
                echo "fullstack"  # Next.js + Solana
                return
            fi
            echo "nextjs"
            return
        elif grep -qi "fastapi" "$PLAN_FILE" 2>/dev/null; then
            echo "fastapi"
            return
        elif grep -qi "claude.*agent.*sdk\|agent-sdk" "$PLAN_FILE" 2>/dev/null; then
            echo "agent-sdk"
            return
        fi
    fi

    # Fallback to file-based detection
    if [ -f "Cargo.toml" ]; then
        if grep -q "anchor" Cargo.toml 2>/dev/null; then
            echo "solana"
        else
            echo "rust"
        fi
    elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
        if grep -q "fastapi" pyproject.toml requirements.txt 2>/dev/null; then
            echo "fastapi"
        elif grep -q "django" pyproject.toml requirements.txt 2>/dev/null; then
            echo "django"
        elif grep -q "flask" pyproject.toml requirements.txt 2>/dev/null; then
            echo "flask"
        elif grep -q "textual" pyproject.toml requirements.txt 2>/dev/null; then
            echo "python-tui"
        else
            echo "python"
        fi
    elif [ -f "package.json" ]; then
        if grep -q '"next"' package.json 2>/dev/null; then
            echo "nextjs"
        elif grep -q '"express"' package.json 2>/dev/null; then
            echo "express"
        elif grep -q '"react"' package.json 2>/dev/null; then
            echo "react"
        else
            echo "node"
        fi
    elif [ -f "go.mod" ]; then
        echo "go"
    else
        echo "unknown"
    fi
}

PROJECT_TYPE=$(detect_project)
echo "Detected: $PROJECT_TYPE"

# Get project name from directory
PROJECT_NAME=$(basename "$PWD")

# ─────────────────────────────────────────────────────────────────
# Set defaults based on project type
# ─────────────────────────────────────────────────────────────────
case "$PROJECT_TYPE" in
    fastapi)
        PORT=8000
        TEST_CMD="pytest -q --tb=short"
        HEALTH_CHECK="curl -sf http://localhost:8000/health"
        FRAMEWORK="fastapi"
        LANGUAGE="Python"
        ;;
    django)
        PORT=8000
        TEST_CMD="python manage.py test"
        HEALTH_CHECK="curl -sf http://localhost:8000/"
        FRAMEWORK="django"
        LANGUAGE="Python"
        ;;
    flask)
        PORT=5000
        TEST_CMD="pytest -q --tb=short"
        HEALTH_CHECK="curl -sf http://localhost:5000/"
        FRAMEWORK="flask"
        LANGUAGE="Python"
        ;;
    python-tui)
        PORT=8000
        TEST_CMD="pytest -q --tb=short"
        HEALTH_CHECK=""
        FRAMEWORK="textual"
        LANGUAGE="Python"
        ;;
    python)
        PORT=8000
        TEST_CMD="pytest -q --tb=short"
        HEALTH_CHECK=""
        FRAMEWORK="standard"
        LANGUAGE="Python"
        ;;
    nextjs)
        PORT=3000
        TEST_CMD="npm test"
        HEALTH_CHECK="curl -sf http://localhost:3000/"
        FRAMEWORK="nextjs"
        LANGUAGE="TypeScript"
        ;;
    react)
        PORT=3000
        TEST_CMD="npm test"
        HEALTH_CHECK="curl -sf http://localhost:3000/"
        FRAMEWORK="react"
        LANGUAGE="TypeScript"
        ;;
    express|node)
        PORT=3000
        TEST_CMD="npm test"
        HEALTH_CHECK="curl -sf http://localhost:3000/health"
        FRAMEWORK="express"
        LANGUAGE="JavaScript"
        ;;
    rust)
        PORT=8080
        TEST_CMD="cargo test"
        HEALTH_CHECK="curl -sf http://localhost:8080/health"
        FRAMEWORK="standard"
        LANGUAGE="Rust"
        ;;
    solana)
        PORT=8899
        TEST_CMD="anchor test"
        HEALTH_CHECK=""
        FRAMEWORK="anchor"
        LANGUAGE="Rust"
        ;;
    go)
        PORT=8080
        TEST_CMD="go test ./..."
        HEALTH_CHECK="curl -sf http://localhost:8080/health"
        FRAMEWORK="standard"
        LANGUAGE="Go"
        ;;
    fullstack)
        PORT=3000
        TEST_CMD="npm test"
        HEALTH_CHECK="curl -sf http://localhost:3000/api/health"
        FRAMEWORK="nextjs+solana"
        LANGUAGE="TypeScript"
        ;;
    agent-sdk)
        PORT=8000
        TEST_CMD="pytest -q --tb=short"
        HEALTH_CHECK=""
        FRAMEWORK="claude-agent-sdk"
        LANGUAGE="Python"
        ;;
    *)
        PORT=3000
        TEST_CMD="echo 'No test command configured'"
        HEALTH_CHECK=""
        FRAMEWORK="unknown"
        LANGUAGE="Unknown"
        ;;
esac

# ─────────────────────────────────────────────────────────────────
# Create project.json
# ─────────────────────────────────────────────────────────────────
if [ ! -f ".claude/config/project.json" ]; then
    cat > .claude/config/project.json << EOF
{
  "project_type": "$PROJECT_TYPE",
  "dev_server_port": $PORT,
  "test_command": "$TEST_CMD",
  "health_check": "$HEALTH_CHECK",
  "init_script": "./scripts/init.sh",
  "required_env": [],
  "required_services": []
}
EOF
    echo "Created: .claude/config/project.json"
else
    echo "Exists: .claude/config/project.json"
fi

# ─────────────────────────────────────────────────────────────────
# Create state.json
# ─────────────────────────────────────────────────────────────────
if [ ! -f ".claude/progress/state.json" ]; then
    cat > .claude/progress/state.json << EOF
{
  "state": "START",
  "entered_at": "$(date -Iseconds)",
  "health_status": "UNKNOWN",
  "history": []
}
EOF
    echo "Created: .claude/progress/state.json"
else
    echo "Exists: .claude/progress/state.json"
fi

# ─────────────────────────────────────────────────────────────────
# Generate .claude/CLAUDE.md (Quick Reference, <50 lines)
# ─────────────────────────────────────────────────────────────────
if [ ! -f ".claude/CLAUDE.md" ]; then
    LOCAL_TEMPLATE="$TEMPLATE_DIR/CLAUDE.local.template.md"

    if [ -f "$LOCAL_TEMPLATE" ]; then
        # Generate quick reference with project-specific values
        sed -e "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" \
            -e "s|{{PROJECT_PURPOSE_ONE_LINER}}|$PROJECT_NAME project|g" \
            "$LOCAL_TEMPLATE" > .claude/CLAUDE.md

        # Remove placeholder (use perl for cross-platform, fallback to sed)
        if command -v perl &>/dev/null; then
            perl -i -pe 's/\{\{ADDITIONAL_COMMANDS\}\}//' .claude/CLAUDE.md
        else
            # macOS sed requires '' after -i, GNU sed doesn't
            sed -i'' -e 's|{{ADDITIONAL_COMMANDS}}||' .claude/CLAUDE.md 2>/dev/null || \
                sed -i -e 's|{{ADDITIONAL_COMMANDS}}||' .claude/CLAUDE.md
        fi

        echo "Created: .claude/CLAUDE.md (quick reference)"
    else
        echo "Warning: Local template not found"
    fi
else
    echo "Exists: .claude/CLAUDE.md"
fi

# ─────────────────────────────────────────────────────────────────
# Generate CLAUDE.md (Project Root, 100-300 lines)
# ─────────────────────────────────────────────────────────────────
if [ ! -f "CLAUDE.md" ]; then
    PROJECT_TEMPLATE="$TEMPLATE_DIR/CLAUDE.project.template.md"

    # Read framework template if exists
    FRAMEWORK_SPEC=""
    FRAMEWORK_FILE="$TEMPLATE_DIR/framework-templates/$(echo $LANGUAGE | tr '[:upper:]' '[:lower:]').md"
    if [ -f "$FRAMEWORK_FILE" ]; then
        FRAMEWORK_SPEC=$(cat "$FRAMEWORK_FILE")
    fi

    # Generate project CLAUDE.md
    cat > CLAUDE.md << EOF
---
name: project
description: $PROJECT_NAME - $PROJECT_TYPE project
keywords: $PROJECT_TYPE, $FRAMEWORK, claude
project_type: $PROJECT_TYPE
framework: $FRAMEWORK
---

# $PROJECT_NAME

**Purpose**: $PROJECT_TYPE project built with $FRAMEWORK.

---

## Project Overview

| Aspect | Details |
|--------|---------|
| **Type** | $PROJECT_TYPE |
| **Framework** | $FRAMEWORK |
| **Language** | $LANGUAGE |

---

## Architecture

### Tech Stack

| Layer | Technology |
|-------|------------|
| Language | $LANGUAGE |
| Framework | $FRAMEWORK |
| Package Manager | $(case $LANGUAGE in Python) echo "pip";; Node|JavaScript) echo "npm";; Rust) echo "cargo";; Go) echo "go modules";; *) echo "unknown";; esac) |

### Project Structure

| Directory | Purpose |
|-----------|---------|
| \`.claude/\` | Agent Harness configuration |
| \`.claude/config/\` | Project settings |
| \`.claude/progress/\` | State tracking |
EOF

    # Add framework-specific content
    if [ -n "$FRAMEWORK_SPEC" ]; then
        echo "" >> CLAUDE.md
        echo "$FRAMEWORK_SPEC" >> CLAUDE.md
    fi

    # Add common sections
    cat >> CLAUDE.md << 'COMMON_EOF'

---

## Common Commands

| Task | Command |
|------|---------|
| Check state | `~/.claude/skills/orchestrator/scripts/check-state.sh` |
| Run tests | `~/.claude/skills/testing/scripts/run-unit-tests.sh` |
| Health check | `~/.claude/skills/implementation/scripts/health-check.sh` |
| Session entry | `~/.claude/skills/orchestrator/scripts/session-entry.sh` |

---

## Config Files

| File | Purpose |
|------|---------|
| `.claude/config/project.json` | Project settings (auto-detected) |
| `.claude/progress/state.json` | Current state |
| `.claude/progress/feature-list.json` | Features |

---

## MCP Servers

### token-efficient MCP

**Use for**: Data processing >50 items, CSV/logs, sandbox execution

| Tool | Use For | Savings |
|------|---------|---------|
| `execute_code` | Python/Bash/Node in sandbox | 98%+ |
| `process_csv` | CSV with filters | 99% |
| `process_logs` | Log pattern matching | 95% |

### context-graph MCP

**Use for**: Decision traces, semantic search, learning loops

| Tool | Purpose |
|------|---------|
| `context_store_trace` | Store decision with category + outcome |
| `context_query_traces` | Semantic search for similar decisions |
| `context_update_outcome` | Mark success/failure |
COMMON_EOF

    echo "Created: CLAUDE.md (project documentation)"
else
    echo "Exists: CLAUDE.md"
fi

# ─────────────────────────────────────────────────────────────────
# Transition state to INIT
# ─────────────────────────────────────────────────────────────────
if [ -f ".claude/progress/state.json" ]; then
    CURRENT_STATE=$(jq -r '.state' .claude/progress/state.json 2>/dev/null || echo "START")
    if [ "$CURRENT_STATE" = "START" ]; then
        TIMESTAMP=$(date -Iseconds)
        jq --arg ts "$TIMESTAMP" '.state = "INIT" | .entered_at = $ts | .history += [{"from": "START", "to": "INIT", "at": $ts, "reason": "init-project.sh complete"}]' \
            .claude/progress/state.json > .claude/progress/state.json.tmp && \
            mv .claude/progress/state.json.tmp .claude/progress/state.json
        echo "State: START → INIT"
    fi
fi

# ─────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────
echo ""
echo "=== Project Initialized ==="
echo ""
echo "Created:"
echo "  CLAUDE.md                    - Project documentation"
echo "  .claude/CLAUDE.md             - Quick reference"
echo "  .claude/config/project.json  - Project settings"
echo "  .claude/progress/state.json  - Current state (INIT)"
echo ""
echo "Project: $PROJECT_NAME ($PROJECT_TYPE with $FRAMEWORK)"
echo ""
echo "Next: Run session-entry.sh to begin"
