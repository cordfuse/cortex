# Cortex — Mobile & Web Setup

> **Claude (claude.ai) is the only supported web/mobile surface.** ChatGPT web/mobile is **not supported**: its sandbox has no network route to GitHub at all — `git clone` fails with `Could not resolve host: github.com` (verified 2026-07-20). This is OpenAI's platform restriction, not a Cortex or model issue. Gemini web/mobile lacks the tool-calling flow Cortex needs.

Set up once — every new chat in the project opens a session automatically.

---

## What works here first

On Claude (claude.ai) — web and mobile — Cortex does **git**: clone your repo, read your records, log new entries, commit, and push. That's the whole capture-and-recall loop, and it works fully on your phone.

What does **not** work here: live connectors (Google, Microsoft 365, Notion, etc.). The AI provider's sandbox blocks outbound network to anything but its own package registries, so connector scripts fail at the proxy — this is Anthropic's and OpenAI's restriction, not something Cortex can work around. Run connectors from a **CLI agent or desktop** instead (see [SETUP-DESKTOP.md](SETUP-DESKTOP.md)); they sync through the same git repo, so a connector run on your laptop shows up in your next mobile session.

Short version: **journaling, records, and recall work everywhere; live integrations are a desktop/CLI thing.**

> Want an OpenAI model instead? Use **Codex CLI on desktop** — the web/mobile surface for Cortex is Claude only (see note above).

---

## Step 1 — Create your repo

**New to Cortex:**

Open GitHub in your mobile browser or the GitHub app. Go to [cordfuse/cortex](https://github.com/cordfuse/cortex) → Use this template → Create a new repository. Name it. Set it **private**. Create it.

**Already have a Cortex repo:**

Skip this step.

---

## Step 2 — Authorize access

**On Claude — install the Personal Cortex GitHub App (recommended; no tokens to create or store):**

Go to [github.com/apps/personal-cortex](https://github.com/apps/personal-cortex) → **Install** → your account → **Only select repositories** → your Cortex repo. One minute, once.

With this method there is **no token to generate, save, rotate, or paste** — each session, the scribe requests a device code and you approve it on your phone (~10 seconds). Nothing secret is ever stored in your project instructions.

**Fallback — generate a fine-grained PAT** (only if you can't use the app; note that current Claude models require the in-chat consent step and may decline autonomous PAT use):

GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token.

- **Repository access:** your Cortex repo only
- **Permissions:** Contents → Read and write

Copy the token — starts with `github_pat_`. You only see it once. Save it somewhere safe (Notes, password manager).

---

## Step 3 — Build your system prompt

Open `manifest/framework/protocol/CORTEX-PROJECT.md` in your repo. Copy the full contents.

At the very top, add your connection block — **device flow** (Claude, recommended):

```
repo: https://github.com/you/your-repo-name
auth: github-device-flow
client_id: Iv23liec4HPiUGJQe7Fs
```

*(The `client_id` is a public identifier for the Personal Cortex app — not a secret.)*

— or **PAT** (fallback):

```
repo: https://github.com/you/your-repo-name
auth: pat
pat: github_pat_...
```

This is the complete system prompt — connection block and protocol instructions in one place. No separate file needed.

---

## Step 4 — Create your project

### Claude (claude.ai)

1. claude.ai → Projects → New project
2. **Instructions:** paste your full system prompt (connection block + CORTEX-PROJECT.md contents)
3. Open a new chat in the project

No project knowledge or file uploads needed.

---

## Step 5 — Say hello

```
hello
```

The scribe says what it's about to do and asks you to confirm. **Device flow:** it shows a short code — open the link, enter the code (or just tap Continue if already authorized), say `done`. **PAT:** it clones directly after your yes. Then boot: protocol load, Gate 3 (`git fetch origin` + version check), the opening scan, and your chosen actor greets you with: **What's on your mind?** plus a short status line.

> The confirm-then-proceed exchange is deliberate: current-generation models require explicit in-chat consent before authenticating to a private repo, and the flow is designed with that grain rather than against it.

---

## Returning sessions

Open a new chat in your Cortex project. Say `hello`, confirm, (device flow: approve the code — one tap when already authorized). The scribe clones fresh and picks up automatically.

---

## Auth maintenance

**Device flow:** nothing to maintain. Session tokens are minted per-session, expire on their own, and are never stored. If GitHub rejects a token, the app probably isn't installed on the repo — install it at [github.com/apps/personal-cortex](https://github.com/apps/personal-cortex).

**PAT:** when it expires or is rotated, the scribe detects auth failure and asks:

> *"The PAT isn't working — please paste a current one."*

Paste your new PAT. The session continues. To fix future sessions, update the PAT value at the top of your project instructions.

---

## Notes

- **Device flow stores no secret anywhere** — the `client_id` in your project instructions is public by design.
- A PAT in your project instructions is visible to your AI provider — keep the project private. (This is the reason device flow is the recommended method on Claude.)
- **Vault decryption is CLI-only by design.** Cloud-hosted Claude (mobile, web) is required to refuse decryption of vault files, because outputting plaintext into a chat would place the secret into the model's context window and the session transcript — which is precisely what the vault exists to prevent. Enforcement layer is the scribe under `manifest/framework/protocol/GUARDRAILS.md` → Vault Decryption Surface (v4.6.6+). Run `bun manifest/framework/scripts/secrets.ts get <name>` from a terminal instead. Mobile-critical secrets (banking, ISP, payment) belong in a password manager (1Password / Bitwarden / Apple Passwords), not the cortex vault — biometric unlock + native autofill is the right surface for those.
