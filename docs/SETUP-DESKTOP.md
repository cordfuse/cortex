# Cortex — Desktop Setup

## Step 1 — Create your repo

**New to Cortex:**

Click **[Use this template](https://github.com/cordfuse/cortex/generate)** on GitHub. Name your repo. Set it **private**. Create it.

**Already have a Cortex repo:**

Skip this step. Your records, vault, and verbs are already there.

---

## Step 2 — Run the installer

**macOS / Linux** — open Terminal and run:

```bash
curl -fsSL https://github.com/cordfuse/cortex/releases/latest/download/install.sh | bash
```

**Windows** — open PowerShell and run:

```powershell
iex (irm https://github.com/cordfuse/cortex/releases/latest/download/install.ps1)
```

The installer will ask for your repo URL (paste the one you just created) and where to clone it. It handles everything else: clones your repo, installs git and Python if missing, and installs all dependencies. Safe to re-run at any time to repair your environment.

---

## Step 3 — Open in your AI agent

```bash
claude      # Claude Code (CLI)
gemini      # Gemini CLI
opencode    # OpenCode
qwen        # Qwen Code
```

**No terminal?** Use **Claude Desktop** ([claude.ai/download](https://claude.ai/download)) — open the app, add your repo folder as a project. No command line needed.

---

## Step 4 — Say hello

```
hello
```

The scribe reads your protocol files, scans for open items, and picks up where you left off.

---

## Returning sessions

```bash
cd your-repo-name
claude    # or whichever agent you use
```

Say `hello`.

---

## Updating

`setup.sh` adds an upstream remote automatically. When a new version ships:

```bash
git fetch upstream
git checkout upstream/main -- protocol/ templates/ scripts/ setup.sh setup.ps1 install.sh install.ps1
git commit -m "sync: cortex vX.X.X"
```

Your `records/`, `attachments/`, `docs/`, and `cortex.secrets/` are never touched.
