# Custom Verbs

Custom session commands the scribe knows about. Invoked by **natural language** — say what you want, the scribe routes the intent.

**To activate a verb:** just ask — *"activate weekly review"* or *"turn on calendar"*. The scribe enables it and commits.
**To deactivate:** *"deactivate medication logging"* or *"turn off meds"*. The scribe disables it and commits.
**To add your own:** describe what you want — the scribe writes it, adds it here, and commits.

`list verbs` shows everything currently active alongside the built-ins.

> **No slash prefixes.** Cortex uses natural language. `/weekly` etc. are not used — many AI client UIs (Claude web, ChatGPT, Gemini web) intercept slash prefixes as their own native commands before the scribe ever sees them. Custom verb names must not collide with built-in verb names (`hello`, `goodbye`, `status`, `sync`, `search`, `list verbs`, `list personalities`, `list actors`).

---

## Available verbs

---

### Personality

## switch personality
Switch active personality. Usage: *"switch personality to casey"*, *"change actor to atlas"*, *"use [name]"*. Scribe updates `personality:` in `context.md`, commits, and **hot-swaps to the new actor immediately** — the next response is in the new voice, no fresh hello required (v4.0.0-alpha.8+). To see what's available: `list personalities`. (Aliases: *change actor*, *use*.)

---

### Multi-Session (v4.0.0-alpha.17+)

## spawn session
Create a new scoped session. Usage: *"spawn session <name>"* / *"new session <name>"*. Scribe generates GUID, writes `sessions/{guid}/context.md`, commits, pushes, and switches the chat to the new session. If no name given, scribe asks; user can `skip` and get an `untitled-<datetime>-<guid-prefix>` placeholder. Naming collisions with active sessions refused; closed names are reusable. See `# Multi-Session` in protocol/CORTEX.md.

## list sessions
Show all known sessions. Default: non-closed only, sorted by most recent engagement. Filters: `today`, `this week`, `active`, `detached`, `closed`, `stale`, `on <machine>`, `with <actor>`, `all`. Output is one line per session: `<name> (<state>) | spawned: <date> | last engaged: <datetime> | actor: <name>`. GUIDs hidden by default; use `list sessions verbose` to surface them.

## engage session
Attach to an existing session. Usage: *"engage session <name>"* / *"open session <name>"*. Scribe finds the session, cross-machine race-checks `last_engaged_at`, warns on archived state, updates engagement metadata, commits, pushes, and switches the chat. If the named session is archived, scribe surfaces a re-engage prompt before restoring.

## close session
Archive a session. Usage: *"close session <name>"*. Scribe moves `sessions/{guid}/` → `archive/sessions/{guid}/`, sets state to `closed`, commits, pushes. The friendly name is freed for reuse immediately. If the closed session was the currently-engaged one, the chat returns to main session.

---

> Activate any of the following, or describe a new one.

---

### Health & daily life

<!--
## daily log
Open a daily log entry. Ask how I'm doing, what happened today, anything worth filing. Use the day template.

## meds
Log medications taken today — name, dose, time, any notes. Use the medication template.

## symptoms
Log current symptoms — what, when, severity, context. Use the symptoms template.

## mood
Quick mood and energy snapshot. One or two questions, then file a short entry.

## sleep
Log last night's sleep — hours, quality, anything notable on waking.

## vitals
Log health vitals — blood pressure, blood sugar, weight, or whatever I track. Ask what I'm logging.

## appointment
Log an appointment — who, when, what was discussed, any follow-ups. Use the appointment template. (Alias: *appt*.)

## therapy
Log a therapy session — what came up, what shifted, anything to follow. Use the session template.
-->

---

### Work & projects

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

### Finance

<!--
## bills
Review upcoming bills. Cross-reference my finance records. List what's due this week with amounts and methods.

## spend
Log a purchase or expense — what, amount, category, notes.

## budget
Review current financial picture. Pull recent finance records and summarise.
-->

---

### Reflection

<!--
## weekly review
Read all records from the past 7 days. Surface patterns, open items, anything unresolved. Ask if I want to file a summary. (Alias: *weekly*.)

## monthly review
Read all records from the past 30 days. Summarise themes, progress, and anything I want to carry forward. (Alias: *monthly*.)

## patterns
Look across all records and tell me what you see — recurring themes, escalations, connections I might have missed.

## open items
List every open, unresolved, or flagged item across all records. Nothing filed, just a list. (Alias: *open*.)

## vent
I need to talk. Listen, reflect, don't advise. File only if I ask.
-->

---

### Connectors
> Requires the relevant integration to be set up. See [docs/CONNECTORS.md](docs/CONNECTORS.md).

<!--
## calendar
Pull this week's calendar events from Google or Microsoft 365. Summarise and ask if anything needs filing.

## mail
Pull and summarise recent emails from Gmail or Outlook. Flag anything that needs action.

## sync tasks
Pull open tasks from Google Tasks or Microsoft To Do. Merge with my current tasks record. (Alias: *tasks-sync*.)

## drive
Check recent files in Google Drive or OneDrive. Ask if anything needs to come into docs/.

## contacts
Look up a person in Google or Microsoft contacts. Useful for filing person records.

## nas
Connect to my home NAS via Tailscale and rclone. Browse available files or pull into docs/.

## backup
Push my docs/ folder to remote storage via rclone.

## pull files
Pull files from a configured rclone remote into docs/. (Alias: *pull-files*.)

## vpn
Check Tailscale status. Bring it up if it's down.
-->

---

<!-- The scribe manages this file. Users never edit it manually. -->
