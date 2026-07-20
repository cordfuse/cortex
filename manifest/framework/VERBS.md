# Verbs

Session actions the scribe knows about. All invoked by **natural language** — say what you want, the scribe routes the intent. Each verb has a `Triggers:` line of natural language patterns. The shorthand name is one trigger among many, never the required form.

**To activate a verb:** just ask — *"activate weekly review"* or *"turn on calendar"*. The scribe enables it and commits.
**To deactivate:** *"turn off meds"* or *"deactivate standup"*. The scribe disables it and commits.
**To add your own:** describe what you want — the scribe writes it, adds it here, and commits.

`list verbs` shows everything currently active with trigger sets.

> **No slash prefixes.** Cortex uses natural language. Slash prefixes are intercepted by AI client UIs before the scribe sees them. Custom verb shorthands must not match built-in intent names (`hello`, `goodbye`, `status`, `sync`, `search`, `list verbs`, `list personalities`, `list actors`).

---

## Available verbs

---

### Personality

## switch personality

Triggers: "switch personality" | "change actor" | "use [name]" | "switch to [name]" | "I want to talk to [name]"

Switch active speaker (single-actor sessions) OR change which actor is the active speaker among multiple in the room (multi-actor sessions, alpha.32+). Scribe updates the active-speaker designation in `context.md`, commits, and **hot-swaps immediately** — the next response is in the new active speaker's voice, no fresh hello required (v4.0.0-alpha.8+). In multi-actor sessions, this does NOT remove other actors from the room — use `remove actor` for that.

## add actor

Triggers: "add actor [name]" | "bring in [name]" | "invite [name]" | "hey [name], join us" | "add [name] to the room"

Bring an additional named actor into the session (multi-actor mode, v4.0.0-alpha.32+). Scribe loads the named actor's personality file, appends a new entry to `actors:` in `context.md` with `active_speaker: false`, commits. The new actor is addressable but does NOT auto-respond unless explicitly named.

## remove actor

Triggers: "remove actor [name]" | "[name], you can step out" | "send [name] away" | "remove [name]"

Remove a named actor from the session (multi-actor mode, v4.0.0-alpha.32+). Scribe surfaces a confirmation prompt unless the actor has 0 contributions this session, then removes the entry from `actors:` in `context.md`, commits. **Refuses to remove the last actor.**

## help

Triggers: "help" | "tutorial" | "show me around" | "how does this work" | "what can you do" | "I'm new to this"

Replay the first-run overview — one conversational beat covering what Cortex is, then the optional deeper tour. Available at any time regardless of onboarding state. Never a step-by-step wizard; never surface internal labels like "Step 1". Appends an `Overview re-run (help)` entry to `manifest/custom/cortex-onboarding.md`. (v4.5.4+; de-wizardified in v4.14.0.)

---

## create actor

Triggers: "create actor [name]" | "new actor [name]" | "new personality [name]" | "make me an actor called [name]" | "I want to create a personality"

Create a new custom personality. Scribe presents a **single batched form** with all required and optional fields, plus a `take all defaults` shortcut. User can also say *"walk me through it"* for turn-by-turn. Output: `manifest/custom/actors/<NAME>.md`, committed, offered for activation (skipped if `## abstract: true`). (v4.0.0-alpha.27+.)

---

## import actor

Triggers: "import actor from [url]" | "add actor from [link]" | "I want to use [person]'s [name] actor" | "here's an actor file: [paste]" | "add this personality: [paste]"

Import a personality file from an external source into the user's actor library. Scribe:
1. Accepts a URL (GitHub gist, raw file link) or pasted file content
2. Infers source handle from URL (GitHub username from gist/raw URL) — if content was pasted with no URL, asks in plain English: *"What should I call the person this came from? I'll use that to keep their actors organised."* If user doesn't know or doesn't care, default to `shared`
3. Writes to `manifest/custom/actors/<source-handle>/<NAME-SLUG>.md`
4. Confirms: *"[Name] from [source-handle] added. Say `change actor to [Name]` to activate."*
5. Commits. Does NOT auto-activate.

Note: if a name collision exists (same `## name` as an existing actor), surfaces the conflict before writing: *"You already have an actor named [Name]. Import anyway as [source-handle]/[Name]? (yes / no)"* (v4.5.3+.)

---

## browse mtx

Triggers:
- Power user: "browse mtx" | "what actors are in mtx" | "show me mtx actors" | "list mtx actors" | "what's available in mtx" | "add actor from mtx" | "import from mtx"
- Natural language: "what actors are available to add?" | "show me who I can bring in" | "who do you have?" | "what personalities are available?" | "show me available actors" | "who can I add to this session?"
- By domain: "show me [domain] actors" | "any [domain] personalities?" | "who do you have for [domain]?" | "what [domain] options are there?" — where [domain] is engineering, health, finance, spiritual, music, productivity, communication, general
- By need: "I need someone more [trait]" | "is there a [role type] I can add?" | "who would be good for [topic]?" | "I'm looking for a [descriptor]"

Browse and selectively import actors from cordfuse/agent-assets. Scribe:
1. Fetches `https://raw.githubusercontent.com/cordfuse/agent-assets/main/README.md` to get the current actor roster
2. Presents the full list grouped by domain, with each actor's name, alias, and one-line description
3. If the user named a domain or trait, filter to matching actors only
4. Prompts: *"Which would you like to add? Name one or more — or say 'all' for everything."*
5. For each selected actor, fetches `https://raw.githubusercontent.com/cordfuse/agent-assets/main/actors/{name}.md` and writes to `manifest/custom/actors/{name}.md`
6. On name collision with an existing custom actor, surfaces: *"You already have [name] — overwrite? (yes / skip)"*
7. Confirms: *"Added: [list]. Say `change actor to [name]` to activate any of them."*
8. Commits all new files in a single commit.

## add from mtx

Triggers:
- Power user: "add [name] from mtx" | "import [name] from mtx" | "get [name] from agent-assets" | "install [name] from mtx"
- Natural language: "add a [role]" | "bring in a [role]" | "I want to talk to a [role]" | "add someone who [does/knows/specializes in X]" | "give me a [descriptor] voice" | "I need a [role type]"

Add a single named actor from cordfuse/agent-assets directly (no browse step). Scribe:
1. If a name was given directly, fetches `https://raw.githubusercontent.com/cordfuse/agent-assets/main/actors/{name}.md`
2. If a role or description was given (NL path), scans the README roster and finds the closest match — surfaces it to the user for confirmation before adding: *"Closest match: [Name] — [one-line description]. Add them? (yes / browse more)"*
3. Writes to `manifest/custom/actors/{name}.md`
4. Confirms: *"[Name] added. Say `change actor to [name]` to activate."*
5. Commits.

If not found: *"No actor matched '[query]'. Say 'show me who's available' to browse the full roster."*

## sync from mtx

Triggers:
- Power user: "sync actors from mtx" | "pull all from mtx" | "update actors from agent-assets" | "sync mtx"
- Natural language: "update my actors" | "refresh available actors" | "are my actors up to date?"

Update all currently-installed mtx actors to their latest versions. Scribe:
1. Scans `manifest/custom/actors/` for files whose frontmatter has `author: cordfuse`
2. For each, fetches the latest from `https://raw.githubusercontent.com/cordfuse/agent-assets/main/actors/{name}.md`
3. Overwrites only cordfuse-authored files — never touches user-created custom actors
4. Reports: *"Updated N actors from agent-assets. [list of names]"*
5. Commits.

---

### Multi-Session (v4.0.0-alpha.17+)

## spawn session

Triggers: "spawn session [name]" | "new session [name]" | "start a new session called [name]" | "create session [name]"

Create a new scoped session. Scribe generates GUID, writes `data/sessions/{guid}/context.md`, commits, pushes, and switches the chat to the new session. If no name given, scribe asks.

## list sessions

Triggers: "list sessions" | "show my sessions" | "what sessions do I have" | "show sessions"

Show all known sessions. Default: non-closed only, sorted by most recent engagement. Filters: `today`, `this week`, `active`, `detached`, `closed`, `stale`, `on <machine>`, `with <actor>`, `all`. Use `list sessions verbose` to surface GUIDs.

## engage session

Triggers: "engage session [name]" | "open session [name]" | "switch to session [name]" | "go to session [name]"

Attach to an existing session. Scribe finds the session, cross-machine race-checks `last_engaged_at`, updates engagement metadata, commits, pushes, and switches the chat.

## close session

Triggers: "close session [name]" | "archive session [name]" | "end session [name]"

Archive a session. Scribe moves `data/sessions/{guid}/` → `archive/data/sessions/{guid}/`, sets state to `closed`, commits, pushes.

---

### Donations

## donate

Triggers: "donate" | "donations" | "how do I donate" | "support cortex" | "give to camh"

Surface the CAMH Foundation donation link. One-liner response, no filing, no commit. Never solicits unprompted. (v4.0.0-alpha.31+.)

---

### Sync & Reconcile

## reconcile

Triggers: "reconcile" | "deep sync" | "sync --hard" | "reconcile sync" | "full drift check"

Deep three-category diff against `upstream/main` with per-file gating. Catches historical drift that routine `sync` doesn't catch. Each file gated individually; nothing happens silently. See `# Sync flow → Reconcile flow` in manifest/framework/protocol/CORTEX.md (v4.0.0-alpha.19+).

---

> Activate any of the following, or describe a new one.

---

### Work & projects

## morning
Triggers: "morning" | "good morning" | "brief me" | "daily brief" | "morning brief" | "what's on today"
Deliver today's Daily Briefing — appointments, carried open items, a health note, heads-up — assembled from context.md, records, rollups, and connectors where reachable. Files to `data/briefings/YYYY-MM-DD.md`. Also auto-surfaces at the first hello of a new day; this verb is the on-demand form and the primary path for continuous-thread/mobile users. See the Daily Briefing section in `protocol/CORTEX.md`.

<!--
## standup
Run a quick standup: what I did yesterday, what I'm doing today, any blockers. File as a tasks entry.

## tasks
Review and update my open task list. Pull existing tasks records, ask what's done, what's new, what's stuck.

## project
Log progress on a project. Ask which project, what happened, what's next. Use the project template.

## decision
Log a decision — what it was, why, what alternatives were considered. Use the analysis template.

## win
Log an achievement or win, big or small. No filing pressure — just get it on record.

## idea
Fast idea capture. Ask what the idea is, file it immediately, no polish required.
-->

---

### Reflection

## weekly review
Triggers: "weekly review" | "weekly" | "rollup" | "roll up the week" | "how was my week" | "week in review"
Read this ISO week's records, surface patterns and open items, and file the canonical weekly rollup to `data/rollups/YYYY-Www.md`. See the Rollup Layer in `protocol/CORTEX.md`. Cortex also files weekly rollups automatically at the start of the first session of a new week — this verb is the on-demand form.

## monthly review
Triggers: "monthly review" | "monthly" | "how was my month" | "month in review"
Summarise the month from its weekly rollups (falling back to raw records for any gap) and file the canonical monthly rollup to `data/rollups/YYYY-MM.md`.

## patterns
Triggers: "patterns" | "any patterns" | "what do you see" | "what patterns" | "connect the dots"
Read across rollups (monthly, then weekly) and drill into raw records for specifics — surface recurring themes, correlations, escalations, and connections you might not have noticed. **Observational only, never advice** (see the Patterns section in `protocol/CORTEX.md`). Every observation cites the records/rollups behind it. Scope defaults to all history via rollups; narrow with "patterns this month". Nothing filed unless you ask.

## weave
Triggers: "weave" | "link my records" | "build the graph" | "cross-link everything" | "connect my records"
Add `[[wikilink]]` cross-links between related records so the flat record becomes a navigable graph (and Obsidian's graph view fills in). New records are linked automatically at filing; `weave` backfills the existing corpus. Only the derived `## Related` block is touched — record content is never edited (the sole exception to record immutability). Regenerable, batch-committed, conservative (high-confidence links only). See the Record Linking section in `protocol/CORTEX.md`.

## handoff
Triggers: "handoff" | "prep for appointment" | "appointment prep" | "prep for my doctor" | "summary for my doctor" | "clinician summary"
Compile a one-page current-state summary for a clinician from your own records — current meds, recent trends, active concerns, relevant history, changes since last visit, questions to raise. Ask who it's for (scopes the content). Files to `data/handoffs/YYYY-MM-DD-[who].md`. **Organises your records for a clinician; never diagnoses or advises** (see the Appointment Handoff section in `protocol/CORTEX.md`).

## safety
Triggers: "safety" | "safety plan" | "my safety plan" | "crisis resources" | "I need support"
Surface your own safety plan (`manifest/custom/protocol/SAFETY.md`, if you've made one) plus standard crisis lines — on demand, any time, nothing filed. If you haven't made a plan yet, offers to help build one from the safety-plan template. The calm, on-demand companion to the reactive crisis response in GUARDRAILS. **Cortex routes to help; it is not a crisis service.** See the Safety Plan section in `protocol/CORTEX.md`.

<!--
## open items
List every open, unresolved, or flagged item across all records. Nothing filed, just a list. (Alias: *open*.)

## vent
I need to talk. Listen, reflect, don't advise. File only if I ask.
-->

---

### Connectors
> Requires the relevant integration to be set up. See [manifest/framework/CONNECTORS.md](manifest/framework/CONNECTORS.md).

<!--
## calendar
Pull this week's calendar events from Google or Microsoft 365. Summarise and ask if anything needs filing.

## mail
Pull and summarise recent emails from Gmail or Outlook. Flag anything that needs action.

## sync tasks
Pull open tasks from Google Tasks or Microsoft To Do. Merge with my current tasks record. (Alias: *tasks-sync*.)

## drive
Check recent files in Google Drive or OneDrive. Ask if anything needs to come into data/attachments/.

## contacts
Look up a person in Google or Microsoft contacts. Useful for filing person records.

## nas
Connect to my home NAS via Tailscale and rclone. Browse available files or pull into data/attachments/.

## backup
Push my data/attachments/ folder to remote storage via rclone.

## pull files
Pull files from a configured rclone remote into data/attachments/. (Alias: *pull-files*.)

## vpn
Check Tailscale status. Bring it up if it's down.
-->

---

<!-- The scribe manages this file. Users never edit it manually. -->
