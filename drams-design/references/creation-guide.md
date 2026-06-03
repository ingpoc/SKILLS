# DRAMS Component Creation Guide

Framework for creating NEW components following Dieter Rams' "less, but better" philosophy.

---

## Creation Workflow

```
1. Define Purpose → 2. Apply Rams' 10 Principles → 3. Use Design Tokens → 4. Add Interactions → 5. Validate
```

---

## Step 1: Define Purpose (Useful + Understandable)

Before writing code, answer:

| Question | Answer Example |
|----------|----------------|
| What problem does it solve? | User needs to select multiple items from a list |
| What's the primary action? | Toggle items on/off |
| What are the states? | Default, hover, active, disabled, focus |
| What feedback is needed? | Visual state change + optional haptic |

**Template:**

```markdown
## [Component Name]

**Purpose:** [One sentence describing the problem it solves]

**Primary Action:** [What user does]

**States:** [List all states]

**Feedback:** [What user sees/feels]
```

---

## Step 2: Apply Rams' 10 Principles

Use this checklist for each new component:

| Principle | Questions | Implementation |
|-----------|-----------|----------------|
| **Innovative** | Is this a fresh interaction or improved pattern? | New animations, gestures, or combinations |
| **Useful** | Does it solve a real problem? | Remove if no clear purpose |
| **Aesthetic** | Is it minimal + timeless? | Neutral palette, generous whitespace, 48px radius |
| **Understandable** | Is it self-evident? | Icon + text, clear affordances |
| **Unobtrusive** | Does it stay back until needed? | Subtle animations, no jarring movements |
| **Honest** | Are states accurate? | Real loading times, true constraints |
| **Long-lasting** | Will it age well? | Stable tech stack, timeless visual |
| **Thorough** | Are edge cases handled? | Empty, error, loading, disabled states |
| **Environmentally** | Is it lightweight? | Minimal code, tree-shakeable |
| **Little design** | Can anything be removed? | Delete until removal breaks |

---

## Step 3: Use Design Tokens

### Color Selection

| Usage | Token |
|-------|-------|
| Primary action | `rgb(255, 97, 26)` |
| Secondary action | `rgb(238, 238, 238)` |
| Hover state | `rgb(232, 232, 232)` |
| Text primary | `#333` |
| Text secondary | `#999` |
| Focus indicator | `rgb(255, 97, 26)` (2px solid) |

### Shape System

| Element | Border Radius |
|---------|---------------|
| Pills, tracks | 48px |
| Circles, balls | 50% |
| Cards, menus | 16-20px |
| Small elements | 8px |

### Spacing

```css
/* Scale: 4, 8, 12, 16, 20, 24, 32px */
gap: 12px;        /* Between related items */
padding: 0 20px;  /* Horizontal padding */
margin-bottom: 8px; /* Vertical spacing */
```

### Animation

```css
/* Primary easing */
transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);

/* Hover (faster) */
transition: background 0.2s ease;

/* 3D transforms (slower) */
transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
```

---

## Step 4: Add Interactions

### State Pattern

```css
/* 1. Base State */
.component { }

/* 2. Hover State */
.component:hover { }

/* 3. Active/Selected State */
.component.active { }

/* 4. Focus State */
.component:focus-visible {
  outline: 2px solid rgb(255, 97, 26);
  outline-offset: 2px;
}

/* 5. Disabled State */
.component:disabled {
  opacity: 0.5;
  pointer-events: none;
}
```

### Microinteraction Guidelines

| Interaction | Duration | Easing | Scale |
|-------------|----------|--------|-------|
| Hover/focus | 0.2s | ease | 1.05 |
| Click/tap | 0.1s | ease-out | 0.95 |
| Slide/expand | 0.4s | cubic-bezier(0.16, 1, 0.3, 1) | N/A |
| Flip/rotate | 0.6s | cubic-bezier(0.4, 0, 0.2, 1) | N/A |

---

## Step 5: Validate

Run the validation script:

```bash
bash ~/.claude/skills/drams-design/scripts/validate-drams.sh your-component.html --strict
```

---

## Component Patterns by Type

### Form Components

**Pattern:** Gray track expands/fills with orange

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

**Examples:** Input, Select, Toggle, Slider

### Action Components

**Pattern:** Orange ball or gradient on hover/click

```css
.action {
  background: radial-gradient(
    50% 50% at 30% 30%,
    rgb(255, 150, 102) 0%,
    rgb(255, 97, 26) 100%
  );
  box-shadow:
    rgba(232, 61, 23, 0.4) 0px 0px 2px -1px inset,
    0 2px 8px rgba(255, 97, 26, 0.3);
}
```

**Examples:** Button, Add to cart, FAB

### Display Components

**Pattern:** White card, subtle shadow, lift on hover

```css
.card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}
```

**Examples:** Product card, Stat card, Info card

### Navigation Components

**Pattern:** Gray pill, orange when active

```css
.nav-item {
  padding: 12px 18px;
  background: rgb(238, 238, 238);
  border-radius: 48px;
}

.nav-item.active {
  background: rgb(255, 97, 26);
  color: white;
}
```

**Examples:** Tab, Radio group, Pill nav

---

## Accessibility Requirements

Every component MUST have:

1. **Keyboard Navigation**
   - Tab: Navigate to/through
   - Enter/Space: Activate
   - Escape: Close/dismiss
   - Arrows: Navigate within

2. **ARIA Attributes**

   ```html
   role="button"
   aria-label="Add to cart"
   aria-pressed="false"
   aria-expanded="false"
   ```

3. **Focus Indicator**

   ```css
   :focus-visible {
     outline: 2px solid rgb(255, 97, 26);
     outline-offset: 2px;
   }
   ```

4. **Touch Targets**
   - Minimum 44x44px
   - Prefer 48px for primary actions

5. **Color Contrast**
   - Text: ≥ 4.5:1
   - Large text: ≥ 3:1
   - UI components: ≥ 3:1

---

## Example: Creating a "Chip" Component

### 1. Define Purpose

User needs to filter by category with removable chips.

### 2. Apply Rams

| Principle | Application |
|-----------|-------------|
| Little design | Just text + X, no border |
| Understandable | X icon clearly indicates removal |
| Unobtrusive | Subtle gray background |
| Aesthetic | Matches DRAMS color tokens |

### 3. Design Tokens

```css
.chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgb(238, 238, 238);
  border-radius: 48px;
  font-size: 14px;
  color: #333;
}

.chip-remove {
  width: 16px;
  height: 16px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.chip-remove:hover { opacity: 1; }
```

### 4. Result

A minimal, self-evident chip component that follows all DRAMS principles.

---

## Quick Reference Sheet

```
┌─────────────────────────────────────────────────────────────┐
│                    DRAMS CREATION CHEAT SHEET                │
├─────────────────────────────────────────────────────────────┤
│  COLORS:  rgb(255,97,26) orange | rgb(238,238,238) track   │
│  RADIUS:  48px pill | 50% circle | 20px card                │
│  EASING:  cubic-bezier(0.16, 1, 0.3, 1)                     │
│  DURATION:  0.2s hover | 0.3s standard | 0.6s 3D            │
├─────────────────────────────────────────────────────────────┤
│  FORMS:  Gray track → focus with shadow                     │
│  ACTIONS:  Orange gradient ball                             │
│  CARDS:  White + subtle shadow → lift on hover              │
│  NAV:    Gray pill → orange when active                     │
├─────────────────────────────────────────────────────────────┤
│  A11Y:   Keyboard, ARIA, focus-visible, 44px min tap       │
│  RAMS:   Delete until removal breaks                        │
└─────────────────────────────────────────────────────────────┘
```
