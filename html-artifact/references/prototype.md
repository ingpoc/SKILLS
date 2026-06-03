# prototype lane — animation / interaction sketch in HTML

Operator's intent: "I want to feel this design before I build it for real." Output is an HTML mock — even if the production target is React, Swift, or native.

## Closest gallery templates

| Template | When |
|---|---|
| `07-prototype-animation.html` | CSS animation / transition sketch — feel the motion |
| `08-prototype-interaction.html` | JS-driven interaction sketch — feel the flow |

## When to hand off

| Operator intent | Use |
|---|---|
| "Let me try parameter X and copy back the values I like" — knob-tuning IS the artifact | **`playground` skill**, not this lane |
| "Show me this animation / interaction so I can decide if it feels right" | **this lane** |
| "Build the polished marketing page" | **`hallmark` skill** |

If unsure, ask: *"Is the prototype itself the deliverable (I'll watch / share it), or do you want to tune parameters and export them back as a prompt?"* Knob-tuning → playground.

## Preflight

1. **Confirm the target.** What's being prototyped? What states / transitions matter?
2. **Confirm fidelity.** Sketch (a few divs + CSS) or higher-fi (closer to real component)? Default sketch.
3. **Output path.** `/tmp/prototype-<slug>.html` unless the operator names a repo location.

## Do — animation (template 07)

1. Render the element(s) being animated, plus a small **playback row** under them: Play / Reset / speed slider (`0.5×` / `1×` / `2×`).
2. **Reduced motion fallback** — `@media (prefers-reduced-motion: reduce)` shows the start and end states statically.
3. Show the **CSS keyframes** in a `<pre>` block under the demo so the operator can copy the actual code.
4. **One animation per page** by default. If comparing variants, lay them out in a grid with labels.

## Do — interaction (template 08)

1. Render the interactive surface plus a **state inspector** in a sidebar (current state, last event).
2. **Reset button** so the operator can replay.
3. Show the **JS event handlers** in a `<pre>` under the demo.
4. **Empty + error + loading states** — every interaction has them; sketch all three or label them "out of scope".

## Closeout

1. `xdg-open <path>`.
2. State path. Tell the operator they can copy the `<style>` block or the JS function directly into their production codebase as a starting point.

## Anti-patterns

- **Prototype that requires a backend.** Always mock data inline. No `fetch()`.
- **Animation with no reduced-motion fallback.** Accessibility, not optional.
- **Interaction without a reset / replay.** The operator will trigger it five times in a row.
- **Polishing visual design.** This is a behavior sketch; if the operator wants polish, hand to hallmark.
