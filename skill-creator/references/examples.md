# Skill Structure Examples

## Example 1: PDF Editor Skill

```
pdf-editor/
├── SKILL.md
│   Purpose: Rotate, merge, split PDFs
│   Trigger: "rotate this PDF", "merge PDFs"
│   Workflow: Detect operation → Use script → Verify output
│
├── scripts/
│   ├── rotate_pdf.py
│   ├── merge_pdf.py
│   └── split_pdf.py
│
└── references/
    └── advanced_operations.md
```

**Analysis:** Repeated code → scripts. Minimal SKILL.md. Advanced docs → references.

## Example 2: BigQuery Skill

```
big-query/
├── SKILL.md
│   Purpose: Query company BigQuery datasets
│   Trigger: "how many users logged in today"
│   Workflow: Identify tables → Check schema → Write query
│   Note: "See references/schema.md for table structure"
│
└── references/
    ├── schema.md (table schemas, relationships)
    └── query_patterns.md (common queries)
```

**Analysis:** Schema → references (avoid rediscovery). Workflow only in SKILL.md.

## Example 3: Frontend Webapp Builder

```
frontend-builder/
├── SKILL.md
│   Purpose: Build React/HTML webapps
│   Trigger: "build a todo app", "create dashboard"
│   Workflow: Copy template → Customize → Deploy
│
├── assets/
│   ├── react-template/
│   │   ├── src/
│   │   ├── public/
│   │   └── package.json
│   └── html-template/
│       └── index.html
│
└── references/
    └── component_patterns.md
```

**Analysis:** Boilerplate → assets (not loaded). Patterns → references.

## Example 4: Brand Guidelines Skill

```
brand-guidelines/
├── SKILL.md
│   Purpose: Apply company branding
│   Trigger: "make this match our brand"
│   Workflow: Load brand colors → Apply to artifact
│
├── assets/
│   ├── logo.png
│   ├── fonts/
│   └── templates/
│
└── references/
    ├── color_palette.md
    ├── typography.md
    └── messaging.md
```

**Analysis:** Visual assets → assets/. Style rules → references. SKILL.md = workflow only.

## Example 5: Internal Comms Skill

```
internal-comms/
├── SKILL.md
│   Purpose: Write company communications
│   Trigger: "write status update", "draft incident report"
│   Workflow: Identify format → Check references → Draft
│
└── references/
    ├── formats.md (status, incident, update templates)
    ├── tone_guide.md
    └── approval_process.md
```

**Analysis:** All details → references. SKILL.md = trigger + workflow pointer.

## Common Patterns

| Skill Type | SKILL.md | scripts/ | references/ | assets/ |
|------------|----------|----------|-------------|---------|
| Code automation | Workflow | Repeated code | APIs, patterns | - |
| Document creation | Workflow | - | Formats, guides | Templates, fonts |
| Data querying | Workflow | - | Schemas, examples | - |
| Brand/design | Workflow | - | Guidelines | Images, templates |
| Integration | Workflow | API clients | API docs | - |
