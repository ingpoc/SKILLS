# report lane — status, incident, write-up, explainer, slides, diagrams

Operator's intent: "Synthesize what I know about X into a thing I can share." Output is a single readable document — often the link gets pasted into Slack / a ticket / an email.

## Closest gallery templates

| Template | When |
|---|---|
| `09-slide-deck.html` | Presentation slides — keyboard-navigable, one idea per slide |
| `10-svg-illustrations.html` | Illustrated SVG explainer — concept-heavy, image-heavy |
| `11-status-report.html` | Weekly / sprint / project status with progress indicators |
| `12-incident-report.html` | Incident post-mortem — timeline, impact, root cause, follow-ups |
| `13-flowchart-diagram.html` | SVG flowchart with annotations in a margin column |
| `14-research-feature-explainer.html` | How a specific feature works in this codebase |
| `15-research-concept-explainer.html` | How a general concept works (less codebase-specific) |
| `17-pr-writeup.html` | PR description / write-up — context, change list, test plan |

## Preflight

1. **Get the source material.** What does the operator know that needs synthesizing? — Slack threads, git history, code reads, existing docs.
2. **Pick template by output type** (table above).
3. **Output path.** Defaults:
   - status → `docs/status/<YYYY-MM-DD>.html`
   - incident → `docs/incidents/<id>.html`
   - explainer → `docs/explainers/<topic>.html`
   - slides → `docs/decks/<topic>.html`
   - flowchart → `docs/diagrams/<topic>.html`
   - PR write-up → paste-into-GitHub, save to `/tmp/pr-<n>-writeup.html`

## Do — status / incident / PR write-up (templates 11, 12, 17)

Common structure:
1. **Header** with TL;DR (2–3 sentences in `--gray-700`, max 620px wide).
2. **Key metrics** row — small tiles, mono numbers, sub-label in `--gray-500`. Honest content rule applies hard here: no fabricated metrics. If a number isn't available, write `—`.
3. **Timeline** for incidents — vertical list with mono timestamps, event description.
4. **Detail sections** with eyebrow + serif H2.
5. **Follow-ups / action items** table at the bottom with owner column.

## Do — explainer (templates 14, 15)

1. **Lead with a single SVG** that captures the whole idea visually — if the explainer doesn't have one, it's the wrong artifact.
2. **Layered sections** — each section explains one mechanism, with annotated code excerpts and a small inline diagram if relevant.
3. **"Gotchas" panel** at the end — non-obvious things that bite people.
4. **Margin notes** for caveats / asides — keeps the main column readable.

## Do — flowchart / SVG illustrations (templates 10, 13)

1. **One SVG dominates the page** — at minimum 640px wide, properly viewBox'd.
2. **Annotations in a margin column** to the right (collapses below at narrow widths).
3. **Use tokens inside SVG** via `<style>` inside the SVG — `fill: var(--clay);` works.
4. **Real numbers, not decorative shapes.** If the flowchart has metrics, they come from data. See [patterns.md § Inline SVG diagrams](patterns.md).

## Do — slide deck (template 09)

1. **One idea per slide** — slide content fits one viewport.
2. **Keyboard nav** — arrow keys / space. Wire it in JS.
3. **Slide counter** in the corner, mono small.
4. **Print-friendly** — `@media print` rules so slides print as handout.

## Closeout

1. `xdg-open <path>`.
2. State path. For PR write-ups, mention they can paste sections into the GitHub PR body.

## Living explainers (auto-updated by a closeout script)

If the operator is producing an explainer whose data must refresh every time a closeout runs — e.g. a baseline summary, a scatter plot of latest runs, an iterations history — use the **fenced-region pattern** instead of regenerating the whole file. See [auto-update-regions.md](auto-update-regions.md).

In short: hand-curate the prose, fence the data zones with `<!-- AUTOUPDATE:name v=1 -->`, and write a deterministic Python rewriter that updates only the fenced bytes. The autoresearch explainer (`docs/autoresearch/autoresearch-explainer.html` + `render_iterations.py`) is the in-repo precedent.

## Anti-patterns

- **Status report with no numbers.** Either the operator gave you data or this isn't a status report.
- **Explainer that's all prose.** If there's no diagram and no code, just write Markdown — bail out.
- **Slides crammed with text.** One idea per slide; if you can't fit, split.
- **Decorative SVG with no information.** Every shape carries meaning or it gets cut.
