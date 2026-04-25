# Cortex — Roadmap

What's shipped, what's in progress, and what's coming.

**Current version:** 3.4.11 — [Changelog](cortex-changelog.md)

---

## Shipped

### v3.4.11 — Provider/Model is a Runtime Property *(current)*
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
- **`list personalities` / `list actors` rendering fixed.** `## name` field verbatim (TARS not Tars, Sherlock not Verbose), canonical category grouping (Defaults / General / Clinical / Faith), deterministic output template.
- **Provenance block requires datetime + timezone.** Aligns with v3.3.0 Time Resolution and ROE Rule 17. `Filed: 2026-04-25 17:30 EDT` instead of date-only.
- **Honesty/deference clarification.** `honesty` is a virtue; `deference` is the only axis. Closes spec ambiguity.

### v3.4.0 — Personality System
- **33 built-in personalities** — Bob (default), Sherlock, + 31 library
  - Validated in 2026-04-25 test sprint: voice differentiation real (Bob vs Sherlock distinct), natural-language creation produces high-quality system prompts, archetype + sycophant warnings fire correctly, dynamic vice re-evaluation on edits
- Tunable trait model: vibe, virtues, vices, soft skills, hard skills — all percentage sliders
- Vice/virtue mirror pairs (pride↔integrity, cowardice↔courage, etc.)
- Archetype system: HARDLINER, DIPLOMAT, ANALYST, CREATIVE, LONE_WOLF, TEAM_PLAYER, JOKESTER
- Personality inheritance — custom personalities declare a parent, override only what they change
- Natural language creation — describe a personality, scribe writes the file
- Natural language tuning — "dial Oscar's sarcasm down to 40%"
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
- [ ] User personality performance notes — "Oscar was too much today"
- [ ] Blend mode — `50% Bob, 50% Sherlock` composite personality

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

### v4.0.0 — Multi-Actor Sessions *(major)*
- [ ] **Hidden scribe** — always present, never speaks, reads/writes Cortex exclusively. Separation of filing engine from conversational voice.
- [ ] **Multi-actor sessions** — spawn named actors mid-session in plain English (*"Hey Oscar, join us"*). Each actor carries their full personality profile.
- [ ] **Panel mode** — single inference context, model co-generates all actor responses in one pass. Actors may build on each other's context.
- [ ] **Independent mode** — subagents, each actor receives the same input with no shared context. True parallel independent opinions. Triggered explicitly (*"blind panel:"*).
- [ ] **`list actors`** — built-in verb showing all active actors in the session
- [ ] **Actor response headers** — every named actor response opens with `**[Name]** — YYYY-MM-DD HH:MM TZ`
- [ ] **Actor management mid-session** — add, remove, modify actors without restarting
- [ ] **Hot-swap** — `"switch to Sherlock"` changes the active conversational actor immediately
- [ ] **Personality history** — per-session record of which actors were active and when

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
