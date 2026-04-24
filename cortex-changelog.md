# Cortex Changelog

One line per change. Newest at top. Append in the same commit as the change.

Format: `YYYY-MM-DD HH:MM TZ | file | what changed`

**Not loaded at `hello`.** Available on demand — ask the scribe or use `search`.

<!-- Future: if this file grows large, rotate annually to cortex-changelog-YYYY.md -->

---
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

