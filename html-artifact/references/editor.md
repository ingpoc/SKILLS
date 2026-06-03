# editor lane — throwaway single-use editing UI with export-back

Operator's intent: "I have a specific data-editing task that's awkward in a text editor. Build me a small UI for it — once." Output is single-use, not a product. The point is the **export back to Claude**: the operator edits, then pastes the result into a new prompt.

## Closest gallery templates

| Template | When |
|---|---|
| `18-editor-triage-board.html` | Drag-drop cards across columns (Now / Next / Later / Cut). For ticket triage, feature buckets, test-case ordering. |
| `19-editor-feature-flags.html` | Form-based config editor with toggles, dependency warnings, validation. For feature flags, env config, JSON/YAML editing. |
| `20-editor-prompt-tuner.html` | Side-by-side prompt editor with live re-render of sample inputs. For prompt iteration, template tuning. |

Use these directly when the use case matches. For unusual use cases, pick the closest by pattern (drag-drop / form / side-by-side) and adapt.

## Hard rule — export-back is mandatory

**Every editor MUST end with one or more export buttons that put the edited state on the clipboard in a Claude-pasteable format.** Without it, the artifact is a dead end. Acceptable formats:

| Button label | Format | Use for |
|---|---|---|
| `Copy as JSON` | minified or pretty JSON | structured configs |
| `Copy as Markdown` | bulleted list / table | ordered lists, prioritized buckets |
| `Copy as prompt` | natural-language instruction | "Update the flags as follows: X=on, Y=off because Z" |
| `Copy as diff` | unified diff | config-file edits |
| `Copy as YAML` | YAML | when input was YAML |

Buttons appear in a **sticky toolbar** at the bottom (or top-right of the page), always visible. Each button uses `navigator.clipboard.writeText` and shows a brief "Copied!" pill — see [patterns.md § Clipboard export](patterns.md).

## Preflight

1. **Get the input data.** Either the operator pastes it inline, names a file to read, or describes the schema. If it's a file, `Read` it before generating the editor.
2. **Confirm the output format.** What does the operator want back? JSON? Markdown list? Diff?
3. **Output path.** `/tmp/editor-<slug>.html` unless the operator says otherwise.

## Do

1. **Header** with one-line context: what's being edited, where the data came from.
2. **Hint line** — single mono line listing keyboard shortcuts / drag affordances.
3. **The editor surface** — chosen by pattern:
   - **Drag-drop board** (template 18): HTML5 dnd API, columns are `<section>` with `<article>` cards.
   - **Form editor** (template 19): `<fieldset>` per group, dependency warnings as `<output>` next to fields.
   - **Side-by-side editor** (template 20): two-column grid, textarea + live preview.
4. **Validation + warnings** rendered inline next to the offending field, color `--rust` for errors, `--clay` for warnings.
5. **Sticky export toolbar** — one or more `Copy as …` buttons + a "Copied!" pill that appears for ~1.5s.
6. **Initial state populated** from the input data the operator gave you. Never start blank if input was provided.

## State management

Single source of truth — a JS object mutated by every control. Every render reads it; every export serializes it:

```js
const state = { /* schema-shaped object */ };
const els = { /* cached element refs */ };
function render() { /* paint from state */ }
function exportJSON() { return JSON.stringify(state, null, 2); }
function exportMarkdown() { /* ... */ }
```

## Closeout

1. `xdg-open <path>`.
2. State path. Remind the operator: edit in the browser, click the right export button, paste back into Claude.

## Anti-patterns

- **No export button.** Hard rule. Without it the editor is useless — the operator can't get the edits back to you.
- **External fetch / save endpoint.** Editor is throwaway and offline. State lives in memory; export is the only egress.
- **Trying to be a product.** This is a one-shot tool for one operator for one task. No user accounts, no persistence beyond clipboard.
- **Hidden / behind-a-button export.** Toolbar is sticky and visible. The operator should never have to hunt for "how do I get my edits back".
- **Empty state UI.** If input data exists, the editor renders it on load. Empty editors are wireframes, not deliverables.
