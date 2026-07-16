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
3. Product-plan, roadmap, phase, or acceptance-gate owner documents.
4. Live implementation proof: code, tests, migrations, deployed/runtime evidence, and explicit status ledgers.
5. A mechanically eligible `CURRENT.md` goal and matching chain state.
6. Recent git history, project-session metadata, and prior skill usage as hints.

Lower sources never override higher sources. A commit, file, stale checkpoint, or past-session claim is not completion proof by itself.

## Entry lane

1. Run `python3 scripts/entry.py` before broad retrieval. It ensures `.session/`, migrates legacy state when needed, and returns workspace freshness, checkpoint eligibility, chain consistency, a cheap owner/plan/status inventory, and a structured `exploration` recommendation. The cheap path does not mine session history, commit logs, or local skills.
2. Call `get_goal`. Preserve a matching unfinished goal. A different unfinished goal is a conflict; do not replace it.
3. Read the narrowest routing owner from `project_inventory.owner_routing_candidates`. Follow its declared product-plan or roadmap route. Filename candidates are fallback discovery only.
4. Read only the plan sections needed to identify the current phase, ordered deliverables, dependencies, and exit gate.
5. Read the implementation/status owner when one exists. Verify disputed or missing status against live repository or runtime evidence.
6. Follow `workspace.program_action`: `rebuild-plan` requires a fresh sync before selecting new work; `use-plan` permits the current selected goal; `product-complete` requires exit-gate readback; `review-blocked-goal` stops at its recorded gate.
7. Follow `exploration.action` below. The main agent owns the decision, validates every accepted finding against live files, and writes only normalized evidence into tracking.

### Conditional exploration

| Action | Meaning | Main-agent decision |
|---|---|---|
| `skip` | Program state is fresh, blocked, complete, or otherwise answerable through narrow deterministic reads | Do not spawn a scanner. |
| `first-migration` | No source-backed program map exists yet | Use `cost_scan` only when owner plus implementation state is broader than one or two deterministic reads. |
| `stale-rebuild` | A source fingerprint or generated projection invalidated an existing map | Read the changed owner slice first; delegate only when rebuilding requires a broad implementation-state comparison. |
| `conflict` | Checkpoint, chain, or program state contradicts another mechanical owner | Use a sidecar only for separable evidence gathering; keep conflict resolution and goal choice on the main thread. |

When delegation is justified, request the custom `cost_scan` role. Its TOML owns model, reasoning, and read-only sandbox settings; do not duplicate those values here. Pass only the task-specific owner paths, exclusions, bounds, and exact deliverable. Require compact scan metrics, three to seven findings, duplicate findings, unknowns, and evidence references. Session history remains off unless explicitly needed and is capped at three relevant sessions.

If the callable spawn surface cannot select `cost_scan`, do not claim its configured model was used. Work directly when the scan is small. A built-in read-only explorer is an honest fallback only when context isolation still has measured value. Do not launch recursive `codex exec` as an automatic fallback.

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

Each remaining goal must name:

- one product-plan deliverable or narrow integration seam;
- prerequisites;
- concrete actions;
- observable verification;
- stop and authority boundaries.

Do not report a completion percentage from file counts, commit counts, test counts, or prose checkboxes. Report a percentage only when the owner plan defines a finite acceptance-gate denominator and every completed item has evidence.

Encode the map with the schema in [program-schema.md](program-schema.md), then run `python3 scripts/session_workspace.py sync --root <root> --program-file <json>`. This atomically writes canonical `.session/TRACKING.json` and its generated `.session/PLAN.md` projection. Never edit `PLAN.md` directly. When an authoritative repository implementation-status owner exists, update it after verified progress as well; `.session` does not replace product-facing delivery records.

## Choose and start one session goal

Write the selected objective to a private temporary Markdown file with:

- `## Outcome`
- `## Plan linkage`
- `## Scope`
- `## Actions`
- `## Constraints`
- `## Verification`
- `## Stop conditions`

The objective should be 180–450 words. `Actions`, `Verification`, and `Stop conditions` must contain concrete list items. For a legacy exact checkpoint, preserve its text exactly; do not rewrite it merely to adopt the newer template.

Run `python3 scripts/validate_goal.py <goal-file>`. For an eligible legacy checkpoint that must remain byte-for-byte exact, use `python3 scripts/validate_goal.py <goal-file> --legacy-resume`; never use that exception for a newly selected goal. After validation:

1. Call `create_goal` with the exact Markdown objective, unless a matching unfinished goal already exists.
2. Mark the selected program goal `in_progress` with `session_workspace.py mark`.
3. Initialize the chain with a hop budget equal to the number of session goals in the current authorized phase, capped at 12: `python3 scripts/chain_state.py init --max-hops <count> --phase-boundary "<boundary>"`. A successor claims its pending nonce instead.
4. Save the exact goal hash with `python3 scripts/chain_state.py set-goal --objective-file <goal-file>`.
5. Load only the owner slice and skills needed for the first action. Past skill usage is a routing hint, not a requirement to reload every prior skill.
6. Make the smallest concrete implementation or verification attempt in the next tool action.
7. Continue until the stop conditions pass or a real blocker/authority boundary is reached.

## Closeout lane

### Completed goal

1. Verify every stop condition with current evidence.
2. Mark the program goal `completed` with one or more evidence references. The helper refuses evidence-free completion.
3. Update the owning implementation/status surface if the repository declares one.
4. Call `update_goal complete`.
5. Run `python3 scripts/checkpoint.py --goal-file <goal-file> --resume-policy reference-only --next-action "<next program-map decision>" --verification "<proof summary>"`.
6. Rebuild and sync the program map to select the next goal or prove completion. Stop when the product/phase exit gate is complete, the next work crosses an authority boundary, or the chain reached `max_hops`.
7. Otherwise run `python3 scripts/chain_state.py prepare-handoff --kind next-goal`.

### Unfinished handoff

Use only after actual automatic compaction or when another task is required to finish the same authorized goal:

1. Keep the active goal unfinished.
2. Run `python3 scripts/checkpoint.py --goal-file <goal-file> --resume-policy ensure-active --next-action "<exact first action>" --blocker "<specific blocker>" --verification "<completed and pending proof>"`.
3. Run `python3 scripts/chain_state.py prepare-handoff --kind continue-goal`.

### Create one successor

Continue only when `prepare-handoff` returns `spawn_allowed: true`.

1. Match the exact current repository root to a Codex project.
2. Create exactly one same-project successor task.
3. Use this prompt:

   `This is an authorized session-orchestrate successor for chain <chain_id>, hop <pending_hop>/<max_hops>. Invoke $session-orchestrate and claim nonce <nonce>. Rebuild the program map from current product-plan and implementation evidence. Preserve a still-eligible unfinished goal exactly; otherwise choose the next unblocked session goal. Create at most one successor and stop at authority or phase boundaries.`

4. Record the task id with `python3 scripts/chain_state.py record-successor --nonce "<nonce>" --thread-id "<thread-id>"`.
5. End the current task. Do not continue implementation after spawning.

## Negative scenarios

| Scenario | Result |
|---|---|
| Fresh task, no checkpoint | Build the map from current owner state. |
| `.session/` missing with legacy state present | Copy legacy checkpoint and chain once, retain legacy files, then use only `.session/`. |
| Product-plan source changed after tracking sync | Return `rebuild-plan`; do not execute the stale selected goal. |
| Generated `PLAN.md` was edited | Return `rebuild-plan`; regenerate it from canonical tracking. |
| Old or future-dated checkpoint | Review only; never activate it. |
| Wrong root, branch, missing commit, or invalid route | Review only. |
| Fresh checkpoint but product plan changed | Reconcile; use the normal new-goal lane if the exact goal is no longer current. |
| Matching checkpoint but chain goal hash differs | Review conflict; do not create a goal. |
| Completed chain or completed active goal | Select the next current goal; never reopen it. |
| Different active goal | Stop for conflict resolution. |
| Product plan exists but status is unclear | Verify live evidence and mark unknown, not complete. |
| No product plan and no explicit product objective | Stop for product-owner direction. |
| Past sessions disagree with current owner docs | Current owner docs and live evidence win. |
| `cost_scan` is unavailable on the callable spawn surface | Work directly or use an honestly labeled built-in read-only explorer only when it still has clear ROI. |
| Sidecar result notification lacks its payload | Recover the existing result before considering a retry; do not repeat the broad scan automatically. |
| Sidecar reports file presence as completion | Record `present_unverified`; only accepted runtime or deterministic proof can establish `proven`. |
| Remaining work crosses spend, deployment, auth, destructive, secret, external-send, or phase authority | Stop and record the specific gate. |

## Mechanical stop

Record a chain stop with:

`python3 scripts/chain_state.py stop --status stopped --reason "<specific reason>"`

Use `completed` only when the authorized phase or product completion gate is proven. Use `blocked` only for a true impasse under the platform's repeated-blocker rule.
