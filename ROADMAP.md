# Cortex — Roadmap

What's shipped, what's in progress, and what's coming.

**Current version:** 4.0.0-alpha.17 — [Changelog](cortex-changelog.md)

---

## Shipped

### v4.0.0-alpha.17 — Phase 6 multi-session foundation *(current)*

The big v4 feature ships its first half. After 18 months of cortex being singleton-only, sessions can finally be scoped — multiple independent runtime states co-existing in the same repo, each with its own active actor + state, sharing the durable record (records, archive, personalities, protocol) globally.

**Why it matters:**
- **Test isolation.** New features can be smoke-tested in scoped sessions without polluting the production singleton.
- **Parallel work threads.** Two simultaneous chats (e.g., dev + journaling) on the same repo no longer collide on `context.md`.
- **Cross-machine continuity.** A session spawned on one machine is engageable from another via `git pull`.

**What ships in alpha.17 (foundation):**
- New `# Multi-Session` section (~150 lines) in `protocol/CORTEX.md` — full design surface from the Phase 6 working spec
- Session `context.md` schema — required + system-managed + user-editable fields with inheritance from singleton
- Lifecycle states: `active` / `detached` / `closed` / `stale` (90d auto-archive)
- File layout: `sessions/{guid}/` for active, `archive/sessions/{guid}/` for closed/stale
- GUID format: `YYYY-MM-DDTHHMM-TZ-<8-char-nanoid>` — sortable + collision-proof
- Two verbs live: `spawn session "<name>"` and `list sessions [filter]`
- Records `Session:` field added to provenance block — required, defaults to `main` for singleton-filed records (user-facing friendly name, not GUID)
- Compression-resilience fallback: scoped session commits include GUID in footer

**Migration: NONE.** Singleton stays at root `context.md`. Scoped sessions are opt-in only via `spawn session`. Existing users see no change unless they invoke the new verbs.

**What's deferred to alpha.18 (runtime):**
- `engage session "<name>"` — attach to existing session, with cross-machine race detection
- `close session "<name>"` — archive flow + name reclamation
- Lifecycle state transitions enforced
- Re-engage from archive flow

**Why split into two:** alpha.17 is the schema + creation surface (additive only — nothing breaks). alpha.18 is the runtime + lifecycle (touches engage / close paths). Splitting lets alpha.17 be field-tested before alpha.18 builds on it.

**Source records:**
- `records/2026-04-27-1707-design-phase-6-multi-session.md` — working spec, 9 of 10 open questions resolved 2026-04-30
- Q3 (multi-actor roster) deferred to Phase 2 design

### v4.0.0-alpha.16 — Claude Code deny-list (framework files protected at OS layer)

`.claude/settings.json` extended with a comprehensive `deny` list covering every framework file. Operationalizes ROE Rule 18 (framework files read-only for the scribe) at the OS / tool layer rather than relying on LLM compliance alone.

**Defense in depth:** even if the scribe's LLM-level rule compliance drifts (e.g., during long sessions, after compaction, or if a personality file system_prompt collides with the rule), the tool layer holds. Framework files only mutate via the sync flow's `git checkout upstream/main` — a `Bash(*)` call that's still in the allow list. Sync continues to work; ad-hoc Edit/Write of framework files does not.

**Coverage:** `protocol/`, `templates/`, `scripts/*.py`, `version.txt`, `.cortex-version`, `LICENSE`, `cortex-changelog.md`, `ROADMAP.md`, `README.md`, `README-SIMPLE.md`, `VERBS.md`, the install/setup scripts, and `.claude/settings.json` itself.

**Agent pointer files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `OPENCODE.md`, `QWEN.md`) deliberately excluded.** They ship with the framework as one-liners pointing at `protocol/CORTEX.md`, but users customize them with personal blocks (per-project session backlogs, per-host instructions, etc.). User-territory in user clones — locking them at the OS layer would break legitimate user customization.

**Personality files NOT covered.** The custom-vs-framework boundary (`PERSONALITY-CUSTOM-*` vs framework names) is too messy to express cleanly in CC's glob patterns without false positives. Personality file protection stays at the LLM-enforced ROE Rule 18 layer for now. Future work might revisit if a clean glob emerges.

**Framework contributors:** the deny list will block legitimate framework dev work (editing protocol files, bumping versions, etc.). Solution: ship a local `.claude/settings.local.json` (gitignored) that overrides the deny list. README documents the exact pattern. Same approach as `cordfuse/ironbound`.

**Why now:** alpha.13/14/15 hardened the bootstrap and sync flows at the protocol layer. Alpha.16 adds the OS-layer reinforcement. The pair (LLM-enforced + OS-enforced) is the same defense-in-depth pattern ironbound established for app-level system files.

### v4.0.0-alpha.15 — Sync flow hardening (live enumeration + pre-sync drift check)

Two targeted fixes to the sync flow surfaced by the personality-sync-drift bug record. No new features.

**Fix B — Live `git ls-tree` enumeration is mandatory.** Hardcoded personality file lists are explicitly a protocol violation. Earlier alpha sync flows used hardcoded checkout lists which silently dropped framework personalities — alpha.4 missed `PERSONALITY-CASUAL.md` (Bob → Casey rename), alpha.6 missed `PERSONALITY-CHUCK-NORRIS.md`, and the drift accumulated across 5 sync cycles before being caught. Live enumeration ensures every sync pulls every framework personality currently on upstream/main.

**Fix D — Pre-sync drift check.** Scribe MUST diff every framework-scope path between local HEAD and upstream/main BEFORE the sync runs. If files differ beyond what the sync would resolve, surface the count in the report: *"Drift detected: N file(s) differ from upstream beyond what this sync resolves. Run `reconcile` to resolve."* This catches historical drift (files silently dropped by earlier hardcoded sync lists) that post-sync cache invalidation alone can't catch.

**`reconcile` verb (Fix A) is alpha.16 candidate** — full reconciliation flow with three-category surfacing (behind / ahead / removed) and user gating per file. The pre-sync drift check in alpha.15 surfaces the count; `reconcile` will resolve.

**One-time reconciliation already applied:** Steve's personal cortex had three documented drifts (CASUAL.md, CHUCK-NORRIS.md, OSCAR.md). Resolved in personal cortex commit `befac99` per Fix C of the bug record. Alpha.15 prevents recurrence.

**Why now:** ironbound + alpha.13 lessons compounded — *"a spec without an enforcement path is a wish"*. Alpha.13 hardened detection. Alpha.15 hardens the underlying file enumeration so detection has correct ground truth.

### v4.0.0-alpha.14 — Default `.claude/settings.json` (`bypassPermissions`)

Ships a default `.claude/settings.json` at framework root with `permissions.defaultMode: "bypassPermissions"`. Claude Code stops asking for per-prompt approval on the cortex hello flow.

**Why:** first-time CC user runs `claude "hello"` in a fresh cortex clone, hits a sequence of approval prompts (10+ before the greeting renders), and the friction kills the cortex value proposition before it can demonstrate itself. Bypass mode is the only sensible default for a protocol that needs broad file + bash access by design.

**Trust model:** protocol files (`protocol/CORTEX.md`, `GUARDRAILS.md`, `ROE.md`, `DISCLAIMER.md`) define what the scribe can do. Those rules are LLM-enforced. CC does not gate the scribe — there is no second OS-level safety layer. Users who want per-prompt approval back can delete `.claude/settings.json`.

Added a clearly-marked "⚠️ Permissions are wide-open by default — and that's deliberate" section to `README.md` explaining the trust model, how to revert, and noting the equivalent flags for other CLI agents (Codex `--full-auto`, etc.).

**Why now:** surfaced during alpha.13 CLI validation when first-time `claude "hello"` invocation in personal cortex hit a permission gate before the version-line test could even fire. The bootstrap UX matters as much as the bootstrap correctness — alpha.13 fixed correctness; alpha.14 fixes the friction that prevented anyone from ever seeing it.

**Future:** ship equivalent default configs for Codex CLI, Gemini CLI, OpenCode, Qwen Code, and GitHub Copilot CLI as their conventions stabilize. File an issue to request a specific agent.

### v4.0.0-alpha.13 — Bootstrap reliability patches

No new features. One focused cycle to close compounding bootstrap failures surfaced during the alpha.12 multi-parent inheritance smoke test (Magnus Pedersen). Four targeted fixes to the protocol:

**Fix 1 — Strict Gate 3 enforcement (`protocol/GUARDRAILS.md`).** `git fetch origin` (and `upstream` if configured) MUST run at hello *before* the greeting renders. If local is behind, the scribe MUST surface the delta and apply the user's `auto_upgrade:` preference (`always` runs sync now, `ask` shows 3-way prompt, `never` still surfaces the delta). Silent stale-state bootstrap is now an explicit protocol violation.

**Fix 2 — Personality cache invalidation (`protocol/CORTEX.md`).** Loading Order step 3b — scribe MUST re-scan `personalities/` from disk on every lookup miss before reporting "no such file." Stale-cached lookup misses are a protocol violation.

**Fix 3 — Filename / name alignment (`protocol/CORTEX.md`).** Custom personality filename slug MUST align with the `## name` field or an alias entry. Refuse to write `PERSONALITY-CUSTOM-BC-SME.md` for a personality named "Magnus Pedersen" — this caused the actual lookup miss in alpha.12. Lookup now falls back through three paths: `## name` → `## aliases` → filename slug.

**Fix 4 — Accurate sync report (`protocol/CORTEX.md`).** Sync flow Step 4 requires reporting **all** files actually pulled, not a sample. Three formats based on change count: 0 / 1 / N. Reporting only `PERSONALITY-YODA.md` when ten files updated is a protocol violation. Personality cache MUST invalidate after any sync that touches `personalities/`.

**Why now:** Fluid Protocol's velocity claim depends on platform reliability. Six alphas in 24 hours is meaningless if any of them might be running on stale state without the user knowing. Reliability is the precondition, not a separate concern.

**No new features in this cycle.** alpha.14+ resumes feature work (Phase 6 multi-session, Phase 2 multi-actor, Legal/Education/Marketing domains, `docs/PERSONALITIES.md` alignment, `## domain` field backfill).

### v4.0.0-alpha.12 — Information Technology domain (+9 personalities)

New top-level domain `Information Technology` with nine framework personalities — all stack-agnostic at the framework level. Stack-specific specialists belong in custom personalities that `parents:` inherit from these.

| # | Name | Role |
|---|---|---|
| 1 | Devon | Senior Software Engineer / Tech Lead |
| 2 | Kai | Junior Developer |
| 3 | Riley | DevOps Engineer |
| 4 | Knox | Infrastructure / Systems Engineer |
| 5 | Vega | Senior Cloud Architect |
| 6 | Avery | Product Manager |
| 7 | Sloane | QA Engineer |
| 8 | Orion | UX/UI Designer |
| 9 | Drew | Functional Consultant |

**Framework personality count: 62 → 71.** Information Technology is the first domain explicitly dedicated to the engineering / IT discipline that builds and operates Cortex itself.

**Why now:** the framework was missing role-archetype personalities for the IT discipline despite being built by and for engineers. Carved out the role layer (framework) from the stack layer (custom). All nine voices are pronoun-neutral by default; users override pronouns and stack expertise via `parents:` inheritance.

**Stack-agnostic principle:** Riley, Knox, Vega all genericized — pipeline platform / hardware vendor / cloud provider specifics live in custom children. Same for Sloane (testing tools) and Orion (design tools). Devon, Kai, Avery, Drew don't carry stack at all.

### v4.0.0-alpha.11 — Multi-parent inheritance

`## parent` (single) extended to `## parents` (ordered list). Custom personalities can now legitimately inherit from multiple framework or custom personalities — the "everything guy" pattern, where a senior IC spans developer + infrastructure + cloud architect or a domain SME spans functional consultant + senior engineer + infrastructure.

**Linearization:** left-to-right precedence. First parent listed wins on any field conflict. `system_prompt`s concatenate in declared order; child `system_prompt_append` runs last. Diamond inheritance dedup'd.

**Backwards-compat:** legacy `## parent: <file>` is treated as `## parents: [<file>]`. No migration required.

**Why now:** surfaced in v4 design conversation while scoping the BC SME custom — multi-parent is the right model for cross-cutting expertise. Small protocol clarification, ships standalone.

### v4.0.0-alpha.10 — Pop Culture additions (+7 personalities)

Seven new framework personalities under the Pop Culture domain:

- **Indiana Jones** — adventurer-archaeologist, dry quips, professorial in his element
- **Captain Jean-Luc Picard** — measured leader, principled, classical references
- **Buffy Summers** — slayer wisecracks plus dead-serious when stakes show up
- **Bill Murray** — deadpan, mournful, surreal cultural persona
- **Angus MacGyver** — no-guns improvisation, narrates-while-doing science teacher
- **Lieutenant Columbo** — disarming, underestimated, "just one more thing"
- **Tony Soprano** — mob-boss-in-therapy, threat-and-vulnerability duality (voice only — ROE/GUARDRAILS bind)

**Framework personality count: 55 → 62.** Pop Culture domain: ~17 → ~24.

Filed `docs/PERSONALITIES-CUT.md` capturing references that were considered but cut, with reasons (Marty McFly, Sherlock Holmes, X-Files duo, Crocodile Dundee, Rocky, Terminator, McClane, Clouseau, Lecter, Walter White, Don Draper, Jack Sparrow, Jack Bauer, Dr. House, Ron Burgundy, Hank Hill, Gandalf).

**Why now:** carved from the long-deferred Pop Culture batch. Direct merge to main — additive only, no protocol/ROE/GUARDRAILS changes, no version-format breaking changes.

**Known gap (follow-up):** `docs/PERSONALITIES.md` is out of date with the `personalities/` folder — missing Pop Culture / Recovery & Peer Support / Family & Friends / Mindfulness & Stoicism sections from alpha.5/alpha.6/alpha.10. Needs an alignment pass.

### v4.0.0-alpha.9 — Response headers (compression-resilience)

Every actor response now opens with a single-line header: `**[Actor — Session]** — YYYY-MM-DD HH:MM TZ`. The header is a compression-resilience mechanism, not a flourish — it re-asserts the actor + session binding on every turn, surviving provider context compaction (Claude auto-compaction, GPT context windowing, etc.).

**What changed:**
- New `# Response Header` section in `protocol/CORTEX.md` specifies the format, recovery semantics on lost binding, and the no-paraphrase rule (the actor renders the header in fixed format, not in their own voice).
- `docs/PERSONALITIES.md` notes the header.
- "Main session" is the user-facing alias for the singleton (default); scoped sessions land in Phase 6.

**Why now:** carved out from Phase 4 + Phase 6, same playbook as alpha.8 hot-swap. The header is display-only and pre-bakes the slot for Phase 6 (multi-session); there everything renders as `main session` until scoped sessions arrive. Compression mitigation kicks in immediately for every session run after merge.

### v4.0.0-alpha.8 — Personality hot-swap (mid-session actor switching)

Kills the deferred-switch UX papercut that's been live since v3.4.0. The active actor's personality file now reloads on user-invoked switch verbs mid-session — no fresh hello required. Voice changes from the very next response.

**What changed:**
- Loading Order step 3b — explicit hot-swap allowed for personality (re-runs on switch verb, not just at hello).
- "Session rules locked at session open" reframed as "Protocol rules locked" — personality is the explicit exception. Voice is configurable mid-session; protocol is not.
- Switch confirmation: *"Switched to X. Loading now."* (was *"Takes effect at next hello."*).
- Tuning a slider on the active personality also hot-swaps; tuning a non-active personality is saved for next load.
- VERBS.md, README, docs/PERSONALITIES.md all updated.

**Why now:** complaint surfaced first in v3.4.0 testing (2026-04-25); officially deferred to Phase 4. On reflection, hot-swap doesn't require Phase 2 multi-actor or Phase 3 subagent infrastructure — it's just a small protocol clarification. Carved out and shipped early.

### v4.0.0-alpha.7 — Bootstrap RWDX guardrail

New Hard Stop in `protocol/GUARDRAILS.md`: until the repo is cloned, protocol files are loaded, AND `git fetch origin` confirms local is current — the scribe refuses **all** RWDX operations (Read, Write, Delete, Execute, including personality loads, verb execution, integration scripts). "Partial bootstrap is not bootstrap." Closes a silent failure mode where an unbootstrapped scribe would offer to fabricate personalities or read records from training data instead of the actual repo. Surfaced when Steve pre-bootstrap asked the scribe to switch to "Yoda" and got an offer to *create* a Yoda personality.

### v4.0.0-alpha.6 — General split + 8 new personalities + 3 new categories + faith axis

**General domain split into 4 sub-categories** — General was overreaching at 16 personalities in one blob. Now:
- **Workplace** (3): Alex, Bishop, Max
- **Creative & Visionary** (3): Harper, Ziggy, Nova
- **Wisdom & Reflection** (4): Sage, Ivy, Rowan, Dante
- **Distinctive Voices** (6): Riff, Marlowe, Reed, Cleo, Finn, Claire

**8 new framework personalities:**
- **Dr. Walsh** (Clinical & wellness) — family doctor / GP, fills the long-flagged gap
- **AA Sponsor** (Recovery & Peer Support) — peer-to-peer 12-step, Big Book grounded, faith axis configurable
- **SAA Sponsor** (Recovery & Peer Support) — same model, trauma-informed, Green Book grounded
- **Terry** (Family & Friends) — best friend, dry-sarcastic, always shows up. Homage to Steve's real-life best friend.
- **Mama** (Family & Friends) — mom-energy, warmth + authority
- **Pop** (Family & Friends) — dad-energy, steady + practical
- **Mindfulness Teacher** (Mindfulness & Stoicism) — secular contemplative practice
- **Marcus** (Mindfulness & Stoicism) — Stoic philosopher, Aurelius-style

**3 new framework categories:**
- **Recovery & Peer Support**
- **Family & Friends**
- **Mindfulness & Stoicism**

**New `faith` axis** in personality file format (alongside deference). Range 0 (strict atheist/scientist) → 100 (devout). Pairs with the existing axis system. Critical for 12-step sponsor personalities — atheist users in recovery can now create custom sponsor variants with `faith: 0` to disable religious framing entirely. Default in AA/SAA Sponsors is 40 (mid, accommodating).

**Total framework personalities: 47 → 55.**

### v4.0.0-alpha.5 — Pop Culture category + 15 new framework personalities + aliases + domain field

**New framework category: Pop Culture.** TARS and Arnold Schwarzenegger move into it from General/Clinical. 15 new personalities added: Mr. Miyagi, John Kreese, Bruce Lee, Chuck Norris, Jean-Claude Van Damme, Sylvester Stallone, Hulk Hogan, Bob Ross, Mr. Rogers, Doc Brown, Yoda, Spock, Robin Williams, Han Solo, The Dude. Pop Culture is now the largest framework category at 17 personalities.

**Total framework personality count: 32 → 47.**

**`## aliases` field added to personality file format.** Optional. Alternate names matched at Loading step 3b name resolution (case-insensitive). Surfaced in `list personalities` output as `Name (alias: X) — Title.` Used for Arnold Schwarzenegger (alias: Arnold) so backwards-compat invocation `change actor to arnold` keeps working after the rename.

**`## domain` field added to personality file format.** Optional. Used for custom-personality sub-grouping within the Custom section of `list personalities`. Built-ins use the canonical category map; custom personalities can declare their own domain (e.g. "Sesame Street", "Peanuts").

**`## speech_style` field added to personality file format.** Optional. Structured speaking-style instructions — cadence, how the character addresses the user, signature phrases, vocabulary quirks, and what to avoid. Layered on top of `## system_prompt` (which covers WHAT the character is); speech_style covers HOW they actually talk. More actionable for the LLM than free-form prose. Applied to all 17 Pop Culture personalities.

**Arnold renamed.** `## name` Arnold → "Arnold Schwarzenegger" (full canonical name). Aliases keep "Arnold" working for invocation.

### v4.0.0-alpha.4 — Rename framework defaults + framework-file read-only guardrail
- **Bob → Casey, Sherlock → Atlas.** Frees the Bob and Sherlock namespace for users who want those names as custom personalities (e.g. Bob McGrath and Sherlock Hemlock from Sesame Street).
- **Casey** — gender-neutral, modern but rooted, friendly. Same warm-plain-spoken archetype Bob filled. File slug stays `PERSONALITY-CASUAL.md`.
- **Atlas** — gender-neutral, mythological weight (held the world; the methodical scribe holds the records). Same precise-methodical archetype Sherlock filled. File slug stays `PERSONALITY-VERBOSE.md`.
- TARS now references "Atlas's precision" instead of "Sherlock's precision" in title and system_prompt.
- **NEW — ROE Rule 18: Framework Files Are Read-Only.** The scribe refuses to edit or delete any framework file in a user's personal cortex (sync would overwrite anyway). Offers correct path instead: `-CUSTOM.md` companions for docs, `PERSONALITY-CUSTOM-*.md` for personality overrides, `ROE-CUSTOM.md` for personal rules. Prevents users from accidentally damaging their framework state.
- **Breaking change (pre-launch acceptable):** existing user `context.md` files saying `personality: bob` or `personality: sherlock` will fail to resolve and fall back to the new default (Casey). Manual edit needed: `personality: casey` or `personality: atlas`. No backwards-compat alias map shipped — pre-launch user count is essentially zero.

### v4.0.0-alpha.3 — Remove framework Oscar
- `personalities/PERSONALITY-OSCAR.md` deleted from the framework. No production users invested in him; namespace freed for users who want their own Oscar (e.g. Oscar the Grouch as a custom personality).
- Built-in personality count: 33 → 32 (Casey + Atlas + 30 library).
- Example references using Oscar updated to use other personalities (Marlowe for sarcasm tuning, Riff for "too much" example).

### v4.0.0-alpha.2 — List verb UX fix
- `list personalities` / `list actors` now render the `## title` field next to every personality name (`Name — Title.`). Names alone are useless when choosing between 33+ personalities — the v3.4.10 names-only canonical template was a UX regression that this patch corrects.
- Surfaced during the v4.0.0-alpha.1 post-merge test. Hard rule #2 added to the rendering spec: always render title, no summarising or paraphrasing.

### v4.0.0-alpha.1 — Phase 1: Hidden Scribe Separation

The first phase of the v4 multi-actor architecture. Splits the v3.x "scribe" concept (which did both filing and conversational voice) into two distinct layers:

- **Active actor** — the named personality the user talks to. Loaded from `personalities/`. Has voice, traits, archetype. **Never touches the repo directly.**
- **Hidden scribe** — a protocol role. Reads, writes, commits, pushes, runs scans, resolves time, appends provenance. **Always present, never speaks.** Has no personality file. Implicit — no loading step required, since the model executing the protocol IS the scribe by default.

Phase 1 is **conceptual + documentation, not mechanical.** The same LLM still produces both active-actor chat and scribe filing in one output stream. Phase 2-3 (multi-actor + subagent modes) introduce mechanical separation. Phase 1 establishes the vocabulary and architectural ground that lets Phase 2-5 build cleanly.

What changed:
- New "Hidden Scribe" top-level section in `protocol/CORTEX.md`
- Loading Order step 3b reframed to load active actor only
- ROE Rule 5 renamed "Scribe, not coach" → "Actor, not coach"
- ROE precedence section maps which rules apply to which layer
- `templates/context.md` heading renamed `## Scribe` → `## Active Actor`
- README.md, README-SIMPLE.md, docs/PERSONALITIES.md updated for v4 framing

What's NOT in Phase 1: multi-actor spawn (Phase 2), panel vs independent modes (Phase 3), hot-swap + actor response headers + mid-session protocol reload (Phase 4), `list actors` expansion (Phase 5).

Spec: [`records/2026-04-26-v4-phase-1-hidden-scribe-spec.md`](records/2026-04-26-v4-phase-1-hidden-scribe-spec.md)

### v3.4.15 — Claude Cowork/Dispatch row in README
- README.md and README-SIMPLE.md now disclose that Cortex with full connector functionality works in Claude Cowork / Dispatch (Claude Code dispatched to the cloud from Claude.ai) — but with an explicit flakiness warning. Cowork is in active development on Anthropic's side; hung tooling calls and unstable behavior are common. Out of cortex's control. Treat as experimental.
- Honest user disclosure: this is the only chat-with-connectors path on mobile RIGHT NOW, until AgentBox v1.0 ships.

### v3.4.14 — AgentBox status accuracy
- README.md and README-SIMPLE.md now accurately describe AgentBox as "in planning stage, not yet built" (previously "in development" / "upcoming" which overstated readiness).

### v3.4.13 — Sandbox Limitation Callout in README
- **Plain-language warning at top of both READMEs.** Users now know up front: on Claude.ai or ChatGPT web/mobile, Cortex can only do git operations (clone, read, commit, push, merge). All third-party APIs (Google, Microsoft, Notion, Slack, etc.) are blocked by the platforms' tool sandboxes — by design, not configurable.
- **Pointer to AgentBox.** For users who want full connector functionality on phone/tablet without a developer setup, the README points at `cordfuse/agentbox` (in development) — a local Electron app that exposes a CLI agent's chat UI to any device, no sandbox restrictions.
- **Trigger:** prevents future users from hitting the same 3-hour cliff Steve hit on 2026-04-25 trying to make `googleapis.com` reachable from Claude.ai web.

### v3.4.12 — Google Connector Smoke Test Fixes
- **Google connector validated end-to-end.** All five Google products (Calendar, Gmail, Drive, Tasks, Contacts) tested live against Steve's account via Penguin. Real data flowing in clean markdown. OAuth refresh token persists in vault.
- **`scripts/integrations/google.py` shadowing fix.** Script is named `google.py` — Python adds its directory to `sys.path[0]`, making `from google.oauth2 import ...` resolve to the script itself instead of the real google PyPI package. Script now strips its own dir from sys.path before the imports.
- **Docstring usage fix in google.py + microsoft.py.** `--passphrase` is a top-level argparse flag and must come BEFORE the subcommand. Old docstring showed it after, causing "unrecognized arguments" errors. Now: `python google.py --passphrase X auth` (correct).
- **Auth output stale wording fix.** Both google.py and microsoft.py printed "Commit cortex.secrets.enc to persist across devices" — but the vault format changed from monolithic `.enc` file to per-secret `cortex.secrets/` folder. Updated to "Commit cortex.secrets/".

### v3.4.11 — Provider/Model is a Runtime Property
- **Reverted v3.4.10 step 3c (auto-fill provider/model in context.md).** Provider and model are runtime properties, not configuration. Persisting them in `context.md` was a category error — values go stale the moment you switch providers, switch devices, or share the repo with another collaborator using a different AI.
- **Provenance now reads real-time.** The scribe pulls `provider:` and `model:` from its own self-knowledge at the moment a record is filed. Always current. No persistence drift.
- **`provider:` and `model:` removed from `context.md` template.** Existing user files with those fields are ignored — clean up at next sync.
- Sprint duration: ~10 minutes from finding to ship. Mistake from v3.4.10 caught and corrected before it could spread.

### v3.4.10 — Time Resolution Hardening + Post-Merge Polish
- **Time Resolution overhaul.** Tier 2 (bash `date`) added between native tools and MCP — works in Claude web project mode and most agent CLIs. Tier 5 (ask user at point of use) added as the explicit fallback when all higher tiers fail. **Hallucinating time is now forbidden** by both CORTEX.md and ROE Rule 17.
- **Mandatory triggers for `get_current_time`.** "What time is it", "when is my next X", "how long until / ago", "is X today/tomorrow", "am I late" — all now require a fresh fetch. Inferring current time from schedule context, message ordering, file mod times, or session memory is explicitly forbidden.
- **Auto-detect provider/model at hello (Loading Order step 3c).** *Reverted in v3.4.11* — provider/model are runtime properties, not configuration. Should not be persisted.
- **Provenance block omits empty fields.** Empty `Provider:` and `Model:` lines no longer render as `*Provider: *` — they drop entirely. Block contracts cleanly when only `Actor:` and `Filed:` are populated.
- **`list personalities` deduplicates.** Each personality appears in exactly one category section. Arnold no longer rendered in both General and Clinical & wellness.

### v3.4.9 — Test Sprint Patch
- **Architectural rule: natural language only, no slash-prefixed verbs.** AI client UIs (Claude web, ChatGPT, Gemini web) intercept slash prefixes — slash verbs silently fail. Cortex routes natural language.
- **Greeting introduces active actor.** Name + title + switch hint as first lines. Solves the "who am I talking to" problem at session open.
- **`list personalities` / `list actors` rendering fixed.** `## name` field verbatim (TARS not Tars, Atlas not Verbose), canonical category grouping (Defaults / General / Clinical / Faith), deterministic output template.
- **Provenance block requires datetime + timezone.** Aligns with v3.3.0 Time Resolution and ROE Rule 17. `Filed: 2026-04-25 17:30 EDT` instead of date-only.
- **Honesty/deference clarification.** `honesty` is a virtue; `deference` is the only axis. Closes spec ambiguity.

### v3.4.0 — Personality System
- **Personality system shipped** — at the time of v3.4.0 release: 33 built-in personalities (Bob default, Sherlock + 31 library). Renamed and expanded since: see v4.0.0-alpha.3, alpha.4, alpha.5 entries above. Current count is 47.
  - Validated in 2026-04-25 test sprint: voice differentiation real (Casey vs Atlas distinct), natural-language creation produces high-quality system prompts, archetype + sycophant warnings fire correctly, dynamic vice re-evaluation on edits
- Tunable trait model: vibe, virtues, vices, soft skills, hard skills — all percentage sliders
- Vice/virtue mirror pairs (pride↔integrity, cowardice↔courage, etc.)
- Archetype system: HARDLINER, DIPLOMAT, ANALYST, CREATIVE, LONE_WOLF, TEAM_PLAYER, JOKESTER
- Personality inheritance — custom personalities declare a parent, override only what they change
- Natural language creation — describe a personality, scribe writes the file
- Natural language tuning — "dial Marlowe's sarcasm down to 40%"
- Sycophant warning — fires when honesty < 40% and deference > 70%
- Archetype vice warnings — flags dangerous trait combinations at creation
- `switch personality` / `change actor` / `use [name]` — natural-language verbs to switch active personality (both `personality:` and `actor:` field aliases accepted)
- `list personalities` / `list actors` built-in verbs (aliases)
- `personality:` / `actor:` field in `context.md` — both spellings accepted
- Record provenance block — every filed record now includes actor, provider, model, date
- `context.md` gains `personality:`, `provider:`, `model:` fields
- Full personality reference: [docs/PERSONALITIES.md](docs/PERSONALITIES.md)

### v3.3.x — Stability Sprint
- **v3.3.4** — Pass 2 open items: two-step verification (grep + read recent records) before surfacing open items
- **v3.3.3** — Sync scope bootstrap: scribe reads upstream's scope definition at sync time, not local stale copy
- **v3.3.2** — Upstream gate self-heals when `upstream` remote is missing on fresh clones
- **v3.3.1** — Sync scope generalised to `scripts/*.py` glob; `get_time.py` auto-lands on sync
- **v3.3.0** — Time resolution: `get_current_time` contract with tier order (native → MCP → script); timestamp ambiguity ask before filing; Google and Microsoft 365 connectors

### v3.2.x — Vault + Connectors
- AES-256 encrypted secrets vault (`cortex.secrets.enc`) — one passphrase governs all
- Tailscale mesh network connector
- rclone connector (70+ filesystem backends)
- Archive folder (`archive/`) with scribe rules — never scanned, never modified

### v3.1.x — Templates + Examples
- 19 templates across personal, health, life admin, work, creative, analytical
- Anonymised example entries
- `cortex-changelog.md` — rolling change log, not loaded at hello, on demand

### v3.0.x — Core Protocol
- Session verbs: `hello`, `goodbye`, `status`, `sync`, `search`, `list verbs`
- 3x opening scan (uncommitted, open items, unresolved follow-ups)
- 3x closing scan (flush before close)
- ROE — 20 rules of engagement for the scribe
- GUARDRAILS — crisis protocol, hard stops, sandbox integrity
- DISCLAIMER — honest framing, crisis resources
- Upstream version gate — checks for framework updates at every `hello`
- AI-driven sync flow — transparent, step-by-step, no blind overwrites
- Custom verbs via `VERBS.md` and `VERBS-CUSTOM.md`
- ROE-CUSTOM.md — personal rule extensions numbered from 100
- Multi-agent support: Claude (CLAUDE.md), Gemini (GEMINI.md), OpenAI (AGENTS.md), Qwen (QWEN.md), OpenCode (OPENCODE.md)
- Cloud + offline/self-hosted deployment modes

---

## In Progress

### v3.4.x — Personality System Refinements
- [ ] Mid-session personality tuning (currently locked to session open — by design)
- [ ] Personality history log — which personality was active per session (Hansard-style)
- [ ] User personality performance notes — "Riff was too much today"
- [ ] Blend mode — `50% Casey, 50% Atlas` composite personality

---

## Upcoming

### v3.5.0 — Integrations Expansion
- [ ] Notion connector
- [ ] Slack connector
- [ ] GitHub connector (issues, PRs, activity)
- [ ] Linear connector
- [ ] Apple Health / Google Fit ingestion
- [ ] Spotify listening history
- [ ] Banking / transactions (read-only, CSV import)
- [ ] Plex library + watch history
- [ ] Jellyfin (self-hosted alternative to Plex)
- [ ] 1Password live connection (`op` CLI — secrets retrieved at runtime, never stored)
- [ ] Bitwarden connector (self-hosted option)

### v3.6.0 — Developer Experience
- [ ] Setup wizard — writes starter `.claude/settings.json` at end of setup (git, gh, docker, npm, mkdir — prevents silent hangs on mobile)
- [ ] Egress proxy / web fetcher — `scripts/integrations/fetcher.py` for fetching arbitrary URLs inside the permitted scripts boundary
- [ ] Fail-gracefully rule — any script calling external services catches network errors and prints manual fallback
- [ ] `donate` verb — surfaces CAMH Foundation link

### v3.7.0 — Federation
- [ ] Multiple isolated Cortex repos linked through a root with read-only pointers
- [ ] Satellites control exposure via `expose.md`
- [ ] Cross-repo `search` from root
- [ ] Full context onboarding on desktop — audit all active projects on first run, file a record per repo

### v4.0.0 — Multi-Actor Sessions *(major, in progress)*

Phased delivery. Phase 1 ships as v4.0.0-alpha.1 (see Shipped above). Subsequent phases roll out as alpha/beta releases until v4.0.0 stable.

- [x] **Phase 1 — Hidden scribe separation** *(shipped v4.0.0-alpha.1, 2026-04-26)* — protocol role split from active actor; conceptual foundation for the rest of v4.
- [ ] **Phase 2 — Multi-actor sessions** *(next)* — spawn named actors mid-session in plain English (*"Hey Marlowe, join us"*). Each actor carries their full personality profile. Multiple named actors in the room simultaneously.
- [ ] **Phase 3 — Panel vs Independent modes** — Panel: single inference context, model co-generates all actor responses in one pass, actors may build on each other's context. Independent: subagents, each actor receives the same input with no shared context. Triggered explicitly (*"blind panel:"*).
- [ ] **Phase 4 — Hot-swap, actor response headers, mid-session protocol reload** — *"switch to Atlas"* changes active actor immediately (no next-hello deferral). Every named actor response opens with `**[Name]** — YYYY-MM-DD HH:MM TZ`. `sync` mid-session reloads protocol rules immediately, not at next hello.
- [ ] **Phase 5 — `list actors` expansion + actor management** — `list actors` shows all currently-loaded actors plus the hidden scribe line. Mid-session add, remove, modify actors. Personality history per session (Hansard-style log of who was active when).

---

## Not Planned

These are explicitly out of scope. Cortex is a scribe and sounding board — not a product that competes with these.

- Diagnosis, therapy, or clinical care
- Crisis intervention (handled by GUARDRAILS — always refers to professional services)
- A native mobile app
- A SaaS or subscription offering
- Cordfuse access to user data — ever

---

*Maintained by [Cordfuse](https://github.com/cordfuse). Roadmap reflects intent, not commitment.*
