# Cortex

[![Version](https://img.shields.io/badge/version-4.0.0--alpha.22-blue)](CORTEX-CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Donate to CAMH](https://img.shields.io/badge/Donate-CAMH%20Foundation-blue)](https://camhfoundation.ca/donate)

**Not a developer?** [Read the plain English version →](README-SIMPLE.md)

> ⚠️ **Framework files — do not edit.** This file and all linked docs are overwritten when the framework updates. Put your personal notes in the `-CUSTOM.md` companions instead — they follow the same pattern as `VERBS-CUSTOM.md` and `ROE-CUSTOM.md` and are never touched by the framework.
>
> | Your notes | Framework doc |
> |---|---|
> | [README-CUSTOM.md](README-CUSTOM.md) | This file |
> | [docs/PERSONALITIES-CUSTOM.md](docs/PERSONALITIES-CUSTOM.md) | [docs/PERSONALITIES.md](docs/PERSONALITIES.md) |
> | [docs/CONNECTORS-CUSTOM.md](docs/CONNECTORS-CUSTOM.md) | [docs/CONNECTORS.md](docs/CONNECTORS.md) |

**Your AI remembers everything. You own the records.**

Every AI chat starts from zero — you re-explain your life every single session. Cortex fixes that. Talk to your AI scribe, it files everything into a private git repo you own. Next session, it reads your records and picks up where you left off. Any device. Any major AI. Nothing sent to Cordfuse.

---

## ⚠️ Permissions are wide-open by default — and that's deliberate

Cortex ships with `.claude/settings.json` carrying a comprehensive allow-list (`Read`, `Edit`, `Write`, `Glob`, `Grep`, `Bash(*)`, `WebSearch`, `WebFetch`). **Claude Code will run every tool call the cortex hello flow needs without per-prompt approval.** Other CLI agents in scope (Codex CLI, Gemini CLI, OpenCode, Qwen Code, GitHub Copilot CLI) have their own auto-accept flags — see each agent's docs for the equivalent.

**Why:** the cortex value proposition depends on the scribe being able to read records, write files, run git commands, and execute integrations without per-prompt friction. Per-call approval would make every session unusable. The protocol files in `protocol/` (`CORTEX.md`, `GUARDRAILS.md`, `ROE.md`, `DISCLAIMER.md`) define what the scribe is allowed to do — those rules are LLM-enforced. There is no second OS-level safety layer.

**Trust model:** you trust the protocol; the scribe complies with the protocol; Claude Code does not gate the scribe.

**Why an allow-list, not bypass mode:** Anthropic's `bypassPermissions` mode triggers a one-time *"do you accept the risk"* confirmation that's loud, scary, and would unnecessarily intimidate first-time users. The comprehensive allow-list achieves the same friction-free outcome by pre-approving each tool the cortex flow uses — Claude Code stays in its default safety mode, just with no prompts because everything cortex calls is on the list.

**If you want per-prompt approval back:** delete or rename `.claude/settings.json`. Claude Code falls back to its default per-prompt gating. Expect every read, write, and bash call to prompt — the scribe's hello flow alone will trigger 10+ approvals before the greeting renders.

**On other agents:** Codex CLI uses `--full-auto`, Gemini CLI has its own approval mode, and so on. None of those settings are git-tracked here yet — file an issue if you want a particular agent's auto-approve config shipped as a default.

### Framework files are protected at the OS layer (v4.0.0-alpha.16+)

`.claude/settings.json` ships with a comprehensive `deny` list covering every framework file: `protocol/`, `templates/`, `scripts/*.py`, `version.txt`, `.cortex-version`, `LICENSE`, `CORTEX-CHANGELOG.md`, `ROADMAP.md`, `README.md`, `README-SIMPLE.md`, `VERBS.md`, the install/setup scripts, and `.claude/settings.json` itself.

**Agent pointer files are intentionally NOT in the deny list.** `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `OPENCODE.md`, `QWEN.md` exist as one-line pointers to `protocol/CORTEX.md` — but users customize them with personal blocks below the pointer (per-project session backlogs, per-host instructions, etc.). They're user-territory in user clones, even though they ship with the framework.

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
| **CLI agents** (Claude Code, Gemini CLI, OpenCode, Qwen, Codex) | Yes | **Yes — full connector functionality** |
| **Self-hosted / cron / scheduled scripts** on your machine | Yes | **Yes — full connector functionality** |
| **Claude Cowork / Dispatch** (cloud Claude Code dispatched from Claude.ai) | Yes | **Yes — but Cowork is flaky and unfinished. Hung tooling calls are common. Out of cortex's control. Treat as experimental.** |
| **Claude.ai web and mobile** (Free/Pro/Max) | Yes | **NO. Sandbox blocks all third-party APIs.** |
| **ChatGPT web and mobile** | Yes | **NO. Sandbox has zero outbound network.** |
| **Gemini web and mobile** | Not supported (no tool-call file access) | N/A |

**On Claude.ai and ChatGPT web/mobile, cortex can ONLY do git operations — clone, read your records, commit, push, merge.** Every connector script (`scripts/integrations/google.py`, `microsoft.py`, `tailscale.py`, `rclone.py`) will fail at the network proxy. **There is no API access. None at all.** This is by design on Anthropic's and OpenAI's side — their sandboxes only allow specific package-registry domains (GitHub, PyPI, npm). Cortex cannot work around this.

**For full connector functionality on a phone or tablet:** [AgentBox](https://github.com/cordfuse/agentbox) — Cordfuse's local-agent-with-PWA-UI app — is the planned answer. **AgentBox is in planning stage; not yet built.** Until it ships, connectors run from a CLI agent on your laptop, scheduled scripts on a home server, or Claude Cowork / Dispatch (with the flakiness caveat above).

---

## Navigation

| | |
|---|---|
| [Why this exists](#why-this-exists) | [Getting started](#getting-started) |
| [What it does differently](#what-cortex-does-differently) | [Session commands](#session-commands) |
| [Personalities →](docs/PERSONALITIES.md) | [Connectors →](docs/CONNECTORS.md) |
| [Roadmap →](ROADMAP.md) | [Changelog →](CORTEX-CHANGELOG.md) |
| [Desktop setup →](docs/SETUP-DESKTOP.md) | [Mobile setup →](docs/SETUP-MOBILE.md) |

---

## Why this exists

I built Cortex because I kept losing the thread.

Every new doctor, every new therapist, every crisis worker — you start from zero. You re-explain your history, your medications, your patterns, your people. The context that took years to build evaporates between appointments. Every AI conversation is the same — it doesn't know you, and it never will unless you tell it again.

For most things that's annoying. For mental health it's dangerous. The people who most need continuity are the ones least likely to get it.

Cortex is a small fix to a big problem. You own your records. Your AI picks up where you left off. Nothing disappears.

If this has been useful to you — or if you just believe mental health infrastructure deserves better — consider donating to [CAMH Foundation](https://camhfoundation.ca/donate), Canada's largest mental health hospital and research centre.

— Steve Krisjanovs

---

## What Cortex does differently

**You own everything.** Records live in your private git repository — not a vendor's database. Plain markdown. Readable by any tool, forever. Portable the day you want out.

**Three AI layers, not a product.** A **Bootstrap actor** runs the operational layer (sync, version checks, scoped session verbs) in clinical voice; an **active actor** (Casey, Atlas, Magnus, etc.) handles conversation; a **hidden scribe** files everything underneath, silently. All three follow a protocol you can read and modify. No upsell, no monetised insights, no lock-in. *(See [docs/PERSONALITIES.md](docs/PERSONALITIES.md) for the full active-actor + hidden-scribe split shipped in v4.0.0-alpha.1, and the operational/conversational mode split shipped in v4.0.0-alpha.20.)*

**Context that carries.** At session start the scribe reads your recent records. It knows what you were working through, what's unresolved, what patterns have been building. Every session picks up where the last one left off.

**Always in sync.** Every `hello` runs `git fetch origin` and `git fetch upstream` before the greeting renders. Local behind remote? Scribe surfaces the delta and applies your `auto_upgrade:` preference (always / ask / never). Silent stale-state operation is a protocol violation as of v4.0.0-alpha.13.

**Hot-swap personalities mid-session (v4.0.0-alpha.8+).** Say *"change actor to Atlas"* and the next response is in Atlas's voice. No fresh hello required.

**Multi-session state isolation (v4.0.0-alpha.17+).** `spawn session "phase 2 design"` creates a scoped session at `sessions/{guid}/`. `engage session` swaps in any time. `close session` archives. The default ("main session" / singleton) is shared across every chat that doesn't explicitly spawn a scoped one. Test isolation, parallel work threads, and cross-machine continuity all work cleanly.

**Multi-parent personality inheritance (v4.0.0-alpha.11+).** Custom personalities can inherit from multiple parents simultaneously — useful for "everything-guy" SMEs who span developer + infrastructure + cloud architect + functional consultant in one role.

**Your active actor has a personality.** 73 built-in personalities — from Casey (warm, funny, plain English) to Atlas (precise, methodical) to Dr. Quinn (psychologist) to Yoda to Magnus the Business Central SME. Switch with one line. Create your own in plain English. [Full personality reference →](docs/PERSONALITIES.md)

**Extensible.** Built-in session commands. Define your own in `VERBS.md` — `weekly review`, `bills`, `checkin`, anything you want. **Natural language only — no slash prefixes** (Claude web and other clients hijack `/`).

**Analysis on demand.** Ask the scribe to look across your records and tell you what it sees. Patterns, connections, escalations, progress.

**Private by default, offline if you need it.** Run fully local with Ollama and a self-hosted git server. Nothing leaves your machine.

---

## Personalities

Your active actor has a personality. Cortex ships with **73 built-in personalities** plus the **Bootstrap actor** that handles operational reporting. Switch active actors with one line in `context.md`, or in plain English: *"change actor to Atlas."* See the full reference for descriptions and trait sliders.

| Category | Personalities |
|---|---|
| **Bootstrap** | Bootstrap (auto-loaded; never user-selected; clinical operational voice) |
| **Workplace** | Alex, Bishop, Max |
| **Creative & Visionary** | Harper, Ziggy, Nova |
| **Wisdom & Reflection** | Sage, Ivy, Rowan, Dante |
| **Distinctive Voices** | Casey (warm, plain English), Atlas (precise, methodical), Riff, Marlowe, Reed, Cleo, Finn, Claire |
| **Information Technology** | Devon (Tech Lead), Kai (Junior Dev), Riley (DevOps), Knox (Infrastructure), Vega (Cloud Architect), Avery (PM), Sloane (QA), Orion (UX/UI), Drew (Functional Consultant) |
| **Clinical & wellness** | Dr. Morgan (psychiatrist), Dr. Quinn (psychologist), Jordan (wellness), Dr. Walsh (family doctor), Dr. Mira (registered dietitian, she/her) |
| **Faith traditions** | Rabbi, Pastor, Father Thomas, Imam, Swami, Lama, Granthi, Daoist, Elder |
| **Mindfulness & Stoicism** | Mindfulness Teacher, Marcus (Stoic philosopher) |
| **Recovery & Peer Support** | AA Sponsor, SAA Sponsor |
| **Family & Friends** | Mama, Pop, Terry (best friend) |
| **Pop Culture** | TARS, Arnold Schwarzenegger, Mr. Miyagi, John Kreese, Bruce Lee, Chuck Norris, Jean-Claude Van Damme, Sylvester Stallone, Hulk Hogan, Bob Ross, Mr. Rogers, Doc Brown, Yoda, Spock, Robin Williams, Han Solo, The Dude, Indiana Jones, Captain Jean-Luc Picard, Buffy Summers, Bill Murray, Angus MacGyver, Lieutenant Columbo, Tony Soprano |

Every personality has tunable sliders across vibe, virtues, vices, soft skills, and hard skills — all 0–100. Create your own with a description. The scribe writes the file and commits it.

**Hard rule:** personalities control tone and language only. GUARDRAILS, ROE, and crisis protocol are never overridden. The voice changes. The values don't.

```
# context.md
personality: casey       ← change this to switch (or leave blank — Bootstrap will ask you to pick)
provider: Anthropic Claude
model: claude-sonnet-4-6
```

[Full personality reference →](docs/PERSONALITIES.md)

---

## Getting started

**[→ Desktop setup](docs/SETUP-DESKTOP.md)** — agent CLI, Claude Desktop, any OS
**[→ Mobile & web setup](docs/SETUP-MOBILE.md)** — Claude project, ChatGPT project

Both guides cover new users and existing Cortex repos.

---

## Session commands

### Built-in verbs

| Verb | What it does |
|---|---|
| `hello` | Open session — Bootstrap runs Gate 3, sync check, scans open items, then user-chosen actor greets |
| `goodbye` | Close session — commit pending, push, surface unresolved |
| `status` | Last session, open items, uncommitted files, vault |
| `sync` | Pull framework updates from upstream + apply (Bootstrap voice) |
| `reconcile` | Deep three-category drift resolution against upstream/main with per-file user gating (v4.0.0-alpha.19+) |
| `search [term]` | Search all records |
| `list verbs` | Show built-in and custom verbs |
| `list personalities` / `list actors` | Show active personality and all available |
| `spawn session "<name>"` | Create scoped session (v4.0.0-alpha.17+) |
| `list sessions [filter]` | Show all sessions with state metadata |
| `engage session "<name>"` | Attach to existing session (v4.0.0-alpha.18+) |
| `close session "<name>"` | Archive a session (v4.0.0-alpha.18+) |

### Custom verbs

Define your own in `VERBS.md`. Invoke by name in natural language — no slash prefix:

| Verb | What it does |
|---|---|
| `change actor to <name>` | Hot-swap active personality (takes effect immediately, next response). Aliases: *switch personality*, *use [name]*. (v4.0.0-alpha.8+) |
| `weekly review` | Weekly review across all records |
| `daily log` | Open a daily log entry |
| `bills` | Review upcoming bills |
| *...and any verb you define* | |

---

## Connect anything

Cortex ships with an AES-256 encrypted secrets vault. One passphrase governs everything.

**[→ Full connector reference](docs/CONNECTORS.md)**

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
protocol/              # Protocol engine — do not edit
  CORTEX.md            # Session rules, personality system, multi-session, time resolution
  DISCLAIMER.md        # Honest framing, legal warnings, crisis resources
  GUARDRAILS.md        # Hard stops, safety rules — overrides everything (alpha.7+ Gate 3 enforced)
  ROE.md               # Rules of engagement (Rule 18: framework files read-only)
  CORTEX-PROJECT.md    # Self-contained prompt for Claude/ChatGPT projects
personalities/         # Personality files (73 framework + your customs)
  PERSONALITY-BOOTSTRAP.md     # Bootstrap (operational voice, auto-loaded)
  PERSONALITY-CASUAL.md        # Casey
  PERSONALITY-VERBOSE.md       # Atlas
  PERSONALITY-[NAME].md        # 70 additional framework personalities
  PERSONALITY-CUSTOM-*.md      # Your custom personalities
records/               # Your dated entries — one file per topic per commit
sessions/              # Scoped sessions (v4.0.0-alpha.17+); each is a folder with its own context.md
attachments/           # One subfolder per record
archive/               # Closed sessions, archived records, deprecated framework files
docs/                  # Source documents + setup guides
  PERSONALITIES.md     # Full personality reference
  CONNECTORS.md        # Connector reference
  SETUP-DESKTOP.md     # Desktop setup guide
  SETUP-MOBILE.md      # Mobile setup guide
templates/             # Blank templates
install/               # Bootstrap installers + setup scripts (v4.0.0-alpha.22+)
  install.sh           # macOS / Linux installer (also published as a release asset)
  install.ps1          # Windows installer (also published as a release asset)
  setup.sh             # macOS / Linux per-machine setup
  setup.ps1            # Windows per-machine setup
scripts/               # Vault tooling + integrations (Python)
.claude/               # Claude Code settings (allow-list + framework deny-list)
  settings.json        # Shipped with framework
  settings.local.json  # Optional contributor override (gitignored)
CLAUDE.md              # Claude Code + Claude Desktop
GEMINI.md              # Gemini CLI
AGENTS.md              # OpenAI Codex + GitHub Copilot CLI + generic agents
OPENCODE.md            # OpenCode
QWEN.md                # Qwen Code
context.md             # Singleton ("main session") state — personality, provider, model
SECRETS.md             # Plain-text index of vault key names (no values)
VERBS.md               # Framework verbs
VERBS-CUSTOM.md        # Your custom verbs
ROADMAP.md             # What's shipped and what's coming
CORTEX-CHANGELOG.md    # Full change log
.cortex-version        # Current framework version (user clones)
version.txt            # Current framework version (framework dev only)
```

---

## Solo or collaborative

Cortex works for one person. It also works for any number of people sharing a repo.

Clone the same repo, run your own AI agent against it, commit your entries. Everyone pushes, everyone pulls, everyone sees the full record. Git handles the collaboration. The AI handles the scribing.

Each person can use a different AI. One uses Claude, another uses ChatGPT, another uses Qwen. Same repo. Same protocol. Same truth.

---

## Cross-agent coordination (CNAC)

Multi-agent workflows over the same repo are supported via what we call **Cortex-Native Agent Coordination (CNAC)**: agents on different machines or different providers coordinate by writing records to the cortex repo. One agent files a test plan as a record; another agent reads it, executes, and files results back as a record. No copy-paste, no separate message bus, full audit trail. The bus is git. The messages are records.

Validated empirically with end-to-end Phase 6 testing in 2026-04-30 — Claude Opus on cachy filed a test plan, Claude Sonnet on mobile read it, executed all 8 steps, filed consolidated results back. Cross-provider, cross-machine, cross-session.

---

## Cloud vs offline

**Cloud:** GitHub + Claude/ChatGPT. Five-minute setup. Frontier models. Tradeoff: records pass through your AI provider.

**Offline:** self-hosted git ([Gitea](https://gitea.io) / [Forgejo](https://forgejo.org)) + [Ollama](https://ollama.com). Nothing leaves your machine. Tradeoff: harder setup, weaker instruction-following.

Guardrails apply in both modes.

---

## Guardrails

`protocol/GUARDRAILS.md` governs the scribe: crisis situations, intent to harm, crime disclosure, child safety, jailbreak attempts, and sandbox integrity. The scribe refuses to start if it's missing.

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

- Git + Python 3.9+
- An AI agent ([Claude Code](https://claude.ai/download), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [OpenCode](https://opencode.ai), Codex CLI, Qwen Code) or web interface (claude.ai, ChatGPT)
- **Model recommendation: Claude Sonnet, or a mid-tier GPT equivalent.** Validated on Claude Sonnet — clean startup, fast, follows the silent-load protocol correctly. Claude Opus is more capable but more verbose at session start and slower. GPT-4o is untested; GPT-4o-mini is likely the right tier for the same reason (less narration, faster). Frontier/largest models are not always better for Cortex — instruction-following on the bootstrap rules matters more than raw capability.
- **Session startup is verbose — this is expected and cannot be suppressed.** When you open a new chat and say `hello`, the AI reads your protocol files, runs Gate 3 (`git fetch origin` + version check), and runs an opening scan before greeting you. You will see tool-call activity during this process. This is the AI doing its job — not an error. The greeting itself is clean. The loading activity is a limitation of how AI providers expose tool use in their interfaces and is outside Cordfuse's control. AgentBox (planned) is the long-term verbosity fix.
- **Gemini web and mobile are not supported.** Gemini's web and mobile interfaces do not support the tool-calling and file access flow Cortex requires. Gemini CLI works fine.
- **ChatGPT compatibility is untested.** The protocol is designed to be provider-agnostic but has been primarily validated on Claude. ChatGPT may behave differently — reports welcome.
- For offline: [Ollama](https://ollama.com) + self-hosted git

---

## Roadmap

[→ Full roadmap](ROADMAP.md)

**v4.0.0-alpha.21 (current)** — Documentation alignment pass: README + interlinked docs brought to current alpha.20 reality. Personality count corrected to 73. Information Technology domain (alpha.12), Pop Culture additions (alpha.10), Bootstrap actor + Dr. Mira (alpha.20) all reflected. Canonical category map in `protocol/CORTEX.md` updated.

**Recent shipped (v4 sprint):** alpha.7 (Bootstrap RWDX guardrail) → alpha.8 (personality hot-swap) → alpha.9 (response headers, compression-resilience) → alpha.10 (Pop Culture +7) → alpha.11 (multi-parent inheritance) → alpha.12 (Information Technology domain +9) → alpha.13 (bootstrap reliability patches) → alpha.14 (`.claude/settings.json` allow-list) → alpha.15 (sync flow hardening) → alpha.16 (CC deny-list) → **alpha.17 + alpha.18 (Phase 6 multi-session sessions)** → alpha.19 (`reconcile` verb) → alpha.20 (Bootstrap actor + Dr. Mira + Operational/Conversational mode) → alpha.21 (this docs alignment).

**Coming:** Phase 2 multi-actor sessions (spawn named actors mid-session, multiple voices in the same session), Phase 3 panel vs independent modes, integrations expansion (Notion, Slack, GitHub, Linear, Health, Spotify), AgentBox v1.0 (PWA wrapping CLI agents), MTX (markdown package manager).

---

## Licence

MIT — see [LICENSE](LICENSE). Nothing here constitutes medical, psychiatric, legal advice, or crisis intervention.

---

<sub>Built by [Steve Krisjanovs](https://github.com/steve-krisjanovs) · [Cordfuse](https://github.com/cordfuse)</sub>
