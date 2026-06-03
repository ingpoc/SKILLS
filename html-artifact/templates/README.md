# Templates — anthropics/html-effectiveness gallery

Twenty self-contained HTML files from `github.com/anthropics/html-effectiveness` (MIT, see `LICENSE`). Each is a starter for one use case; copy and replace content, keep tokens.

| File | Lane | Pattern |
|---|---|---|
| `00-gallery-index.html` | — | Original gallery landing page (reference for cross-linking style) |
| `01-exploration-code-approaches.html` | plan | Side-by-side code approaches |
| `02-exploration-visual-designs.html` | plan | Mockup grid (6 variations) |
| `03-code-review-pr.html` | review | Inline diff + margin annotations + severity coding |
| `04-code-understanding.html` | review | Module walkthrough |
| `05-design-system.html` | review | Tokens + component documentation |
| `06-component-variants.html` | review | State matrix for a component |
| `07-prototype-animation.html` | prototype | CSS animation with playback controls |
| `08-prototype-interaction.html` | prototype | JS-driven interaction sketch |
| `09-slide-deck.html` | report | Keyboard-navigable slides |
| `10-svg-illustrations.html` | report | Illustration-heavy explainer |
| `11-status-report.html` | report | Weekly status with metric tiles |
| `12-incident-report.html` | report | Timeline + impact + root cause |
| `13-flowchart-diagram.html` | report | SVG flowchart with margin annotations |
| `14-research-feature-explainer.html` | report | Feature explainer (codebase-specific) |
| `15-research-concept-explainer.html` | report | Concept explainer (generic) |
| `16-implementation-plan.html` | plan | Phased plan with milestones / files / risks |
| `17-pr-writeup.html` | report | PR description for pasting into GitHub |
| `18-editor-triage-board.html` | editor | Drag-drop columns with copy-as-Markdown |
| `19-editor-feature-flags.html` | editor | Form editor with dependency validation |
| `20-editor-prompt-tuner.html` | editor | Side-by-side editor with live re-render |

## Provenance

Source: `https://github.com/anthropics/html-effectiveness` (commit at clone time).
License: MIT (see `LICENSE`).
The Acme product name + all data in the templates are fictional — see the upstream README.

## How to use

1. Identify the lane (see `../SKILL.md`).
2. Pick the closest template (table above).
3. Copy to your output path. Replace content. Keep `:root` tokens unless the operator named a different brand.
4. Run `xdg-open` on the result and tell the operator the path.
