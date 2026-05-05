# Cortex Upgrade Preferences

Controls how the scribe handles framework version updates at `hello`.

---

auto_upgrade: ask
skipped_versions:

---

## Options

**`auto_upgrade:`**
- `ask` — present options at every new version (default)
- `always` — sync silently, note it in the greeting
- `never` — notify once per version, never sync automatically

**`skipped_versions:`** — comma-separated list of versions to never ask about again (e.g. `3.4.1, 3.4.2`). Managed by the scribe when you choose "Skip this version."

The `sync` verb always runs a manual sync regardless of this setting.
