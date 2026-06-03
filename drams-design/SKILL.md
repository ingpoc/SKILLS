---
name: drams-design
description: "Use when designing UI components, building layouts, creating page structures, or developing design systems following Dieter Rams' principles. Load for any task involving buttons, sliders, cards, forms, inputs, menus, headers, navigation, hero sections, grids, responsive layouts, page templates, tabs, toasts, modals, alerts, loading states, or UI/layout elements that need to be innovative, useful, aesthetic, understandable, unobtrusive, honest, long-lasting, thorough, environmentally friendly, or embody 'less but better' design philosophy."
license: MIT
version: "2.0.1"
context: fork
agent: general-purpose
---

# DRAMS Design Skill

Dieter Rams-inspired UI components following "less, but better" philosophy.

**Use this skill to:**

- Generate existing components from templates
- Create NEW components using DRAMS principles
- Validate components against Rams' 10 principles

---

## Quick Start

### Use Existing Components

```bash
# List available components
bash ~/.claude/skills/drams-design/scripts/list-components.sh --detailed

# Generate a component (vanilla HTML)
bash ~/.claude/skills/drams-design/scripts/generate-component.sh rolling-search ./src

# Generate a React component
bash ~/.claude/skills/drams-design/scripts/generate-component.sh product-card ./src --react
```

### Create New Components

```bash
# Read the creation guide
cat ~/.claude/skills/drams-design/references/creation-guide.md

# Validate your new component
bash ~/.claude/skills/drams-design/scripts/validate-drams.sh your-component.html --strict
```

---

## Design Tokens

| Category | Value | Usage |
|----------|-------|-------|
| Primary orange | `rgb(255, 97, 26)` | Accents, actions, active states |
| Orange highlight | `rgb(255, 150, 102)` | Gradient at 30% position |
| Gray track | `rgb(238, 238, 238)` | Backgrounds, inactive states |
| Gray hover | `rgb(232, 232, 232)` | Interactive states |
| Text dark | `#333` | Primary text |
| Text light | `#999` | Secondary text |
| Border radius | 48px, 50%, 16-20px | Pills, circles, cards |
| Easing | `cubic-bezier(0.16, 1, 0.3, 1)` | Primary animations |
| Duration | 0.3s - 0.4s | Standard transitions |

---

## Layout Patterns

### Page Structure

| Element | Max Width | Padding | Notes |
|---------|-----------|---------|-------|
| Header container | 1200px | 24px | Sticky positioning |
| Main content | 800px | 24px | Centered |
| Card container | - | 24px | Full width with padding |

### Sticky Header

Logo left (Sacramento 36px), pill navigation right.

```tsx
<header style={{ position: 'sticky', top: 0, zIndex: 50, borderBottom: '1px solid rgb(238,238,238)' }}>
  <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px', display: 'flex', justifyContent: 'space-between', gap: '48px' }}>
    <Link href="/"><h1 className="font-sacramento" style={{ fontSize: '36px' }}>flatwatch</h1></Link>
    <nav style={{ display: 'flex', gap: '8px' }}>{/* Pill nav */}</nav>
  </div>
</header>
```

### Pill Navigation

Gray pills (`rgb(238,238,238)`), orange when active (`rgb(255,97,26)`).

```tsx
<Link href="/page" className={`
  h-10 px-4 rounded-full font-medium text-sm
  ${isActive ? 'bg-[rgb(255,97,26)] text-white shadow-[0_2px_8px_rgba(255,97,26,0.3)]' : 'bg-[rgb(238,238,238)] text-[#333] hover:bg-[rgb(232,232,232)]'}
`}>Label</Link>
```

### Hero Section

Centered content with DRAMS card.

```tsx
<div className="min-h-screen flex items-center justify-center">
  <main className="max-w-2xl flex-col items-center gap-12 text-center">
    <h1 className="text-4xl sm:text-5xl font-semibold tracking-tight">Title</h1>
  </main>
</div>
```

### DRAMS Card

White, subtle shadow, lifts on hover.

```css
background: white; border-radius: 24px; padding: 32px;
box-shadow: 0 4px 16px rgba(0,0,0,0.06);
transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
/* Hover: box-shadow: 0 8px 24px rgba(0,0,0,0.1); transform: translateY(-4px); */
```

### Card Grids

Responsive: 1 col (mobile) → 2 col (tablet 768px) → 3 col (desktop 1024px).

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
```

---

## Responsive Design

### Breakpoints

| Name | Min Width | Prefix |
|------|-----------|--------|
| Mobile | - | (base) |
| Tablet | 768px | `md:` |
| Desktop | 1024px | `lg:` |
| Wide | 1200px | `xl:` |

### Mobile-First Approach

Write base styles for mobile, use `md:`/`lg:` for larger screens.

```tsx
<div className="flex-col gap-4 md:flex-row md:gap-8">
```

---

## Available Templates (Updated)

| Component | Type | Description |
|-----------|------|-------------|
| **Layouts** |
| `sticky-header` | Layout | Fixed header with logo + pill nav |
| `pill-navigation` | Layout | Horizontal pill-based navigation |
| `hero-section` | Layout | Centered hero with DRAMS card |
| `card-grid` | Layout | Responsive card grid |
| `drams-card` | Display | White card with hover lift |
| **Forms** |
| `rolling-search` | Form | Expandable search with animated ball |
| `text-box` | Form | Input with focus indicator |
| `dropdown` | Form | Custom select with orange ball |
| `select-box` | Form | Quantity selector with +/- |
| `time-selector` | Form | Circular hours/minutes display |
| `toggle-switch` | Form | Animated on/off slider |
| **Display** |
| `product-card` | Display | Image + details + add button |
| `flip-card` | Display | 3D flip reveal with specs |
| **Navigation** |
| `radio-group` | Nav | Pill-shaped radio options |
| **Actions** |
| `action-button` | Action | Orange gradient button |

---

## Creating New Components

Follow this workflow for ANY new component:

```
1. Define Purpose → 2. Apply Rams' 10 Principles → 3. Use Design Tokens → 4. Add Interactions → 5. Validate
```

### Step 1: Define Purpose

| Question | Example |
|----------|---------|
| What problem does it solve? | User needs to select multiple items |
| What's the primary action? | Toggle items on/off |
| What are the states? | Default, hover, active, disabled |

### Step 2: Apply Rams' 10 Principles

| Principle | Check |
|-----------|-------|
| Innovative | Is this a fresh or improved interaction? |
| Useful | Does it solve a real problem? |
| Aesthetic | Minimal, neutral palette? |
| Understandable | Self-evident without instructions? |
| Unobtrusive | Stays back until needed? |
| Honest | Accurate states, no deception? |
| Long-lasting | Timeless design? |
| Thorough | Edge cases handled? |
| Environmentally | Lightweight code? |
| Little design | Can anything be removed? |

### Step 3: Use Design Tokens

```css
/* Form Pattern: Gray track */
.track {
  background: rgb(238, 238, 238);
  border-radius: 48px;
}

/* Action Pattern: Orange gradient */
.action {
  background: radial-gradient(
    50% 50% at 30% 30%,
    rgb(255, 150, 102) 0%,
    rgb(255, 97, 26) 100%
  );
}

/* Animation Pattern */
transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
```

### Step 4: Add Interactions

```css
/* State Pattern */
.component { }
.component:hover { }
.component.active { }
.component:focus-visible {
  outline: 2px solid rgb(255, 97, 26);
  outline-offset: 2px;
}
```

### Step 5: Validate

```bash
bash ~/.claude/skills/drams-design/scripts/validate-drams.sh component.html --strict
```

**Full creation guide:** `~/.claude/skills/drams-design/references/creation-guide.md`

---

## Available Templates

| Component | Description | Use Case |
|-----------|-------------|----------|
| `rolling-search` | Expandable search with animated ball | Product search, filters |
| `text-box` | Input with focus indicator | Email, name inputs |
| `dropdown` | Custom select with orange ball | Size, color selection |
| `select-box` | Quantity selector with +/- | Product quantity |
| `time-selector` | Circular hours/minutes display | Delivery time, scheduling |
| `toggle-switch` | Animated on/off slider | Settings, preferences |
| `product-card` | Image + details + add button | Product listings |
| `flip-card` | 3D flip reveal with specs | Product details |
| `radio-group` | Pill-shaped radio options | Color, size options |

---

## Component Patterns by Type

### Form Components

Gray track expands/fills with orange on focus.

```css
.track {
  background: rgb(238, 238, 238);
  border-radius: 48px;
}
.track:focus-within {
  background: rgb(230, 230, 230);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
```

### Action Components

Orange gradient ball with inner shadow.

```css
background: radial-gradient(
  50% 50% at 30% 30%,
  rgb(255, 150, 102) 0%,
  rgb(255, 97, 26) 100%
);
box-shadow:
  rgba(232, 61, 23, 0.4) 0px 0px 2px -1px inset,
  0 2px 8px rgba(255, 97, 26, 0.3);
```

### Display Components

White card with subtle shadow, lifts on hover.

```css
.card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}
```

### Navigation Components

Gray pill becomes orange when active.

```css
.nav-item {
  background: rgb(238, 238, 238);
  border-radius: 48px;
}
.nav-item.active {
  background: rgb(255, 97, 26);
  color: white;
}
```

---

## Accessibility Requirements

Every component MUST have:

| Requirement | Implementation |
|-------------|----------------|
| Keyboard nav | Tab, Enter/Space, Escape, Arrows |
| ARIA labels | `role`, `aria-label`, `aria-expanded` |
| Focus indicator | `outline: 2px solid rgb(255, 97, 26)` |
| Touch targets | Minimum 44x44px |
| Color contrast | ≥ 4.5:1 for text |

---

## Reference Docs

| Resource | When to Load |
|----------|-------------|
| `creation-guide.md` | Creating NEW components |
| `design-tokens.md` | Need exact token values |
| `component-catalog.md` | Reference existing components |
| `rams-principles.md` | Deep dive on a principle |

---

## Script Reference

```bash
# List components
bash ~/.claude/skills/drams-design/scripts/list-components.sh --detailed

# Generate existing component
bash ~/.claude/skills/drams-design/scripts/generate-component.sh <component> [output-dir] [--react]

# Validate component (new or existing)
bash ~/.claude/skills/drams-design/scripts/validate-drams.sh <file> [--strict]

# Create showcase page
bash ~/.claude/skills/drams-design/scripts/create-showcase.sh <name> [--components all|<list>]
```

---

## Quick Cheat Sheet

```
┌─────────────────────────────────────────────────────────────┐
│                    DRAMS DESIGN CHEAT SHEET                 │
├─────────────────────────────────────────────────────────────┤
│  COLORS:  rgb(255,97,26) | rgb(238,238,238) | #333 | #999  │
│  RADIUS:  48px pill | 50% circle | 20px card                │
│  EASING:  cubic-bezier(0.16, 1, 0.3, 1)                     │
│  DURATION:  0.2s hover | 0.3s standard | 0.6s 3D            │
├─────────────────────────────────────────────────────────────┤
│  FORMS:    Gray track → focus with shadow                   │
│  ACTIONS:  Orange gradient ball                             │
│  CARDS:    White + shadow → lift on hover                   │
│  NAV:      Gray pill → orange when active                   │
├─────────────────────────────────────────────────────────────┤
│  A11Y:     Keyboard, ARIA, focus-visible, 44px tap target  │
│  RAMS:     Delete until removal breaks                      │
└─────────────────────────────────────────────────────────────┘
```

---

## License

MIT
