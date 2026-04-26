# context.md — Canonical Session Context

Read at every `hello`. Update in the same commit whenever people, situations, or threads change.

---

## Active Actor

personality: bob

*`personality:` (or `actor:`) — name of the active actor (the named personality the user talks to). File in `personalities/`. Bob is the default. Both spellings are accepted. Change via natural language: "use sherlock", "switch personality to sherlock", or "change actor to sherlock" — the hidden scribe updates this and commits, takes effect at next `hello`.*
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
