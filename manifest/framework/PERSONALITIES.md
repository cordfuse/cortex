# Cortex Personalities

> **In v4+, every cortex session has three AI layers:**
>
> 1. The **Bootstrap actor** (v4.0.0-alpha.20+) — auto-loaded for the operational layer. Handles Gate 3, sync prompts, opening scans, and any state-changing verb response in clinical voice. Hot-swaps out as soon as operational work is done.
> 2. The **active actor** — your chosen named personality. Apex (framework default), or any custom personality you've created. This is who you talk to. The personality file controls voice — tone, language, manner, traits.
> 3. The **hidden scribe** — always present, never speaks. Handles all filing, committing, scanning. Defined by the protocol (CORTEX.md + ROE.md), no personality file.
>
> **Personality files configure the Bootstrap actor and the active actor only.** The hidden scribe's behavior is the same in every session, regardless of which active actor you've loaded.

Cortex ships with **one framework active actor (Apex)** plus the Bootstrap actor. Everything else is yours to build.

**Hard rule:** Personality files control tone and language only. GUARDRAILS, ROE, and crisis protocol are never overridden by a personality file. Every personality respects all safety rules in full.

**Activating a personality:** Set one line in `context.md`:
```
personality: apex
```
Both `personality:` and `actor:` are accepted. **If `personality:` is missing or blank (v4.0.0-alpha.20+):** Bootstrap surfaces a picker and asks you to choose.

**Hot-swap mid-session (v4.0.0-alpha.8+):** *"change actor to [name]"* — scribe updates `context.md`, commits, adopts the new voice next response. No fresh hello required.

**Multi-parent inheritance (v4.0.0-alpha.11+):** custom personalities can inherit from multiple parents simultaneously via `## parents` (a list).

To see what's available: `list actors`

To create your own: describe it in plain English — the scribe writes the file, commits it, and asks if you want to activate it.

---

## Bootstrap Actor (v4.0.0-alpha.20+)

### Bootstrap — `PERSONALITY-BOOTSTRAP.md`
*Operational. Boots Cortex, runs verbs, surfaces state. Clinical, factual, plain English.*

**Bootstrap is loaded automatically at every session.** It runs Gate 3 enforcement, sync prompts, opening scans, and any state-changing verb response. When operational work is complete, Bootstrap hot-swaps out and the user's chosen actor takes over for conversational turns.

You don't pick Bootstrap — it picks itself. It never engages in conversation and steps out as soon as a verb's response is rendered.

> Archetype: ANALYST / HARDLINER · Vibe: very low humor, low warmth, high seriousness

---

## Framework Actor

### Apex — `PERSONALITY-APEX.md`
*Precise, curious, direct. Thinks clearly, speaks plainly.*

The one framework default. Generic, no domain specialty. Adapts to planning, analysis, writing, technical work, thinking out loud. The reliable starting point before you build custom actors for specific needs.

> Archetype: ANALYST · Vibe: moderate humor, moderate warmth, moderately serious

---

## Custom Actors (v4.4.0+)

The framework ships lean. Specialty, character, and domain-specific actors belong in your personal fork as `PERSONALITY-CUSTOM-*.md` files. They are never overwritten by framework sync.

### Creating a custom actor

Describe what you want in plain English — the scribe writes the personality file and commits it. Or write it yourself following the [personality file format](../manifest/framework/protocol/CORTEX.md#personality-file-format).

### Crediting custom actors

Add an `## author` field to any `PERSONALITY-CUSTOM-*.md`:

```
## author
github.com/yourhandle
```

The `list actors` output surfaces `↳ by [author]` under the actor entry. The credit travels with the file if you share it. Format is freeform — handle, name, URL, anything.

### Sharing custom actors

Custom personality files are plain markdown. Drop them in a gist, a repo, a DM. The recipient copies one file into their `personalities/` folder. If the file is named `PERSONALITY-CUSTOM-*.md`, cortex picks it up automatically on next `list actors`.

---

## Personality file format

See [manifest/framework/protocol/CORTEX.md → Personality file format](../manifest/framework/protocol/CORTEX.md#personality-file-format) for the full field reference including vibe, virtues, vices, soft skills, hard skills, archetypes, and the `## author` credit field.
