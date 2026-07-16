# Session orchestration workflow

## Outcome contract

`$session-orchestrate` turns the current product plan into a bounded sequence of session goals. It does not own product intent and it does not persist a second roadmap. Every task rebuilds a compact program view from current owner documents and live evidence, then executes one goal.

The two planning levels are different:

- **Program map:** the ordered remaining goals needed to satisfy the product plan and its exit gates.
- **Session goal:** one independently verifiable slice of that map, including the actions to perform now.

The program map is derived and disposable. Product-plan and implementation-status owners remain authoritative.

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

1. Run `python3 scripts/entry.py` before broad retrieval. Its JSON includes checkpoint eligibility, chain consistency, owner candidates, plan/status candidates, recent commits, project-local skills, and bounded recent project-session hints.
2. Call `get_goal`. Preserve a matching unfinished goal. A different unfinished goal is a conflict; do not replace it.
3. Read the narrowest routing owner from `project_inventory.owner_routing_candidates`. Follow its declared product-plan or roadmap route. Filename candidates are fallback discovery only.
4. Read only the plan sections needed to identify the current phase, ordered deliverables, dependencies, and exit gate.
5. Read the implementation/status owner when one exists. Verify disputed or missing status against live repository or runtime evidence.
6. Use recent project sessions only to learn recurring actions, known friction, or relevant skills. Inspect at most three matching sessions and never use them as completion or authorization evidence.

### Checkpoint decisions

| Entry mode | Meaning | Required action |
|---|---|---|
| `resume-exact-goal` | Mechanically fresh and chain-consistent candidate | Confirm the current owner plan still permits the exact goal and its constraints, then reuse/create only that exact goal. |
| `review-checkpoint` | Stale, malformed, divergent, completed, or conflicting state | Never activate the saved objective. Reconcile against current owner state and select through the new-goal lane. |
| `choose-next-goal` | No activatable saved goal | Build the program map from current owner state. |

Freshness is necessary, not sufficient. A product-plan change, newly completed work, a different active goal, or a new authority gate can still invalidate an otherwise fresh checkpoint.

If no product/roadmap owner exists, use an explicit current user objective as the temporary completion contract. If neither exists, stop for product-owner direction; do not fabricate a roadmap from repository shape or old sessions.

## Build the program map

Before selecting a goal, state a compact map containing:

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

Use the current task plan surface for the program map when available. Do not create `PROGRAM.md`, `ROADMAP.md`, or another durable plan unless the repository explicitly declares that surface as the implementation-plan owner. When an implementation owner exists, update it after verified progress instead of creating a parallel ledger.

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
2. Initialize the chain with a hop budget equal to the number of session goals in the current authorized phase, capped at 12: `python3 scripts/chain_state.py init --max-hops <count> --phase-boundary "<boundary>"`. A successor claims its pending nonce instead.
3. Save the exact goal hash with `python3 scripts/chain_state.py set-goal --objective-file <goal-file>`.
4. Load only the owner slice and skills needed for the first action. Past skill usage is a routing hint, not a requirement to reload every prior skill.
5. Make the smallest concrete implementation or verification attempt in the next tool action.
6. Continue until the stop conditions pass or a real blocker/authority boundary is reached.

## Closeout lane

### Completed goal

1. Verify every stop condition with current evidence.
2. Update the owning implementation/status surface if the repository declares one.
3. Call `update_goal complete`.
4. Run `python3 scripts/checkpoint.py --goal-file <goal-file> --resume-policy reference-only --next-action "<next program-map decision>" --verification "<proof summary>"`.
5. Rebuild the compact program map. Stop when the product/phase exit gate is complete, the next work crosses an authority boundary, or the chain reaches `max_hops`.
6. Otherwise run `python3 scripts/chain_state.py prepare-handoff --kind next-goal`.

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
| Old or future-dated checkpoint | Review only; never activate it. |
| Wrong root, branch, missing commit, or invalid route | Review only. |
| Fresh checkpoint but product plan changed | Reconcile; use the normal new-goal lane if the exact goal is no longer current. |
| Matching checkpoint but chain goal hash differs | Review conflict; do not create a goal. |
| Completed chain or completed active goal | Select the next current goal; never reopen it. |
| Different active goal | Stop for conflict resolution. |
| Product plan exists but status is unclear | Verify live evidence and mark unknown, not complete. |
| No product plan and no explicit product objective | Stop for product-owner direction. |
| Past sessions disagree with current owner docs | Current owner docs and live evidence win. |
| Remaining work crosses spend, deployment, auth, destructive, secret, external-send, or phase authority | Stop and record the specific gate. |

## Mechanical stop

Record a chain stop with:

`python3 scripts/chain_state.py stop --status stopped --reason "<specific reason>"`

Use `completed` only when the authorized phase or product completion gate is proven. Use `blocked` only for a true impasse under the platform's repeated-blocker rule.
