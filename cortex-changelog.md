# Cortex Changelog

One line per change. Newest at top. Append in the same commit as the change.

Format: `YYYY-MM-DD HH:MM TZ | file | what changed`

**Not loaded at `hello`.** Available on demand — ask the scribe or use `search`.

<!-- Future: if this file grows large, rotate annually to cortex-changelog-YYYY.md -->

---
2026-04-27 18:23 UTC | version.txt | bump to 4.0.0-alpha.8 — personality hot-swap (mid-session actor switching)
2026-04-27 18:23 UTC | protocol/CORTEX.md | personality file reloads on user-invoked switch verbs mid-session — Loading Order step 3b re-runs, scribe adopts new voice in the very next response. No fresh hello required. Voice is configurable mid-session; protocol is not (protocol files still lock at hello).
2026-04-27 18:23 UTC | protocol/CORTEX.md | "Personality is locked at session open" → replaced with "Personality hot-swaps mid-session"; broader "Session rules are locked" reframed as "Protocol rules are locked" with personality as the explicit exception
2026-04-27 18:23 UTC | protocol/CORTEX.md | Switching personality section — confirmation message changed from "Switched to X. Takes effect at next hello." to "Switched to X. Loading now." Tuning section: if tuned personality is active, hot-swap; otherwise note for next load.
2026-04-27 18:23 UTC | VERBS.md / README.md / docs/PERSONALITIES.md | switch-personality verb documentation updated — hot-swap immediate, no fresh hello required (alpha.8+)
2026-04-27 15:51 UTC | version.txt | bump to 4.0.0-alpha.7 — guardrail: hard block all RWDX until bootstrap complete
2026-04-27 15:51 UTC | protocol/GUARDRAILS.md | NEW Hard Stop: bootstrap incomplete blocks all RWDX (read/write/delete/execute) until repo cloned, protocol loaded, and remote synced
2026-04-27 01:19 UTC | version.txt | bump to 4.0.0-alpha.6 — General split + 8 new personalities + 3 new categories + faith axis
2026-04-27 01:19 UTC | protocol/CORTEX.md | canonical category map: split General (16) into Workplace (3) + Creative & Visionary (3) + Wisdom & Reflection (4) + Distinctive Voices (6); General as a category is retired
2026-04-27 01:19 UTC | personalities/ | NEW: Dr. Walsh (family doctor / GP) — Clinical & wellness fills the GP gap surfaced 2026-04-26
2026-04-27 01:19 UTC | personalities/ | NEW: AA Sponsor + SAA Sponsor (peer-support, 12-step, Big Book / Green Book referenced) — new "Recovery & Peer Support" framework category
2026-04-27 01:19 UTC | personalities/ | NEW: Terry (best friend, dry-sarcastic, always shows up) + Mama (mom-energy) + Pop (dad-energy) — new "Family & Friends" framework category. Terry is named as homage to Steve's real-life best friend.
2026-04-27 01:19 UTC | personalities/ | NEW: Mindfulness Teacher (secular contemplative) + Marcus (Stoic philosopher, Aurelius-style) — new "Mindfulness & Stoicism" framework category, fills the secular contemplative gap
2026-04-27 01:19 UTC | protocol/CORTEX.md | personality file format adds `faith` axis (0 = atheist/scientist, 100 = devout). Pairs with deference as the second axis. Atheist users in 12-step recovery can now create custom sponsor variants with faith: 0 to disable religious framing.
2026-04-27 01:19 UTC | personalities/PERSONALITY-AA-SPONSOR.md + PERSONALITY-SAA-SPONSOR.md | system_prompt instructs grounding in The Big Book (AA) / The Green Book (SAA) with web search if needed; faith axis discipline section explains how the personality adjusts framing based on faith value
2026-04-27 01:19 UTC | README.md + ROADMAP.md | category table updated with 5 new categories (Workplace, Creative & Visionary, Wisdom & Reflection, Distinctive Voices, Mindfulness & Stoicism, Recovery & Peer Support, Family & Friends); General row removed; count updated 47 → 55
2026-04-27 00:02 UTC | version.txt | bump to 4.0.0-alpha.5 — Pop Culture category + 15 new framework personalities + ## aliases + ## domain fields
2026-04-27 00:02 UTC | personalities/ | NEW: 15 framework personalities in Pop Culture category — Mr. Miyagi, John Kreese, Bruce Lee, Chuck Norris, Jean-Claude Van Damme, Sylvester Stallone, Hulk Hogan, Bob Ross, Mr. Rogers, Doc Brown, Yoda, Spock, Robin Williams, Han Solo, The Dude. Each with full trait sliders + system_prompt + alias entries where appropriate. Total framework personalities: 32 → 47.
2026-04-27 00:02 UTC | protocol/CORTEX.md | personality file format spec adds optional `## speech_style` field — structured speaking-style instructions (cadence, address, signature phrases, quirks, avoid) layered on top of system_prompt. More actionable for the LLM than free-form prose. Optional but strongly recommended for character-defining personalities.
2026-04-27 00:02 UTC | personalities/ | speech_style added to all 17 Pop Culture personalities (TARS, Arnold Schwarzenegger, and the 15 new ones). Each captures cadence, how they address the user, signature phrases, vocabulary quirks, and what to avoid.
2026-04-27 00:02 UTC | personalities/PERSONALITY-ARNOLD.md | renamed `## name` Arnold → "Arnold Schwarzenegger"; added `## aliases` field with [Arnold] for backwards-compat invocation. Moved from Clinical & wellness category to Pop Culture in canonical map.
2026-04-27 00:02 UTC | protocol/CORTEX.md | personality file format spec — added optional `## aliases` field (alternate names matched at name resolution); added optional `## domain` field (custom personality grouping in list output)
2026-04-27 00:02 UTC | protocol/CORTEX.md | Loading Order step 3b — name resolution now checks `## name` first, falls back to `## aliases` (case-insensitive) before falling back to default Casey
2026-04-27 00:02 UTC | protocol/CORTEX.md | list personalities/actors — new hard rule for aliases display (`Name (alias: X) — Title.`); new hard rule for domain sub-grouping in Custom section; canonical category map adds Pop Culture row with 17 personalities (TARS + Arnold + 15 new); General row drops TARS; Clinical & wellness row drops Arnold
2026-04-27 00:02 UTC | protocol/CORTEX.md + README.md + README-SIMPLE.md + docs/PERSONALITIES.md + ROADMAP.md | rename "Movie characters" → "Pop Culture" (broader, accommodates Bob Ross / Mr. Rogers / Robin Williams alongside martial arts / sci-fi)
2026-04-27 00:02 UTC | README.md + README-SIMPLE.md + docs/PERSONALITIES.md + ROADMAP.md | personality count updated 32 → 47; Pop Culture category row added
2026-04-26 23:37 UTC | version.txt | bump to 4.0.0-alpha.4 — rename framework default personalities (Bob → Casey, Sherlock → Atlas) to free namespace
2026-04-26 23:37 UTC | personalities/PERSONALITY-CASUAL.md | name field Bob → Casey; system_prompt rewritten for Casey. File slug stays CASUAL (archetype label, slug doesn't drive display).
2026-04-26 23:37 UTC | personalities/PERSONALITY-VERBOSE.md | name field Sherlock → Atlas; system_prompt rewritten for Atlas. File slug stays VERBOSE.
2026-04-26 23:37 UTC | personalities/PERSONALITY-TARS.md | system_prompt_append updated — "Same precision as Sherlock" → "Same precision as Atlas". Title also updated.
2026-04-26 23:37 UTC | protocol/CORTEX.md + README.md + README-SIMPLE.md + docs/PERSONALITIES.md + templates/context.md + ROADMAP.md + VERBS.md | bulk replace Bob → Casey, Sherlock → Atlas, bob → casey, sherlock → atlas. Affected: default personality references, examples, output template, switch examples, canonical category map.
2026-04-26 23:37 UTC | BREAKING (acceptable pre-launch) | existing user context.md files saying `personality: bob` or `personality: sherlock` will fail to resolve and fall back to default (Casey). Steve's personal cortex needs context.md updated to `personality: casey` or `personality: atlas` after sync. No backwards-compat alias map shipped — pre-launch acceptable.
2026-04-26 23:37 UTC | protocol/ROE.md | new Rule 18 — "Framework Files Are Read-Only". Scribe refuses to edit/delete any framework file in a user's personal cortex repo (sync would overwrite anyway). Offers correct path: -CUSTOM.md companion files, PERSONALITY-CUSTOM-*.md for personality overrides, ROE-CUSTOM.md for personal rules. Surfaced by Steve during alpha.4 review: "we need guardrails to prevent or warn the user about removing a framework actor."
2026-04-26 23:15 UTC | version.txt | bump to 4.0.0-alpha.3 — remove Oscar from framework personalities
2026-04-26 23:15 UTC | personalities/PERSONALITY-OSCAR.md | DELETED — no production users invested; freeing the namespace. 33 → 32 built-in personalities.
2026-04-26 23:15 UTC | protocol/CORTEX.md + README.md + README-SIMPLE.md + docs/PERSONALITIES.md + ROADMAP.md | drop Oscar from canonical category map, count from 33 → 32, replace Oscar example references (e.g. "dial Oscar's sarcasm down" → "dial Marlowe's sarcasm down")
2026-04-26 23:04 UTC | version.txt | bump to 4.0.0-alpha.2 — list verb UX fix
2026-04-26 23:04 UTC | protocol/CORTEX.md | list personalities/actors — output template now requires title rendered next to every name (`Name — Title.`); v3.4.10 names-only template was a UX regression, names alone are useless when choosing between 33+ personalities. Hard rule #2 added: always render title field next to name, no summarising or paraphrasing. Surfaced in v4.0.0-alpha.1 post-merge test.
2026-04-26 22:34 UTC | version.txt | bump to 4.0.0-alpha.1 — v4 Phase 1 (Hidden Scribe Separation)
2026-04-26 22:34 UTC | protocol/CORTEX.md | new Hidden Scribe top-level section — split between active actor (named personality, voice) and hidden scribe (protocol role, filing, no personality, never speaks). Scribe is implicit (no loading step). Phase 1 of v4 architectural reframe.
2026-04-26 22:34 UTC | protocol/CORTEX.md | Loading Order step 3b reframed to load active actor only (no scribe load step — scribe is the protocol-execution baseline)
2026-04-26 22:34 UTC | protocol/CORTEX.md | Personality System section opening reframed — "active actor has a personality" instead of "scribe has a personality"
2026-04-26 22:34 UTC | protocol/CORTEX.md | During-the-session: explicit that filing operations are performed by the hidden scribe, not by the active actor's voice
2026-04-26 22:34 UTC | protocol/ROE.md | precedence section adds v4 layer mapping note (which rules apply to active actor vs hidden scribe vs both)
2026-04-26 22:34 UTC | protocol/ROE.md | Rule 5 renamed "Scribe, not coach" → "Actor, not coach" — aligns with v4 vocabulary; rule governs active actor's user-facing behavior
2026-04-26 22:34 UTC | templates/context.md | Scribe section heading renamed to "Active Actor"; helper text updated to clarify the active-actor / hidden-scribe split
2026-04-26 22:34 UTC | README.md | "The AI is two layers" replaces "The AI is a scribe, not a product"; personalities section updated to "active actor has a personality" with pointer to Hidden Scribe spec
2026-04-26 22:34 UTC | README-SIMPLE.md | point #5 rewritten in plain English — introduces both active actor (with personality) and hidden scribe (silent filer)
2026-04-26 22:34 UTC | docs/PERSONALITIES.md | new top section explains v4 two-layer split — personality files configure active actor only; hidden scribe has no personality
2026-04-26 22:34 UTC | records/2026-04-26-v4-phase-1-hidden-scribe-spec.md | spec record (with post-review corrections section) filed for design provenance
2026-04-26 21:16 UTC | version.txt | bump to 3.4.15 — README adds Claude Cowork/Dispatch row with flakiness warning
2026-04-26 21:16 UTC | README.md | "What works where" table adds Claude Cowork / Dispatch row — connectors work because Cowork dispatches a real Claude Code instance to the cloud, but Cowork is flaky/unfinished (hung tooling calls etc.) — out of cortex's control, treat as experimental
2026-04-26 21:16 UTC | README-SIMPLE.md | new "power-user option: Claude Cowork / Dispatch" paragraph in plain English with the flakiness caveat
2026-04-26 14:54 UTC | version.txt | bump to 3.4.14 — README accuracy: AgentBox is in planning stage, not in development
2026-04-26 14:54 UTC | README.md + README-SIMPLE.md | clarify AgentBox status — "in planning stage, not yet built" (was "in development" / "upcoming" which overstated readiness)
2026-04-26 14:46 UTC | version.txt | bump to 3.4.13 — README sandbox-limitation callout
2026-04-26 14:46 UTC | README.md | new "What works where" table at top — explicit that Claude/ChatGPT web+mobile sandboxes block all third-party APIs (Google, Microsoft, etc.). Cortex can only do git operations (clone, read, commit, push, merge) in those environments. Connectors require CLI agents or AgentBox.
2026-04-26 14:46 UTC | README-SIMPLE.md | new "What Cortex CAN'T do on Claude or ChatGPT" section in plain English — points users to AgentBox (in dev) or CLI agents for connector functionality on chat surfaces
2026-04-26 01:52 UTC | version.txt | bump to 3.4.12 — Google connector smoke test fixes
2026-04-26 01:52 UTC | scripts/integrations/google.py + microsoft.py | docstring usage fix — `--passphrase` is a top-level flag and must come BEFORE the subcommand, not after; old docstring showed it after which caused argparse "unrecognized arguments" errors during smoke test
2026-04-26 01:52 UTC | scripts/integrations/google.py + microsoft.py | auth output stale wording — "Commit cortex.secrets.enc" → "Commit cortex.secrets/" (vault format changed from monolithic .enc file to per-secret folder)
2026-04-25 ~23:00 UTC | scripts/integrations/google.py | strip script's own dir from sys.path to avoid shadowing google PyPI package — script is named google.py, was producing false "Google client libraries not installed" errors during smoke test (commit de5ef20, folded into v3.4.12)
2026-04-25 23:29 UTC | version.txt | bump to 3.4.11 — revert v3.4.10 step 3c (provider/model auto-fill); runtime property, not configuration
2026-04-25 23:29 UTC | protocol/CORTEX.md | revert Loading Order step 3c — no auto-fill of provider/model in context.md
2026-04-25 23:29 UTC | protocol/CORTEX.md | provenance block reads provider/model from scribe real-time self-knowledge, never from context.md
2026-04-25 23:29 UTC | templates/context.md | remove provider:/model: from Scribe section — runtime properties don't belong in config
2026-04-25 23:16 UTC | version.txt | bump to 3.4.10 — v3.4.9 post-merge test patch + smoke-break time bug fix
2026-04-25 23:16 UTC | protocol/CORTEX.md | list personalities/actors — exclusive category map, no duplicate rendering (v3.4.10 finding #1)
2026-04-25 23:16 UTC | protocol/CORTEX.md | provenance block omits empty Provider/Model lines instead of rendering blank (v3.4.10 finding #2)
2026-04-25 23:16 UTC | protocol/CORTEX.md | Loading Order step 3c — auto-fill provider/model in context.md at hello if blank (v3.4.10 finding #4)
2026-04-25 23:16 UTC | protocol/CORTEX.md | Time Resolution — Tier 2 (bash date) added, Tier 5 (ask user at point of use) added, mandatory triggers list, never hallucinate (v3.4.10 finding #5+#6)
2026-04-25 23:16 UTC | protocol/ROE.md | Rule 17 — mandatory get_current_time triggers, forbidden inference sources, hallucinating time forbidden (v3.4.10 finding #5+#6)
2026-04-25 21:14 UTC | version.txt | bump to 3.4.9 — v3.4.0 test sprint patch
2026-04-25 21:14 UTC | protocol/CORTEX.md | clarify honesty is a virtue, deference is the only axis (sprint finding #9)
2026-04-25 21:14 UTC | protocol/CORTEX.md | provenance block requires datetime + timezone (sprint finding #7)
2026-04-25 21:14 UTC | protocol/CORTEX.md | hello greeting introduces active actor + switch hint as first two lines (sprint finding #6)
2026-04-25 21:14 UTC | protocol/CORTEX.md | list personalities/actors — name field verbatim, categories, canonical output template (sprint findings #2-5)
2026-04-25 21:14 UTC | VERBS.md / VERBS-CUSTOM.md / protocol/CORTEX.md / README.md / docs/PERSONALITIES.md / templates/context.md / records/donation-mechanism.md / ROADMAP.md | drop slash-prefixed verbs — natural language only (sprint finding #1, architectural)
2026-04-25 14:30 UTC | templates/README.local.md | removed — superseded by README-CUSTOM.md (consistent with -CUSTOM.md companion pattern)
2026-04-25 01:15 UTC | version.txt | bump to 3.4.8
2026-04-25 01:15 UTC | protocol/CORTEX.md | CRITICAL fix: docs/ glob removed from sync scope — replaced with explicit named framework files only; blind docs/ sync would delete user personal documents
2026-04-25 00:45 UTC | version.txt | bump to 3.4.7
2026-04-25 00:45 UTC | README.md | warning banner + -CUSTOM.md companion table; docs/ added to sync scope; *-CUSTOM.md excluded from sync
2026-04-25 00:45 UTC | templates/ | new: README-CUSTOM.md, PERSONALITIES-CUSTOM.md, CONNECTORS-CUSTOM.md
2026-04-25 00:30 UTC | version.txt | bump to 3.4.6
2026-04-25 00:30 UTC | README.md | link to README.local.md added at top; README.md added to sync scope
2026-04-25 00:30 UTC | templates/README.local.md | new: starter template for personal notes, never synced by framework
2026-04-25 00:30 UTC | protocol/CORTEX.md | sync scope expanded: README.md, README-SIMPLE.md added; README.local.md explicitly excluded
2026-04-25 00:15 UTC | version.txt | bump to 3.4.5
2026-04-25 00:15 UTC | protocol/CORTEX.md | feat: user-controlled upgrade gate — ask/always/never preference, skipped_versions list, sync verb always on demand
2026-04-25 00:15 UTC | templates/cortex-upgrade.md | new: upgrade preferences template
2026-04-24 23:58 UTC | version.txt | bump to 3.4.4
2026-04-24 23:58 UTC | protocol/CORTEX-PROJECT.md | fix: silent load instruction added to system prompt — scribe outputs nothing until greeting is ready, fires from token one before CORTEX.md is read
2026-04-24 23:45 UTC | version.txt | bump to 3.4.3
2026-04-24 23:45 UTC | protocol/CORTEX.md | fix: personalities/ added to sync scope (built-ins only, never CUSTOM); context.md migration step appends missing fields after sync
2026-04-24 23:30 UTC | version.txt | bump to 3.4.2
2026-04-24 23:30 UTC | protocol/CORTEX.md | fix: auto-sync framework updates silently at hello — clean updates apply automatically, noted in one greeting line; only real conflicts gate the session
2026-04-24 23:15 UTC | version.txt | bump to 3.4.1
2026-04-24 23:15 UTC | protocol/CORTEX.md | fix: silent load at hello — scribe outputs nothing during load sequence, no narration of confusion or raw counts, single clean greeting
2026-04-24 16:07 UTC | version.txt | bump to 3.4.0 — personality system
2026-04-24 16:07 UTC | personalities/ | ship 33 built-in personalities: Bob (default), Sherlock, + 31 library (TARS, Oscar, Claire, Riff, Alex, Sage, Harper, Max, Ivy, Bishop, Nova, Marlowe, Ziggy, Reed, Cleo, Finn, Rowan, Dante, Dr. Morgan, Dr. Quinn, Jordan, Arnold, Rabbi, Pastor, Father Thomas, Imam, Swami, Lama, Granthi, Daoist, Elder)
2026-04-24 16:07 UTC | protocol/CORTEX.md | personality system: loading order step 3b, list personalities verb, full spec section (format, trait tables, archetypes, inheritance, scribe behaviour, warnings, provenance, ecosystem vocabulary)
2026-04-24 16:07 UTC | templates/context.md | add personality:, provider:, model: fields
2026-04-24 16:07 UTC | VERBS.md | add /personality verb — switch active personality, commits context.md
2026-04-24 16:07 UTC | README.md | add personalities section: 33 built-ins, category table, hard rule callout, context.md snippet
2026-04-24 16:07 UTC | protocol/CORTEX.md | during-session: record provenance block appended to every filed record (actor, provider, model, date)
2026-04-24 16:07 UTC | protocol/CORTEX.md | personality spec: ecosystem vocabulary note — shared vice/virtue/archetype model with Politik, Crosstalk flag
2026-04-24 02:33 UTC | version.txt | bump to 3.3.5 — no-code version bump to test upgrade gate end-to-end
2026-04-24 02:22 UTC | version.txt | bump to 3.3.4 — hello Pass 2 now verifies open items against recent records before surfacing
2026-04-24 02:22 UTC | protocol/CORTEX.md | hello Pass 2: two-step (grep + verify) — read full source file and all records modified in past 7 days before treating unchecked boxes as open
2026-04-24 01:56 UTC | version.txt | bump to 3.3.3 — sync scope now read from upstream's CORTEX.md at sync time (fixes scope-widening bootstrap)
2026-04-24 01:56 UTC | protocol/CORTEX.md | sync flow Scope: read from upstream's CORTEX.md at sync time, not local — prevents scope-widening releases from failing to bootstrap themselves
2026-04-24 01:32 UTC | version.txt | bump to 3.3.2 — upstream gate self-heals when `upstream` remote is missing on fresh clones
2026-04-24 01:32 UTC | protocol/CORTEX.md | Opening (`hello`): upstream version check now verifies `upstream` remote exists and auto-adds it if missing — fixes silent no-op on fresh personal-repo clones
2026-04-24 00:08 UTC | version.txt | bump to 3.3.1 — sync scope generalised to scripts/*.py (top-level glob)
2026-04-24 00:08 UTC | protocol/CORTEX.md | sync flow scope: scripts/setup.py+healthcheck.py+secrets.py → 'scripts/*.py' glob; auto-pulls get_time.py and any future top-level framework scripts
2026-04-23 23:15 UTC | version.txt | bump to 3.3.0 — Time Resolution contract + scripts/get_time.py + ROE Rule 17
2026-04-23 23:15 UTC | protocol/ROE.md | Rule 17 (Time) — fetch fresh via get_current_time, ambiguity-ask, no Tier 4
2026-04-23 23:15 UTC | protocol/CORTEX.md | Time Resolution section — get_current_time contract, tier order, point-of-use fetch, ambiguity-ask rule
2026-04-23 23:15 UTC | scripts/get_time.py | new — Tier 3 fallback for get_current_time contract (ISO 8601 + tz)
2026-04-23 02:30 UTC | protocol/CORTEX.md | archive/ folder — retired files, never scanned, read only on explicit request — v3.2.2
---

