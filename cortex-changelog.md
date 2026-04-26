# Cortex Changelog

One line per change. Newest at top. Append in the same commit as the change.

Format: `YYYY-MM-DD HH:MM TZ | file | what changed`

**Not loaded at `hello`.** Available on demand — ask the scribe or use `search`.

<!-- Future: if this file grows large, rotate annually to cortex-changelog-YYYY.md -->

---
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

