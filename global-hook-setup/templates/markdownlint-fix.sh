#!/bin/bash
# PostToolUse hook: Auto-fix markdownlint issues for .md files
# Ultra-lightweight: exits immediately for non-.md files

# Read tool input from stdin
FILE=$(cat | jq -r '.tool_input.file_path // empty' 2>/dev/null)

# Exit if not an .md file
[[ "$FILE" != *.md ]] && exit 0

# Exit if file doesn't exist
[[ ! -f "$FILE" ]] && exit 0

# Run markdownlint fix
npx --yes markdownlint-cli2 --fix "$FILE" 2>/dev/null

exit 0
