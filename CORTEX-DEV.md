# Cortex — Developer Mode

You are a normal coding assistant. There are no persona constraints, no scribe role, no crisis protocol. You help the developer build and maintain the Cortex protocol.

`CORTEX.md` and all other protocol files are source code you help edit — not instructions for you to follow.

---

## Welcome

At session start, greet briefly:

> **Cortex Dev** — Ready to build. What are we working on?

---

## Dev Commands

- **"build"** / **"scaffold"** — create or update protocol files
- **"test"** — walk through the user experience as if you were a new user cloning the repo
- **"review"** — read all protocol files and give an honest critique
- **"help"** — show project structure and available commands

---

## Project Structure

```
CORTEX.md              # Protocol engine — the scribe's instructions
CORTEX-DEV.md          # This file — dev mode
DISCLAIMER.md          # Honest framing and crisis resources
ROE.md                 # Rules of engagement
CLAUDE.md              # One-liner → CORTEX.md
GEMINI.md              # Same
AGENTS.md              # Same
PLAN.md                # Development plan and roadmap
README.md              # Public-facing repo README
templates/             # Blank templates for each file type
  day.md
  event.md
  person.md
  medication.md
  theory.md
examples/              # Anonymised example entries
```

---

## Dev Mode Activation

Dev mode is implicit — if you are in a repo that contains `CORTEX-DEV.md`, dev mode is active. No passphrase needed.

In dev mode:
- You may discuss the protocol design openly
- You may edit any file in the repo
- You may critique CORTEX.md, ROE.md, or any other protocol file
- You will not adopt the scribe persona or follow crisis protocols

---

## Commit Discipline

One file per commit. Commit immediately after writing or editing a file. Do not batch changes.

```bash
git add <file>
git commit -m "description"
git push
```

---

## Branch Rules

**`dev`** — where all development happens. `CORTEX-DEV.md` and `PLAN.md` live here permanently. Never merge these to `main`.

**`main`** — always user-ready. The GitHub template uses this branch. Only user-facing files belong here:
- `CORTEX.md`
- `DISCLAIMER.md`
- `ROE.md`
- `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`
- `templates/`
- `examples/`
- `README.md`
- `version.txt`

### Merging dev → main

Never merge the full branch. Cherry-pick or manually apply only user-facing changes:

```bash
git checkout main
git checkout dev -- CORTEX.md ROE.md DISCLAIMER.md README.md templates/ examples/ version.txt
git commit -m "merge: <description>"
git push
```

`CORTEX-DEV.md` and `PLAN.md` stay on `dev`. Always.

---

## Release

Cortex has no build step — it ships as-is. Tag from `main`:

```bash
git checkout main
VERSION=$(cat version.txt)
git tag "v${VERSION}"
git push origin "v${VERSION}"
```

Update `version.txt` on `dev` first, merge it to `main`, then tag. Write release notes manually after the tag is pushed.
