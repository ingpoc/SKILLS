# Audit lane — run deterministic checks

Loaded on demand when the operator picks the Audit lane (or types "audit / check / validate / review skill(s)").

## Do

```bash
# Single skill — pass a directory or SKILL.md path.
python3 ~/.codex/skills/create-skill/scripts/audit.py ~/.agents/skills/<name>

# User-global sweep — every SKILL.md under ~/.agents/skills/.
python3 ~/.codex/skills/create-skill/scripts/audit.py --all

# Strict mode — promotes spec-soft warnings (desc > 1024, body > 5000 tokens) to hard.
# Use before promoting a skill to cross-runtime / public consumption.
python3 ~/.codex/skills/create-skill/scripts/audit.py --all --strict

# Machine-readable output for downstream tooling.
python3 ~/.codex/skills/create-skill/scripts/audit.py --all --json
```

## Output format

Per-skill findings, two tiers:

| Severity | Meaning | Default exit |
|---|---|---|
| **HARD** | Spec violation or sanity-bound breach. Examples: missing `name`, invalid kebab-case, missing `description`, body > 15000 tokens, description > 8000 chars. | Exit 1. |
| **SOFT** | Style warning. Examples: description > 1024 chars (spec cap, locally permitted), body > 5000 tokens (spec recommendation), missing trigger phrasing, name != directory. | Exit 0 (still reported). |

`--strict` promotes spec-soft items to hard. Use when the skill needs cross-runtime portability per agentskills.io's client showcase (Codex, Gemini CLI, Cursor, etc.).

For per-check rationale and finding → fix mapping, see [checklist.md](checklist.md).

## JSON shape

```json
{
  "reports": [
    {
      "path": ".agents/skills/foo/SKILL.md",
      "name": "foo",
      "hard_findings": 0,
      "soft_findings": 2,
      "checks": [
        {"check": "name_kebab_case", "severity": "hard", "status": "pass", "message": "..."},
        ...
      ]
    }
  ],
  "total_hard": 0,
  "total_soft": 5
}
```

## Closeout

- **Hard findings** → switch to Optimize lane (audit is read-only). Load [optimize.md](optimize.md).
- **Soft findings** → surface to the operator with a recommendation; let them decide whether to optimize now or defer. Project style explicitly tolerates verbose descriptions and large bodies in some skills (`autoresearch`, `knowledge-base`) where activation precision is worth the discovery cost.
- **Clean** → report exit 0, summarize counts, end the lane.

## Reading the JSON for downstream automation

When `--json` is used, the caller (CI script, cron job, another skill) can branch on:

| Field | Interpretation |
|---|---|
| `total_hard > 0` | Repo has spec-violating skills — fail the gate. |
| `total_soft > 0` | Repo has style warnings — log but don't fail unless `--strict` was used. |
| Per-check `status: "fail"` with `severity: "hard"` | Specific skill needs Optimize lane. Use the `path` field to target it. |
| Per-check `status: "warn"` with severity `"soft"` | Informational. Map the `check` ID to [checklist.md](checklist.md) for the fix. |

## What audit does NOT check

Awareness of audit's blind spots — these need operator judgment:

- **Description quality** beyond trigger-phrase presence. A vague-but-trigger-rich description still passes `description_has_triggers`.
- **Body coherence.** A body can be the right size and still be unreadable.
- **Whether scripts actually work.** Audit checks `scripts/*.py` exists, not that it runs.
- **Duplicate or overlapping skills.** Use `context-efficiency-audit`; its portfolio scan owns stale and competing trigger routes.
- **Cross-skill dependency drift.** If skill A links to skill B and B gets renamed, audit on A reports a dangling link but doesn't propose the rename source.

For these, lean on operator judgment in the Optimize lane's "confirm scope" preflight.
