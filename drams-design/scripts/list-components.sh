#!/bin/bash
# DRAMS Design - List Components
# Usage: bash list-components.sh [--detailed]

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DETAILED="${1:-}"

if [[ "$DETAILED" == "--detailed" ]]; then
  printf "%-20s | %-50s\n" "Component" "Description"
  printf "%s\n" | tr ' ' '-'
  echo "sticky-header        |  Fixed header with logo + pill nav"
  echo "pill-navigation      |  Horizontal pill-based navigation"
  echo "hero-section         |  Centered hero with DRAMS card"
  echo "card-grid            |  Responsive card grid"
  echo "drams-card           |  White card with hover lift"
  echo "rolling-search       |  Expandable search with animated orange ball"
  echo "text-box             |  Input with focus indicator dot"
  echo "dropdown             |  Custom select with orange ball toggle"
  echo "select-box           |  Quantity selector with +/- buttons"
  echo "time-selector        |  Circular hours/minutes display"
  echo "toggle-switch        |  Animated on/off slider"
  echo "product-card         |  Image + details + add button"
  echo "flip-card            |  3D flip reveal with specs"
  echo "radio-group          |  Pill-shaped radio options"
else
  echo "Available components:"
  echo "  sticky-header"
  echo "  pill-navigation"
  echo "  hero-section"
  echo "  card-grid"
  echo "  drams-card"
  echo "  rolling-search"
  echo "  text-box"
  echo "  dropdown"
  echo "  select-box"
  echo "  time-selector"
  echo "  toggle-switch"
  echo "  product-card"
  echo "  flip-card"
  echo "  radio-group"
fi

echo ""
echo "Usage: bash ~/.claude/skills/drams-design/scripts/generate-component.sh <component> [output-dir]"
