---
name: product-sites
description: Design and direct premium product, SaaS, app, portfolio, and launch sites with a clear product story, high data-ink ratio, grounded polished product imagery, responsive evidence composition, purposeful GSAP motion, and independent customer UI/UX acceptance. Use when creating or materially redesigning a product site. Coordinate with frontend-app-builder for concept-to-code implementation, imagegen for capture-grounded product imagery, review-customer-ui-ux for the final review loop, and Sites for setup, runtime, and deployment; do not replace those owners.
---

# Product Sites

> **Self-validate after edits.** Run the local `create-skill` audit.

Create a product site that makes one promise clear, proves it honestly, and
feels intentionally art-directed at every viewport.

## Ownership

This skill owns:

- product narrative and section rhythm;
- the taste thesis and editing decisions;
- the real-capture-to-polished-render grounding contract;
- proof credibility and screenshot/render treatment;
- web-specific data-ink discipline;
- responsive proof composition;
- the motion brief and GSAP choreography;
- final customer UI/UX review admission and closeout.

It does not own:

- visual concept generation, design-system extraction, frontend code, or
  fidelity mechanics: use `build-web-apps:frontend-app-builder`;
- image generation mechanics: use `imagegen` through the frontend builder;
- platform-specific screenshot mechanics: use the current browser, simulator,
  device, or native-app owner;
- DRAMS tokens/components: use `drams-design` only when DRAMS is explicitly
  requested or already owns the product;
- Sites initialization, storage, source publishing, access, or deployment: use
  `sites:sites-building` and `sites:sites-hosting`;
- independent customer review mechanics: use `review-customer-ui-ux`.

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
- presentation asset policy (`real`, `generated`, or `mixed`), including
  whether source captures are reference-only or publishable;
- required product surfaces and states, plus any prior accepted
  version/viewport the user asks to preserve or compare;
- claims the available evidence cannot support;
- required sections, routes, and exact user-supplied copy;
- the user's art direction and target viewport, if supplied.

Delete unsupported claims. A polished render may explain a product, but it
must not masquerade as runtime or synchronization proof.

### 2. Capture the real product

Before concepting marketing imagery or implementing the page:

- open the current product and capture at least one fresh, real screenshot of
  its primary customer-visible state;
- capture every additional surface or state that the marketing imagery will
  claim or depict;
- record the product identity, hierarchy, representative content, state, and
  details the polished render must preserve;
- exclude credentials, private data, unrelated system chrome, and stale or
  debug-only state.

Treat these screenshots as the grounding packet. They may be reference-only.
If the product cannot be run and captured, stop and report the missing
prerequisite; do not fabricate a substitute product.

### 3. Choose one design thesis

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

### 4. Build the narrative

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

End every product site with a compact owner-identity footer linking LinkedIn,
X, and GitHub. Resolve profile URLs from the brief or project context. In
Gurusharan's workspace, use these defaults unless he supplies replacements:

- LinkedIn: `https://www.linkedin.com/in/gurusharangupta`
- X: `https://x.com/gurusharan`
- GitHub: `https://github.com/ingpoc`

Keep this rule app-agnostic: these are owner profile links, not product or
repository links. Do not add a repository URL unless the user explicitly asks
for one. Give icon-only links accessible names.

### 5. Generate grounded product imagery, then build

Invoke `build-web-apps:frontend-app-builder` with the truth brief, narrative,
thesis, copy inventory, grounding packet, proof inventory, target viewports,
and motion brief.

During its concept phase, invoke `imagegen` with the real screenshots labeled
as grounding references. Generate, inspect, and save at least one high-quality
polished product image, then use that asset on the site. It must preserve the
observed product identity and required surfaces/states, remove incidental
capture noise, avoid unsupported features or claims, and follow the chosen
background/canvas treatment. A generated derivative remains a product render,
not runtime evidence.

Follow the frontend owner's concept approval, implementation, Browser/IAB, and
fidelity requirements exactly.

Do not duplicate its component architecture, coding, image-generation, or
browser-verification instructions here.

### 6. Compose proof before decoration

For each visual proof:

- bind its caption to the same figure/grid cell;
- keep title, state, and representative content readable at 100% zoom;
- use separate per-surface assets when one composite becomes illegible or
  ambiguous responsively;
- make source-to-output relationships explicit with position, labels, or a
  connector;
- remove rails, watermarks, borders, and empty canvas that encode no state;
- integrate generated imagery intentionally with the page background; reject
  accidental matte edges, canvas seams, or a pasted-poster appearance;
- use real captures when credibility is the job and polished generated renders
  when presentation is the job.

### 7. Add motion after layout is stable

Write the motion brief before GSAP code. Each animation must clarify entry,
hierarchy, causality, continuity, or state. If its purpose cannot be named,
remove it.

Use GSAP only when requested, already installed, or clearly justified. Keep
semantic HTML and the static layout complete without JavaScript. Respect
`prefers-reduced-motion`.

### 8. Verify the customer-visible result

In addition to the frontend builder's fidelity gate:

- verify the exact viewport from the user's screenshot or complaint;
- verify one wide desktop and one narrow mobile viewport;
- inspect the first viewport, every proof sequence, and the final action;
- confirm captions remain attached to their evidence;
- confirm text inside raster product renders remains readable;
- confirm generated imagery is not described as live evidence;
- confirm the generated asset covers the required surfaces/states and remains
  faithful to its real capture packet;
- compare media scale, typography scale, section density, and canvas treatment
  with any prior accepted version the user cited;
- confirm motion has no scroll-jacking, layout shift, or reduced-motion defect;
- compare the live capture against the concept/reference before claiming done.

### 9. Review, implement, and re-review

After the site passes implementation fidelity and before Sites handoff, invoke
`review-customer-ui-ux` in artifact-review mode on frozen desktop/mobile
evidence and one exact product-source fingerprint.

Implement the reconciled recommendations through the frontend owner, then
follow the review skill's acceptance-check and fresh blind UI+UX re-review loop
until dual Pass or its documented stop condition. Any source change invalidates
the prior review fingerprint. Do not brief fresh reviewers with prior findings
or fix history, and do not publish an unreviewed replacement as the accepted
version.

## Acceptance

Ship only when:

- a new visitor can name the product, benefit, and next action quickly;
- the page has one dominant idea rather than many equal components;
- every section advances the story or earns its proof;
- decorative ink is subordinate to information ink;
- proof is readable, labeled, and honest;
- a fresh real-product grounding packet exists and its polished generated
  derivative is used on the site;
- desktop and mobile express the same hierarchy without clipping or memory
  burden;
- motion improves comprehension and disappears safely when reduced;
- the current source fingerprint has completed the
  `review-customer-ui-ux` implement/re-review loop;
- the final footer links to the owner's LinkedIn, X, and GitHub profiles with
  accessible names;
- no fixable agency-review comment remains.

## Handoff

If `.openai/hosting.json` exists or Sites was requested, hand the validated
and reviewed source fingerprint to Sites and let Sites own publishing. Report
the live URL and any intentional evidence or access limitation without
deployment internals.
