# v4 Multi-Actor — Flow Control Addendum

**Filed:** 2026-04-26
**Addendum to:** `records/2026-04-26-v4-phase-1-hidden-scribe-spec.md`
**Source question:** Steve, 2026-04-26 — *"should the script also (in v4) dictate the flow of the conversation? e.g. round robin, chaos, etc"*

---

## Why this is a separate record

Filed as a discrete addendum (not a Phase 1 spec update) because flow control is a **Phase 2-3 design dimension**, not Phase 1. Phase 1 is the structural split (active actor vs hidden scribe) — single active actor still, so no flow question exists yet. This record captures the design space so it isn't lost between Phase 1 ship and Phase 2 design.

**Phase 1 PR (#18) is unchanged by this record. No scope creep.**

---

## The design dimension

Once Phase 2 lands and multiple named actors can be in the room simultaneously, a new question arises: **when the user asks something, in what order do the actors respond?**

This is distinct from the panel-vs-independent addressing modes already specified. Addressing modes are about **information flow** (does each actor see the others' context?). Flow control is about **turn-taking** (who speaks when, in what order, with what trigger).

The two axes are orthogonal:

| | Address-by-name flow | Round-robin flow | Personality-derived flow | etc. |
|---|---|---|---|---|
| **Panel mode** (shared context) | applicable | applicable | applicable | applicable |
| **Independent mode** (parallel subagents) | N/A — by definition parallel, no flow | N/A | N/A | N/A |

Flow control only matters in panel mode.

---

## Flow types worth considering

### 1. Address-by-name (proposed default for Phase 2)

Actors only speak when the user names them. Conservative, predictable, no overlap. No new actor speaks unless invited.

> User: *"Sherlock, what do you think?"* → only Sherlock responds.
> User: *"What do you all think?"* → all currently-active actors respond, in declaration order.

**Why this is the right Phase 2 default:** simplest possible behavior. No personality reasoning, no priority ranking, no implicit speak-up. Users can be explicit about who they want to hear from. Failure mode is verbose ("everyone responds when I say 'all'") but predictable.

### 2. Round robin

Actors take turns in a fixed order, regardless of personality or topic. Fair, structured.

> Use cases: brainstorming, retrospectives, jury-style deliberation, equal airtime moderation.

Configurable order (in declaration order, in alphabetical order, in custom order via context.md).

### 3. Chaos / personality-derived (proposed default for Phase 3 panel mode)

The interesting one. **Use existing personality trait sliders to drive flow naturally.** No new config layer, no new spec extension — the existing trait model already encodes this.

Mapping (proposed):
- High `confidence` + high `impatience` + low `deference` → speaks first
- High `bluntness` → cuts in / interrupts
- High `deference` + high `patience` → waits for invitation
- High `empathy` + high `active_listening` → defers to whoever needs the floor most
- High `humor` + high `energy` → speaks early to lighten tone, but yields on serious topics

Net effect: a session with Bob (warm, patient, deferential), Sherlock (confident, methodical), and Oscar (bold, theatrical) produces a natural rhythm — Sherlock and Oscar speak up first, Bob comes in with synthesis. **No flow config required.** This is the elegant case for personality-driven multi-actor sessions.

**Edge case to handle:** all actors with high deference + high patience → nobody speaks. Mitigation: hidden scribe surfaces a fallback prompt to the highest-confidence actor as the default speaker.

### 4. Moderator-led

One designated actor (or the user) gates who speaks next. Useful for: structured problem-solving where a primary advisor (e.g., Dr. Quinn the psychologist-style listener) decides when other voices add value.

> User: *"Dr. Quinn, lead this session. Bring in Sherlock or Oscar when their input would help."*

Moderator role is set via natural language. No new field required — handled by an active actor with appropriate prompt context.

### 5. Reactive

Actors stay silent unless they have specific value to add — driven by topic relevance match against the actor's `domain_fluency` or `hard_skills` or archetype.

> User: *"What's the right approach to this database migration?"*
> Sherlock (high analytical_thinking, ANALYST archetype) → speaks.
> Bob (high warmth, no domain_fluency match) → stays silent.
> Oscar (high creativity, low analytical_thinking) → optional contribution.

Requires the active-actor layer to evaluate topic relevance per actor. More expensive (more reasoning per turn) but more appropriate output.

---

## Phase mapping

- **Phase 2 (multi-actor spawn) — default: address-by-name.** Most conservative. Users get multi-actor without needing to learn flow concepts. Override via natural language: *"talk among yourselves"* could trigger ad-hoc panel mode.
- **Phase 3 (panel vs independent modes) — default: personality-derived flow.** When the user explicitly invokes panel mode, flow comes from trait sliders. Round-robin / moderator-led / reactive are explicit user-facing overrides.
- **Phase 4 (hot-swap + headers + reload) — explicit flow verbs.** *"set flow to round-robin"* / *"set flow to chaos"* — captured as a session-level setting, mid-session adjustable. Stored in context.md or session-scoped state.
- **Phase 5 (`list actors` expansion) — surface current flow.** `list actors` output includes the active flow mode if non-default.

---

## Where flow configuration lives (proposed)

Three options for storing the active flow mode:

1. **`context.md` field** — `flow: address-by-name` / `flow: round-robin` / `flow: personality` / `flow: moderator(name)` etc. Persists across sessions. Simple. Conflicts if user wants different flows for different multi-actor configurations.

2. **Session-only / verb-driven** — set via *"set flow to X"*, lasts only this session. No persistence. User reconfigures each time. More flexible but repetitive.

3. **Per-actor-set** — flow is tied to which combination of actors is in the room. e.g., "when Bob + Sherlock are both active, use round-robin; when just Bob, address-by-name." Most powerful but complex to express in markdown.

**Recommendation: start with (1) `context.md` field as v4 default, allow (2) verb override mid-session.** Option (3) is over-engineered for v4; can revisit later if real usage demands it.

---

## Personality-derived flow — open questions

These need empirical testing in Phase 3 before locking in:

1. **Does the model reliably reproduce trait-driven turn order?** Or does it drift toward "everyone speaks every turn" regardless of trait sliders?
2. **What's the right algorithm for combining traits into speak-priority?** Simple weighted sum? Threshold + tiebreaker? Should the algorithm be in protocol or implicit in model behavior?
3. **How does the user override personality-derived flow when they want a specific actor first?** Address-by-name should always take precedence — naming an actor explicitly bypasses flow logic.
4. **Does the hidden scribe enforce flow, or does it emerge from active-actor coordination?** Cleanest answer: emerges from active-actor reasoning given prompt context. Scribe stays out of flow control entirely.

---

## What this does NOT change

- Phase 1 PR (#18) — unchanged. Phase 1 is structural; flow is Phase 2+.
- Active-actor / hidden-scribe split — unchanged. Flow is an active-actor concern; scribe is unaffected.
- Personality file format — unchanged. Existing trait sliders are sufficient inputs for personality-derived flow; no new fields needed.
- Independent mode (Phase 3 subagents) — unchanged. Flow doesn't apply.

---

## Definition of done for flow control work

By end of Phase 4:
- Default flow in Phase 2 (address-by-name) shipped and working
- Default flow in Phase 3 panel mode (personality-derived) shipped, behavior empirically validated (real conversations with Bob + Sherlock + Oscar produce the expected rhythm)
- `flow:` field in context.md spec, three explicit overrides supported (round-robin, chaos, moderator-led)
- Mid-session `set flow to X` verb in CORTEX.md
- README + docs/PERSONALITIES.md updated with flow-control section

---

*Filed by Bob to capture the design dimension before Phase 2 work begins. Steve raised the question; this is the canonical answer for now. Revisit during Phase 2 design with empirical testing of personality-derived flow.*
