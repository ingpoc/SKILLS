---
name: enforcement
description: "Design a deterministic blocking gate for a repeated unsafe or invalid transition after advisory guidance has failed. Use when the operator asks to enforce a state transition, prevent a destructive or secret-bearing action, or convert a proven verification rule into a runtime guard. Do not assume Claude hook events or invent a hook surface; confirm the current runtime's supported mechanism first."
---

# Enforcement

Enforcement converts one already-proven invariant into a blocking control.

## Procedure

1. Identify the repeated invalid action and the existing deterministic assertion that detects it.
2. Confirm the actual runtime owner: repository script, CI gate, Codex rule, plugin hook, operating-system sandbox, or external service policy.
3. Place the block at the narrowest point before irreversible state change.
4. Fail closed only for destructive, secret, security, or external-send boundaries. Keep ordinary routing and quality guidance informational unless the repository explicitly requires a block.
5. Test an allowed case, a denied case, diagnostic output, and recovery after the condition is corrected.
6. Document how to disable or remove the guard safely.

## Boundary

- `determinism` owns the machine-checkable assertion.
- `enforcement` owns where and how that proven assertion blocks an action.
- `verify` reports readiness but does not create blocking runtime policy.

Runtime-specific hook schemas belong in the plugin or repository that implements them, not in this global skill.
