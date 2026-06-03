# patterns — reusable HTML/CSS/JS recipes

Snippets that recur across the 20 gallery templates. Copy + adapt.

## Two-column body + sidebar (300px)

The default layout for plans, reviews, explainers — main column reads top-to-bottom; sidebar carries margin notes, TOC, status, or annotations.

```css
.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 48px;
  align-items: start;
}
@media (max-width: 880px) {
  .layout { grid-template-columns: minmax(0, 1fr); }
  .sidebar { border-top: 1.5px solid var(--gray-300); padding-top: 24px; margin-top: 24px; }
}
```

`minmax(0, 1fr)` on the main column is non-negotiable — bare `1fr` breaks when a child has `overflow-wrap` issues.

## Eyebrow → headline → lead

See [design-tokens.md § Eyebrow → headline → lead](design-tokens.md). Standard top-of-section block.

## Inline diff styling (review lane)

```css
.diff       { font-family: var(--mono); font-size: 13px; background: var(--paper); border: 1.5px solid var(--gray-300); border-radius: 10px; overflow: hidden; }
.diff .file { padding: 8px 14px; background: var(--gray-150); color: var(--gray-700); border-bottom: 1.5px solid var(--gray-300); }
.diff pre   { margin: 0; padding: 0; }
.diff .ln   { display: grid; grid-template-columns: 48px 48px 1fr; }
.diff .ln > span:nth-child(1),
.diff .ln > span:nth-child(2) { color: var(--gray-500); padding: 1px 10px; text-align: right; user-select: none; }
.diff .ln > span:nth-child(3) { padding: 1px 12px; white-space: pre; }
.diff .add  { background: #EAF4E6; }   /* olive-tinted */
.diff .add > span:nth-child(3) { color: #3F5E2C; }
.diff .del  { background: #F8E5E2; }   /* rust-tinted */
.diff .del > span:nth-child(3) { color: #7A2920; }
.diff .ctx  { color: var(--gray-700); }
```

## Code annotation with `<mark>`

```css
mark {
  background: linear-gradient(transparent 60%, var(--oat) 60%);
  color: inherit;
  padding: 0 1px;
}
```

Wrap critical tokens in code with `<mark>` for a clay-toned underline highlight without disturbing the line.

## Inline SVG diagrams

Use `viewBox` (not fixed width/height). Style via `<style>` inside the SVG so tokens cascade:

```html
<svg viewBox="0 0 800 360" role="img" aria-label="Deploy pipeline">
  <style>
    .node     { fill: var(--paper); stroke: var(--gray-300); stroke-width: 1.5; }
    .node-on  { fill: var(--oat); }
    .label    { font-family: var(--mono); font-size: 12px; fill: var(--slate); }
    .edge     { stroke: var(--gray-500); stroke-width: 1.5; fill: none; marker-end: url(#arrow); }
    .edge-hot { stroke: var(--clay); }
  </style>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--gray-500)"/>
    </marker>
  </defs>
  <!-- nodes + edges -->
</svg>
```

Token references inside SVG (`fill: var(--clay)`) cascade from `:root` — confirmed working across Chrome / Safari / Firefox.

## `<details>/<summary>` collapsibles

Reusable disclosure for long sections (gotchas, raw-data dumps, full TSV rows). Default closed.

```html
<details>
  <summary>Raw fixture data (25 rows)</summary>
  <table>…</table>
</details>
```

```css
details        { border-top: 1.5px solid var(--gray-300); padding: 14px 0; }
summary        { font-family: var(--mono); font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--gray-500); cursor: pointer; list-style: none; }
summary::-webkit-details-marker { display: none; }
summary::before { content: "+ "; color: var(--clay); }
details[open] > summary::before { content: "− "; }
```

## Drag-drop board (editor lane)

HTML5 dnd API — sufficient for triage-board use cases:

```js
let dragId = null;

document.querySelectorAll('.card').forEach(card => {
  card.draggable = true;
  card.addEventListener('dragstart', e => {
    dragId = card.dataset.id;
    card.classList.add('dragging');
  });
  card.addEventListener('dragend', () => card.classList.remove('dragging'));
});

document.querySelectorAll('.column').forEach(col => {
  col.addEventListener('dragover', e => { e.preventDefault(); col.classList.add('over'); });
  col.addEventListener('dragleave', () => col.classList.remove('over'));
  col.addEventListener('drop', e => {
    e.preventDefault();
    col.classList.remove('over');
    const card = document.querySelector(`[data-id="${dragId}"]`);
    col.appendChild(card);
    state.assignments[dragId] = col.dataset.column;
    render();
  });
});
```

## Clipboard export (editor lane)

```js
async function copy(text, label) {
  await navigator.clipboard.writeText(text);
  const pill = document.getElementById('copied-pill');
  pill.textContent = `Copied — ${label}`;
  pill.classList.add('show');
  setTimeout(() => pill.classList.remove('show'), 1500);
}
```

```css
.toolbar {
  position: sticky;
  bottom: 0;
  padding: 14px 16px;
  background: rgba(250,249,245,0.94);
  backdrop-filter: blur(8px);
  border-top: 1.5px solid var(--gray-300);
  display: flex;
  gap: 10px;
  align-items: center;
}
.btn {
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  background: var(--slate);
  color: var(--ivory);
  border: 0;
  padding: 8px 14px;
  border-radius: 8px;
  cursor: pointer;
}
.btn.secondary { background: transparent; color: var(--slate); border: 1.5px solid var(--gray-300); }
.btn:hover    { background: var(--clay); }
.pill         { font-family: var(--mono); font-size: 11px; color: var(--olive); opacity: 0; transition: opacity 0.2s; }
.pill.show    { opacity: 1; }
```

## Sticky table-of-contents (long documents)

Lives in the sidebar column. Highlights the current section via `IntersectionObserver`:

```js
const links = document.querySelectorAll('.toc a');
const targets = [...links].map(a => document.querySelector(a.getAttribute('href')));
const obs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      links.forEach(l => l.classList.toggle('active',
        l.getAttribute('href') === '#' + e.target.id));
    }
  });
}, { rootMargin: '-40% 0px -50% 0px' });
targets.forEach(t => t && obs.observe(t));
```

## Print-friendly (slide decks, reports)

```css
@media print {
  body { background: white; padding: 0; }
  .no-print { display: none; }
  .slide { page-break-after: always; }
}
```

## Reduced motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

Apply globally even on static pages — costs nothing, protects users with vestibular sensitivities.

## Mobile baseline

```css
html, body { overflow-x: clip; }   /* never `hidden` — clip preserves sticky positioning */
img, svg, video { max-width: 100%; height: auto; }
```

Plus `minmax(0, 1fr)` on every grid track that contains text or images.
