#!/bin/bash
# Initialize .claude/ structure for a new project
# Usage: init-project.sh [project-dir]
# Creates: project.json, state.json, CLAUDE.md (project), .claude/CLAUDE.md (quick ref), .claude/scripts/

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
    # File-based detection first (highest priority — actual project files)
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
        # Fallback: check plan files only when no project files detected
        PLAN_FILE=$(find ~/.claude/plans -name "*.md" -type f 2>/dev/null | head -1)
        if [ -n "$PLAN_FILE" ] && [ -f "$PLAN_FILE" ]; then
            if grep -qi "next.js\|nextjs" "$PLAN_FILE" 2>/dev/null; then
                if grep -qi "solana\|anchor" "$PLAN_FILE" 2>/dev/null; then
                    echo "fullstack"
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
        if [ -f "tsconfig.json" ]; then
            LANGUAGE="TypeScript"
        else
            LANGUAGE="JavaScript"
        fi
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
    # Compute package manager for project.json
    case "$LANGUAGE" in
        Python) PKG_MGR_JSON="pip" ;;
        JavaScript|TypeScript) PKG_MGR_JSON="npm" ;;
        Rust) PKG_MGR_JSON="cargo" ;;
        Go) PKG_MGR_JSON="go" ;;
        *) PKG_MGR_JSON="unknown" ;;
    esac

    cat > .claude/config/project.json << EOF
{
  "project_type": "$PROJECT_TYPE",
  "framework": "$FRAMEWORK",
  "language": "$LANGUAGE",
  "package_manager": "$PKG_MGR_JSON",
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
# Copy automation scripts to .claude/scripts/
# ─────────────────────────────────────────────────────────────────
mkdir -p .claude/scripts
SCRIPTS_COPIED=0

# Copy SCRIPTS_README.md as README.md
IMPL_TEMPLATES="$HOME/.claude/skills/implementation/templates"
if [ -f "$IMPL_TEMPLATES/SCRIPTS_README.md" ] && [ ! -f ".claude/scripts/README.md" ]; then
    cp "$IMPL_TEMPLATES/SCRIPTS_README.md" .claude/scripts/README.md
    echo "Created: .claude/scripts/README.md"
    SCRIPTS_COPIED=$((SCRIPTS_COPIED + 1))
fi

# Copy implementation script templates
for template_file in get-current-feature.sh health-check.sh feature-commit.sh mark-feature-complete.sh; do
    example_file="$IMPL_TEMPLATES/${template_file}.example"
    target_file=".claude/scripts/${template_file}"

    if [ -f "$example_file" ] && [ ! -f "$target_file" ]; then
        cp "$example_file" "$target_file"
        chmod +x "$target_file"
        echo "Created: .claude/scripts/${template_file}"
        SCRIPTS_COPIED=$((SCRIPTS_COPIED + 1))
    fi
done

# Copy orchestrator scripts
ORCH_SCRIPTS="$HOME/.claude/skills/orchestrator/scripts"
for orch_script in check-state.sh validate-transition.sh check-context.sh; do
    if [ -f "$ORCH_SCRIPTS/${orch_script}" ] && [ ! -f ".claude/scripts/${orch_script}" ]; then
        cp "$ORCH_SCRIPTS/${orch_script}" ".claude/scripts/${orch_script}"
        chmod +x ".claude/scripts/${orch_script}"
        echo "Created: .claude/scripts/${orch_script}"
        SCRIPTS_COPIED=$((SCRIPTS_COPIED + 1))
    fi
done

if [ $SCRIPTS_COPIED -gt 0 ]; then
    echo ""
    echo "Auto-customizing scripts based on project.json..."
    
    # Get project config values
    PORT=$(jq -r '.dev_server_port // 3000' .claude/config/project.json)
    TEST_CMD=$(jq -r '.test_command // "npm test"' .claude/config/project.json)
    HEALTH=$(jq -r '.health_check // "curl -sf http://localhost:$PORT/health"' .claude/config/project.json)
    LANGUAGE=$(jq -r '.language // "JavaScript"' .claude/config/project.json)
    
    # Auto-customize each TEMPLATE-*.sh script
    for tmpl in .claude/scripts/TEMPLATE-*.sh; do
        if [ -f "$tmpl" ]; then
            base=$(basename "$tmpl" | sed 's/TEMPLATE-//')
            
            # Customize based on project type
            case "$base" in
                health-check.sh)
                    if [ "$LANGUAGE" = "Python" ]; then
                        sed -e "s|__PORT__|$PORT|g" \
                            -e "s|__HEALTH__|$HEALTH|g" \
                            -e "s|FRONTEND_PORT=3000|BACKEND_PORT=$PORT|g" \
                            -e "s|uvicorn|python -m uvicorn|g" \
                            -e "s|next dev||g" \
                            "$tmpl" > ".claude/scripts/$base"
                    else
                        cp "$tmpl" ".claude/scripts/$base"
                    fi
                    ;;
                restart-servers.sh)
                    if [ "$LANGUAGE" = "Python" ]; then
                        sed -e "s|__PORT__|$PORT|g" \
                            -e "s|npm run dev|python -m uvicorn src.main:app --reload|g" \
                            -e "s|next dev||g" \
                            -e "s|FRONTEND_PORT=3000|BACKEND_PORT=$PORT|g" \
                            "$tmpl" > ".claude/scripts/$base"
                    else
                        cp "$tmpl" ".claude/scripts/$base"
                    fi
                    ;;
                run-tests.sh)
                    if [ "$LANGUAGE" = "Python" ]; then
                        sed -e "s|__TEST_CMD__|PYTHONPATH=. pytest|g" \
                            -e "s|__PORT__|$PORT|g" \
                            -e "s|npm test|pytest|g" \
                            "$tmpl" > ".claude/scripts/$base"
                    else
                        cp "$tmpl" ".claude/scripts/$base"
                    fi
                    ;;
                *)
                    cp "$tmpl" ".claude/scripts/$base"
                    ;;
            esac
            
            chmod +x ".claude/scripts/$base"
            rm "$tmpl"
            echo "  ✓ Auto-customized: $base"
        fi
    done
    echo "✅ Scripts auto-customized"
fi

# ─────────────────────────────────────────────────────────────────
# Copy MCP config from workspace (if exists)
# ─────────────────────────────────────────────────────────────────
if [ ! -f ".mcp.json" ]; then
    if [ -f "$HOME/.jarvis/workspaces/.mcp.json" ]; then
        cp "$HOME/.jarvis/workspaces/.mcp.json" .mcp.json
        echo "Created: .mcp.json (from workspace)"
    elif [ -f "$HOME/.claude/.mcp.json" ]; then
        cp "$HOME/.claude/.mcp.json" .mcp.json
        echo "Created: .mcp.json (from global)"
    fi
fi

# ─────────────────────────────────────────────────────────────────
# Setup MCP servers (if mcp-setup skill exists)
# ─────────────────────────────────────────────────────────────────
if [ -f "$HOME/.claude/skills/mcp-setup/scripts/verify-setup.sh" ]; then
    echo ""
    echo "Verifying MCP configuration..."
    if bash "$HOME/.claude/skills/mcp-setup/scripts/verify-setup.sh" 2>/dev/null; then
        echo "✅ MCP servers configured"
    else
        echo "⚠️ MCP not configured (optional - run ~/.claude/skills/mcp-setup/scripts/setup-all.sh if needed)"
    fi
fi

# ─────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────
if [ ! -f ".mcp.json" ]; then
    if [ -f "$HOME/.jarvis/workspaces/.mcp.json" ]; then
        cp "$HOME/.jarvis/workspaces/.mcp.json" .mcp.json
        echo "Created: .mcp.json (from workspace)"
    elif [ -f "$HOME/.claude/.mcp.json" ]; then
        cp "$HOME/.claude/.mcp.json" .mcp.json
        echo "Created: .mcp.json (from global)"
    fi
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

    # Pre-compute package manager for heredoc
    case "$LANGUAGE" in
        Python) PKG_MGR="pip" ;;
        JavaScript|TypeScript) PKG_MGR="npm" ;;
        Rust) PKG_MGR="cargo" ;;
        Go) PKG_MGR="go modules" ;;
        *) PKG_MGR="unknown" ;;
    esac

    if [ -f "$PROJECT_TEMPLATE" ]; then
        # Copy template
        cp "$PROJECT_TEMPLATE" CLAUDE.md
        
        # Substitute variables
        sed -i'' -e "s|\$PROJECT_NAME|$PROJECT_NAME|g" \
                -e "s|\$PROJECT_TYPE|$PROJECT_TYPE|g" \
                -e "s|\$FRAMEWORK|$FRAMEWORK|g" \
                -e "s|\$LANGUAGE|$LANGUAGE|g" \
                -e "s|\$PKG_MGR|$PKG_MGR|g" \
                CLAUDE.md 2>/dev/null || \
        sed -e "s|\$PROJECT_NAME|$PROJECT_NAME|g" \
                -e "s|\$PROJECT_TYPE|$PROJECT_TYPE|g" \
                -e "s|\$FRAMEWORK|$FRAMEWORK|g" \
                -e "s|\$LANGUAGE|$LANGUAGE|g" \
                -e "s|\$PKG_MGR|$PKG_MGR|g" \
                "$PROJECT_TEMPLATE" > CLAUDE.md
        
        echo "Created: CLAUDE.md (project documentation)"
    else
        echo "Warning: Template not found at $PROJECT_TEMPLATE"
    fi
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
echo "  CLAUDE.md                      - Project documentation"
echo "  .claude/CLAUDE.md               - Quick reference"
echo "  .claude/config/project.json    - Project settings"
echo "  .claude/progress/state.json    - Current state (INIT)"
echo "  .claude/scripts/               - Automation scripts"
echo "  .claude/scripts/README.md      - Script documentation"
if [ $SCRIPTS_COPIED -gt 0 ]; then
    echo ""
    echo "Automation scripts copied to .claude/scripts/:"
    echo "  - get-current-feature.sh"
    echo "  - health-check.sh"
    echo "  - feature-commit.sh"
    echo "  - mark-feature-complete.sh"
    echo "  - check-state.sh"
    echo "  - validate-transition.sh"
    echo "  - check-context.sh"
fi
echo ""
echo "Project: $PROJECT_NAME ($PROJECT_TYPE with $FRAMEWORK)"
echo ""
echo "Next steps:"
echo "  1. Review .claude/scripts/README.md"
echo "  2. Customize scripts for your project"
echo "  3. Run session-entry.sh to begin"
