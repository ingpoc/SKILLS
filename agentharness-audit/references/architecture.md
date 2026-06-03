# Architectural Best Practices — One per Principle

This file documents the canonical architectural pattern for each of the 13 principles.
Use it in three contexts:
- **Auditing**: the pattern is the standard against which the codebase is measured
- **Reporting**: include in HTML deep-dives and AGENTS.md so operators understand the WHY
- **Building from scratch**: a harness built to these patterns starts at 9.5+ without iteration

Each entry has: **Pattern** (what to build), **Anti-pattern** (what to avoid),
**Design rationale** (why it works), **Compounds with** (which other principles it amplifies).

---

## P01 — Cache-Stable System Prompt

### Pattern: Three-tier assembly with explicit invariants

```
stable   → built once at agent init, never changes within a session
context  → built once per session, changes between sessions (AGENTS.md, cwd files)
volatile → rebuilt each turn, always last in assembly order
```

The critical invariant: **every byte before the volatile tier is identical across all turns
in a session.** This means the LLM provider's prefix cache hits on turns 2–N.

Implementation rules:
- No wall-clock timestamps (use date-only at most)
- No random IDs, nonces, or per-call values in stable or context tiers
- Memory snapshots go in volatile — they change as the agent learns
- The volatile tier must be last — it can change without invalidating the upstream prefix
- Document the invariant in code comments, not just in docs

### Anti-pattern: Rebuild-on-every-turn

```python
# WRONG: rebuilds every turn, cache miss on every API call
def build_prompt():
    return f"You are Hermes. Time: {datetime.now().isoformat()}. ..."
```

Any value that changes per-turn in the stable section means the provider sees a different
prompt hash every call — paying full input token cost every time.

### Design rationale

LLM provider prefix caches (Anthropic prompt caching, OpenAI cached inputs) work by
hashing the prefix bytes. Identical prefix = cache hit = ~90% cost reduction on input tokens
and ~50% latency reduction. A single minute-precision timestamp in turn 1 means every
subsequent turn pays full price.

The three-tier model emerged from Hermes `agent/system_prompt.py` — the date-only timestamp
comment (`credit: @iamfoz, PR #20451`) documents the moment this became explicit.

### Winner Reference — Hermes

- `agent/system_prompt.py:269-271` — `now.strftime('%A, %B %d, %Y')` date-only timestamp
  with explicit `# date-only for cache stability` comment
- `agent/system_prompt.py:60-65` — `_cached_system_prompt` field, built once, invalidated
  only after compression event
- `agent/conversation_loop.py` — prompt rebuild guard: only triggered by compression,
  not by per-turn logic

### Compounds with
- **P02 Deferred Loading**: stable prompt + deferred schemas = maximum cache efficiency.
  The stable section stays small (no tool schemas) and byte-identical.
- **P03 Learning Loop**: volatile tier holds memory — learning changes volatile but not
  stable, so the cache warm-up cost is paid only once per session.

---

## P02 — Deferred Context Loading

### Pattern: Description-as-routing-layer → content on demand

Three-layer information hierarchy:

```
Layer 1 — Always loaded (names only):
  "available tools: bash, read_file, tool_search, memory, skill_invoke, ..."

Layer 2 — Descriptions (loaded at session start, no schemas):
  "tool_search: returns full schema for tools matching a query"
  "skill_invoke: executes a named skill"

Layer 3 — Content (loaded on demand via tool call):
  tool_search("bash") → returns full JSON schema
  skill_invoke("code-review") → loads full skill instructions
```

The model sees Layer 1 + 2 always. It fetches Layer 3 only when it decides it needs it.

### Anti-pattern: Upfront content dump

```python
# WRONG: all 40 tool schemas + all 70 skill bodies in the system prompt
system_prompt = f"""
Tools available:
{json.dumps(ALL_TOOL_SCHEMAS)}   # 15,000 tokens

Skills available:
{ALL_SKILL_CONTENT}              # 30,000 tokens
"""
```

The model's attention is finite. Loading 45,000 tokens of tool/skill content that
the model won't use for a given task crowds out the actual task context.

### Design rationale

The core insight: **the model needs just enough to decide what to load, not everything
it might eventually need.** A one-line tool description is enough for the model to call
`tool_search("bash")`. The schema doesn't need to be there before that decision.

This maps directly to how senior engineers read codebases: they scan file names and
function signatures first, read full implementations only when relevant. The harness
should give the model the same browsing interface.

Claude Code's `ToolSearch` deferred schema pattern demonstrated this at scale — the
difference between 70 tool schemas always loaded vs. names + descriptions is ~50K tokens
per session.

### Winner Reference — Claude Code (tool schemas) + Hermes (memory index)

- Claude Code `<system-reminder>` injects tool names only; `ToolSearch(query="select:ToolName")`
  fetches full schema on demand — the canonical description-as-routing-layer implementation
- Hermes `~/.hermes/memory/MEMORY.md` — index file listing each entry as
  `- [slug](file.md) — one-line hook`; agent reads index first, fetches content file on demand
- Codex `codex-rs/core/src/context/available_skills_instructions.rs` —
  `AvailableSkillsInstructions` fragment loads skill names and descriptions, not bodies

### Compounds with
- **P01 Cache-Stable Prompt**: smaller stable section = more cache-stable. No tool schemas
  in the stable tier means the stable section stays byte-identical.
- **P04 Read Path**: MEMORY.md index is an application of this same pattern to memory.
  The index is Layer 2 (descriptions); individual memory files are Layer 3 (content).

---

## P03 — Mechanical Learning Loop (Write Path)

### Pattern: Dual-counter nudge + forked reviewer + lifecycle GC

The write path has three independent mechanisms:

```
1. Turn counter (in main loop):
   every N user turns → fire memory review nudge

2. Iteration counter (in tool loop):
   every M tool iterations → fire skill review nudge

3. Background reviewer (forked process):
   runs LLM review pass against agent-created artifacts
   stale → archive → reactivate lifecycle
```

These three are intentionally separate. The counter is mechanical (no LLM, no failure mode).
The reviewer is LLM-based (smart, but async so it can't block the main agent).

Counter must be **hydrated from history** on process restart — gateway processes create
fresh agents per message; a counter that starts at 0 on every restart never fires.

```python
# Hydrate on restart:
prior_turns = sum(1 for m in history if m["role"] == "user")
_turns_since_memory = prior_turns % _memory_nudge_interval
```

### Anti-pattern: Intention-based write

```python
# WRONG: the agent writes when it thinks it should
# This works under low context pressure but fails when:
# - context is large (agent's planning degrades)
# - agent is mid-task (focused on task, not meta-cognition)
# - operator didn't set up the right instructions
```

Intention-based memory requires the agent to simultaneously manage the task AND
meta-cognition about its own knowledge. Under context pressure, meta-cognition loses.
The counter fires whether or not the agent is thinking about it.

### Design rationale

**The write path must be mechanical, not intentional.** Human memory has the same property:
sleep consolidates memories whether or not you decide to consolidate them. The harness
should implement the same invariant: knowledge persists through a mechanical path, not
through the agent's in-context deliberation.

The dual-counter design handles two different kinds of valuable information:
- Turn-based nudge: captures conversational/declarative knowledge (what the user cares about)
- Iteration-based nudge: captures procedural knowledge (multi-step patterns worth a skill)

### Winner Reference — Hermes

- `agent/conversation_loop.py:429-439` — turn counter nudge: `_turns_since_memory`,
  `_memory_nudge_interval = 5`, fires `_should_review_memory` flag
- `agent/conversation_loop.py:699-703` — iteration counter nudge: `_iters_since_skill`,
  `_skill_nudge_interval = 15`, fires after 15 tool iterations
- `agent/conversation_loop.py:384-403` — counter hydration from conversation history on
  process restart: `prior = sum(1 for m in history if m.get("role") == "user")`
- `agent/conversation_loop.py:4154-4158` — post-turn background review trigger
- `agent/curator.py:1369-1450` — `run_curator_review()` spawns forked `AIAgent` for
  LLM review pass; `apply_automatic_transitions()` state machine

### Compounds with
- **P04 Read Path**: the write path is worthless without a retrieval mechanism. A closed
  loop requires both. Build them together.
- **P07 Skill Lifecycle**: the write path creates skills; the lifecycle GC prevents them
  from accumulating into noise.

---

## P04 — Strong Read Path

### Pattern: Index-before-content + FTS over sessions + stale detection

Two-level retrieval architecture:

```
Level 1 — Index (always in context):
  MEMORY.md:
  - [project-goals](project-goals.md) — user's current goals and constraints
  - [auth-decisions](auth-decisions.md) — authentication architecture decisions

Level 2 — Content (fetched on demand):
  memory tool → reads project-goals.md → full content
```

Full-text search over session history:
```python
session_search("authentication") → returns summaries of relevant past sessions
```

Stale detection on every memory read:
```python
if entry.written_at < (now - STALE_THRESHOLD):
    flag_as_stale(entry)  # add [STALE — written N days ago] prefix
```

### Anti-pattern: Wholesale memory injection

```python
# WRONG: entire memory block dumped into system prompt
system_prompt += format_all_memory()  # 8,000 tokens of potentially irrelevant memory
```

Wholesale injection has two failure modes:
1. Stale facts compete with fresh context (the agent reads an outdated decision as current)
2. Relevant memory is diluted by irrelevant memory (attention is finite)

### Design rationale

The retrieval path mirrors how good documentation systems work: a table of contents
(index) tells you what exists; you read the chapter (content) only when relevant.

FTS over sessions solves a specific failure mode: the agent knows a decision was made
in a past session but can't recall which one. Semantic search helps but requires embeddings;
FTS5 is deterministic, fast, and needs no external service.

Stale detection is the most underimplemented piece. A memory entry written 90 days ago
about a library version is likely wrong today. The harness should flag it, not silently
inject it as fact.

### Winner Reference — Hermes (FTS + index) + Claude Code (MEMORY.md pattern)

- Hermes `agent/memory_manager.py` — `<memory-context>` fence tags, `StreamingContextScrubber`
  strips memory block before injecting fresh retrieval
- Hermes FTS5 `session_search` tool — SQLite full-text search over past sessions,
  returns summaries not full transcripts
- Claude Code `~/.claude/projects/<project>/memory/MEMORY.md` — index-before-content
  pattern: one-line per entry with slug + description + file link

### Compounds with
- **P02 Deferred Loading**: MEMORY.md index IS deferred loading applied to memory.
  The same architectural principle — descriptions before content.
- **P08 Truth-Grounding**: stale detection is the memory-layer implementation of
  truth-grounding. Without it, the agent cites old facts as current.

---

## P05 — Model-Adaptive Guidance

### Pattern: Family detection → stable-tier guidance injection → configurable override

```python
model_family_guidance = {
    ("gpt", "codex", "grok"):   OPENAI_EXECUTION_GUIDANCE,   # tool-use enforcement
    ("gemini", "gemma"):         GOOGLE_CONCISENESS_GUIDANCE,  # verbosity reduction
    ("mistral", "mixtral"):      MISTRAL_TOOL_GUIDANCE,        # tool persistence
    ("claude",):                 None,  # follows tool-use natively
}

for keywords, guidance in model_family_guidance.items():
    if any(k in model_lower for k in keywords):
        stable_parts.append(guidance)
        break
```

Override path: `tool_use_enforcement: auto | true | false | [model-substrings]`

Guidance must go in the **stable tier** — it's model-specific, not session-specific.
Putting it in volatile would invalidate the cache every turn.

### Anti-pattern: One-size-fits-all system prompt

Different models fail in different ways:
- GPT-4o tends to describe actions instead of calling tools → needs enforcement guidance
- Gemini tends to be verbose and use relative paths → needs conciseness guidance
- Grok tends to suggest workarounds when tools exist → needs tool-preference guidance
- Claude follows tool use natively → adding enforcement guidance wastes tokens

A single prompt for all models means you're either under-guiding weak models (they fail)
or over-guiding strong models (they waste tokens acknowledging redundant instructions).

### Design rationale

**The harness is the right layer to compensate for model failure modes, not the operator.**
Every operator who switches models would otherwise need to rewrite their system prompt.
The harness should absorb that complexity once, centrally.

This also means model-switching (P13) is truly zero-friction — not just zero config,
but zero prompt-engineering work.

### Winner Reference — Hermes

- `agent/system_prompt.py:140-168` — full family detection and guidance injection:
  checks `("gpt", "codex", "grok")`, `("gemini", "gemma")`, `("mistral", "mixtral")`,
  injects `OPENAI_MODEL_EXECUTION_GUIDANCE` / `GOOGLE_MODEL_OPERATIONAL_GUIDANCE` etc.
- `agent/system_prompt.py:160-168` — model family detection logic: `model_lower = (self.model or "").lower()`
- `agent/conversation_loop.py` — `tool_use_enforcement: auto | true | false | [substrings]`
  config override path

### Compounds with
- **P13 Provider Flexibility**: model-adaptive guidance makes provider switching truly
  zero-cost. Without it, switching from Claude to GPT-4o requires prompt rewriting.
- **P01 Cache-Stable Prompt**: guidance in the stable tier means it doesn't invalidate
  the cache when it's injected.

---

## P06 — Subagent Delegation as Context Isolation

### Pattern: Typed specializations + summary-only return + parallel dispatch

```python
SUBAGENT_TYPES = {
    "explore": ExploreAgent,   # maps structure, returns file tree + key symbols
    "review":  ReviewAgent,    # checks correctness, returns findings only
    "plan":    PlanAgent,      # creates ordered steps, returns numbered list
    "execute": ExecuteAgent,   # does work, returns status + summary
}

def spawn_subagent(task: str, type: str) -> SubagentResult:
    agent = SUBAGENT_TYPES[type](task)
    result = agent.run()
    return SubagentResult(
        summary=result.summary,   # ONLY the summary goes to main context
        structured=result.data,
        # NOT: result.full_conversation_history
    )
```

The discipline: **main agent is coordinator, subagents are workers.**
The coordinator sees results, not work logs.

### Anti-pattern: All work in main context

```python
# WRONG: multi-step research task done entirely in main context
# - step 1 result stays in context for steps 2-N
# - context grows with each step
# - by step 10, the original task is 8,000 tokens ago
```

### Design rationale

The main context is the agent's working memory. Like human working memory, it's finite
and degrades under load. Long chains of tool calls compound: each result stays in context,
pushing the original task further back.

Subagents reset: they start with a clean context, do one focused thing, and return a
compact result. The main agent's working memory stays near the task.

**Typed specializations** serve two purposes:
1. The specialization's system prompt focuses the subagent (an "explore" agent doesn't
   try to edit files; a "review" agent doesn't try to plan)
2. The output contract is explicit — the caller knows what shape result to expect

### Winner Reference — Claude Code (typed subagents) + Hermes (background fork)

- Claude Code `Agent` tool — typed subagent dispatch: `subagent_type` parameter selects
  specialization (Explore, Plan, code-reviewer, etc.); result returned as single message
  to main context, not full conversation trace
- Claude Code subagent types `Explore`, `Plan`, `general-purpose` — each has its own
  allowed tools and system prompt; the main context sees only the result
- Hermes `agent/background_review.py` — background fork that runs post-turn review
  without blocking main conversation; result injected as `<system-reminder>` not as
  assistant message

### Compounds with
- **P10 Security**: subagents in a sandbox are safer than the main agent running
  arbitrary shell commands. The subagent's blast radius is bounded by its type.
- **P01 Cache-Stable Prompt**: subagents can have their own stable prompts, separate
  from the main agent's. The main agent's cache is not polluted by subagent work.

---

## P07 — Skill Lifecycle / Self-Pruning

### Pattern: State machine + automated transitions + LLM review pass + pre-snapshot

Skill states:
```
active → stale → archived
   ↑_______________|   (reactivate if use_count increases)
```

Automated transitions (no LLM, deterministic):
```python
if days_since_use > ARCHIVE_DAYS:  state = "archived"
elif days_since_use > STALE_DAYS:  state = "stale"
elif use_count > REACTIVATE_THRESHOLD and state == "stale":  state = "active"
```

LLM review pass (smart, async, runs in background fork):
- Reviews stale candidates for merge, rewrite, or archive
- Identifies duplicates
- Suggests improvements based on recent usage patterns

Pre-snapshot before every mutation:
```python
snapshot = backup_skills(reason="pre-curator-run")
curator.run()  # safe to mutate — snapshot exists
```

### Anti-pattern: Append-only skill storage

```
# Without lifecycle GC:
Month 1: 10 skills
Month 3: 35 skills (many redundant or stale)
Month 6: 80 skills — context budget for skill descriptions exhausted
```

Skills without lifecycle management accumulate like unreviewed code. The skill list
grows until it either hits context budget limits or degrades in quality (irrelevant
skills compete with relevant ones for the model's attention).

### Design rationale

**Skills are software. Software rots.** A skill created for a task three months ago
may use a deprecated API, reference a file that no longer exists, or be superseded by
a better skill created last month. The harness needs a GC mechanism, just like any
memory management system.

The hybrid approach (deterministic transitions + LLM review) is important:
- Deterministic transitions handle the easy cases (clearly old, clearly unused) without
  burning LLM tokens
- LLM review handles the subtle cases (two skills that do similar things, a skill that
  could be improved based on recent patterns)

### Winner Reference — Hermes

- `agent/curator.py:1369-1450` — `run_curator_review()`: spawns a forked `AIAgent` for
  LLM review pass over agent-created skills
- `agent/curator.py` — `apply_automatic_transitions()`: deterministic state machine
  (`active → stale → archived → reactivate`) with configurable day thresholds
- `agent/curator.py` — `curator_backup.snapshot_skills()`: pre-mutation snapshot before
  every curator run
- Hermes skill metadata YAML — `state: active|stale|archived`, `created_at`, `last_used_at`,
  `created_by: agent|user`, `use_count` fields

### Compounds with
- **P03 Learning Loop**: the write path creates skills; the lifecycle GC maintains quality.
  Together they form a complete knowledge management system.
- **P02 Deferred Loading**: a well-maintained skill list (not too large, well-described)
  is essential for the description-as-routing-layer to work. 80 stale skills defeats deferred loading.

---

## P08 — Per-Turn Truth-Grounding

### Pattern: Doctrine + structural verification + stale detection

Three layers:

```
Layer 1 — Doctrine (in stable system prompt, for ALL models):
  "Before recommending a file path: verify it exists.
   Before claiming a symbol exists: grep for it.
   Before citing memory: check written_at freshness.
   If unverified: say so and verify before answering."

Layer 2 — Structural verification (deterministic tool):
  quality_gate(claims) → checks file existence, symbol presence, memory freshness

Layer 3 — Stale detection (in memory read path):
  entries with written_at > STALE_THRESHOLD → flagged in context
```

The doctrine tells the model what to do. The quality gate enforces it. Stale detection
catches the most common truth failure (citing an outdated memory as current fact).

### Anti-pattern: Trusting training data

The model's training data is a prior. It was accurate at training time.
Three things make training data dangerous as a source of truth:
1. **Version drift**: library APIs change between training and deployment
2. **Repo drift**: files and symbols in the user's codebase weren't in training data at all
3. **Memory staleness**: a memory entry written 6 months ago may reflect a decision that was reversed

The harness must structurally distrust training data — not by instruction alone (models
override instructions under context pressure) but by making verification the path of
least resistance.

### Design rationale

**Instructions fail under context pressure. Structural enforcement doesn't.**

When the context is large and the model is mid-task, "be careful to verify" instructions
compete with the current task for attention. A structural hook (quality gate before
reporting done) doesn't require the model to remember — it's enforced by the harness.

The doctrine is still necessary: it shapes the model's default behavior before it
reaches the quality gate. But doctrine alone is insufficient for production quality.

### Winner Reference — Claude Code (doctrine) + Hermes (structural enforcement)

- Claude Code global `CLAUDE.md` — "Before recommending from memory" section: explicit
  rules for file-path verification, symbol grepping, stale memory checking before citing
- Claude Code `CLAUDE.md:` — "If a memory names a file path: check the file exists.
  If a memory names a function: grep for it." — the canonical doctrine template
- Hermes global `AGENTS.md` — "Retrieve before recall for unfamiliar/risky work" doctrine
- Hermes `agent/memory_manager.py` — `written_at` field on every memory entry;
  `StreamingContextScrubber` strips stale entries before injection

### Compounds with
- **P04 Read Path**: stale detection in the read path is the memory-layer implementation
  of truth-grounding. Both principles require `written_at` timestamps on memory entries.
- **P03 Learning Loop**: a mechanical write path combined with stale detection creates
  a self-correcting knowledge system — facts are written automatically and their
  freshness is tracked automatically.

---

## P09 — Operator Ergonomics

### Pattern: One-line install → wizard → zero-config defaults → self-diagnosis

```
Install:  curl | bash    (handles all dependencies)
Start:    source ~/.bashrc && hermes
First:    hermes setup   (guided wizard: provider → model → tools → memory)
Verify:   hermes hello   (end-to-end stack test: model + tools + memory)
Debug:    hermes doctor  (diagnoses common issues, suggests fixes)
```

Each step must be achievable by a non-expert in under 2 minutes.
Zero-config means: sensible provider default, sensible model default, memory enabled by default.

### Anti-pattern: Prerequisite configuration wall

```
# WRONG ergonomics:
Step 1: Get API key from provider X (requires account creation, billing setup)
Step 2: Set PROVIDER_API_KEY in .env
Step 3: Configure config.yaml with model, tools, memory settings
Step 4: Run hermes setup (which just re-asks what you already configured)
```

The prerequisite wall is the most common reason good harnesses fail to get adoption.
The time from "I want to try this" to "I got value" determines whether the operator
becomes a long-term user.

### Design rationale

**Time-to-first-value is the most important operator metric.** Everything before first
value is a dropout point. The harness should minimize the distance between "downloaded"
and "had a useful conversation."

OAuth login (accepting a token the operator already has) is qualitatively different from
API key setup. It eliminates account creation, billing, and key management from the
first-run path — the three highest-friction steps.

Sensible defaults are the second most important piece: the harness should work for most
operators without any configuration. Configuration should be opt-in enhancement, not
prerequisite.

### Winner Reference — Hermes

- `install.sh` — one-line bootstrap: `curl -fsSL <url> | bash`, handles `uv` install +
  PATH setup + first-run message
- `hermes_cli/` — `hermes setup` interactive wizard: guides through provider → model →
  memory → tools without any prior configuration
- `hermes_cli/auth.py` — `api_key_env_vars = ("ANTHROPIC_API_KEY", "ANTHROPIC_TOKEN",
  "CLAUDE_CODE_OAUTH_TOKEN")` — accepts Claude Code OAuth token, eliminating API key
  requirement for most users
- `hermes doctor` command — diagnoses common issues (missing API key, bad model name,
  network errors) and prints fix instructions

### Compounds with
- **P13 Provider Flexibility**: good ergonomics requires that switching providers doesn't
  break the ergonomic promise. `hermes model` preserves the wizard UX across providers.
- **P05 Model-Adaptive Guidance**: the harness adapts to the model so the operator
  doesn't have to reconfigure when switching. Ergonomics across providers.

---

## P10 — Security / Trust Model

### Pattern: Defense in depth — OS sandbox + allowlists + hooks + audit log

```
Layer 1 — OS sandbox (structural, can't be bypassed):
  bubblewrap (Linux) / sandbox-exec (macOS) wraps shell subprocess
  network isolation via --unshare-net (Linux) or Seatbelt deny-network

Layer 2 — Permission allowlists (harness-enforced):
  allowed_tools = ["bash", "read_file"]  # deny by default
  bash_allowlist = ["git ", "python ", "npm test"]

Layer 3 — Pre-execution hooks (configurable):
  pre_bash_hook(cmd) → blocks dangerous patterns before execution

Layer 4 — Audit log (observability):
  ~/.harness/audit.jsonl → timestamp, tool, args hash, result code
```

The key principle: **each layer is independent.** If a model is jailbroken and bypasses
the allowlist, the OS sandbox still blocks network exfiltration. If the OS sandbox isn't
available, the allowlist provides fallback enforcement.

### Anti-pattern: Instruction-only safety

```python
# WRONG: rely entirely on system prompt instructions
system_prompt += "Never run rm -rf or access /etc. Be careful with shell commands."
```

Adversarial prompts, prompt injection via tool results, and context pressure can all
cause models to override safety instructions. Instructions are a hint to the model,
not an enforcement mechanism.

### Design rationale

The threat model for an agent harness has two distinct adversaries:
1. **Unintentional harm**: the agent misunderstands the task and takes a destructive action
2. **Adversarial injection**: a malicious file, web page, or tool result hijacks the agent

Instructions handle case 1 partially. They don't handle case 2.

Structural enforcement (OS sandbox, allowlists, hooks) handles both cases because it
operates outside the model's context — the model cannot override it by "deciding" to.

The audit log is essential for the third case: post-incident investigation. Without a
log, you can't reconstruct what the agent did or why.

### Winner Reference — Codex (OS sandbox) + Claude Code (allowlists + hooks)

- `codex-rs/AGENTS.md` — "Seatbelt sandbox" on macOS (`sandbox-exec`), bubblewrap on
  Linux; `CODEX_SANDBOX_NETWORK_DISABLED` env var disables network at OS level
- `codex-rs/AGENTS.md` — `--full-auto` mode runs in sandbox with no confirmation prompts;
  outside sandbox, every shell command requires user approval
- Claude Code `settings.json` — `allowedTools` and `deniedTools` arrays enforced by
  harness before model sees the tool; `hooks` block runs shell commands on tool events
- Claude Code `hooks` — `PreToolUse` hook can `exit 1` to block a tool call structurally
  before it reaches the model

### Compounds with
- **P06 Subagent Delegation**: sandboxed subagents with typed specializations limit
  blast radius. An "explore" subagent that can't write files or make network calls
  is safely isolated even if compromised.
- **P12 Compaction**: compaction events should be audited — a suspicious compaction
  that drops context about sensitive operations is a security concern, not just a
  technical one.

---

## P11 — Multi-Surface Presence

### Pattern: Platform-agnostic handler + shared persistent store + surface-aware routing

```python
class GatewaySession:
    platform: str           # "telegram" | "discord" | "cli" | "slack"
    user_id: str
    memory_path: Path       # ~/.harness/memory/ — SAME regardless of platform
    user_profile_path: Path # ~/.harness/USER.md — SAME regardless of platform

def handle_message(session: GatewaySession, text: str) -> str:
    agent = get_or_create_agent(session)
    # agent loads from the SAME memory path regardless of platform
    return agent.run(text)
```

Platform-specific behavior injected via platform hints in the stable system prompt
(not in business logic):
```python
PLATFORM_HINTS = {
    "telegram": "Responses are delivered via Telegram. Keep replies concise.",
    "cli":      "You are running in a terminal. Use ANSI formatting when helpful.",
}
```

### Anti-pattern: Per-platform agent instances

```python
# WRONG: separate memory per platform
telegram_agent = Agent(memory_path="~/.harness/telegram-memory/")
cli_agent       = Agent(memory_path="~/.harness/cli-memory/")
# These agents have different worldviews of the same user
```

The agent's identity is its memory. If memory is split by surface, the agent on Telegram
doesn't know what the agent on CLI learned yesterday. This defeats presence — the operator
has to repeat context on every surface switch.

### Design rationale

**Presence means the agent remembers you regardless of which interface you use.**

The surfaces differ in ergonomics (Telegram is mobile, CLI is keyboard) but the agent
is the same entity across all of them. Memory, USER.md profile, and skill state should
be shared.

The implementation implication: the memory path must be an absolute path resolved at
the HARNESS level, not at the gateway level. Each gateway reads from the same store.

### Winner Reference — Hermes

- `gateway/` directory — platform-agnostic `GatewaySession` handler shared across
  Telegram, Discord, Slack, WhatsApp, Signal gateways
- All gateways resolve memory to `~/.hermes/memory/` — the same absolute path used
  by the CLI surface; facts written on Telegram are retrievable on CLI
- `gateway/telegram.py` — Telegram bot using `python-telegram-bot`; session state
  stored in shared `~/.hermes/sessions/` alongside CLI sessions
- `hermes gateway` CLI command — single entry point to start any configured gateway;
  bot token read from `.env`

### Compounds with
- **P03 Learning Loop**: memory written during a Telegram conversation should be
  retrievable during the next CLI session. This only works if both surfaces write to
  the same store AND the volatile tier is reloaded from disk on every message.
- **P09 Ergonomics**: multi-surface setup should be wizard-driven. `hermes gateway`
  should walk the operator through bot token setup with the same ergonomic standard
  as `hermes setup`.

---

## P12 — Compaction Under Pressure

### Pattern: Pre-turn check + mid-turn recovery + tool output truncation + analytics

```
Stage 1 — Pre-turn (before API call):
  if estimate_tokens(messages) > context_limit * 0.85:
      messages = compact(messages)  # summarize middle turns

Stage 2 — Mid-turn (during streaming, catches 413):
  try:
      async for chunk in stream: yield chunk
  except ContextLimitError:
      messages = compact(messages)
      stream = retry(messages)
      async for chunk in stream: yield chunk

Stage 3 — Tool output truncation (before each result injected):
  if estimate_tokens(result) > MAX_TOOL_OUTPUT:
      result = truncate(result) + "[truncated — use search to find specific content]"

Stage 4 — Analytics (for every compaction event):
  log CompactionEvent(trigger, strategy, tokens_before, tokens_after)
```

Loop detection: if two consecutive compactions don't reduce token count below threshold,
raise `CompactionLoopError` rather than looping forever.

### Anti-pattern: Crash on overflow or silent truncation

```python
# WRONG option 1: crash
raise ContextLengthExceeded("Too many tokens")

# WRONG option 2: silent truncation
messages = messages[-20:]  # drop oldest without telling the model
```

Crashing loses the task. Silent truncation is worse: the model doesn't know context
was dropped and may reference events it can no longer see, producing incoherent responses
without knowing why.

### Design rationale

**Context overflow is a runtime invariant violation, not an error.** It must be handled
gracefully at every stage, not just at turn boundaries.

The three-stage approach is necessary because overflow can happen at different points:
- Pre-turn overflow: the accumulated history is too large before sending
- Mid-turn overflow: a long tool output within a streaming response pushes past the limit
- Tool output overflow: a single search result is larger than the usable budget

Each stage requires a different response strategy. A harness that only handles pre-turn
will crash on the other two.

Analytics per compaction event are not optional for production systems. Without them
you cannot debug why a session lost coherence mid-task — the compaction event is the
root cause.

### Winner Reference — Codex (three-mode) + Hermes (413-aware + loop detection)

- `codex-rs/core/src/compact.rs` — `CompactionStrategy` (summarize / drop-oldest / hybrid),
  `CompactionPhase` (pre-turn / mid-turn / manual), `CompactionTrigger`, `CompactionStatus`
  analytics — the most complete compaction implementation of any harness reviewed
- `codex-rs/core/src/compact.rs` — mid-turn streaming compaction: catches 413 during
  `async for chunk in stream`, recompacts, retries — handles the case other harnesses miss
- Hermes `agent/conversation_loop.py` — 413-aware error handler with auto-recompaction
  and loop detection: raises `CompactionLoopError` if two consecutive compactions don't
  reduce token count

### Compounds with
- **P02 Deferred Loading**: smaller stable section + deferred schemas = more headroom
  before compaction is needed. The two principles together reduce compaction frequency.
- **P04 Read Path**: after compaction, the read path (session search, memory retrieval)
  lets the agent recover lost context from persistent storage rather than from the
  now-compacted message history.

---

## P13 — Provider / Model Flexibility

### Pattern: ProviderProfile registry + zero-code switching + tiered auth resolution

```python
@dataclass
class ProviderProfile:
    name: str
    base_url: str
    api_key_env_vars: tuple[str, ...]  # resolution order — first found wins
    default_model: str
    api_mode: str  # "openai" | "anthropic" | "bedrock" | "gemini"
    # Optional hooks for provider-specific behavior:
    prepare_messages: Callable = identity
    build_extra_body:  Callable = lambda **ctx: {}
    fetch_models:      Callable = default_fetch_models
```

Tiered auth resolution (no code changes to switch providers):
```python
def resolve_api_key(provider: ProviderProfile) -> str:
    for env_var in provider.api_key_env_vars:
        val = os.getenv(env_var)
        if val:
            return val
    raise AuthError(f"No auth found for {provider.name}. Set one of: {provider.api_key_env_vars}")
```

Provider plugins discovered from filesystem — no registry edits to add a new provider:
```
plugins/model-providers/
  anthropic/provider.py   # ProviderProfile(name="anthropic", ...)
  openai/provider.py
  my-custom/provider.py   # drop a file, it's registered
```

### Anti-pattern: Hardcoded provider strings

```python
# WRONG: provider baked into business logic
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = client.messages.create(model="claude-opus-4-7", ...)
```

When the operator wants to try GPT-4o instead of Claude, they need to find every
hardcoded string and API call. When Anthropic releases a new model, same problem.

### Design rationale

**The model is a dependency, not a constant.** Best software engineering practice
treats dependencies as injectable/swappable. The same principle applies to LLMs.

The `ProviderProfile` pattern centralizes all provider-specific knowledge in one place:
auth, base URL, API mode, message preprocessing, model listing. Every downstream layer
reads from the profile — auth resolution, transport, doctor health checks — so adding
a new provider is a single file addition with no downstream changes.

Provider plugins (discovered from filesystem) take this further: third-party providers
can be added without modifying core harness code, making the provider ecosystem
independently extensible.

### Winner Reference — Hermes

- `hermes_cli/auth.py` — `api_key_env_vars = ("ANTHROPIC_API_KEY", "ANTHROPIC_TOKEN",
  "CLAUDE_CODE_OAUTH_TOKEN")` — tiered auth resolution with 3-env-var fallback chain
- `providers/base.py` — `ProviderProfile` dataclass with `name`, `base_url`,
  `api_key_env_vars`, `default_model`, `api_mode`, optional `prepare_messages` hook
- `providers/README.md` — plugin discovery pattern: drop a `provider.py` file in
  `plugins/model-providers/<name>/`, it's auto-registered with no core changes
- `providers/` — 30+ pre-built provider profiles covering Anthropic, OpenAI, Gemini,
  Mistral, Groq, Bedrock, Together, Fireworks, and custom endpoints
- `hermes model` CLI command — interactive provider/model switcher; reads from
  `ProviderProfile` registry, no hardcoded strings

### Compounds with
- **P05 Model-Adaptive Guidance**: zero-code provider switching is only truly zero-cost
  if switching providers also switches the appropriate guidance block. Together they
  mean the operator can run `hermes model`, pick a new provider, and get the correct
  behavior immediately.
- **P09 Ergonomics**: the wizard (`hermes model`) is the ergonomic interface to the
  provider registry. The registry handles correctness; the wizard handles discoverability.

---

## Compounding Effects — Principle Clusters

Some principles produce disproportionate value when implemented together:

### Cluster A — Token Economy (P01 + P02 + P12)
Cache-stable prompt + deferred loading + robust compaction = minimum tokens per useful turn.
This cluster determines the raw cost efficiency of the harness. Build it first.

### Cluster B — Knowledge Flywheel (P03 + P04 + P07)
Mechanical write path + strong read path + skill lifecycle = a harness that gets smarter
over time without operator intervention. This is the core differentiator between
a harness and a smart chatbot.

### Cluster C — Correctness Foundation (P08 + P04 + P03)
Truth-grounding + read path with stale detection + mechanical writes with timestamps =
a harness that knows what it knows, knows when it doesn't know, and knows when its
knowledge is stale. Without this cluster, the learning flywheel (B) produces confident
wrong answers as easily as confident right ones.

### Cluster D — Production Readiness (P09 + P10 + P13)
Ergonomics + security + provider flexibility = a harness an operator can deploy to
production and trust with real users. None of the three is sufficient alone.
