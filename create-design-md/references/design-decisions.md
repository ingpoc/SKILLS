# DESIGN.md Decision Reference

Use this reference as a coverage map, not a questionnaire. Derive answers from
evidence first and ask the user only through the targeted-question gate in
`SKILL.md`.

## Decision map

### 1. Product identity

- What human problem does the application solve?
- For whom, in what setting, and how often?
- What change should the person experience after using it?
- What is the product explicitly not?
- What must feel uniquely true of this product rather than its category?
- What business, safety, privacy, or platform constraints shape the experience?

Required output: one-sentence product promise, design thesis, non-goals, and the
first-impression objective.

### 2. Experience philosophy

- What is the user's primary job?
- What emotional state do they enter with and leave with?
- What is the shortest honest path to value?
- Which decisions are frequent, consequential, reversible, or collaborative?
- Where must the system explain, confirm, wait, or allow correction?
- What should technology automate, and what must remain human-controlled?
- What behaviors must never be optimized for engagement?

Required output: one-sentence experience thesis, human journey arc, governing
principles, anti-principles, and agency rules.

### 3. Audience and context

- Abilities, experience levels, cultures, languages, and age considerations.
- Physical environment, attention level, connectivity, privacy, and device posture.
- Occasional high-consideration use versus frequent operational use.
- Content sensitivity, emotional risk, and consequences of mistakes.
- Assistive technology and alternative input/output needs.

Do not define audiences through stereotypes. Describe goals, abilities, context,
and behavior.

### 4. Critical journeys

For each critical journey define:

- entry condition and user intent;
- minimum information needed to begin;
- primary content and action at each meaningful step;
- system feedback and continuity between steps;
- consequential boundary and confirmation;
- completion signal and human outcome;
- cancellation, correction, retry, and safe exit;
- return path and preserved state.

Prioritize the first-value journey, core repeat journey, trust-sensitive journey,
and recovery journey.

### 5. Information architecture and navigation

- What are the primary product objects and their relationships?
- Which destinations are persistent, contextual, on demand, or interruptive?
- What deserves a top-level destination versus a state within another object?
- What does each screen help the user accomplish now?
- What must remain stable across platforms?
- Where should search, filtering, history, settings, and account controls live?
- How are deep links, back behavior, restoration, and interrupted flows handled?

Navigation is not a feature inventory. Separate destinations, actions, system state,
and account controls.

### 6. Disclosure and content hierarchy

- What is the single dominant content element?
- What is the single primary action?
- What must always be visible for comprehension or safety?
- What becomes relevant only in the current state?
- What can be revealed on demand?
- What duplicated, internal, or unactionable information should be removed?
- What must appear beside the action it affects?

Define `persistent`, `contextual`, `on demand`, `interruptive`, and `remove` rules.

### 7. AI and automation trust

When AI or automation exists, define:

- capability and explicit limits;
- what is user-provided fact versus system interpretation;
- uncertainty and provenance language;
- when the system may suggest, draft, prepare, or act;
- when explicit approval is mandatory;
- preview, edit, correct, remove, retry, undo, and appeal paths;
- audience and sharing scope before consequential action;
- what happens when the model, network, or tool fails;
- retention, privacy, moderation, and audit expectations.

Never let AI aesthetics substitute for understandable authority and control.

### 8. Visual identity and theme

Define intentional positions on these axes:

- expressive or restrained;
- warm or clinical;
- editorial or utilitarian;
- airy or dense;
- playful or serious;
- familiar or novel.

Then derive:

- typography roles, hierarchy, scaling, and reading width;
- color behavior, semantic roles, contrast, and light/dark appearance;
- spacing rhythm and density;
- geometry, corner behavior, borders, depth, and materials;
- imagery, illustration, photography, iconography, and data visualization;
- one or two signature moves and where they are allowed;
- anti-homogenization rules and prohibited category clichés.

Specify behavior before tokens. Hex values and component constants may follow once
the direction is stable.

### 9. Interaction, motion, haptics, and sound

- What direct-manipulation and platform conventions should remain familiar?
- How does each action acknowledge input and communicate state change?
- Which transitions preserve spatial or conceptual continuity?
- Which moments deserve emotional emphasis?
- What is the reduced-motion equivalent?
- What information conveyed through sound or haptics also has visual or textual
  expression?
- What latency needs progress, optimistic feedback, cancellation, or background
  completion?

Motion must explain, confirm, orient, or add rare meaningful delight. Otherwise,
remove it.

### 10. Content design

- Product voice, vocabulary, reading level, and emotional register.
- Naming rules for product objects and actions.
- How instructions, privacy, uncertainty, errors, and confirmations are phrased.
- Prohibited manipulative, technical, judgmental, or generic AI language.
- Localization, text expansion, pluralization, dates, names, and cultural nuance.
- Content ownership when generated text is editable or shared.

### 11. Accessibility and inclusion

Define acceptance for:

- semantic structure, labels, focus order, and screen-reader operation;
- text scaling and reflow without clipped decisions or disclosures;
- sufficient contrast and non-color state cues;
- touch targets, keyboard, switch, pointer, and voice alternatives as applicable;
- reduced motion, reduced transparency, increased contrast, and sensory controls;
- captions, transcripts, audio description, and alternative input;
- plain language, error identification, timeouts, and cognitive load;
- inclusive examples and content without persona stereotypes.

Accessibility is a design input and acceptance gate, not a later compliance pass.

### 12. Responsive and cross-platform behavior

- Device priorities and supported sizes, orientations, windows, and input methods.
- What hierarchy and emotional sequence remain invariant?
- What may reflow, combine, split, or disclose at larger sizes?
- What should use native platform conventions rather than forced parity?
- How do multitasking, keyboard, hover, drag, context menus, and window restoration
  affect the experience?

Preserve concepts and outcomes across platforms, not identical layouts.

### 13. State system

For every important object or journey, define applicable states:

- initial and empty;
- loading and progressive loading;
- partial or stale;
- ready and active;
- success and completion;
- offline and reconnecting;
- permission required or denied;
- blocked, expired, withdrawn, or unavailable;
- recoverable and unrecoverable error;
- correction, undo, deletion, and return.

Empty states explain value and one next action. Error states preserve completed
work and provide an honest recovery path.

### 14. Privacy, safety, and dignity

- What data is collected, inferred, stored, shared, and deleted?
- When is permission requested and what benefit is explained first?
- Who can see each type of content, and how can that change?
- Which actions expose identity, contact others, publish, purchase, delete, or cause
  social consequence?
- What blocking, reporting, moderation, withdrawal, and account-deletion paths exist?
- How are declined, unmatched, empty, and failure states phrased without shame?

Consequential control belongs beside the consequence.

### 15. Validation and governance

Define independent acceptance signals for:

- philosophical fit: the screen advances the human outcome and follows principles;
- UX fit: the journey is understandable, controllable, recoverable, and complete;
- visual fit: hierarchy, craft, theme, responsiveness, and distinctiveness;
- accessibility: representative end-to-end assistive-technology proof;
- trust: explanations, scope, approval, correction, and undo work as promised;
- parity: live capture compared with the canonical reference when applicable.

Name the owner for philosophy, tokens, components, mockups, and validation. Avoid
duplicating any of them inside `DESIGN.md` when a stable owner already exists.

### 16. Build handoff contract

For each critical journey or consequential screen, define a compact contract that
lets implementation preserve the intended experience without turning `DESIGN.md`
into a technical specification:

| Field | Required definition |
| --- | --- |
| Identity | Stable product-language journey or screen name |
| Entry | User intent, prerequisite state, and initiating action or route |
| Arrival | Unique visible or semantic signal that proves the intended state |
| Primary action | The action, why the person takes it, and any consequential boundary |
| Postcondition | Observable human outcome or persisted state change |
| State coverage | Applicable loading, empty, partial, ready, offline, permission, success, error, correction, recovery, deletion, and return states |
| Navigation | Back, cancel, interruption, restoration, and preserved progress |
| Layout | Persistent versus scrolling regions, safe-area or viewport obligations, and full-content behavior |
| Accessibility | Reading order, scalable content, alternative input or output, and stable semantic naming needs |
| Async behavior | Content that may arrive late, move hierarchy, or alter control availability |
| Platform adaptation | Outcome and hierarchy invariants plus allowed native differences |
| Dependencies | Links to the owners for capabilities, data, components, tokens, permissions, privacy, and validation |
| Acceptance | Semantic, state, accessibility, responsive, trust, and visual evidence required |

Include only fields that materially protect the journey. Describe product outcomes
and constraints, not framework types, shell commands, fixture values, coordinates,
or architecture guesses. Link to stable owners rather than duplicating their
contracts. Mark a missing dependency as unresolved or deferred with its trigger;
do not conceal it behind polished mockups.

## Recommended DESIGN.md structure

1. Control owner and evidence boundary
2. Product promise and non-goals
3. Governing design philosophy
4. Experience philosophy and journey arc
5. Audience, context, and trust posture
6. Product objects, information architecture, and navigation
7. Disclosure and interaction principles
8. AI or automation authority and recovery
9. Visual identity and theme
10. Typography, color, spacing, geometry, imagery, and iconography
11. Motion, haptics, and sound
12. Content voice and terminology
13. Accessibility and inclusion
14. Responsive and platform adaptation
15. State, privacy, safety, and dignity rules
16. Signature experiences and representative screen hierarchy
17. Build handoff contracts for critical journeys
18. New-screen decision filter and acceptance criteria
19. Explicit deferrals and reconsideration triggers
20. Research sources, if used

This is a coverage structure, not a demand for 20 long sections. Merge adjacent
sections when clarity improves, omit irrelevant ones, and link to detailed token
or component owners instead of copying them.

## Targeted-question patterns

There is no fixed question limit. Ask all material questions that remain after the
due-diligence pass, but never expose this reference as a form. Group questions by
decision dependency and rerun the map after upstream answers because they may
resolve or invalidate later questions.

Ask in dependency order:

1. product promise or audience conflict;
2. experience model or consequential authority;
3. primary journey or information architecture;
4. emotional objective and visual axes;
5. signature theme choices;
6. lower-level tokens only when they cannot be derived later.

Each question should use this form:

> **Decision:** [what must be decided]
>
> **Why now:** [which downstream experience changes]
>
> **Recommended direction:** [choice and evidence]
>
> **Alternatives:** [two or three concise options with tradeoffs]

Introduce the set with a compact diligence receipt:

> **Established from evidence:** [decisions already supported by owner sources]
>
> **Still requires your judgment:** [why the remaining choices cannot be inferred]

Do not ask the user to approve decisions already explicit in the canonical product
owner, recoverable from current product evidence, or settled by an applicable
platform constraint. Surface the evidence and proceed.
