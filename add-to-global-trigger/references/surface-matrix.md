# Surface Matrix

Use this file for the exact command path after `SKILL.md` has established the owner surface.

## Matrix

| Request shape | Primary owner | Required gate | Required edits | Required validation |
| --- | --- | --- | --- | --- |
| Existing durable target, short routing line | `~/.codex/AGENTS.md` | `workflow summary agentmd-quality-gate` | update trigger line only | check the line points to a real target |
| New runtime multi-step process | `~/.codex/docs/workflows/` | `workflow summary workflow-doc-creation` | create or update workflow doc, then add trigger | `workflow registry`, `workflow lint` |
| New authoring checklist or gate | `~/.codex/docs/references/` or `~/.codex/docs/quality-gate/` | `workflow summary workflow-doc-creation` | create or update reference doc, then add trigger | `workflow registry`, `workflow lint` |
| New first-class short name such as `workflow summary foo` | `~/.codex/bin/workflow.py` plus doc owner | `workflow summary workflow-cli-quality-gate` | update `ALIASES` or other CLI routing, then add trigger if needed | `workflow lint`, `workflow lint --full`, CLI regression test, manual summary check |
| Deterministic misuse that should be blocked or enforced | hooks, lint, deny rule, or runtime config | surface-specific enforcement gate | do not add prose trigger by default | run the validation for the enforcement surface |

## Trigger-Only Path

Use this when the durable target already exists.

```bash
workflow summary placement
workflow search "<topic>"
rg -n "<topic>|<doc-name>" ~/.codex/AGENTS.md ~/.codex/docs ~/.codex/skills -g '*.md'
workflow summary agentmd-quality-gate
```

Then:
- update `~/.codex/AGENTS.md`
- confirm the trigger is short, bounded, and points to an existing target

## New Workflow + Trigger Path

Use this when the request is a runtime process and the trigger needs a durable target.

```bash
workflow summary placement
workflow search "<topic>"
rg -n "<topic>|<doc-name>" ~/.codex/AGENTS.md ~/.codex/docs ~/.codex/skills -g '*.md'
workflow summary workflow-doc-creation
```

Then:
- author the workflow doc under `~/.codex/docs/workflows/`
- if alias support is required, update `~/.codex/bin/workflow.py`
- run `workflow summary agentmd-quality-gate`
- update `~/.codex/AGENTS.md` last
- run:

```bash
workflow registry
workflow lint
```

If `workflow.py` changed, also run:

```bash
workflow lint --full
python3 -m unittest discover -s /Users/gurusharan/.codex/tests -p 'test_workflow_cli_regression.py'
workflow summary <new-name>
```

## New Reference + Trigger Path

Use this when the request is authoring guidance, a checklist, or a validation rule.

```bash
workflow summary placement
workflow search "<topic>"
rg -n "<topic>|<doc-name>" ~/.codex/AGENTS.md ~/.codex/docs ~/.codex/skills -g '*.md'
workflow summary workflow-doc-creation
```

Then:
- author the reference or quality-gate doc under `~/.codex/docs/references/` or `~/.codex/docs/quality-gate/`
- add CLI alias support only if the doc needs a stable short name
- run `workflow summary agentmd-quality-gate`
- update `~/.codex/AGENTS.md` last
- run:

```bash
workflow registry
workflow lint
```

## Alias-Update Path

Use this when first-class short-name routing is part of the request.

```bash
workflow summary workflow-cli-quality-gate
time bash -c 'workflow summary placement'  # or the closest affected command
```

Then:
- update `ALIASES` in `~/.codex/bin/workflow.py`
- keep the alias unique and aligned to one owning doc
- run:

```bash
time bash -c 'workflow summary <new-name>'
workflow lint
workflow lint --full
python3 -m unittest discover -s /Users/gurusharan/.codex/tests -p 'test_workflow_cli_regression.py'
workflow registry
```

Success means:
- `workflow summary <new-name>` resolves correctly
- `workflow registry` does not report the new doc as unregistered

## Use Enforcement Instead Of Prose

Use this when the real need is to block or mechanically steer behavior.

Examples:
- repeated Markdown misuse -> tighten `rumdl`
- repeated Python misuse -> tighten `ruff`
- repeated unsafe action -> hook or deny rule
- hard runtime restriction -> config or runtime guard

Do not add a new global trigger unless a small routing line is still useful after the enforcement surface exists.
