# Cortex — Mobile & Web Setup

> **Gemini web and mobile do not support the tool-calling flow required by Cortex.** Use Claude or ChatGPT.

Set up once — every new chat in the project opens a session automatically.

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

## Step 3 — Create your CONNECT.md

Create a plain text file called `CONNECT.md` **on your device only. Never commit this to your repo.**

```
repo: https://github.com/you/your-repo-name
pat: github_pat_...
```

This is how the scribe authenticates and knows where your repo lives. Keep it local.

---

## Step 4 — Get the system prompt

Open your repo on GitHub. Navigate to `protocol/CORTEX-PROJECT.md`. Copy the full contents — this is your system prompt.

---

## Step 5 — Create your project

### Claude (claude.ai)

1. claude.ai → Projects → New project
2. **Instructions (system prompt):** paste the full contents of `protocol/CORTEX-PROJECT.md`
3. **Project knowledge:** upload your `CONNECT.md`
4. Open a new chat in the project

### ChatGPT (chat.openai.com)

1. Explore GPTs → Create a GPT → Configure
2. **Instructions:** paste the full contents of `protocol/CORTEX-PROJECT.md`
3. **Knowledge:** upload your `CONNECT.md`
4. Save and open a chat

---

## Step 6 — Say hello

```
hello
```

The scribe sets up silently and greets you. No narration — just: **What's on your mind?**

---

## Returning sessions

Open a new chat in your Cortex project. Say `hello`. The scribe clones fresh and picks up automatically.

---

## Notes

- Your `CONNECT.md` PAT is visible in the project knowledge — keep the project private
- The scribe can store your PAT in the vault after first session: `python scripts/secrets.py store github-pat`
- If your PAT expires, generate a new one and update `CONNECT.md` in the project knowledge
