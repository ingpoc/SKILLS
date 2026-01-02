# SVG Pattern Templates

## Standard Setup

```tsx
<svg viewBox="0 0 500 500" className="w-full h-full">
  <!-- Paths go here -->
</svg>
```

**Rules:**

- Always `viewBox="0 0 500 500"`
- Keep coordinates within 0-500 range
- Use semantic path classes: `.fill-path`, `.draw-path`, `.label-path`

## Path Classes

| Class | Purpose | Fill | Stroke |
|-------|---------|------|--------|
| `.fill-path` | Shapes, filled elements | cream/charcoal | none |
| `.draw-path` | Lines, connectors | none | cream/charcoal |
| `.label-path` | Text labels | none | none |

## Chapter 1: Person + Context

Introductory figure with surrounding elements.

```tsx
<svg viewBox="0 0 500 500">
  {/* Person - center figure */}
  <circle className="fill-path" cx="250" cy="140" r="35"
          fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>
  <path className="fill-path"
        d="M 215 180 Q 200 220 210 280 L 210 320 Q 210 340 230 340 L 270 340 Q 290 340 290 320 L 290 280 Q 300 220 285 180 Z"
        fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>

  {/* Surrounding elements */}
  <circle className="draw-path" cx="150" cy="200" r="25"
          fill="none" stroke={isLight ? '#141413' : '#FAF9F5'}
          strokeWidth="2" opacity="0"/>
  <circle className="draw-path" cx="350" cy="200" r="25"
          fill="none" stroke={isLight ? '#141413' : '#FAF9F5'}
          strokeWidth="2" opacity="0"/>

  {/* Labels */}
  <text className="label-path" x="150" y="250" fill={isLight ? '#141413' : '#FAF9F5'}>
    Attribute
  </text>
</svg>
```

## Chapter 2: Horizontal Flow

Left-to-right process with connecting lines.

```tsx
<svg viewBox="0 0 500 500">
  {/* Step 1 - left */}
  <rect className="fill-path" x="60" y="200" width="80" height="60" rx="8"
        fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>

  {/* Step 2 - middle */}
  <rect className="fill-path" x="210" y="200" width="80" height="60" rx="8"
        fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>

  {/* Step 3 - right */}
  <rect className="fill-path" x="360" y="200" width="80" height="60" rx="8"
        fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>

  {/* Connecting lines */}
  <path className="draw-path" d="M 140 230 L 210 230"
        stroke={isLight ? '#141413' : '#FAF9F5'}
        strokeWidth="2" opacity="0"/>
  <path className="draw-path" d="M 290 230 L 360 230"
        stroke={isLight ? '#141413' : '#FAF9F5'}
        strokeWidth="2" opacity="0"/>
</svg>
```

## Chapter 3: Growth Trajectory

Upward curve with milestone points.

```tsx
<svg viewBox="0 0 500 500">
  {/* Growth curve */}
  <path className="draw-path"
        d="M 50 420 Q 120 400 160 350 T 280 250 T 400 150 T 450 80"
        stroke={isLight ? '#141413' : '#FAF9F5'}
        strokeWidth="3" opacity="0"/>

  {/* Milestone points */}
  <circle className="fill-path" cx="160" cy="350" r="10"
          fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>
  <circle className="fill-path" cx="280" cy="250" r="10"
          fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>
  <circle className="fill-path" cx="400" cy="150" r="10"
          fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>
</svg>
```

## Chapter 4: Central Hub

Center element with radiating connections.

```tsx
<svg viewBox="0 0 500 500">
  {/* Outer ring */}
  <circle className="draw-path" cx="250" cy="250" r="120"
          fill="none" stroke={isLight ? '#141413' : '#FAF9F5'}
          strokeWidth="2" opacity="0"/>

  {/* Inner ring */}
  <circle className="draw-path" cx="250" cy="250" r="80"
          fill="none" stroke={isLight ? '#141413' : '#FAF9F5'}
          strokeWidth="2" opacity="0"/>

  {/* Center hub */}
  <circle className="fill-path" cx="250" cy="250" r="45"
          fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>

  {/* Satellite nodes */}
  <circle className="fill-path" cx="250" cy="130" r="20"
          fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>
  <circle className="fill-path" cx="370" cy="250" r="20"
          fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>
  <circle className="fill-path" cx="250" cy="370" r="20"
          fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>
  <circle className="fill-path" cx="130" cy="250" r="20"
          fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>
</svg>
```

## Finale: Concentric Symbol

Centered symbolic conclusion.

```tsx
<svg viewBox="0 0 500 500">
  {/* Outer ring */}
  <circle className="draw-path" cx="250" cy="250" r="150"
          fill="none" stroke={isLight ? '#141413' : '#FAF9F5'}
          strokeWidth="2" opacity="0"/>

  {/* Middle ring */}
  <circle className="draw-path" cx="250" cy="250" r="100"
          fill="none" stroke={isLight ? '#141413' : '#FAF9F5'}
          strokeWidth="2" opacity="0"/>

  {/* Inner core */}
  <circle className="fill-path" cx="250" cy="250" r="60"
          fill={isLight ? '#141413' : '#FAF9F5'} opacity="0"/>

  {/* Radiating lines */}
  <path className="draw-path" d="M 250 100 L 250 150"
        stroke={isLight ? '#141413' : '#FAF9F5'}
        strokeWidth="2" opacity="0"/>
  <path className="draw-path" d="M 250 350 L 250 400"
        stroke={isLight ? '#141413' : '#FAF9F5'}
        strokeWidth="2" opacity="0"/>
  <path className="draw-path" d="M 100 250 L 150 250"
        stroke={isLight ? '#141413' : '#FAF9F5'}
        strokeWidth="2" opacity="0"/>
  <path className="draw-path" d="M 350 250 L 400 250"
        stroke={isLight ? '#141413' : '#FAF9F5'}
        strokeWidth="2" opacity="0"/>
</svg>
```

## Color Selection by Section

```tsx
const isLight = number % 2 === 1; // Odd chapters = light
const fillColor = isLight ? '#141413' : '#FAF9F5';  // charcoal on light, cream on dark
```
