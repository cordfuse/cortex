# Cortex — Connectors

Store credentials once in the encrypted vault. Ask your scribe to pull data — it retrieves credentials, calls the service, and offers to file the result.

```bash
bun manifest/framework/scripts/secrets.ts store <name> --description "what this is"
bun manifest/framework/scripts/secrets.ts list
bun manifest/framework/scripts/secrets.ts repassphrase    # rotate the global passphrase
```

---

## Built

### Tailscale — mesh VPN

Reach your home network, NAS, or desktop from any device over a private encrypted tunnel.

```bash
bun manifest/framework/scripts/integrations/tailscale.ts auth             # store auth key in vault
bun manifest/framework/scripts/integrations/tailscale.ts up               # connect
bun manifest/framework/scripts/integrations/tailscale.ts peers            # list devices + IPs
bun manifest/framework/scripts/integrations/tailscale.ts ip <hostname>    # get a peer's IP
bun manifest/framework/scripts/integrations/tailscale.ts down             # disconnect
```

Get an auth key: [tailscale.com/admin/settings/keys](https://login.tailscale.com/admin/settings/keys) — create a reusable key, store it with `tailscale.ts auth`.

---

### rclone — any filesystem

Pull from and push to any filesystem — NAS, cloud storage, SFTP, local drives. 70+ backends supported. Config is stored in the vault, never written to disk unencrypted.

```bash
bun manifest/framework/scripts/integrations/rclone.ts auth                  # store rclone config in vault
bun manifest/framework/scripts/integrations/rclone.ts remotes               # list configured remotes
bun manifest/framework/scripts/integrations/rclone.ts ls <remote:path>      # list files
bun manifest/framework/scripts/integrations/rclone.ts pull <remote:path>    # pull files to data/attachments/
bun manifest/framework/scripts/integrations/rclone.ts push <remote:path>    # push files to remote
bun manifest/framework/scripts/integrations/rclone.ts mount <remote:path>   # mount as local filesystem
```

Combine with Tailscale: use `tailscale.ts ip <hostname>` to get your NAS IP, then configure an SFTP remote in rclone pointing to that IP.

---

### Google

Calendar, Gmail, Drive, Tasks, Contacts.

```bash
bun manifest/framework/scripts/integrations/google.ts auth               # one-time OAuth setup
bun manifest/framework/scripts/integrations/google.ts calendar --days 7
bun manifest/framework/scripts/integrations/google.ts gmail --count 20
bun manifest/framework/scripts/integrations/google.ts drive --count 20
bun manifest/framework/scripts/integrations/google.ts tasks
bun manifest/framework/scripts/integrations/google.ts contacts --count 50
```

> **Google Keep is not supported.** Google has never released a public API for Keep.

---

### Microsoft 365

Mail, Calendar, OneDrive, Teams, SharePoint, To Do, Planner, OneNote. One Azure app registration covers everything.

```bash
bun manifest/framework/scripts/integrations/microsoft.ts auth            # one-time OAuth setup
bun manifest/framework/scripts/integrations/microsoft.ts mail --count 20
bun manifest/framework/scripts/integrations/microsoft.ts calendar --days 7
bun manifest/framework/scripts/integrations/microsoft.ts onedrive --count 20
bun manifest/framework/scripts/integrations/microsoft.ts teams --count 20
bun manifest/framework/scripts/integrations/microsoft.ts sharepoint --count 20
bun manifest/framework/scripts/integrations/microsoft.ts todo
bun manifest/framework/scripts/integrations/microsoft.ts planner
bun manifest/framework/scripts/integrations/microsoft.ts onenote --count 20
```

---

## Roadmap

| Connector | What it will do |
|---|---|
| Notion | Pages, databases, tasks |
| Apple iCloud | Calendar, Reminders, Notes |
| Slack | Messages, channels, threads |
| GitHub | Issues, PRs, notifications |
| Linear | Issues, projects, cycles |
| Apple Health | Activity, sleep, vitals |
| Fitbit / Garmin | Activity, sleep, heart rate |
| Spotify | Listening history, playlists |
| Banking (OFX/CSV) | Transactions, balances |
| WhatsApp / SMS | Message history (export-based) |

> Want a connector that isn't listed? [Open an issue](https://github.com/cordfuse/cortex/issues).
