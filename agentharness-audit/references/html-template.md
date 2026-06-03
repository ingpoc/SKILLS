# HTML report template — self-contained report artifact

The literal HTML lives in [`templates/audit.html.template`](../templates/audit.html.template). Copy that file to `docs/agentharness-audit/<harness>-audit.html`, then replace placeholder tokens. This document holds the **design rationale**, the **placeholder substitution helpers**, and the **fill-in checklist**. The audit skill must use this bundled template directly; do not regenerate the HTML from scratch and do not require loading `html-artifact` during an audit run.

## Provenance

The template was originally derived from the `html-artifact` report lane, with the gallery's `14-research-feature-explainer.html` as the structural basis. That provenance is already encoded here and in `templates/audit.html.template`; future audit runs should not load `html-artifact` unless they are changing this template itself. Tokens follow the embedded design contract: ivory paper, slate ink, clay accent, system serif/sans/mono, and zero CDN fonts.

## Design principles

1. **Feature-explainer macrostructure.** The audit *is* an explainer: "how this harness performs across 13 quality principles." The 200px sticky sidebar carries section nav (overall → scorecard → priorities → P01..P13). The principle deep-dives mirror the marginalia pattern from the gallery: main column for prose, right column for the score + citations grouped by harness.
2. **Stat-led hero.** The overall score is the hero number — large serif numeral colored by `{SCORE_CLASS}`. A short executive summary sits next to it inside a 3px clay left-border (matching the gallery's `.tldr` pattern). Four follow-up tiles count principles by class (met / near / mute / far).
3. **High data-ink ratio (Tufte).** `Found` / `Missing` / `Rec` blocks use *left-border-only* — no background fills. The `arch` block is the only filled block (soft oat tint with olive border), making the canonical-architecture reference visually distinct without being garish.
4. **Self-contained.** Zero external assets. No Google Fonts, no CDN scripts. Renders identically from `file://`, offline, and in air-gapped reviewer environments. System font stacks only (`ui-serif`, `system-ui`, `ui-monospace`).
5. **Honest scoring contract.** Every score cell carries a citation column; every principle deep-dive carries a `Found` block with file:line. The skill's hard rule #1 ("evidence before score") is enforced by the template structure — there is no place for an unsupported score.
6. **Print-ready.** `@media print` collapses the marginalia column, removes sticky positioning, and forces page-break-inside avoid on principle blocks. White paper background is already the default.
7. **Audit-only, no auto-rewrite.** Audits are point-in-time. The template has no `<!-- AUTOUPDATE: -->` fences. Re-running the audit produces a new file, not a rewrite of an old one.

## Color semantics

The four severity classes map to the [html-artifact design tokens](../../../html-artifact/references/design-tokens.md):

| Class | Score range | CSS token | Where it shows |
|---|---|---|---|
| `met`  | 9.5–10.0 | `var(--olive)` `#788C5D` | sage green — target met |
| `near` | 7.0–9.4  | `var(--clay)`  `#D97757` | clay — primary accent (good but short) |
| `mute` | 4.0–6.9  | `var(--gray-500)` `#87867F` | neutral mid |
| `far`  | 0.0–3.9  | `var(--rust)`  `#B04A3F` | rust — alarm |

The `met-tag` pill (added beside `.pname` when a principle scores ≥9.5) uses `--olive` border + label.

## Substitution helpers

```python
def score_class(score: float) -> str:
    """CSS class suffix for .sc-score-* and .pscore"""
    if score >= 9.5: return "met"
    if score >= 7.0: return "near"
    if score >= 4.0: return "mute"
    return "far"

def bar_color_token(score: float) -> str:
    if score >= 9.5: return "var(--olive)"
    if score >= 7.0: return "var(--clay)"
    if score >= 4.0: return "var(--gray-500)"
    return "var(--rust)"

def bar_pct(score: float) -> int:
    return int((score / 10.0) * 100)

def format_gap(score: float) -> str:
    gap = 9.5 - score
    if gap <= 0: return "✓"
    return f"−{gap:.1f}"

def gap_class(score: float) -> str:
    # Same buckets as score_class — keeps the gap cell color-coded by severity.
    return score_class(score)

def rec_label(score: float) -> str:
    return "To maintain 9.5+" if score >= 9.5 else "To reach 9.5"

def count_by_class(scores: list[float]) -> dict[str, int]:
    counts = {"met": 0, "near": 0, "mute": 0, "far": 0}
    for s in scores:
        counts[score_class(s)] += 1
    return counts
```

## Margin citation structure

For each principle, collect winner citations from `references/architecture.md` § Winner Reference, group them by harness, and emit one `.mcite-group` per harness that has citations.

```html
<aside class="pmargin">
  <div class="pscore near">7.2<span class="denom">/10</span></div>
  <div class="mcites">
    <div class="mcite-group">
      <span class="htag">hermes</span>
      <span class="mcite-item">agent/system_prompt.py:269–271</span>
      <span class="mcite-item">system_prompt.py:60–65</span>
    </div>
    <div class="mcite-group">
      <span class="htag">claude code</span>
      <span class="mcite-item">global CLAUDE.md (doctrine)</span>
    </div>
    <div class="mcite-group">
      <span class="htag">codex</span>
      <span class="mcite-item">codex-rs/core/src/compact.rs</span>
    </div>
  </div>
</aside>
```

If a principle has no winner citation for a given harness, **omit that `.mcite-group` entirely** — don't emit empty groups. If the audited codebase itself has a notable citation (the thing being scored), add it as its own `.mcite-group` using the harness name as the `.htag`.

## Filling the template — checklist

Placeholders in `templates/audit.html.template` and where the value comes from:

| Placeholder | Source |
|---|---|
| `{HARNESS_NAME}` | the audited harness name (e.g. `autonomous-agent-builder`) |
| `{HARNESS_NAME_LOWER}` | lowercased (used in HTML tags) |
| `{ORG_NAME}` | owning org / team (e.g. `acme`, `anthropic`) — `(unknown)` if not detectable |
| `{AUDIT_DATE}` | ISO date of the audit run |
| `{COMMIT_REF}` | `git rev-parse --short HEAD` of the audited tree at audit time |
| `{OVERALL_SCORE}` | mean of all 13 principle scores, formatted to 1 decimal |
| `{OVERALL_SCORE_CLASS}` | `score_class(overall_score)` |
| `{EXECUTIVE_SUMMARY}` | 2–4 sentence prose summary anchored in the lowest-gap finding |
| `{COUNT_MET}` / `{COUNT_NEAR}` / `{COUNT_MUTE}` / `{COUNT_FAR}` | `count_by_class(scores)` |
| `{KEY_FILE_N}` | the 4 most-cited source files from discovery (sidebar) |
| Per-principle (P01..P13): | |
| `{SCORE}` | the score, formatted to 1 decimal |
| `{SCORE_CLASS}` | `score_class(score)` → `met` / `near` / `mute` / `far` |
| `{BAR_PCT}` | `bar_pct(score)` → 0–100 |
| `{BAR_COLOR_TOKEN}` | `bar_color_token(score)` → CSS var string |
| `{GAP_CLASS}` | `gap_class(score)` |
| `{GAP}` | `format_gap(score)` → `✓` or `−X.X` |
| `{KEY_CITATION}` | primary file:line from Step 2 discovery |
| `{REC_LABEL}` | `rec_label(score)` |
| `{PRINCIPLE_ID}` / `{PRINCIPLE_ID_LOWER}` / `{PRINCIPLE_NAME}` | from `references/principles.md` |
| `{WHAT_WAS_FOUND_WITH_CODE_CITATIONS}` | discovery evidence — prose + `<code>` for file:line |
| `{WHAT_IS_ABSENT}` | the specific gap — omit the `<div class="info missing">` entirely when score ≥ 9.5 |
| `{SPECIFIC_RECOMMENDATION_WITH_FILE_LINE}` | a concrete source change ("implement Y at Z"), never "improve X" |
| `{CANONICAL_PATTERN}` / `{ANTI_PATTERN}` / `{DESIGN_RATIONALE}` | from `references/architecture.md` |
| `{WINNER_LABEL}` | comma-separated harness names with winner refs |
| `{WINNER_CITATIONS_INLINE}` | inline winner refs (`harness file:line · ...`) |
| `{HARNESS_TAG_N}` / `{FILE_LINE_NA}` | margin citation groups (see § Margin citation structure) |
| Priority stack (top 3): | |
| `{PRINCIPLE_ID_1..3}` / `{PRINCIPLE_NAME_1..3}` / `{GAP_1..3}` / `{ACTION_1..3}` | ranked by gap-to-9.5 descending |
| `{KEY_FILES_INSPECTED}` | comma-list for the footer |

## Per-principle rendering rules

1. **`met-tag` rule.** Add `<span class="met-tag">TARGET MET</span>` inside `.pname` only when score ≥ 9.5.
2. **`missing-block` rule.** Omit the entire `<div class="info missing">…</div>` when score ≥ 9.5.
3. **`rec-label` rule.** Use "To maintain 9.5+" when score = 9.5; otherwise "To reach 9.5".
4. **`mcite-group` rule.** One group per harness that has at least one citation for this principle. Never emit an empty group. The audited harness itself gets a group with its own name as the `.htag`.

## What this template intentionally does *not* include

- **No drift-detection or AUTOUPDATE fences.** Audits are point-in-time snapshots. Re-running produces a new file. If you want a comparison view, write a separate tool that reads two `*-audit.html` outputs.
- **No interactive sorting / filtering / collapsibles in the scorecard.** Operators print this. JS is limited to the IntersectionObserver that highlights the current section in the sidebar nav.
- **No CDN-loaded fonts.** Hard rule. The previous version of this template pulled three Google Fonts; that violated html-artifact's self-containment guarantee. Replaced with system stacks.
- **No assertion of hallmark conformance.** The header carries a date and the skill name, nothing more. If a future revision earns the full hallmark slop-test pass (P5 H5 E5 S5 R5 V5 plus the contrast / mobile / honest / chrome / tokens / icons / slop badge), the stamp can be added then.

## Quick sanity check after fill

Before writing the output file, verify:

- [ ] Every score has a `{KEY_CITATION}` filled (no `(none)` strings).
- [ ] Counts in the four tiles sum to 13.
- [ ] `{OVERALL_SCORE}` equals the mean of the 13 individual scores to ±0.05.
- [ ] No `{PLACEHOLDER}` strings remain in the output.
- [ ] All scores ≥ 9.5 have a `met-tag` span; all scores < 9.5 don't.
- [ ] No `.info.missing` block exists where score ≥ 9.5.
- [ ] No `.mcite-group` is empty.
