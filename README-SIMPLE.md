# Cortex — Plain English

## The short version

Every time you open ChatGPT, Claude, or any AI — it has no idea who you are. You start from zero. Again.

Cortex fixes that. You talk to it, it remembers everything, and next time you open it, it picks up exactly where you left off. Like a journal that actually reads itself back to you.

And unlike every other app that promises this — **you own the data. Not us. Not anyone.**

---

## Why I built this

Start a new chat with any AI and it has no idea who you are. You explain yourself all over again — who you are, what you're working on, what you said last time. You can reopen an old chat, but nothing you built up comes with you into a new one. Every time, from scratch.

I built Cortex because I needed it to not work like that. My own memory isn't something I can always count on, so starting over isn't a minor annoyance for me — it's the actual problem. I wanted something that remembers for me, that I own, that doesn't vanish between conversations.

I know I'm not the only one who's felt this.

If Cortex has been useful to you, consider donating to [CAMH Foundation](https://camhfoundation.ca/donate) — that's where this started.

<a href="https://camhfoundation.ca/donate"><img src="assets/camh-logo.png" alt="Support CAMH Foundation" height="40"></a>

— Steve Krisjanovs

---

## What it actually does

1. **You talk.** You open Cortex in an AI app and just... talk. About your day, your health, your finances, your work, whatever's on your mind.

2. **It files.** The AI organises what you said into a dated note and saves it to a private folder that belongs to you.

3. **It remembers.** Next time you open it, it reads your recent notes and picks up where you left off. It knows what you were dealing with. It knows what's unresolved.

4. **You own it.** Your notes live in a private GitHub repository — like a folder in the cloud that only you control. Plain text files. No lock-in. Readable forever.

5. **It has a personality.** Cortex actually has three AI layers working together. The **active actor** is who you talk to — that's the one with the personality. **63 ready-made personalities ship with it** — engineers, doctors, coaches, philosophers, creative voices — with **Apex** (precise, curious, direct) as the default. Or describe any personality in plain English and it gets created on the spot, or install one someone else built. The second layer — the **Bootstrap actor** — handles the operational stuff (sync, version checks, session management) in a clean clinical voice and steps out for normal conversation. The third layer — the **hidden scribe** — is silent. It just files things. You won't ever see it in chat. It works the same in every session no matter which active actor you pick.

---

## What you need

- A free [GitHub](https://github.com) account — this is where your notes are stored
- A [Claude](https://claude.ai) account — this is the AI you talk to
- That's it

> **Note:** Use Claude. ChatGPT web/mobile cannot reach GitHub at all (its sandbox blocks the connection — verified July 2026), and Gemini web/mobile doesn't support the file access Cortex needs. On a computer, OpenAI models work via Codex CLI.

> **Model matters:** On Claude, any current model works — the setup below authenticates with a quick approve-on-your-phone step each session.

No downloads. No app store. No subscription. We don't make money from this, and we never see your data.

---

## How to set it up (mobile, 10 minutes)

**1. Copy the template**

Go to [github.com/cordfuse/cortex](https://github.com/cordfuse/cortex) → click **Use this template** → name your repo (e.g. `my-cortex`) → set it to **Private** → create it.

**2. Let the AI reach your repo**

**Install the Personal Cortex app (no tokens needed):**

Go to [github.com/apps/personal-cortex](https://github.com/apps/personal-cortex) → **Install** → pick **only your cortex repo**. Done — no token to create, copy, or save. Each session you'll approve access with one tap on your phone.

**3. Set up your AI project**

Go to your GitHub repo → `manifest/framework/protocol/CORTEX-PROJECT.md` → copy the full contents.

At the very top, add your connection block:

```
repo: https://github.com/YOUR-USERNAME/my-cortex
auth: github-device-flow
client_id: Iv23liec4HPiUGJQe7Fs
```

*(That `client_id` is public — it just names the Personal Cortex app. It is not a secret.)*

Replace with your actual username. This combined text is your complete system prompt.

**On Claude (claude.ai):**
- Go to Projects → New project
- **Instructions:** paste your complete system prompt (connection block + CORTEX-PROJECT.md contents)
- No file uploads needed



**4. Say hello**

Open a new chat in your project. Type: `hello`

That's it. Your Cortex is live.

---

## What happens next

**On your very first session**, the AI gets to know you — it asks what you want Cortex *for* (your personal life, work, a creative project, research, your health, or your finances) and only asks about what fits. Pick more than one, or skip it and just start. Health and mood are always opt-in. Whatever you share becomes the memory it carries forward.

Every time you open a new chat after that, the AI reads your repo, checks what's happened recently, and asks what's on your mind.

You talk. It files. Next session, it remembers.

> **Heads up:** When you first open a chat and say `hello`, you'll see the AI working — reading files, checking things. This is normal and expected. It's not broken. The greeting at the end is what matters. This loading activity is how AI assistants work and isn't something Cortex can hide.

---

## What Cortex CAN'T do on web or mobile

Cortex on Claude.ai web or Claude mobile is **limited to your records**. Talk to your scribe, it reads your files, it writes new entries, it saves them. That's it.

**It cannot:**
- Read your Gmail, Calendar, Drive, Tasks, or Contacts
- Send email
- Reach Microsoft 365 (Mail, Calendar, OneDrive, Teams)
- Connect to anything outside your private cortex repo

**Why:** Claude's web/mobile app runs its tools inside a locked-down environment that **only allows specific websites** (GitHub, where your records live). Connecting to anything else — like Google or Microsoft — is **blocked by the platform itself**. This is intentional security, not something Cortex can change.

**If you want connectors (Gmail, Calendar, etc.) in chat:**
- Use Cortex from a developer terminal (Claude Code, Gemini CLI, etc.).
- **Power-user option: Claude Cowork / Dispatch.** Anthropic has a feature where you can launch Claude Code from the Claude.ai website and it runs in the cloud. Cortex with full connectors works there because it's a real Claude Code session, not the locked-down web app. **But Cowork itself is unstable** — sessions can hang, tools can get stuck, things break. It's still in development on Anthropic's side. Treat as experimental until they finish it. Out of Cortex's control.

For the journal-and-scribe experience, web and mobile are perfectly fine. They just don't connect to the rest of your digital life.

---

## Is my data safe?

- Your notes are in **your private GitHub repo** — only you can see them
- We have zero access to your data — there's no server in the middle
- The AI processes your messages under its own privacy policy — same as any chat you have with it
- If you stop using Cortex, your notes are still there, in plain text, forever

---

## Questions?

Open an issue at [github.com/cordfuse/cortex](https://github.com/cordfuse/cortex/issues) or read the [full technical README](README.md).

---

<sub>Built by [Steve Krisjanovs](https://github.com/steve-krisjanovs) · [Cordfuse](https://github.com/cordfuse) · MIT licence</sub>
