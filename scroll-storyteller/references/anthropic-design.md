# Anthropic Design System Reference

Complete design language reference deduced from Anthropic's website illustrations.

## Color Philosophy

### Strict Duotone

Anthropic uses exactly two colors across ALL illustrations:

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| Cream | `#FAF9F5` | rgb(250, 249, 245) | Light backgrounds, light-on-dark elements |
| Charcoal | `#141413` | rgb(20, 20, 19) | Dark backgrounds, dark-on-light elements |

**Rules:**
- No gradients within illustrations (CSS gradients OK for effects)
- No third colors, ever
- No grays - only cream and charcoal
- Opacity (0.3-0.6) creates depth, not additional colors

### Background Contexts

| Section Type | Background | Illustration Fill |
|--------------|------------|-------------------|
| Dark section | `#141413` | `#FAF9F5` |
| Light section | `#FAF9F5` | `#141413` |

## Typography

### Font Stack

| Role | Primary | Fallback | Weight |
|------|---------|----------|--------|
| Display/Headings | Instrument Serif | Georgia, serif | 400 |
| Body/UI | Inter | -apple-system, sans-serif | 300-400 |

### Sizing Scale

```css
--text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
--text-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);
--text-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
--text-lg: clamp(1.125rem, 1rem + 0.625vw, 1.25rem);
--text-xl: clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem);
--text-2xl: clamp(1.5rem, 1.2rem + 1.5vw, 2rem);
--text-3xl: clamp(2rem, 1.5rem + 2.5vw, 3rem);
--text-4xl: clamp(2.5rem, 2rem + 2.5vw, 4rem);
--text-5xl: clamp(3rem, 2rem + 5vw, 7rem);
```

### Typography Characteristics

| Property | Display | Body |
|----------|---------|------|
| Letter-spacing | -0.02em to -0.04em | 0 |
| Line-height | 1.1 - 1.2 | 1.5 - 1.8 |
| Weight | 400 (regular) | 300-400 |
| Style | Elegant, editorial | Clean, readable |

## SVG Illustration Rules

### Path Types

| Allowed | Not Allowed |
|---------|-------------|
| `<path>` with Bézier curves | `<circle>` |
| `<ellipse>` (sparingly) | `<rect>` |
| Complex organic shapes | `<polygon>` |
| | `<line>` |

### Curve Commands

```
M - Move to (start point)
Q - Quadratic Bézier (one control point)
C - Cubic Bézier (two control points)
L - Line to (use sparingly, for structure)
Z - Close path
```

**Example organic path:**
```xml
<path d="M250 150 Q300 120 350 160 Q400 220 360 300
         Q300 380 250 360 Q180 340 160 280
         Q140 200 200 150 Q230 130 250 150 Z"/>
```

### Composition Rules

| Rule | Implementation |
|------|----------------|
| ViewBox | 500x500 or 1000x1000 (square) |
| Path count | 2-4 paths per illustration |
| Fill method | `fill` attribute, never `stroke` for main shapes |
| Layering | Light shapes behind, dark shapes in front |
| Opacity | 0.3-0.6 for depth layers, never below 0.2 |

### Organic Feel Techniques

1. **Asymmetry** - No perfect circles or rectangles
2. **Curve variation** - Mix quadratic and cubic Béziers
3. **Imperfect edges** - Control points offset from geometric perfection
4. **Flowing transitions** - Smooth curves, no sharp angles
5. **Negative space** - Let shapes breathe

## Animation Principles

### Timing Functions

| Animation Type | Easing |
|----------------|--------|
| Reveals | `cubic-bezier(0.25, 0.46, 0.45, 0.94)` |
| Cursor follow | Linear interpolation with factor 0.15-0.4 |
| Hover effects | `cubic-bezier(0.4, 0, 0.2, 1)` |
| Scroll parallax | Direct scroll mapping (no easing) |

### Duration Guidelines

| Effect | Duration |
|--------|----------|
| Micro-interactions | 150-300ms |
| Element reveals | 600-800ms |
| Page transitions | 400-600ms |
| Stagger delay | 100-200ms per item |

### Animation Values

```javascript
// Cursor smoothing
const outerEasing = 0.15;  // Slower, smoother
const innerEasing = 0.4;   // Faster, responsive

// Scroll parallax
const parallaxSpeed = 0.3; // Subtle movement

// Intersection threshold
const revealThreshold = 0.2;
const rootMargin = '0px 0px -100px 0px';
```

## Interactive Patterns

### Custom Cursor

```css
.cursor {
  width: 40px;
  height: 40px;
  border: 1px solid currentColor;
  border-radius: 50%;
  mix-blend-mode: difference;
  pointer-events: none;
  position: fixed;
  z-index: 9999;
}

.cursor-dot {
  width: 8px;
  height: 8px;
  background: currentColor;
  border-radius: 50%;
}
```

### Spotlight Effect

```css
.spotlight-layer {
  background: radial-gradient(
    circle 400px at var(--mouse-x) var(--mouse-y),
    rgba(250, 249, 245, 0.03) 0%,
    transparent 100%
  );
}
```

### Staggered Reveals

```javascript
words.forEach((word, i) => {
  setTimeout(() => {
    word.classList.add('revealed');
  }, baseDelay + i * staggerDelay);
});
```

## Layout Patterns

### Section Structure

```
Hero (dark)
  └── Full viewport, centered content

Chapter (alternating)
  └── Two-column: content + illustration
  └── Reverse layout on even chapters

Quote (dark)
  └── Centered, large italic text

Finale (dark)
  └── Combined visual, summary content
```

### Spacing Scale

```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-24: 6rem;     /* 96px */
--space-32: 8rem;     /* 128px */
```

### Container Widths

| Context | Max Width |
|---------|-----------|
| Content | 600-700px |
| Chapter inner | 1200px |
| Full bleed | 100vw |

## Accessibility

### Motion Preferences

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Touch Devices

```javascript
const isTouchDevice = 'ontouchstart' in window;
if (isTouchDevice) {
  cursor.style.display = 'none';
  cursorDot.style.display = 'none';
}
```

### Contrast

The duotone palette inherently provides excellent contrast:
- Cream on charcoal: 15.5:1 ratio
- Charcoal on cream: 15.5:1 ratio

Both exceed WCAG AAA requirements (7:1).

## Source Analysis

Design language deduced from these Anthropic illustrations:

| Illustration | Key Patterns |
|--------------|--------------|
| LampPaper | Desk lamp, light cone, layered documents |
| Hand Build | Hand holding geometric shape, finger detail |
| Hand NodeTree | Hand with branching nodes, connection lines |
| Node Box | Central container with satellite elements |
| Object ScaleShapes | Overlapping organic forms, depth through opacity |
| Object Chat | Communication bubbles, flowing shapes |
| Hand Key | Hand grasping object, trust/security theme |

All illustrations share:
- Exact same two colors
- Organic Bézier paths
- Fill-only rendering
- 2-4 path compositions
- Thematic symbolism (hands = human agency, nodes = AI systems)
