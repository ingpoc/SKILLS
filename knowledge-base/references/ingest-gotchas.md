# Ingest Gotchas

Specific failure modes encountered on first KB-pass (2026-05-22). Future runs will hit them again unless flagged.

## 1. PATH shadow on WSL-2

**Symptom:** `workflow knowledge list --tag tools` returns `env: 'python': No such file or directory`.

**Cause:** A Windows-side `/mnt/c/Users/<user>/.local/bin/workflow` is earlier in `PATH` than the Linux binary at `/home/$USER/.local/bin/workflow`. The Windows wrapper invokes `python` (not `python3`), which isn't available on the Linux side.

**Diagnostic:**

```bash
type workflow              # shows path
which -a workflow          # all matches
head -1 $(which workflow)  # shebang of resolved binary
```

If `type workflow` returns `/mnt/c/...`, you're hitting the shadow.

**Fix:** Always invoke the Linux binary by full path:

```bash
/home/$USER/.local/bin/workflow knowledge list --tag tools --json
```

Or use the env-var passthrough directly:

```bash
CODEX_WORKFLOW_PUBLIC_ENTRYPOINT=1 python3 ~/.claude/bin/workflow.py knowledge list --tag tools --json
```

## 2. `python` vs `python3`

Most modern Linux distros (Ubuntu 22.04+, Debian 12+) ship `python3` only — no `python` symlink. The workflow CLI's wrapper script explicitly uses `python3`, but some subprocess paths in shell scripts may still call `python`. If a bash script in this skill ever fails with `env: 'python': No such file or directory`, audit the script for bare `python` invocations and change to `python3`.

## 3. Long titles → renamed slugs on ingest

**Symptom:** Wrote a rubric titled "Claude Agent SDK lever rubric — first-stop index of every option, callback, message type, and pattern". Tried `workflow knowledge read claude-agent-sdk-rubric` → "Article not found" with helpful hint pointing to `claude-agent-sdk-lever-rubric-first-stop-index-of-every-opti`.

**Cause:** Ingest derives the slug by lowercasing the title and truncating to ~55 chars after the date prefix.

**Fix:** Use short titles for rubrics (so the slug is predictable + matches the BEFORE triggers in `~/.claude/CLAUDE.md`):

- Bad: "Claude Agent SDK lever rubric — first-stop index of every option, callback, message type, and pattern" → slug truncated
- Good: "Claude Agent SDK rubric" → slug `claude-agent-sdk-rubric` (exactly 23 chars after date prefix)

The four canonical rubric titles:

- `Claude Agent SDK rubric`
- `Claude Code rubric`
- `Claude Managed Agents rubric`
- `Codex SDK rubric`

For lever articles, descriptive long titles are fine — search will find them even if the slug is truncated.

## 4. `--strict` lint catches `date_published: unknown` omissions

**Symptom:** 5 articles fail `workflow knowledge lint --strict --json` with empty top-level `errors`/`warnings` arrays.

**Cause:** The JSON shape nests errors under `results[].errors`, not at the top level. The actual error is `missing required frontmatter field 'date_published'`. Haiku writer agents commonly omit this field because the value is the literal string `unknown`.

**Diagnostic:**

```bash
workflow knowledge lint /tmp/kb-drafts/<file>.md --json | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('ok=', d.get('ok'))
print('errors=', d['results'][0]['errors'])
"
```

**Fix:** Pre-flight grep to find missing fields before lint:

```bash
for f in /tmp/kb-drafts/<date>-*.md; do
  if ! grep -q '^date_published:' "$f"; then
    echo "MISSING date_published: $f"
  fi
done
```

Then patch in `date_published: unknown` before `date_processed:` line. Single-line Python sed-like edit:

```python
content = open(p).read()
new = content.replace('source_author: Anthropic\ndate_processed:', 'source_author: Anthropic\ndate_published: unknown\ndate_processed:')
open(p, 'w').write(new)
```

## 5. Re-ingest leaves orphan slug files

**Symptom:** Edited a rubric title from long to short. Re-ingested. Now have two files in `~/.claude/knowledge/raw/`: the old long-slug AND the new short-slug.

**Cause:** Ingest writes a new file at the new slug; it doesn't delete the old file.

**Fix:** Manually delete the old before re-ingesting:

```bash
rm ~/.claude/knowledge/raw/<old-slug>.md
workflow knowledge ingest /tmp/kb-drafts/<file>.md --tags ...
```

Or run `workflow knowledge reindex` after manual deletion to refresh the search index.

## 6. Search scores are negative (BM25-like)

**Symptom:** Search returns scores like `-12.84`, `-11.69`, `-10.77`.

**Cause:** The search engine uses BM25 with log scoring. Lower magnitude = better match.

**Interpretation:**
- `-5.0` to `-8.0` → strong match (specific keyword in title)
- `-8.0` to `-12.0` → moderate match (keyword in body)
- `-12.0` to `-18.0` → weak match (related keyword)
- Below `-18.0` → barely relevant

Don't filter results by absolute threshold; take top N from sorted list.

## 7. Ingest JSON status differs from lint JSON status

**Symptom:** A Python one-liner that reads `json.load(sys.stdin)['status']` works for lint output but returns `?` for ingest output.

**Cause:** Different output shapes.

- `lint <file> --json`: `{"status": "failed", "results": [{"ok": false, "errors": [...]}]}`
- `ingest <file> --json`: outputs a different envelope where `status` may not be top-level (the bash output also shows reindex info before the JSON).

**Fix:** Parse ingest output more carefully. The reliable indicator of ingest success is the reindex count increasing, not the JSON status field:

```bash
before=$(ls ~/.claude/knowledge/raw/ | wc -l)
workflow knowledge ingest /tmp/kb-drafts/<file>.md --tags ... > /dev/null
after=$(ls ~/.claude/knowledge/raw/ | wc -l)
if [ $after -gt $before ]; then echo "ingested"; else echo "no-op"; fi
```

## 8. Parallel Haiku writers are the right cost lever

Empirical from first pass (2026-05-22):

- 4 parallel Haiku general-purpose agents, 12 articles each → ~2–3 min wall-clock, ~75K tokens per agent
- Sequential single-agent run → ~10× wall-clock for same output

The cost lever is **per-batch tokens**, not per-article. Bigger batch per agent = more amortization of system prompt + tool-call overhead.

**Optimal batch size:** 10–15 articles per Haiku general-purpose agent. Below 8 wastes setup cost; above 15 hits agent context limits and writes degrade.

## 9. Don't trust the rubric to find articles for you

Rubric tables CITE article slugs but agents read via `workflow knowledge search`, not by following slug links. So a slight slug-mismatch in a rubric table doesn't break the rubric's usefulness — but it does break the trail.

If you intend the agent to follow the slug, use `workflow knowledge read <slug>` in the rubric and verify the slug exists post-ingest:

```bash
for slug in claude-agent-sdk-rubric claude-code-rubric ...; do
  workflow knowledge read "$slug" --json | python3 -c "import sys,json; print(json.load(sys.stdin).get('status'))"
done
```

If `read` returns `error`, fix the title or update the rubric reference to the actual ingested slug.

## 10. The `--tags` flag on ingest is required-in-practice

Even though articles have `tags:` in frontmatter, the ingest CLI's `--tags` flag is not optional in practice. Tags from frontmatter are read but the CLI examples always pass `--tags` explicitly. Safest pattern:

```bash
tags=$(python3 -c "
import re
with open('$f') as fh: head = fh.read()[:2000]
m = re.search(r'tags:\s*\[([^\]]+)\]', head)
print(','.join([p.strip().strip(chr(34)).strip(chr(39)) for p in m.group(1).split(',')]) if m else '')
")
workflow knowledge ingest "$f" --tags "$tags" --json
```

## 11. WebFetch returns empty shells for JS-heavy sites

**Symptom:** `WebFetch` on claude.com/blog, anthropic.com/engineering, openai.com/news, or developers.openai.com returns HTML with only navigation chrome and JavaScript — no article body. The agent writes a stub article or fails because there's no content to synthesize.

**Cause:** These sites render article content client-side via React/Next.js. `WebFetch` only gets the initial HTML shell.

**Fix — detect and switch:**
1. After `WebFetch`, check if the content has readable prose (not just CSS/JS and nav links).
2. If the fetched content is under 200 words or consists only of site navigation, retry with `browser_navigate` + `browser_console` to extract the article body, or use the Hermes Chrome bridge.
3. The telltale sign: the fetched content has `<script>` tags and navigation links but no `<article>` or `<p>` tags with actual text.

**Sites that require browser tools:**
- `claude.com/blog/*` — all articles are JS-rendered
- `anthropic.com/engineering/*` — all articles are JS-rendered
- `openai.com/news/*` — all articles are JS-rendered
- `developers.openai.com/*` — all pages are JS-rendered

**Sites where WebFetch works fine:**
- `raw.githubusercontent.com/*` — CHANGELOG.md, models.json, etc.
- `code.claude.com/docs/en/changelog` — static markdown
- `arxiv.org/abs/*` — static HTML with readable body
