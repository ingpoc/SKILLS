---
name: research
description: Process a research article or blog post into actionable insights for the knowledge base. Use for /research, "process this article", "extract insights from". NOT for web search or code review.
allowed-tools: Read, Write, Bash, Glob, Grep, WebFetch, mcp__chrome-devtools-mcp__list_pages, mcp__chrome-devtools-mcp__new_page, mcp__chrome-devtools-mcp__take_snapshot, mcp__chrome-devtools-mcp__select_page
---

# Research: Extract and Catalog Actionable Insights

**EXECUTE this skill now.** Follow the workflow steps below using the provided $ARGUMENTS. Do NOT describe, summarize, or explain this skill — run it.

## Constants

- `KNOWLEDGE_ROOT`: `~/.codex/knowledge`
- `KNOWLEDGE_RAW`: `~/.codex/knowledge/raw` (single source of truth for accepted insights)
- `TMP_IMPORT_DIR`: `/tmp/knowledge-import`

## Commands

Parse $ARGUMENTS to determine action:
- `/research <url>` — Fetch, extract insights, catalog
- `/research search <query>` — Search existing insights by keyword/tag
- `/research list` — List accepted KB articles
- `/research tags` — List all tags with counts
- `/research` (no args) — Show usage help

## Gotchas

| Gotcha | What happens | Do instead |
|--------|--------------|------------|
| Placeholder source URLs | `workflow knowledge validate --json` fails on values such as `pasted-content`. | Capture an HTTP/HTTPS source URL before accepting an insight; if the user pasted content, ask for the original source metadata. |
| Direct KB writes | Manual writes can skip lint, reindexing, and schema enforcement. | Write temp files under `/tmp/knowledge-import/`, run `workflow knowledge lint`, then ingest with `workflow knowledge ingest`. |
| Duplicate source URLs | One source may correctly produce multiple accepted insight files. | Treat duplicate source URLs as source groups, not drift; deduplicate by identical insight/title instead. |
| Legacy section names | `## Application` or `## Application to Control Plane` can pass older readers but creates validation warnings. | Always write the canonical third section as `## Applicability`. |

## Workflow: Process a URL

### Step 1: Check for Duplicates

Check both live KB entries and the rejected-source index before fetching:

1. Search accepted insights in `KNOWLEDGE_RAW/` for the source URL or a distinctive article title fragment. Use `rg -n "<url-or-title-fragment>" ~/.codex/knowledge/raw`.
2. Check `workflow knowledge search "<url-or-title-fragment>"` output for previously rejected URLs. The skip index is only useful for sources that produced no accepted insights.

Decision rule:
- If accepted insights already exist for the same source, report the matching KB files and skip unless the article has materially changed.
- If `workflow knowledge search` shows a prior rejected source (`accepted: 0`), report "Previously processed, no insights passed quality gate. Skip unless article has been updated."
- Default: skip duplicates. Only reprocess when the source has changed or the user explicitly asks.

### Step 2: Fetch the Article

**Try WebFetch first:**

```
WebFetch(url, "Extract the complete article content including all sections, findings, techniques, code examples, benchmarks, and conclusions. Preserve technical detail — do not summarize. If there are specific numbers, percentages, or measurements, include them exactly.")
```

If WebFetch returns a redirect, follow it with a second fetch.

**If WebFetch returns 403/blocked → fallback to Chrome DevTools MCP:**

1. Call `list_pages` to check for existing browser pages — reuse one if already on the target domain
2. If no reusable page: call `new_page` with the article URL
3. Wait for page to load, then call `take_snapshot` to capture the full page content as text
4. Use the snapshot text as the article content — continue to Step 3 as normal

This fallback handles paywalls, bot-protection, and Cloudflare blocks that reject automated fetchers but allow real browsers.

**If Chrome DevTools MCP is also unavailable** (no browser, MCP not configured), ask the user to paste the article text directly, then process the pasted content. Also ask for source URL, source title, author or organization, and publication date; accepted KB files must not use placeholder source URLs such as `pasted-content`.

### Step 3: Extract and Gate Insights

From the fetched content, identify candidate insights — techniques, findings, or patterns that could change how an agent works. For each candidate, produce:
- **title**: Short, specific (e.g., "Tool descriptions need example usage to improve accuracy")
- **insight**: 1-3 sentences of the actionable takeaway. Not a summary — the specific thing to do or know.
- **evidence**: What supports this? Quote numbers, benchmarks, or reasoning from the article.
- **applicability**: How this maps to the user's control plane, skills, agents, or projects.
- **tags**: 1-3 from: `prompting`, `agents`, `architecture`, `tools`, `evaluation`, `safety`, `context-engineering`, `mcp`, `workflows`, `performance`, `multi-agent`, `coding-agents`

### Step 3b: Quality Gate

Score each candidate against these 5 criteria. **Only insights passing 4/5 get written to the knowledge base.** The KB is cream, not bulk.

| # | Criterion | Pass | Fail |
|---|-----------|------|------|
| 1 | **Changes a decision** — would an agent do something differently after reading this? | Specific technique/pattern agent wouldn't arrive at alone | Truism, common sense, or obvious to any experienced SE |
| 2 | **Concrete** — has a specific what-to-do (numbers, thresholds, steps, architecture) | "20-50 tasks from real failures", "separate generator from evaluator" | "Use good practices", "prefer boring technology" |
| 3 | **Evidence-backed** — someone tried it and reported results | Benchmarks, case studies, specific failure stories, quoted data | Blog opinion, untested theory, "it should work" |
| 4 | **Applicable** — works in our environment (Claude Code, managed Win11, Python) | Principle transfers even if source is different platform | Platform-specific internals (OpenAI Responses API ordering, Codex sandbox) |
| 5 | **Not already encoded** — isn't already baked into CLAUDE.md, a skill, or the CLI | New technique not yet operationalized | Insight already lives in our rules, skills, or workflow docs |

For each rejected insight, record: title, which criteria failed, one-line reason.

**The KB is a staging area, not a permanent archive.** Insights graduate out when operationalized into CLAUDE.md, skills, or workflow docs. Redundant articles should be pruned.

### Step 4: Write Accepted Insight Files

For each insight that **passed the quality gate** (4/5+ criteria), create a file at `KNOWLEDGE_RAW/{date}-{slugified-title}.md`.

Do NOT write directly into the KB. Instead:

1. Create `TMP_IMPORT_DIR` if needed.
2. Write one temporary markdown file per accepted insight to `TMP_IMPORT_DIR/`.
3. Run `workflow knowledge lint /tmp/knowledge-import/<file>.md --json`.
4. Ingest each accepted file with `workflow knowledge ingest /tmp/knowledge-import/<file>.md`.
5. Let `workflow knowledge ingest` handle the destination filename and reindexing.
6. Run `workflow knowledge validate --json` after ingestion. If it fails, fix the temporary source metadata or article shape before treating the research run as complete.

Do NOT write rejected insights.

```markdown
---
title: {title}
source_url: {HTTP/HTTPS url}
source_title: {article title}
source_author: {author or organization}
date_published: {article date or "unknown"}
date_processed: {today YYYY-MM-DD}
tags: [{tag1}, {tag2}]
---

## Insight

{The actionable takeaway — what to do or know}

## Evidence

{Supporting data, benchmarks, quotes from the article}

## Applicability

{How this applies to the user's control plane, skills, agents, CLAUDE.md, or projects}
```

### Step 5: Record Fully Rejected Sources

Only record a source when it produced **zero accepted insights**. Accepted insights already live in the KB and should not be duplicated in a second index.

For a fully rejected source, write a temporary JSON payload like:

```json
{
  "url": "{url}",
  "title": "{article title}",
  "author": "{author or org}",
  "date_published": "{date}",
  "date_processed": "{today}",
  "candidates": {total extracted},
  "accepted": {passed quality gate},
  "rejected": {failed quality gate},
  "insight_files": ["{filename1}.md"],
  "rejection_reasons": ["{title} — not concrete", "{title} — already encoded"],
  "tags": ["{all unique tags from accepted insights}"]
}
```

Save that JSON to `TMP_IMPORT_DIR/<slug>-rejection.json`, then run:

`workflow knowledge record-rejection /tmp/knowledge-import/<slug>-rejection.json`

Do not edit `sources.json` directly. `workflow knowledge record-rejection` owns that write path.

### Step 6: Report

```
Processed: {article title}
Source: {url}
Candidates: {total} | Accepted: {accepted} | Rejected: {rejected}

Accepted (written to KB):
  1. {title} [tags] — 5/5
  2. {title} [tags] — 4/5
  ...

Rejected (not worth keeping):
  1. {title} — FAIL: not concrete, already encoded
  2. {title} — FAIL: not applicable (platform-specific)
  ...

Files written to: ~/.codex/knowledge/raw/
Run: workflow knowledge search <keyword> to find insights later.
```

## Workflow: Search Insights

When the user runs `/research search <query>`:

Run:

`workflow knowledge search "<query>"`

If the user needs the full entry after search, use:

`workflow knowledge summary <article>` or `workflow knowledge read <article>`

## Workflow: List Sources

When the user runs `/research list`:

Run:

`workflow knowledge list`

If the user specifically wants only one domain, use:

`workflow knowledge list --tag <tag>`

## Workflow: List Tags

When the user runs `/research tags`:

Run:

`workflow knowledge list`

or, when you need aggregate counts plus date range:

`workflow knowledge stats`

## Important

- Extract **actionable insights**, not article summaries. The question is always "what should I DO differently?"
- One insight per file. An article with 10 candidates may produce 3 accepted files — that's fine.
- **Quality over quantity.** An article that produces 0 accepted insights is a valid outcome. Report it honestly.
- If WebFetch fails (403, timeout), ask the user to paste the content. Process pasted text identically.
- Accepted files require canonical metadata: `source_url`, `source_title`, `source_author`, `date_published`, `date_processed`, and `tags`.
- Tags must come from the fixed set listed above. Do not invent new tags.
- Filenames use format: `YYYY-MM-DD-slugified-title.md` (max 80 chars for filename)
- Accepted insight files are append-only. Never modify existing KB entries.
- Rejected-source bookkeeping goes through `workflow knowledge record-rejection`, not direct JSON mutation.
- Accepted-source dedup must check the live KB first.
- **The KB is a staging area.** When an insight gets operationalized (encoded into CLAUDE.md, a skill, or workflow docs), it can be pruned from the KB. The KB should shrink over time as insights graduate into the system.
