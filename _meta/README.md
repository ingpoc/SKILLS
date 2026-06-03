# Skill Source Catalog

This folder is the machine-local source of truth for skill ownership.

## Fields

- `surface`: where the runtime sees the skill (`codex-root`, `codex-system`, `claude`)
- `class`: ownership class
  - `vendor`: downloaded from upstream and safe to auto-refresh
  - `system`: shipped by Codex; audit for drift but do not overwrite automatically
  - `custom`: local or user-authored authority; never auto-refresh
- `update_policy`
  - `auto`: refresh from upstream when upstream differs
  - `audit_only`: compare against upstream and report drift only
  - `manual`: do not touch automatically

## Invariant

Never edit an upstream-managed skill in place if you want to keep local changes.
Fork it under a new custom name instead.
