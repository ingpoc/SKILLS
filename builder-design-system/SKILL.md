---
name: builder-design-system
description: "Apply the Autonomous Agent Builder design system to the autonomous-agent-builder codebase. Use when building or restyling Builder dashboard pages, adding or auditing primitive components, generating theme presets, wiring status language, motion hooks, or validating a screen against the locked Builder design system."
---

# Autonomous Agent Builder — Design System Skill

You are applying the **Autonomous Agent Builder design system v0.5** to the `autonomous-agent-builder` codebase. This skill bundles the locked tokens, themes, primitive APIs, page patterns, and status language into a deterministic playbook.

## When to invoke

Use this skill when the user asks you to:
- Build a new page or surface in the agent-builder app
- Restyle an existing page to match the system
- Add or audit a primitive component
- Generate a new theme preset
- Validate that a screen conforms to the system

## What's in this skill

| File | Use |
|---|---|
| `tokens.css` | Single source of truth for color, type, spacing, radii, shadows, status colors. Drop into `frontend/src/index.css` or import alongside it. |
| `themes.json` | Six locked theme presets — `calm`, `operator`, `sage`, `ember`, `midnight`, `paper`. Each declares hue, density, radius, mode. |
| `components.md` | Primitive component API contracts — core (`StatusPill`, `Surface`, `Eyebrow`, `Tabs`, `Button`, `StatusDot`, `Code`, `Kbd`, `Meter`, `Stat`, `Input`, `BrandMark`) + editorial (`EditorialContent`, `KnowledgeCard`, `KnowledgeEditorialSummary`, `MemorySidebar`, `RelatedSidebar`, `TagCloud`, `EmptyState`, `SectionLabel`). |
| `patterns.md` | Page-level patterns — page intro, three-column chrome, condense-on-scroll, configurable design-system drawer, Settings page hierarchy, command palette, status pill rules, **Motion choreography (GSAP)** with named recipes and `data-*` hooks. |
| `status-language.md` | Status taxonomy + tone mapping, plus the **memory-type tones** (`decision` / `pattern` / `correction`). |

## Operating rules

1. **Never invent colors.** Use `var(--*)` tokens or `oklch()` with the system's hue/lightness scale. New accents must be one of the 9 hues in `themes.json`.
2. **Never invent statuses.** Every state-bearing UI must use a status string from `status-language.md` and the `StatusPill` / `StatusDot` primitives.
3. **Always use the primitives** in `components.md` for buttons, surfaces, tabs, dots, pills, eyebrows, code, kbd, editorial blocks, knowledge cards, tag clouds, drawers, empty states, section labels. Never hand-roll equivalents.
3a. **Motion is part of the contract.** When building a List+Detail, Stream, or Dashboard page, attach the right `data-*` hooks (`data-board-section`, `data-agent-stage`, `data-kpi`, `data-cost-bar`, `data-stagger`) so the page picks up the system's choreography automatically. Every new tween must respect `prefers-reduced-motion` and `clearProps: "all"`.
4. **Page intros follow the pattern** in `patterns.md` — Eyebrow + display heading + 60ch lede paragraph + content. No exceptions on top-level pages.
5. **Status pills are read-only.** Don't make them buttons or links — they describe state, they don't change it.
6. **Density is a multiplier**, not a category. Read `--density` and multiply paddings/heights inside primitives. Don't fork primitives per density.
7. **Dark mode is data-driven.** Set `data-theme="dark"` on `<html>` — never hard-code dark hex values in components.
8. **Information architecture beats paint.** The reference system's main value is how it makes Builder objects legible: tasks, runs, approvals, traces, memories, docs, costs, and decisions. Do not stop at matching colors, cards, or typography if the page still hides the operational object in the wrong place.
9. **Theme configuration is a product surface.** Preserve the reference `tweaks.jsx` model: preset cards with mini previews, advanced controls for hue/chroma/density/radius/mode/display face, live CSS-variable updates, and a reset path back to presets. Do not replace it with a static theme picker.

## Standard workflow

When asked to build or modify a page in the codebase:

1. **Read the locked system.** Open `tokens.css`, `components.md`, `patterns.md`. Don't guess.
2. **Identify the page archetype and owning object.** Most pages are one of:
   - **List + detail** (Board, Backlog, Inbox): scan many records; selected detail stays secondary.
   - **Agent chat + run trace** (Agent): operator chat/voice is one mode; task/run evidence is a separate mode centered on one run.
   - **Dashboard** (Metrics, Observability): health bands first, then trace/event/history drill-down.
   - **Reference** (Knowledge, Memory): durable records with readable detail, not raw dumps.
3. **Wrap in the standard page intro** (Eyebrow + heading + lede).
4. **Compose with primitives** — never `<div>` a button, never bare-color a status.
5. **Wire status strings** to the lookup in `status-language.md`.
6. **Audit before finishing** — run the checklist at the bottom of `patterns.md`.

## Builder product IA rules

Apply these before page-level styling:

- **Agent is two modes.** Use `Agent chat` for operator-to-Builder-Agent text and realtime voice. Use `Run trace` for task/run inspection: prompt, thinking, tool calls, tool args/results, gates, approvals, logs, diffs, cost, runtime, model, duration, and stop reason.
- **Voice is transport, not a route.** Voice controls live in Agent chat and voice preferences live in Settings. Voice utterances may mirror into Run trace only when they affect run evidence.
- **Board is the work horizon.** Board cards and drawers summarize task ownership, current state, and run list. Detailed thinking/tool/gate inspection belongs in Agent Run trace. Add an "Open in Agent Run trace" path rather than duplicating the full run viewer in the Board drawer.
- **Settings are operator preferences first.** Prefer this order: Voice & Realtime, Agent surface, Board & layout, Runtime, Appearance/design tokens. Do not lead with token controls when the user is configuring how to operate Builder.
- **Design configuration remains rich.** If the app has both a design-system drawer and a Settings page, keep the drawer focused on live theme/preset/advanced preview controls and keep the Settings page focused on durable operator preferences. The Settings page may mirror appearance state, but it should not lose the full configurable theme editor.
- **Compare and Observability stay evidence-first.** Compare should use real AgentRun records and highlight baseline vs variant outcomes. Observability should show health bands, trace waterfall/spans, SDK events, and run history with dense readable drill-down.
- **Knowledge and Memory are reference records.** Use filter/list plus persistent editorial detail. Long-form content must render through `EditorialContent`; never expose final prose as raw `pre` text.

## Theme application

The configurable design system is modeled by the reference `src/tweaks.jsx`. It is a live operator control, not just internal CSS:

- Theme presets bundle `id`, `name`, `tagline`, `hue`, `density`, `radius`, `mode`, `fontDisplay`, and `fontUi`.
- Picking a preset updates all knobs at once and shows a compact preview tile.
- Advanced/custom mode may override `hue`, `accent chroma`, `density`, `radius`, `mode`, and display face independently.
- Persist preferences in one runtime-preference object. Use `null` for "follow preset" overrides so reset is deterministic.
- Apply theme state by setting CSS variables and root attributes/classes; do not branch component styles by theme id.

At minimum the active theme writes:

```css
:root {
  --accent-hue: <hue>;
  --accent-chroma: <chroma>;
  --density: <density>;
  --radius-base: <radius>px;
}
:root[data-theme="dark"] { /* dark token overrides */ }
```

All primitives derive every visual from these knobs + the static token base. To add a new theme: append to `themes.json` with a unique `id`, `name`, `tagline`, `hue`, `density`, `radius`, `mode`, and font metadata. Avoid adding per-page theme conditionals.

## Generating a new component

If you must add a new primitive (rare):

1. Confirm an existing primitive doesn't already cover it.
2. Use only `var(--*)` tokens for color, spacing, radius, shadow.
3. Honor `--density` for any vertical padding or height.
4. Honor `data-theme="dark"` automatically by using semantic tokens (`--fg`, `--bg`, `--surface`, `--line`) — never raw hex.
5. Add it to `components.md` with its API contract before merging.

## Done criteria

A page or component is done when:
- All colors come from tokens
- All statuses come from `status-language.md` (and memory types from the memory-type tones table)
- All shells, buttons, pills, tabs, dots come from primitives
- All long-form markdown renders through `EditorialContent`
- All list rows on knowledge surfaces use `KnowledgeCard`; all drawers use `MemorySidebar` / `RelatedSidebar`
- The page renders correctly in all 6 themes (light + dark)
- The page has a proper intro block
- The page declares the correct motion hooks (see `patterns.md` → Motion choreography) and respects `prefers-reduced-motion`
- No raw hex codes in the diff (search the diff for `#[0-9a-f]{3,8}` — should be empty)
- `--density` is respected on any custom height/padding

## Out of scope

- Backend / SDK changes
- Routing changes
- New nav entries (those are owned by `App.tsx` and require a product decision)

If a user asks for one of the above, complete the design work and clearly call out the non-design changes for them to handle separately.
