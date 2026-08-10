---
name: create-design-md
description: >-
  Create, refine, or audit an application's canonical DESIGN.md covering product
  design philosophy, user experience philosophy, journeys, information
  architecture, visual theme, interaction, motion, accessibility, trust, and
  validation. Use when starting an app, finalizing its theme or UX direction,
  reconciling conflicting design decisions, or turning scattered design notes
  into one build-ready owner document. Ask targeted user questions only when a
  material decision is unresolved or contradictory and cannot be established
  from product evidence.
---

# Create DESIGN.md

> **Self-validate after edits.** Run the local `create-skill` audit after changing this skill.

Create one governing design owner that helps future agents make coherent product,
UX, and visual decisions without rediscovering intent or treating a theme as a
palette.

## Outcome contract

The resulting `DESIGN.md` must:

- state one product-specific design thesis and one experience thesis;
- translate those theses into journeys, interaction rules, and a visual system;
- distinguish confirmed decisions from reasoned inferences;
- resolve material contradictions with the user before finalizing;
- define accessibility, trust, responsive, state, and validation requirements;
- provide a compact build handoff for critical journeys without prescribing the
  implementation;
- be decisive enough to reject an attractive but philosophically wrong screen;
- remain concise enough to be loaded before design or implementation work.

Do not create a sibling design owner when one already exists. Refine the canonical
file in place and remove displaced or contradictory guidance in the same pass.

## Workflow

### 1. Find the owner and evidence

Read the narrowest applicable repository instructions first. Locate an existing
`DESIGN.md`, product goal, PRD, current roadmap, design-system source, representative
screens or captures, and validation contract. Stop retrieval when the product
promise, audience, primary journey, and controlling design owner are clear.

Evidence priority:

1. explicit user decisions and current product owner documents;
2. shipped or actively validated product behavior;
3. current platform-owner guidance such as Apple HIG or Material guidance;
4. award-winning products as bounded inspiration, never as templates;
5. trends, galleries, and competitors only when the user requests them.

When platform guidance or award status could have changed, verify it from current
official sources. Cite research in a short evidence-boundary section; do not turn
the design owner into a literature review.

### 2. Build the decision map

Read [references/design-decisions.md](references/design-decisions.md). For every
applicable decision area, assign exactly one status:

- `confirmed` — explicitly owned by the user or canonical product source;
- `inferred` — supported by product evidence and safe to derive;
- `unresolved` — materially changes the experience and lacks enough evidence;
- `contradictory` — credible owner sources or shipped behavior disagree;
- `irrelevant` — does not apply to this product or stage.

Record the source and one-sentence rationale for confirmed and inferred decisions.
Do not dump this internal map as a generic questionnaire. Convert it into a
curated set of decisions that genuinely require the user's judgment.

### 3. Run the targeted-question gate

Before asking anything, complete a due-diligence pass:

- inspect the canonical product, requirements, roadmap, design, and validation
  owners that could answer the decision;
- inspect representative current screens, captures, design tokens, and shipped
  behavior when they exist;
- search for the decision using product language and likely synonyms;
- verify current official platform guidance when the question depends on a
  platform convention or standard;
- distinguish an absent answer from an answer the agent merely dislikes;
- identify the exact downstream decisions that remain blocked.

Do not ask the user to restate discoverable product facts or choose between options
that evidence has already eliminated.

Ask the user only when all are true:

1. the decision is `unresolved` or `contradictory`;
2. different answers would materially change philosophy, journey, trust boundary,
   information architecture, or theme;
3. the answer cannot be discovered from the repository or current product;
4. choosing a default would risk diverging from the user's intent.

Ask every question required to resolve the material design space. There is no fixed
numerical cap. Order questions by dependency and group related decisions so the
user can answer coherently without unnecessary back-and-forth. When upstream
answers may eliminate downstream questions, ask the upstream set first, then run
the decision map again before asking the remainder.

Before the question set, briefly state what evidence was inspected, what it already
established, and why the remaining choices require user judgment. Each question
must:

- name the concrete decision and why it matters now;
- offer two or three genuinely different directions;
- recommend one direction when evidence supports it;
- explain the experiential tradeoff in plain language;
- avoid implementation jargon and premature token choices.

Every question must earn its place. Remove any question whose answer would not
change the philosophy, experience, trust boundary, information architecture,
theme, or acceptance criteria.

Pause finalization until material questions are answered. Do not ask about color
hex values, corner radii, or animation curves before the emotional objective,
experience thesis, and primary journey are settled.

Good question:

> Should the system's recommendation remain a proposal the person reviews, or may
> it apply automatically with undo? I recommend review before applying when the
> decision changes persisted or shared state because it preserves informed agency.
> This changes confirmation, explanation, notification, and recovery behavior.

Weak question:

> What colors and fonts do you like?

If no material uncertainty remains, proceed without asking for confirmation.

### 4. Derive philosophy before theme

Write the design thesis from audience, primary job, environment, frequency, risk,
emotional objective, and brand promise. Write the experience thesis as the human
change the journey creates, not a list of screens.

Then define:

- governing principles and explicit anti-principles;
- the primary journey and consequential decision points;
- AI or automation authority, explanation, approval, correction, and recovery;
- information hierarchy and disclosure model;
- intentional positions on expressive/restrained, warm/clinical,
  editorial/utilitarian, airy/dense, playful/serious, and familiar/novel axes;
- one or two signature moves that express the product promise;
- visual theme behavior across type, color, geometry, materials, imagery, motion,
  haptics, and sound.

Theme choices must follow the philosophy. A palette swap, generic glass treatment,
or copied design system is not a design direction.

### 5. Write or refine the canonical DESIGN.md

Use the output structure in
[references/design-decisions.md](references/design-decisions.md). Include only
applicable sections, but never omit a material decision because it is difficult.

When refining an existing file:

- preserve confirmed product identity and useful unique detail;
- replace vague adjectives with decision rules and observable acceptance signals;
- reconcile contradictions instead of appending another opinion;
- separate philosophy from visual tokens and component specifications;
- keep platform adaptations conceptually consistent without forcing identical UI;
- name intentionally deferred decisions and their trigger for reconsideration.

Do not implement screens unless the user also asks for implementation.

### 6. Create the build handoff

For each critical journey or consequential screen, add the smallest handoff needed
to preserve design intent through implementation. Use the field map in
[references/design-decisions.md](references/design-decisions.md) and cover:

- entry conditions, a unique arrival signal, the primary action, and its semantic
  postcondition;
- applicable loading, empty, partial, ready, error, permission, correction,
  recovery, and return states;
- navigation, interruption, restoration, persistent regions, accessibility, and
  responsive or platform invariants;
- asynchronous content that may change hierarchy or control position;
- dependencies by owning capability or document, plus the evidence required for
  acceptance.

Keep this contract product- and outcome-oriented. Link to technical, component,
token, API, platform-capability, fixture, and validation owners instead of copying
them. Do not invent framework types, commands, test data, or architecture merely
to make the design appear build-ready. Mark missing dependencies or intentionally
deferred behavior explicitly.

### 7. Validate the owner

Before completion, verify:

- every required decision area is answered, explicitly deferred, or irrelevant;
- no unresolved material contradiction is hidden by polished prose;
- the theme is traceable to the design and experience theses;
- every journey has empty, loading, partial, success, error, offline, permission,
  correction, and recovery behavior where applicable;
- accessibility is structural and voice, color, motion, pointer, or vision is never
  the only path to meaning or control;
- AI-generated interpretation is distinguishable, explainable, correctable, and
  reversible at consequential moments;
- new-screen acceptance criteria can reject philosophical, UX, and visual drift;
- every critical journey has a handoff that identifies its semantic outcome,
  relevant states, recovery, dependencies, and acceptance evidence;
- the handoff does not duplicate or silently contradict implementation and
  validation owners;
- the file is the sole owner and links to mockups or tokens rather than duplicating
  them.

Run repository documentation validation when available. Report validation debt
separately from the design result; never weaken a rule to create a green check.

### 8. Emit design admission when orchestrated

When a receipt-backed `session-orchestrate` lifecycle requests design admission,
the design owner emits the `orchestration-receipt.v1` contract defined by
`session-orchestrate`. Use `stageKind: "design"` and count applicable positive and
negative journey/state scenarios from the build handoff. `pass` means the current
design fingerprint is decision-complete and the named product-source fingerprint
is the one implementation will receive. Unresolved decisions remain blockers;
mockup presence alone is not a pass. The canonical `DESIGN.md` remains the design
truth and orchestration stores only the compact receipt.

## Completion report

Tell the user:

- where the canonical `DESIGN.md` lives;
- the final design thesis and experience thesis;
- which material decisions were resolved or intentionally deferred;
- which critical journeys received build handoffs and any unresolved dependency;
- what existing guidance was replaced;
- what validation ran and any remaining evidence gap.

Do not claim the application follows the philosophy without comparing live or
captured product evidence to the document.
