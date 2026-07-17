# [YYYY-Www | YYYY-MM] — Rollup

<!--
  A rollup is a DERIVED digest, not a raw record. Raw records in data/records/ remain
  the source of truth. This file compresses a period so the hello Loading Order can carry
  longitudinal context without paging every raw record. Rollups are regenerable: delete
  this file and the scribe rebuilds it from the underlying records/weeklies.

  Weekly rollup   → data/rollups/YYYY-Www.md   (compresses one ISO week of raw records)
  Monthly rollup  → data/rollups/YYYY-MM.md    (compresses that month's weekly rollups)

  Keep it tight. A rollup that is as long as the records it summarises has failed its job.
-->

## Period
<!-- e.g. Week 2026-W29 (Mon Jul 13 – Sun Jul 19), or Month 2026-07 -->

## Sources
<!-- The record dates (and, for monthly, the weekly rollups) this digest is built from.
     Enables regeneration and provenance. e.g. records 2026-07-13 … 2026-07-19 -->

## Summary
<!-- 2–5 sentences. What defined the period. No performance, no advice. -->

## Health trends
<!-- Only axes the user actually logged. Show direction/range, not every reading.
     e.g. Sleep: avg ~5.5h, two nights <4h. Mood: low mid-week, recovered by Fri.
     Meds: consistent except Wed. Weight: 78.1 → 77.6 kg. Omit axes with no data. -->

## Notable events
<!-- Appointments, decisions, wins, incidents worth carrying forward. -->

## Open items carried forward
- [ ] <!-- Unresolved items still live at period end. -->

## Patterns noticed
<!-- Correlations or recurrences the scribe observed across the period. Optional. -->
