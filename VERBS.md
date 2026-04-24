# Custom Verbs

Custom session commands — call them with a `/` prefix (e.g. `/weekly`).

**To activate a verb:** just ask — *"activate /weekly"* or *"turn on /calendar"*. The scribe enables it and commits.  
**To deactivate:** *"deactivate /meds"*. The scribe disables it and commits.  
**To add your own:** describe what you want — the scribe writes it, adds it here, and commits.

`list verbs` shows everything currently active alongside the built-ins.

---

## Available verbs

---

### Personality

## /personality
Switch active personality. Usage: `/personality bob`, `/personality sherlock`, `/personality [name]`. Scribe updates `personality:` in `context.md` and commits. Takes effect at next `hello`. To see what's available: `list personalities`.

---

> Activate any of the following, or describe a new one.

---

### Health & daily life

<!--
## /daily
Open a daily log entry. Ask how I'm doing, what happened today, anything worth filing. Use the day template.

## /meds
Log medications taken today — name, dose, time, any notes. Use the medication template.

## /symptoms
Log current symptoms — what, when, severity, context. Use the symptoms template.

## /mood
Quick mood and energy snapshot. One or two questions, then file a short entry.

## /sleep
Log last night's sleep — hours, quality, anything notable on waking.

## /vitals
Log health vitals — blood pressure, blood sugar, weight, or whatever I track. Ask what I'm logging.

## /appt
Log an appointment — who, when, what was discussed, any follow-ups. Use the appointment template.

## /therapy
Log a therapy session — what came up, what shifted, anything to follow. Use the session template.
-->

---

### Work & projects

<!--
## /standup
Run a quick standup: what I did yesterday, what I'm doing today, any blockers. File as a tasks entry.

## /tasks
Review and update my open task list. Pull existing tasks records, ask what's done, what's new, what's stuck.

## /project
Log progress on a project. Ask which project, what happened, what's next. Use the project template.

## /decision
Log a decision — what it was, why, what alternatives were considered. Use the analysis template.

## /win
Log an achievement or win, big or small. No filing pressure — just get it on record.

## /idea
Fast idea capture. Ask what the idea is, file it immediately, no polish required.
-->

---

### Finance

<!--
## /bills
Review upcoming bills. Cross-reference my finance records. List what's due this week with amounts and methods.

## /spend
Log a purchase or expense — what, amount, category, notes.

## /budget
Review current financial picture. Pull recent finance records and summarise.
-->

---

### Reflection

<!--
## /weekly
Weekly review. Read all records from the past 7 days. Surface patterns, open items, anything unresolved. Ask if I want to file a summary.

## /monthly
Monthly review. Read all records from the past 30 days. Summarise themes, progress, and anything I want to carry forward.

## /patterns
Look across all records and tell me what you see — recurring themes, escalations, connections I might have missed.

## /open
List every open, unresolved, or flagged item across all records. Nothing filed, just a list.

## /vent
I need to talk. Listen, reflect, don't advise. File only if I ask.
-->

---

### Connectors
> Requires the relevant integration to be set up. See [docs/CONNECTORS.md](docs/CONNECTORS.md).

<!--
## /calendar
Pull this week's calendar events from Google or Microsoft 365. Summarise and ask if anything needs filing.

## /mail
Pull and summarise recent emails from Gmail or Outlook. Flag anything that needs action.

## /tasks-sync
Pull open tasks from Google Tasks or Microsoft To Do. Merge with my current tasks record.

## /drive
Check recent files in Google Drive or OneDrive. Ask if anything needs to come into docs/.

## /contacts
Look up a person in Google or Microsoft contacts. Useful for filing person records.

## /nas
Connect to my home NAS via Tailscale and rclone. Browse available files or pull into docs/.

## /backup
Push my docs/ folder to remote storage via rclone.

## /pull-files
Pull files from a configured rclone remote into docs/.

## /vpn
Check Tailscale status. Bring it up if it's down.
-->

---

<!-- The scribe manages this file. Users never edit it manually. -->
