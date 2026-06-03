# auto-update regions — fenced HTML zones a script can rewrite

The pattern for artifacts that are **part hand-curated, part regenerated**: a human writes the prose, an automated closeout rewrites the live data. Used when an artifact is a "living document" — for example, an explainer where the architecture and FAQ are stable but the metrics, table rows, and scatter points must reflect the latest run.

## When to use this pattern

- The artifact has a stable conceptual frame the operator authors once.
- Inside that frame, specific zones (tables, SVG points, summary stats) must change every time a closeout script runs.
- Two-file split (one hand-curated + one generated) would force readers to know about both and risks them drifting out of sync.

If only data changes ever → just emit a fresh file each time. If only prose changes ever → it's not auto-updateable. The fence pattern earns its keep only in mixed-ownership artifacts.

## The fence

Use HTML comments with a named region. Always paired, always versioned.

```html
<!-- AUTOUPDATE:baseline-summary v=1 -->
<div class="stats">
  <div class="stat"><div class="num">216,497</div><div class="lab">μ</div></div>
  <!-- … -->
</div>
<!-- /AUTOUPDATE:baseline-summary -->
```

Rules:

1. **Always paired.** A missing closing fence is a fatal error. The updater script must refuse to write and exit non-zero.
2. **Named.** Every region has a unique slug (`baseline-summary`, `iterations-table`, `scatter-points`). Names are stable contracts.
3. **Versioned** with `v=N`. Bump when the inner schema changes — the updater can refuse to write into a version it doesn't recognize.
4. **No nested fences.** A region cannot contain another AUTOUPDATE region.
5. **Inside `<body>` only.** Don't fence the `<head>`, `<style>`, or `<script>` blocks — those should stay stable.

## The updater script

A deterministic Python script (~30 lines + parsing). Skeleton:

```python
import re, pathlib, sys

FENCE = re.compile(
    r"(<!-- AUTOUPDATE:(?P<name>[a-z0-9-]+) v=(?P<v>\d+) -->)"
    r"(?P<body>.*?)"
    r"(<!-- /AUTOUPDATE:(?P=name) -->)",
    re.DOTALL,
)

def rewrite(path: pathlib.Path, regions: dict[str, str]) -> None:
    text = path.read_text()
    seen = set()
    def repl(m):
        name = m.group("name")
        seen.add(name)
        if name not in regions:
            return m.group(0)            # leave untouched
        return f'{m.group(1)}\n{regions[name]}\n{m.group(4)}'
    new = FENCE.sub(repl, text)
    missing = set(regions) - seen
    if missing:
        sys.exit(f"AUTOUPDATE: regions not found in {path}: {missing}")
    path.write_text(new)
```

## Drift checks (not auto-rewrites)

Some content is structural enough that it shouldn't auto-rewrite but should fail-loud on drift. Example: an architecture table that lists every script in a directory. The closeout script should:

1. Scan the source-of-truth (filesystem, manifest, etc.).
2. Compare against what the artifact claims.
3. **Print a drift warning, do not rewrite.** Architecture changes deserve operator framing.

Drift checks pair well with fenced regions: the script rewrites data, warns on structural drift.

## What stays human-owned

A reliable test: *would a fresh closeout, run on its own, produce sensible artifact prose?* If no, the section is human-owned and stays outside fences. Examples that should stay outside:

- Section headings, the narrative arc, the FAQ
- Architecture descriptions (use drift checks instead)
- Anything answering "why" rather than "what is the current state"
- Hand-picked highlights (e.g., the top 5 ideas from a list of 30 — ordering implies judgment)

## Example: precedent in this repo

The autoresearch explainer at `docs/autoresearch/autoresearch-explainer.html` uses fences for:

- `baseline-summary` — the four stat tiles + commit ref
- `baseline-scatter` — the SVG data points (axes stay static, only `<circle>` elements update)
- `baseline-raw-rows` — `<tbody>` of the raw-runs table
- `iterations-list` — the iterations history (latest 10 + collapsed older runs)

Rewriter: `.codex/skills/autoresearch/scripts/render_iterations.py`. Triggered by lane closeouts in the autoresearch skill.

## Why this beats two files

| | Two files | One file with fences |
|---|---|---|
| Reader entry | Must know about both | Single link |
| Drift between concept + data | Real | Impossible by construction |
| Update mechanism | Whole-file rewrite | Region-scoped rewrite |
| Diff readability | Whole-file replace | Section-scoped diffs |
| Risk of stomping prose | None | Mitigated by named fences + fail-loud |
| Right call when… | Files have independent lifecycles | Files would always be opened together |
