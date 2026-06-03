#!/bin/bash
# Migrate from ANTHROPIC_API_KEY to AUTH_TOKEN + BASE_URL
# Usage: ~/.claude/skills/claude-glm-agent/scripts/migrate-env.sh [--dry-run]

set -e

DRY_RUN=false
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
    esac
done

echo "=== Environment Variable Migration ==="
echo ""
echo "This script migrates from ANTHROPIC_API_KEY to ANTHROPIC_AUTH_TOKEN"
echo "with z.ai proxy configuration."
echo ""

FILES_TO_MIGRATE=()

# Scan for .env files
if [ -f ".env" ]; then
    FILES_TO_MIGRATE+=(".env")
fi
if [ -f ".env.local" ]; then
    FILES_TO_MIGRATE+=(".env.local")
fi
if [ -f ".env.example" ]; then
    FILES_TO_MIGRATE+=(".env.example")
fi

if [ ${#FILES_TO_MIGRATE[@]} -eq 0 ]; then
    echo "⚠️  No .env files found to migrate"
    exit 0
fi

echo "Found files:"
for file in "${FILES_TO_MIGRATE[@]}"; do
    echo "  - $file"
done
echo ""

# Process each file
for file in "${FILES_TO_MIGRATE[@]}"; do
    echo "Processing: $file"

    # Check if ANTHROPIC_API_KEY exists
    if ! grep -q "ANTHROPIC_API_KEY" "$file" 2>/dev/null; then
        echo "  ⚠️  No ANTHROPIC_API_KEY found, skipping"
        echo ""
        continue
    fi

    # Check if already migrated
    if grep -q "ANTHROPIC_BASE_URL.*z.ai" "$file" 2>/dev/null; then
        echo "  ⚠️  Already configured for z.ai, skipping"
        echo ""
        continue
    fi

    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY RUN] Would migrate $file"
        echo ""
        continue
    fi

    # Backup
    BACKUP="${file}.backup.$(date +%s)"
    cp "$file" "$BACKUP"
    echo "  ✓ Backed up to: $BACKUP"

    # Replace API_KEY with AUTH_TOKEN
    sed -i.bak 's/ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN/g' "$file"
    rm -f "${file}.bak"
    echo "  ✓ Replaced ANTHROPIC_API_KEY → ANTHROPIC_AUTH_TOKEN"

    # Add BASE_URL if not present
    if ! grep -q "ANTHROPIC_BASE_URL" "$file" 2>/dev/null; then
        echo "" >> "$file"
        echo "# z.ai GLM 4.7 Proxy" >> "$file"
        echo "ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic" >> "$file"
        echo "  ✓ Added ANTHROPIC_BASE_URL"
    fi

    # Add model overrides if not present
    if ! grep -q "ANTHROPIC_DEFAULT_SONNET_MODEL" "$file" 2>/dev/null; then
        echo "ANTHROPIC_DEFAULT_HAIKU_MODEL=glm-4.7" >> "$file"
        echo "ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7" >> "$file"
        echo "ANTHROPIC_DEFAULT_OPUS_MODEL=glm-4.7" >> "$file"
        echo "  ✓ Added model overrides"
    fi

    echo "  ✓ Migrated: $file"
    echo ""
done

echo "=== Migration Complete ==="
echo ""
echo "Next steps:"
echo "  1. Update ANTHROPIC_AUTH_TOKEN values with your z.ai token"
echo "  2. Restart your development server"
echo "  3. Test connection: ~/.claude/skills/claude-glm-agent/scripts/test-proxy.sh"
