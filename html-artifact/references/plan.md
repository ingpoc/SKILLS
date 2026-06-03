# plan lane — implementation plan, approach exploration, mockup grid

Operator's intent: "I'm about to start building X — help me think through it." Output is something the operator (and reviewers) will actually read before code is written.

## Closest gallery templates

| Template | When |
|---|---|
| `01-exploration-code-approaches.html` | Compare 2–4 implementation approaches with code excerpts side-by-side |
| `02-exploration-visual-designs.html` | Mockup grid — multiple UI directions to choose between |
| `16-implementation-plan.html` | Phased plan with milestones, files touched, risks, open questions |

## Preflight

1. **Get the brief.** What is being built / changed? What constraints? If unclear, ask via `AskUserQuestion` — don't guess.
2. **Pick template by sub-mode**:
   - "explore approaches" / "compare options" → `01`
   - "explore designs" / "mockup grid" / "6 different X" → `02`
   - "implementation plan" / "phased plan" / "break down X" → `16`
   - If the brief is "plan AND mockups" → use `16` as the spine, embed mockup grid pattern from `02` inside one section.
3. **Choose output path.** Default `docs/plans/<slug>.html` if the repo has a `docs/` tree; otherwise ask. Never overwrite without confirmation.

## Do

1. **Copy the template** to the chosen path.
2. **Replace content top-down**, keeping the structural skeleton:
   - Eyebrow (`PLAN · <area> · <date>`) → H1 (with one italic `<em>` word in `--clay`) → lead paragraph
   - Section 1: problem framing
   - Section 2: approach(es) — for `01`-style, a 2–4 column grid with code excerpts; for `16`-style, a phased timeline
   - Section 3: data flow / architecture — inline SVG if there's a diagram, otherwise table or `<pre>`
   - Section 4: files touched (`<table>` with file path + change summary)
   - Section 5: risks / open questions
   - Section 6: rollout / verification
3. **Keep the tokens.** Replace copy and structure inside sections; do not change `:root` colors or font stacks unless the operator named a different brand.
4. **Honest content rule.** No invented stats ("3× faster"), no fake stakeholders, no fake URLs. If a number isn't supplied, write `—` and label "to confirm".
5. **Code excerpts** go in `<pre><code>` with `--mono` and `--gray-150` background. Annotate by wrapping with `<mark>` (clay underline) — see [patterns.md § Code annotation](patterns.md).

## Closeout

1. `xdg-open <path>` (or `open` on macOS) so the operator sees it.
2. State the file path in the final message. Mention which template was used as the basis.
3. If the plan implies follow-up artifacts (e.g. "and a separate spec for the API"), suggest them — don't generate them unless asked.

## Anti-patterns specific to plan

- **Single-column wall of text.** A plan is a comparison/structure artifact; use grids, tables, and side-by-sides.
- **No diagram when data flow matters.** If the plan involves more than one service or store, draw the data flow inline as SVG.
- **Fabricated phase durations.** "Phase 1: 2 weeks" with no source. Either the operator gave durations or label them "estimate / to confirm".
