# Mac Widget Design System

Use this for compact health, productivity, status, finance, and operational desktop widgets. The target is a native macOS desktop widget that reads clearly over any wallpaper without becoming a pale card.

## Visual Contract

- Authored background: black or near-black. A good starting point is `Color.black.opacity(0.94)` to `Color.black.opacity(0.88)` in `containerBackground(for: .widget)`.
- Avoid beige, cream, sand, cyan, blue glass, decorative blur washes, and one-note gradients.
- If transparency is required, let macOS and the wallpaper supply color. Do not paint the widget blue to simulate glass.
- Use `.containerBackground(for: .widget)` for the real widget background. Use preview-only fallback backgrounds separately.
- Be careful with `.ultraThinMaterial` on desktop widgets: it can produce the pale/grey/whitewashed state. If used, pair it with a strong black overlay and verify on the actual desktop.

## Layout

- First read: widget name/status plus one priority finding.
- Second read: compact dashboard rows with aligned values.
- Density is expected. Do not build marketing cards, nested cards, hero sections, or decorative panels inside the widget.
- Prefer direct labels over legends. Example: `Sleep`, `6h 50m; inspect caffeine/meals`, `80`.
- Use mini meters only when they encode a real numeric signal. Keep them 2-3 px high.
- Separators should be low-contrast and functional, not decorative.
- Use stable row heights and fixed value columns so values do not shift.

## Color And State

- Semantic accents only:
  - `red`: attention/critical/risk
  - `orange`: watch/degraded/missing context
  - `green`: good/fresh/healthy
  - `white/gray`: neutral or unavailable
- Do not color the entire widget by status. The surface stays black; accents carry state.
- Missing data is a state, not blank space. Use `--`, `No signal`, `Unavailable`, `Stale`, or domain-specific text.
- For selected/active or tinted rendering modes, verify the actual desktop. WidgetKit may alter appearance beyond what static previews show.

## Typography

- Use system fonts.
- Avoid viewport-scaled typography.
- Use bold only for scan anchors: app name, priority headline, row title, row value.
- Keep detail text readable but secondary; do not let it compete with values.
- Use `lineLimit` and `minimumScaleFactor` on row labels/values.

## Anti-Patterns

- Blue/cyan “glass” backgrounds that look good in isolation but fail against real desktop states.
- Beige or grey material cards that turn into active-state whitewash.
- Multiple cards inside the widget.
- Decorative charts with no decision value.
- Hiding stale sync, dead battery, or missing sensor data because the main score still looks fine.
