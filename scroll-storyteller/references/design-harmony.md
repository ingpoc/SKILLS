# Design Harmony Guidelines

Principles for creating visually cohesive scroll storytelling experiences following the Anthropic design language.

---

## Color Architecture

### Duotone Foundation

Every palette uses exactly two colors: **light** and **dark**. This constraint creates focus and prevents visual chaos.

```
--light: <dominant background color>
--dark: <accent/foreground color>
```

### Palette Mood System

| Mood | Palettes | Character |
|------|----------|-----------|
| **Warm** | Anthropic, Sepia, Ember | Inviting, organic, grounded |
| **Cool** | Ocean, Forest, Midnight | Calm, contemplative, focused |
| **Neutral** | Steel | Professional, clean, balanced |
| **Creative** | Dusk | Playful, unexpected, artistic |

### Application Rules

1. **Backgrounds** always use the light color
2. **Text** on light backgrounds uses the dark color
3. **Dark sections** invert: background uses dark, text uses light
4. **SVG fills** use either light or dark with opacity for depth
5. **No strokes** on main shapes (fills only for organic feel)

### Opacity Depth Scale

```
0.1 - 0.2: Background layers, subtle texture
0.3 - 0.4: Secondary shapes, supporting elements
0.5 - 0.6: Primary shapes, main content
0.7 - 0.8: Emphasis, highlights
1.0: Focal points, core elements
```

---

## Palette Mood → SVG Style

The palette mood should influence not just colors but also SVG illustration style, complexity, and emotional quality.

### Style by Mood

| Mood | Opacity Range | Path Complexity | Curve Character | Emotional Quality |
|------|--------------|-----------------|-----------------|-------------------|
| **Warm** (Anthropic, Sepia, Ember) | 0.15-0.6 | Medium | Gentle Q curves, soft transitions | Welcoming, organic, grounded |
| **Cool** (Ocean, Forest, Midnight) | 0.10-0.5 | Medium-High | Mix Q and C curves, crisp edges | Calm, precise, contemplative |
| **Neutral** (Steel) | 0.12-0.55 | Medium | Balanced curves, clean forms | Professional, balanced, clear |
| **Creative** (Dusk) | 0.08-0.5 | High | Complex Béziers, experimental forms | Playful, unexpected, artistic |

### Warm Mood SVG Guidelines

**Character:** Soft, inviting, human-centered
**Opacity:** Start higher (0.15+), build to 0.6 for focal points
**Curves:** Prefer `Q` (quadratic) for gentle, natural curves
**Shapes:** Rounded, organic, slightly asymmetric
**Spacing:** Generous, breathing room between elements

```svg
<!-- Warm mood example: gentle curves, medium opacity -->
<path fill="var(--deep)" opacity="0.4"
  d="M250 200 Q280 180 310 200 Q340 240 310 280 Q280 300 250 280 Q220 260 220 220 Q220 190 250 200 Z"/>
```

### Cool Mood SVG Guidelines

**Character:** Precise, calm, structured
**Opacity:** Lower floor (0.10), maximum 0.5 for restraint
**Curves:** Mix `Q` and `C` (cubic) for controlled complexity
**Shapes:** Cleaner silhouettes, more defined edges
**Spacing:** Tight, intentional negative space

```svg
<!-- Cool mood example: crisper curves, lower opacity -->
<path fill="var(--deep)" opacity="0.35"
  d="M250 200 C270 180 290 180 310 200 C330 220 330 250 310 270 C290 290 270 290 250 270 C230 250 230 220 250 200 Z"/>
```

### Neutral Mood SVG Guidelines

**Character:** Professional, balanced, accessible
**Opacity:** Middle range (0.12-0.55)
**Curves:** Simple, efficient paths
**Shapes:** Clear, readable silhouettes
**Spacing:** Consistent, grid-aware

```svg
<!-- Neutral mood example: balanced, clear -->
<path fill="var(--deep)" opacity="0.45"
  d="M250 180 Q290 180 310 220 Q330 260 310 300 Q290 340 250 340 Q210 340 190 300 Q170 260 190 220 Q210 180 250 180 Z"/>
```

### Creative Mood SVG Guidelines

**Character:** Experimental, layered, unexpected
**Opacity:** Wide range (0.08-0.5), more atmospheric layers
**Curves:** Complex multi-point Béziers, overlapping shapes
**Shapes:** Abstract, non-literal, symbolic
**Spacing:** Overlapping, layered depth

```svg
<!-- Creative mood example: complex, layered -->
<g opacity="0.35">
  <path fill="var(--deep)"
    d="M200 180 Q230 150 270 160 Q310 170 320 210 Q330 250 300 280 Q270 310 230 300 Q190 290 180 250 Q170 210 200 180 Z"/>
  <path fill="var(--deep)" opacity="0.6"
    d="M240 200 Q260 180 290 190 Q310 210 300 240 Q290 270 260 270 Q230 270 220 240 Q210 210 240 200 Z"/>
</g>
```

### Palette-Specific Recommendations

| Palette | Best For Topics | SVG Character |
|---------|----------------|---------------|
| **Anthropic** | Tech, AI, Product | Soft organic blobs, radiating forms |
| **Sepia** | Historical, Legacy, Memory | Aged textures, document-like |
| **Ember** | Passion, Energy, Transformation | Warm glow, ascending forms |
| **Ocean** | Flow, Depth, Journey | Wave forms, horizontal layers |
| **Forest** | Growth, Nature, Renewal | Tree-like, vertical growth |
| **Midnight** | Mystery, Power, Contrast | High contrast, dramatic silhouettes |
| **Steel** | Business, Clarity, Structure | Clean lines, architectural |
| **Dusk** | Creativity, Dreams, Transition | Layered, atmospheric, ethereal |

### Mood Transition in Narrative

As the story progresses, SVG mood can subtly shift:

| Position | Mood Adjustment |
|----------|-----------------|
| **Hero** | Establish base mood, atmospheric (lower opacity) |
| **Chapter 1** | Pure expression of mood |
| **Chapter 2** | Slight intensity increase (conflict) |
| **Chapter 3** | Mood peaks (triumph/resolution) |
| **Finale** | Return to calm, symbolic summary |

---

## Typography Hierarchy

### Font Pairing

**Display:** `Instrument Serif` - Headlines, titles, quotes
**Body:** `Inter` - Descriptions, labels, UI elements

### Scale System

```css
/* Hero Title */
font-size: clamp(3rem, 8vw, 7rem);

/* Chapter Titles */
font-size: clamp(2rem, 5vw, 3.5rem);

/* Body Text */
font-size: 1.1rem;
font-weight: 300;

/* Labels/Small */
font-size: 0.9rem;
text-transform: uppercase;
letter-spacing: 0.15em;
```

**`clamp()` pattern:** `clamp(min, preferred, max)` ensures responsive scaling without breakpoints.

### Letter-Spacing

```css
/* Headlines */
letter-spacing: -0.02em;

/* Uppercase labels */
letter-spacing: 0.15em - 0.2em;

/* Body text */
letter-spacing: normal;
```

**Rule:** Negative spacing for large headlines, positive for uppercase.

---

## Spacing System

### Content Padding

```
Mobile:     30px (left/right)
Tablet:     60px
Desktop:    80px - 100px
```

### Section Rhythm

```
Hero:        100vh (full viewport)
Chapters:    100vh (minimum)
Transitions: 200px
Quote:       100vh
Finale:      100vh
```

### Grid Gaps

```
Chapter inner:  60px
Content cards:  40px
SVG elements:   auto (organic spacing)
```

---

## Depth & Layering

### Z-Index Stack

```
0: Background elements
1: Content, illustrations
10: Progress bar
50: Transition sections
100: Spotlight layer
9999: Custom cursor
```

### Visual Depth Techniques

1. **Opacity layering:** Background shapes at 0.1-0.2, foreground at 0.5-1.0
2. **Scale cues:** Larger = closer, smaller = farther
3. **Parallax:** Separate layers move at different speeds
4. **Overlap:** Elements partially obscure each other
5. **Blur:** Background elements can have subtle blur (optional)

---

## Motion Quality

### Easing Philosophy

| Easing | Emotion | Use Case |
|--------|---------|----------|
| `power3.out` | Gentle arrival | Hero reveals, content fade-in |
| `power2.inOut` | Smooth transition | State changes, toggles |
| `back.out(1.7)` | Playful pop | Scale reveals |
| `power1.inOut` | Meditative | Float animations |
| `none` | Constant | Loops, rotation |

### Stagger Principles

```
Words:        0.08 - 0.1 per word
Paths:        0.15 - 0.2 per path
Cards:        0.2 per card
Sections:     0.3 - 0.5 per section
```

**Rule:** Smaller increments = more elegance. Large staggers feel disjointed.

### Duration Standards

```
Micro:    0.3 - 0.5s (hover states)
Short:    0.8 - 1s (fade-ins)
Medium:   1 - 1.5s (draw animations)
Long:     2s+ (slow reveals, transitions)
```

---

## Cohesion Devices

### Custom Cursor
**Purpose:** Creates subtle connection between user and content
**Style:** Minimal ring + dot, `mix-blend-mode: difference`
**Motion:** Smooth lerp (0.15-0.4 factor)

### Progress Bar
**Purpose:** Orient user in content flow
**Style:** 3px fixed top, gradient fill
**Motion:** Scrub-linked to scroll position

### Chapter Numbers
**Purpose:** Visual rhythm, section markers
**Style:** Large, low opacity (0.15), serif font
**Position:** Top-left absolute

### Scroll Indicator
**Purpose:** Initial cue for scroll interaction
**Style:** Minimal line + text label
**Animation:** Subtle bounce (10px, 1s ease-in-out)

---

## SVG Design Rules

### Organic Shapes Only

**Allowed:**
- `<path>` elements with Bézier curves (Q, C commands)
- Organic blobs, asymmetric shapes
- Hand-drawn feel curves

**Prohibited:**
- Perfect circles (use `<path>` approximation instead)
- Rectangles with sharp corners
- Straight lines (use slight curves)
- Strokes on main shapes

### Path Construction

```svg
<!-- Good: Organic multi-point path -->
<path d="M250 150 Q300 120 350 160 Q400 220 360 300 Q300 380 250 360..."/>

<!-- Avoid: Geometric primitives -->
<circle cx="250" cy="250" r="100"/>
<rect x="100" y="100" width="200" height="200"/>
```

### Fill Application

```css
/* Use CSS variables, never hardcoded colors */
fill: var(--light);  /* or var(--dark) */

/* Add opacity for depth */
fill: var(--dark);
opacity: 0.4;
```

### Animation Classes

```
.organic-path     - Base class for all SVG paths
.fade-path        - Elements that fade in
.scale-path       - Elements that scale up
.draw-path        - Elements that stroke-draw
```

---

## Section Design Patterns

### Hero
- **Purpose:** Establish mood, invite engagement
- **Elements:** Title, subtitle, scroll indicator, optional lamp/spotlight
- **Animation:** Staggered word reveal
- **Duration:** Full viewport height

### Chapters
- **Purpose:** Deliver narrative content
- **Layout:** Grid (content + illustration)
- **Variation:** Alternate left/right or light/dark
- **Transition:** Fade-in on scroll

### Quote
- **Purpose:** Emotional resonance, thematic emphasis
- **Style:** Large serif, centered, minimal
- **Placement:** Between chapters or before finale
- **Animation:** Simple fade from below

### Finale
- **Purpose:** Resolution, key takeaway
- **Elements:** Concentric symbol, title, summary text
- **Animation:** Coordinated reveal
- **Duration:** Full viewport height

---

## Responsive Considerations

### Breakpoint Strategy

Use `clamp()` instead of media queries where possible:
```css
font-size: clamp(2rem, 5vw, 3.5rem); /* No breakpoints needed */
```

### Grid Adaptation

```css
/* Mobile first */
.chapter-inner {
  grid-template-columns: 1fr;
  gap: 60px;
}

/* Desktop */
@media (min-width: 769px) {
  .chapter-inner {
    grid-template-columns: 1fr 1fr;
  }
}
```

### Touch Considerations

- **Disable custom cursor** on touch devices
- **Larger tap targets** for interactive elements
- **Simpler animations** for mobile performance
- **Reduced motion** respects user preferences

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Accessibility

### Contrast Requirements

- Body text: Minimum 4.5:1 contrast ratio
- Large text (18pt+): Minimum 3:1 contrast ratio
- All duotone palettes are WCAG AA compliant

### Semantic HTML

```html
<section aria-labelledby="chapter-title">
  <h2 id="chapter-title">Chapter Title</h2>
  <p>Description</p>
</section>
```

### Motion Preferences

Always respect `prefers-reduced-motion`:
```css
@media (prefers-reduced-motion: reduce) {
  /* Disable or simplify all animations */
}
```

---

## Anti-Patterns

### Avoid These

1. **Rainbow colors** - Breaks duotone constraint
2. **Geometric SVG shapes** - Violates organic design language
3. **Strokes on fills** - Creates busy visual noise
4. **Hard shadows** - Use opacity for depth instead
5. **Janky animations** - Use proper easing/stagger
6. **Overlapping text** - Insufficient reading space
7. **Inconsistent spacing** - Follow rhythm system
8. **Too many fonts** - Stick to Instrument Serif + Inter
