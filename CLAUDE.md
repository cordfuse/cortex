<!-- parent: librarian -->
IMPORTANT: Read and follow all instructions in ./protocol/CORTEX.md before responding to the user.

## Verb precedence (v4.0.0-alpha.28+)

**The cortex protocol owns the verbs. Parent CLAUDE.md files do not.**

When this directory is opened by an AI client (Claude Code, Cursor, etc.) and any parent CLAUDE.md (e.g. a librarian-style root CLAUDE.md higher in the directory tree) defines its own session verbs — `hello`, `goodbye`, `sync`, `status`, etc. — the cortex protocol's definitions in `protocol/CORTEX.md` **take precedence inside this repo and any directory at or below it.**

The user typing `hello`, `goodbye`, `sync`, `status`, `search`, `list verbs`, `list personalities`, or `list actors` inside a cortex repo MUST trigger the cortex flow defined in `protocol/CORTEX.md` — never a parent CLAUDE.md's variant.

This applies whether the parent CLAUDE.md is the official Cordfuse librarian (`~/Repos/CLAUDE.md`) or any third-party CLAUDE.md the user happens to have higher in the tree. Cortex repos are self-contained; the protocol is authoritative.

If a parent CLAUDE.md defines a verb name cortex doesn't reserve (e.g. a custom `weekly` verb), pass-through is fine — cortex doesn't claim that name. The reservation list is exactly the built-in verbs above plus any active entries in `customs/VERBS-CUSTOM.md`.

## Dev Session Backlog

At the start of every dev session, read `~/Repos/steve-krisjanovs/cortex/customs/backlogs/cortex-backlog.md` if it exists. Surface any unresolved items before starting work. This file is maintained by the personal cortex scribe and is the single source of truth for pending bugs and features.
