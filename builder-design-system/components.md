# Component primitives

Every screen in the agent-builder app composes from this set. Never hand-roll equivalents.

## StatusPill

```tsx
<StatusPill status="running" />
```

| Prop | Type | Notes |
|---|---|---|
| `status` | one of `status-language.md` keys | Required |
| `withDot` | boolean | Default `true` |
| `className` | string | |

**Rules:** read-only; never wrap in `<button>` or `<a>`; the label is automatic from the status key.

## StatusDot

```tsx
<StatusDot tone="active" pulse size={6} />
```

| Prop | Notes |
|---|---|
| `tone` | `active` `done` `review` `pending` `blocked` `muted` |
| `pulse` | adds the live-ping ring. Use only for actively-running states |
| `size` | px diameter, default 6 |

## Surface

```tsx
<Surface raised className="p-5 space-y-4">…</Surface>
```

The standard card/panel. `raised` adds the elevated shadow. Pads itself by default; override with `className`.

## Eyebrow

```tsx
<Eyebrow>Section title · subtitle</Eyebrow>
```

Mono uppercase 10px tracking-[0.2em] muted. Use as section headers above content.

## Button

```tsx
<Button variant="default" size="md">Run</Button>
```

| variant | use |
|---|---|
| `default` | Primary action, accent fill |
| `secondary` | Surface fill with border |
| `ghost` | Hover-only background |
| `danger` | Destructive — red tone |

`size`: `sm` `md` `lg`. Density-aware via `--density`.

## Tabs

```tsx
<Tabs
  value={tab}
  onChange={setTab}
  items={[{ value: "trace", label: "Trace" }, { value: "events", label: "SDK events" }]}
/>
```

Pill-style tabs. **Note:** prop is `items`, not `options`.

## Input

Standard form input. Inherits `--radius-sm`, density, focus ring uses `--accent`.

## Code / Kbd

`<Code>` for inline monospace strings. `<Kbd>⌘K</Kbd>` for keyboard hints — small key cap with subtle border.

## Meter

```tsx
<Meter value={0.62} tone="done" />
```

Horizontal progress bar. Tone controls fill color.

## Stat

Big number + label + optional trend. Use in dashboard headers (Metrics, Observability health bands).

## BrandMark

The autonomous-agent-builder bot tile. Don't recreate — import this.

---

## EditorialContent

```tsx
<EditorialContent content={markdown} externalTitle={doc.title} />
```

Markdown-to-editorial renderer used everywhere we surface long-form knowledge or memory content. Parses headings, paragraphs, lists, quotes, and fenced code blocks; cleans wikilinks `[[a|b]]` → `b`; inline `\`code\`` and `**bold**`.

| Block | Treatment |
|---|---|
| `# h1` | Newsreader 2.2–2.5rem, weight 600, tracking -0.05em, max-w 13ch |
| `## h2` | Section divider + 11px mono eyebrow uppercase tracking-[0.2em] |
| `### h3` | 1rem sans semibold |
| paragraph | 14px / line-height 1.6 / `--fg/0.84` / max-w 69ch |
| list | 14px, marker `--fg-muted`, max-w 70ch, gap 2.5 |
| quote | `--status-active/0.05` tint, left-border 3px `--status-active/0.35`, asymmetric radius (right-1rem / left-0.3rem) |
| code | Surface-2 panel, mono eyebrow label, mono body 12px |

**Rules:** never style headings inline elsewhere; if a screen needs to render markdown, use this. Pass `externalTitle` when the page already shows the doc title so the first `# h1` is suppressed.

## KnowledgeCard

```tsx
<KnowledgeCard doc={doc} onSelect={setId} isSelected={id === doc.id} />
```

Standard list-item card for knowledge surfaces. Composes the `surface-list-item` utility (see Patterns). Hover micro-shifts right by 4px via GSAP (respects `prefers-reduced-motion`).

Anatomy: type badge + mono author/source · title (16px semibold tracking-tight) · 60-char excerpt · right-aligned mono meta (`{n} links`, version) · tag footer (max 4 + overflow chip).

## KnowledgeEditorialSummary

```tsx
<KnowledgeEditorialSummary doc={doc} relatedDocs={related} />
```

The large editorial hero used at the top of a knowledge document view. Layout:

1. **Meta strip** — status dot (`active`) + source author + doc type + date, mono uppercase
2. **Display title** — Newsreader 2.2–2.8rem, tracking -0.065em, max-w 46rem
3. **Lede paragraphs** — 16px / 1.62, max-w 42rem
4. **Two-column inset** (xl: 1.08fr / 0.92fr):
   - **Operator brief** — tinted `--status-active/0.05` panel with bulleted takeaways (max 3, ≤18 words each)
   - **Document map** + **Supporting context** stack — scope, link count, related count, in mono

Use only as a page hero, not in lists.

## MemorySidebar

```tsx
<MemorySidebar entry={entry} content={content} isOpen={open} onClose={close} />
```

Right-anchored slide-in drawer for a memory record. Width 36rem on `sm+`. Slides via GSAP (`x: 0 ↔ 100%`, 0.4s `power3.out`). Backdrop fades on mobile only (`lg:hidden`).

Memory type maps to badge variant via `MEMORY_TYPE_TONE` (see status-language). Body uses `<EditorialContent>`.

## RelatedSidebar

```tsx
<RelatedSidebar doc={doc} relatedDocs={related} onSelectDoc={...} onClose={...} isOpen={...} />
```

Dual-mode sidebar:

- **Desktop (`xl+`)** — sticky `top-24` rail, `h-[calc(100vh-7rem)]`, persistent. Close button hidden.
- **Below `xl`** — slide-in drawer (38rem) with backdrop.

Inner: badge + author + title + tag chips · separator · `KnowledgeDocumentView` · **Related context** section with three collapsible `<details>` groups: *Links to (n)* · *Referenced by (n)* · *Related topics (n)*. Each row uses `surface-list-item p-3` with title + type badge + 88-char excerpt. Empty state inline via `<EmptyState>`.

## TagCloud

```tsx
<TagCloud tags={tags} selectedTags={selected} onTagToggle={toggle} />
```

Filterable tag-chip cluster. Sort order: selected first, then by count descending. Each chip uses `<Badge>` with three visible states:

| State | Visual | Pointer |
|---|---|---|
| **Selected** | default variant + trailing `×` icon, scale 1.05 | clickable |
| **Available** | outline variant, opacity 1 | clickable |
| **Disabled** | outline variant, opacity 0.3 | `none` |

Each chip shows `name (count)`. Tween: opacity + scale, 0.4s `power2.out`. Click on disabled is suppressed unless already selected.

## EmptyState

```tsx
<EmptyState label="…" detail="…" action={<Button>…</Button>} className="…" />
```

The shared empty-state block. Renders an Eyebrow-style `label` + 60ch `detail` line in `--fg-3`, optional action. **No illustrations.** Use the same component for *no results*, *not yet selected*, and *not yet ingested* — vary the copy, not the shape.

## SectionLabel

```tsx
<SectionLabel>Related context</SectionLabel>
```

Slim wrapper for an in-content section header — mono 11px, uppercase, tracking-[0.18em], `--fg-3`. Use inside detail panes and drawers where a full `<Eyebrow>` page-frame would feel too top-level.

---

## Page-level composition

A typical page body looks like:

```tsx
<div className="space-y-6" data-screen-label="Pagename">
  <div data-stagger>
    <Eyebrow>Surface · short subtitle</Eyebrow>
    <h1 className="mt-2 …display heading…">Headline.</h1>
    <p className="mt-3 max-w-[60ch] …lede…">One-paragraph framing.</p>
  </div>

  <div data-stagger>{/* primary content */}</div>
</div>
```

`data-stagger` gets picked up by the GSAP entrance animation in `App.tsx`. See **patterns.md → Motion choreography** for the full list of `data-*` hooks.

---

# Voice chat primitives

Realtime voice surface. All voice components share one state machine — pass the same `state` string everywhere on the surface so the orb, indicator, waveform, and controls stay in sync.

**State machine:** `idle` → `connecting` → `listening` ⇄ `thinking` ⇄ `speaking`, with `muted`, `interrupted`, `error`, `ended` as side states.

**State → status tone:**

| State | Tone | Notes |
|---|---|---|
| `idle` | `pending` | Pre-connection |
| `connecting` | `pending` | Establishing channel — orb shows rotating dashed ring |
| `listening` | `active` | User is speaking — orb breathes at 0.9s, halo pulses |
| `thinking` | `review` | Agent composing reply — orb breathes very gently |
| `speaking` | `active` | Agent is talking — orb breathes at 0.45s, amplitude-driven |
| `interrupted` | `review` | User cut in mid-reply |
| `muted` | `done` | Paused, mic off — orb at 35% opacity |
| `error` | `blocked` | Reconnecting — orb desaturated |
| `ended` | `done` | Call complete |

## VoiceOrb

```tsx
<VoiceOrb state="speaking" amplitude={0.6} size={80} />
```

| Prop | Type | Notes |
|---|---|---|
| `state` | voice state key | Required |
| `amplitude` | `0..1` | Optional. When provided, overrides the state-driven breathe with live audio level |
| `size` | px | Default `80` |
| `label` | `string \| false` | Mono caption under the orb. Pass `false` to omit |

Rules: never use the orb without a `state`; never restyle the gradient — it sources color from `--status-{tone}`.

## VoiceWaveform

```tsx
<VoiceWaveform state="listening" amplitudes={amps} bars={42} height={36} />
```

| Prop | Notes |
|---|---|
| `state` | voice state key — drives color and self-driven fallback |
| `amplitudes` | optional array of `0..1` values; when omitted the bars self-animate |
| `bars` | bar count, default `24` |
| `height` | px, default `32` |
| `tone` | override tone token (rare) |

## VoiceTurnIndicator

Pill specialized for voice state. Like `StatusPill`, but always shows the live state label plus an optional `who` (agent name) and `model` (mono caption).

```tsx
<VoiceTurnIndicator state="listening" who="Atlas" model="haiku-4.5" />
```

## VoiceCaption

A single conversational turn. The body renders in `Newsreader` at `var(--text-lg)`, capped at `var(--prose-body)`. Pass `isLive` to append a blinking caret and fade-in newly streamed words.

```tsx
<VoiceCaption speaker="agent" text="Pulling the deploy logs now…" isLive timestamp="14:02:11" />
```

| Prop | Notes |
|---|---|
| `speaker` | `"user"` or agent display name |
| `text` | streaming string — re-render with the growing transcript |
| `isLive` | true while words are still arriving |
| `timestamp` | optional mono caption under the turn |

## VoiceToolCallChip

Inline marker for a tool the agent called mid-call. Slides in from `x: -8`. Dashed border in the call's tone.

```tsx
<VoiceToolCallChip tool="search_knowledge" status="running" detail="query: 'deploy errors'" />
```

`status` is `running` (active tone, pulsing dot) | `done` (done tone) | `error` (blocked tone).

## VoiceControls

The 2- or 3-button cluster: mute / push-to-talk / hang-up. Hang-up is always the danger tone. Pass `compact` inside `VoiceDock`.

## VoiceDock

Floating dock — the always-visible compact bar.

```tsx
<VoiceDock
  state={state} agentName="Atlas" caption="Pulling deploy logs…"
  muted={muted} onMute={…} onHangUp={…} onExpand={…}
  position="bottom-right"
/>
```

| Prop | Notes |
|---|---|
| `state` | voice state |
| `agentName` | display name |
| `amplitude` | optional `0..1`, drives the inline orb |
| `caption` | one-line text shown next to the state label (latest agent utterance, or hint) |
| `muted` / `onMute` | mic toggle |
| `onHangUp` | end the call |
| `onExpand` | when set, shows an expand button — open `VoicePanel` |
| `position` | `bottom-right` (default), `bottom-left`, `bottom-center` |

Rules: max one dock on screen; positioned with `position: fixed`; entrance from `y: 24` (0.4s).

## VoicePanel

Expanded surface. Compose with `<Surface>` if you need to embed it inline; pass `fullscreen` to use it as a focus overlay.

```tsx
<VoicePanel
  state={state}
  agentName="Atlas"
  voiceName="ember" voices={["ember","alloy","echo","verse"]} onChangeVoice={…}
  amplitudes={amps}
  transcript={turns}             /* [{ speaker, text, timestamp, toolCalls? }] */
  liveText={partial} liveSpeaker="agent"
  muted={muted} onMute={…} onHangUp={…} onCollapse={…}
/>
```

Header carries the orb + name + `VoiceTurnIndicator`. Footer carries `VoiceControls` plus a one-line operator hint that varies by state. Transcript auto-scrolls to the bottom on append.

## VoiceTranscriptCard

List-row artifact for past calls — same `surface-list-item` cadence as `KnowledgeCard`. Hover micro-shifts `x: 4`. Includes duration and turn count on the right.

```tsx
<VoiceTranscriptCard
  title="Triaged the prod 502s"
  agent="Atlas" durationSec={742} turnCount={18}
  timestamp="Today · 14:01"
  summary="Walked through the last hour of error logs, scoped to the checkout pod…"
  onOpen={…}
/>
```

---

**Globals exported:** `VOICE_STATE_LABEL`, `VOICE_STATE_TONE`, `VoiceOrb`, `VoiceWaveform`, `VoiceTurnIndicator`, `VoiceCaption`, `VoiceToolCallChip`, `VoiceControls`, `VoiceDock`, `VoicePanel`, `VoiceTranscriptCard` — load `src/voice-chat.jsx` after `primitives.jsx` and `editorial-primitives.jsx`.
