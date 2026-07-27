# GSAP choreography for product sites

## Contents

1. Motion brief
2. Choreography patterns
3. Implementation rules
4. Motion QA

## Motion brief

For every motion cue, name:

- trigger;
- target;
- purpose;
- start and end state;
- duration and easing;
- reduced-motion behavior.

Use motion to explain:

- entry hierarchy;
- source-to-destination flow;
- state change;
- continuity across surfaces;
- the relationship between text and proof.

Remove motion whose purpose is only “make it feel premium.”

## Choreography patterns

Prefer a small motion vocabulary:

- first viewport: one coordinated entrance, roughly 600–900 ms;
- section reveal: 450–750 ms with 60–140 ms stagger;
- proof sequence: source first, destinations second, connector last;
- state change: animate the changed value or row, not the whole page;
- one signature transition reused sparingly.

Do not fade every section identically. Do not scroll-jack, trap input, hide
content until JavaScript runs, or use parallax that fights reading.

## Implementation rules

- Use CSS for static layout and simple hover/focus transitions.
- Use GSAP only when installed, requested, or justified by sequencing.
- Animate `transform` and `opacity`; avoid layout properties in scroll loops.
- Scope animations with `gsap.context()` and call `revert()` on cleanup.
- Register `ScrollTrigger` once and use `once: true` for one-time narrative
  reveals unless replay is meaningful.
- Use `gsap.matchMedia()` or an equivalent boundary when choreography differs
  by viewport.
- Never apply entrance transforms to images whose transform already performs a
  crop or alignment; animate a wrapper instead.
- Keep the complete page readable before animation starts.
- Under `prefers-reduced-motion: reduce`, skip reveals and transitions rather
  than merely shortening them.

## Motion QA

Verify:

- no flash of hidden content;
- no clipped or displaced proof;
- no transform collision with responsive crop logic;
- no layout shift while scrolling;
- no animation warning for missing targets;
- no stale ScrollTrigger after navigation or hot reload;
- keyboard and touch behavior remain unaffected;
- reduced-motion mode shows the final state immediately;
- mobile motion is simpler than desktop when space or performance requires it.

Browser console warnings, a successful build, or a static screenshot alone do
not prove motion quality. Observe the actual sequence at desktop and mobile.
