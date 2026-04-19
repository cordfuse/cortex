# Cortex — Connectors

Store credentials once in the encrypted vault. Ask your scribe to pull data — it retrieves credentials, calls the service, and offers to file the result.

```bash
python scripts/secrets.py store <name> --description "what this is"
python scripts/secrets.py list
python scripts/secrets.py repassphrase    # rotate the global passphrase
```

---

## Built

### Tailscale — mesh VPN

Reach your home network, NAS, or desktop from any device over a private encrypted tunnel.

```bash
python scripts/integrations/tailscale.py auth             # store auth key in vault
python scripts/integrations/tailscale.py up               # connect
python scripts/integrations/tailscale.py peers            # list devices + IPs
python scripts/integrations/tailscale.py ip <hostname>    # get a peer's IP
python scripts/integrations/tailscale.py down             # disconnect
```

Get an auth key: [tailscale.com/admin/settings/keys](https://login.tailscale.com/admin/settings/keys) — create a reusable key, store it with `tailscale.py auth`.

---

### rclone — any filesystem

Pull from and push to any filesystem — NAS, cloud storage, SFTP, local drives. 70+ backends supported. Config is stored in the vault, never written to disk unencrypted.

```bash
python scripts/integrations/rclone.py auth                  # store rclone config in vault
python scripts/integrations/rclone.py remotes               # list configured remotes
python scripts/integrations/rclone.py ls <remote:path>      # list files
python scripts/integrations/rclone.py pull <remote:path>    # pull files to docs/
python scripts/integrations/rclone.py push <remote:path>    # push files to remote
python scripts/integrations/rclone.py mount <remote:path>   # mount as local filesystem
```

Combine with Tailscale: use `tailscale.py ip <hostname>` to get your NAS IP, then configure an SFTP remote in rclone pointing to that IP.

---

### Google

Calendar, Gmail, Drive, Tasks, Contacts.

```bash
python scripts/integrations/google.py auth               # one-time OAuth setup
python scripts/integrations/google.py calendar --days 7
python scripts/integrations/google.py gmail --count 20
python scripts/integrations/google.py drive --count 20
python scripts/integrations/google.py tasks
python scripts/integrations/google.py contacts --count 50
```

> **Google Keep is not supported.** Google has never released a public API for Keep.

---

### Microsoft 365

Mail, Calendar, OneDrive, Teams, SharePoint, To Do, Planner, OneNote. One Azure app registration covers everything.

```bash
python scripts/integrations/microsoft.py auth            # one-time OAuth setup
python scripts/integrations/microsoft.py mail --count 20
python scripts/integrations/microsoft.py calendar --days 7
python scripts/integrations/microsoft.py onedrive --count 20
python scripts/integrations/microsoft.py teams --count 20
python scripts/integrations/microsoft.py sharepoint --count 20
python scripts/integrations/microsoft.py todo
python scripts/integrations/microsoft.py planner
python scripts/integrations/microsoft.py onenote --count 20
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
