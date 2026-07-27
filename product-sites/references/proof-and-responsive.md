# Proof and responsive composition

## Contents

1. Proof inventory
2. Presentation versus evidence
3. Figure construction
4. Responsive rules
5. Verification ledger

## Proof inventory

Before concepting, list each asset with:

| Field | Meaning |
| --- | --- |
| Source | Exact file, capture, dataset, or generated asset |
| Type | Real capture, measured evidence, generated render, or illustration |
| Claim supported | The narrow statement the asset actually proves |
| Native size | Pixel dimensions and aspect ratio |
| Readable content | Title, state, rows, labels, or values that must survive |
| Risk | Clipping, stale state, noise, private data, or unsupported inference |

Do not let a marketing treatment silently widen the claim.

## Presentation versus evidence

Use real captures when the section's job is trust, acceptance, release state,
or runtime proof. Use generated renders when the job is to make the intended
experience coherent and polished.

Generated renders may preserve the product's real information architecture and
customer-readable content, but describe them as product renders or examples.
Keep real acceptance captures outside the marketing claim when necessary.

## Figure construction

Each surface owns its image and caption:

```html
<figure>
  <img alt="What the surface shows and why it matters" />
  <figcaption>macOS widget</figcaption>
</figure>
```

When comparing surfaces:

- keep figures in one grid or sequence;
- label source and destination directly;
- repeat a distinctive task, title, state, or value so continuity is visible;
- show only enough rows to prove the relationship;
- crop each surface independently rather than scaling one giant composite;
- use one connector only when it encodes direction or causality.

Never place captions in a separate grid whose tracks can diverge from the
images.

## Responsive rules

At the user's reported viewport, verify the actual scroll position and
composition. A viewport crop can make complete content appear broken, but that
does not excuse a layout whose meaning depends on scrolling.

Wide:

- preserve readable product content;
- let proof occupy enough width to function as evidence;
- align figure captions to their own surfaces.

Medium:

- switch from side-by-side copy/proof before either becomes cramped;
- keep the headline, mechanism, and proof in one comprehensible sequence;
- avoid labels clustering under only part of the visual.

Narrow:

- stack figures or use a focused sequence;
- retain an orientation marker such as `Codex → macOS → iOS`;
- keep each card and label together;
- fit the proof within a reasonable memory span, preferably about two
  viewport heights;
- crop vertically before shrinking text below legibility;
- keep the next action reachable without traversing decorative repetition.

## Verification ledger

Record at least:

| Check | Evidence |
| --- | --- |
| Exact complaint viewport | Fresh live screenshot |
| Wide desktop | Fresh live screenshot |
| Narrow mobile | Fresh live screenshot(s) covering the sequence |
| Caption ownership | DOM or visual confirmation |
| Raster text readability | 100% zoom inspection |
| Claim boundary | Copy compared to proof type |
| Production access | Deployed response with its actual access state |

An unauthenticated sign-in page proves an owner-only gate, not public
availability. Report the access boundary honestly.
