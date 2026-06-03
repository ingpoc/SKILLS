# Page patterns

## 1. Page intro

Every top-level page opens with the same three-line block:

1. `<Eyebrow>` — surface + subtitle, mono uppercase
2. Display heading — Newsreader 36px, weight 400, letter-spacing -0.025em, line-height 1.08
3. Lede paragraph — 15px, leading 1.7, color `--fg-3`, max-width 60ch

```tsx
<div data-stagger>
  <Eyebrow>Observability · traces · spans · evidence</Eyebrow>
  <h1 className="mt-2 …">Every run, every span, every gate.</h1>
  <p className="mt-3 max-w-[60ch] …">One-paragraph framing.</p>
</div>
```

## 2. App chrome

Three-column grid, sticky, blurred backdrop, condenses on scroll.

| Column | Content |
|---|---|
| Left | `<BotTile />` + brand wordmark |
| Center | Pill-shaped nav: Agent · Board · Metrics · Observability · Knowledge · Memory · Backlog |
| Right | Icon-only utility cluster: ✨ runs · 🔍 ⌘K · 📥 Inbox(badge) · ⇄ Compare · ⊞ Settings · ☀/☾ |

On scroll past 24px, brand and utilities fade out, nav pill stays.

## 3. Configurable Design System Drawer

The reference `src/tweaks.jsx` is the canonical interaction model for theme configuration.

Use a right-anchored drawer when the operator is tuning the design system while seeing the app behind it:

- **Design** — theme preset cards with miniature UI previews, active marker, tagline, and reset-to-preset behavior
- **Advanced** — hue swatches, accent chroma, density, radius, mode, and display face controls
- **Preferences** — runtime SDK, board density, agent inspector default, transcript default, transcript layout, compare display, notifications
- **Runtime** — read-only SDK state, active runs, approvals/questions, permission mode, cost/tokens, MCP servers/tools

Live changes must update CSS variables/root attributes immediately. Use `null` override values for "follow preset" so reset clears custom state without losing the selected preset. Do not collapse this drawer into a static dropdown; the preview cards and advanced controls are part of the product.

## 4. Settings Page

Settings may be a full page or right-anchored drawer depending on the app shell, but its hierarchy is operator-preference first:

- **Voice & Realtime** — realtime model, voice, push-to-talk, inline transcript, bind to current session, destructive-action confirmation phrase
- **Agent surface** — default mode, inspector tab, transcript filter, transcript layout
- **Board & layout** — board density, compare display
- **Runtime** — runtime SDK and read-only state, MCP servers/tools, cost/tokens
- **Appearance** — theme presets and advanced token overrides

If implemented as a drawer, use a soft overlay (not opaque) so the underlying app remains visible while previewing design changes. If implemented as a full page, use numbered sections with a left label column and right controls.

The Settings page may include or mirror appearance controls, but do not remove the richer configurable design-system drawer behavior from the product.

## 5. Command palette

⌘K opens a centered modal with grouped, fuzzy-searched results: Actions · Routes · Tasks · Knowledge. ↑↓↵ keyboard nav, Esc closes. Mono IDs in the right column.

## 6. Page archetypes

| Archetype | Examples | Layout |
|---|---|---|
| **List + detail** | Board, Backlog, Inbox | Left rail of items, right pane for selected detail. Selected row highlighted with accent-tint background. |
| **Agent chat + run trace** | Agent | Two top-level modes. `Agent chat` is operator text/voice with composer and inline questions/approvals. `Run trace` centers one task/run with prompt, thinking, tools, gates, logs, diffs, cost, runtime, and approvals. |
| **Stream** | SDK events | Single vertical scrolling thread. Newest at the bottom. Sticky filter bar at top. |
| **Dashboard** | Metrics, Observability | Health-bands strip across the top, then tabs for drill-down. Stat cards use `<Stat>` primitive. |
| **Reference** | Knowledge, Memory | Card grid or filterable list. No hover-to-edit — these are records. |

## 6a. Agent page split

The Agent page is the product control room and must not collapse every concern into one transcript.

### Agent chat

- Primary object: the operator conversation with the SDK-backed Builder Agent.
- Includes typed composer, realtime voice controls, pending question/approval cards, session resume/new-thread actions, and the current response stream.
- Realtime voice is a transport layered on the same session. Do not create a standalone Voice route.

### Run trace

- Primary object: one task/run.
- Required visible groups: task/run header, phase strip, original prompt, thinking/reasoning summaries, tool calls with args/results, gate results, approvals, cost/budget, runtime/model/provider, duration/turns/tokens, logs, diffs, and stop reason.
- Board drawers may summarize the same runs, but detailed inspection belongs here. Provide a clear path from a Board run row to this mode.

## 7. Status pills

Use `<StatusPill status="…" />`. The label and tone come from the status key. Never hand-roll these.

## 8. Empty states

Pattern: small `<Eyebrow>` + one sentence in `--fg-3` + optional ghost button. Never use illustrations.

## 9. Error states

Same as empty state but eyebrow is `Error · <code>` and the sentence describes the failure in operator language. Don't apologize. Offer the next action.

## 10. Motion choreography (GSAP)

The codebase ships GSAP (`gsap@3.14` + `@gsap/react@2.1` + `ScrollTrigger`). Animations are not decorative — they are a named, deterministic part of the page contract. Every hook respects `prefers-reduced-motion: reduce` and uses `clearProps: "all"` so the final state is pure CSS.

### Data hooks

| Attribute | Used on | Drives |
|---|---|---|
| `data-stagger` | Page intro block | Initial fade-up of the hero |
| `data-board-section` | Board pipeline columns | Phase-1 section reveal |
| `data-slot='card'` | Board cards (shadcn `Card`) | Phase-2 card cascade |
| `data-agent-stage='section'` | Agent page region | Section slide-up |
| `data-agent-stage='card'` | Agent page card | Card cascade (delayed) |
| `data-agent-inspector='true'` | Inspector rail | Fade+slide on activate |
| `data-kpi` | Metrics KPI card | ScrollTrigger entrance |
| `data-cost-bar` | Cost bar fill | Height 0 → target on mount |

### Named recipes

| Name | Targets | Tween |
|---|---|---|
| **Page entrance (sections)** | `[data-board-section]`, `[data-agent-stage='section']` | `y: 24 → 0`, opacity, **0.45s**, stagger 0.1, `power3.out` |
| **Page entrance (cards)** | `[data-slot='card']`, `[data-agent-stage='card']` | `y: 12 → 0`, scale `0.97 → 1`, opacity, **0.35s**, stagger 0.04, delay 0.3, `power2.out` |
| **Inspector reveal** | `[data-agent-inspector='true']` | `x: 8 → 0`, `y: 16 → 0`, opacity, **0.3s**, `power2.out`, on activeInspector change |
| **List-row hover shift** | `KnowledgeCard` button | `x: 0 → 4` on `mouseenter`, **0.18s** `power2.out` |
| **Drawer slide** | `MemorySidebar`, `RelatedSidebar` | `x: 100% ↔ 0`, **0.32–0.4s**, `power3.out`; backdrop opacity 0–1, **0.24–0.3s** |
| **KPI on-scroll** | `[data-kpi]` | `y: 20 → 0`, scale `0.97 → 1`, opacity, **0.45s**, stagger 0.08, `ScrollTrigger { start: "top 90%", once: true }` |
| **Cost-bar fill** | `[data-cost-bar]` | `height: 0% → style.height`, **0.5s**, delay `0.4 + i*0.02`, `power2.out` |
| **Tag toggle** | `TagCloud` chips | opacity `1 / 0.3` + scale `1 / 1.05`, **0.4s**, `power2.out` |
| **Ambient liveness** | `.pulse-ring`, `.breathe`, `.ambient-scan` | Pure CSS keyframes — see tokens |
| **Voice orb (speaking)** | `VoiceOrb` (state=`speaking`) | scale `0.96 ↔ 1.08`, **0.45s**, `sine.inOut`, yoyo infinite — overridden by amplitude prop when streamed |
| **Voice orb (listening)** | `VoiceOrb` (state=`listening`) | scale `0.98 ↔ 1.04`, **0.9s**, yoyo |
| **Voice orb (thinking)** | `VoiceOrb` (state=`thinking`) | scale `0.99 ↔ 1.01`, **1.4s**, yoyo — deliberately subtle |
| **Voice orb (connecting)** | `VoiceOrb` outer ring | `rotation: 0 → 360`, **1.6s**, linear, infinite |
| **Voice waveform** | `VoiceWaveform` bars | height transition **60ms** linear when `amplitudes` provided, otherwise **120ms** `ease-out` self-driven |
| **Voice dock entrance** | `VoiceDock` | `y: 24 → 0`, opacity, **0.4s**, `power3.out` |
| **Voice panel entrance** | `VoicePanel` | `y: 16 → 0`, opacity, **0.4s**, `power3.out`, `clearProps: "all"` |
| **Voice caption stream** | `VoiceCaption` body when `isLive` | opacity `0.6 → 1`, **0.18s**, on each appended text chunk |
| **Voice tool-call enter** | `VoiceToolCallChip` | `x: -8 → 0`, opacity, **0.28s**, `power3.out` |
| **Voice transcript hover** | `VoiceTranscriptCard` | `x: 0 → 4` on `mouseenter`, **0.18s** — matches list-row hover shift |

### Rules

1. **Never animate without a `data-*` hook.** All entrance animations are hook-driven so any page automatically gets the right choreography by including the right attributes.
2. **One scope per page.** Use `useGSAP({ scope: containerRef })` rooted at the page wrapper — never global selectors.
3. **Reduced motion is non-negotiable.** Every drawer/hover hook short-circuits to instant state when `matchMedia("(prefers-reduced-motion: reduce)").matches`. Apply the same guard if you add a new tween.
4. **`clearProps: "all"`** at the end of entrance tweens so CSS controls the resting state (theme switches don't have to fight inline styles).
5. **No reveal on infinite scroll lists.** Only the first render of a page gets a stagger; subsequent inserts are instant or use the dedicated row-hover shift.
6. **No motion on telemetry numbers.** Use CSS `.breathe` / `.pulse-ring` only for liveness — don't tween stat values.

---

## Conformance checklist

Run through this before considering a page done:

- [ ] Page intro with Eyebrow + display heading + 60ch lede
- [ ] All colors are `var(--*)` tokens or themed `oklch()` — no raw hex
- [ ] Every status uses a key from `status-language.md`
- [ ] Every button is `<Button variant=…>`, never a styled `<div>`
- [ ] Every panel is `<Surface>`, never an ad-hoc `<div className="rounded border">`
- [ ] Every pill is `<StatusPill>` — no custom badges
- [ ] Every tab strip is `<Tabs items=…>`
- [ ] `data-stagger` on hero blocks for entrance animation
- [ ] Correct motion hooks attached (`data-board-section`, `data-agent-stage`, `data-kpi`, etc.)
- [ ] Every new tween respects `prefers-reduced-motion`
- [ ] `data-screen-label` on the page root for analytics + comments
- [ ] Renders correctly in all 6 themes (light + dark)
- [ ] Mobile: nav row collapses, layout reflows at <lg
- [ ] Keyboard: focus visible, Esc closes overlays
