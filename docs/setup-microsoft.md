# Microsoft 365 Integration Setup

One-time setup. Takes about 10 minutes. One Azure app registration covers all services — Mail, Calendar, OneDrive, Teams, SharePoint, To Do, Planner, OneNote.

---

## 1. Register an Azure app

1. Go to [portal.azure.com](https://portal.azure.com)
2. Search for **Azure Active Directory** → **App registrations**
3. Click **New registration**
   - Name: anything (e.g. `cortex`)
   - Supported account types: **Accounts in any organizational directory and personal Microsoft accounts**
   - Redirect URI: **Public client/native** → `http://localhost`
4. Click **Register**
5. Copy the **Application (client) ID** — you'll need it shortly
6. Copy the **Directory (tenant) ID** — or use `common` for personal accounts

---

## 2. Create a client secret

1. In your app registration → **Certificates & secrets**
2. Click **New client secret**
3. Set an expiry (24 months is fine)
4. Click **Add** — copy the **Value** immediately (you won't see it again)

---

## 3. Add API permissions

1. In your app registration → **API permissions**
2. Click **Add a permission → Microsoft Graph → Delegated permissions**
3. Add each of these:
   - `Mail.Read`
   - `Calendars.Read`
   - `Files.Read.All`
   - `Chat.Read`
   - `ChannelMessage.Read.All`
   - `Sites.Read.All`
   - `Tasks.Read`
   - `Notes.Read.All`
   - `offline_access`
   - `User.Read`
4. Click **Grant admin consent** if you have admin rights — otherwise your users will be prompted on first login

---

## 4. Run auth

```bash
python scripts/integrations/microsoft.py auth
```

Enter your Tenant ID (or `common`), Client ID, and Client Secret when prompted. A device code will appear — open the URL shown, enter the code, and log in. Your credentials are stored encrypted in the vault.

---

## 5. Pull data

```bash
python scripts/integrations/microsoft.py mail
python scripts/integrations/microsoft.py calendar --days 7
python scripts/integrations/microsoft.py onedrive
python scripts/integrations/microsoft.py teams
python scripts/integrations/microsoft.py sharepoint
python scripts/integrations/microsoft.py todo
python scripts/integrations/microsoft.py planner
python scripts/integrations/microsoft.py onenote
```

Or just ask your scribe: *"What's unread in Teams?"*, *"Pull my Outlook calendar"*, *"Show my open To Do tasks."*

---

## Notes

- Credentials are stored in `cortex.secrets/` — AES-256 encrypted, one file per secret, safe to commit
- Committing the vault file syncs your credentials across devices
- One app registration covers all Microsoft 365 services — no separate setup per service
- To revoke access: [myapps.microsoft.com](https://myapps.microsoft.com) → remove Cortex
- Personal Microsoft accounts (Outlook.com, Hotmail) use tenant ID `common`
- Teams and SharePoint permissions may require admin consent in corporate tenants
