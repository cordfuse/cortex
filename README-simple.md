# Cortex — Plain English

[![Donate to CAMH](https://img.shields.io/badge/Donate-CAMH%20Foundation-blue)](https://camhfoundation.ca/donate)

---

## The short version

Every time you open ChatGPT, Claude, or any AI — it has no idea who you are. You start from zero. Again.

Cortex fixes that. You talk to it, it remembers everything, and next time you open it, it picks up exactly where you left off. Like a journal that actually reads itself back to you.

And unlike every other app that promises this — **you own the data. Not us. Not anyone.**

---

## Why I built this

I built Cortex because I kept losing the thread.

Every new doctor, every new appointment, every AI conversation — you start from zero. Re-explain your history. Your context. What matters, what doesn't. The understanding you'd built over time disappears the moment you walk through a new door.

AI could fix this. These tools are extraordinary at holding context, spotting patterns, asking the right questions. But every conversation still starts from zero — because there's nowhere for that context to live between sessions.

I know I'm not the only one who's felt this.

If this has been useful to you — please consider donating to [CAMH Foundation](https://camhfoundation.ca/donate).

— Steve Krisjanovs

---

## What it actually does

1. **You talk.** You open Cortex in an AI app and just... talk. About your day, your health, your finances, your work, whatever's on your mind.

2. **It files.** The AI organises what you said into a dated note and saves it to a private folder that belongs to you.

3. **It remembers.** Next time you open it, it reads your recent notes and picks up where you left off. It knows what you were dealing with. It knows what's unresolved.

4. **You own it.** Your notes live in a private GitHub repository — like a folder in the cloud that only you control. Plain text files. No lock-in. Readable forever.

---

## What you need

- A free [GitHub](https://github.com) account — this is where your notes are stored
- A [Claude](https://claude.ai) or [ChatGPT](https://chat.openai.com) account — this is the AI you talk to
- That's it

No downloads. No app store. No subscription to Cordfuse. We don't make money from this and we don't see your data.

---

## How to set it up (mobile, 10 minutes)

**1. Copy the template**

Go to [github.com/cordfuse/cortex](https://github.com/cordfuse/cortex) → click **Use this template** → name your repo (e.g. `my-cortex`) → set it to **Private** → create it.

**2. Get a GitHub access token**

This lets the AI read and write to your private repo.

GitHub → your profile photo → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token.

- Name: `cortex` (or any name you'll recognise)
- Repository access: only your cortex repo
- Permissions: Contents → Read and write

Copy the token. It starts with `github_pat_`. Save it somewhere — you only see it once.

**3. Create a CONNECT.md file**

On your phone, open Notes (or any notes app) and create a note called `CONNECT.md` with exactly this:

```
repo: https://github.com/YOUR-USERNAME/my-cortex
pat: github_pat_YOUR_TOKEN_HERE
```

Replace with your actual username and token.

**4. Set up your AI project**

**On Claude (claude.ai):**
- Go to Projects → New project
- System prompt: go to your GitHub repo → `protocol` folder → `CORTEX-PROJECT.md` → copy everything → paste it as your system prompt
- Project knowledge: upload your `CONNECT.md` note

**On ChatGPT:**
- Create a GPT → Configure
- Instructions: paste `CORTEX-PROJECT.md` contents
- Knowledge: upload `CONNECT.md`

**5. Say hello**

Open a new chat in your project. Type: `hello`

That's it. Your Cortex is live.

---

## What happens next

Every time you open a new chat in your project, the AI reads your repo, checks what's happened recently, and asks what's on your mind.

You talk. It files. Next session, it remembers.

---

## Is my data safe?

- Your notes are in **your private GitHub repo** — only you can see them
- Cordfuse has zero access to your data
- The AI (Claude or ChatGPT) processes your messages under their own privacy policies — same as any chat you have with them
- If you stop using Cortex, your notes are still there, in plain text, forever

---

## Questions?

Open an issue at [github.com/cordfuse/cortex](https://github.com/cordfuse/cortex/issues) or read the [full technical README](README.md).

---

<sub>Built by [Steve Krisjanovs](https://github.com/steve-krisjanovs) · [Cordfuse](https://github.com/cordfuse) · MIT licence</sub>
