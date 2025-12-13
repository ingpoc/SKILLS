#!/bin/bash
# Two-Agent Harness System Setup Script
# Installs the complete two-agent development architecture
#
# Usage: bash setup-two-agent-system.sh [--force]
#   --force: Overwrite existing files without prompting

set -e

# Configuration
CLAUDE_DIR="$HOME/.claude"
SKILL_DIR="$CLAUDE_DIR/skills/two-agent-harness"
AGENTS_DIR="$CLAUDE_DIR/agents"
HOOKS_DIR="$CLAUDE_DIR/hooks"
REFERENCE_DIR="$CLAUDE_DIR/REFRENCE/TWO-AGENT-HARNESS"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parse arguments
FORCE=false
if [ "$1" = "--force" ]; then
    FORCE=true
fi

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
}

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}→${NC} $1"
}

# Check if file exists and handle accordingly
copy_file() {
    local src="$1"
    local dest="$2"
    local name="$3"

    if [ -f "$dest" ] && [ "$FORCE" != "true" ]; then
        print_warning "$name already exists, skipping (use --force to overwrite)"
    else
        cp "$src" "$dest"
        print_status "Installed $name"
    fi
}

# Main installation
main() {
    print_header "Two-Agent Harness System Setup"
    echo ""
    echo "This script will install:"
    echo "  • 2 agent definitions (initializer-agent, coding-agent)"
    echo "  • 5 enforcement hooks"
    echo "  • 9 reference documentation files"
    echo "  • CLAUDE.md configuration"
    echo ""

    # Verify skill directory exists
    if [ ! -d "$SKILL_DIR" ]; then
        print_error "Skill directory not found: $SKILL_DIR"
        echo "Please ensure the skill is properly installed first."
        exit 1
    fi

    # Step 1: Create directories
    print_header "Step 1: Creating Directories"

    mkdir -p "$AGENTS_DIR"
    print_status "Created $AGENTS_DIR"

    mkdir -p "$HOOKS_DIR"
    print_status "Created $HOOKS_DIR"

    mkdir -p "$REFERENCE_DIR"
    print_status "Created $REFERENCE_DIR"

    # Step 2: Install agents
    print_header "Step 2: Installing Agents"

    copy_file "$SKILL_DIR/assets/agents/initializer-agent.md" "$AGENTS_DIR/initializer-agent.md" "initializer-agent"
    copy_file "$SKILL_DIR/assets/agents/coding-agent.md" "$AGENTS_DIR/coding-agent.md" "coding-agent"

    # Step 3: Install hooks
    print_header "Step 3: Installing Hooks"

    for hook in pre-tool-guard.sh post-tool-guard.sh session-progress-check.sh verify-coding-agent.sh session-end.sh; do
        if [ -f "$SKILL_DIR/assets/hooks/$hook" ]; then
            copy_file "$SKILL_DIR/assets/hooks/$hook" "$HOOKS_DIR/$hook" "$hook"
            chmod +x "$HOOKS_DIR/$hook"
        else
            print_warning "Hook not found: $hook"
        fi
    done

    # Step 4: Configure settings.json with hooks
    print_header "Step 4: Configuring Hook Settings"

    if [ -f "$SETTINGS_FILE" ]; then
        # Check if hooks are already configured
        if grep -q "pre-tool-guard" "$SETTINGS_FILE" 2>/dev/null; then
            print_warning "Hooks already configured in settings.json"
        else
            print_info "Adding hook configurations to settings.json..."
            # Use Python to safely modify JSON
            python3 << 'EOF'
import json
import os

settings_file = os.path.expanduser("~/.claude/settings.json")
hooks_dir = os.path.expanduser("~/.claude/hooks")

try:
    with open(settings_file, 'r') as f:
        settings = json.load(f)
except:
    settings = {}

# Ensure hooks array exists
if 'hooks' not in settings:
    settings['hooks'] = []

# Define hooks to add
new_hooks = [
    {
        "event": "PreToolUse",
        "command": f"{hooks_dir}/pre-tool-guard.sh",
        "timeout": 5000
    },
    {
        "event": "PostToolUse",
        "command": f"{hooks_dir}/post-tool-guard.sh",
        "timeout": 5000
    },
    {
        "event": "SessionStart",
        "command": f"{hooks_dir}/session-progress-check.sh",
        "timeout": 5000
    },
    {
        "event": "SessionEnd",
        "command": f"{hooks_dir}/session-end.sh",
        "timeout": 5000
    }
]

# Add hooks if not already present
for new_hook in new_hooks:
    exists = any(h.get('command', '').endswith(os.path.basename(new_hook['command']))
                 for h in settings['hooks'])
    if not exists:
        settings['hooks'].append(new_hook)
        print(f"  Added {os.path.basename(new_hook['command'])}")

with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)

print("  Hook configuration complete")
EOF
        fi
    else
        print_info "Creating new settings.json with hook configurations..."
        cat > "$SETTINGS_FILE" << EOF
{
  "hooks": [
    {
      "event": "PreToolUse",
      "command": "$HOOKS_DIR/pre-tool-guard.sh",
      "timeout": 5000
    },
    {
      "event": "PostToolUse",
      "command": "$HOOKS_DIR/post-tool-guard.sh",
      "timeout": 5000
    },
    {
      "event": "SessionStart",
      "command": "$HOOKS_DIR/session-progress-check.sh",
      "timeout": 5000
    },
    {
      "event": "SessionEnd",
      "command": "$HOOKS_DIR/session-end.sh",
      "timeout": 5000
    }
  ]
}
EOF
        print_status "Created settings.json with hook configurations"
    fi

    # Step 5: Install reference documentation
    print_header "Step 5: Installing Reference Documentation"

    if [ -d "$SKILL_DIR/references" ]; then
        for ref in "$SKILL_DIR/references"/*.md; do
            if [ -f "$ref" ]; then
                filename=$(basename "$ref")
                copy_file "$ref" "$REFERENCE_DIR/$filename" "$filename"
            fi
        done
    else
        print_warning "Reference directory not found"
    fi

    # Step 6: Update CLAUDE.md
    print_header "Step 6: Configuring CLAUDE.md"

    SNIPPET_FILE="$SKILL_DIR/assets/claude-md-snippet.md"

    if [ -f "$CLAUDE_MD" ]; then
        # Check if already configured
        if grep -q "Two-Agent System" "$CLAUDE_MD" 2>/dev/null; then
            print_warning "Two-agent configuration already exists in CLAUDE.md"
        else
            print_info "Appending two-agent configuration to CLAUDE.md..."
            echo "" >> "$CLAUDE_MD"
            cat "$SNIPPET_FILE" >> "$CLAUDE_MD"
            print_status "Updated CLAUDE.md with two-agent configuration"
        fi
    else
        print_info "Creating CLAUDE.md with two-agent configuration..."
        cat "$SNIPPET_FILE" > "$CLAUDE_MD"
        print_status "Created CLAUDE.md"
    fi

    # Step 7: Validate installation
    print_header "Step 7: Validating Installation"

    ERRORS=0

    # Check agents
    if [ -f "$AGENTS_DIR/initializer-agent.md" ]; then
        print_status "initializer-agent installed"
    else
        print_error "initializer-agent NOT found"
        ERRORS=$((ERRORS + 1))
    fi

    if [ -f "$AGENTS_DIR/coding-agent.md" ]; then
        print_status "coding-agent installed"
    else
        print_error "coding-agent NOT found"
        ERRORS=$((ERRORS + 1))
    fi

    # Check hooks
    for hook in pre-tool-guard.sh post-tool-guard.sh session-progress-check.sh session-end.sh; do
        if [ -x "$HOOKS_DIR/$hook" ]; then
            print_status "$hook installed and executable"
        else
            print_error "$hook NOT found or not executable"
            ERRORS=$((ERRORS + 1))
        fi
    done

    # Check CLAUDE.md
    if grep -q "Two-Agent System" "$CLAUDE_MD" 2>/dev/null; then
        print_status "CLAUDE.md configured"
    else
        print_error "CLAUDE.md configuration missing"
        ERRORS=$((ERRORS + 1))
    fi

    # Final status
    print_header "Installation Complete"

    if [ $ERRORS -eq 0 ]; then
        echo -e "${GREEN}"
        echo "  ╔══════════════════════════════════════════════════════════╗"
        echo "  ║   Two-Agent Harness System Successfully Installed!       ║"
        echo "  ╚══════════════════════════════════════════════════════════╝"
        echo -e "${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Restart Claude Code for hooks to take effect"
        echo "  2. Start a new project: 'Initialize this project with feature breakdown'"
        echo "  3. The system will delegate to initializer-agent and coding-agent"
        echo ""
        echo "Documentation: ~/.claude/REFRENCE/TWO-AGENT-HARNESS/"
        echo ""
    else
        echo -e "${RED}"
        echo "  Installation completed with $ERRORS error(s)"
        echo "  Please review the errors above and fix manually"
        echo -e "${NC}"
        exit 1
    fi
}

main "$@"
