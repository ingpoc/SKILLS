# Organic SVG Templates

Hand-drawn Bézier path patterns for Anthropic-style illustrations. All paths use only `#FAF9F5` (cream) and `#141413` (charcoal).

## Design Rules

| Rule | Implementation |
|------|----------------|
| **Fills only** | Use `fill`, never `stroke` for main shapes |
| **Organic curves** | Quadratic (Q) and Cubic (C) Bézier, not geometric |
| **Duotone** | Only `#FAF9F5` and `#141413` |
| **Layered** | Light shapes first, dark shapes on top |
| **Opacity** | Use 0.3-0.6 for depth, never below 0.2 |

## Desk Lamp (Hero)

Table lamp with light cone for hero sections:

```xml
<div class="lamp-container">
  <svg class="lamp-svg" viewBox="0 0 200 300" fill="none">
    <!-- Base shadow -->
    <ellipse cx="100" cy="280" rx="50" ry="12" fill="#FAF9F5" opacity="0.1"/>
    <!-- Base -->
    <path d="M70 280 L75 260 L125 260 L130 280 Z" fill="#FAF9F5"/>
    <!-- Arm -->
    <path d="M100 260 L100 180 Q100 160 85 150 L60 130"
          stroke="#FAF9F5" stroke-width="4" fill="none" stroke-linecap="round"/>
    <!-- Head -->
    <path d="M30 140 Q60 110 90 130 L60 160 Q40 150 30 140 Z" fill="#FAF9F5"/>
    <!-- Bulb glow -->
    <ellipse cx="55" cy="145" rx="8" ry="5" fill="#FAF9F5" opacity="0.6"/>
  </svg>
  <div class="light-cone"></div>
</div>
```

## Central Hub (Orchestration/Focus)

Organic shape representing central control:

```xml
<svg viewBox="0 0 500 500" fill="none">
  <!-- Main hub shape -->
  <path class="organic-path" fill="#FAF9F5"
    d="M200 250 Q180 200 220 180 Q260 160 300 180 Q340 200 320 250
       Q300 300 260 320 Q220 340 180 300 Q160 280 200 250 Z"/>

  <!-- Satellite nodes -->
  <path class="organic-path" fill="#FAF9F5" opacity="0.4"
    d="M120 150 Q160 120 200 140 Q180 180 140 190 Q100 200 120 150 Z"/>
  <path class="organic-path" fill="#FAF9F5" opacity="0.4"
    d="M380 150 Q340 120 300 140 Q320 180 360 190 Q400 200 380 150 Z"/>
  <path class="organic-path" fill="#FAF9F5" opacity="0.4"
    d="M120 350 Q160 380 200 360 Q180 320 140 310 Q100 300 120 350 Z"/>
  <path class="organic-path" fill="#FAF9F5" opacity="0.4"
    d="M380 350 Q340 380 300 360 Q320 320 360 310 Q400 300 380 350 Z"/>

  <!-- Central eye -->
  <ellipse class="organic-path" cx="250" cy="250" rx="30" ry="20" fill="#141413"/>
  <circle class="organic-path" cx="250" cy="250" r="8" fill="#FAF9F5"/>
</svg>
```

## Organic Blob (Abstract Concept)

Flowing shape for abstract ideas:

```xml
<svg viewBox="0 0 500 500" fill="none">
  <!-- Main blob -->
  <path class="organic-path" fill="#141413"
    d="M250 150 Q300 120 350 160 Q400 220 360 300
       Q300 380 250 360 Q180 340 160 280
       Q140 200 200 150 Q230 130 250 150 Z"/>

  <!-- Accent blob -->
  <path class="organic-path" fill="#141413" opacity="0.3"
    d="M200 100 Q230 80 260 100 Q280 130 250 150 Q220 140 200 100 Z"/>
</svg>
```

## Gateway Arches (Enforcement/Filter)

Cascading arches representing filtering or gates:

```xml
<svg viewBox="0 0 500 500" fill="none">
  <!-- Outer arch -->
  <path class="organic-path" fill="#141413"
    d="M100 400 Q150 300 250 280 Q350 300 400 400
       L380 400 Q340 320 250 300 Q160 320 120 400 Z"/>

  <!-- Middle arch -->
  <path class="organic-path" fill="#141413" opacity="0.6"
    d="M130 380 Q170 300 250 285 Q330 300 370 380
       L350 380 Q320 320 250 305 Q180 320 150 380 Z"/>

  <!-- Inner arch -->
  <path class="organic-path" fill="#141413" opacity="0.3"
    d="M160 360 Q190 300 250 290 Q310 300 340 360
       L320 360 Q300 320 250 310 Q200 320 180 360 Z"/>

  <!-- Lock symbol -->
  <rect class="organic-path" x="225" y="180" width="50" height="40" rx="5" fill="#141413"/>
  <path class="organic-path" fill="none" stroke="#141413" stroke-width="8"
    d="M235 180 L235 160 Q235 140 250 140 Q265 140 265 160 L265 180"/>
</svg>
```

## Knowledge Tree (Growth/Learning)

Organic tree shape for learning or evolution:

```xml
<svg viewBox="0 0 500 500" fill="none">
  <!-- Tree crown -->
  <path class="organic-path" fill="#FAF9F5"
    d="M250 400 L250 280
       Q230 260 210 280 Q190 260 200 230
       Q180 220 190 190 Q170 180 200 160
       Q220 140 250 150 Q280 140 300 160
       Q330 180 310 190 Q320 220 300 230
       Q310 260 290 280 Q270 260 250 280 L250 400 Z"/>

  <!-- Roots -->
  <path class="organic-path" fill="#FAF9F5" opacity="0.4"
    d="M250 400 Q220 420 200 450 Q180 420 160 440"/>
  <path class="organic-path" fill="#FAF9F5" opacity="0.4"
    d="M250 400 Q280 420 300 450 Q320 420 340 440"/>

  <!-- Knowledge nodes -->
  <circle class="organic-path" cx="200" cy="160" r="15" fill="#FAF9F5"/>
  <circle class="organic-path" cx="300" cy="160" r="12" fill="#FAF9F5" opacity="0.8"/>
  <circle class="organic-path" cx="250" cy="120" r="10" fill="#FAF9F5" opacity="0.6"/>
</svg>
```

## Concentric Symbol (Unity/Completion)

Layered organic circles for finale:

```xml
<svg viewBox="0 0 400 400" fill="none">
  <!-- Outer ring -->
  <path class="organic-path" fill="#FAF9F5"
    d="M200 50 Q280 80 320 150 Q360 220 320 290
       Q280 360 200 380 Q120 360 80 290
       Q40 220 80 150 Q120 80 200 50 Z"/>

  <!-- Dark ring -->
  <path class="organic-path" fill="#141413"
    d="M200 80 Q260 100 290 160 Q320 220 290 280
       Q260 340 200 355 Q140 340 110 280
       Q80 220 110 160 Q140 100 200 80 Z"/>

  <!-- Inner light ring -->
  <path class="organic-path" fill="#FAF9F5" opacity="0.8"
    d="M200 120 Q240 135 260 175 Q280 215 260 255
       Q240 295 200 305 Q160 295 140 255
       Q120 215 140 175 Q160 135 200 120 Z"/>

  <!-- Inner dark ring -->
  <path class="organic-path" fill="#141413"
    d="M200 150 Q225 160 240 185 Q255 210 240 235
       Q225 260 200 268 Q175 260 160 235
       Q145 210 160 185 Q175 160 200 150 Z"/>

  <!-- Core -->
  <circle class="organic-path" cx="200" cy="200" r="25" fill="#FAF9F5"/>
  <circle class="organic-path" cx="200" cy="200" r="10" fill="#141413"/>
</svg>
```

## Hand Holding (Trust/Connection)

Abstract hand shape for human themes:

```xml
<svg viewBox="0 0 500 500" fill="none">
  <!-- Palm -->
  <path class="organic-path" fill="#FAF9F5"
    d="M250 180 Q280 160 310 180 Q340 200 330 240
       Q320 280 280 300 Q240 320 200 300
       Q160 280 170 240 Q180 200 220 180 Q235 170 250 180 Z"/>

  <!-- Fingers extending -->
  <path class="organic-path" fill="#FAF9F5" opacity="0.5"
    d="M250 120 Q260 100 280 110 Q300 120 290 140
       Q280 160 260 150 Q240 140 250 120 Z"/>
  <path class="organic-path" fill="#FAF9F5" opacity="0.5"
    d="M350 200 Q380 190 390 210 Q400 240 380 250
       Q360 260 350 240 Q340 220 350 200 Z"/>
  <path class="organic-path" fill="#FAF9F5" opacity="0.5"
    d="M150 200 Q120 190 110 210 Q100 240 120 250
       Q140 260 150 240 Q160 220 150 200 Z"/>

  <!-- Object being held -->
  <path class="organic-path" fill="#141413"
    d="M240 220 Q250 210 260 220 L270 250
       Q260 260 250 260 Q240 260 230 250 L240 220 Z"/>
</svg>
```

## Creating Your Own

### Step 1: Start with a simple shape

```xml
<path d="M250 200 Q300 150 350 200 Q300 250 250 200 Z"/>
```

### Step 2: Add organic variation

- Offset control points slightly
- Avoid perfect symmetry
- Use curves, not straight lines

### Step 3: Layer for depth

```xml
<!-- Background shape (lighter/transparent) -->
<path fill="#FAF9F5" opacity="0.4" d="..."/>

<!-- Main shape -->
<path fill="#FAF9F5" d="..."/>

<!-- Foreground detail (if on light bg, use #141413) -->
<path fill="#141413" d="..."/>
```

### Step 4: Add the `organic-path` class

For scroll-triggered stagger animation:

```xml
<path class="organic-path" fill="..." d="..."/>
```

## Color Reference

| Context | Fill Color |
|---------|------------|
| Dark background sections | `#FAF9F5` |
| Light background sections | `#141413` |
| Opacity for depth | 0.3 - 0.6 |
| Never below | 0.2 |
