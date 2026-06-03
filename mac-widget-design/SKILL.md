---
name: mac-widget-design
description: "Use when creating, updating, or verifying a local macOS WidgetKit widget, especially desktop widgets with a native black dashboard visual system, reliable local install/run workflow, app-group snapshot/cache internals, timeline reloads, and real desktop screenshot proof."
---

# Mac Widget Design

Build or retrofit macOS WidgetKit widgets that run locally, look native on the desktop, and have reliable data internals. Prefer updating an existing widget when the repo already has a carrier app, Widget extension, shared Swift package, or installer; create a new local widget only when no suitable surface exists or the user asks for a fresh widget.

## Decision Tree

1. **Existing widget present**: inspect `Package.swift`, `.xcodeproj`, `WidgetBundle`, `WidgetConfiguration`, `*Widget*.swift`, app-group IDs, cache writers, and install scripts. Update the current surface.
2. **No widget present**: create a native macOS carrier app plus WidgetKit extension. Use SwiftPM for shared core code and preview/test utilities, but do not assume SwiftPM alone can install a WidgetKit extension.
3. **Design-only request**: still check WidgetKit background behavior and desktop proof; widget design cannot be trusted from static preview alone.
4. **Internals-only request**: still verify the visible failure states; stale data, dead ring/battery, missing sensor timestamps, and unavailable metrics must be visible.

## Load References

- For visual layout and colors, read `references/design-system.md`.
- For WidgetKit architecture, local running, cache, and data safety, read `references/internals.md`.
- Before final verification, read `references/local-proof.md`.

## Required Workflow

1. Retrieve current repo context before editing:
   - `rg --files -g 'Package.swift' -g '*.xcodeproj' -g '*.swift' -g '*install*' -g '*Widget*'`
   - `rg 'WidgetBundle|WidgetConfiguration|containerBackground|AppGroup|WidgetCenter|TimelineProvider|AppIntentTimelineProvider'`
2. Choose **update** or **create** explicitly. For an existing widget, keep existing bundle IDs, app-group IDs, signing setup, installer style, and cache locations unless they are broken.
3. Apply the black dashboard design system:
   - Use a black or near-black widget surface for the authored background.
   - Do not hardcode beige, cyan, blue glass, decorative gradients, or wallpaper-colored washes.
   - Use color only as semantic signal accents: red/orange/green/neutral.
   - Keep the layout data-first: priority summary, compact aligned rows, direct labels, small progress meters, minimal separators.
4. Implement or preserve reliable internals:
   - Widget reads cached snapshots; the app/sync command owns network calls.
   - Cache to app-group storage and at least one local fallback that the widget can read in local/dev installs.
   - Show stale/missing/unreliable data as a visible state, not as a healthy state.
   - Surface low/dead battery, missing sensor timestamp, stale sync, and failed refresh.
   - Trigger WidgetKit timeline reloads after cache writes or local install.
5. Run deterministic checks:
   - Use repo tests/builds first.
   - Run `python3 ~/.codex/skills/mac-widget-design/scripts/check_widget_design.py <repo-root>` after the widget files exist.
6. Prove the real widget:
   - Render a preview if the repo supports one.
   - Install the local carrier app/extension.
   - Capture the actual desktop widget with Finder active and app windows hidden.
   - Treat the desktop capture as authoritative for background, selected/inactive states, clipping, and legibility.

## Completion Standard

Do not call the widget done from a SwiftUI preview alone. A valid finish needs current code inspection, tests/builds, local install evidence, and a real desktop screenshot showing the widget running with live or representative cached data.
