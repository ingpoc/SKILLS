# Session orchestration workflow

## Experiment hypothesis

Bounded fresh tasks are useful only if they preserve exact intent while reducing repeated discovery and compaction. Keep this workflow when two or more real handoffs satisfy all of these checks:

1. The successor restores the exact unfinished goal or intentionally selects the next goal after a completed one.
2. The successor begins from the saved first command without broad repository rediscovery.
3. Exactly one successor is created for each handoff.
4. Phase, spend, deployment, authentication, external-send, and destructive-action gates stop correctly.
5. Save, resume, and task-creation overhead is smaller than the avoided rediscovery and repeated compaction.

Drop the workflow when handoffs repeatedly require operator repair, duplicate work, lose goal criteria, or add more ceremony than they save.

## Entry lane

### Invocation contract

The operator invoking `$session-orchestrate` is the authorization signal. Do not ask them to repeat a fixed sentence such as "authorize a new recovery window."

1. Run `python3 scripts/entry.py` before broad retrieval.
2. When it returns `mode: resume-exact-goal`, call `get_goal` and compare against the exact objective in `goal_file`:
   - matching active goal -> reuse it;
   - no goal or the same goal in `blocked` state -> call `create_goal` with the exact file content; this invocation begins a fresh blocked audit;
   - a different active goal -> stop for conflict resolution;
   - the same goal already completed -> treat the checkpoint as stale and choose the next goal.
3. The invocation renews one bounded execution window for actions already authorized by that saved objective and route. A prior stop caused only by an expired retry window, temporary browser/tooling state, or operator pause is not a reason to ask for another phrase.
4. Preserve every saved constraint. Invocation alone never authorizes spend, deployment, external sends, destructive operations, credential inspection, or a phase change.
5. Follow `chain_action`: reuse an active chain, claim only a nonce-addressed pending handoff, or initialize a new bounded chain. For `resume-goal-chain-closed`, continue the exact goal in the current task while leaving the stopped chain untouched and creating no successor; the old boundary remains evidence, not a ban on in-task work.

### Preflight

1. Call `get_goal`. Preserve a matching unfinished goal; never replace a different unfinished goal.
2. Run `resume-session` when `CURRENT.md` exists, then use the exact goal file returned by `entry.py`. Verify any saved first command against current repository evidence before executing it.
3. Inspect the narrow owner section for delivery order. In BrandGPT, read the current `PRODUCTPLAN` phase section and its exit gate.
4. Initialize or claim chain state:
   - New chain: `python3 scripts/chain_state.py init --max-hops 3 --phase-boundary "<boundary>"`
   - Successor: `python3 scripts/chain_state.py claim --nonce "<nonce>"`

### Choose the goal

Choose one goal that has meaningful implementation plus verification but does not contain an entire product phase. A good goal usually owns one deliverable, one narrow integration seam, and its directly relevant proof.

Write the exact objective to a temporary Markdown file using these headings:

- `## Outcome`
- `## Scope`
- `## Constraints`
- `## Verification`
- `## Stop conditions`

Run `python3 scripts/validate_goal.py <goal-file>`. The deterministic envelope is 180–450 words with at least one concrete list item in Scope, Verification, and Stop conditions. If it fails, split or tighten the goal; do not loosen the validator to admit a phase-sized objective.

After validation:

1. Call `create_goal` with the exact Markdown objective.
2. Save its hash with `python3 scripts/chain_state.py set-goal --objective-file <goal-file>`.
3. Load at most one bounded owner slice needed for the first action.
4. The next tool action must be the smallest concrete implementation or verification attempt. Do not open a second design cycle. If no concrete attempt is safe, checkpoint the specific blocker and stop.
5. Work until the stop conditions are met or a real blocker is reached.

## Closeout lane

### Completed goal

1. Verify every stop condition with current evidence.
2. Call `update_goal` with `complete`.
3. Run `python3 scripts/checkpoint.py --goal-file <goal-file> --resume-policy reference-only --next-action "<next product-plan decision>" --verification "<proof summary>"`; do not hand-build multiline save-session environment variables.
4. Stop instead of spawning when the phase exit gate is complete, the next work crosses an authority boundary, or the chain reached `max_hops`.
5. Otherwise run `python3 scripts/chain_state.py prepare-handoff --kind next-goal`.

### Unfinished emergency handoff

Use only after an actual automatic compaction or when the current task cannot safely finish without another one:

1. Keep the active goal unfinished.
2. Run `python3 scripts/checkpoint.py --goal-file <goal-file> --resume-policy ensure-active --next-action "<exact first action>" --blocker "<specific blocker>" --verification "<completed and pending proof>"`.
3. Run `python3 scripts/chain_state.py prepare-handoff --kind continue-goal`.

### Create one successor

Read the JSON from `prepare-handoff`. Continue only when `spawn_allowed` is `true`.

1. Call `codex_app__list_projects` and match the project whose local root exactly equals the current repository root.
2. Call `codex_app__create_thread` once with that project id and a local environment. Do not choose a model unless the operator explicitly requested one.
3. Use this initial prompt, substituting the returned values:

   `This is an explicitly authorized session-orchestrate successor for chain <chain_id>, hop <pending_hop>/<max_hops>. Invoke $resume-session first, then $session-orchestrate and claim nonce <nonce>. Preserve an unfinished saved goal exactly; otherwise choose the next session-sized goal from the current owner plan. Create at most one successor and stop at authority or phase boundaries.`

4. Record the returned thread id with `python3 scripts/chain_state.py record-successor --nonce "<nonce>" --thread-id "<thread-id>"`.
5. End the current task. Do not continue implementation after spawning.

## Blocked or stopped

For a genuine blocker, call `update_goal blocked` only after the platform's repeated-blocker threshold is met. Otherwise leave the goal active, checkpoint the blocker, and stop without spawning when operator input is required.

Record the chain stop mechanically:

`python3 scripts/chain_state.py stop --status stopped --reason "<specific reason>"`

Use `completed` when the planned chain boundary is satisfied and `blocked` only for a true impasse.

## Trial scorecard

For each handoff record:

- goal exactness: pass/fail
- first action used saved route: pass/fail
- duplicate successor: count, expected zero
- operator repair prompts: count
- compactions before handoff: count
- approximate handoff overhead: tool calls and elapsed time
- authority/phase stop correctness: pass/fail

Record observed counters with `chain_state.py record-metric`. Operator steering that is required to escape repeated planning, retry, or closeout work counts as an operator repair.

After two real handoffs, keep only if all safety checks pass and at least one task avoided broad rediscovery or repeat compaction. Otherwise refine once; if the second trial remains flat or worse, delete the skill and hook.
