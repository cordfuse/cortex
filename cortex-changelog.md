# Cortex Changelog

One line per change. Newest at top. Append in the same commit as the change.

Format: `YYYY-MM-DD HH:MM TZ | file | what changed`

**Not loaded at `hello`.** Available on demand — ask the scribe or use `search`.

<!-- Future: if this file grows large, rotate annually to cortex-changelog-YYYY.md -->

---
2026-04-23 23:15 UTC | version.txt | bump to 3.3.0 — Time Resolution contract + scripts/get_time.py + ROE Rule 17
2026-04-23 23:15 UTC | protocol/ROE.md | Rule 17 (Time) — fetch fresh via get_current_time, ambiguity-ask, no Tier 4
2026-04-23 23:15 UTC | protocol/CORTEX.md | Time Resolution section — get_current_time contract, tier order, point-of-use fetch, ambiguity-ask rule
2026-04-23 23:15 UTC | scripts/get_time.py | new — Tier 3 fallback for get_current_time contract (ISO 8601 + tz)
2026-04-23 02:30 UTC | protocol/CORTEX.md | archive/ folder — retired files, never scanned, read only on explicit request — v3.2.2
---

