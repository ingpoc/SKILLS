#!/usr/bin/env bash
# Validation script for scroll-storyteller skill
# Usage: bash scripts/validate.sh [html-file]

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ERRORS=0
WARNINGS=0

echo "🔍 Scroll-Storyteller Validation"
echo "==============================="
echo ""

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- File Structure Validation ---
echo "📁 Checking skill structure..."

required_files=(
  "SKILL.md"
  "scripts/generate.sh"
  "scripts/svg-generator.sh"
  "assets/svg-templates.md"
  "references/anthropic-design.md"
  "references/gsap-patterns.md"
  "references/css-only-patterns.md"
  "references/design-harmony.md"
)

for file in "${required_files[@]}"; do
  if [ -f "$SKILL_DIR/$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ${RED}❌ Missing: $file${NC}"
    ((ERRORS++))
  fi
done

# Check executable scripts
echo ""
echo "🔐 Checking executable permissions..."
if [ -x "$SKILL_DIR/scripts/generate.sh" ]; then
  echo "  ✅ scripts/generate.sh is executable"
else
  echo "  ${YELLOW}⚠️  scripts/generate.sh should be executable${NC}"
  ((WARNINGS++))
fi

if [ -x "$SKILL_DIR/scripts/svg-generator.sh" ]; then
  echo "  ✅ scripts/svg-generator.sh is executable"
else
  echo "  ${YELLOW}⚠️  scripts/svg-generator.sh should be executable${NC}"
  ((WARNINGS++))
fi

# --- HTML Validation (if file provided) ---
if [ -n "$1" ] && [ -f "$1" ]; then
  echo ""
  echo "📄 Validating HTML file: $1"
  HTML_FILE="$1"

  # Check for required elements
  echo ""
  echo "  Checking required elements..."

  required_elements=(
    "cursor-ring"
    "cursor-dot"
    "progress-bar"
    "scroll-indicator"
    "hero-title"
    "chapter-number"
  )

  for element in "${required_elements[@]}"; do
    if grep -q "$element" "$HTML_FILE"; then
      echo "    ✅ .$element found"
    else
      echo "    ${RED}❌ .$element missing${NC}"
      ((ERRORS++))
    fi
  done

  # Check for geometric shapes (should NOT be present in SVGs)
  echo ""
  echo "  Checking for prohibited geometric shapes..."

  geometric_count=0

  # Count circles, but exclude spotlight-circle (functional element)
  circle_count=$(grep -c '<circle' "$HTML_FILE" || echo "0")
  spotlight_count=$(grep -c 'spotlight-circle' "$HTML_FILE" || echo "0")
  decorative_circles=$((circle_count - spotlight_count))

  if [ "$decorative_circles" -gt 0 ]; then
    echo "    ${RED}❌ Found <circle> elements: $decorative_circles (should use organic paths)${NC}"
    ((geometric_count += decorative_circles))
  else
    if [ "$spotlight_count" -gt 0 ]; then
      echo "    ✅ No decorative circles (spotlight circles OK: $spotlight_count)"
    else
      echo "    ✅ No <circle> elements"
    fi
  fi

  if grep -q '<rect' "$HTML_FILE"; then
    count=$(grep -c '<rect' "$HTML_FILE" || echo "0")
    echo "    ${RED}❌ Found <rect> elements: $count (should use organic paths)${NC}"
    ((geometric_count += count))
  else
    echo "    ✅ No <rect> elements"
  fi

  if [ $geometric_count -gt 0 ]; then
    ((ERRORS++))
  fi

  # Check for organic paths (should be present)
  echo ""
  echo "  Checking for organic paths..."

  organic_count=$(grep -c 'organic-path' "$HTML_FILE" || echo "0")
  if [ "$organic_count" -gt 10 ]; then
    echo "    ✅ Found $organic_count organic-path elements"
  else
    echo "    ${YELLOW}⚠️  Only $organic_count organic-path elements (expected more)${NC}"
    ((WARNINGS++))
  fi

  # Check for hardcoded colors in SVG (warning only - some may be in comments)
  echo ""
  echo "  Checking for hardcoded colors in SVG fills..."

  # Count hardcoded colors in fill attributes (using -E for compatibility)
  hardcoded_fills=$(grep -oE 'fill="#[0-9A-Fa-f]{6}"' "$HTML_FILE" | wc -l | tr -d ' ')
  hardcoded_vars=$(grep -c 'fill="var(--' "$HTML_FILE" || echo "0")

  echo "    📊 CSS variable fills: $hardcoded_vars"
  echo "    📊 Hardcoded fills: $hardcoded_fills"

  if [ "$hardcoded_fills" -gt "$hardcoded_vars" ]; then
    echo "    ${YELLOW}⚠️  More hardcoded fills than CSS variables${NC}"
    ((WARNINGS++))
  else
    echo "    ✅ Using CSS variables for fills"
  fi

  # Check for transition sections (GSAP only)
  if grep -q 'ScrollTrigger' "$HTML_FILE"; then
    echo ""
    echo "  Checking GSAP-specific features..."

    transition_count=$(grep -c 'transition-section' "$HTML_FILE" || echo "0")
    if [ "$transition_count" -ge 2 ]; then
      echo "    ✅ Found $transition_count transition-section elements"
    else
      echo "    ${YELLOW}⚠️  Only $transition_count transition-section elements (expected ≥2)${NC}"
      ((WARNINGS++))
    fi

    spotlight_count=$(grep -c 'spotlight-layer' "$HTML_FILE" || echo "0")
    if [ "$spotlight_count" -ge 1 ]; then
      echo "    ✅ Found spotlight-layer"
    else
      echo "    ${YELLOW}⚠️  spotlight-layer not found${NC}"
      ((WARNINGS++))
    fi
  fi

  # Check for CSS-only features
  if ! grep -q 'ScrollTrigger' "$HTML_FILE" && grep -q 'IntersectionObserver' "$HTML_FILE"; then
    echo ""
    echo "  Checking CSS-only specific features..."

    lamp_count=$(grep -c 'lamp-container\|desk-lamp' "$HTML_FILE" || echo "0")
    if [ "$lamp_count" -ge 1 ]; then
      echo "    ✅ Found desk lamp element"
    else
      echo "    ${YELLOW}⚠️  Desk lamp not found${NC}"
      ((WARNINGS++))
    fi
  fi

  # --- Chapter Count Validation ---
  echo ""
  echo "  Checking chapter structure..."

  # Count chapter sections
  chapter_count=$(grep -c '<section class="chapter' "$HTML_FILE" || echo "0")
  echo "    📊 Found $chapter_count chapter section(s)"

  if [ "$chapter_count" -lt 3 ]; then
    echo "    ${RED}❌ Minimum 3 chapters required${NC}"
    ((ERRORS++))
  elif [ "$chapter_count" -gt 5 ]; then
    echo "    ${RED}❌ Maximum 5 chapters allowed${NC}"
    ((ERRORS++))
  else
    echo "    ✅ Valid chapter count (3-5)"
  fi

  # Verify chapter numbers are sequential
  echo ""
  echo "  Checking chapter number sequence..."

  for i in $(seq 1 "$chapter_count"); do
    padded=$(printf "%02d" "$i")
    if grep -q "class=\"chapter-number\">$padded<" "$HTML_FILE" || grep -q ">$padded</span>" "$HTML_FILE"; then
      echo "    ✅ Chapter $padded found"
    else
      echo "    ${RED}❌ Chapter $padded missing or out of order${NC}"
      ((ERRORS++))
    fi
  done

  # Check light/dark alternation (light first, then alternating)
  echo ""
  echo "  Checking light/dark alternation..."

  alternation_valid=true
  prev_theme=""

  # Extract chapter themes in order
  while IFS= read -r line; do
    if echo "$line" | grep -q 'chapter light'; then
      theme="light"
    elif echo "$line" | grep -q 'chapter dark'; then
      theme="dark"
    else
      continue
    fi

    if [ -n "$prev_theme" ] && [ "$theme" == "$prev_theme" ]; then
      alternation_valid=false
    fi
    prev_theme="$theme"
  done < <(grep -o '<section class="chapter [^"]*"' "$HTML_FILE")

  # Check first chapter is light
  first_chapter=$(grep -o '<section class="chapter [^"]*"' "$HTML_FILE" | head -1)
  if echo "$first_chapter" | grep -q 'light'; then
    echo "    ✅ First chapter is light-themed"
  else
    echo "    ${RED}❌ First chapter should be light-themed${NC}"
    ((ERRORS++))
    alternation_valid=false
  fi

  if [ "$alternation_valid" == "true" ]; then
    echo "    ✅ Light/dark alternation correct"
  else
    echo "    ${RED}❌ Light/dark alternation broken${NC}"
    ((ERRORS++))
  fi

fi

# --- Test Generation ---
echo ""
echo "🧪 Testing generation..."

# Test GSAP generation
if bash "$SKILL_DIR/scripts/generate.sh" "/tmp/validate-test-gsap" "1" "--gsap" 2>&1 | grep -q "Created:"; then
  echo "  ✅ GSAP generation works"
  rm -f "/tmp/validate-test-gsap.html"
else
  echo "  ${RED}❌ GSAP generation failed${NC}"
  ((ERRORS++))
fi

# Test CSS-only generation
if bash "$SKILL_DIR/scripts/generate.sh" "/tmp/validate-test-css" "1" 2>&1 | grep -q "Created:"; then
  echo "  ✅ CSS-only generation works"
  rm -f "/tmp/validate-test-css.html"
else
  echo "  ${RED}❌ CSS-only generation failed${NC}"
  ((ERRORS++))
fi

# Test variable chapter counts
echo ""
echo "  Testing chapter count options..."

for chapters in 3 4 5; do
  if bash "$SKILL_DIR/scripts/generate.sh" "/tmp/validate-test-ch$chapters" "1" "--chapters" "$chapters" 2>&1 | grep -q "Created:"; then
    # Verify correct chapter count
    actual=$(grep -c '<section class="chapter' "/tmp/validate-test-ch$chapters.html" || echo "0")
    if [ "$actual" -eq "$chapters" ]; then
      echo "  ✅ --chapters $chapters works (generated $actual chapters)"
    else
      echo "  ${RED}❌ --chapters $chapters failed (expected $chapters, got $actual)${NC}"
      ((ERRORS++))
    fi
    rm -f "/tmp/validate-test-ch$chapters.html"
  else
    echo "  ${RED}❌ --chapters $chapters generation failed${NC}"
    ((ERRORS++))
  fi
done

# --- SVG Generator Test ---
echo ""
echo "🎨 Testing SVG generator..."

if source "$SKILL_DIR/scripts/svg-generator.sh" 2>/dev/null && declare -f generate_svg_for_chapter > /dev/null; then
  echo "  ✅ svg-generator.sh functions available"
else
  echo "  ${RED}❌ svg-generator.sh failed to load${NC}"
  ((ERRORS++))
fi

# --- Summary ---
echo ""
echo "==============================="
echo "📊 Validation Summary"
echo "==============================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo -e "${GREEN}✅ All checks passed!${NC}"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo -e "${YELLOW}⚠️  Passed with $WARNINGS warning(s)${NC}"
  exit 0
else
  echo -e "${RED}❌ Failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
  exit 1
fi
