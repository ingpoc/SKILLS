#!/usr/bin/env bash
set -eu

ROOT="${1:-.}"

echo "# Requirements Surface Grep"
echo

echo "## Current route"
(cd "$ROOT" && npm run goal:next) 2>/dev/null || true
echo

echo "## Mockup inventory"
find "$ROOT/mockups" -maxdepth 2 -type f \( -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' -o -name '*.webp' \) 2>/dev/null | sort || true
echo

echo "## Likely dead-control wording"
rg -n "coming soon|TODO|disabled|placeholder|stub|not implemented|fake|static|mock only|No .* yet|could not be loaded" "$ROOT" \
  -g'*.md' -g'*.swift' -g'*.js' -g'*.sh' -g'*.json' \
  -g'!node_modules' -g'!.build' -g'!output' 2>/dev/null || true
echo

echo "## Runtime-proof wording"
rg -n "runtime tap|manual proof|simulator|verify:macos-screens|verify:simulator-local|smoke:mvp|phase:preflight" "$ROOT/PROGRESS.md" "$ROOT/docs" "$ROOT/script" 2>/dev/null || true

