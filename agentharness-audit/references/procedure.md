# Audit Procedure — Step by Step

## Step 1 — Resolve target codebase

If user specified a path, use it. Otherwise use the current working directory.

```bash
# Confirm it's an agent harness (look for agent loop, tool dispatch, model calls)
find . -name "*.py" -o -name "*.ts" -o -name "*.rs" | head -5
grep -r "tool_call\|function_call\|model\|completion\|chat" --include="*.py" -l | head -10
```

If none of these signals are present, output:
```
This codebase does not appear to be an agent harness (no agent loop, tool dispatch,
or model calls detected). Stopping audit.
```

Identify the harness name from: `pyproject.toml` name field, `package.json` name field,
top-level README h1, or directory name as fallback.

## Step 2 — Discovery map

Read the following (parallel reads where possible):

| What to find | Where to look |
|---|---|
| System prompt assembly | grep for "system_prompt", "build_prompt", "system_message" |
| Tool loading | grep for "tools", "tool_schema", "function_definitions" |
| Memory / persistence | grep for "memory", "persist", "write", "session" |
| Compaction | grep for "compact", "compress", "summarize", "context_limit" |
| Subagent / fork | grep for "subagent", "fork", "spawn", "Agent(" |
| Config / setup | look for setup.sh, setup wizard, config.yaml, config.toml |
| Operator instructions | AGENTS.md, CLAUDE.md, SOUL.md, .cursorrules |
| Provider handling | grep for "provider", "model", "api_key", "base_url" |

Read key files fully. Aim to read at least:
- The main agent loop (largest file with "loop", "run", "agent" in name)
- The system prompt builder
- The memory/persistence layer
- The tool loading mechanism

## Step 3 — Score all 13 principles

For each principle in `references/principles.md`:

1. State what you found (file:line citations)
2. State what is absent ("not found: no mid-turn compaction detected")
3. Apply the rubric and assign a score
4. Write a one-line gap statement: "Missing: X. Would need: Y at Z to reach 9.5"

Compute:
- Individual scores: P1 through P13
- Weighted overall score: `sum(scores) / 13` (equal weights)
- Gap per principle: `9.5 - score` (negative = already above target)

## Step 4 — Write HTML report

Use the bundled HTML template as a self-contained artifact source. Do not hand-roll a new layout, do not ask whether to use `html-artifact`, and do not depend on loading another skill. The template already embeds the html-artifact report-lane design conventions needed for this audit.

Create `docs/agentharness-audit/` if it doesn't exist:
```bash
mkdir -p docs/agentharness-audit
```

Copy the bundled template file into place, then fill placeholders:
```bash
cp ~/.codex/skills/agentharness-audit/templates/audit.html.template \
   docs/agentharness-audit/<harness-name>-audit.html
```

The literal HTML scaffold lives in [`templates/audit.html.template`](../templates/audit.html.template). The design rationale, substitution helpers (`score_class` / `bar_color_token` / `bar_pct` / `format_gap` / `gap_class` / `rec_label` / `count_by_class`), and per-placeholder fill checklist live in [`references/html-template.md`](html-template.md). Read both before filling.

Before filling, collect margin citations for every principle from `references/architecture.md` § Winner Reference — grouped by harness (hermes / claude code / codex). These go in the `.pmargin > .mcites` column, not in the arch-block prose. Omit any `.mcite-group` that has no citation for the current principle.

The report must include:
1. **Header**: harness name, audit date (YYYY-MM-DD), commit ref
2. **Hero**: overall score (large serif numeral, severity-colored) + 2–3 sentence executive summary
3. **Tile row**: 4 stat tiles counting principles by class (met / near / mute / far)
4. **Scorecard**: all 13 principles as a compact table with score bar + citation + gap
5. **Priority stack**: top 3 improvements by `gap` desc, each with specific action
6. **Deep-dive**: one section per principle — found / missing / recommendation / canonical architecture, with marginalia for score + winner citations

For each principle's deep-dive section, include a "Canonical Architecture" block pulled from `references/architecture.md` for that principle — the Pattern, Anti-pattern, and Design rationale. This is the reference standard the harness is being measured against. Also cite which winner harness exemplifies the pattern (e.g., "Winner: Hermes `agent/system_prompt.py:269`").

The template is self-contained — zero CDN dependencies, system font stacks only. Renders identically online and offline. Treat `html-artifact` references in the template guide as provenance and design rationale, not as a runtime dependency or an instruction to load that skill.

## Step 5 — Write AGENTS.md directive

Write `docs/agentharness-audit/<harness-name>-AGENTS.md`.
Full template: see `references/agents-template.md`.

Rules for AGENTS.md content:
- Written FOR the agent, not the human
- Every recommendation names a specific file to create/modify
- Every recommendation names a specific pattern to implement
- Reference how other harnesses solved it (cite file:line from Hermes/Codex/Claude Code)
- For each principle, include the "Canonical Architecture Pattern" from `references/architecture.md`
  so the agent knows exactly what the winning implementation looks like before it starts coding
- Acceptance criteria per principle: what concrete observable change signals 9.5

## Step 6 — Print terminal summary

After writing both files, print to terminal:

```
=== Agent Harness Audit: <HarnessName> ===
Date: YYYY-MM-DD
Overall: X.X / 10

PRINCIPLE                           SCORE  GAP
─────────────────────────────────────────────
P01 Cache-Stable System Prompt      X.X    -Y.Y
P02 Deferred Context Loading        X.X    -Y.Y
P03 Mechanical Learning Loop        X.X    -Y.Y
P04 Strong Read Path                X.X    -Y.Y
P05 Model-Adaptive Guidance         X.X    -Y.Y
P06 Subagent Delegation             X.X    -Y.Y
P07 Skill Lifecycle                 X.X    -Y.Y
P08 Per-Turn Truth-Grounding        X.X    -Y.Y
P09 Operator Ergonomics             X.X    -Y.Y
P10 Security / Trust Model          X.X    -Y.Y
P11 Multi-Surface Presence          X.X    -Y.Y
P12 Compaction Under Pressure       X.X    -Y.Y
P13 Provider / Model Flexibility    X.X    -Y.Y
─────────────────────────────────────────────
TOP 3 IMPROVEMENTS:
  1. <principle> (gap: Y.Y) — <one-line action>
  2. <principle> (gap: Y.Y) — <one-line action>
  3. <principle> (gap: Y.Y) — <one-line action>

Reports written to:
  docs/agentharness-audit/<name>-audit.html
  docs/agentharness-audit/<name>-AGENTS.md
```
