---
name: html-artifact
description: "Produce a single self-contained HTML file as the deliverable for information-dense tasks that benefit from tables, SVG diagrams, inline code annotations, side-by-side comparisons, tabs, interactive controls, or copy-back affordances. Lanes: plan, review, report, prototype, editor. Use when the operator asks for an HTML artifact, HTML file, single-page HTML, HTML explainer, HTML spec, PR review in HTML, incident or status report as HTML, implementation plan in HTML, feature explainer, concept explainer, flowchart, SVG diagram, slide deck, design-system docs, component variant gallery, drag-drop triage board, feature-flag admin UI, prompt tuner, shareable explainer, or throwaway UI/editor. Do not use for high-design marketing pages or production apps."
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion
---

# html-artifact — single-file HTML as the output medium

> **Self-validate after edits.** Any change to this skill's files (SKILL.md, scripts/, references/, templates/) must be followed by `./scripts/validate.sh` from the skill directory. Hard findings → create-skill Optimize lane.

Use HTML, not Markdown, when the deliverable carries multiple representations (prose + diagram + code + data) or when the operator will share it as a link. The output is **one** self-contained `.html` file with inline CSS + JS — no build, no CDN where avoidable, no external assets. Default visual system matches the `anthropics/html-effectiveness` gallery (ivory paper, slate ink, clay accent, serif headlines, sans body, mono labels) — see [references/design-tokens.md](references/design-tokens.md).

## Entry — pick a lane

First action is `AskUserQuestion` unless the typed prompt names a lane:

| Lane | When to choose | Procedure |
|---|---|---|
| **plan** | Implementation plan, approach exploration, mockup grid, design exploration | [references/plan.md](references/plan.md) |
| **review** | PR review, code walkthrough, design-system doc, component variant gallery | [references/review.md](references/review.md) |
| **report** | Status / incident / PR write-up, feature or concept explainer, slide deck, flowchart, SVG illustration | [references/report.md](references/report.md) |
| **prototype** | Animation or interaction sketch (HTML mock, not final React/Swift) | [references/prototype.md](references/prototype.md) |
| **editor** | Throwaway single-use editing UI with export-back-to-Claude | [references/editor.md](references/editor.md) |

Skip the question when the typed prompt names a lane unambiguously:

| Phrase pattern | Lane |
|---|---|
| "plan / spec / approach exploration / mockup grid in HTML" | plan |
| "PR review / code review / code understanding / design system in HTML" | review |
| "status / incident / weekly / PR write-up / explainer / slide deck / flowchart in HTML" | report |
| "prototype / animate / sketch interaction in HTML" | prototype |
| "editor / triage / drag-drop / flag UI / prompt tuner in HTML" | editor |
| anything ambiguous ("HTML artifact for X") | **Ask.** |

## Hard rules (universal — apply to every lane)

1. **One file.** Inline `<style>` and `<script>`. No external CSS, no `<script src=…>` to local files. CDN scripts allowed only when their absence would degrade the artifact materially (Chart.js, Prism.js) and only after asking the operator — most artifacts need none.
2. **Self-contained on disk.** The file must render correctly from `file://` and `xdg-open` — no fetch() to external endpoints, no asset paths.
3. **Default to the gallery design system.** Use the palette + typography in [references/design-tokens.md](references/design-tokens.md) unless the operator gives a different brand. Override the tokens, not the structural patterns.
4. **Honest content.** No fabricated metrics, testimonials, logos, or counts. If the operator hasn't supplied a number, use `—` plus a `data-placeholder` note or omit the panel. (Same rule hallmark enforces.)
5. **Editor lane requires export-back.** Every interactive editor MUST end with one or more buttons that copy the edited state to the clipboard as JSON, Markdown, prompt text, or diff — so the operator can paste back into Claude. Without it, the artifact is a dead end.
6. **Closeout: open the file.** After writing, run `xdg-open <file>` (or `open` on macOS) so the operator sees the result. State the file path in the final message.
7. **Pre-flight: is HTML actually right?** If the brief is ≤ 200 words of plain prose with no diagram, no code, no comparison, and no interactivity, bail out and tell the operator "Markdown is fine for this — want HTML anyway?"

## Templates — 20-file starter gallery

`templates/` contains the full `anthropics/html-effectiveness` gallery (MIT). Each lane procedure names the closest matches. Default workflow: copy the closest template, replace content, keep tokens.

| File | Category | Use for |
|---|---|---|
| `01-exploration-code-approaches.html` | plan | Side-by-side code approach comparison |
| `02-exploration-visual-designs.html` | plan | Mockup grid for design variations |
| `03-code-review-pr.html` | review | PR with inline diff + margin annotations |
| `04-code-understanding.html` | review | Code walkthrough / explainer |
| `05-design-system.html` | review | Design-system documentation |
| `06-component-variants.html` | review | Component state matrix |
| `07-prototype-animation.html` | prototype | CSS animation sketch |
| `08-prototype-interaction.html` | prototype | JS interaction sketch |
| `09-slide-deck.html` | report | Slide presentation |
| `10-svg-illustrations.html` | report | Illustrated SVG explainer |
| `11-status-report.html` | report | Weekly / status update |
| `12-incident-report.html` | report | Incident post-mortem |
| `13-flowchart-diagram.html` | report | SVG flowchart |
| `14-research-feature-explainer.html` | report | Feature explainer |
| `15-research-concept-explainer.html` | report | Concept explainer |
| `16-implementation-plan.html` | plan | Phased implementation plan |
| `17-pr-writeup.html` | report | PR description / write-up |
| `18-editor-triage-board.html` | editor | Drag-drop triage board |
| `19-editor-feature-flags.html` | editor | Feature-flag admin UI |
| `20-editor-prompt-tuner.html` | editor | Live prompt tuning UI |
| `00-gallery-index.html` | — | Original gallery landing page |

## Cross-references

- [references/plan.md](references/plan.md) — plan lane (Preflight / Do / Closeout)
- [references/review.md](references/review.md) — review lane
- [references/report.md](references/report.md) — report lane
- [references/prototype.md](references/prototype.md) — prototype lane
- [references/editor.md](references/editor.md) — editor lane (export-back is mandatory)
- [references/design-tokens.md](references/design-tokens.md) — shared `:root` palette + font stacks
- [references/patterns.md](references/patterns.md) — reusable CSS/JS recipes (two-column grid, eyebrow header, inline SVG sparkline, details/summary, drag-drop, clipboard export)
- [references/auto-update-regions.md](references/auto-update-regions.md) — fenced-region pattern for explainers a closeout script must refresh (precedent: autoresearch)
- Sibling skills:
  - **`playground`** — when the artifact's purpose IS the live knob-tuning loop (controls → preview → prompt → copy). html-artifact `editor` lane is for editing data; `playground` is for editing parameters.
  - **`hallmark`** — when visual-design quality is the goal (marketing page, component polish, brand surface). html-artifact uses a fixed design system; hallmark picks one.

## Why this skill exists

The 2026-05 Anthropic blog post *"The unreasonable effectiveness of HTML"* (Thariq Shihipar) argues Claude Code's outputs should default to HTML because Markdown loses tables/SVG/interactivity/shareability past ~100 lines. Without this skill the model defaults to Markdown for plans, reviews, reports, and editors — losing information density and the export-back loop that keeps the operator in the loop. This skill encodes the gallery's conventions (Acme/Anthropic palette, eyebrow → serif H1 → sans body, 1.5px / 10-12px borders, two-column body + 300px sidebar, `<details>` collapsibles, clipboard export) so each artifact looks made instead of generated.
