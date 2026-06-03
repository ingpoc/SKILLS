# The 13 Meta-Principles — Scoring Rubric

Each principle is scored 0–10. Apply the rubric consistently across all harnesses.

## Universal scoring rubric

| Score | Meaning |
|---|---|
| 0–2 | Absent or actively harmful (e.g., prompt rebuilt every turn, no memory at all) |
| 3–4 | Rudimentary / hardcoded / single-case (e.g., one provider hardcoded, flat memory file) |
| 5–6 | Functional but manual, fragile, or operator-dependent |
| 7–8 | Well-implemented, covers main cases, some edge gaps |
| 9–10 | Excellent: handles edge cases, production-hardened, cache/token-aware |

A score of 9.5+ requires: correct default behavior, edge-case handling, explicit
documentation of the invariant in code, and no known failure modes.

---

## P1 — Cache-Stable System Prompt

**What it measures**: Is the system prompt byte-stable across turns? Every rebuild is a prefix
cache miss — costing latency and money.

**Evidence to look for**:
- Timestamp format (minute-precision = cache miss every turn; date-only = stable all day)
- Whether system prompt is built once and cached vs rebuilt each turn
- Whether memory changes mid-session force a rebuild
- Whether compression events are the only rebuild trigger

| Score | Evidence |
|---|---|
| 0–2 | Prompt rebuilt every turn, includes timestamps/random ids |
| 3–4 | Partially stable but unstable section invalidates whole prompt |
| 5–6 | Cached but no explicit cache-friendliness design (e.g., minute timestamps) |
| 7–8 | Cached with mostly stable content; minor volatile sections |
| 9–10 | Three-tier design (stable/context/volatile), date-only timestamps, rebuilt only after compression, explicit cache invariant in code comments |

**9.5 reference**: Hermes `agent/system_prompt.py:269-271` — date-only timestamp with explicit
comment crediting the PR that introduced it. System prompt cached on `_cached_system_prompt`,
only rebuilt after compression events.

---

## P2 — Deferred Context Loading

**What it measures**: Do tools, skills, and docs load only when the model decides they're needed?
Or is everything dumped into context at session start?

**Evidence to look for**:
- Tool schema loading: upfront vs on-demand
- Skill loading: full content vs description-only with load-on-invoke
- Doc loading: always in prompt vs fetched by tool call
- Memory loading: full dump vs index + on-demand fetch

| Score | Evidence |
|---|---|
| 0–2 | All tools, skills, docs in system prompt always |
| 3–4 | Some tools/skills deferred but no routing layer |
| 5–6 | Skills have descriptions but content loaded eagerly |
| 7–8 | Skills deferred, tool schemas mostly upfront |
| 9–10 | Full lazy stack: ToolSearch/equivalent for schemas, description-only skill list, MEMORY.md index pattern, docs fetched by tool |

**9.5 reference**: Claude Code — `ToolSearch` defers full tool schemas; skills listed with
description only, `Skill` tool loads on invocation; `MEMORY.md` is a lightweight index.

---

## P3 — Mechanical Learning Loop (Write Path)

**What it measures**: Does the agent autonomously persist knowledge via turn counters or
iteration triggers — without being told to?

**Evidence to look for**:
- Turn-counter-based memory nudge (fire every N turns)
- Iteration-counter-based skill nudge (fire after N tool iterations)
- Autonomous memory write (agent writes without operator instruction)
- Curator or background review process

| Score | Evidence |
|---|---|
| 0–2 | No memory write path at all |
| 3–4 | Agent can write memory when instructed but no autonomous trigger |
| 5–6 | Nudge exists but requires operator to enable or configure manually each session |
| 7–8 | Automatic nudge with persistent counter, minor gaps (e.g., doesn't survive process restart) |
| 9–10 | Turn-counter + iteration-counter nudges, counter hydrated from history on restart, forked LLM review, curator with stale/archive/reactivate lifecycle |

**9.5 reference**: Hermes `conversation_loop.py:429-439` (memory nudge), `699-703` (skill nudge),
`4154-4158` (post-turn review trigger), `curator.py:1369-1450` (forked AIAgent review pass).

---

## P4 — Strong Read Path (Retrieval)

**What it measures**: Can the agent find past sessions, memory entries, and docs on demand?
Is there an index-before-content pattern?

**Evidence to look for**:
- FTS (full-text search) over past sessions
- Memory index (lightweight) → full content (on demand)
- Cross-session recall tool
- Workflow/doc search command
- Explicit retrieval triggers in operator instructions

| Score | Evidence |
|---|---|
| 0–2 | No retrieval beyond current context |
| 3–4 | Memory loaded wholesale into prompt (no indexing) |
| 5–6 | Session history accessible but no structured search |
| 7–8 | FTS or keyword search over sessions; memory index exists |
| 9–10 | FTS5 session search with LLM summarization, MEMORY.md index + per-file reads, workflow doc search, explicit retrieval doctrine in operator instructions |

**9.5 reference**: Hermes FTS5 + `session_search` tool + Honcho user modeling.
Claude Code MEMORY.md index + `workflow search/read/summary`.

---

## P5 — Model-Adaptive Guidance

**What it measures**: Does the harness detect the model family and inject compensating guidance
for that model's known failure modes?

**Evidence to look for**:
- Model name detection in system prompt builder
- Different guidance blocks injected per model family
- Tool-use enforcement for weak models
- Conciseness guidance for verbose models

| Score | Evidence |
|---|---|
| 0–2 | Single hardcoded model, no adaptation |
| 3–4 | Generic guidance applies to all models equally |
| 5–6 | Operator can manually configure per-model guidance |
| 7–8 | 2–3 model families detected and handled |
| 9–10 | Detects GPT/Grok/Gemini/Claude/etc., injects family-specific blocks, configurable override |

**9.5 reference**: Hermes `system_prompt.py:160-168` — detects model substring, injects
`OPENAI_MODEL_EXECUTION_GUIDANCE` for GPT/Codex/Grok, `GOOGLE_MODEL_OPERATIONAL_GUIDANCE`
for Gemini/Gemma.

---

## P6 — Subagent Delegation as Context Isolation

**What it measures**: Are subagents first-class? Do they return summaries (not traces) to
protect the main context?

**Evidence to look for**:
- Subagent spawn mechanism (runtime, not config-only)
- What returns to main context: full trace vs summary
- Typed specializations (e.g., Explore, Plan, code-review)
- Parallel subagent support

| Score | Evidence |
|---|---|
| 0–2 | No subagent support |
| 3–4 | Subagents configurable but not runtime-spawnable |
| 5–6 | Subagents spawnable but return full traces |
| 7–8 | Subagents return summaries; one or two typed specializations |
| 9–10 | Typed specializations with defined contracts, summaries only, parallel support, main context unaffected |

**9.5 reference**: Claude Code `Agent` tool with Explore/Plan/code-review specializations.
Hermes `background_review.py` forked AIAgent with minimal context scope.

---

## P7 — Skill Lifecycle / Self-Pruning

**What it measures**: Does the agent review its own skills and prune stale ones autonomously?

**Evidence to look for**:
- Curator or background review process
- Stale/archive/reactivate state machine
- Snapshot before mutations
- LLM review pass against skill candidates

| Score | Evidence |
|---|---|
| 0–2 | Skills never reviewed or pruned |
| 3–4 | Operator can manually delete skills |
| 5–6 | Agent can manage skills on request but no automatic review |
| 7–8 | Automatic review scheduled, but no state machine |
| 9–10 | Curator runs on schedule, stale/archive/reactivate transitions, pre-snapshot, LLM review pass, REPORT.md diff |

**9.5 reference**: Hermes `curator.py` — `apply_automatic_transitions()`, `run_curator_review()`
spawns forked AIAgent, `curator_backup.snapshot_skills()` before mutations, full state machine.

---

## P8 — Per-Turn Truth-Grounding

**What it measures**: Does the harness structurally enforce read-before-act? Are there quality
gates that block the agent from recommending things it hasn't verified?

**Evidence to look for**:
- Operator instructions with explicit retrieve-before-recall rules
- Quality gate commands (`workflow quality-gate`, etc.)
- Before-recommending-from-memory checks in operator docs
- Harness-level hooks that block unverified actions

| Score | Evidence |
|---|---|
| 0–2 | No grounding rules anywhere |
| 3–4 | Vague "be careful" instructions |
| 5–6 | Retrieve-before-recall mentioned but not enforced |
| 7–8 | Explicit rules in AGENTS.md/CLAUDE.md with specific file-check patterns |
| 9–10 | Retrieve-before-recall doctrine, quality gate commands, before-recommending-from-memory rules with stale-memory detection, applied consistently across all surfaces |

**9.5 reference**: Claude Code CLAUDE.md — "retrieve before recall for unfamiliar/risky work",
"Before recommending from memory: check the file exists; grep for the function."

---

## P9 — Operator Ergonomics

**What it measures**: Can a smart non-expert get a useful first session in under 5 minutes?

**Evidence to look for**:
- One-line install script
- Setup wizard or guided first-run
- No API key configuration required (OAuth or equivalent)
- Sensible defaults (model, tools, memory)

| Score | Evidence |
|---|---|
| 0–2 | Requires expert configuration to function |
| 3–4 | Documented setup but many manual steps |
| 5–6 | Reasonable setup but requires API key management |
| 7–8 | Quick setup, one provider, minimal friction |
| 9–10 | One-line install, setup wizard, OAuth/no-key-juggling, 30+ providers, model-adaptive defaults |

**9.5 reference**: Hermes — `curl | bash`, `source ~/.bashrc`, `hermes` → running. `hermes setup`
wizard covers all configuration. Supports `CLAUDE_CODE_OAUTH_TOKEN` as valid auth.

---

## P10 — Security / Trust Model

**What it measures**: Is execution sandboxed? Are permissions explicit and structurally enforced
(not just instructed)?

**Evidence to look for**:
- OS-level sandbox (Seatbelt, seccomp, containers)
- Permission allowlists enforced by harness, not model
- Network isolation
- Hook-based blocking of unsafe actions
- Audit trail for tool calls

| Score | Evidence |
|---|---|
| 0–2 | No sandboxing, no permission model |
| 3–4 | Model instructed to be careful, no structural enforcement |
| 5–6 | Permission allowlists exist but applied inconsistently |
| 7–8 | Allowlists enforced, hooks block some actions |
| 9–10 | OS sandbox (Seatbelt/seccomp), network isolation, full permission allowlists, hooks block unsafe actions, analytics on every sensitive operation |

**9.5 reference**: Codex `AGENTS.md` — Seatbelt sandbox, `CODEX_SANDBOX_NETWORK_DISABLED`
enforced on shell tool invocations, `CODEX_SANDBOX=seatbelt` propagated to child processes.

---

## P11 — Multi-Surface Presence

**What it measures**: Is the same agent accessible from multiple interfaces with shared memory?

**Evidence to look for**:
- CLI interface
- IDE integration
- Messaging gateways (Telegram, Discord, Slack, WhatsApp)
- Shared memory/context across surfaces

| Score | Evidence |
|---|---|
| 0–2 | Single interface only |
| 3–4 | CLI + one other |
| 5–6 | CLI + IDE, no messaging |
| 7–8 | 3+ surfaces but memory not shared across them |
| 9–10 | CLI + IDE + 3+ messaging platforms + shared memory + voice support |

**9.5 reference**: Hermes — Telegram, Discord, Slack, WhatsApp, Signal, CLI, voice memo
transcription, 7 terminal backends, all sharing USER.md and memory.

---

## P12 — Compaction Under Pressure

**What it measures**: When the context fills, does the harness recover gracefully — including
mid-stream?

**Evidence to look for**:
- Pre-turn compaction (before sending)
- Mid-turn compaction (while streaming)
- Multiple compaction strategies
- Analytics/telemetry on compaction events
- Loop detection after compression

| Score | Evidence |
|---|---|
| 0–2 | Crashes or corrupts on context overflow |
| 3–4 | Truncates history without summary |
| 5–6 | Pre-turn summarization only |
| 7–8 | Pre-turn + manual compaction, basic analytics |
| 9–10 | Pre-turn + mid-turn + manual, multiple strategies, full analytics per event, loop detection, TruncationPolicy for tool outputs |

**9.5 reference**: Codex `compact.rs` — three compaction modes including mid-turn streaming,
`CompactionStrategy/Phase/Trigger/Status` analytics, `SUMMARIZATION_PROMPT` + `SUMMARY_PREFIX`
templates. Hermes: 413-aware auto-compression + loop detection after compression.

---

## P13 — Provider / Model Flexibility

**What it measures**: Does the harness work with multiple LLM providers without code changes?

**Evidence to look for**:
- Number of supported providers
- Provider switching mechanism (config vs code change)
- Auth handling (API key, OAuth, credential files, IAM)
- OpenAI-compatible API mode for custom endpoints

| Score | Evidence |
|---|---|
| 0–2 | Single hardcoded provider/model |
| 3–4 | 2–3 providers via code changes |
| 5–6 | Multiple providers via config, basic auth only |
| 7–8 | 5–10 providers, multiple auth modes |
| 9–10 | 20+ providers, zero-code switching, handles API key + OAuth + credential files + IAM + custom endpoints |

**9.5 reference**: Hermes — 30+ providers, `hermes model` switches with no code changes,
auth resolves `ANTHROPIC_API_KEY` → `ANTHROPIC_TOKEN` → `CLAUDE_CODE_OAUTH_TOKEN` chain,
supports Azure identity, Bedrock IAM roles, custom endpoints.
