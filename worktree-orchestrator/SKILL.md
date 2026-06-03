---
name: worktree-orchestrator
description: "Use when spawning parallel Claude Code subagents in git worktrees for code review, architecture analysis, SDK verification, or testing. Load for multi-agent codebase optimization, parallel PR creation, or orchestrating Claude Code features across isolated worktrees. Triggers: 'parallel analysis', 'worktree review', 'multi-agent optimization', 'spawn reviewers', 'orchestrate worktrees', 'smart review'."
keywords: [worktree, parallel, subagent, orchestration, code-review, architecture, sdk-verifier, testing, multi-agent, smart-setup]
---

# Worktree Orchestrator

Spawn parallel Claude Code subagents in isolated git worktrees, each running specialized analysis (code review, architecture, SDK verification, testing), then aggregate results and create PRs.

## Two Modes

| Mode | Script | When to Use |
|------|--------|-------------|
| **Smart (Dynamic)** | `smart_setup.sh` | Let system decide which agents based on codebase analysis |
| **Static (Fixed)** | `setup_worktrees.sh` | Always spawn all 5 agent types |

## Smart Mode (Recommended)

Analyzes codebase and selects appropriate agents:

```
Orchestrator: "Analyzing jarvis-mac..."
  → Python project (75 files)
  → Claude Agent SDK detected
  → Tests exist
  → API + Auth code detected

Decision: Spawn 5 agents (all HIGH confidence)
  ✅ sdk-verify (SDK detected)
  ✅ testing (tests detected)
  ✅ review-security (API + auth)
  ✅ architecture (132 files)
  ✅ review-performance (large project)
```

### Detection Rules

| Detection | Triggers Agent | Confidence |
|-----------|----------------|------------|
| Claude Agent SDK | sdk-verify | high |
| tests/ directory | testing | high |
| API endpoints | review-security | high |
| Auth code | review-security | high |
| 50+ source files | architecture | high |
| React/Frontend | review-performance | high |
| Small project (<20 files) | architecture | low (skip) |

## Static Mode

Always creates 5 worktrees:

```
main-branch (orchestrator)
    │
    ├── worktree: review-security/     → code-review (security)
    ├── worktree: review-performance/  → code-review (performance)
    ├── worktree: architecture/        → Plan agent
    ├── worktree: sdk-verify/          → agent-sdk-verifier
    └── worktree: testing/             → testing skill
```

## Workflow

### Phase 1: Setup

```bash
# Smart mode (recommended) - analyzes codebase first
~/.claude/skills/worktree-orchestrator/scripts/smart_setup.sh [base-branch] [target-dir]

# Static mode - always creates 5 worktrees
~/.claude/skills/worktree-orchestrator/scripts/setup_worktrees.sh [base-branch] [target-dir]
```

Creates worktrees in `../<worktree-name>/` with isolated `.claude/sessions/`.

### Phase 2: Spawn Agents

Use Task tool to spawn parallel subagents in each worktree:

| Agent Type | Focus Area | Model | Subagent Type |
|------------|------------|-------|---------------|
| code-review | Security | sonnet | general-purpose |
| code-review | Performance | sonnet | general-purpose |
| plan | Architecture | opus | Plan |
| agent-sdk-verifier | SDK compliance | haiku | agent-sdk-verifier-py |
| testing | Coverage | haiku | test-runner |

### Phase 3: Aggregate Results

```bash
~/.claude/skills/worktree-orchestrator/scripts/aggregate_results.sh [target-dir]
```

### Phase 4: Create PRs

```bash
~/.claude/skills/worktree-orchestrator/scripts/create_prs.sh [target-dir] [base-branch]
```

## Scripts Reference

| Script | Purpose | Output |
|--------|---------|--------|
| `analyze_codebase.sh` | Detect features, recommend agents | JSON analysis |
| `smart_setup.sh` | Dynamic worktree creation | Selected worktrees |
| `setup_worktrees.sh` | Static worktree creation | All 5 worktrees |
| `aggregate_results.sh` | Collect agent outputs | summary.md |
| `create_prs.sh` | Generate PRs from changes | PR URLs |
| `create_issues.sh` | Create GitHub issues from findings | Issue URLs |
| `clean_worktrees.sh` | Remove all worktrees | Clean state |

## Output Structure

```
.claude/worktrees/
├── analysis.json              # Smart mode detection results
├── FINAL_SUMMARY.md           # Combined analysis summary
├── review-security/
│   ├── findings.md
│   └── patches/
├── review-performance/
│   └── findings.md
├── architecture/
│   └── architecture_review.md
├── sdk-verify/
│   └── sdk_compliance.md
├── testing/
│   └── test_report.md
└── aggregated/
    ├── summary.md
    └── prioritized_actions.md
```

## Example Usage

```bash
# 1. Smart setup (recommended) - outputs to .claude/worktrees/
~/.claude/skills/worktree-orchestrator/scripts/smart_setup.sh main

# 2. Spawn agents via Task tool (parallel)
# - Each agent reads worktree-metadata.json for focus area
# - Writes findings.md to worktree root

# 3. Aggregate results
~/.claude/skills/worktree-orchestrator/scripts/aggregate_results.sh

# 4. Create GitHub issues from findings (requires gh CLI)
~/.claude/skills/worktree-orchestrator/scripts/create_issues.sh

# 5. Comment @claude on issues to have Claude fix them

# 6. Cleanup when done
~/.claude/skills/worktree-orchestrator/scripts/clean_worktrees.sh
```

## GitHub Issue Integration

After aggregation, create GitHub issues from findings:

```bash
# Requires GitHub CLI (gh)
brew install gh
gh auth login

# Create issues
~/.claude/skills/worktree-orchestrator/scripts/create_issues.sh
```

Issues are formatted for @claude GitHub App integration:

1. Install <https://github.com/apps/claude> on your repo
2. Comment `@claude please fix this` on any issue
3. Claude analyzes and creates a PR

## Resource Loading

| Resource | When to Load | Purpose |
|----------|--------------|---------|
| `scripts/analyze_codebase.sh` | Phase 1 (smart) | Detect codebase features |
| `scripts/smart_setup.sh` | Phase 1 (smart) | Dynamic worktree creation |
| `scripts/setup_worktrees.sh` | Phase 1 (static) | Fixed worktree creation |
| `scripts/aggregate_results.sh` | Phase 3 | Collect agent outputs |
| `scripts/create_prs.sh` | Phase 4 | Generate PRs |
| `scripts/clean_worktrees.sh` | Cleanup | Remove worktrees |
| `references/agent_prompts.md` | Phase 2 | Subagent task templates |

## Integration with .agent Framework

| .agent Concept | worktree-orchestrator Equivalent |
|----------------|----------------------------------|
| AGENT_COMMS_FRAMEWORK | Task tool + SendMessage |
| ARCHITECTURE.md | architecture/ worktree output |
| IMPLEMENTATION_PLAN.md | Plan agent output |
| Evidence ladder | Per-worktree findings |

## Key Rules

1. **Parallel execution**: All agents run concurrently via Task tool
2. **Isolation**: Each worktree has separate `.claude/sessions/`
3. **No context bleeding**: Agents cannot see each other's work
4. **Deterministic aggregation**: Scripts collect, not LLM judgment
5. **Evidence-based**: All findings require file refs + line numbers
6. **Smart selection**: Only spawn relevant agents based on codebase
