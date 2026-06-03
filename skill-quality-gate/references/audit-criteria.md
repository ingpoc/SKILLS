# Audit Criteria

Use this rubric with `scripts/audit.sh` output when scoring a skill.

## PASS / WARN / FAIL heuristics

### 1. Category fit
- PASS: clear best-fit skill category and workflow type
- WARN: partly mixed with another category
- FAIL: generic prompt blob with no skill identity

### 2. Gotchas section
- PASS: `## Gotchas` exists with 3+ real failure patterns and the advice changes behavior
- WARN: gotchas exist but are vague, generic, or fewer than 3 items
- FAIL: no gotchas section

### 3. Script audit
- PASS: fragile executable logic lives in `scripts/`, referenced script assets exist, and inline bash is short or illustrative (`inline_bash_lines` stays low)
- WARN: some inline bash remains but is short and illustrative, or script references exist without much executable weight
- FAIL: referenced script assets are missing, or heavy literal execution blocks are embedded in `SKILL.md`

### 4. Progressive disclosure
- PASS: concise core file plus references/scripts only when needed; section structure is easy to scan
- WARN: somewhat long but still navigable, or disclosure exists but weakly
- FAIL: overloaded monolith with no disclosure path, few sections, or no modular escape hatches

### 5. Railroading
- PASS: explains constraints with reasons, low imperative density, and enough `why` / `because` explanations to justify strict instructions
- WARN: moderate imperative phrasing or weak explanation
- FAIL: mostly orders with little reasoning, or imperative density is clearly high without compensating rationale

### 6. Obvious knowledge
- PASS: mostly non-obvious workflow or environment-specific guidance
- WARN: mixed with generic model knowledge
- FAIL: largely generic advice the model already knows

### 7. Environment compatibility
- PASS: `quick_validate.py` passes, frontmatter is current, and referenced runtime assets exist
- WARN: validator passes but there are minor compatibility caveats or environment assumptions to call out
- FAIL: invalid frontmatter, unsupported keys, missing referenced assets, or broken runtime assumptions

### 8. Storage audit
- PASS: persistence location is explicit and appropriate
- WARN: storage behavior is implied, not explicit
- FAIL: writes ambiguous or unsafe state

### 9. Description trigger quality
- PASS: concise trigger-oriented description with clear use cases and recognizable trigger phrases
- WARN: understandable but noisy, too short, or too broad
- FAIL: vague description that will not trigger reliably

## Metric cues from `audit.sh`

- `gotcha_item_count`: below 3 is usually a WARN unless the section is especially strong
- `inline_bash_lines`: high counts suggest executable logic should move into `scripts/`
- `missing_script_references` / `missing_reference_references`: any non-zero count is usually FAIL for Environment compatibility
- `section_count` and `workflow_step_count`: low counts can indicate weak structure or poor disclosure
- `imperative_density_pct`: treat as a cue, not a law; examples and tables can inflate it
- `unexpected_frontmatter_keys`: any non-zero count should align with validator failure or at least a strong warning
