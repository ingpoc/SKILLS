---
name: knowledge-base
description: "Maintain the canonical local agent-engineering knowledge corpus under ~/.codex/knowledge: ingest an accepted source, refresh an existing article from its primary source, repair metadata, reindex search, or rebuild the generated browser. Use only when the operator asks to change or maintain that corpus. Do not use for evaluating whether research should be adopted or for recalling session history."
allowed-tools: Read Write Bash
---

# Knowledge Base

The Markdown articles under `~/.codex/knowledge/raw/` are canonical. Search indexes and the HTML browser are generated views.

## Select one operation

- **Ingest:** add an operator-approved source as a new article.
- **Refresh:** update an existing article from its canonical primary source.
- **Maintain:** repair metadata, links, taxonomy, or generated views without adding research claims.
- **Query:** use the `workflow knowledge` commands; do not mutate the corpus.

## Mutation procedure

1. Read [frontmatter schema](references/frontmatter-schema.md) and the narrow operation-specific reference.
2. For external material, browse the canonical primary source using the current web capability. Do not rely on unavailable legacy tool names.
3. Keep sourced facts, inference, and operator decisions distinct. Never store credentials, customer content, or raw session transcripts.
4. Write or update one canonical Markdown article; do not edit the generated HTML browser.
5. Run the corpus lint and `workflow knowledge reindex`.
6. Rebuild the browser with `python3 scripts/build_browser.py` after a content mutation.
7. Query the changed topic and inspect the generated article before declaring success.

## Delegation

Use direct deterministic work for one or two articles. A bounded read-only sidecar is appropriate only for multiple independent primary sources; the main agent owns adoption decisions and writes.

## Boundary

- `research-evaluator`: decides whether external research should be adopted.
- `knowledge-base`: stores and retrieves accepted engineering knowledge.
- `recall`: reconstructs local session history.
- `context-graph`: stores project decision traces.

## References and scripts

- [frontmatter schema](references/frontmatter-schema.md)
- [learning and evidence rules](references/learning.md)
- [canonical surface URLs](references/surface-urls.md)
- [ingest gotchas](references/ingest-gotchas.md)
- `scripts/detect_updates.py` — compare tracked upstream versions.
- `scripts/build_browser.py` — rebuild the derived HTML browser.
