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

## Entry lane

1. Resolve both roots once: `export SESSION_ORCHESTRATE_ROOT="$(git rev-parse --show-toplevel)" SESSION_ORCHESTRATE_SKILL="${CODEX_HOME:-$HOME/.codex}/skills/session-orchestrate"`. Then run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/entry.py" --root "$SESSION_ORCHESTRATE_ROOT"` before broad retrieval. The explicit root must be the caller's current Git product repository; entry ignores a stale root environment value, fails outside Git, and refuses the global skills repository. It then ensures only that product's `.session/`, migrates only same-root legacy state, and returns workspace freshness, checkpoint eligibility, chain consistency, a cheap owner/plan/status inventory, `orchestration_action`, and a structured `exploration` recommendation. Treat `mode` as checkpoint eligibility and `orchestration_action` as the next orchestration behavior. The cheap path does not mine session history, commit logs, or local skills.
2. Call `get_goal`. Preserve a matching unfinished goal. A different unfinished goal is a conflict; do not replace it.
3. Read the narrowest routing owner from `project_inventory.owner_routing_candidates`. Follow its declared product-plan or roadmap route. Filename candidates are fallback discovery only.
4. When `workspace.program_action` is `use-plan`, reuse the selected goal and source fingerprints; do not rebuild or repeat broad discovery. If `workspace.selection_probe` exists, rerun only that declared read-only selector and require its normalized target to match before activation. Otherwise read only the owner sections needed to identify the current phase, ordered deliverables, dependencies, and exit gate.
5. Read the implementation/status owner when one exists. Verify disputed or missing status against live repository or runtime evidence.
6. If the repository declares a deterministic next-work or queue selector, run it before choosing the goal. Persist its route, normalized target, and owner source references as `selection_probe`; the selected goal's `admission_target` must match. A mutable `dynamic-queue` map contains only that admitted unfinished goal and refreshes after completion instead of speculating about future queue items.
7. Follow `workspace.program_action`: `rebuild-plan` requires a fresh sync before selecting new work; `use-plan` permits the current selected goal only after any selection probe still matches; `product-complete` requires exit-gate readback; `review-blocked-goal` stops at its recorded gate.
8. Follow `exploration.action` below. The main agent owns the decision, validates every accepted finding against live files, and writes only normalized evidence into tracking.

### Conditional exploration

| Action | Meaning | Main-agent decision |
|---|---|---|
| `skip` | Program state is fresh, blocked, complete, or otherwise answerable through narrow deterministic reads | Do not spawn a scanner. |
| `first-migration` | No source-backed program map exists yet | Use `explorer` only when owner plus implementation state is broader than one or two deterministic reads. |
| `stale-rebuild` | A source fingerprint or generated projection invalidated an existing map | Read the changed owner slice first; delegate only when rebuilding requires a broad implementation-state comparison. |
| `conflict` | Checkpoint, chain, or program state contradicts another mechanical owner | Use a sidecar only for separable evidence gathering; keep conflict resolution and goal choice on the main thread. |

When delegation is justified, request the configured `explorer` role. Its TOML owns the read-only sandbox and compact-output contract while model and reasoning remain runtime-selected. Pass only the task-specific owner paths, exclusions, bounds, and exact deliverable. Require compact scan metrics, three to seven findings, duplicate findings, unknowns, and evidence references. Session history remains off unless explicitly needed and is capped at three relevant sessions.

If the callable spawn surface cannot select the configured `explorer`, do not claim its role contract was used. Work directly when the scan is small. An honestly labeled generic read-only sidecar is acceptable only when context isolation still has measured value. Do not launch recursive `codex exec` as an automatic fallback.

Collect the existing sidecar result before closing it. If a completion notification loses the payload, inspect or recover that agent result before retrying; never repeat a broad scan by default. Persist only main-agent-validated states (`proven`, `present_unverified`, `absent`, or `unknown`) and evidence references, never the raw transcript.

### Checkpoint decisions

| Entry mode | Meaning | Required action |
|---|---|---|
| `resume-exact-goal` | Mechanically fresh and chain-consistent candidate | Confirm the current owner plan still permits the exact goal and its constraints, then reuse/create only that exact goal. |
| `review-checkpoint` | Stale, malformed, divergent, completed, or conflicting state | Never activate the saved objective. Reconcile against current owner state and select through the new-goal lane. |
| `choose-next-goal` | No activatable saved goal | Build the program map from current owner state. |

Freshness is necessary, not sufficient. A product-plan change, newly completed work, a different active goal, or a new authority gate can still invalidate an otherwise fresh checkpoint.

If no product/roadmap owner exists, use an explicit current user objective as the temporary completion contract. If neither exists, stop for product-owner direction; do not fabricate a roadmap from repository shape or old sessions.

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

Encode the map with the schema in [program-schema.md](program-schema.md), then run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/session_workspace.py" sync --root "$SESSION_ORCHESTRATE_ROOT" --program-file <json>`. This atomically writes canonical `.session/TRACKING.json` and its generated `.session/PLAN.md` projection. Never edit `PLAN.md` directly. When an authoritative repository implementation-status owner exists, update it after verified progress as well; `.session` does not replace product-facing delivery records.

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

Run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/validate_goal.py" <goal-file> --delivery-unit <selected-delivery-unit>`. For an eligible legacy checkpoint that must remain byte-for-byte exact, add `--legacy-resume`; never use that exception for a newly selected goal. After validation:

1. Call `create_goal` with the exact Markdown objective, unless a matching unfinished goal already exists.
2. Mark the selected program goal `in_progress` with `"$SESSION_ORCHESTRATE_SKILL/scripts/session_workspace.py" mark`.
3. Initialize the chain with a hop budget equal to the number of substantive session goals in the current authorized phase, capped at 12: `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" init --max-hops <count> --phase-boundary "<boundary>"`. A successor claims its pending nonce instead. For `recover-orphaned-chain`, reuse the existing hop after the admission probe; do not initialize or increment the chain.
4. Save the exact goal hash with `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" set-goal --objective-file <goal-file>`.
5. Load only the owner slice and skills needed for the first action. Past skill usage is a routing hint, not a requirement to reload every prior skill.
6. Make the smallest concrete implementation or verification attempt in the next tool action.
7. Continue until the stop conditions pass or a real blocker/authority boundary is reached.

## Closeout lane

### Completed goal

1. Verify every stop condition with current evidence.
2. Mark the program goal `completed` with one or more evidence references. The helper refuses evidence-free completion.
3. Update the owning implementation/status surface if the repository declares one.
4. Call `update_goal complete`.
5. Run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/checkpoint.py" --goal-file <goal-file> --resume-policy reference-only --next-action "<next program-map decision>" --verification "<proof summary>"`.
6. Refresh only the implementation evidence affected by the completed goal. Rebuild the map only when an owner-source fingerprint changed; otherwise mark and select in the existing map. Run the admission probe on the next candidate. Stop when it reconciles to product/phase completion, crosses an authority boundary, or the chain reached `max_hops`.
7. Otherwise write and validate the exact next objective, then run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" prepare-handoff --kind next-goal --next-objective-file <next-goal-file> --next-delivery-unit <delivery-unit> --first-command "<exact first command>"`. Never spawn after reconciliation-only work.

### Unfinished handoff

Use only after actual automatic compaction or when another task is required to finish the same authorized goal:

1. Keep the active goal unfinished.
2. Run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/checkpoint.py" --goal-file <goal-file> --resume-policy ensure-active --next-action "<exact first action>" --blocker "<specific blocker>" --verification "<completed and pending proof>"`.
3. Run `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" prepare-handoff --kind continue-goal --first-command "<exact first command>"`.

### Create one successor

Continue only when `prepare-handoff` returns `spawn_allowed: true`.

1. Match the exact current repository root to a Codex project.
2. Create exactly one same-project successor task.
3. Use this prompt:

   `This is an authorized session-orchestrate successor for chain <chain_id>, hop <pending_hop>/<max_hops>. Invoke $session-orchestrate and claim nonce <nonce>. The handoff contains the exact admitted goal and first command; recover them mechanically and do not rebuild a fresh program map. Revalidate only if entry reports stale sources or a conflict. Create at most one successor and stop at authority or phase boundaries.`
4. Record the task id with `python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" record-successor --nonce "<nonce>" --thread-id "<thread-id>"`.
5. End the current task. Do not continue implementation after spawning.

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
| Claimed handoff interrupted before goal creation | Reclaim the same nonce, recover the exact objective and first command, call `create_goal`, then settle with `set-goal`. Do not increment history twice. |
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
| Past sessions disagree with current owner docs | Current owner docs and live evidence win. |
| Configured `explorer` is unavailable on the callable spawn surface | Work directly or use an honestly labeled generic read-only sidecar only when it still has clear ROI. |
| Sidecar result notification lacks its payload | Recover the existing result before considering a retry; do not repeat the broad scan automatically. |
| Sidecar reports file presence as completion | Record `present_unverified`; only accepted runtime or deterministic proof can establish `proven`. |
| A phase repeatedly needs the same project-specific test, deploy, runtime, or recovery recipe | Prove it once, then update or create one repository-local skill and record it as the relevant lifecycle route; do not add the recipe to this global skill. |
| A proposed local skill wraps one obvious command or duplicates a global owner | Keep the command inline or use the existing owner; do not create another surface. |
| Remaining work crosses spend, deployment, auth, destructive, secret, external-send, or phase authority | Stop and record the specific gate. |

## Mechanical stop

Record a chain stop with:

`python3 "$SESSION_ORCHESTRATE_SKILL/scripts/chain_state.py" stop --status stopped --reason "<specific reason>"`

Use `completed` only when the authorized phase or product completion gate is proven. Use `blocked` only for a true impasse under the platform's repeated-blocker rule.
