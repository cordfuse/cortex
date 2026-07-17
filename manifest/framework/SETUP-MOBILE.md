# Cortex — Mobile & Web Setup

> **Gemini web and mobile do not support the tool-calling flow required by Cortex.** Use Claude or ChatGPT.

Set up once — every new chat in the project opens a session automatically.

---

## What works here first

On Claude (claude.ai) and ChatGPT — web and mobile — Cortex does **git**: clone your repo, read your records, log new entries, commit, and push. That's the whole capture-and-recall loop, and it works fully on your phone.

What does **not** work here: live connectors (Google, Microsoft 365, Notion, etc.). The AI provider's sandbox blocks outbound network to anything but its own package registries, so connector scripts fail at the proxy — this is Anthropic's and OpenAI's restriction, not something Cortex can work around. Run connectors from a **CLI agent or desktop** instead (see [SETUP-DESKTOP.md](SETUP-DESKTOP.md)); they sync through the same git repo, so a connector run on your laptop shows up in your next mobile session.

Short version: **journaling, records, and recall work everywhere; live integrations are a desktop/CLI thing.**

> ChatGPT is supported but less battle-tested than Claude — the protocol is validated primarily on Claude. If something behaves oddly on ChatGPT, that's the likely reason.

---

## Step 1 — Create your repo

**New to Cortex:**

Open GitHub in your mobile browser or the GitHub app. Go to [cordfuse/cortex](https://github.com/cordfuse/cortex) → Use this template → Create a new repository. Name it. Set it **private**. Create it.

**Already have a Cortex repo:**

Skip this step.

---

## Step 2 — Generate a GitHub PAT

GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token.

- **Repository access:** your Cortex repo only
- **Permissions:** Contents → Read and write

Copy the token — starts with `github_pat_`. You only see it once. Save it somewhere safe (Notes, password manager).

---

## Step 3 — Build your system prompt

Open `manifest/framework/protocol/CORTEX-PROJECT.md` in your repo. Copy the full contents.

At the very top, add your connection block:

```
repo: https://github.com/you/your-repo-name
pat: github_pat_...
```

This is the complete system prompt — repo URL, PAT, and protocol instructions in one place. No separate file needed.

---

## Step 4 — Create your project

### Claude (claude.ai)

1. claude.ai → Projects → New project
2. **Instructions:** paste your full system prompt (connection block + CORTEX-PROJECT.md contents)
3. Open a new chat in the project

### ChatGPT (chat.openai.com)

1. Explore GPTs → Create a GPT → Configure
2. **Instructions:** paste your full system prompt (connection block + CORTEX-PROJECT.md contents)
3. Save and open a chat

No project knowledge or file uploads needed.

---

## Step 5 — Say hello

```
hello
```

Bootstrap runs Gate 3 (`git fetch origin` + version check), the opening scan, and surfaces version state in clinical voice. Then your chosen actor greets you with: **What's on your mind?** plus a short status line.

---

## Returning sessions

Open a new chat in your Cortex project. Say `hello`. The scribe clones fresh and picks up automatically.

---

## When your PAT expires or is rotated

The scribe detects auth failure automatically and asks:

> *"The PAT isn't working — please paste a current one."*

Paste your new PAT. The session continues. To fix future sessions, update the PAT value at the top of your project instructions.

---

## Notes

- The PAT in your project instructions is visible to your AI provider — keep the project private
- **Vault decryption is CLI-only by design.** Cloud-hosted Claude (mobile, web) is required to refuse decryption of vault files, because outputting plaintext into a chat would place the secret into the model's context window and the session transcript — which is precisely what the vault exists to prevent. Enforcement layer is the scribe under `manifest/framework/protocol/GUARDRAILS.md` → Vault Decryption Surface (v4.6.6+). Run `bun manifest/framework/scripts/secrets.ts get <name>` from a terminal instead. Mobile-critical secrets (banking, ISP, payment) belong in a password manager (1Password / Bitwarden / Apple Passwords), not the cortex vault — biometric unlock + native autofill is the right surface for those.
