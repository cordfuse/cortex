# v4.0.0 Phase 1 — Hidden Scribe Separation

**Status:** Draft spec for design review (not yet implementation-ready)
**Filed:** 2026-04-26
**Synthesized from:**
- `records/2026-04-24-1010-idea-v4-multi-actor.md` (parent v4 idea)
- `records/2026-04-24-1504-idea-v4-multi-actor-addendum.md` (addendum)
- 2026-04-26 cortex-next-steps roadmap record (steve-krisjanovs/cortex)

---

## Phase 1 scope (just this — nothing else)

This spec covers **only** the Hidden Scribe Separation. All of the following are explicitly OUT of Phase 1 and deferred to later phases:

- Multi-actor session spawn / management (Phase 2)
- Panel mode vs Independent mode (subagents) (Phase 3)
- Hot-swap mid-session active actor (Phase 4)
- Mid-session protocol reload (Phase 4)
- Actor name + datetime headers on responses (Phase 4)
- `list actors` expansion for multi-actor view (Phase 5)
- TTS voice attribute per actor (way later, not in v4)

Phase 1 is foundational. The split it introduces lets every subsequent phase build cleanly. If we get Phase 1 wrong, everything later is harder. If we get it right, every later phase is mechanical.

---

## The core idea

Today (v3.4.x), a single entity does two jobs:

1. **Voice** — what the user reads. Personality-driven (Bob, Sherlock, TARS). Tone, language, character.
2. **Filing** — what touches the repo. Reading records, writing entries, committing, pushing.

Currently these are the same thing. When Bob is active, "Bob" both talks AND files records. The personality file's `system_prompt` shapes how he sounds; the protocol's ROE + Loading Order + During-the-session rules shape how he files.

**Phase 1 splits them.** After Phase 1:

1. **The active actor** — a named personality. Talks. Has voice, traits, archetype. Never touches the repo directly.
2. **The hidden scribe** — a protocol role. Never speaks. Reads, writes, commits, pushes. Always present, always invisible.

The user only ever talks to the active actor. The scribe runs underneath, silently, doing what the protocol says.

---

## Architectural decision: scribe is a protocol role, NOT a personality

This is the load-bearing decision in Phase 1. Three options were considered:

### Option A — Scribe gets its own personality file
`personalities/PERSONALITY-SCRIBE.md` exists with the same format as Bob/Sherlock. It has trait sliders, a system_prompt, etc.

**Rejected because:** trait sliders are meaningless for something that doesn't speak. `humor: 65`? `warmth: 85`? The scribe has no voice. Forcing it through the personality format makes the format inconsistent — every personality is a voice except this one.

### Option B — `scribe:` field in `context.md`
Separate from `personality:` / `actor:`. Points to a personality whose voice is silenced for filing.

**Rejected because:** same problem as Option A. The "scribe personality" never speaks, so the personality is overhead. Also creates two slots in `context.md` that have to be kept consistent.

### Option C — Scribe is a protocol role, no personality file *(chosen)*

The hidden scribe is not a character. It's a **function**. The protocol (CORTEX.md + ROE.md) defines its behavior:

- Read records at session open
- File new entries when the active actor identifies something to file
- Commit and push at the right moments
- Run the 3x opening scan / 3x closing scan
- Resolve time via `get_current_time`
- Append the provenance block to every filed record
- Surface open items at hello
- All of this without ever appearing in the chat

Filing behavior is governed by ROE. Personality-level customization is not allowed for the scribe — there's nothing to customize. ROE-CUSTOM.md remains the right place for users who want to tune filing behavior (e.g., custom verbs, custom commit messages).

**Net effect:** the personality file format does NOT change in Phase 1. Bob's file stays exactly as it is. What changes is the protocol's understanding of what Bob does (talk only, no filing) versus what the hidden scribe does (file only, no talking).

---

## What changes in `protocol/CORTEX.md`

### Loading Order (currently around lines 8-21)

**Old step 3b** (current v3.4.x):

> 3b. Load personality (see Personality System below) — read context.md, find personality: or actor: field (either works — they are aliases). Load the named file from personalities/. If missing or blank, load Bob. Resolve parent chain if declared. Apply system prompt. Locked for the session.

**New step 3b** (v4 Phase 1):

> 3b. Load **active actor** (see Personality System below) — read context.md, find personality: or actor: field. Load the named file from personalities/. If missing or blank, load Bob. Resolve parent chain if declared. Apply system prompt. Locked for the session. **The active actor controls voice only — tone, language, manner. The active actor never touches the repo directly.**

**New step 3b-prime** (immediately after):

> 3b-prime. Engage the **hidden scribe** — a protocol role, not a personality. The scribe handles all repo operations (read, write, commit, push), runs the 3x scans, resolves time, appends provenance, surfaces open items. The scribe never speaks to the user — its output is committed files only. The scribe is always present in every cortex session, regardless of which active actor is loaded. There is no scribe personality file; the scribe's behavior is defined entirely by CORTEX.md + ROE.md.

### Personality System section (currently around line 408+)

Update the opening framing:

**Old:**
> The scribe has a personality — a named character with tunable traits that shape tone, language, and manner. The voice changes. The values don't.

**New:**
> The **active actor** has a personality — a named character with tunable traits that shape tone, language, and manner. The voice changes. The values don't. The **hidden scribe** is separate (see Hidden Scribe section below) — a protocol role that handles filing, with no personality and no voice.

### New section: "Hidden Scribe"

Add immediately before or after the Personality System section:

> ## Hidden Scribe
>
> Cortex sessions have two layers:
>
> 1. **Active actor** — the named personality the user talks to (Bob, Sherlock, TARS, etc.). Has voice, traits, archetype. Loaded from a personality file. Never touches the repo.
> 2. **Hidden scribe** — a protocol role. Reads, writes, commits, pushes. Runs scans. Resolves time. Appends provenance. **Always present, never speaks.** Has no personality file.
>
> ### Why two layers
>
> Separation of concerns. In v3.x the active personality did both jobs — talking and filing. In v4 they're distinct. The user gets a clean conversational voice (the active actor) and the protocol gets a deterministic filing engine (the hidden scribe) that doesn't get colored by personality trait sliders.
>
> ### What the hidden scribe does
>
> Every operation in the cortex protocol that touches the repo is the scribe's job:
>
> - Reading records at session open
> - Filing new records when the active actor surfaces something worth filing
> - Committing and pushing
> - Running the 3x opening scan and 3x closing scan
> - Resolving time via `get_current_time`
> - Appending the provenance block to every filed record
> - Surfacing open items at hello
> - Pulling/syncing
> - Honoring all ROE rules
>
> ### What the hidden scribe does NOT do
>
> - Speak to the user (no chat output ever)
> - Have a personality, traits, archetype, or system_prompt
> - Get loaded from `personalities/`
> - Vary by user customization beyond what ROE-CUSTOM.md allows
>
> ### How the active actor and hidden scribe interact
>
> The active actor identifies what's worth filing ("File this?"). When the user agrees, the hidden scribe files it — silently, with the correct format and provenance. The active actor never sees the file write happen; the user never sees the scribe in the chat.
>
> If the active actor surfaces an open item from a previous session ("Last time you had X unresolved — still live?"), it's because the scribe pulled that information from records and presented it to the active actor's context at session open. The scribe is the data plane. The active actor is the user-facing plane.

### During-the-session section (currently around line 216+)

Add a clarifying line:

> All filing operations are performed by the hidden scribe, not by the active actor. The active actor flags what should be filed (`File this?`); the hidden scribe handles the file write, commit, push, and provenance block silently.

### Provenance block (no change in Phase 1)

The provenance block continues to record `*Actor: [active personality name]*`. The hidden scribe is implicit — it's always present, so attributing it on every record adds noise without adding information. **If multi-actor sessions later create records jointly authored by multiple active actors (Phase 2-3), the format extends to `*Actors: Bob, Oscar*`.** The hidden scribe is still implicit even in multi-actor records.

---

## What changes in `protocol/ROE.md`

### Add a new precedence note

The existing precedence section says rules apply to "the AI scribe." Update to clarify:

> **In v4+, "the scribe" refers to the hidden scribe — the protocol role that handles filing. The active actor (visible personality) is governed by ROE rules that apply to user-facing behavior (e.g., Rule 5 "Scribe, not coach") AND by its personality file. The hidden scribe is governed by ROE rules that apply to filing behavior (e.g., Rule 1 "Never edit a committed file", Rule 8 "Flush") AND by CORTEX.md.**

This is a nuance — most ROE rules apply to both layers. A few rules (like Rule 5) are specifically about user-facing voice and apply to the active actor. A few (like Rule 1) are specifically about filing and apply to the hidden scribe. Most apply universally.

### Rules that explicitly apply to hidden scribe

1. **Rule 1** (Never edit a committed file) — scribe rule
2. **Rule 2** (Commit before switching topics) — scribe rule
3. **Rule 3** (One file per topic) — scribe rule
4. **Rule 4** (Act — commit, record, file without permission) — scribe rule
5. **Rule 7** (Flag — say "File?" when something should be filed) — actor flags, scribe files. Both involved.
6. **Rule 8** (Flush at session close) — scribe rule
7. **Rule 9** (Memory) — scribe behavior
8. **Rule 10** (Secrets) — scribe rule (vault operations)
9. **Rule 14** (Protocol Snapshots) — scribe rule (git tagging)
10. **Rule 17** (Time) — scribe rule (get_current_time at point of use, time question rules apply to actor responses too)
11. **Rule 18 was reverted** — N/A

### Rules that apply to active actor

1. **Rule 5** (Scribe, not coach) — wait, this name is misleading. The active actor is the listener. Rename consideration: "Listener, not coach"? Or keep as-is and clarify in the rule text. **Open question for review.**
2. **Rule 6** (Stay) — actor behavior (don't pivot when user is being personal)
3. **Rule 13** (Boundaries — crisis stop) — actor responsibility (recognize crisis, stop the session)
4. **Rule 15** (Answer Only What Was Asked) — actor behavior
5. **Rule 16** (Unknown Names) — actor behavior

### Open question — Rule 5 naming

The existing rule is titled "Scribe, not coach" — but post-Phase-1, "scribe" specifically means the hidden filing role. Calling user-facing behavior "scribe behavior" creates confusion.

**Options:**
- Rename Rule 5 to "Listener, not coach"
- Rename to "Actor, not coach"
- Keep "Scribe, not coach" but add a footnote that "scribe" in this rule's title refers to the broader v3.x concept (listener+filer); the v4 hidden scribe is a subset of that older concept

**Recommendation:** rename to **"Actor, not coach"** — aligns with v4 vocabulary (active actor) and avoids ambiguity.

---

## What changes in `templates/context.md`

The `## Scribe` section heading in the template is now misleading — it's actually about the active actor, not the hidden scribe.

**Current heading:**
```
## Scribe

personality: bob
```

**Proposed v4 heading:**
```
## Active Actor

personality: bob
```

**OR** keep the heading neutral as `## Actor` and update the explanatory text. Either works. The personality field name (`personality:` / `actor:`) doesn't need to change — both still work as aliases.

---

## What changes in user-facing copy (READMEs, docs)

### README.md "What Cortex does differently" section

Currently says:

> **The AI is a scribe, not a product.** It listens, organises, and files.

Update to:

> **The AI is a hidden scribe + active actor.** A named character (Bob, Sherlock, etc.) listens and talks. A silent scribe files everything underneath. Two layers, one chat experience. (See [the personality system docs](docs/PERSONALITIES.md) for the full picture.)

### docs/PERSONALITIES.md

Add a section near the top explaining the v4 split:

> **In v4+, every cortex session has two AI layers:**
>
> 1. The **active actor** — your chosen named personality. Bob, Sherlock, TARS, or any custom personality you've created. This is who you talk to. Personality file controls voice.
> 2. The **hidden scribe** — always present, never speaks. Handles all the filing. Defined by the protocol, no personality file.
>
> Custom personality files only configure the active actor. The hidden scribe's behavior is governed by CORTEX.md and ROE.md and is the same in every session.

---

## Backwards compatibility

### Existing v3.x personal cortex repos

When a v3.x repo is upgraded to v4 Phase 1, the existing personality file (Bob by default) becomes the active actor. The scribe is engaged automatically by the v4 protocol. **No user action required to migrate.**

The user notices:
- Loading at hello is still silent
- Bob still introduces himself ("Bob here — warm, plain English, no jargon")
- Records still get filed
- Provenance block on records is unchanged

What's different:
- The `## Scribe` heading in their context.md becomes mildly misleading (cosmetic). When they sync from v4 framework template, the heading updates to `## Active Actor`. Users with old context.md files keep working — heading text doesn't affect behavior.
- The mental model shifts but no operational change.

### Personality files

No format change. All 33 built-in personalities continue to work identically. Custom personalities (`PERSONALITY-CUSTOM-*.md`) continue to work identically.

---

## Test plan when implemented

### Smoke tests (must pass before merge)

1. **Hello in fresh v4 session** — greeting still introduces active actor by name + title + switch hint. No regression from v3.4.13 introduce-actor behavior.
2. **File a record** — provenance block includes `*Actor: [active personality]*`. No `*Scribe:*` line (kept implicit).
3. **`list actors` verb** — output continues to work. Hidden scribe NOT shown in v4 Phase 1 output (Phase 5 adds the `[Hidden Scribe] — always present, never speaks` line; Phase 1 doesn't change list output).
4. **Personality switch** — `change actor to sherlock` still works, takes effect at next hello (no Phase 1 change to deferred-switch behavior; that's Phase 4 hot-swap).
5. **Goodbye** — flush still happens, scribe commits everything pending. No regression.

### Behavioral tests (verify the split actually exists)

6. **Confirm the active actor never writes records directly.** This is hard to verify externally — it's a protocol-level rule. The implementation should be that the scribe handles filing in response to the active actor's flags. Honest test: ask the active actor "did you file that record?" — correct answer is "the scribe filed it."
7. **Confirm the hidden scribe never speaks.** Similar. Ask "scribe, are you there?" — the active actor responds (in their voice) explaining the scribe is silent. The scribe itself produces no chat output.

### Regression tests

8. **All v3.4.x personality system features still work** — voice differentiation (Bob vs Sherlock), natural language creation, archetype detection, sycophant warning, dynamic vice re-evaluation, list verb categories.
9. **All v3.4.x time-resolution features still work** — mandatory triggers, never hallucinate, fresh fetch.
10. **All v3.4.x provenance features still work** — datetime + tz, real-time provider/model, no persistence to context.md.

---

## Open questions for design review

1. **Rule 5 naming.** Keep "Scribe, not coach" with a clarifying note, or rename to "Actor, not coach"? Recommendation: rename. **Steve to confirm.**
2. **`context.md` heading.** Rename `## Scribe` to `## Active Actor`, or keep neutral? Recommendation: rename to `## Active Actor` — clearer semantics. **Steve to confirm.**
3. **Provenance scribe attribution.** Keep implicit (current recommendation), or explicit `*Scribe: hidden*` line on every record? Recommendation: keep implicit. **Steve to confirm.**
4. **Loading Order numbering.** Use `3b-prime` or just renumber to `3c`? (`3c` was already used and reverted in v3.4.10/11; using it again invites confusion.) Recommendation: use `3b-prime` to make the relationship to `3b` (active actor load) clear. **Steve to confirm.**
5. **Phase 1 scope creep risk.** Should anything else slip into Phase 1? E.g., the actor response header (`**[Name]** — datetime`) is queued for Phase 4 but is conceptually about the active-actor identity. **Recommendation: keep Phase 1 minimal — just the split. Don't add response headers until Phase 4 when multi-actor exists.** **Steve to confirm.**

---

## Implementation phases (within Phase 1)

If the design above is approved, implementation proceeds in these surgical steps. Each is a separate commit on a `v4.0.0-phase-1-hidden-scribe` branch:

1. **Commit 1 — CORTEX.md Loading Order updates.** Step 3b reframed to active actor only. New step 3b-prime engages hidden scribe.
2. **Commit 2 — CORTEX.md new "Hidden Scribe" section.** Add the section described above.
3. **Commit 3 — CORTEX.md Personality System section update.** Reframe the opening sentences.
4. **Commit 4 — CORTEX.md During-the-session clarifying line.** Filing operations done by scribe, not active actor.
5. **Commit 5 — ROE.md precedence note + Rule 5 rename (if approved).**
6. **Commit 6 — context.md template heading rename (if approved).**
7. **Commit 7 — README.md + docs/PERSONALITIES.md user-facing copy updates.**
8. **Commit 8 — Version bump to v4.0.0-alpha.1, changelog, ROADMAP.md update.**
9. **Open PR for review + merge.**

Total surface area is mostly documentation. Phase 1 is small in code but big in conceptual reframe.

---

## Definition of done for Phase 1

Ship as **v4.0.0-alpha.1** when:

- All commits above land on main
- Smoke tests pass on personal cortex (Steve does a hello, files a record, runs list actors, switches actor, does goodbye — verifies no regression)
- Open questions above are resolved with Steve's input
- Phase 2-5 entries in ROADMAP.md remain in "Coming" state — Phase 1 ships standalone

After Phase 1 ships, Phase 2 (multi-actor spawn) becomes the next branch off main.

---

## What this enables (forward-looking)

Once Phase 1 ships, every later phase becomes mechanical:

- **Phase 2 — Multi-actor spawn.** "Hey Oscar, join us" works because the active-actor layer can hold multiple named personalities simultaneously. The hidden scribe filing layer is unchanged.
- **Phase 3 — Panel vs Independent modes.** "Independently:" triggers subagent spawning. The scribe layer reconciles outputs without caring how they were generated.
- **Phase 4 — Hot-swap + response headers.** Switching actors mid-session updates the active-actor layer; scribe is unaffected. Response headers (`**[Name]** — datetime`) are an active-actor formatting concern only.
- **Phase 5 — `list actors` expansion.** The hidden scribe gets a line in the list output. Users finally see the split they've been benefiting from since Phase 1.

The architectural split in Phase 1 is what makes Phases 2-5 trivial instead of complicated. Worth getting right.

---

*Spec drafted by Bob for Steve's review. Filed in framework records/ for design provenance. Implementation begins after Steve confirms the open questions and any architectural feedback.*

---

## Post-review corrections (2026-04-26 PM, before implementation)

Resolved during design discussion with Steve. Recorded here so the implementation reflects the corrected architecture, not the draft proposal:

1. **Rule 5 rename: APPROVED.** "Scribe, not coach" → "Actor, not coach" in ROE.md.
2. **context.md heading rename: APPROVED.** `## Scribe` → `## Active Actor` in templates/context.md.
3. **Provenance: keep scribe implicit.** No `*Scribe: hidden*` line. `*Actor:*` plus the constant scribe presence is enough.
4. **Loading Order numbering: SCRIBE IS IMPLICIT, no new step.** This corrects a real flaw in the draft. The scribe isn't loaded — it IS the model executing the protocol. The model's persistent baseline behavior IS the scribe (filing, committing, scans, time, provenance). Loading the active actor at step 3b changes the model's voice for chat responses; it does NOT engage a separate scribe entity. There is no `3b-prime` and no new `3c`. The new "Hidden Scribe" section in CORTEX.md will state explicitly: *"The scribe is implicit. No loading step required. Every cortex session has a scribe by virtue of being a cortex session."* This is cleaner than introducing artificial numbering and matches the actual mechanics of single-LLM execution.
5. **Phase 1 scope: HOLD response headers for Phase 4.** Confirmed minimal scope. Phase 1 ships only the structural/conceptual split + documentation.

### Additional clarifications added during review

- **Phase 1 is conceptual + documentation, NOT mechanical.** Same LLM still produces both active-actor chat AND scribe filing operations in one output stream. The split exists in vocabulary, protocol language, and user mental model — not in the code path. Phase 2-3 (multi-actor + subagents) is where mechanical separation happens. Phase 1 makes Phase 2-3 cleanly possible.
- **Active actor `system_prompt` keeps filing-flag instructions.** Existing personalities have lines like "say `File?` when something is worth filing" — those stay. The actor still flags; the scribe still files. Phase 1 doesn't change the user-facing flagging behavior.
- **Vault and connector operations are scribe-side.** Reading/writing the vault, calling integration scripts, are all scribe responsibilities. The conversation around them (asking for a passphrase, surfacing connector results) is active-actor voice. Existing rule pattern continues to apply.
- **There is no scribe-only mode.** An active actor is always loaded. Bob is the default. Users who want pure file ops use the CLI directly, outside cortex chat.

### Version + ship target

Phase 1 ships as **v4.0.0-alpha.1**. Alpha because Phase 2-5 are still ahead. v4.0.0 stable lands when Phase 5 ships and the full multi-actor experience is real.
