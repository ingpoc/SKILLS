# Color Palette Reference

## Core Duotone

```css
:root {
  --cream: #FAF9F5;    /* Light backgrounds, dark text on light sections */
  --charcoal: #141413; /* Dark backgrounds, light text on dark sections */
}
```

## Section Color Mapping

| Section Type | Background | Text | Description |
|--------------|------------|------|-------------|
| Light | `var(--cream)` | `var(--charcoal)` | Hero, Chapters 1, 3 |
| Dark | `var(--charcoal)` | `var(--cream)` | Chapters 2, 4, Finale |

## SVG Fill Colors

| Context | Light Section | Dark Section |
|---------|--------------|--------------|
| Shapes/Fills | `#141413` (charcoal) | `#FAF9F5` (cream) |
| Lines/Strokes | `#141413` (charcoal) | `#FAF9F5` (cream) |
| Labels | `#141413` (charcoal) | `#FAF9F5` (cream) |

## Allowed Accents (Limited Use)

Only for interactive elements - not for primary content:

```css
/* Wallet button only - handled by wallet-adapter */
--primary: #0052A5;       /* Indian blue - for CTAs */
--saffron: #FF9933;      /* Indian saffron - for highlights */
```

**Rule:** Do NOT use accent colors for:

- Section backgrounds
- Body text
- Illustrations
- Borders

## Implementation Example

```tsx
// Correct - using duotone
<section className="bg-[var(--cream)] text-[var(--charcoal)]">
  <h2 style={{ color: 'var(--charcoal)' }}>Title</h2>
</section>

// Incorrect - using arbitrary color
<section className="bg-[#E5E5E5]">  // ❌ Wrong color
```
