#!/bin/bash
# validate_colors.sh - Check if colors match duotone palette

ALLOWED_COLORS=(
  "#FAF9F5"  # cream
  "#141413"  # charcoal
  "var(--cream)"
  "var(--charcoal)"
  "var(--primary)"
  "var(--saffron)"
)

file="$1"

if [ -z "$file" ]; then
  echo "Usage: validate_colors.sh <file>"
  exit 1
fi

# Find potential hex colors (6 digits)
hex_colors=$(grep -oE '#[0-9A-Fa-f]{6}' "$file" | sort -u)

violations=0
for color in $hex_colors; do
  valid=false
  for allowed in "${ALLOWED_COLORS[@]}"; do
    if [[ "$color" == "$allowed" ]]; then
      valid=true
      break
    fi
  done
  if [ "$valid" = false ]; then
    echo "❌ Invalid color: $color"
    ((violations++))
  fi
done

if [ $violations -eq 0 ]; then
  echo "✅ All colors valid (duotone palette)"
  exit 0
else
  echo "❌ Found $violations invalid color(s)"
  exit 1
fi
