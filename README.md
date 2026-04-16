# Cortex

A private record of your life. Git-driven. AI-scribed.

Cortex is a personal record-keeping protocol — a structured, private system for logging and making sense of your thoughts, experiences, health, relationships, work, and anything else worth recording. The AI acts as a scribe and sounding board. You own the data. Nothing is sent anywhere you don't control.

It is not therapy. It is not a journal app. It is not a coach. It is a protocol — and the distinction matters.

> **Read [DISCLAIMER.md](DISCLAIMER.md) before you start. Seriously.**

---

## What it does

You open Cortex in your AI agent and talk. The scribe listens, asks clarifying questions, and organises what you say into structured dated files in your private git repository. At session end, everything is committed and pushed. Your records are yours — permanently, portably, privately.

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

## Getting started

### 1. Create your repo

Click **[Use this template](../../generate)** on GitHub. Name your repo — something like `my-cortex`. Set it **private**. Create it.

### 2. Clone it

```bash
git clone git@github.com:you/my-cortex.git
cd my-cortex
```

### 3. Open it in your AI agent

```bash
claude    # Claude Code
gemini    # Gemini CLI
codex     # OpenAI Codex
opencode  # OpenCode
```

Or upload the repo to [claude.ai](https://claude.ai) or [ChatGPT](https://chat.openai.com) if you prefer a web interface.

### 4. Start

Say hello. The scribe takes it from there.

---

## Cloud vs offline

Two ways to run Cortex. Both are valid. Choose based on your privacy needs.

### Cloud (default)

**Git:** GitHub, GitLab.com, or any hosted provider.
**AI:** Claude, Gemini, ChatGPT, or any hosted agent.

- Easy setup — five minutes from template to first session
- Syncs across devices automatically
- Frontier models (Claude Sonnet, GPT-4o) follow guardrails most reliably
- **Tradeoff:** Your AI provider processes your records under their privacy policy. Your git host can be subpoenaed. Records leave your machine.

### Offline / self-hosted

**Git:** [Gitea](https://gitea.io), [Forgejo](https://forgejo.org), or [GitLab CE](https://gitlab.com/oss/packages) on your own hardware.
**AI:** [Ollama](https://ollama.com) with a local model (Llama 3, Mistral, Qwen, Phi).

- Nothing leaves your machine
- No AI provider processing your records
- No subpoena exposure on the git host
- Works air-gapped
- **Tradeoff:** Harder to set up. Local LLMs are weaker at instruction-following — guardrails apply but reliability varies by model. Choose the largest model your hardware supports.

**Guardrails apply in both modes. Privacy and reliability pull in opposite directions — choose your tradeoff consciously.**

---

## Guardrails

Cortex ships with `GUARDRAILS.md` — hard stops that govern how the AI scribe behaves. They cover crisis situations, intent to harm others, crime disclosure, child safety, jailbreak attempts, and sandbox integrity.

**If you remove or modify `GUARDRAILS.md`, the scribe operates without any of these protections. Cordfuse accepts zero liability for the consequences. You are on your own.**

The scribe will refuse to start if `GUARDRAILS.md` or `DISCLAIMER.md` is missing.

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
- An AI agent CLI ([Claude Code](https://claude.ai/download), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [Codex](https://platform.openai.com/codex), [OpenCode](https://opencode.ai)) — or a web interface (claude.ai, ChatGPT)
- For offline: [Ollama](https://ollama.com) and a self-hosted git server

---

## Licence

MIT — see [LICENSE](LICENSE).

This protocol is provided as-is. Nothing in it constitutes medical advice, psychiatric care, legal advice, or crisis intervention. Read [DISCLAIMER.md](DISCLAIMER.md).

---

<sub>Built by [Steve Krisjanovs](https://github.com/steve-krisjanovs) · [Cordfuse](https://github.com/cordfuse)</sub>
