---
name: product-sites
description: Design and direct premium product, SaaS, app, portfolio, and launch sites with a clear product story, high data-ink ratio, credible product proof, responsive evidence composition, and purposeful GSAP motion. Use for new product landing pages, major site redesigns, screenshot-led product storytelling, DRAMS/Tufte-inspired web layouts, or when a site must feel distinctly high-taste rather than template-generated. Coordinate with frontend-app-builder for concept-to-code implementation and with Sites for setup, runtime, and deployment; do not replace either owner.
---

# Product Sites

Create a product site that makes one promise clear, proves it honestly, and
feels intentionally art-directed at every viewport.

## Ownership

This skill owns:

- product narrative and section rhythm;
- the taste thesis and editing decisions;
- proof credibility and screenshot/render treatment;
- web-specific data-ink discipline;
- responsive proof composition;
- the motion brief and GSAP choreography.

It does not own:

- visual concept generation, design-system extraction, frontend code, or
  fidelity mechanics: use `build-web-apps:frontend-app-builder`;
- image generation mechanics: follow `imagegen` through the frontend builder;
- DRAMS tokens/components: use `drams-design` only when DRAMS is explicitly
  requested or already owns the product;
- Sites initialization, storage, source publishing, access, or deployment: use
  `sites:sites-building` and `sites:sites-hosting`;
- independent customer review: use `review-customer-ui-ux` when requested or
  when release confidence depends on a blind review.

No separate `taste` skill is required. This skill is the product-site taste
layer; do not add a second taste checklist when one becomes available.

## Required reading

Read only the references needed for the task:

- Always read [design principles](references/design-principles.md) before
  concepting or restructuring a full page.
- Read [proof and responsive composition](references/proof-and-responsive.md)
  whenever the site uses screenshots, device views, product renders, factual
  claims, diagrams, or dense data.
- Read [GSAP choreography](references/gsap-choreography.md) whenever motion is
  requested or would materially clarify hierarchy or state.

## Workflow

### 1. Establish the product truth

Write a compact brief before design:

- audience;
- one job the site must do;
- one primary action;
- one-sentence promise;
- proof inventory, with each item marked `real capture`, `measured evidence`,
  `generated product render`, or `unsupported`;
- claims the available evidence cannot support;
- required sections, routes, and exact user-supplied copy;
- the user's art direction and target viewport, if supplied.

Delete unsupported claims. A polished render may explain a product, but it
must not masquerade as runtime or synchronization proof.

### 2. Choose one design thesis

Define:

- one visual thesis in a sentence;
- three to five design axes such as editorial/systemic, warm/technical,
  restrained/expressive, dense/airy;
- one container model;
- two to four recurring motifs;
- one signature media treatment;
- one or two motion cues.

Reject concepts that depend on generic card walls, bento grids, gradient glow,
floating dashboard chrome, decorative pills, fake metrics, or empty space that
does not improve hierarchy.

### 3. Build the narrative

Prefer this sequence, changing it only when the product requires another:

1. Promise: product identity, benefit, and primary action.
2. Orientation: what deserves attention and why.
3. Mechanism: how the product works.
4. Proof: real output, realistic product rendering, or measured evidence.
5. Trust: limits, provenance, privacy, or release state when material.
6. Action: one clear next step.

Vary section density, alignment, and image-to-text ratio. Preserve one gutter,
type system, color lock, and media grammar so the page feels continuous rather
than assembled from templates.

### 4. Hand the visual build to the frontend owner

Invoke `build-web-apps:frontend-app-builder` with the truth brief, narrative,
thesis, copy inventory, proof inventory, target viewports, and motion brief.
Follow its Image Gen, concept approval, implementation, Browser/IAB, and
fidelity requirements exactly.

Do not duplicate its component architecture, coding, image-generation, or
browser-verification instructions here.

### 5. Compose proof before decoration

For each visual proof:

- bind its caption to the same figure/grid cell;
- keep title, state, and representative content readable at 100% zoom;
- use separate per-surface assets when one composite becomes illegible or
  ambiguous responsively;
- make source-to-output relationships explicit with position, labels, or a
  connector;
- remove rails, watermarks, borders, and empty canvas that encode no state;
- use real captures when credibility is the job and polished generated renders
  when presentation is the job.

### 6. Add motion after layout is stable

Write the motion brief before GSAP code. Each animation must clarify entry,
hierarchy, causality, continuity, or state. If its purpose cannot be named,
remove it.

Use GSAP only when requested, already installed, or clearly justified. Keep
semantic HTML and the static layout complete without JavaScript. Respect
`prefers-reduced-motion`.

### 7. Verify the customer-visible result

In addition to the frontend builder's fidelity gate:

- verify the exact viewport from the user's screenshot or complaint;
- verify one wide desktop and one narrow mobile viewport;
- inspect the first viewport, every proof sequence, and the final action;
- confirm captions remain attached to their evidence;
- confirm text inside raster product renders remains readable;
- confirm generated imagery is not described as live evidence;
- confirm motion has no scroll-jacking, layout shift, or reduced-motion defect;
- compare the live capture against the concept/reference before claiming done.

For a blind review, provide frozen screenshots and one exact source
fingerprint. Do not leak intended fixes to reviewers. A release-quality pass
has no open P0-P2 customer-visible findings.

## Acceptance

Ship only when:

- a new visitor can name the product, benefit, and next action quickly;
- the page has one dominant idea rather than many equal components;
- every section advances the story or earns its proof;
- decorative ink is subordinate to information ink;
- proof is readable, labeled, and honest;
- desktop and mobile express the same hierarchy without clipping or memory
  burden;
- motion improves comprehension and disappears safely when reduced;
- no fixable agency-review comment remains.

## Handoff

If `.openai/hosting.json` exists or Sites was requested, hand the validated
source to Sites and let Sites own publishing. Report the live URL and any
intentional evidence or access limitation without deployment internals.
