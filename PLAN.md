# Cortex — Plan

**Repo:** cordfuse/cortex  
**Status:** Pre-scaffold  
**Owner:** Steve Krisjanovs / Cordfuse

---

## What it is

A personal record-keeping protocol for mental health — built for the AI agent era.

Not a journal app. Not a mental health coach. A protocol: a structured, git-driven system for recording, tracking, and making sense of your own mental landscape. The AI is a scribe and a sounding board. You own the data. You control the structure.

**Tagline:** *Your mind. Your git. Your AI.*

---

## Why git

- Immutable history — entries are timestamped by commit, not just filename. The past can't be accidentally overwritten.
- Sync without a cloud service — push to a private GitHub repo, no Dropbox, no iCloud, no third party reading your mental health data.
- The psychological weight of a commit — filing something with a hash feels different from saving a text file. The entry is done.
- Portability and longevity — markdown + git will be readable in 30 years. Proprietary apps may not exist in 5.
- Ownership — no server, no account, no company holding your records. Clone it, keep it private, it's yours.

---

## Framing

**What it is:**
- A structured protocol for personal mental health records
- Works with any AI agent (Claude, Gemini, OpenAI) on the user's existing account
- Flat dated markdown files in a private git repo
- Rules of Engagement that define how the AI behaves as a scribe

**What it is not:**
- Therapy
- A crisis tool
- Medical advice
- A replacement for professional care

The disclaimer lives in the repo and in the README. Honest framing from the start — not buried in fine print.

---

## Structure (target)

```
cordfuse/cortex/
  README.md            — what it is, who it's for, how to get started
  ROE.md               — rules of engagement (generalized)
  DISCLAIMER.md        — honest framing, crisis resources
  CLAUDE.md            — agent instructions (one-liner to ROE)
  GEMINI.md            — same
  AGENTS.md            — same
  templates/
    day.md             — daily log template
    event.md           — episode or significant event
    person.md          — person in your life (relationship context)
    medication.md      — medication log (optional)
    theory.md          — insight, pattern, breakthrough
  examples/
    2026-01-01-day.md  — anonymised example day file
    2026-01-01-event.md
```

---

## ROE principles (generalized from personal cortex)

1. **Never edit a committed file.** Corrections go in a new dated file.
2. **Commit before topic switch.** Current thread recorded before moving on.
3. **File every topic separately.** One file per topic per day.
4. **Act.** Commit, record — no permission needed, no narration.
5. **Stay.** When the subject is personal, stay there. No pivoting.
6. **Flush.** On session close, commit and push everything pending.
7. **Scribe, not coach.** The AI listens, reflects, and organises. It does not diagnose, advise, or guide therapy.

---

## Agent behaviour

- Reads ROE.md at session start
- Acts as a scribe — captures, organises, asks clarifying questions
- Never gives medical advice or mental health guidance
- Commits and pushes at session close
- Reminds the user when something should be filed
- Does not carry over session context unless stored in committed files

---

## Disclaimer requirements

- Not a substitute for professional mental health care
- Not a crisis tool — must include crisis line references (988 in US, equivalents elsewhere)
- The AI scribe is not a therapist or counsellor
- No data is collected by Cordfuse — the repo is private and owned by the user
- Cordfuse is not liable for decisions made based on records in this repo

---

## Distribution model

`cordfuse/cortex` is a **GitHub template repo**. Users click "Use this template", name their repo, set it private, clone it, and open it in their AI agent. Their data lives in their own private repo from day one.

`CORTEX-DEV.md` lives on `main` for development. It is excluded from the template — users never see it.

No ZIP. No build step. No manual file deletion. The user *is* the repo.

## Launch plan

1. Scaffold repo structure and templates
2. Write README — product framing, honest, no fluff
3. Write DISCLAIMER.md — thorough, not performative
4. Generalize ROE.md from personal cortex
5. Write template files with clear placeholder guidance
6. Write anonymised example files
7. Configure template repo exclusions (CORTEX-DEV.md, PLAN.md)
8. Add to cordfuse org profile README
9. Announce — Steve Krisjanovs, Cordfuse

---

## Deployment modes

Cortex supports two deployment models. Both are valid. Both are documented in the README.

### Cloud (default)

**Git:** GitHub, GitLab.com, Bitbucket, or any hosted provider.
**AI:** Claude (Anthropic), Gemini (Google), ChatGPT (OpenAI), or any hosted agent CLI.

| Strength | Weakness |
|---|---|
| Easy setup — five minutes from template to first session | Your AI provider processes your records under their privacy policy |
| Sync across devices automatically | Your git host can be subpoenaed |
| Frontier models (Claude Sonnet, GPT-4o) — best instruction-following, strongest guardrail reliability | Records leave your machine |
| Automatic backups via remote push | Provider terms can change |
| Works on any device including mobile | |

### Offline / self-hosted (privacy-first)

**Git:** Self-hosted Gitea, Forgejo, or GitLab CE on a local machine or home server.
**AI:** Local LLM via Ollama — Llama 3, Mistral, Qwen, Phi, or any model that runs locally.

| Strength | Weakness |
|---|---|
| Nothing leaves your machine | Harder to set up — requires Ollama, a local git server, or comfort with local-only repos |
| No AI provider processing your records | Local LLMs are weaker at instruction-following — guardrails may not hold as reliably |
| No subpoena exposure on the git host (if truly local) | No automatic device sync unless you set up your own server |
| No third-party terms or policy changes | Smaller models may produce lower quality scribe output |
| Works air-gapped | Mobile access requires self-hosted infrastructure |

**Guardrails apply in both modes.** Reliability depends on the model. A frontier model will follow guardrails more consistently than a small local LLM. If you use an offline setup, choose the largest model your hardware supports.

---

## What success looks like

Someone dealing with a new diagnosis, a hard relationship, or a rough patch clones this repo in five minutes, opens it in Claude, and has a place to put the hard stuff that is theirs — private, permanent, structured. No app, no subscription, no company reading their records.

That's it.
