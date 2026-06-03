# DRAMS Design Tokens

Complete design system specifications extracted from rolling-search.html reference implementation.

---

## Colors

### Primary

| Token | Value | Usage |
|-------|-------|-------|
| `--color-orange-primary` | `rgb(255, 97, 26)` | Accents, actions, active states |
| `--color-orange-highlight` | `rgb(255, 150, 102)` | Gradient light (30%) |
| `--color-orange-dark` | `rgb(232, 61, 23)` | Inner shadows |

### Neutral

| Token | Value | Usage |
|-------|-------|-------|
| `--color-gray-track` | `rgb(238, 238, 238)` | Inactive backgrounds |
| `--color-gray-hover` | `rgb(232, 232, 232)` | Hover states |
| `--color-gray-dark` | `rgb(230, 230, 230)` | Focus states |
| `--color-text-primary` | `#333` | Primary text |
| `--color-text-secondary` | `#999` | Secondary text, placeholders |
| `--color-text-muted` | `#666` | Tertiary text |
| `--color-white` | `rgb(252, 252, 250)` | Off-white (icons) |
| `--color-pure-white` | `#fff` | Backgrounds |

### Semantic

| Token | Value | Usage |
|-------|-------|-------|
| `--color-success` | `rgb(255, 97, 26)` | Active states (reuse orange) |
| `--color-error` | `rgb(220, 38, 38)` | Error states |
| `--color-border` | `rgba(0,0,0,0.06)` | Subtle borders |

---

## Spacing

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | 4px | Tight spacing |
| `--space-sm` | 8px | Small gaps |
| `--space-md` | 12px | Medium gaps |
| `--space-lg` | 16px | Section padding |
| `--space-xl` | 20px | Component padding |
| `--space-2xl` | 24px | Large padding |
| `--space-3xl` | 32px | Section headers |

### Layout Spacing

| Token | Value | Usage |
|-------|-------|-------|
| `--gap-logo-nav` | 48px | Space between logo and nav |
| `--gap-section` | 48px | Section vertical spacing |

### Container Widths

| Token | Value | Usage |
|-------|-------|-------|
| `--container-narrow` | 800px | Reading content |
| `--container-standard` | 1024px | Standard pages |
| `--container-wide` | 1200px | Dashboards |

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-pill` | 48px | Pills, tracks, inputs |
| `--radius-circle` | 50% | Balls, circles |
| `--radius-card` | 16-20px | Cards, menus |
| `--radius-sm` | 8px | Small elements |

---

## Typography

| Token | Value | Usage |
|-------|-------|-------|
| `--font-family` | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` | System font stack |
| `--font-size-xs` | 11px | Labels, badges |
| `--font-size-sm` | 13px | Meta text |
| `--font-size-base` | 14-15px | Body text |
| `--font-size-md` | 16px | Inputs, titles |
| `--font-size-lg` | 18px | Card titles |
| `--font-size-xl` | 20px | Prices |
| `--font-size-2xl` | 28px | Time display |
| `--font-size-hero` | 32px | Page titles |
| `--font-weight-light` | 300 | Time display |
| `--font-weight-normal` | 400/500 | Body text |
| `--font-weight-semibold` | 500 | Labels |
| `--font-weight-bold` | 600 | Prices |
| `--letter-spacing-tight` | -0.5px | Hero text |
| `--letter-spacing-wide` | 0.5-1px | Uppercase labels |

### Display Typography

| Token | Value | Usage |
|-------|-------|-------|
| `--font-logo` | 'Sacramento', cursive | Logo text |
| `--font-size-logo` | 36px | Logo display |
| `--font-size-logo-sub` | 12px | Logo subtitle |

---

## Shadows

### Elevation

| Level | CSS | Usage |
|-------|-----|-------|
| Subtle | `0 2px 8px rgba(0,0,0,0.04)` | Component sections |
| Card | `0 4px 16px rgba(0,0,0,0.06)` | Product cards |
| Hover | `0 8px 24px rgba(0,0,0,0.1)` | Card hover |
| Menu | `0 8px 32px rgba(0,0,0,0.1)` | Dropdown menus |
| Focus | `0 4px 12px rgba(0,0,0,0.08)` | Input focus |
| Orange | `0 2px 8px rgba(255, 97, 26, 0.3)` | Orange elements |

### Multi-layer (Orange Ball)

```css
box-shadow:
  rgba(232, 61, 23, 0.35) 0px 0px 0px -0.75px inset,
  rgba(232, 61, 23, 0.7) 0px 0px 0px -1.5px inset,
  rgba(0, 0, 0, 0.25) -2px -1px 4px 0px inset,
  rgba(204, 44, 16, 0.455) -0.66px -0.06px 0.53px -0.75px inset,
  rgba(204, 44, 16, 0.475) -2.52px -0.23px 2.02px -1.5px inset,
  rgba(204, 44, 16, 0.55) -11px -1px 8.84px -2.25px inset;
```

---

## Animation

### Easing Functions

| Token | Value | Usage |
|-------|-------|-------|
| `--ease-out-expo` | `cubic-bezier(0.16, 1, 0.3, 1)` | Primary easing |
| `--ease-out-back` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Bouncy effects |
| `--ease-smooth` | `ease` | Standard transitions |
| `--ease-in-out` | `ease-in-out` | Bidirectional |

### Durations

| Token | Value | Usage |
|-------|-------|-------|
| `--duration-instant` | 0.2s | Hover, icon changes |
| `--duration-fast` | 0.3s | Standard transitions |
| `--duration-base` | 0.4s | Expanding, sliding |
| `--duration-slow` | 0.6s | 3D transforms (flip) |

---

## Gradients

### Orange Ball

```css
background: radial-gradient(
  50% 50% at 29.1% 29.7%,
  rgb(255, 150, 102) 0%,
  rgb(255, 97, 26) 100%
);
```

### Product Image Placeholder

```css
background: linear-gradient(135deg, #f5f5f5 0%, #ebebeb 100%);
```

---

## Sizes

### Touch Targets

| Element | Size |
|---------|------|
| Buttons | 40-44px |
| Orange ball | 42px |
| Toggle | 56x32px |
| Radio pill | 48px height |

### Component Widths

| Component | Width |
|-----------|-------|
| Rolling search (collapsed) | 234px |
| Rolling search (expanded) | 234px |
| Time unit | 80px |
| Select value | 60px |
| Input padding | 0 20px |

---

## Z-Index Scale

| Level | Value | Usage |
|-------|-------|-------|
| Base | 1 | Normal content |
| Dropdown | 10 | Menus, overlays |
| Modal | 100 | Modals |
| Toast | 200 | Notifications |

---

## Breakpoints

| Name | Min Width | Usage |
|------|-----------|-------|
| Mobile | - | Base styles |
| Tablet | 768px | `md:` prefix |
| Desktop | 1024px | `lg:` prefix |
| Wide | 1200px | `xl:` prefix |

---

## Container Patterns

```css
.container-narrow { max-width: 800px; margin: 0 auto; padding: 0 24px; }
.container-wide { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
```

---

## CSS Variables (Root)

```css
:root {
  /* Colors */
  --color-orange-primary: rgb(255, 97, 26);
  --color-orange-highlight: rgb(255, 150, 102);
  --color-orange-dark: rgb(232, 61, 23);
  --color-gray-track: rgb(238, 238, 238);
  --color-gray-hover: rgb(232, 232, 232);
  --color-gray-dark: rgb(230, 230, 230);
  --color-text-primary: #333;
  --color-text-secondary: #999;
  --color-text-muted: #666;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 12px;
  --space-lg: 16px;
  --space-xl: 20px;

  /* Border Radius */
  --radius-pill: 48px;
  --radius-circle: 50%;
  --radius-card: 20px;

  /* Animation */
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --duration-fast: 0.3s;
  --duration-base: 0.4s;
}
```
