---
name: skill-profile
description: >
  Use when managing ~/.codex/skills as a Git-backed profile library: switch to
  the branch matching the current project, create that branch from main when
  missing, keep this skill present in every profile branch, and import missing
  required skills from main.
---

# Skill Profile

## Purpose

Manage `~/.codex/skills` as a branch-profiled skill library.

- `main` = canonical library with all skills.
- `<project-name>` branch = active subset for that project.
- `skill-profile` = bootstrap skill; keep it on every profile branch.

Use this skill when the user asks to switch skill sets for a project, create a project skill branch, add a missing skill to the current profile, or check whether a skill exists on `main`.

## Ground Rules

- Work in `~/.codex/skills` unless the user gives another skills repo.
- Derive profile name from the project repo basename unless the user provides one.
- Never overwrite dirty work. Run `git status --short --branch` first; stop if unrelated changes would be affected.
- Do not delete skills during setup unless the user explicitly asks to prune.
- Shared skill edits flow back to `main`; profile branches select skills, they do not become permanent forks.
- Keep `skill-profile` in every branch. When creating a profile branch, verify this directory exists before ending.

## Quick Checks

```bash
python3 ~/.codex/skills/skill-profile/scripts/profile_status.py --repo ~/.codex/skills
python3 ~/.codex/skills/skill-profile/scripts/profile_status.py --repo ~/.codex/skills --skill <skill-name>
```

The script is read-only. Use it before branch changes or when a requested skill is missing.

## Switch Or Create Project Profile

1. Identify profile:
   - explicit user name wins;
   - else current project basename, e.g. `samantha-mac`.
2. Inspect:
   ```bash
   git -C ~/.codex/skills status --short --branch
   git -C ~/.codex/skills branch --list <profile>
   ```
3. If branch exists:
   ```bash
   git -C ~/.codex/skills switch <profile>
   ```
4. If missing:
   ```bash
   git -C ~/.codex/skills switch main
   git -C ~/.codex/skills switch -c <profile>
   test -d ~/.codex/skills/skill-profile
   git -C ~/.codex/skills status --short --branch
   ```
5. If the user wants a minimal branch, ask for the seed skill list or infer from the current project's repo-local skills. Remove unneeded skills only with explicit approval.

## Import A Missing Skill From Main

Use when the active profile lacks a skill the project needs.

1. Check active profile and main:
   ```bash
   python3 ~/.codex/skills/skill-profile/scripts/profile_status.py --repo ~/.codex/skills --skill <skill-name>
   ```
2. If `main_has_skill=true`, copy from `main` into the active profile:
   ```bash
   git -C ~/.codex/skills checkout main -- <skill-name>
   git -C ~/.codex/skills status --short -- <skill-name>
   ```
3. If `main_has_skill=false`, search names on main:
   ```bash
   git -C ~/.codex/skills ls-tree -d --name-only main | rg '<keyword>'
   ```
4. If still missing, say the skill is not in `main`; create it only if the user asks.

## Copy From Project Back To Main

Use only for shared skill improvements, not project-specific customization.

```bash
git -C ~/.codex/skills switch main
git -C ~/.codex/skills checkout <profile> -- <skill-name>
git -C ~/.codex/skills status --short -- <skill-name>
```

Review the diff before committing. If the change is project-specific, keep it on the project profile branch.

## Closeout

Report:

- active branch before/after;
- created or switched branch;
- skills imported from `main`;
- whether `skill-profile` exists in the active branch;
- dirty files left for the user to review.
