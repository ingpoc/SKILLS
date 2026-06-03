---
name: add-to-global-trigger
description: Route proposed additions to the global Codex control plane by deciding whether a request belongs in `~/.codex/AGENTS.md`, a global workflow or reference doc under `~/.codex/docs`, `~/.codex/bin/workflow.py`, or an enforceable non-prose surface. Use when asked to "add this to global AGENTS", "promote this workflow to global", "add a new global trigger", or decide whether something should be a trigger, workflow, reference, hook, lint rule, or runtime guard.
---

# Add To Global Trigger

## Overview

Use this skill to add or refuse additions to the global Codex trigger layer without blurring surface ownership. Decide the owner surface first, then edit only the surfaces the request actually needs.

Global scope only:
- `~/.codex/AGENTS.md`
- `~/.codex/docs/`
- `~/.codex/bin/workflow.py`

Do not use this skill for repo-local `AGENTS.md` work.

## Decision Order

1. Run `workflow summary placement`.
2. Search existing global docs, skills, and trigger lines before adding anything.
3. Classify the request into exactly one primary owner:
   - `AGENTS.md` for a short, stable routing rule that points to an existing durable target.
   - `docs/workflows/` for a runtime multi-step process.
   - `docs/references/` or `docs/quality-gate/` for authoring guidance, checklists, or validation rules.
   - hooks, lint, deny rules, or runtime config when the behavior is deterministic and enforceable.
   - `skills/` when the request is a reusable method with judgment.
4. Author the durable target before adding the trigger that points to it.
5. Edit `~/.codex/AGENTS.md` last.

If the request is longer than three short lines of stable instruction, do not put the full content in `AGENTS.md`. Create or update the owning surface and add only a compact trigger.

## Search Before Writing

Run targeted retrieval before editing:

```bash
workflow list
workflow search "<topic>"
rg -n "<topic>|<candidate-name>" ~/.codex/AGENTS.md ~/.codex/docs ~/.codex/skills -g '*.md'
```

Collapse duplicates instead of creating parallel guidance. If an existing doc or skill already owns the concept, update that surface rather than adding a new one.

## Surface Rules

### Trigger Only

Choose this path only when all of the following are true:
- the durable target already exists
- the rule is stable and short
- the trigger can route through `workflow summary <doc>` or another existing surface
- no new enforcement or new method is required

Before editing `~/.codex/AGENTS.md`, run:

```bash
workflow summary agentmd-quality-gate
```

### New Workflow or Reference Doc

Choose a new doc when the trigger needs a durable target.

- Use a workflow doc for runtime execution steps.
- Use a reference or quality-gate doc for authoring guidance or checklists.

Before creating the doc, run:

```bash
workflow summary workflow-doc-creation
```

Do not describe global doc creation as a reindex task. Global docs are discovered by filesystem scan.

### Workflow CLI Alias Support

Edit `~/.codex/bin/workflow.py` only when the new doc needs first-class short-name support through `workflow summary <name>`, `workflow read <name>`, or other alias-based routing.

Before changing `workflow.py`, run:

```bash
workflow summary workflow-cli-quality-gate
```

Measure before and after for the command path you changed. Treat alias support as a CLI surface change, not just a doc change.

### Enforced Instead of Prose

Do not add prose when the request is really about blocking or mechanically steering behavior. Prefer:
- `rumdl` for recurring Markdown misuse
- `ruff` for recurring Python misuse
- hooks or deny rules for unsafe actions
- runtime config for hard restrictions

If you route to enforcement, explain briefly why the request should not become a global trigger or doc.

## Authoring Order

Follow this order exactly:

1. `workflow summary placement`
2. search existing global surfaces
3. if creating a doc, `workflow summary workflow-doc-creation` and author the doc
4. if alias support is needed, `workflow summary workflow-cli-quality-gate` and update `~/.codex/bin/workflow.py`
5. if editing `AGENTS.md`, `workflow summary agentmd-quality-gate`
6. add or update the global trigger line in `~/.codex/AGENTS.md`
7. run validation for every touched surface

Use the exact command sequences in [surface-matrix.md](references/surface-matrix.md).

## Validation

Always validate the surfaces you touched.

- `~/.codex/AGENTS.md` changed:
  - verify the line is concise, bounded, and points to an existing target
- global doc created or edited:
  - `workflow registry`
  - `workflow lint`
- `~/.codex/bin/workflow.py` changed:
  - `workflow lint`
  - `workflow lint --full`
  - `python3 -m unittest discover -s /Users/gurusharan/.codex/tests -p 'test_workflow_cli_regression.py'`
  - manual check that `workflow summary <alias>` works

If `workflow registry` shows unrelated pre-existing drift, report it but do not fix it unless the requested change depends on it.

## Refusal Cases

Refuse or reroute when:
- the request is repo-local rather than global
- the content is session-specific
- the content is derivable from code or git history instead of deserving a durable doc
- the request wants prose where enforcement is the right owner
- the new trigger would duplicate an existing global trigger or doc
