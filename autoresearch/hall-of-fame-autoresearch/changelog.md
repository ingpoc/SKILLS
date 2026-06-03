# Changelog — Hall of Fame Autoresearch

## Experiment 1 — keep

**Score:** 5/5 (100%) — improvement from baseline 3/5

**Change:** Added explicit instruction to step 6: "Write to `experiments/autoresearch/state.json` (the actual source path), NOT just to the output artifacts directory" AND "If no new data file updates were needed, explicitly log 'no updates needed' in the artifact log"

**Result:** EVAL 4 and EVAL 5 both fixed. State persistence now works correctly across iterations.

---

## Experiment 0 — baseline

**Score:** 3/5 (60%)

**Evals:**

- EVAL 1: Universe Coverage — PASS (30 symbols screened)
- EVAL 2: v4 Filter Correctness — PASS
- EVAL 3: Outcome Verification — PASS
- EVAL 4: Data File Updates — FAIL
- EVAL 5: State Persistence — FAIL

**Issues identified:**

- State.json written to output dir only, not source path
- No explicit "no updates needed" logging

**Mutation:** Added explicit path instruction + no-op logging requirement
