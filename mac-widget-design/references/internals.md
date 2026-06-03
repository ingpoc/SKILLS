# WidgetKit Internals

Use this when creating or updating the code path that makes a macOS widget run locally and show trustworthy data.

## Architecture

- The Widget extension should render from local cached data. Avoid doing primary network fetches inside the timeline provider.
- A carrier app, menu app, CLI, launch agent, or sync command should fetch remote data and write a normalized snapshot.
- Shared Swift package/core modules should own parsing, normalization, presentation, and tests.
- Widget view code should consume a presentation model, not raw API payloads.

## Local Cache

Implement candidate cache locations so local installs survive app-group or container quirks:

- Preferred: app-group container URL.
- Fallback: user Application Support path for the app/group.
- Optional mirror: Widget extension container path if the local install needs it.

The widget timeline provider should try candidate URLs in order and render an explicit failure snapshot if none are readable.

## Data Trust

Widgets must not silently reassure when data is incomplete.

- Stale sync: visible status and dashboard row when material.
- Missing sensor timestamp: visible status.
- Low/dead battery: visible status; critical/dead should outrank normal health rows.
- Unavailable metric: visible `--` and short reason.
- Old snapshot: show age/stale state rather than `Ready`.

## Timeline Reloads

After writing cache data, trigger WidgetKit reloads from the host app or local installer:

```swift
WidgetCenter.shared.reloadAllTimelines()
// or WidgetCenter.shared.reloadTimelines(ofKind: "YourWidgetKind")
```

Do not rely on the user reopening the widget gallery to see data changes.

## Creation Checklist

For a fresh local widget:

- Native macOS app target as the hidden or lightweight carrier.
- WidgetKit extension target.
- Shared core package/module for snapshot model, presenter, and view.
- Local preview renderer if practical.
- Install script that builds, installs to `~/Applications` or the expected local app path, refreshes cache, enables/refreshes the extension, and reloads timelines.
- Tests for parsing, presentation, cache candidate ordering, stale data, and failure states.

## Update Checklist

For an existing widget:

- Preserve bundle identifiers, app-group IDs, signing, installer semantics, and user cache locations unless broken.
- Add missing fallback cache paths instead of replacing the only current path.
- Add explicit presentation tests before changing risk ordering.
- Keep network/API changes outside the Widget extension unless the existing architecture requires otherwise and the risk is understood.
