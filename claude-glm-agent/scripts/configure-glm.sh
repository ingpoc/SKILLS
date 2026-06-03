#!/bin/bash
# Configure .env files for z.ai GLM 4.7 proxy
# Usage: ./.claude/scripts/configure-glm.sh [--migrate] [--token=YOUR_TOKEN]

set -e

# === Configuration (tailored during init) ===
PROJECT_TYPE=""
ENV_PREFIX=""

# Parse arguments
MIGRATE=false
TOKEN=""
for arg in "$@"; do
    case $arg in
        --migrate)
            MIGRATE=true
            shift
            ;;
        --token=*)
            TOKEN="${arg#*=}"
            shift
            ;;
    esac
done

echo "=== GLM 4.7 Proxy Configuration ==="
echo ""

# === 1. Detect project type if not set ===
if [ -z "$PROJECT_TYPE" ]; then
    echo "1. Detecting project type..."
    if [ -f "package.json" ]; then
        if grep -q '"next"' package.json 2>/dev/null; then
            PROJECT_TYPE="nextjs"
            ENV_PREFIX="NEXT_PUBLIC_"
        elif grep -q '"vite"' package.json 2>/dev/null; then
            PROJECT_TYPE="vite"
            ENV_PREFIX="VITE_"
        else
            PROJECT_TYPE="node"
            ENV_PREFIX=""
        fi
    elif [ -f "requirements.txt" ]; then
        PROJECT_TYPE="python"
        ENV_PREFIX=""
    elif [ -f "go.mod" ]; then
        PROJECT_TYPE="go"
        ENV_PREFIX=""
    elif [ -f "Cargo.toml" ]; then
        PROJECT_TYPE="rust"
        ENV_PREFIX=""
    else
        PROJECT_TYPE="unknown"
        ENV_PREFIX=""
    fi
    echo "✓ Detected: $PROJECT_TYPE"
    echo ""
else
    echo "✓ Project type: $PROJECT_TYPE (pre-configured)"
    echo ""
fi

# === 2. Migration mode ===
if [ "$MIGRATE" = true ]; then
    echo "2. Migration mode: scanning for existing ANTHROPIC_API_KEY..."
    API_KEY_FOUND=""

    if [ -f ".env" ]; then
        if grep -q "ANTHROPIC_API_KEY" .env 2>/dev/null; then
            API_KEY_FOUND=".env"
        fi
    fi
    if [ -f ".env.local" ]; then
        if grep -q "ANTHROPIC_API_KEY" .env.local 2>/dev/null; then
            API_KEY_FOUND=".env.local"
        fi
    fi
    if [ -f ".env.example" ]; then
        if grep -q "ANTHROPIC_API_KEY" .env.example 2>/dev/null; then
            API_KEY_FOUND=".env.example"
        fi
    fi

    if [ -n "$API_KEY_FOUND" ]; then
        echo "⚠️  Found ANTHROPIC_API_KEY in: $API_KEY_FOUND"
        echo ""
        echo "This will:"
        echo "  1. Backup the existing file"
        echo "  2. Replace ANTHROPIC_API_KEY with ANTHROPIC_AUTH_TOKEN"
        echo "  3. Add ANTHROPIC_BASE_URL"
        echo "  4. Add model override variables"
        echo ""
        read -p "Continue? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted."
            exit 0
        fi

        # Backup
        BACKUP="${API_KEY_FOUND}.backup.$(date +%s)"
        cp "$API_KEY_FOUND" "$BACKUP"
        echo "✓ Backed up to: $BACKUP"

        # Replace variables
        sed -i.bak 's/ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN/g' "$API_KEY_FOUND"
        rm -f "${API_KEY_FOUND}.bak"

        # Update token value if new token provided
        if [ -n "$TOKEN" ]; then
            # Use awk for more robust replacement
            awk -v token="$TOKEN" '{gsub(/ANTHROPIC_AUTH_TOKEN=.*/, "ANTHROPIC_AUTH_TOKEN=" token)} 1' "$API_KEY_FOUND" > "$API_KEY_FOUND.tmp" && mv "$API_KEY_FOUND.tmp" "$API_KEY_FOUND"
        fi

        # Add new variables if not present
        if ! grep -q "ANTHROPIC_BASE_URL" "$API_KEY_FOUND" 2>/dev/null; then
            echo "" >> "$API_KEY_FOUND"
            echo "# z.ai GLM 4.7 Proxy" >> "$API_KEY_FOUND"
            echo "ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic" >> "$API_KEY_FOUND"
        fi

        if ! grep -q "ANTHROPIC_DEFAULT_SONNET_MODEL" "$API_KEY_FOUND" 2>/dev/null; then
            echo "ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7" >> "$API_KEY_FOUND"
            echo "ANTHROPIC_DEFAULT_OPUS_MODEL=glm-4.7" >> "$API_KEY_FOUND"
        fi

        echo "✓ Migrated: $API_KEY_FOUND"
        echo ""
        if [ -n "$TOKEN" ]; then
            echo "Token has been updated to the new z.ai token."
            echo ""
        fi
        echo "Next steps:"
        echo "  1. Test connection: ~/.claude/skills/claude-glm-agent/scripts/test-proxy.sh"
        exit 0
    else
        echo "⚠️  No ANTHROPIC_API_KEY found, proceeding with normal configuration..."
        echo ""
    fi
fi

# === 3. Get z.ai token ===
if [ -z "$TOKEN" ]; then
    echo "3. Enter your z.ai token:"
    echo "   (Get your token from https://z.ai)"
    read -sp "   Token: " TOKEN
    echo
    echo ""
fi

if [ -z "$TOKEN" ]; then
    echo "❌ Token is required"
    exit 1
fi

# === 4. Determine target file ===
case "$PROJECT_TYPE" in
    nextjs)
        TARGET_FILE=".env.local"
        ;;
    vite)
        TARGET_FILE=".env"
        ;;
    python|go|rust|node)
        TARGET_FILE=".env"
        ;;
    *)
        TARGET_FILE=".env"
        ;;
esac

# === 5. Create or update .env file ===
echo "4. Configuring: $TARGET_FILE"
echo ""

# Backup existing file
if [ -f "$TARGET_FILE" ]; then
    BACKUP="${TARGET_FILE}.backup.$(date +%s)"
    cp "$TARGET_FILE" "$BACKUP"
    echo "✓ Backed up existing file to: $BACKUP"
fi

# Check if already configured
if [ -f "$TARGET_FILE" ] && grep -q "ANTHROPIC_BASE_URL.*z.ai" "$TARGET_FILE" 2>/dev/null; then
    echo "⚠️  File already configured for z.ai"
    read -p "   Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Write configuration
cat > "$TARGET_FILE" << EOF
# z.ai GLM 4.7 Proxy Configuration
${ENV_PREFIX}ANTHROPIC_AUTH_TOKEN=$TOKEN
${ENV_PREFIX}ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
${ENV_PREFIX}ANTHROPIC_DEFAULT_HAIKU_MODEL=glm-4.7
${ENV_PREFIX}ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7
${ENV_PREFIX}ANTHROPIC_DEFAULT_OPUS_MODEL=glm-4.7
EOF

echo "✓ Created: $TARGET_FILE"
echo ""

# === 6. Update .gitignore if needed ===
echo "5. Updating .gitignore..."
if [ -f ".gitignore" ]; then
    if ! grep -q "^\.env\.local$" .gitignore 2>/dev/null; then
        if [ "$TARGET_FILE" = ".env.local" ]; then
            echo ".env.local" >> .gitignore
            echo "✓ Added .env.local to .gitignore"
        fi
    fi
    if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
        if [ "$TARGET_FILE" = ".env" ]; then
            # Check if .env is already ignored with pattern
            if ! grep -q "\.env" .gitignore 2>/dev/null; then
                echo ".env" >> .gitignore
                echo "✓ Added .env to .gitignore"
            fi
        fi
    fi
else
    echo ".env.local" > .gitignore
    echo "✓ Created .gitignore"
fi
echo ""

# === 7. Instructions ===
echo "=== Configuration Complete ==="
echo ""
echo "Variables configured:"
echo "  ${ENV_PREFIX}ANTHROPIC_AUTH_TOKEN=***"
echo "  ${ENV_PREFIX}ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic"
echo "  ${ENV_PREFIX}ANTHROPIC_DEFAULT_HAIKU_MODEL=glm-4.7"
echo "  ${ENV_PREFIX}ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7"
echo "  ${ENV_PREFIX}ANTHROPIC_DEFAULT_OPUS_MODEL=glm-4.7"
echo ""
echo "Next steps:"
echo "  1. Restart your development server"
echo "  2. Test proxy: ~/.claude/skills/claude-glm-agent/scripts/test-proxy.sh"
echo ""
echo "For deployment, set these environment variables in your hosting platform:"
echo "  - Netlify: Site settings > Environment variables"
echo "  - Vercel: Project settings > Environment variables"
echo "  - Render: Environment tab in service settings"
