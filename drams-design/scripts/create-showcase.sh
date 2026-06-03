#!/bin/bash
# DRAMS Design - Create Showcase
# Usage: bash create-showcase.sh <name> [--components all|<list>]

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATES_DIR="$SKILL_DIR/assets/templates"
OUTPUT_NAME="$1"
COMPONENTS_ARG="${2:-all}"
OUTPUT_DIR="."

# Parse components
if [[ "$COMPONENTS_ARG" == "all" ]]; then
  COMPONENTS=("rolling-search" "text-box" "dropdown" "select-box" "time-selector" "toggle-switch" "product-card" "flip-card" "radio-group")
else
  IFS=',' read -ra COMPONENTS <<< "$COMPONENTS_ARG"
fi

OUTPUT_FILE="$OUTPUT_DIR/${OUTPUT_NAME}.html"

# Start building HTML
cat > "$OUTPUT_FILE" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DRAMS Components Showcase</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      min-height: 100vh;
      background: #fafafa;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      padding: 60px 20px;
    }
    .header { text-align: center; margin-bottom: 60px; }
    .header h1 { font-weight: 300; font-size: 32px; color: #333; letter-spacing: -0.5px; }
    .header p { color: #999; font-size: 14px; margin-top: 8px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 40px;
      max-width: 1400px;
      margin: 0 auto;
    }
    .component-section {
      background: white;
      border-radius: 16px;
      padding: 32px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .component-title {
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #999;
      margin-bottom: 24px;
      font-weight: 500;
    }
EOF

# Extract and append styles from each component
for comp in "${COMPONENTS[@]}"; do
  comp=$(echo "$comp" | xargs)
  TEMPLATE="$TEMPLATES_DIR/${comp}.html"

  if [[ -f "$TEMPLATE" ]]; then
    # Extract styles from template (between <style> tags)
    sed -n '/<style>/,/<\/style>/p' "$TEMPLATE" | sed '1d;$d' >> "$OUTPUT_FILE"
  fi
done

# Continue HTML structure
cat >> "$OUTPUT_FILE" << 'EOF'
  </style>
</head>
<body>
  <div class="header">
    <h1>DRAMS Components</h1>
    <p>Less, but better — Dieter Rams-inspired UI</p>
  </div>
  <div class="grid">
EOF

# Append component HTML (wrapped in sections)
for comp in "${COMPONENTS[@]}"; do
  comp=$(echo "$comp" | xargs)
  TEMPLATE="$TEMPLATES_DIR/${comp}.html"

  if [[ -f "$TEMPLATE" ]]; then
    # Get title
    TITLE=$(echo "$comp" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')

    # Extract body content (between body tags or after style)
    CONTENT=$(sed -n '/<body>/,/<\/body>/p' "$TEMPLATE" | sed '1d;$d')

    echo "    <div class=\"component-section\">" >> "$OUTPUT_FILE"
    echo "      <div class=\"component-title\">$TITLE</div>" >> "$OUTPUT_FILE"
    echo "      $CONTENT" >> "$OUTPUT_FILE"
    echo "    </div>" >> "$OUTPUT_FILE"
  fi
done

# Close HTML
cat >> "$OUTPUT_FILE" << 'EOF'
  </div>

  <script>
    // Rolling Search
    document.querySelectorAll('.search-container').forEach(container => {
      const ball = container.querySelector('.orange-ball');
      const input = container.querySelector('.search-input');

      ball?.addEventListener('click', () => {
        container.classList.toggle('expanded');
        if (container.classList.contains('expanded')) {
          input?.focus();
        }
      });

      input?.addEventListener('blur', () => {
        setTimeout(() => container.classList.remove('expanded'), 150);
      });
    });

    // Dropdown
    document.querySelectorAll('.dropdown').forEach(dropdown => {
      const track = dropdown.querySelector('.dropdown-track');
      const label = dropdown.querySelector('.dropdown-label');
      const items = dropdown.querySelectorAll('.dropdown-item');

      track?.addEventListener('click', () => dropdown.classList.toggle('open'));

      items.forEach(item => {
        item.addEventListener('click', () => {
          items.forEach(i => i.classList.remove('selected'));
          item.classList.add('selected');
          if (label) {
            label.textContent = item.textContent;
            label.classList.remove('placeholder');
          }
          dropdown.classList.remove('open');
        });
      });
    });

    // Quantity
    document.querySelectorAll('.select-box').forEach(box => {
      const valueEl = box.querySelector('.select-value');
      let value = 1;

      box.querySelector('.plus-btn')?.addEventListener('click', () => {
        if (value < 99) {
          value++;
          if (valueEl) valueEl.textContent = value;
        }
      });

      box.querySelector('.minus-btn')?.addEventListener('click', () => {
        if (value > 1) {
          value--;
          if (valueEl) valueEl.textContent = value;
        }
      });
    });

    // Toggle
    document.querySelectorAll('.toggle-switch').forEach(toggle => {
      toggle.addEventListener('click', () => toggle.classList.toggle('active'));
    });

    // Flip Card
    document.querySelectorAll('.flip-card').forEach(card => {
      card.addEventListener('click', () => card.classList.toggle('flipped'));
    });
  </script>
</body>
</html>
EOF

echo "Created showcase: $OUTPUT_FILE"
