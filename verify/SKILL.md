---
name: verify
description: "Dispatch repository verification through the narrowest declared validation owner and return one evidence-backed readiness verdict. Use when the operator asks to verify a build, run quality checks, validate current changes, or decide whether work is ready. Do not invent generic commands when AGENTS.md, package scripts, a phase gate, or a specialist skill already owns validation."
allowed-tools: Bash Read
---

# Verify

This skill coordinates verification; it does not own project-specific commands.

## Procedure

1. Read the narrowest applicable `AGENTS.md` validation section and any route it explicitly names.
2. Prefer, in order: a repo-declared phase gate, a repo validation script, package-manager scripts, then a narrowly inferred command only when no owner exists.
3. Run the smallest gate that covers the changed surface. Expand only after a failure or when the operator requests full verification.
4. Capture the command, exit status, relevant counts, and first actionable failure. Do not dump full logs.
5. For rendered UI, deployment, database, provider, or security work, invoke the matching specialist skill instead of approximating its proof.

## Verdict

Return:

- `READY` only when every required owner gate passed;
- `NOT READY` when a required gate failed;
- `UNVERIFIED` when the owning gate is unavailable or requires authority not granted.

Name skipped gates and why. A successful build alone does not prove rendered behavior, deployment state, persistence, authorization, or customer value.

## Boundary

`verify` owns orchestration and reporting. Repository instructions and specialist skills own the actual acceptance criteria and commands.
