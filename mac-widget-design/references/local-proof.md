# Local Proof

Use this before claiming a macOS widget is complete.

## Minimum Evidence

- Current files inspected.
- Swift build/tests passed, or the exact blocker is reported.
- Any repo-specific Python/JS tests passed when they cover parsing/cache/presentation.
- Static preview rendered if the repo provides a renderer.
- Local carrier app/extension installed.
- Widget timeline/cache refreshed with live or representative data.
- Real desktop screenshot captured with Finder active and app windows hidden.

## Desktop Screenshot Pattern

Use the repo's installer first. Then capture the desktop, not the Codex window:

```bash
osascript -e 'tell application "Finder" to activate'
osascript -e 'tell application "System Events" to keystroke "h" using {command down, option down}'
sleep 1
screencapture -x /tmp/widget-desktop-proof.png
```

If the screenshot captures another app, it is not valid proof. Repeat with Finder active and other apps hidden.

## Visual Checks

- Background is black/near-black if using this design system.
- No beige/grey whitewash unless the user explicitly asked for it.
- No hardcoded blue/cyan glass tint.
- Text and values are readable.
- Row values do not clip.
- Priority finding is visible.
- Stale/missing/unreliable data is visible.
- Selected/active desktop state is checked when the user calls it out.

## Evidence Reporting

Final responses should name the commands and artifacts, for example:

- `swift test` passed.
- `python3 .../check_widget_design.py .` passed.
- Preview: `/tmp/widget-preview.png`.
- Desktop proof: `/tmp/widget-desktop-proof.png`.
