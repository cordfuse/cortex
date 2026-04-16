# Google Integration Setup

One-time setup. Takes about 5 minutes. Covers Calendar, Gmail, Drive, Tasks, and Contacts.

---

## 1. Create a Google Cloud project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click the project dropdown at the top → **New Project**
3. Name it anything (e.g. `cortex`) → **Create**

---

## 2. Enable the APIs

In your new project:

1. Go to **APIs & Services → Library**
2. Search and enable each of these:
   - **Google Calendar API**
   - **Gmail API**
   - **Google Drive API**
   - **Google Tasks API**
   - **People API**

---

## 3. Create OAuth credentials

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. If prompted, configure the OAuth consent screen first:
   - User type: **External**
   - App name: anything
   - Add your own email as a test user
   - Scopes: add Calendar, Gmail, Drive (read-only is fine)
4. Back in Create Credentials → OAuth client ID:
   - Application type: **Desktop app**
   - Name: anything
   - Click **Create**
5. Download the credentials — or just copy the **Client ID** and **Client Secret**

---

## 4. Run auth

```bash
python scripts/integrations/google.py auth
```

Enter your Client ID and Client Secret when prompted. A browser window will open — log in and approve access. Your credentials are stored encrypted in the vault.

---

## 5. Pull data

```bash
python scripts/integrations/google.py calendar --days 7
python scripts/integrations/google.py gmail --count 20
python scripts/integrations/google.py drive --count 20
python scripts/integrations/google.py tasks
python scripts/integrations/google.py contacts
```

Or just ask your scribe: *"Pull my calendar for the week."*

---

## Notes

- Credentials are stored in `cortex.secrets.enc` — AES-256 encrypted, safe to commit
- Committing the vault file syncs your credentials across devices
- To revoke access at any time: Google Account → Security → Third-party apps
