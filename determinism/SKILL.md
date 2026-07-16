---
name: determinism
description: "Design machine-checkable assertions, stable hashes, fixtures, and exit-code contracts for behavior that must be reproducible. Use when an outcome currently depends on subjective agent judgment or when prompts and generated artifacts need versioned integrity checks. Do not use merely to run an existing repository verification gate; that is verify's job."
---

# Determinism

Turn a repeated judgment into an executable contract.

## Procedure

1. Name the exact input, expected invariant, and authoritative readback.
2. Use the simplest deterministic mechanism: parser, schema, fixture, checksum, query, or narrow test.
3. Return a meaningful exit status: `0` for satisfied, nonzero for a specific failure class.
4. Keep diagnostics compact and stable enough for another script or agent to consume.
5. Version prompts or generated contracts when their semantics affect the result; record a hash when drift must be detected.
6. Prove both a passing case and a deliberately failing case.

## Boundary

- `determinism` designs the assertion or integrity mechanism.
- `verify` selects and runs the repository's declared gates.
- testing skills construct broader behavioral test suites.

## References

- [references/code-verification.md](references/code-verification.md) — executable assertion patterns.
- [references/prompt-versioning.md](references/prompt-versioning.md) — semantic versions and hashes for prompt contracts.
