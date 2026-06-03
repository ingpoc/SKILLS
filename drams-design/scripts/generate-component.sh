#!/bin/bash
# DRAMS Design - Generate Component
# Usage: bash generate-component.sh <component> [output-dir] [--react]

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPONENTS_DIR="$SKILL_DIR/assets/templates"
REACT_DIR="$SKILL_DIR/assets/react"
LAYOUT_TEMPLATES_DIR="$SKILL_DIR/assets/component_templates"

COMPONENT="$1"
OUTPUT_DIR="${2:-.}"
USE_REACT=false

if [[ "$3" == "--react" || "$2" == "--react" ]]; then
  USE_REACT=true
fi

# Helper function to get HTML filename
get_html_file() {
  case "$1" in
    "sticky-header") echo "sticky-header.html" ;;
    "pill-navigation") echo "pill-navigation.html" ;;
    "hero-section") echo "hero-section.html" ;;
    "card-grid") echo "card-grid.html" ;;
    "drams-card") echo "drams-card.html" ;;
    "rolling-search") echo "rolling-search.html" ;;
    "text-box") echo "text-box.html" ;;
    "dropdown") echo "dropdown.html" ;;
    "select-box") echo "select-box.html" ;;
    "time-selector") echo "time-selector.html" ;;
    "toggle-switch") echo "toggle-switch.html" ;;
    "product-card") echo "product-card.html" ;;
    "flip-card") echo "flip-card.html" ;;
    "radio-group") echo "radio-group.html" ;;
    *) echo "" ;;
  esac
}

# Helper function to get React filename
get_react_file() {
  case "$1" in
    "sticky-header") echo "StickyHeader.tsx" ;;
    "pill-navigation") echo "PillNavigation.tsx" ;;
    "hero-section") echo "HeroSection.tsx" ;;
    "card-grid") echo "CardGrid.tsx" ;;
    "drams-card") echo "DRAMSCard.tsx" ;;
    "rolling-search") echo "RollingSearch.tsx" ;;
    "text-box") echo "TextBox.tsx" ;;
    "dropdown") echo "Dropdown.tsx" ;;
    "select-box") echo "SelectBox.tsx" ;;
    "time-selector") echo "TimeSelector.tsx" ;;
    "toggle-switch") echo "ToggleSwitch.tsx" ;;
    "product-card") echo "ProductCard.tsx" ;;
    "flip-card") echo "FlipCard.tsx" ;;
    "radio-group") echo "RadioGroup.tsx" ;;
    *) echo "" ;;
  esac
}

# Helper function to check if component is a layout component (uses component_templates dir)
is_layout_component() {
  case "$1" in
    "sticky-header"|"pill-navigation"|"hero-section"|"card-grid"|"drams-card")
      echo "true"
      ;;
    *)
      echo "false"
      ;;
  esac
}

# Handle comma-separated list
IFS=',' read -ra COMPONENTS <<< "$COMPONENT"
SUCCESS=0
FAILED=0

for comp in "${COMPONENTS[@]}"; do
  comp=$(echo "$comp" | xargs)  # Trim whitespace

  if [[ -z "$comp" ]]; then
    continue
  fi

  if [[ "$USE_REACT" == true ]]; then
    # Check if it's a layout component (uses component_templates dir)
    if [[ "$(is_layout_component "$comp")" == "true" ]]; then
      SOURCE="$LAYOUT_TEMPLATES_DIR/$(get_react_file "$comp")"
    else
      SOURCE="$REACT_DIR/$(get_react_file "$comp")"
    fi
    EXT="tsx"
  else
    SOURCE="$COMPONENTS_DIR/$(get_html_file "$comp")"
    EXT="html"
  fi

  if [[ ! -f "$SOURCE" ]]; then
    echo "Error: Component '$comp' not found" >&2
    ((FAILED++))
    continue
  fi

  # Create output filename
  if [[ "$USE_REACT" == true ]]; then
    OUTPUT_FILE="$OUTPUT_DIR/$(get_react_file "$comp")"
  else
    OUTPUT_FILE="$OUTPUT_DIR/${comp}.${EXT}"
  fi

  # Create output directory if needed
  mkdir -p "$OUTPUT_DIR"

  # Copy file
  cp "$SOURCE" "$OUTPUT_FILE"
  echo "Created: $OUTPUT_FILE"
  ((SUCCESS++))
done

if [[ $FAILED -gt 0 ]]; then
  echo "" >&2
  echo "Available components:" >&2
  bash "$SKILL_DIR/scripts/list-components.sh" >&2
  exit 1
fi

echo ""
echo "Generated $SUCCESS component(s)"
