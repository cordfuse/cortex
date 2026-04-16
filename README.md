# Cortex

A private record of your life. Git-driven. AI-scribed.

Cortex is a personal record-keeping protocol — a structured, private system for logging and making sense of your thoughts, experiences, health, relationships, work, and anything else worth recording. The AI acts as a scribe and sounding board. You own the data. Nothing is sent anywhere you don't control.

It is not therapy. It is not a journal app. It is not a coach. It is a protocol — and the distinction matters.

> **Read [protocol/DISCLAIMER.md](protocol/DISCLAIMER.md) before you start. Seriously.**

---

## What it does

You open Cortex in your AI agent and talk. The scribe listens, asks clarifying questions, and organises what you say into structured dated files in your private git repository. Records live in `records/`, attachments in `attachments/`. At session end, everything is committed and pushed. Your records are yours — permanently, portably, privately.

Over time, Cortex becomes a corpus you can query. Patterns emerge. Connections surface. The analysis template exists for exactly this — the AI looks across your records and tells you what it sees.

---

## What it covers

Cortex ships with 19 templates across every domain worth recording:

**Personal:** daily log, event, person, theory/insight
**Health:** therapy session, medication, symptoms, appointment
**Life admin:** finance, inventory, supplies, tasks
**Work:** work log, project, career
**Creative:** idea, creative session
**Analytical:** analysis, review

Use what fits. Ignore what doesn't. Add your own.

---

## Repo structure

```
protocol/          # Protocol engine — CORTEX.md, GUARDRAILS.md, ROE.md, DISCLAIMER.md
records/           # Your dated entries — YYYY-MM-DD-HHMM-[slug].md
attachments/       # Attachments — one subfolder per record
templates/         # Blank templates
examples/          # Anonymised example entries
scripts/           # Setup, healthcheck, secrets, make-private
```

---

## Getting started

### Desktop

**1. Create your repo**

Click **[Use this template](../../generate)** on GitHub. Name your repo. Set it **private**. Create it.

**2. Clone it**

```bash
git clone git@github.com:you/your-repo-name.git
cd your-repo-name
```

**3. Open it in your AI agent**

```bash
claude    # Claude Code
gemini    # Gemini CLI
opencode  # OpenCode
```

Or open [claude.ai](https://claude.ai) or [ChatGPT](https://chat.openai.com) and upload the repo if you prefer a web interface.

**4. Start**

Say hello. The scribe takes it from there.

---

### Mobile (Claude or ChatGPT project — recommended)

**1. Create a Claude or ChatGPT project**

Paste the contents of `protocol/CORTEX-PROJECT.md` as the project system prompt.

Create a `CONNECT.md` file with your repo URL and PAT and upload it to the project knowledge:

```
repo: https://github.com/you/your-repo-name
pat: github_pat_...
```

Every new chat in the project clones your repo automatically and opens a Cortex session.

**2. First-time setup — leave repo public initially**

Click **[Use this template](../../generate)** on GitHub (mobile browser or GitHub app). Name it. Leave visibility set to **Public**. Create it.

Open your Claude or ChatGPT project and say hello. The scribe clones it and is ready.

**3. Generate a GitHub PAT**

On GitHub: Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token.

- Name it anything (e.g. `cortex-mobile`)
- Repository access: your Cortex repo only
- Permissions: Contents → Read and write, Administration → Read and write

Copy the token — starts with `github_pat_`. You only see it once.

**4. Store the PAT**

Tell the scribe:

> Store my GitHub PAT. Ask me for the token and a passphrase.

The scribe asks for both in chat. Reply with each. The encrypted vault is committed and pushed automatically.

**5. Make the repo private**

The GitHub API is not accessible from Claude or ChatGPT mobile — flip it manually.

On GitHub: your repo → Settings → scroll to Danger Zone → Change visibility → Make private.

Update `CONNECT.md` in your project knowledge with the PAT so future sessions clone automatically.

**6. Done**

Your Cortex is live, private, and synced.

---

### Returning sessions

**Desktop:** `cd your-repo && claude` — say hello.

**Mobile project:** open a new chat in your Cortex project — the scribe clones the repo and picks up where you left off.

---

## Cloud vs offline

Two ways to run Cortex. Both are valid. Choose based on your privacy needs.

### Cloud (default)

**Git:** GitHub, GitLab.com, or any hosted provider.
**AI:** Claude, Gemini, ChatGPT, or any hosted agent.

- Easy setup — five minutes from template to first session
- Syncs across devices automatically
- Frontier models follow guardrails most reliably
- **Tradeoff:** Your AI provider processes your records under their privacy policy. Your git host can be subpoenaed. Records leave your machine.

### Offline / self-hosted

**Git:** Local repo, or self-hosted [Gitea](https://gitea.io) / [Forgejo](https://forgejo.org) / [GitLab CE](https://gitlab.com/oss/packages).
**AI:** [Ollama](https://ollama.com) running a local model with tool calling.
**Interface:** [Open WebUI](https://openwebui.com) or any frontend that exposes tool calling.

- Nothing leaves your machine
- No AI provider processing your records
- No subpoena exposure on the git host
- Works air-gapped
- **Tradeoff:** Harder to set up. Local LLMs are weaker at instruction-following — guardrails apply but reliability varies. Choose the largest model your hardware supports.

**Guardrails apply in both modes. Privacy and reliability pull in opposite directions — choose your tradeoff consciously.**

---

## Guardrails

Cortex ships with `protocol/GUARDRAILS.md` — hard stops that govern how the AI scribe behaves. They cover crisis situations, intent to harm others, crime disclosure, child safety, jailbreak attempts, and sandbox integrity.

**If you remove or modify `protocol/GUARDRAILS.md`, the scribe operates without any of these protections. Cordfuse accepts zero liability for the consequences. You are on your own.**

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

- A git client
- An AI agent CLI ([Claude Code](https://claude.ai/download), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [OpenCode](https://opencode.ai)) — or a web interface (claude.ai, ChatGPT)
- For offline: [Ollama](https://ollama.com) and a self-hosted git server

---

## Licence

MIT — see [LICENSE](LICENSE).

This protocol is provided as-is. Nothing in it constitutes medical advice, psychiatric care, legal advice, or crisis intervention. Read [protocol/DISCLAIMER.md](protocol/DISCLAIMER.md).

---

<sub>Built by [Steve Krisjanovs](https://github.com/steve-krisjanovs) · [Cordfuse](https://github.com/cordfuse)</sub>
