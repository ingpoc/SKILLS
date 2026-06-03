---
name: codex-productivity-auditor
description: "Audit a project and recent Codex session behavior to recommend Codex productivity setup across AGENTS.md, skills, hooks, MCP/plugins, subagents, local environment actions, automations, memories, and workflow docs. Use when the user asks how to make repeated steering second nature or asks what Codex setup is missing."
---

# Codex Productivity Auditor

Recommend the smallest durable Codex setup changes that make repeated user
steering automatic without adding friction.

## Workflow

1. Inspect project setup: `AGENTS.md`, `.codex/config.toml`,
   `.codex/agents/`, skills, hooks, workflow docs, scripts, and tests.
2. Run deterministic session analysis:
   ```bash
   scripts/transcript_signal_scan.py --project <project-or-path>
   ```
3. Load only the references needed for the recommendation:
   - session signals: `references/session-analysis-rubric.md`
   - owner placement: `references/owner-surface-rubric.md`
   - hooks, automations, MCP/plugins, or always-loaded rules:
     `references/friction-risk-rubric.md`
   - subagent/model choices: `references/model-routing-rubric.md`
   - signal vocabulary: `references/signal-taxonomy.md`
4. Check official OpenAI Codex docs when product behavior may drift.
5. Recommend at most five setup changes, plus what not to configure yet.

## Fixed Decisions

- Raw Codex JSONL under `~/.codex/sessions` and
  `~/.codex/archived_sessions` is the canonical session-analysis source.
- Do not use qmd or Obsidian for scoring or recommendations; use them only for
  explicit human-readable lookup or semantic discovery requests.
- For repeated local run/test/log command friction, prefer Codex local
  environment actions over hooks or automations.
- Do not hand-write local-environment action schema. Create the first action
  through Codex app settings, inspect the generated project `.codex` artifact,
  then edit only with that schema in hand.

## Recommendation Shape

```text
Top Recommendations
1. <setup change>
   Evidence: <signal counts and pointers>
   Owner: <surface>
   Change: <exact action>
   Confidence: high|medium|low
   Validation: <command/proof>

Not Recommended Yet
- <feature>: <why>

Loopholes Checked
- <loophole>: <fix or downgrade>
```

Keep the answer compact. Do not paste long transcript excerpts; cite counts,
JSONL file paths, line numbers, and command evidence.
