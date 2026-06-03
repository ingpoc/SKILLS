# Design tokens — shared `:root` block

Every artifact uses this block unless the operator names a different brand. It matches the `anthropics/html-effectiveness` gallery exactly so a new artifact sits cleanly next to the 20 starter templates.

## The block

```css
:root {
  /* Surface */
  --ivory:    #FAF9F5;   /* page background */
  --paper:    #FFFFFF;   /* card / panel background */
  --slate:    #141413;   /* primary ink */

  /* Accent */
  --clay:     #D97757;   /* primary accent (Anthropic orange) */
  --clay-d:   #B85C3E;   /* accent hover / pressed */
  --oat:      #E3DACC;   /* tinted underline / soft fill */
  --olive:    #788C5D;   /* secondary accent (calm / pass) */
  --rust:     #B04A3F;   /* alert / fail */

  /* Neutral ramp */
  --gray-150: #F0EEE6;   /* subtle fill (matches ivory family) */
  --gray-300: #D1CFC5;   /* hairline borders, 1.5px */
  --gray-500: #87867F;   /* secondary text */
  --gray-700: #3D3D3A;   /* body text on ivory */

  /* Type */
  --serif: ui-serif, Georgia, "Times New Roman", Times, serif;
  --sans:  system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --mono:  ui-monospace, "SF Mono", Menlo, Monaco, Consolas, monospace;
}
```

## Typographic roles

| Role | Stack | Used for |
|---|---|---|
| Display / headlines | `--serif`, weight 500, letter-spacing `-0.01em` to `-0.018em` | H1, H2 |
| Body | `--sans`, 14–16 px, line-height 1.5–1.6 | Paragraphs, table cells |
| Eyebrow / labels / data | `--mono`, 11–13 px, uppercase, letter-spacing 0.08–0.12em | Section eyebrows, code, numeric data |

Headline italic: `h1 em { font-style: italic; color: var(--clay); }` — italic-as-emphasis is the gallery's voice.

## Layout numbers

| Token | Value | Used for |
|---|---|---|
| Page max-width | 920 px (review/diagram) · 1120 px (plan/report) · 1180 px (editor) | `.wrap`, `.page`, `.sheet` |
| Body padding | 48 px 32 px 80 px → 56 px 24 px 96 px | `body` |
| Card radius | 10–12 px | Panels |
| Hairline border | `1.5px solid var(--gray-300)` | Cards, headers, dividers |
| Two-column gap | 24–48 px | Body + sidebar |
| Sidebar width | 300–340 px (collapses to 1fr at 880 px) | Margin notes, TOC, status panel |

## Eyebrow → headline → lead

The canonical header pattern (used by every gallery file):

```html
<header>
  <div class="eyebrow">PR · #247 · backend</div>
  <h1>Refactor the <em>retry</em> envelope</h1>
  <p class="lead">One-line summary in <code>--gray-700</code> on <code>--ivory</code>, max 620 px.</p>
</header>
```

```css
.eyebrow {
  font-family: var(--mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--gray-500);
  margin-bottom: 10px;
}
h1 {
  font-family: var(--serif);
  font-weight: 500;
  font-size: clamp(30px, 4vw, 38px);
  letter-spacing: -0.01em;
  margin-bottom: 12px;
}
.lead {
  font-size: 14.5px;
  line-height: 1.6;
  color: var(--gray-700);
  max-width: 640px;
}
```

## Override rules

- **Operator names a brand** → swap `--clay`, `--clay-d`, `--oat`, `--olive`, `--rust`. Keep the structural tokens (gray ramp, font stacks, radii).
- **Operator names dark mode** → swap `--ivory`/`--paper`/`--slate` and the gray ramp; keep clay (it works on both). Update text colors accordingly.
- **Operator says "use brand X"** → ask via `AskUserQuestion` for the 5 brand hex values before guessing.

## Don'ts

- No new fonts loaded from Google Fonts / CDN. Stick to the three system stacks.
- No purple/pink/cyan-blue defaults — that's slop palette. Clay-and-olive is the house style.
- No gradient backgrounds. The gallery uses flat fills, hairlines, and one accent rule.
- No drop shadows beyond `0 12px 32px rgba(20,20,19,.10)` on a single hero card. Default is no shadow.
