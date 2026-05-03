# context.md — Canonical Session Context

Read at every `hello`. Update in the same commit whenever people, situations, or threads change.

---

## Active Actors

actors:
  - name: casey
    active_speaker: true
    joined_at: 2026-01-01 00:00 UTC

*`actors:` (v4.0.0-alpha.32+) — array of named personalities present in the session. Each entry: `name` (required), `active_speaker: true|false` (exactly one entry must be `true` — that's the default responder when no actor is named in a turn), `joined_at` (informational timestamp). Add actors via natural language: "Hey Oscar, join us" or "add actor oscar". Remove via "Oscar, you can step out" or "remove actor oscar". Switch the active speaker via "change actor to oscar". See protocol/CORTEX.md → Multi-actor sessions.*

*Legacy single-actor format (pre-alpha.32) is still supported for backward compatibility:*

```
personality: casey
```

*If both `personality:` and `actors:` are present, `actors:` wins. Sync flow offers an opt-in migration from `personality:` to `actors:` at the alpha.32 upgrade.*

*Provider and model are read from the model's real-time self-knowledge when filing records. They are NOT persisted here — that would go stale the moment you switch providers or devices.*
*The hidden scribe (the protocol role that handles all filing) is implicit and has no configuration — see protocol/CORTEX.md → Hidden Scribe.*

---

## People

| Name | Who | Key Context |
|---|---|---|
| | | |

---

## Current Situation

What's going on right now that the scribe needs to know.

---

## Open Threads

- [ ] 

---

*Last updated: YYYY-MM-DD*
*Update this file in the same commit whenever people, situations, or threads change.*

---

<!-- 
SPLITTING: when any section grows large enough to be unwieldy, ask the scribe to split it out.
Sub-files follow the pattern: context-people.md, context-medical.md, context-projects.md, etc.
This file becomes the TOC — each section gets a one-liner and a link to its sub-file.
The scribe suggests splits. You decide the name and timing.
-->
