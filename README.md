# Cortex

[![Version](https://img.shields.io/badge/version-3.4.0-blue)](cortex-changelog.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Donate to CAMH](https://img.shields.io/badge/Donate-CAMH%20Foundation-blue)](https://camhfoundation.ca/donate)

**Not a developer?** [Read the plain English version →](README-SIMPLE.md)

**Your AI remembers everything. You own the records.**

Every AI chat starts from zero — you re-explain your life every single session. Cortex fixes that. Talk to your AI scribe, it files everything into a private git repo you own. Next session, it reads your records and picks up where you left off. Any device. Any major AI. Nothing sent to Cordfuse.

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

**The AI is a scribe, not a product.** It listens, organises, and files. It follows a protocol you can read and modify. No upsell, no monetised insights, no lock-in.

**Context that carries.** At session start the scribe reads your recent records. It knows what you were working through, what's unresolved, what patterns have been building. Every session picks up where the last one left off.

**Always in sync.** Every `hello` checks that your local repo is up to date before the session starts. Works across as many devices as you have.

**Your scribe has a personality.** 33 built-in personalities — from Bob (warm, funny, plain English) to Sherlock (precise, methodical) to Dr. Quinn (psychologist listening style) to Lama (Buddhist equanimity). Switch with one line. Create your own in plain English. [Full personality reference →](docs/PERSONALITIES.md)

**Extensible.** Built-in session commands. Define your own in `VERBS.md` — `/weekly`, `/bills`, `/checkin`, anything you want.

**Analysis on demand.** Ask the scribe to look across your records and tell you what it sees. Patterns, connections, escalations, progress.

**Private by default, offline if you need it.** Run fully local with Ollama and a self-hosted git server. Nothing leaves your machine.

---

## Personalities

Your scribe has a personality. Cortex ships with **33 built-in personalities** — switch between them with one line in `context.md`. Bob is the default.

| Category | Personalities |
|---|---|
| **Defaults** | Bob (warm, funny, plain English), Sherlock (precise, methodical, technical) |
| **General** | TARS, Oscar, Claire, Riff, Alex, Sage, Harper, Max, Ivy, Bishop, Nova, Marlowe, Ziggy, Reed, Cleo, Finn, Rowan, Dante |
| **Clinical & wellness** | Dr. Morgan (psychiatrist style), Dr. Quinn (psychologist style), Jordan (wellness coach), Arnold (fitness) |
| **Faith traditions** | Rabbi, Pastor, Father Thomas, Imam, Swami, Lama, Granthi, Daoist, Elder |

Every personality has tunable sliders across vibe, virtues, vices, soft skills, and hard skills — all 0–100. Create your own with a description. The scribe writes the file and commits it.

**Hard rule:** personalities control tone and language only. GUARDRAILS, ROE, and crisis protocol are never overridden. The voice changes. The values don't.

```
# context.md
personality: bob       ← change this to switch
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

Define your own in `VERBS.md` with a `/` prefix:

| Verb | What it does |
|---|---|
| `/personality [name]` | Switch active personality (takes effect at next `hello`) |
| `/actor [name]` | Alias for `/personality` — fully interchangeable |
| `/weekly` | Weekly review across all records |
| `/daily` | Open a daily log entry |
| `/bills` | Review upcoming bills |
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
  PERSONALITY-CASUAL.md        # Bob (default)
  PERSONALITY-VERBOSE.md       # Sherlock (opt-in)
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
- **Gemini web and mobile are not supported.** Gemini's web and mobile interfaces do not support the tool-calling and file access flow Cortex requires. Gemini CLI works fine.
- For offline: [Ollama](https://ollama.com) + self-hosted git

---

## Roadmap

[→ Full roadmap](ROADMAP.md)

**v3.4.0 (current)** — Personality system: 33 built-in personalities, tunable trait sliders, inheritance, clinical and faith tradition voices.

**Coming:** integrations expansion (Notion, Slack, GitHub, Linear, Health, Spotify), setup wizard, egress proxy, federation, and v4.0.0 multi-actor sessions.

---

## Licence

MIT — see [LICENSE](LICENSE). Nothing here constitutes medical, psychiatric, legal advice, or crisis intervention.

---

<sub>Built by [Steve Krisjanovs](https://github.com/steve-krisjanovs) · [Cordfuse](https://github.com/cordfuse)</sub>
