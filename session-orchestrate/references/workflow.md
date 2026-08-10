# Session orchestration workflow

## Outcome contract

`$session-orchestrate` turns the current product plan into a bounded sequence of session goals. It does not own product intent. It persists a source-fingerprinted execution map under `.session/`, refreshes that map from current owner documents and live evidence, then executes one goal.

The two planning levels are different:

- **Program map:** the ordered remaining goals needed to satisfy the product plan and its exit gates.
- **Session goal:** one independently verifiable slice of that map, including the actions to perform now.

The program map is derived and replaceable. `.session/TRACKING.json` owns its cross-session progress and evidence, while product-plan and implementation-status documents remain authoritative for product intent.

## Source precedence

Use evidence in this order:

1. Current user instructions and hard authority boundaries.
2. Repository routing instructions and the owner route they declare.
3. Product-plan, roadmap, phase, or acceptance-gate owner documents, including an `AGENTS.md`-declared composite owner chain when no single plan file exists.
4. Live implementation proof: code, tests, migrations, deployed/runtime evidence, and explicit status ledgers.
5. A mechanically eligible `CURRENT.md` goal and matching chain state.
6. Recent git history, project-session metadata, and prior skill usage as hints.

Lower sources never override higher sources. A commit, file, stale checkpoint, or past-session claim is not completion proof by itself.

## Operator DNA

Evidence basis: a 2026-07-10 through 2026-07-17 read-only analysis of 281 local
Codex sessions across 13 project roots, filtered to 1,451 user-authored prompt
records and 496 unique prompt texts. These are cross-project defaults for
judgment, not authority. Current explicit instructions, repository owners, live
evidence, and the boundaries in Source precedence always win. Normal runs must
not remine history to apply them.

| Priority | Default behavior |
|---|---|
| Product completion | Resolve the product plan, implementation status, and acceptance owners; say what is already proven and map the remaining exit gates. Optimize for customer-visible product progress, not activity or file counts. |
| First-principles judgment | Challenge requirements that do not improve usefulness, intuitive experience, quality, security, safety, or ease of use. Preserve model judgment for ambiguous product and architecture choices instead of keyword routing. |
| Goal shape and persistence | Select the smallest full-lifecycle goal that materially advances the plan. Keep implementation, proof, cleanup, and required promotion together; continue autonomously until its evidence passes, a true impasse exists, or an authority/phase boundary is reached. |
| Current truth | Prefer owner files, current code, and runtime readback over prose or old sessions. Use history only to locate a missing route or repeated learning, never to declare current completion. |
| Proof-layer honesty | Prove the actual claimed target. Distinguish source/build, local deterministic, rendered/runtime, and deployed customer proof; compare visual work to its reference and test locally before deployment when both layers apply. |
| Durable learning | Repeated friction belongs in the narrowest script, lint, hook, skill, workflow, or ledger owner. Fix that owner, delete displaced routes or advice, and leave future agents a reproducible path rather than a chat-only reminder. |
| Efficient execution | Improve quality, reliability, token use, context, and time together. Measure first. Use bounded cheaper agents for broad independent exploration when the treatment repays its overhead; keep integration, blocking decisions, and ambiguous judgment on the main thread. A first migration may justify a bounded current-state explorer; resumed deterministic work does not. |
| Reporting and authority | Lead with the actual outcome, remaining gap, exact blocker, and next owned action. Do not stop for a recap, role switch, or status question. Autonomy never grants spend, deployment, external-send, destructive, authentication, secret, signed-release, or new-phase authority. |

## Entry lane

1. Resolve both roots once: `export SESSION_ORCHESTRATE_ROOT="$(git rev-parse --show-toplevel)" SESSION_ORCHESTRATE_SKILL="${CODEX_HOME:-$HOME/.codex}/skills/session-orchestrate"`. Run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/entry.py" --compact --root "$SESSION_ORCHESTRATE_ROOT"` once; when an authorized successor prompt supplies a nonce, add `--claim-nonce <nonce>`. The explicit root must be the caller's current Git product repository. Entry returns checkpoint eligibility, chain consistency, compact owner/status inventory, `orchestration_action`, and a stable `route_receipt`. Reuse the receipt until one of its named invalidators changes. Never pipe a goal through `jq`, command substitution, or an improvised temporary-file rewrite.
2. If `route_receipt.reference_command` is present, run it once to read only the required workflow sections. Run `goal_detail_argv` only when the selected goal's actions or lifecycle routes are needed. Never read full workflow or tracking as a standard bookend. `execute-claimed-handoff` requires neither read: use `goal_file`, preserve its objective through `create_goal`, settle with `set-goal`, and execute `first_command`.
3. Call `get_goal`. Preserve a matching unfinished goal. A different unfinished goal is a conflict; do not replace it.
4. Read the narrowest routing owner from `project_inventory.owner_routing_candidates`. Follow its declared product-plan or roadmap route. Filename candidates are fallback discovery only.
5. When `workspace.program_action` is `use-plan`, reuse the selected goal and source fingerprints; do not rebuild or repeat broad discovery. If `workspace.selection_probe` exists, rerun only that declared read-only selector and require its normalized target to match before activation. Otherwise read only the owner sections needed to identify the current phase, ordered deliverables, dependencies, and exit gate.
6. Read the implementation/status owner when one exists. Verify disputed or missing status against live repository or runtime evidence.
7. If the repository declares a deterministic next-work or queue selector, run it before choosing the goal. Persist its route, normalized target, and owner source references as `selection_probe`; the selected goal's `admission_target` must match. A mutable `dynamic-queue` map contains only that admitted unfinished goal and refreshes after completion instead of speculating about future queue items.
8. Follow `workspace.program_action`: `rebuild-plan` requires a fresh sync before selecting new work; `use-plan` permits the current selected goal only after any selection probe still matches; `product-complete` requires exit-gate readback; `review-blocked-goal` stops at its recorded gate.
9. Follow `exploration.action` below. The main agent owns the decision, validates every accepted finding against live files, and writes only normalized evidence into tracking.

### Conditional exploration

| Action | Meaning | Main-agent decision |
|---|---|---|
| `skip` | Program state is fresh, blocked, complete, or otherwise answerable through narrow deterministic reads | Do not spawn a scanner. |
| `first-migration` | No source-backed program map exists yet | Consider delegation only when owner plus implementation state is broader than one or two deterministic reads. |
| `stale-rebuild` | A source fingerprint or generated projection invalidated an existing map | Read the changed owner slice first; delegate only when rebuilding requires a broad implementation-state comparison. |
| `conflict` | Checkpoint, chain, or program state contradicts another mechanical owner | Use a sidecar only for separable evidence gathering; keep conflict resolution and goal choice on the main thread. |

`exploration.action` identifies an evidence need, not an agent type. When it is not `skip`, load `codex-routing-policy` for the lane, `subagent-playbook` for the callable agent type, and `codex-efficient-delegation` for the direct-versus-delegate gate and treatment bounds. Work directly when the scan is small, blocking, tightly coupled, or duplicates main-thread retrieval. Pass only the task-specific owner paths, exclusions, bounds, and exact deliverable. Session history remains off unless explicitly needed and is capped at three relevant sessions.

If the callable spawn surface cannot select the configured `explorer`, do not claim its role contract was used. Work directly when the scan is small. An honestly labeled generic read-only sidecar is acceptable only when context isolation still has measured value. Do not launch recursive `codex exec` as an automatic fallback.

Collect the existing sidecar result before closing it. If a completion notification loses the payload, inspect or recover that agent result before retrying; never repeat a broad scan by default. Persist only main-agent-validated states (`proven`, `present_unverified`, `absent`, or `unknown`) and evidence references, never the raw transcript.

### Choose the execution container

Goal selection and execution-container selection are separate decisions:

| Container | Use only when |
|---|---|
| Current task | Default; one or two deterministic steps, the blocking implementation or decision, or tightly coupled judgment. |
| Bounded subagent | The same goal has an independent, owner-bounded outcome with compact proof, current-state recheck, and useful non-overlapping main-thread work. Let the routing/delegation owners choose `explorer`, `worker`, verifier, or complete-outcome reviewer. |
| Same-goal successor | Context is genuinely exhausted, a compaction boundary requires a fresh task, or the operator explicitly requests a new task. Pause the source Codex goal before preparing the handoff. |
| Next-goal successor | The current goal is completed with accepted evidence and the owner plan admits a materially different acceptance gap. Complete the source Codex goal before preparing the handoff. |

Tester/fixer/retester roles, proof continuation, deployment stages, and cleanup are not goal or successor boundaries. Keep the blocking step on the main thread unless a repository owner explicitly requires isolated role ownership with a disjoint write scope; then use one bounded worker and return to the same goal. Fresh customer, UI/UX, accessibility, or operator judgment uses the `codex-efficient-delegation` complete-outcome review variant—never page-, control-, or checklist-sized agents.

### Checkpoint decisions

| Entry mode | Meaning | Required action |
|---|---|---|
| `resume-exact-goal` | Mechanically fresh and chain-consistent candidate | Confirm the current owner plan still permits the exact goal and its constraints, then reuse/create only that exact goal. |
| `review-checkpoint` | Stale, malformed, divergent, completed, or conflicting state | Never activate the saved objective. Reconcile against current owner state and select through the new-goal lane. |
| `choose-next-goal` | No activatable saved goal | Build the program map from current owner state. |

Freshness is necessary, not sufficient. A product-plan change, newly completed work, a different active goal, or a new authority gate can still invalidate an otherwise fresh checkpoint.

If no product/roadmap owner exists, use an explicit current user objective as the temporary completion contract. If neither exists, stop for product-owner direction; do not fabricate a roadmap from repository shape or old sessions.

### Active chain review

Read `goal_detail_argv`, compare `route_receipt.current_goal_id`, the selected program goal, its status, and any unfinished Codex goal. If all identities match and the acceptance gap still fails, continue the same hop; never initialize a second chain. If an older state lacks `current_goal_id`, reconcile the chain hash and selected goal once, then bind the id through `set-goal`. Stop on a genuine identity conflict.

When entry reports `execute-pending-command`, execute only the returned command,
then immediately call `consume-command` with its exact hash and truthful result.
When it reports `resume-proof-campaign`, use the retained proof-owner packet;
do not rebuild the program map, mine history, increment a terminal blocker, or
create a successor.

### Closed chain review

Read the recorded stop reason and tactical checkpoint. Do not create a new chain while the program remains blocked or the stop reason still controls. A legacy authority stop may resume only after explicit authority and an exact goal-file hash match via `resume-authority --legacy-authority-stop`; a phase stop requires new phase authority. If the prior chain completed and the current owner permits more work, proceed through normal program-map selection.

## Build the program map

Before selecting a goal, derive a compact map containing:

1. **Completion gate:** the observable product-plan outcome and current phase boundary.
2. **Implemented evidence:** deliverables already proven, with owner sections or live proof.
3. **Unknowns:** claims that lack enough evidence; do not count them complete.
4. **Remaining goals:** ordered session-sized outcomes with prerequisites and authority gates.
5. **Selected goal:** the first unblocked goal whose prerequisites are satisfied.

Each remaining goal must be large enough to justify a task: one product deliverable, its direct integration seam, and the proof needed to accept it. It must name:

- one product-plan deliverable or narrow integration seam;
- prerequisites;
- concrete actions;
- observable verification;
- stop and authority boundaries.

### Aggregate the project lifecycle

Before splitting goals, inspect the current repository's declared implementation, test/runtime, promotion, acceptance, cleanup, and handoff routes. When several stages serve one owner-plan milestone or exit gate, represent them as one `project-lifecycle` delivery unit with two to eight ordered `lifecycle_stages`.

Every lifecycle stage records its id, kind, action, exact repository route, acceptance signal, and optional authority gate. The lifecycle must contain implementation plus a later verification against the repository's actual target. Beyond that core, derive stages from this project only:

- a web product may declare local verification, promotion, deployed verification, and an authorized handoff;
- a native or creative runtime may declare integration, editor/device/rendered verification, independent acceptance, cleanup, and optional capability hardening;
- a repository with no deployment or external handoff omits those stages entirely.

Do not force one project's lifecycle onto another. Promotion, authentication, spend, runtime teardown, and external-action boundaries pause the same exact goal with `ensure-active`; they do not create a micro-goal or authorize the action. A successor needed only for context limits uses `continue-goal`. Complete the goal only when every declared stage has evidence or preserves its exact authority blocker.

Use `bounded-deliverable` only when the owner plan genuinely defines an independently accepted slice without a multi-stage lifecycle. Do not label a test file, inventory pass, promotion, runtime retest, or notification as its own goal merely because it is a separate command.

### Harden project-local routes

The global orchestrator owns route discovery and the decision to preserve a proven route; it does not own project-specific commands. Prefer an existing repository-local skill or owner script. Update that owner when it is incomplete.

Create a repository-local skill only after the path works and at least one of these is true:

- the same project-specific setup, validation, cleanup, or recovery is expected across phases;
- two attempts encountered the same avoidable friction;
- the route combines three or more ordered commands, environment checks, retained evidence, or cleanup duties;
- a safety or authority boundary must be applied consistently by future agents.

Do not create a skill for one or two obvious deterministic commands, generic doctrine already owned globally, or an unproven workaround. Use the global skill-creation owner, place the result under the repository's declared local skill directory, validate it, and add only the narrow routing trigger the repository requires. Creating or repairing that capability is an action inside the current product goal, never a substitute micro-goal. Record the result as that lifecycle stage's `route`; future sessions reuse it without mining history.

Do not split a deliverable into inventory, source inspection, test-writing, and readback goals. Those are actions inside one goal. A proof-only goal is valid when the unproven runtime or release gate is itself a substantive product-plan exit gate.

Do not report a completion percentage from file counts, commit counts, test counts, or prose checkboxes. Report a percentage only when the owner plan defines a finite acceptance-gate denominator and every completed item has evidence.

Encode the map with the schema in [program-schema.md](program-schema.md), then run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/session_workspace.py" sync --root "$SESSION_ORCHESTRATE_ROOT" --program-file <json>`. This atomically writes canonical `.session/TRACKING.json` and its generated `.session/PLAN.md` projection. Never edit `PLAN.md` directly. When an authoritative repository implementation-status owner exists, update it after verified progress as well; `.session` does not replace product-facing delivery records. Rerun compact entry after sync; the next receipt owns goal admission.

## Choose and start one session goal

Before creating a goal, run an admission probe: at most five narrow owner or live-proof commands that answer whether the selected acceptance gap still fails. If current evidence already satisfies it, mark the program item completed with that evidence and select again in the same task. Reconciliation alone never initializes a chain, consumes a hop, or creates a successor. Stop only at product completion, an authority gate, or a real unresolved gap.

Write the admitted objective to a private temporary Markdown file with:

- `## Outcome`
- `## Plan linkage`
- `## Acceptance gap` with `- Current:` and `- Exit:` items
- `## Scope`
- `## Actions` for `bounded-deliverable`; omit it for `project-lifecycle`
- `## Expected durable delta` with an `- Implementation:` or `- Runtime:` item plus `- Evidence:`
- `## Delivery lifecycle` with ordered `[implementation]`, `[verification]`, and any project-required optional stage items when `delivery_unit` is `project-lifecycle`
- `## Constraints`
- `## Verification`
- `## Stop conditions`

The objective should be concise and no longer than 300 words; do not pad it to meet a minimum. `Acceptance gap`, `Expected durable delta`, `Verification`, and `Stop conditions` must contain concrete list items. A bounded deliverable's `Actions` must also be concrete; a project lifecycle's structured stages own its actions, so duplicating `## Actions` is invalid. The durable delta must name both the changed implementation/runtime surface and retained acceptance evidence. For a legacy exact checkpoint, preserve its text exactly; do not rewrite it merely to adopt the newer template.

Run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/validate_goal.py" <goal-file> --delivery-unit <selected-delivery-unit>`. For an eligible legacy checkpoint, add `--legacy-resume`; never use that exception for a newly selected goal. Every transaction canonicalizes trailing whitespace to one final newline, so use the same goal file rather than shell-extracting its text. After validation:

1. Call `create_goal` with the exact Markdown objective, unless a matching unfinished goal already exists.
2. Mark the selected program goal `in_progress` with `"$SESSION_ORCHESTRATE_SKILL/scripts/session_workspace.py" mark`.
3. Initialize the chain with a hop budget equal to the number of substantive session goals in the current authorized phase, capped at 12: `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" init --max-hops <count> --phase-boundary "<boundary>"`. A successor claims its pending nonce instead. For `recover-orphaned-chain`, reuse the existing hop after the admission probe; do not initialize or increment the chain.
4. Bind the selected goal id and exact canonical objective with `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" set-goal --goal-id <selected-goal-id> --objective-file <goal-file>`.
5. Load only the owner slice and skills needed for the first action. Past skill usage is a routing hint, not a requirement to reload every prior skill.
6. Make the smallest concrete implementation or verification attempt in the next tool action.
7. Complete implementation and migrations before final rendered/runtime acceptance. If source changes afterward, invalidate only affected evidence and rerun it.
8. Continue until the stop conditions pass, a true impasse occurs, or an authority/phase boundary is reached.

### Freeze before expensive acceptance

Do not enter repeated capture or blind-review loops while the behavioral contract
or proof owner is still changing. Before final rendered or independent acceptance:

1. Freeze the owner-backed acceptance rubric, including positive and applicable
   negative/recovery outcomes.
2. Review the semantic proof contract first. A dispatched action, preview flag,
   build, or screenshot cannot substitute for the claimed visible or persisted
   postcondition.
3. Finish the coherent source batch and retain cheap targeted proof that the
   proof owner fails closed.
4. Create one immutable artifact root keyed by the current product fingerprint,
   then record readiness:

```bash
python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" freeze-proof \
  --product-fingerprint "<current product source fingerprint>" \
  --acceptance-contract "<owner section or compact rubric reference>" \
  --proof-owner "<repository proof route>" \
  --artifact-root "<immutable fingerprint-keyed evidence root>" \
  --evidence "<semantic proof-contract review or targeted proof>"
```

Run the expensive build/capture campaign once from that frozen source. Give one
frozen packet to the repository's independent-review owner. Consolidate all
reviewers' P0-P2 findings before one coherent fix batch; do not spawn a new review
pair for each finding. Any later source mutation invalidates the freeze: run
`freeze-proof` again after targeted repair. The helper records source freezes,
post-freeze mutations, proof reruns, and final review cycles in chain metrics.

## Closeout lane

Record every material proof generation before using it for completion:

```bash
python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" record-proof \
  --scope "<owner-defined acceptance surface>" \
  --proof-status pass \
  --product-fingerprint "<current product source fingerprint>" \
  --proof-environment-fingerprint "<runner/runtime fingerprint when relevant>" \
  --result "<concise exact result>" \
  --evidence "<retained artifact path or stable id>"
```

A final rendered or independent acceptance generation adds
`--final-acceptance`. The helper rejects it unless its product fingerprint and
evidence match the current frozen readiness packet.

A new generation supersedes only the same scope. Product source and proof
environment remain separate so a runner repair does not pretend the product
changed, while older runner-dependent proof cannot silently remain current.
Use the returned generation id in completion evidence.

### Completed goal

1. Verify every stop condition with current evidence.
2. Mark the program goal `completed` with one or more evidence references. The helper refuses evidence-free completion.
3. Update the owning implementation/status surface if the repository declares one.
4. Call `update_goal complete`.
5. Run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/checkpoint.py" --goal-file <goal-file> --resume-policy reference-only --next-action "<next program-map decision>" --verification "<proof summary>"`.
6. Refresh only the implementation evidence affected by the completed goal. Rebuild the map only when an owner-source fingerprint changed; otherwise mark and select in the existing map. Run the admission probe on the next candidate. Stop when it reconciles to product/phase completion, crosses an authority boundary, or the chain reached `max_hops`.
7. Otherwise write and validate the exact next objective, then run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" prepare-handoff --kind next-goal --reason completed-goal --source-goal-state completed --completion-evidence "<accepted current-goal proof>" --next-goal-id <next-goal-id> --next-objective-file <next-goal-file> --next-delivery-unit <delivery-unit> --first-command "<exact first command>"`. Never spawn after reconciliation-only work.

### Unfinished handoff

Use only after actual automatic compaction or when another task is required to finish the same authorized goal:

1. Keep the active goal unfinished.
2. Run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/checkpoint.py" --goal-file <goal-file> --resume-policy ensure-active --next-action "<exact first action>" --blocker "<specific blocker>" --verification "<completed and pending proof>"`.
3. Call `update_goal paused` so the source task cannot resume implementation after transfer.
4. Run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" prepare-handoff --kind continue-goal --reason <context-exhausted|compaction-boundary|operator-requested-task> --source-goal-state paused --first-command "<exact first command>"`. A role change, review, fix, retest, or proof continuation does not qualify for this lane.

### Awaiting authority

Use this for authentication, deployment, spend, secrets, destructive operations, or external sends that require operator authority. It is not a terminal blocker and does not justify a successor.

1. Checkpoint the exact unfinished goal with `ensure-active`.
2. Run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" await-authority --goal-file <goal-file> --reason "<specific gate>" --next-command "<first authorized command>"`.
3. Stop without marking the goal or chain blocked. Status questions, authentication handoffs, and operator repair prompts do not count toward repeated-blocker thresholds.

### Proof campaign pause

Use this when a repository-owned verification campaign exhausts its bounded
recovery but the exact product goal is still actionable. First consume the
attempted command with result `blocked`, then persist the blocker:

```bash
python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" pause-proof \
  --owner "<proof owner>" --scope "<acceptance surface>" \
  --reason "<exact observed blocker>" \
  --next-command "<first owner diagnostic or rerun command>" \
  --product-fingerprint "<current product source fingerprint>" \
  --proof-environment-fingerprint "<current runner/runtime fingerprint>" \
  --evidence "<retained blocker artifact>" --recovery-used
```

This records a blocked proof generation and changes the chain to
`proof_blocked`; it does not consume a hop, authorize another phase, create a
successor, or count as terminal goal blockage. After the proof owner is repaired
and independently checked, run `resume-proof --reason "<repair evidence>"`.
Execute its returned command once and consume its hash. If the same blocker
persists, update the same scoped proof packet rather than reopening discovery.
4. After explicit authority, run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" resume-authority --reason "<authority supplied>"`, then continue the same goal and hop from the returned `goal_file`.

### Create one successor

This is continuity transfer, not subagent delegation. Use it only after the execution-container decision selects a successor.

An explicit `$session-orchestrate` invocation or explicit successor-task request is the user request required by `codex_app__create_thread`. Do not request separate confirmation after `prepare-handoff` returns `spawn_allowed: true`; apply the zero-successor conditions from Hard rule 3.

1. For `continue-goal`, checkpoint the exact objective and pause the source Codex goal. Prepare with `--reason context-exhausted|compaction-boundary|operator-requested-task --source-goal-state paused`.
2. For `next-goal`, record current-goal completion, call `update_goal` with `complete`, and prepare with `--reason completed-goal --source-goal-state completed --completion-evidence <accepted-proof>`.
3. Continue only when `prepare-handoff` returns `spawn_allowed: true`; it rejects role-switch/retest handoffs and non-terminal source goals.
4. Use `codex_app__list_projects` to match the exact current repository root, then use `codex_app__create_thread` to create exactly one same-project successor task. Do not substitute a subagent.
5. Use this prompt:

   `This is an authorized session-orchestrate successor for chain <chain_id>, hop <pending_hop>/<max_hops>. Invoke $session-orchestrate with claim nonce <nonce>. Pass the nonce to entry; use its exact goal_file and first_command without plan, history, memory, or full-workflow discovery. Create at most one successor and pause the same goal at authority boundaries.`
6. Record the task id with `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" record-successor --nonce "<nonce>" --thread-id "<thread-id>"`.
7. End the current task. The paused/completed source goal must not resume implementation after spawning.

If task creation is unavailable or fails, leave the chain `handoff_pending`, retain the nonce and exact objective, report the exact failure, and do not prepare or create a duplicate successor.

## Negative scenarios

| Scenario | Result |
|---|---|
| Fresh task, no checkpoint | Build the map from current owner state. |
| Fresh program map and no resumable checkpoint | Reuse tracking, probe its selected gap, and avoid broad plan or session mining. |
| `.session/` missing with legacy state present | Copy legacy checkpoint and chain once, retain legacy files, then use only `.session/`. |
| Product-plan source changed after tracking sync | Return `rebuild-plan`; do not execute the stale selected goal. |
| Tracking uses an older orchestration policy | Return `rebuild-plan`; preserve evidence while regrouping fragmented work into the current delivery unit. |
| Generated `PLAN.md` was edited | Return `rebuild-plan`; regenerate it from canonical tracking. |
| Old or future-dated checkpoint | Review only; never activate it. |
| Wrong root, branch, missing commit, or invalid route | Review only. |
| Fresh checkpoint but product plan changed | Reconcile; use the normal new-goal lane if the exact goal is no longer current. |
| Matching checkpoint but chain goal hash differs | Review conflict; do not create a goal. |
| Completed chain or completed active goal | Select the next current goal; never reopen it. |
| Selected goal already passes its admission probe | Reconcile it inline and select again; do not create a goal, chain, or successor for that item. |
| One accepted milestone is split into implementation, test/runtime proof, promotion, retest, cleanup, or handoff micro-goals | Rebuild it as one repository-defined `project-lifecycle` goal. Omit stages this project does not own; preserve authority gates and use unfinished continuation across context boundaries. |
| Claimed handoff interrupted before goal creation | Pass the same nonce to entry. Reuse `.session/CLAIMED_GOAL.md`, call `create_goal`, then settle with `set-goal`. Do not increment history twice or extract objective text through the shell. |
| Legacy active chain has no goal hash but `CURRENT.md` has an eligible exact goal | Follow `recover-unset-goal`: create or preserve that exact goal, then settle the chain with `set-goal`; do not start another chain. |
| Active chain has no goal or handoff and `CURRENT.md` is `reference-only` | Follow `recover-orphaned-chain`: reuse fresh tracking, admission-probe its selected goal, reconcile already-proven items inline, then bind the first substantive goal with `set-goal`. Do not initialize a chain or consume another hop. |
| Command resolves `~/.codex/skills` as project root | Refuse without writing state; rerun from or pass the actual product root. |
| Invocation is outside Git or a chain helper's exported root differs from the current Git repository | Refuse without writing state; never fall back to the current directory, a previous project, or a stale environment value. |
| Different active goal | Stop for conflict resolution. |
| Product plan exists but status is unclear | Verify live evidence and mark unknown, not complete. |
| No file named product plan, but `AGENTS.md` declares authoritative scope, status, and acceptance routes | Use that composite owner chain as `plan_sources`; filename heuristics do not override repository routing. |
| No authoritative completion owner or explicit product objective | Stop for product-owner direction. |
| Repository selector target disagrees with the selected goal | Reject the map and rebuild from the selector target; do not activate a structurally valid but stale goal. |
| A mutable queue exposes future candidates | Persist only the exact admitted unfinished goal, then rerun the selector after completion; do not enumerate speculative queue goals. |
| `.session` is stale or an active chain is orphaned | Rebuild `TRACKING.json` and `PLAN.md` in place from current owners. Preserve `CURRENT.md`, `ORCHESTRATION.json`, admitted/claimed goals, nonces, blockers, history, and successor ids; never recover by deleting `.session`. |
| Past sessions disagree with current owner docs | Current owner docs and live evidence win. |
| Delegation is considered | Route through `codex-routing-policy`, `subagent-playbook`, and `codex-efficient-delegation`; do not duplicate their agent-type matrix here. |
| A tester/fixer/retester role change is proposed as a successor | Reject it. Work directly or use one bounded owner-isolated worker under the same goal. |
| A successor is proposed while the source Codex goal is active | Pause it for `continue-goal`, or complete it with accepted evidence for `next-goal`, before preparing the handoff. |
| Bare `$session-orchestrate` completes a goal and the next eligible goal returns `spawn_allowed: true` | Create exactly one same-project successor without asking again, then record its task id. |
| Successor task creation is unavailable or fails | Preserve `handoff_pending` and the nonce, report the exact failure, and do not prepare a duplicate. |
| Sidecar result notification lacks its payload | Recover the existing result before considering a retry; do not repeat the broad scan automatically. |
| Sidecar reports file presence as completion | Record `present_unverified`; only accepted runtime or deterministic proof can establish `proven`. |
| A phase repeatedly needs the same project-specific test, deploy, runtime, or recovery recipe | Prove it once, then update or create one repository-local skill and record it as the relevant lifecycle route; do not add the recipe to this global skill. |
| A proposed local skill wraps one obvious command or duplicates a global owner | Keep the command inline or use the existing owner; do not create another surface. |
| Remaining work crosses spend, deployment, auth, destructive, secret, or external-send authority | Checkpoint and use `await-authority`; resume the same goal only after explicit authority. |
| Remaining work crosses into a new product phase | Stop the chain at the recorded phase boundary; do not infer authorization. |
| A repository testing owner already returned an exact issue, blocker, verification state, and next command | Use that packet directly; skip broad session introspection unless uncaptured improvised recovery or repeated friction remains. |
| Proof emits raw logs, base64, large screenshots, or repeated full files | Keep within `route_receipt.evidence_budget`; retain artifact paths, stable ids or hashes, and concise results. |

## Mechanical stop

Record a chain stop with:

`python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" stop --status stopped --reason "<specific reason>"`

Use `completed` only when the authorized phase or product completion gate is proven. Use `blocked` only for a true impasse under the platform's repeated-blocker rule.
