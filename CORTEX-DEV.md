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

## Release

Cortex has no build step — it ships as-is. A release is just a git tag:

```bash
VERSION=$(cat version.txt)
git tag "v${VERSION}"
git push origin "v${VERSION}"
```

Update `version.txt` before tagging. Write release notes manually after the tag is pushed.
