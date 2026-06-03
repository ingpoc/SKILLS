---
name: harness-audit
description: Check system setup health across 7 categories. Use for /harness-audit, "verify my setup", "check harness". NOT for project quality (/audit) or eval scoring (/eval-score).
model: sonnet
effort: low
allowed-tools: Read, Bash, Glob, Grep
---

# Harness Audit: Control Plane Health Score

**EXECUTE this skill now.** Follow the workflow steps below using the provided $ARGUMENTS. Do NOT describe, summarize, or explain this skill — run it.

## Constants

- `CLAUDE_DIR`: `C:/Users/gurusharan.gupta/.claude`
- `REGISTRY_DIR`: `C:/Users/gurusharan.gupta/Agents/Claude Code`

---

## Category 1: Tool Coverage (4 checks)

1. **Skills installed** — `ls ~/.claude/skills/` has ≥ 8 skill directories
2. **Core skills present** — scan, audit, research, execplan, init-project all exist in `~/.claude/skills/`
3. **Bin scripts valid** — `bin/scan.sh` and `bin/install.sh` exist and are executable
4. **Manifest exists** — `manifest.json` present and valid JSON (check with `python -m json.tool manifest.json`)

## Category 2: Context Efficiency (4 checks)

5. **Global CLAUDE.md size** — word count ≤ 500 words (token efficient)
6. **Project CLAUDE.md size** — word count ≤ 300 words if present
7. **Skills have context:fork** — count skills with `context: fork` in frontmatter; PASS if ≥ 70% of exploration/registry skills have it (scan, audit, dashboard, register, context-budget, verify, save-session = 7; PASS if ≥ 5 have it)
8. **Skill size limit** — no individual SKILL.md exceeds 200 lines

## Category 3: Quality Gates (4 checks)

9. **Model frontmatter** — all SKILL.md files have a `model:` field in frontmatter
10. **Effort frontmatter** — all SKILL.md files have an `effort:` field
11. **Eval criteria exist** — `eval/criteria/` has ≥ 1 non-template JSON file
12. **Principles registered** — `principles/_index.json` exists and has ≥ 3 entries

## Category 4: Session Persistence (4 checks)

13. **save-session skill** — `~/.claude/skills/save-session/SKILL.md` exists
14. **resume-session skill** — `~/.claude/skills/resume-session/SKILL.md` exists
15. **session-data dir** — `~/.claude/session-data/` directory exists (create if missing)
16. **Context budget skill** — `~/.claude/skills/context-budget/SKILL.md` exists

## Category 5: Eval Coverage (4 checks)

17. **Eval scaffolds** — `eval/scaffolds/` has ≥ 1 directory
18. **Eval history** — `eval/history/` has ≥ 1 score entry
19. **Criteria coverage** — each workflow in `workflows/` has a matching criteria file in `eval/criteria/`
20. **Score recency** — most recent score in `eval/history/` is within 30 days (check file mtime)

## Category 6: Security Guardrails (4 checks)

21. **Hooks managed-only** — `~/.claude/settings.json` does not contain any `hooks` key (managed-only env)
22. **Bypass disabled** — `settings.json` does not have `bypassPermissionsMode: true`
23. **MCP whitelist** — if `.mcp.json` exists, all servers are in the known whitelist (context7, playwright, or other explicitly approved)
24. **No secrets in skills** — no SKILL.md file contains patterns matching `(password|secret|api_key|token)\s*=\s*['\"][^'\"]{8,}`

## Category 7: Cost Efficiency (4 checks)

25. **Mechanical skills use Haiku** — scan, register, dashboard, context-budget, save-session, verify all have `model: haiku`
26. **Model routing documented** — `~/.claude/CLAUDE.md` contains either a model routing table OR a reference to `rules/performance.md` (check for "rules/" or "model routing" or "Model Routing" in the file)
27. **Subagent model set** — `settings.json` has `CLAUDE_CODE_SUBAGENT_MODEL=haiku` in env block
28. **Token cap set** — `settings.json` has `MAX_THINKING_TOKENS` in env block

---

## Scoring Workflow

For each check:
- Use Read/Glob/Bash/Grep to evaluate the condition
- Record PASS or FAIL with a one-line reason

After all checks, compute:
- Per-category score: (passed / 4) × 10 → 0–10
- Overall score: average of 7 category scores → 0–10

## Output Format

```
## Harness Audit Report — <date>

| # | Category | Score | Checks |
|---|----------|-------|--------|
| 1 | Tool Coverage | X/10 | 4 PASS / 0 FAIL |
| 2 | Context Efficiency | X/10 | 3 PASS / 1 FAIL |
| 3 | Quality Gates | X/10 | ... |
| 4 | Session Persistence | X/10 | ... |
| 5 | Eval Coverage | X/10 | ... |
| 6 | Security Guardrails | X/10 | ... |
| 7 | Cost Efficiency | X/10 | ... |

**Overall Score: X.X / 10**

### Failures
<list each failed check with: check name, what was found, how to fix>

### Grade
- 9.0–10: Excellent — control plane is production-ready
- 7.0–8.9: Good — minor gaps, address before scaling
- 5.0–6.9: Fair — notable gaps affecting efficiency
- < 5.0: Poor — critical issues require immediate attention
```

Stop and report even if some checks error (e.g., file missing). A missing file is a FAIL, not an error.
