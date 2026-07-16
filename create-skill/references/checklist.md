# Audit checklist — what each check asserts and how to fix

`scripts/audit.py` produces findings under fixed check IDs. This table is the source of truth for what each one means and what to do about it. Use it to interpret audit JSON output during the Optimize lane.

## Legend

- **Severity**: `hard` blocks (exit 1). `soft` warns (exit 0 by default; promoted to hard under `--strict`).
- **Status**: `pass` (clean), `warn` (soft finding), `fail` (hard finding under current mode).

## Checks

| Check ID | Severity | What it asserts | Why it matters | Fix |
|---|---|---|---|---|
| `readable` | hard | The SKILL.md file exists and is readable. | Without this nothing else is meaningful. | Restore from git, or scaffold a new one via Create lane. |
| `frontmatter_present` | hard | File starts with `---\n` and contains a closing `---\n`. | Skills without frontmatter cannot be discovered. | Add `---` delimiters around the YAML block at the top of the file. |
| `name_present` | hard | `name:` field exists and is non-empty. | The spec's only required identifier. | Add `name: <kebab-case>` to frontmatter. Must equal the directory name. |
| `name_kebab_case` | hard | Name matches `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`. | Cross-runtime compatibility per agentskills.io spec. Invalid names get rejected by Codex / Gemini / etc. | Rename directory + frontmatter + grep for cross-references. See [spec.md § Name validation](spec.md). |
| `name_matches_dir` | soft | `name:` field equals the parent directory name. | Confused operators search by one and find nothing because they don't match. | Pick one as canonical; rename the other to match. |
| `description_present` | hard | `description:` field exists and is non-empty. | Discovery pass loads name + description. Without description, the agent has nothing to match operator intent against — skill is effectively invisible. | Author one — see [description.md](description.md). |
| `description_length` (soft `warn`) | soft | ≤ 1024 chars (agentskills.io spec cap). | Spec compliance for cross-runtime portability. | Tighten OR document the local-style decision in the body's "Why this skill exists" footer. |
| `description_length` (hard `fail`) | hard | ≤ 8000 chars (project sanity ceiling). | Beyond this, every conversation's discovery pass pays a heavy token tax for one skill. | Move detail from description into the body; description is for activation, not exhaustive documentation. |
| `description_has_triggers` | soft | Description contains "Use when …" / "Triggers:" / "Use this skill" / similar phrasing. | Without explicit trigger phrasing, activation depends on the agent inferring intent from generic prose. Inference is unreliable. | Add explicit trigger phrases using operator vocabulary. See [description.md § Trigger word brainstorming](description.md). |
| `allowed_tools_shape` | soft | If `allowed-tools` is present, it's a string or list (not a scalar number, mapping, etc.). | Malformed `allowed-tools` may be silently ignored by the runtime, leading to a skill that "doesn't work" with no clear cause. | Fix the YAML — space-separated string `"Read Write Bash"` or list `[Read, Write, Bash]`. |
| `body_token_budget` (soft `warn`) | soft | ≤ 5000 tokens (chars/4 estimate). Spec recommendation. | Past 5000, every activation pays a heavy context-window tax. Operators using long sessions feel this most. | Move bulk into `references/<topic>.md` files; replace inline content with a one-line summary + link. |
| `body_token_budget` (hard `fail`) | hard | ≤ 15000 tokens. Sanity ceiling. | At this size the skill body crowds out actual conversation context. | Body restructure — extract per-topic reference files, keep body as a router/index. See `autoresearch/SKILL.md` for the pattern. |
| `progressive_disclosure` | soft | Body acts as a router, not a content dump. Fires when: (a) the canonical lane markers `### Preflight` / `### Do` / `### Closeout` repeat (= multiple lanes inline), or (b) body > 4000 tokens with zero `references/` links (= monolith). | The body loads on every activation. A multi-lane skill carrying all lane procedures inline burns tokens on procedures only one chosen lane needs. Even single-flow skills past 4000 tokens with no progressive split waste activation context. This check is the missing-piece audit caught after the original `create-skill` SKILL.md had three lanes inline at 2800 tokens — under the 5000 soft cap but still 60% wasted on non-router content. | **Multi-lane case:** create `references/<lane>.md` per lane, move the lane's Preflight/Do/Closeout into it, replace the body section with a one-line summary + link. **Monolith case:** identify the largest deep-procedure block and extract it. The body should keep only: lane selection table, universal hard rules, spec quick-ref, cross-reference index. |
| `self_validate_directive` | soft | Body contains the canonical blockquote `> **Self-validate after edits.** …` near the top — usually right after the H1. Never promoted to hard under `--strict` (it's project convention, not agentskills.io spec). | The directive lives in always-loaded body so that any agent activating the skill — including agents that will go on to edit it — sees the rule before they make changes. Without it, an agent edits the skill, doesn't re-validate, and the next session inherits a broken skill silently. | Insert the canonical line: `> **Self-validate after edits.** Any change to this skill's files (SKILL.md, scripts/, references/, templates/, assets/) must be followed by \`./scripts/validate.sh\` from the skill directory. Hard findings → create-skill Optimize lane.` Place it right after the H1 (or right after the frontmatter if the skill has no H1). |
| `referenced_files_exist` | soft | Every `references/<f>`, `scripts/<f>`, `templates/<f>`, `assets/<f>` link in the body resolves either against the skill directory or the repo root. | Dangling links confuse the agent at execution time — it tries to read a file that doesn't exist and either errors or hallucinates. | Either create the missing file, fix the path, or delete the dangling link. |

## Reading the JSON output

`audit.py --json` emits:

```json
{
  "reports": [
    {
      "path": ".agents/skills/foo/SKILL.md",
      "name": "foo",
      "hard_findings": 1,
      "soft_findings": 2,
      "checks": [
        {"check": "name_kebab_case", "severity": "hard", "status": "pass", "message": "kebab-case valid"},
        {"check": "description_length", "severity": "soft", "status": "warn", "message": "1309 chars > spec limit 1024 (local style permits ...)"},
        ...
      ]
    }
  ],
  "total_hard": 1,
  "total_soft": 2
}
```

`hard_findings > 0` means exit 1. `soft_findings` are informational unless `--strict` was passed.

## Optimize lane — finding → fix mapping

When you switch to the Optimize lane after an audit, work through findings in this order (highest-leverage first):

1. **`name_*` failures first.** Renaming is invasive (cross-references). Get it done before other edits create more refs to fix.
2. **`description_present` / `description_has_triggers` next.** These directly affect activation — a skill nobody can activate is invisible regardless of body quality.
3. **`body_token_budget` hard failures.** Restructure the body into router + references/ before adding any new content.
4. **`description_length` warnings — decide, don't reflexively fix.** Verbose descriptions are intentional for multi-lane skills. Tighten only when the verbosity isn't earning its activation precision.
5. **`referenced_files_exist`.** Cheap fixes — usually a typo or a file that was renamed without updating refs.
6. **`name_matches_dir` warnings.** Cosmetic but pay it down when you're already in the area.

After every fix: re-run audit. Each finding count should drop.

## What audit does NOT check

Awareness of audit's blind spots:

- **Description quality** beyond the trigger-phrase heuristic. Vague-but-trigger-rich descriptions still pass `description_has_triggers` — operator judgment required.
- **Body coherence.** A body can be the right size and still be unreadable garbage.
- **Whether scripts actually work.** `audit.py` checks they exist, not that they run.
- **Whether the skill duplicates an existing skill.** Use `context-efficiency-audit`, which owns portfolio-level stale and competing routes.
- **Cross-skill dependencies.** If skill A links to skill B and skill B gets renamed, audit on skill A reports the dangling link but doesn't suggest the rename source.

For these, lean on the operator's judgment and the optimize lane's "confirm scope with operator" preflight.
