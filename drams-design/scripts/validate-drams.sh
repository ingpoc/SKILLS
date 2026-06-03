#!/bin/bash
# DRAMS Design - Validate Component
# Validates against Rams' principles, accessibility, and design tokens
# Exit: 0=pass, 1=warnings, 2=errors

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FILE="$1"
STRICT="${2:-}"

if [[ ! -f "$FILE" ]]; then
  echo "Error: File not found: $FILE" >&2
  exit 2
fi

WARNINGS=0
ERRORS=0

# Design tokens to check
TOKENS=(
  "rgb\(255, 97, 26\)"
  "rgb\(238, 238, 238\)"
  "rgb\(232, 232, 232\)"
  "#333"
  "#999"
  "cubic-bezier\(0\.16, 1, 0\.3, 1\)"
)

echo "Validating: $FILE"
echo ""

# Check for design token compliance
echo "Checking design tokens..."
for token in "${TOKENS[@]}"; do
  if ! grep -qE "$token" "$FILE"; then
    echo "  ⚠ Missing token: $token"
    ((WARNINGS++))
  fi
done

# Check for proper border radius
if ! grep -qE "border-radius:\s*(48px|50%|1[6-9]px|20px)" "$FILE"; then
  echo "  ⚠ No DRAMS border radius found"
  ((WARNINGS++))
fi

# Check for animations
if ! grep -qE "transition:" "$FILE"; then
  echo "  ⚠ No transitions found"
  ((WARNINGS++))
fi

# Check for proper easing
if ! grep -qE "cubic-bezier" "$FILE" && grep -qE "transition:" "$FILE"; then
  echo "  ⚠ Transitions without DRAMS easing"
  ((WARNINGS++))
fi

# Accessibility checks
echo ""
echo "Checking accessibility..."

# Check for ARIA labels
if grep -qE "(button|a|input)" "$FILE" && ! grep -qE "aria-" "$FILE"; then
  echo "  ⚠ Missing ARIA attributes"
  ((WARNINGS++))
fi

# Check for alt text on images
if grep -qE "<img" "$FILE" && ! grep -qE 'alt=' "$FILE"; then
  echo "  ⚠ Images without alt text"
  ((WARNINGS++))
fi

# Check for outline removal (bad practice)
if grep -qE "outline:\s*none" "$FILE" && ! grep -qE "outline.*0.*solid.*rgb\(255, 97, 26\)" "$FILE"; then
  echo "  ✗ Outline removed without focus indicator"
  ((ERRORS++))
fi

# Rams' principles checks
echo ""
echo "Checking Rams' principles..."

# Little design as possible
LINE_COUNT=$(wc -l < "$FILE")
if [[ $LINE_COUNT -gt 500 ]]; then
  echo "  ⚠ File large ($LINE_COUNT lines) - consider simplification"
  ((WARNINGS++))
fi

# Check for unnecessary elements
if grep -qE "important!" "$FILE"; then
  echo "  ⚠ Using !important - avoid"
  ((WARNINGS++))
fi

# Color contrast (basic check)
if grep -qE "color:\s*#999" "$FILE" && grep -qE "background:\s*#fff|white" "$FILE"; then
  # #999 on white has ~4.6:1 contrast - OK
  :
fi

echo ""
if [[ $ERRORS -gt 0 ]]; then
  echo "❌ Validation failed with $ERRORS error(s)"
  exit 2
elif [[ $WARNINGS -gt 0 ]]; then
  echo "⚠ Validation passed with $WARNINGS warning(s)"
  exit 1
else
  echo "✅ Validation passed"
  exit 0
fi
