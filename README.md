# Cortex

[![Donate to CAMH](https://img.shields.io/badge/Donate-CAMH%20Foundation-blue)](https://camhfoundation.ca/donate)

**Not a developer?** [Read the plain English version →](README-simple.md)

**Your AI remembers everything. You own the records.**

Every AI chat starts from zero — you re-explain your life every single session. Cortex fixes that. Talk to your AI scribe, it files everything into a private git repo you own. Next session, it reads your records and picks up where you left off. Any device. Any major AI. Nothing sent to Cordfuse.

**Cloud** (GitHub + Claude/ChatGPT): frontier models, five-minute setup, smarter responses. Your records pass through your AI provider's servers.  
**Local** (Ollama + self-hosted git): nothing leaves your machine. Ever. Total privacy, more technical setup.

> **Read [protocol/DISCLAIMER.md](protocol/DISCLAIMER.md) before you start. Seriously.**

---

## Why this exists

I built Cortex because I kept losing the thread.

Every new doctor, every new therapist, every crisis worker — you start from zero. You re-explain your history, your medications, your patterns, your people. The context that took years to build evaporates between appointments. Every AI conversation is the same — it doesn't know you, and it never will unless you tell it again.

For most things that's annoying. For mental health it's dangerous. The people who most need continuity are the ones least likely to get it.

Cortex is a small fix to a big problem. You own your records. Your AI picks up where you left off. Nothing disappears.

If this has been useful to you — or if you just believe mental health infrastructure deserves better — consider donating to [CAMH Foundation](https://camhfoundation.ca/donate), Canada's largest mental health hospital and research centre. That's where I'd put the money.

— Steve Krisjanovs, Ontario, Canada

---

## The problem

Your life happens across a hundred apps — none of them talk to each other, none of them are yours, and none of them have any idea who you are.

Notes rot in silos. Health records disappear when you switch providers. Work logs don't connect to personal patterns. Therapy insights evaporate between sessions. Every AI conversation starts from zero.

Existing tools are either too simple, too clinical, or too locked-in — and the AI tools that could help process your most sensitive records on servers you don't control, under privacy policies you didn't write.

---

## What Cortex does differently

**You own everything.** Records live in your private git repository — not a vendor's database. Plain markdown. Readable by any tool, forever. Portable the day you want out.

**The AI is a scribe, not a product.** It listens, organises, and files. It follows a protocol you can read and modify. No upsell, no monetised insights, no lock-in.

**Context that carries.** At session start the scribe reads your recent records. It knows what you were working through, what's unresolved, what patterns have been building. Every session picks up where the last one left off.

**Always in sync.** Every `hello` checks that your local repo is up to date before the session starts. Works across as many devices as you have.

**Extensible.** Built-in session commands. Define your own in `VERBS.md` — `/weekly`, `/bills`, `/checkin`, anything you want.

**Analysis on demand.** Ask the scribe to look across your records and tell you what it sees. Patterns, connections, escalations, progress — the kind of insight that only emerges when everything is in one place.

**Private by default, offline if you need it.** Run fully local with Ollama and a self-hosted git server. Nothing leaves your machine.

---

## Solo or collaborative

Cortex works for one person. It also works for any number of people sharing a repo.

Clone the same repo, run your own AI agent against it, commit your entries. Everyone pushes, everyone pulls, everyone sees the full record. Git handles the collaboration. The AI handles the scribing.

A couple's shared health journal. A team's decision log. A band's creative sessions. A family's care record. A startup's retrospectives. Any group that needs a shared, AI-scribed, permanent record — owned by the group, not a platform.

Each person can use a different AI. One uses Claude, another uses ChatGPT, another uses Qwen. Same repo. Same protocol. Same truth.

---

## Getting started

**[→ Desktop setup](docs/setup-desktop.md)** — agent CLI, Claude Desktop, any OS  
**[→ Mobile & web setup](docs/setup-mobile.md)** — Claude project, ChatGPT project  

Both guides cover new users and existing Cortex repos.

---

## Session commands

| Verb | What it does |
|---|---|
| `hello` | Open session — sync, scan open items, greet |
| `goodbye` | Close session — commit pending, push, surface unresolved |
| `status` | Last session, open items, uncommitted files, vault |
| `sync` | Pull + push mid-session |
| `search [term]` | Search all records |
| `list verbs` | Show built-in and custom verbs |

Define your own in `VERBS.md` with a `/` prefix — `/weekly`, `/bills`, `/checkin`.

---

## Connect anything

Cortex ships with an AES-256 encrypted secrets vault — one file per secret, committed to your repo, safe because everything is encrypted. One passphrase governs everything.

**[→ Full connector reference](docs/connectors.md)**

| Connector | Status |
|---|---|
| **Tailscale** | Built — mesh VPN, reach home network from anywhere |
| **rclone** | Built — any filesystem, 70+ backends |
| **Google** | Built — Calendar, Gmail, Drive, Tasks, Contacts |
| **Microsoft 365** | Built — Mail, Calendar, OneDrive, Teams, and more |
| Notion, iCloud, Slack, GitHub, Linear, Health, Spotify, Banking | Roadmap |

---

## What it covers

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
protocol/           # Protocol engine — do not edit
records/            # Your dated entries
attachments/        # One subfolder per record
docs/               # Source documents + setup guides
templates/          # Blank templates
scripts/            # Setup, vault, integrations
cortex.secrets/     # Encrypted vault (committed, safe)
  vault.json        # Key index — names, descriptions, rotation date
install.sh          # Pipe installer — Linux/macOS (curl | bash)
install.ps1         # Pipe installer — Windows (iex irm)
setup.sh            # Re-run setup after already cloned — Linux/macOS
setup.ps1           # Re-run setup after already cloned — Windows
VERBS.md            # Your custom session verbs
```

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
- For offline: [Ollama](https://ollama.com) + self-hosted git

---

## Licence

MIT — see [LICENSE](LICENSE). Nothing here constitutes medical, psychiatric, legal advice, or crisis intervention.

---

<sub>Built by [Steve Krisjanovs](https://github.com/steve-krisjanovs) · [Cordfuse](https://github.com/cordfuse)</sub>
