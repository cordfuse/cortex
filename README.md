# Cortex

[![Version](https://img.shields.io/badge/version-4.16.7-blue)](manifest/framework/CORTEX-CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Support CAMH](https://img.shields.io/badge/support-CAMH%20Foundation-e4002b)](https://camhfoundation.ca/donate)

> **Your AI forgets you every session.** Cortex is a private git repo your AI reads at the start of every conversation — so it remembers your context, files what matters as you talk, and connects it all together automatically. Any device, any major AI. **You own the memory; you rent the intelligence.**

**Not a developer?** [Read the plain-English version →](README-SIMPLE.md)

## The problem

Every AI chat starts from zero. You re-explain your context, your projects, your preferences — every single session. The AI is capable but amnesiac. You end up doing the same setup work over and over, and the AI never gets smarter about *you*.

## The solution

Cortex is a private git repo your AI scribe reads at the start of every session. It files your records as you talk, tracks your threads, and **automatically links related records together** — so your history becomes a connected web instead of a flat pile, and the scribe follows the thread instead of re-searching it. Next session it picks up where you left off, any device, any major AI.

**You own everything.** It's plain markdown in your own git repo — no vendor database, no server in the middle, readable by any tool, portable the day you want out. The model is rented; the memory is yours. Move from one frontier AI to the next and your second brain comes with you.

**63 ready-made actors ship with the framework** — engineers, doctors, advisors, creative voices, spiritual guides — with **Apex** (a precise generalist) as the default. Build your own in plain English in `manifest/custom/actors/`; custom actors are never overwritten by framework updates.

---

## Using this repo

**Create your own:** tap the green **Use this template** button on GitHub — it's there on both web and mobile — to make your own cortex. Or run `gh repo create my-cortex --template cordfuse/cortex` from a terminal.

> ⚠️ **Framework files — do not edit.** This file and all linked docs are overwritten when the framework updates. Put your personal notes in `manifest/custom/` instead — files like `manifest/custom/VERBS.md`, `manifest/custom/protocol/ROE.md`, and `manifest/custom/protocol/GUARDRAILS.md` are never touched.
>
> | Your notes | Framework doc |
> |---|---|
> | [manifest/custom/README.md](manifest/custom/README.md) | This file |
> | [manifest/custom/actors/](manifest/custom/actors/) | [manifest/framework/PERSONALITIES.md](manifest/framework/PERSONALITIES.md) |
> | [manifest/custom/VERBS.md](manifest/custom/VERBS.md) | [manifest/framework/VERBS.md](manifest/framework/VERBS.md) |

---

## ⚠️ Permissions are wide-open by default — and that's deliberate

Cortex ships with `.claude/settings.json` carrying a comprehensive allow-list (`Read`, `Edit`, `Write`, `Glob`, `Grep`, `Bash(*)`, `WebSearch`, `WebFetch`). **Claude Code will run every tool call the cortex hello flow needs without per-prompt approval.** Other CLI agents in scope (Codex CLI, Gemini CLI, Antigravity CLI, OpenCode, Qwen Code, GitHub Copilot CLI) have their own auto-accept flags — see each agent's docs for the equivalent.

**Why:** the cortex value proposition depends on the scribe being able to read records, write files, run git commands, and execute integrations without per-prompt friction. Per-call approval would make every session unusable. The protocol files in `manifest/framework/protocol/` (`CORTEX.md`, `GUARDRAILS.md`, `ROE.md`, `DISCLAIMER.md`) define what the scribe is allowed to do — those rules are LLM-enforced. There is no second OS-level safety layer.

**Trust model:** you trust the protocol; the scribe complies with the protocol; Claude Code does not gate the scribe.

**Why an allow-list, not bypass mode:** Anthropic's `bypassPermissions` mode triggers a one-time *"do you accept the risk"* confirmation that's loud, scary, and would unnecessarily intimidate first-time users. The comprehensive allow-list achieves the same friction-free outcome by pre-approving each tool the cortex flow uses — Claude Code stays in its default safety mode, just with no prompts because everything cortex calls is on the list.

**If you want per-prompt approval back:** delete or rename `.claude/settings.json`. Claude Code falls back to its default per-prompt gating. Expect every read, write, and bash call to prompt — the scribe's hello flow alone will trigger 10+ approvals before the greeting renders.

**On other agents:** Codex CLI uses `--full-auto`, Gemini CLI has its own approval mode, and so on. None of those settings are git-tracked here yet — file an issue if you want a particular agent's auto-approve config shipped as a default.

### Framework files are protected at the OS layer (v4.0.0-alpha.16+)

`.claude/settings.json` ships with a comprehensive `deny` list covering every framework file: `manifest/framework/protocol/`, `manifest/framework/templates/`, `manifest/framework/scripts/*.ts`, `version.txt`, `.cortex-version`, `LICENSE`, `ROADMAP.md`, `README.md`, `README-SIMPLE.md`, `manifest/framework/CORTEX-CHANGELOG.md`, `manifest/framework/VERBS.md`, `manifest/framework/CORTEX-DEV.md`, the install/setup scripts, and `.claude/settings.json` itself.

**Agent pointer files are intentionally NOT in the deny list.** `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `ANTIGRAVITY.md`, `OPENCODE.md`, `QWEN.md` exist as one-line pointers to `manifest/framework/protocol/CORTEX.md` — but users customize them with personal blocks below the pointer (per-project session backlogs, per-host instructions, etc.). They're user-territory in user clones, even though they ship with the framework.

**Why:** ROE Rule 18 already says framework files are read-only for the scribe (LLM-enforced). The `deny` list operationalizes the same rule at the tool layer (OS-enforced). Defense in depth — even if the scribe's LLM compliance drifts, the tool layer holds. Framework files only mutate via the sync flow's `git checkout upstream/main` (a `Bash(*)` call), which IS allowed and which IS the correct path for framework changes.

**Framework contributors:** if you're working on Cortex itself (modifying protocol files, shipping new alpha releases, etc.), the deny list will block you. Create a local override:

```json
// .claude/settings.local.json (gitignored — your local override)
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "deny": []
  }
}
```

`.claude/settings.local.json` is in `.gitignore`, so your local override never gets committed. Claude Code merges both files at session start with the local override winning. Without this override, contributing to framework files becomes friction-heavy.

This is the same pattern used in `cordfuse/ironbound`. Lifted directly.

---

## What works where — read this first

Cortex behaves **differently** depending on where you run it. The difference is hard, not soft, and it's not a configuration issue — it's the platforms.

| Environment | Git operations (clone, read, commit, push, merge) | Third-party APIs (Google, Microsoft 365, Notion, Slack, Spotify, etc.) |
|---|---|---|
| **CLI agents** (Claude Code, Gemini CLI, Antigravity CLI, OpenCode, Qwen, Codex) | Yes | **Yes — full connector functionality** |
| **Self-hosted / cron / scheduled scripts** on your machine | Yes | **Yes — full connector functionality** |
| **Claude Cowork / Dispatch** (cloud Claude Code dispatched from Claude.ai) | Yes | **Yes — but Cowork is flaky and unfinished. Hung tooling calls are common. Out of cortex's control. Treat as experimental.** |
| **Claude.ai web and mobile** (Free/Pro/Max) | Yes | **NO. Sandbox blocks all third-party APIs.** |
| **ChatGPT web and mobile** | **No — sandbox cannot resolve github.com at all (verified 2026-07-20). Not supported.** | **NO.** |
| **Gemini web and mobile** | Not supported (no tool-call file access) | N/A |

**On Claude.ai web/mobile, cortex can ONLY do git operations — clone, read your records, commit, push, merge.** Connector scripts will fail at the network proxy. **There is no third-party API access. None at all.** This is by design on Anthropic's and OpenAI's side — their sandboxes only allow specific package-registry domains. Cortex cannot work around this.

**For full connector functionality on a phone or tablet:** connectors run from a CLI agent on your laptop, scheduled scripts on a home server, or Claude Cowork / Dispatch (with the flakiness caveat above).

**On UX verbosity:** CLI agents (Claude Code, Gemini CLI, Antigravity CLI, OpenCode, Qwen) are the least verbose session experience — no tool-call accordion UI, scribe reads files directly, and the user sees only the curated greeting. Web project mode on claude.ai has inherent startup verbosity (file-listing UI, tool-call expansions) that Cordfuse cannot suppress — that's the AI provider's UI, not a cortex protocol issue. If a clean, quiet session is the goal, run cortex from a CLI agent.

---

## Navigation

| | |
|---|---|
| [Why this exists](#why-this-exists) | [Getting started](#getting-started) |
| [What it does differently](#what-cortex-does-differently) | [Session commands](#session-commands) |
| [Personalities →](manifest/framework/PERSONALITIES.md) | [Connectors →](manifest/framework/CONNECTORS.md) |
| [Roadmap →](ROADMAP.md) | [Changelog →](manifest/framework/CORTEX-CHANGELOG.md) |
| [Desktop setup →](manifest/framework/SETUP-DESKTOP.md) | [Mobile setup →](manifest/framework/SETUP-MOBILE.md) |

---

## Why this exists

Start a new chat with any AI and you're a stranger again. It has no memory of who you are, what you're working on, or what you told it last time. You can scroll back to an old conversation — but nothing carries forward into a new one, and it can't connect the dots across them. Every time, from scratch.

I built Cortex because I needed it to *not* work like that. My own memory isn't something I can always rely on, so starting over from scratch isn't a small annoyance for me — it's the actual problem. I wanted something that remembers for me, that I own, that doesn't disappear between conversations.

That's all it is. Your records live in your own repo. Your AI reads them at the start of every chat and picks up where you left off. Nothing gets lost.

If Cortex has been useful to you, consider donating to [CAMH Foundation](https://camhfoundation.ca/donate) — that's where this started.

<a href="https://camhfoundation.ca/donate"><img src="assets/camh-logo.png" alt="Support CAMH Foundation" height="40"></a>

— Steve Krisjanovs

---

## What Cortex does differently

**You own everything.** Records live in your private git repository — not a vendor's database. Plain markdown. Readable by any tool, forever. Portable the day you want out.

**Three AI layers, not a product.** A **Bootstrap actor** runs the operational layer (sync, version checks, scoped session verbs) in clinical voice; an **active actor** (Apex, or any custom personality you create) handles conversation; a **hidden scribe** files everything underneath, silently. All three follow a protocol you can read and modify. No upsell, no monetised insights, no lock-in. *(See [manifest/framework/PERSONALITIES.md](manifest/framework/PERSONALITIES.md) for the full active-actor + hidden-scribe split shipped in v4.0.0-alpha.1, and the operational/conversational mode split shipped in v4.0.0-alpha.20.)*

**Context that carries.** At session start the scribe reads your recent records. It knows what you were working through, what's unresolved, what patterns have been building. Every session picks up where the last one left off.

**Onboarding that adapts to you (v4.14.0+).** A fresh cortex doesn't dump you into a blank vault — on the first session it asks what you want cortex *for* (personal life · work · creative practice · research · health · finances) and only asks about what fits. A professional cortex never asks about your family; a health cortex never asks about deadlines. Pick more than one, or skip it and just start. Sensitive tiers (health, mood) are always opt-in and delicately gated — and everything is *recorded, never advised*.

**A connected record, not a pile (v4.15.0+).** Every new record gets a `## Related` block of `[[wikilinks]]` to the records it continues or touches, and the `weave` verb backfills the whole vault. The scribe follows threads instead of re-searching them — and graph tools (Obsidian, Logseq, Foam) light up for free.

**Always in sync.** Every `hello` runs `git fetch origin` and `git fetch upstream` before the greeting renders. Local behind remote? Scribe surfaces the delta and applies your `auto_upgrade:` preference (always / ask / never). Silent stale-state operation is a protocol violation as of v4.0.0-alpha.13.

**Hot-swap personalities mid-session (v4.0.0-alpha.8+).** Say *"change actor to [name]"* and the next response is in that actor's voice. No fresh hello required.

**Multi-session state isolation (v4.0.0-alpha.17+).** `spawn session "phase 2 design"` creates a scoped session at `data/sessions/{guid}/`. `engage session` swaps in any time. `close session` archives. The default ("main session" / singleton) is shared across every chat that doesn't explicitly spawn a scoped one. Test isolation, parallel work threads, and cross-machine continuity all work cleanly.

**Multi-parent personality inheritance (v4.0.0-alpha.11+).** Custom personalities can inherit from multiple parents simultaneously — useful for "everything-guy" SMEs who span developer + infrastructure + cloud architect + functional consultant in one role.

**Your active actor has a personality.** 63 ship ready-made — from `senior-software-engineer` to `family-doctor` to `stoic-philosopher` — with **Apex** as the generic default. Build your own in plain English and commit them to `manifest/custom/actors/`. Credit your work with an `## author` field. [Full personality reference →](manifest/framework/PERSONALITIES.md)

**Natural language intent routing (v4.5.0+).** Say "sync me up" or "what's the status?" — the scribe classifies intent before matching verb shorthand. No need to remember exact command names; natural phrasing works throughout.

**Actor selection at hello (v4.5.1+).** Bootstrap always presents an actor-selection dialog at session start. Name an actor in your opening message to skip the dialog — otherwise pick from the list. Available sessions surface in the same prompt so you can re-engage and pick actors in one turn.

**Extensible.** Built-in session commands. Define your own in `manifest/custom/VERBS.md` — `weekly review`, `bills`, `checkin`, anything you want. **Natural language only — no slash prefixes** (Claude web and other clients hijack `/`).

**Analysis on demand.** Ask the scribe to look across your records and tell you what it sees. Patterns, connections, escalations, progress.

**Private by default, offline if you need it.** Run fully local with Ollama and a self-hosted git server. Nothing leaves your machine.

---

## Personalities

Cortex ships with **63 framework actors** plus the **Bootstrap actor** that handles operational reporting.

| Category | Actors |
|---|---|
| **Bootstrap** | Bootstrap (auto-loaded; never user-selected; clinical operational voice) |
| **Default** | Apex (`precise-generalist`) — generic, precise, no domain specialty |
| **Framework roster (63)** | Engineering (`senior-software-engineer`, `devops-engineer`, `cloud-architect`, …), health (`family-doctor`, `clinical-psychiatrist`, `registered-dietitian`, …), advisory (`financial-planner`, `legal-advisor`, `executive-coach`, …), creative (`creative-director`, `songwriter`, …), philosophy & faith (`stoic-philosopher`, `buddhist-guide`, and guides across major traditions), voices (`minimalist-voice`, `plain-language-voice`, …) — say `list actors` for the full set |
| **Custom** | Any actor file in `manifest/custom/actors/` |

Framework actors sync from [`cordfuse/agent-assets`](https://github.com/cordfuse/agent-assets). Custom actors are never overwritten by framework sync. Add an `## author` field to credit yourself or anyone you're sharing with.

Every personality has tunable sliders across vibe, virtues, vices, soft skills, and hard skills — all 0–100. Create your own with a description. The scribe writes the file and commits it.

**Hard rule:** personalities control tone and language only. GUARDRAILS, ROE, and crisis protocol are never overridden. The voice changes. The values don't.

```
# context.md
actors: []               ← Bootstrap always prompts — name an actor in your opening message to skip the dialog
provider: Anthropic Claude
model: claude-opus-4-8
```

[Full personality reference →](manifest/framework/PERSONALITIES.md)

---

## Getting started

**[→ Desktop setup](manifest/framework/SETUP-DESKTOP.md)** — agent CLI, Claude Desktop, any OS
**[→ Mobile & web setup](manifest/framework/SETUP-MOBILE.md)** — Claude project (web/mobile is Claude-only)

Both guides cover new users and existing Cortex repos.

**Web/mobile auth (v4.16.0+):** on Claude, no tokens needed — install the [Personal Cortex GitHub App](https://github.com/apps/personal-cortex) on your repo once, and each session authenticates via GitHub's device flow (approve on your phone, ~10 seconds; nothing secret stored anywhere). Validated on Opus 4.8, Sonnet 5, and Fable 5. A fine-grained PAT remains the fallback.

---

## Session commands

### Built-in verbs

| Verb | What it does |
|---|---|
| `hello` | Open session — Bootstrap runs Gate 3, sync check, scans open items, then prompts for actor selection (or activates named actor from opening message) (v4.5.1+) |
| `goodbye` | Close session — commit pending, push, surface unresolved |
| `status` | Last session, open items, uncommitted files, vault |
| `sync` | Pull framework updates from upstream + apply (Bootstrap voice) |
| `reconcile` | Deep three-category drift resolution against upstream/main with per-file user gating (v4.0.0-alpha.19+) |
| `search [term]` | Search all records |
| `weave` | Backfill `[[wikilink]]` cross-links across existing records (v4.15.0+) |
| `morning` | Daily briefing — appointments, open items, heads-up |
| `patterns` | Cross-record pattern analysis |
| `handoff` | Compile a clinician/professional summary from your records |
| `help` | Replay the first-run overview |
| `list verbs` | Show built-in and custom verbs |
| `list personalities` / `list actors` | Show active personality and all available |
| `spawn session "<name>"` | Create scoped session (v4.0.0-alpha.17+) |
| `list sessions [filter]` | Show all sessions with state metadata |
| `engage session "<name>"` | Attach to existing session (v4.0.0-alpha.18+) |
| `close session "<name>"` | Archive a session (v4.0.0-alpha.18+) |
| `rename session "<old>" "<new>"` | Rename a session; GUID stays, past records keep their label (v4.16.7+) |

### Custom verbs

Define your own in `manifest/custom/VERBS.md`. Invoke by name in natural language — no slash prefix:

| Verb | What it does |
|---|---|
| `change actor to <name>` | Hot-swap active personality (takes effect immediately, next response). Aliases: *switch personality*, *use [name]*. (v4.0.0-alpha.8+) |
| `weekly review` | Weekly review across all records |
| `meds` | Log medications taken today |
| `therapy` | Log a therapy or counselling session |
| *...and any verb you define* | |

---

## Connect anything

Cortex ships with an AES-256 encrypted secrets vault. One passphrase governs everything.

**[→ Full connector reference](manifest/framework/CONNECTORS.md)**

| Connector | Status |
|---|---|
| **Tailscale** | Built — mesh VPN, reach home network from anywhere |
| **rclone** | Built — any filesystem, 70+ backends |
| **Google** | Built — Calendar, Gmail, Drive, Tasks, Contacts |
| **Microsoft 365** | Built — Mail, Calendar, OneDrive, Teams, SharePoint, To Do, Planner, OneNote |
| Notion, Slack, GitHub, Linear | Roadmap |
| Apple Health, Spotify, Banking | Roadmap |
| Plex, Jellyfin | Roadmap |
| 1Password, Bitwarden | Roadmap |

---

## Templates

19 templates across every domain worth recording:

| Category | Templates |
|---|---|
| Personal | daily log, event, person, theory/insight |
| Health | therapy session, medication, symptoms, appointment |
| Life admin | finance, inventory, supplies, tasks |
| Work | work log, project, career |
| Creative | idea, creative session |
| Analytical | analysis, review |

---

## Repo structure

```
manifest/
  framework/           # Ships with the framework -- overwritten on sync
    protocol/          # Protocol engine -- do not edit
      CORTEX.md        # Session rules, personality system, multi-session, time resolution
      GUARDRAILS.md    # Hard stops, safety rules -- overrides everything
      ROE.md           # Rules of engagement
      DISCLAIMER.md    # Honest framing, legal warnings, crisis resources
      CORTEX-PROJECT.md  # Self-contained prompt for Claude projects
    templates/         # Record skeletons + install scaffolding
    actors/            # 63 built-in actors (precise-generalist "Apex" = default)
    BOOTSTRAP.md       # Operational scribe voice (auto-loaded)
    VERBS.md           # Framework verbs (managed by scribe)
    PERSONALITIES.md   # Full personality reference
    CONNECTORS.md      # Connector reference
    SETUP-DESKTOP.md
    SETUP-MOBILE.md
    CORTEX-CHANGELOG.md
    CORTEX-DEV.md
    scripts/           # Environment-aware tools (setup, healthcheck, secrets, etc.)
      integrations/    # Connector scripts
  custom/              # User territory -- never synced from upstream
    protocol/          # User protocol overrides
      ROE.md           # Custom rules of engagement
      GUARDRAILS.md    # Custom guardrails extensions
    templates/         # User template overrides (optional)
    actors/            # Custom actors
    VERBS.md           # Custom verbs + overrides
    README.md          # Personal notes about this instance
    PERSONALITIES.md   # Notes on personalities + custom actors
    CONNECTORS.md      # Personal connector setup notes
    cortex-upgrade.md  # Auto-upgrade preferences
data/records/               # Dated entries -- one file per topic per commit
data/attachments/           # Source documents + record attachments
  YYYY-MM-DD-HHMM-[slug]/   # Record-specific attachments
  YYYY-MM-DD-[provider]-[type].[ext]  # Standalone source docs
  assets/              # Shared static assets
archive/               # Retired files -- read only on explicit request
install/               # Bootstrap installers + setup scripts
.claude/               # Claude Code settings
CLAUDE.md              # Claude Code + Claude Desktop
GEMINI.md              # Gemini CLI (sunset 2026-06-18 — use ANTIGRAVITY.md)
ANTIGRAVITY.md         # Antigravity CLI (Gemini CLI successor)
AGENTS.md              # OpenAI Codex + generic agents
OPENCODE.md            # OpenCode
QWEN.md                # Qwen Code
context.md             # Main session state -- actor, provider, model
SECRETS.md             # Plain-text index of vault key names (no values)
ROADMAP.md             # What's shipped and what's coming
.cortex-version        # Current framework version (user clones)
version.txt            # Current framework version (framework dev only)
```

---

## One cortex per access boundary, not per topic

A common first instinct is to set up multiple cortexes — one for health, one for programming, one for business, one for family. **Don't.** That instinct reproduces the exact problem cortex exists to solve.

Cortex was built because every new professional handoff and every new AI conversation re-starts from zero. The continuity loss is the pain. Splitting your own cortex by topic re-creates that loss internally — the scribe can't see your sleep patterns alongside your project deadlines if those records live in separate repos.

**The rule:** split cortexes by **access boundary**, not by **topic**.

If two pieces of information have the same audience (just you, or you + spouse, or you + a co-founder), they belong in the same cortex. Topic separation is what the personality system and Phase 6 multi-session sessions are for, not what separate repos are for.

### When monocortex is right (most users)

- Solo individuals managing their whole life — health, work, family, ideas, finances, recovery, all in one
- Couples sharing household management
- Solo creators integrating projects + personal life
- Anyone who built cortex to escape the lost-context problem

### When multiple cortexes are justified

Only when **access boundaries** demand it:

- **Employer or client IP separation** — paid work under contract that legally can't mix with personal records
- **Compliance-regulated professional records** — lawyer with client privilege, therapist with HIPAA-equivalent obligations, doctor with patient charts. The pro records legally can't mix with personal life
- **Multi-stakeholder teams with role-based visibility** — e.g., a startup where engineering's cortex shouldn't include founder-level financials
- **Public-creator + private-personal** — separate audiences require separate repos

In all of these the boundary is **who can see what**, not **what is it about**.

### Topic separation without fragmenting the record

Within a monocortex, topic context is handled by:

- **Personalities** — `change actor to family-doctor` for health mode; `change actor to senior-software-engineer` for engineering; `change actor to financial-planner` for money. The voice + lens shifts naturally.
- **Phase 6 scoped sessions** — `spawn session "phase 2 design"` keeps a programming sprint's runtime state isolated from main; `spawn session "weekly checkin"` keeps a health journal's actor and context separate. Records still file to the unified `data/records/` folder with `Session: phase 2 design` in provenance, so cross-domain searches still work.
- **Records folder** — naturally chronological + searchable across all topics

You get the cognitive separation without losing the integrating layer.

---

## Solo or collaborative

Cortex works for one person. It also works for any number of people sharing a repo.

Clone the same repo, run your own AI agent against it, commit your entries. Everyone pushes, everyone pulls, everyone sees the full record. Git handles the collaboration. The AI handles the scribing.

Each person can use a different AI. One uses Claude, another uses Codex, another uses Qwen. Same repo. Same protocol. Same truth.

---

## Cross-agent coordination (CNAC)

Multi-agent workflows over the same repo are supported via what we call **Cortex-Native Agent Coordination (CNAC)**: agents on different machines or different providers coordinate by writing records to the cortex repo. One agent files a test plan as a record; another agent reads it, executes, and files results back as a record. No copy-paste, no separate message bus, full audit trail. The bus is git. The messages are records.

Validated empirically with end-to-end Phase 6 testing in 2026-04-30 — Claude Opus on cachy filed a test plan, Claude Sonnet on mobile read it, executed all 8 steps, filed consolidated results back. Cross-provider, cross-machine, cross-session.

---

## Cloud vs offline

**Cloud:** GitHub + Claude. Five-minute setup. Frontier models. Tradeoff: records pass through your AI provider.

**Offline:** self-hosted git ([Gitea](https://gitea.io) / [Forgejo](https://forgejo.org)) + [Ollama](https://ollama.com). Nothing leaves your machine. Tradeoff: harder setup, weaker instruction-following.

Guardrails apply in both modes.

---

## Guardrails

`manifest/framework/protocol/GUARDRAILS.md` governs the scribe: crisis situations, intent to harm, crime disclosure, child safety, jailbreak attempts, and sandbox integrity. The scribe refuses to start if it's missing.

The Bootstrap RWDX guardrail (v4.0.0-alpha.7+) blocks all read/write/delete/execute operations until bootstrap is complete (repo cloned + protocol loaded + `git fetch origin` confirms current with remote).

**Remove or modify GUARDRAILS.md and you are on your own. Cordfuse accepts zero liability.**

---

## Privacy

- Cordfuse has no access to your records
- No telemetry, no analytics, no data collection
- Git history is immutable — deleted files remain in history
- A private hosted repo can be subpoenaed — run offline if this matters

---

## Requirements

- Git
- An AI agent ([Claude Code](https://claude.ai/download), [Gemini CLI](https://github.com/google-gemini/gemini-cli) (sunset 2026-06-18 — superseded by Antigravity), [Antigravity CLI](https://github.com/google-antigravity/antigravity-cli), [OpenCode](https://opencode.ai), Codex CLI, Qwen Code) or web interface (claude.ai — the only web surface with GitHub access)
- **Model recommendation: any current Claude model.** Validated end-to-end on Opus 4.8, Sonnet 5, and Fable 5 (v4.16.0 web-auth run), and on earlier Sonnet generations throughout. On web, session start is consent-first — the scribe says what opening your vault involves and waits for your yes. For OpenAI models, use Codex CLI on desktop.
- **Session startup is verbose — this is expected and cannot be suppressed.** When you open a new chat and say `hello`, the AI reads your protocol files, runs Gate 3 (`git fetch origin` + version check), and runs an opening scan before greeting you. You will see tool-call activity during this process. This is the AI doing its job — not an error. The greeting itself is clean. The loading activity is a limitation of how AI providers expose tool use in their interfaces and is outside Cordfuse's control.
- **Gemini web and mobile are not supported.** Gemini's web and mobile interfaces do not support the tool-calling and file access flow Cortex requires. Gemini CLI works fine.
- **ChatGPT web/mobile is not supported.** Its sandbox has no network route to GitHub — `git clone` fails with `Could not resolve host: github.com` (verified 2026-07-20). OpenAI models work via **Codex CLI** on desktop; the protocol itself remains provider-agnostic.
- For offline: [Ollama](https://ollama.com) + self-hosted git

---

## Roadmap

[→ Full roadmap](ROADMAP.md)

**v4.16 (current)** — Tokenless web auth: GitHub device flow via the [Personal Cortex app](https://github.com/apps/personal-cortex) — no PATs to create or store, consent-first session open, validated on Opus 4.8 / Sonnet 5 / Fable 5. The line has since added: a **Financial** intake domain (income · obligations · assets · goals, tender tier gated); a **`rename session`** verb; a documented **custom-verb lifecycle** (deactivate/reactivate/remove); reserved-verb-name enforcement across *all* built-ins; standardised template heading conventions; and a hardening pass (secrets-vault corruption guard, rclone/tailscale credential-exposure fixes, protocol-defect cleanup). Plus earlier: ChatGPT web/mobile confirmed unsupported (sandbox has no route to GitHub), and a verb-catalog cleanup.

**v4.15** — Record Linking (Weave): automatic `[[wikilink]]` cross-links on capture + a `weave` backfill verb. The flat record becomes a navigable graph — no dead edges, hand-authored content never touched.

**v4.14** — Personal Intake: empty-vault onboarding that adapts to what you use cortex *for*. Universal core (identity, preferences) plus opt-in domain packs — personal · professional · creative · research · health · financial, multi-select; sensitive capture delicately gated, recorded-never-advised. First-run intro is one conversational beat, not a step wizard.

**Coming:** Phase 2 multi-actor sessions (spawn named actors mid-session, multiple voices in the same session), Phase 3 panel vs independent modes, integrations expansion (Notion, Slack, GitHub, Linear, Health, Spotify).

---

## Licence

MIT — see [LICENSE](LICENSE). Nothing here constitutes medical, psychiatric, legal advice, or crisis intervention.

---

<sub>Built by [Steve Krisjanovs](https://github.com/steve-krisjanovs) · [Cordfuse](https://github.com/cordfuse)</sub>
