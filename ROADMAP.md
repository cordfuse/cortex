# Cortex — Roadmap

What's shipped, what's in progress, and what's coming.

**Current version:** 4.0.0-alpha.1 — [Changelog](cortex-changelog.md)

---

## Shipped

### v4.0.0-alpha.1 — Phase 1: Hidden Scribe Separation *(current)*

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

### v4.0.0 — Multi-Actor Sessions *(major, in progress)*

Phased delivery. Phase 1 ships as v4.0.0-alpha.1 (see Shipped above). Subsequent phases roll out as alpha/beta releases until v4.0.0 stable.

- [x] **Phase 1 — Hidden scribe separation** *(shipped v4.0.0-alpha.1, 2026-04-26)* — protocol role split from active actor; conceptual foundation for the rest of v4.
- [ ] **Phase 2 — Multi-actor sessions** *(next)* — spawn named actors mid-session in plain English (*"Hey Oscar, join us"*). Each actor carries their full personality profile. Multiple named actors in the room simultaneously.
- [ ] **Phase 3 — Panel vs Independent modes** — Panel: single inference context, model co-generates all actor responses in one pass, actors may build on each other's context. Independent: subagents, each actor receives the same input with no shared context. Triggered explicitly (*"blind panel:"*).
- [ ] **Phase 4 — Hot-swap, actor response headers, mid-session protocol reload** — *"switch to Sherlock"* changes active actor immediately (no next-hello deferral). Every named actor response opens with `**[Name]** — YYYY-MM-DD HH:MM TZ`. `sync` mid-session reloads protocol rules immediately, not at next hello.
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
