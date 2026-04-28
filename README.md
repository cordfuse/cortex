# Cortex

[![Version](https://img.shields.io/badge/version-4.0.0--alpha.15-blue)](cortex-changelog.md)
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
| [Roadmap →](ROADMAP.md) | [Changelog →](cortex-changelog.md) |
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

**The AI is two layers, not a product.** A named active actor (Casey, Atlas, etc.) listens and talks. A hidden scribe files everything underneath, silently. Both follow a protocol you can read and modify. No upsell, no monetised insights, no lock-in. *(See [docs/PERSONALITIES.md](docs/PERSONALITIES.md) for the full active-actor + hidden-scribe split shipped in v4.0.0-alpha.1.)*

**Context that carries.** At session start the scribe reads your recent records. It knows what you were working through, what's unresolved, what patterns have been building. Every session picks up where the last one left off.

**Always in sync.** Every `hello` checks that your local repo is up to date before the session starts. Works across as many devices as you have.

**Your active actor has a personality.** 55 built-in personalities — from Casey (warm, funny, plain English) to Atlas (precise, methodical) to Dr. Quinn (psychologist listening style) to Lama (Buddhist equanimity). Switch with one line. Create your own in plain English. [Full personality reference →](docs/PERSONALITIES.md) *(The hidden scribe — the protocol role that handles filing — is separate and has no personality. See [Hidden Scribe](protocol/CORTEX.md#hidden-scribe).)*

**Extensible.** Built-in session commands. Define your own in `VERBS.md` — `weekly review`, `bills`, `checkin`, anything you want. **Natural language only — no slash prefixes** (Claude web and other clients hijack `/`).

**Analysis on demand.** Ask the scribe to look across your records and tell you what it sees. Patterns, connections, escalations, progress.

**Private by default, offline if you need it.** Run fully local with Ollama and a self-hosted git server. Nothing leaves your machine.

---

## Personalities

Your active actor has a personality. Cortex ships with **55 built-in personalities** — switch between them with one line in `context.md`. Casey is the default. (The hidden scribe is separate — see [Hidden Scribe](protocol/CORTEX.md#hidden-scribe).)

| Category | Personalities |
|---|---|
| **Defaults** | Casey (warm, funny, plain English), Atlas (precise, methodical, technical) |
| **Workplace** | Alex, Bishop, Max |
| **Creative & Visionary** | Harper, Ziggy, Nova |
| **Wisdom & Reflection** | Sage, Ivy, Rowan, Dante |
| **Distinctive Voices** | Riff, Marlowe, Reed, Cleo, Finn, Claire |
| **Clinical & wellness** | Dr. Morgan (psychiatrist), Dr. Quinn (psychologist), Jordan (wellness), Dr. Walsh (family doctor) |
| **Faith traditions** | Rabbi, Pastor, Father Thomas, Imam, Swami, Lama, Granthi, Daoist, Elder |
| **Mindfulness & Stoicism** | Mindfulness Teacher, Marcus (Stoic philosopher) |
| **Recovery & Peer Support** | AA Sponsor, SAA Sponsor |
| **Family & Friends** | Mama, Pop, Terry (best friend) |
| **Pop Culture** | TARS, Arnold Schwarzenegger, Mr. Miyagi, John Kreese, Bruce Lee, Chuck Norris, Jean-Claude Van Damme, Sylvester Stallone, Hulk Hogan, Bob Ross, Mr. Rogers, Doc Brown, Yoda, Spock, Robin Williams, Han Solo, The Dude |

Every personality has tunable sliders across vibe, virtues, vices, soft skills, and hard skills — all 0–100. Create your own with a description. The scribe writes the file and commits it.

**Hard rule:** personalities control tone and language only. GUARDRAILS, ROE, and crisis protocol are never overridden. The voice changes. The values don't.

```
# context.md
personality: casey       ← change this to switch
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
| `hello` | Open session — sync check, scan open items, load personality, greet |
| `goodbye` | Close session — commit pending, push, surface unresolved |
| `status` | Last session, open items, uncommitted files, vault |
| `sync` | Pull + push mid-session |
| `search [term]` | Search all records |
| `list verbs` | Show built-in and custom verbs |
| `list personalities` | Show active personality and all available |
| `list actors` | Alias for `list personalities` |

### Custom verbs

Define your own in `VERBS.md`. Invoke by name in natural language — no slash prefix:

| Verb | What it does |
|---|---|
| `switch personality to [name]` | Hot-swap active personality (takes effect immediately, next response). Aliases: *change actor*, *use [name]* |
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
| Notion, Slack, GitHub, Linear | Roadmap v3.5.0 |
| Apple Health, Spotify, Banking | Roadmap v3.5.0 |
| Plex, Jellyfin | Roadmap v3.5.0 |
| 1Password, Bitwarden | Roadmap v3.5.0 |

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
  CORTEX.md            # Session rules, personality system, time resolution
  DISCLAIMER.md        # Honest framing, legal warnings, crisis resources
  GUARDRAILS.md        # Hard stops, safety rules — overrides everything
  ROE.md               # 20 rules of engagement
  CORTEX-PROJECT.md    # Self-contained prompt for Claude/ChatGPT projects
personalities/         # Personality files
  PERSONALITY-CASUAL.md        # Casey (default)
  PERSONALITY-VERBOSE.md       # Atlas (opt-in)
  PERSONALITY-[NAME].md        # 31 additional built-ins
  PERSONALITY-CUSTOM-*.md      # Your custom personalities
records/               # Your dated entries — one file per topic per commit
attachments/           # One subfolder per record
docs/                  # Source documents + setup guides
  PERSONALITIES.md     # Full personality reference
  CONNECTORS.md        # Connector reference
  SETUP-DESKTOP.md     # Desktop setup guide
  SETUP-MOBILE.md      # Mobile setup guide
templates/             # Blank templates
scripts/               # Setup, vault, integrations
CLAUDE.md              # Claude Code + Claude Desktop
GEMINI.md              # Gemini CLI
AGENTS.md              # OpenAI Codex + generic agents
OPENCODE.md            # OpenCode
QWEN.md                # Qwen Code
context.md             # Your session context — personality, people, situation
SECRETS.md             # Plain-text index of vault key names (no values)
VERBS.md               # Framework verbs
VERBS-CUSTOM.md        # Your custom verbs
ROADMAP.md             # What's shipped and what's coming
cortex-changelog.md    # Full change log
version.txt            # Current framework version
```

---

## Solo or collaborative

Cortex works for one person. It also works for any number of people sharing a repo.

Clone the same repo, run your own AI agent against it, commit your entries. Everyone pushes, everyone pulls, everyone sees the full record. Git handles the collaboration. The AI handles the scribing.

Each person can use a different AI. One uses Claude, another uses ChatGPT, another uses Qwen. Same repo. Same protocol. Same truth.

---

## Cloud vs offline

**Cloud:** GitHub + Claude/ChatGPT. Five-minute setup. Frontier models. Tradeoff: records pass through your AI provider.

**Offline:** self-hosted git ([Gitea](https://gitea.io) / [Forgejo](https://forgejo.org)) + [Ollama](https://ollama.com). Nothing leaves your machine. Tradeoff: harder setup, weaker instruction-following.

Guardrails apply in both modes.

---

## Guardrails

`protocol/GUARDRAILS.md` governs the scribe: crisis situations, intent to harm, crime disclosure, child safety, jailbreak attempts, and sandbox integrity. The scribe refuses to start if it's missing.

**Remove or modify it and you are on your own. Cordfuse accepts zero liability.**

---

## Privacy

- Cordfuse has no access to your records
- No telemetry, no analytics, no data collection
- Git history is immutable — deleted files remain in history
- A private hosted repo can be subpoenaed — run offline if this matters

---

## Requirements

- Git + Python 3.9+
- An AI agent ([Claude Code](https://claude.ai/download), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [OpenCode](https://opencode.ai)) or web interface (claude.ai, ChatGPT)
- **Model recommendation: Claude Sonnet, or a mid-tier GPT equivalent.** Validated on Claude Sonnet — clean startup, fast, follows the silent-load protocol correctly. Claude Opus is more capable but more verbose at session start and slower. GPT-4o is untested; GPT-4o-mini is likely the right tier for the same reason (less narration, faster). Frontier/largest models are not always better for Cortex — instruction-following on the silent-load rule matters more than raw capability.
- **Session startup is verbose — this is expected and cannot be suppressed.** When you open a new chat and say `hello`, the AI reads your protocol files, checks your repo state, and runs an opening scan before greeting you. You will see tool-call activity during this process. This is the AI doing its job — not an error. The greeting itself is clean. The loading activity is a limitation of how AI providers expose tool use in their interfaces and is outside Cordfuse's control.
- **Gemini web and mobile are not supported.** Gemini's web and mobile interfaces do not support the tool-calling and file access flow Cortex requires. Gemini CLI works fine.
- **ChatGPT compatibility is untested.** The protocol is designed to be provider-agnostic but has only been validated on Claude to date. ChatGPT may behave differently — reports welcome.
- For offline: [Ollama](https://ollama.com) + self-hosted git

---

## Roadmap

[→ Full roadmap](ROADMAP.md)

**v4.0.0-alpha.5 (current)** — Multi-actor architecture (Phase 1: Hidden Scribe Separation) + personality system expanded to 47 built-ins across Defaults / General / Clinical / Faith / Pop Culture, with optional `## domain` field for custom-personality grouping and `## aliases` for invocation flexibility.

**Coming:** v4 phases 2-5 (multi-actor sessions, panel vs independent modes, hot-swap, list actors expansion), integrations expansion (Notion, Slack, GitHub, Linear, Health, Spotify), setup wizard, egress proxy, federation.

---

## Licence

MIT — see [LICENSE](LICENSE). Nothing here constitutes medical, psychiatric, legal advice, or crisis intervention.

---

<sub>Built by [Steve Krisjanovs](https://github.com/steve-krisjanovs) · [Cordfuse](https://github.com/cordfuse)</sub>
