# Cortex

**Your AI remembers everything. You own the records.**

Every AI chat starts from zero — you re-explain your life every single session. Cortex fixes that. Talk to your AI scribe, it files everything into a private git repo you own. Next session, it reads your records and picks up where you left off. Any device. Any major AI. Nothing sent to Cordfuse.

**Cloud** (GitHub + Claude/ChatGPT): frontier models, five-minute setup, smarter responses. Your records pass through your AI provider's servers.  
**Local** (Ollama + self-hosted git): nothing leaves your machine. Ever. Total privacy, more technical setup.

> **Read [protocol/DISCLAIMER.md](protocol/DISCLAIMER.md) before you start. Seriously.**

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

## Session commands

Cortex has built-in session verbs and supports user-defined custom verbs.

### Built-in

| Verb | What it does |
|---|---|
| `hello` | Open session — syncs with remote, scans for open items, greets you |
| `goodbye` | Close session — commits everything pending, pushes, surfaces unresolved items |
| `status` | Quick health check: last session, open items, uncommitted files, vault contents |
| `sync` | Pull + push mid-session — useful when switching devices |
| `search [term]` | Search all records for a keyword |
| `list verbs` | Show all built-in and custom verbs |

### Your own verbs

Define custom session commands in `VERBS.md`. Call them with a `/` prefix — guaranteed never to conflict with built-ins.

```markdown
## /weekly
Read all records from the past 7 days. Surface patterns and open items. Ask if I want to file a summary.

## /bills
Pull my Google Calendar for due dates. Cross-reference my household-payments record. List what's due this week.
```

---

## What it covers

Cortex ships with 19 templates across every domain worth recording:

| Category | Templates |
|---|---|
| Personal | daily log, event, person, theory/insight |
| Health | therapy session, medication, symptoms, appointment |
| Life admin | finance, inventory, supplies, tasks |
| Work | work log, project, career |
| Creative | idea, creative session |
| Analytical | analysis, review |

Use what fits. Ignore what doesn't. Add your own.

---

## Connect anything

Cortex ships with an AES-256 encrypted secrets vault (`cortex.secrets/`) — one file per secret, all committed to your repo, safe because everything is encrypted. Store API keys, tokens, and credentials once. Your scribe retrieves them on demand and pulls data from any connected service directly into your records.

The vault is managed by a single passphrase. `cortex.secrets/vault.json` is a plain-text manifest listing all key names and descriptions — so the scribe always knows what's available without decrypting anything.

```bash
python scripts/secrets.py store <name> --description "what this is"   # store a secret
python scripts/secrets.py list                                          # show all key names
python scripts/secrets.py get <name>                                    # retrieve a value
python scripts/secrets.py delete <name>                                 # remove (with confirmation)
python scripts/secrets.py repassphrase                                  # rotate the global passphrase
```

### Tailscale — reach your home network from anywhere

Cortex integrates with [Tailscale](https://tailscale.com) so you can reach your home server, NAS, or desktop from any device over a private mesh VPN.

```bash
python scripts/integrations/tailscale.py auth      # store your auth key in the vault
python scripts/integrations/tailscale.py up        # connect to Tailscale
python scripts/integrations/tailscale.py peers     # list connected devices + IPs
python scripts/integrations/tailscale.py ip <host> # get a peer's Tailscale IP
```

### rclone — any filesystem, anywhere

Cortex integrates with [rclone](https://rclone.org) to pull from and push to any filesystem — NAS, cloud storage, SFTP, or local drives. Config is stored in the vault, never on disk unencrypted.

```bash
python scripts/integrations/rclone.py auth               # store rclone config in vault
python scripts/integrations/rclone.py remotes            # list configured remotes
python scripts/integrations/rclone.py ls <remote:path>   # list files
python scripts/integrations/rclone.py pull <remote:path> # pull files to docs/
python scripts/integrations/rclone.py push <remote:path> # push files to remote
python scripts/integrations/rclone.py mount <remote:path> # mount remote as local filesystem
```

### Google (Calendar, Gmail, Drive, Tasks, Contacts)

```bash
python scripts/integrations/google.py auth        # one-time setup
python scripts/integrations/google.py calendar --days 7
python scripts/integrations/google.py gmail --count 20
python scripts/integrations/google.py drive --count 20
python scripts/integrations/google.py tasks
python scripts/integrations/google.py contacts
```

### Microsoft 365 (Mail, Calendar, OneDrive, Teams, SharePoint, To Do, Planner, OneNote)

```bash
python scripts/integrations/microsoft.py auth     # one-time setup
python scripts/integrations/microsoft.py mail
python scripts/integrations/microsoft.py calendar --days 7
python scripts/integrations/microsoft.py onedrive
python scripts/integrations/microsoft.py teams
python scripts/integrations/microsoft.py sharepoint
python scripts/integrations/microsoft.py todo
python scripts/integrations/microsoft.py planner
python scripts/integrations/microsoft.py onenote
```

> **Google Keep is not listed.** Google has never released a public API for Keep.

---

## Repo structure

```
protocol/                    # Protocol engine — do not edit
  CORTEX.md                  # Session flow, file naming, integrations
  GUARDRAILS.md              # Hard stops and safety rules — overrides everything
  ROE.md                     # Rules of engagement
  DISCLAIMER.md              # Honest framing and legal warnings
records/                     # Your dated entries — YYYY-MM-DD-HHMM-[slug].md
attachments/                 # Attachments — one subfolder per record
docs/                        # Source documents — bills, invoices, screenshots, PDFs
templates/                   # Blank templates
examples/                    # Anonymised example entries
scripts/                     # Setup, vault, healthcheck
  setup.py                   # Environment setup + system dependency installer
  secrets.py                 # Vault management (store, get, list, delete, repassphrase)
  integrations/
    tailscale.py             # Tailscale mesh VPN connector
    rclone.py                # rclone filesystem connector
    google.py                # Google services
    microsoft.py             # Microsoft 365 services
cortex.secrets/              # Encrypted vault — one .enc file per secret (committed, safe)
  vault.json                 # Plain-text manifest: key names, descriptions, rotation date
setup.sh                     # Bootstrap — Linux/macOS (installs Python, git, deps)
setup.ps1                    # Bootstrap — Windows
VERBS.md                     # Your custom session verbs (/ prefix)
```

---

## Getting started

### Desktop

**1. Create your repo**

Click **[Use this template](../../generate)** on GitHub. Name your repo. Set it **private**. Create it.

**2. Clone and run setup**

```bash
git clone git@github.com:you/your-repo-name.git
cd your-repo-name
bash setup.sh        # Linux/macOS — installs dependencies, writes cortex.config
.\setup.ps1          # Windows
```

**3. Open it in your AI agent**

```bash
claude    # Claude Code (CLI)
gemini    # Gemini CLI
opencode  # OpenCode
qwen      # Qwen Code
```

Not a developer? **Claude Desktop** ([claude.ai/download](https://claude.ai/download)) is the easiest entry point — open the app, add your repo as a project, no terminal needed.

**4. Start**

Say `hello`. The scribe takes it from there.

---

### Mobile (Claude or ChatGPT project)

> **Note:** Gemini web and mobile do not support the project + tool-calling flow required by Cortex. Use Claude or ChatGPT on mobile.

Set up once — every new chat opens a session automatically.

**1. Create your GitHub repo**

Click **[Use this template](../../generate)** on GitHub. Name it. Set it **private**. Create it.

**2. Generate a GitHub PAT**

GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token.

- Repository access: your Cortex repo only
- Permissions: Contents → Read and write

Copy the token — starts with `github_pat_`. You only see it once.

**3. Create a Claude or ChatGPT project**

- **System prompt:** open `protocol/CORTEX-PROJECT.md` in your repo and paste its contents
- **Project knowledge:** add a file with your repo URL and PAT (never commit this file)

**4. Open a new chat in the project**

Say `hello`. The scribe clones your repo and picks up where you left off.

---

### Returning sessions

**Desktop:** `cd your-repo && claude` — say `hello`.

**Mobile:** open a new chat in your Cortex project.

---

### Updating

`setup.py` adds an upstream remote automatically. Pull protocol and script updates when a new version ships.

```bash
git fetch upstream
git checkout upstream/main -- protocol/ templates/ scripts/ setup.sh setup.ps1
git commit -m "sync: cortex vX.X.X"
```

Your `records/`, `attachments/`, `docs/`, and `cortex.secrets/` are never touched. Only protocol files, templates, and scripts are updated.

---

## Cloud vs offline

### Cloud (default)

**Git:** GitHub, GitLab.com, or any hosted provider.  
**AI:** Claude, Gemini, ChatGPT, or any hosted agent.

- Five-minute setup, syncs across devices automatically
- Frontier models follow guardrails most reliably
- **Tradeoff:** Your AI provider processes your records under their privacy policy. Your git host can be subpoenaed.

### Offline / self-hosted

**Git:** Local repo, or self-hosted [Gitea](https://gitea.io) / [Forgejo](https://forgejo.org) / [GitLab CE](https://gitlab.com/oss/packages).  
**AI:** [Ollama](https://ollama.com) running a local model with tool calling.

- Nothing leaves your machine. Works air-gapped.
- **Tradeoff:** Harder to set up. Local LLMs are weaker at instruction-following — guardrails apply but reliability varies.

**Guardrails apply in both modes. Privacy and reliability pull in opposite directions — choose your tradeoff consciously.**

---

## Guardrails

Cortex ships with `protocol/GUARDRAILS.md` — hard stops covering crisis situations, intent to harm, crime disclosure, child safety, and jailbreak attempts.

The sandbox whitelist in GUARDRAILS permits git operations against trusted remotes and repo-internal scripts. Unknown remotes prompt confirmation before being added to the whitelist.

**If you remove or modify `protocol/GUARDRAILS.md`, the scribe operates without any of these protections. Cordfuse accepts zero liability for the consequences.**

The scribe will refuse to start if `protocol/GUARDRAILS.md` or `protocol/DISCLAIMER.md` is missing.

---

## Privacy

- Cordfuse has no access to your records
- No telemetry, no analytics, no data collection of any kind
- Your repo is yours — private, portable, permanent
- Git history is immutable — deleting a file does not remove it from commit history
- A private hosted repository can be subpoenaed — if this matters to you, run offline

---

## Requirements

- Git
- Python 3.9+
- An AI agent CLI ([Claude Code](https://claude.ai/download), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [OpenCode](https://opencode.ai)) — or a web interface (claude.ai, ChatGPT)
- For offline: [Ollama](https://ollama.com) and a self-hosted git server

---

## Licence

MIT — see [LICENSE](LICENSE).

This protocol is provided as-is. Nothing in it constitutes medical advice, psychiatric care, legal advice, or crisis intervention. Read [protocol/DISCLAIMER.md](protocol/DISCLAIMER.md).

---

<sub>Built by [Steve Krisjanovs](https://github.com/steve-krisjanovs) · [Cordfuse](https://github.com/cordfuse)</sub>
