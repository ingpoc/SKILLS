---
name: macos-widget-reinstall
description: Replace a stale macOS desktop widget after its host app or WidgetKit extension changes. Use when the visible widget is cached, missing, or must be removed and added again.
---

# macOS Widget Reinstall

Use the macOS widget editor to replace a stale widget. The rendered widget is
the acceptance surface: a successful build or host-app update does not prove
that WidgetKit is displaying current data.

## Workflow

1. Capture the current widget and record what is stale or missing.
2. Open Notification Center from the system bar. If Computer Use cannot access
   the system-bar control, ask the user to open it; do not guess coordinates.
3. Click **Edit Widgets**. Once the editor is visible, target
   `com.apple.notificationcenterui` with Computer Use.
4. Remove old instances: right-click each matching widget and select
   **Remove Widget**. If a desktop widget is not exposed through accessibility,
   have the user open its context menu, then select the visible removal action.
5. In the gallery, search for the widget or host-app name, choose the intended
   size, and drag it to the desktop or Notification Center.
6. Exit editing and capture the rendered widget. Compare it with the expected
   current data; a gallery preview alone is not proof of a live update.

## Deterministic extension registration

Prefer the repository's canonical installer when it owns this sequence. If none
exists, stop the host and wait for exit; unregister installed, source, and
DerivedData copies; poll `pluginkit` until no registration remains; then install
and register only the canonical `/Applications` extension. Poll until exactly
one canonical path remains, compare built and installed widget binaries and
signatures, then launch the host.

`pluginkit -r` and `-a` settle asynchronously. Registering before removal
finishes can remove the new registration later; unregistering a byte-identical
source copy after canonical registration can also unregister the canonical
identity. Canonical registration must therefore be last.

## When to reinstall (vs reload)

Reinstall after shared-schema or widget-UI changes when the desktop instance
still shows the previous layout or fields. `WidgetCenter.reloadTimelines`,
killing `WidgetKit Extension` / `chronod`, or bumping the build number may help
but are **not** reliable acceptance by themselves — remove and re-add, then
capture the live desktop widget.

## Cache boundary

If a re-added widget still shows sample or old content, report
`widget_cache_not_refreshed`. Verify the host and widget share the same data
source, then investigate extension registration and timeline refresh separately.
Check for duplicate `pluginkit` registrations and non-canonical install paths; a
marketing or build-number bump alone is not proof the system loaded the
corrected extension. Do not claim a cache-clearing fix without visible proof.

Before treating two gallery entries as duplicate local apps, distinguish the
native Mac extension from a Continuity iPhone widget provider. Confirm each
provider's bundle identifier and source in WidgetKit/Chrono metadata; one
canonical Mac provider plus one identified remote iOS provider is not stale
registration. Remove or disable a remote provider only when the user explicitly
wants iPhone widgets hidden.

If a full-screen capture is black or inaccessible, enumerate WindowServer
windows, select the exact Notification Center window for the widget, and capture
that window by ID. Re-resolve the ID each time; the rendered widget remains the
acceptance surface.
