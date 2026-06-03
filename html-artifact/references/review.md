# review lane — PR review, code understanding, design system, component variants

Operator's intent: "Help me (or someone else) understand this code." Output is annotated, structured, navigable.

## Closest gallery templates

| Template | When |
|---|---|
| `03-code-review-pr.html` | PR review with inline diff + margin annotations + severity-coded findings |
| `04-code-understanding.html` | Code walkthrough — explain how a module works, key paths, gotchas |
| `05-design-system.html` | Document a design system: tokens, components, usage guidance |
| `06-component-variants.html` | Show a component in every state (default / hover / active / disabled / loading / error) |

## Preflight

1. **Get the target.** PR number / file path / module name / component name. If a PR, fetch with `gh pr view <n> --json title,body,files,additions,deletions` and `gh pr diff <n>`.
2. **Confirm reviewer audience.** "Reviewer who knows this codebase" vs "drive-by reviewer / non-engineer" changes how much context to include.
3. **Output path.** PR review → `docs/reviews/pr-<n>.html`. Code understanding → `docs/explainers/<module>.html`. Design system → `docs/design-system.html`. Component variants → `docs/components/<name>.html`. Ask if these don't exist.

## Do — PR review (template 03)

1. Header: repo line (mono) → H1 (PR title with one italic word) → meta row (`+lines / -lines · files · author · branch`).
2. **Summary panel** at top: 2–4 sentence plain-English summary of what changed and why.
3. **Findings list** — color-coded by severity:
   - `--rust` (#B04A3F) = blocking
   - `--clay` (#D97757) = should-fix
   - `--olive` (#788C5D) = nit / praise
   - Each finding: file path + line range, the diff excerpt, the comment in margin.
4. **Inline diff blocks** with green / red line backgrounds — see [patterns.md § Diff styling](patterns.md).
5. **Margin annotations** use a two-column grid: 1fr diff + 280–320px notes column (collapses to stacked on narrow viewports).
6. **Test plan** section at bottom — checkboxes the reviewer can tick after manual verification.

## Do — code understanding (template 04)

1. Header: module name + one-line purpose.
2. **Entry points** table: each public function / class with one-line summary and link to the section below.
3. **Walkthrough** — interleave prose + code excerpts. Each excerpt has a file path eyebrow (`src/foo.py · L42-L78`) and an annotated explanation in the margin column.
4. **Data flow** SVG if the module spans more than one file or talks to external services.
5. **Gotchas** section — non-obvious behavior, surprising edge cases, related issues.

## Do — design system / component variants (templates 05, 06)

1. **Tokens panel** first — show the actual CSS variables with swatches.
2. **One component per section** with all variants in a grid.
3. **Live preview** — render the real HTML inline, not a screenshot. Each variant gets its own `<div>` styled with the tokens.
4. **Code excerpts** under each preview showing the canonical usage.

## Closeout

1. `xdg-open <path>`.
2. State path. If a PR, also tell the operator they can post the URL into the GitHub PR conversation as a single-link review.

## Anti-patterns

- **Rendering screenshots of diffs.** Render the actual diff as HTML so reviewers can copy code from it.
- **All findings same severity.** Severity is the whole point — color-code or don't bother.
- **Margin annotations only on desktop.** Collapse gracefully — on narrow viewports, annotations become inline blocks under the code, not hidden.
