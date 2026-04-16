#!/usr/bin/env python3
"""
Cortex Microsoft 365 integration — Mail, Calendar, OneDrive, Teams,
SharePoint, To Do, Planner, OneNote.

All services use a single Azure app registration (one auth, everything covered).

One-time setup:
  1. Go to https://portal.azure.com → Azure Active Directory → App registrations
  2. New registration — name it anything, set redirect URI to http://localhost
  3. Under API permissions, add Microsoft Graph delegated permissions:
       Mail.Read, Calendars.Read, Files.Read.All, Chat.Read,
       ChannelMessage.Read.All, Sites.Read.All, Tasks.Read,
       Notes.Read.All, offline_access, User.Read
  4. Under Certificates & secrets, create a client secret — copy it immediately
  5. Run: python scripts/integrations/microsoft.py auth

Usage:
  python scripts/integrations/microsoft.py auth [--passphrase <p>]
  python scripts/integrations/microsoft.py mail [--count 20] [--passphrase <p>]
  python scripts/integrations/microsoft.py calendar [--days 7] [--passphrase <p>]
  python scripts/integrations/microsoft.py onedrive [--count 20] [--passphrase <p>]
  python scripts/integrations/microsoft.py teams [--count 20] [--passphrase <p>]
  python scripts/integrations/microsoft.py sharepoint [--count 20] [--passphrase <p>]
  python scripts/integrations/microsoft.py todo [--passphrase <p>]
  python scripts/integrations/microsoft.py planner [--passphrase <p>]
  python scripts/integrations/microsoft.py onenote [--count 20] [--passphrase <p>]

Requires: pip install msal requests
"""

import os
import sys
import json
import argparse
import subprocess
import getpass
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

SCOPES = [
    "Mail.Read",
    "Calendars.Read",
    "Files.Read.All",
    "Chat.Read",
    "ChannelMessage.Read.All",
    "Sites.Read.All",
    "Tasks.Read",
    "Notes.Read.All",
    "offline_access",
    "User.Read",
]

try:
    import msal
    import requests
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Run: pip install msal requests")
    sys.exit(1)


# ── Vault helpers ─────────────────────────────────────────────────────────────

def get_secret(name: str, passphrase: str) -> str:
    secrets_script = os.path.join(ROOT, "scripts", "secrets.py")
    result = subprocess.run(
        [sys.executable, secrets_script, "get", name, "--passphrase", passphrase],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR: Could not retrieve '{name}' from vault.")
        print("Run: python scripts/integrations/microsoft.py auth")
        sys.exit(1)
    return result.stdout.strip()


def store_secret(name: str, value: str, passphrase: str):
    secrets_script = os.path.join(ROOT, "scripts", "secrets.py")
    subprocess.run(
        [sys.executable, secrets_script, "store", name,
         "--value", value, "--passphrase", passphrase],
        check=True
    )


# ── Auth ──────────────────────────────────────────────────────────────────────

def get_access_token(passphrase: str) -> str:
    client_id = get_secret("msft_client_id", passphrase)
    client_secret = get_secret("msft_client_secret", passphrase)
    refresh_token = get_secret("msft_refresh_token", passphrase)
    tenant_id = get_secret("msft_tenant_id", passphrase)

    app = msal.ConfidentialClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=client_secret,
    )

    result = app.acquire_token_by_refresh_token(refresh_token, scopes=SCOPES)

    if "access_token" not in result:
        print("ERROR: Token refresh failed.")
        print(result.get("error_description", ""))
        sys.exit(1)

    # Store updated refresh token if rotated
    if "refresh_token" in result and result["refresh_token"] != refresh_token:
        store_secret("msft_refresh_token", result["refresh_token"], passphrase)

    return result["access_token"]


def graph(token: str, path: str, params: dict = None) -> dict:
    resp = requests.get(
        f"{GRAPH_BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
    )
    if not resp.ok:
        print(f"ERROR: Graph API {path} returned {resp.status_code}")
        print(resp.text[:300])
        sys.exit(1)
    return resp.json()


def cmd_auth(passphrase: str):
    print("Microsoft 365 / Azure OAuth setup")
    print("You need an Azure App Registration with Microsoft Graph permissions.")
    print("https://portal.azure.com → Azure Active Directory → App registrations\n")

    tenant_id = input("Tenant ID (or 'common' for personal accounts): ").strip()
    client_id = input("Client ID (Application ID): ").strip()
    client_secret = input("Client Secret: ").strip()

    app = msal.ConfidentialClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=client_secret,
    )

    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        print("ERROR: Failed to create device flow.")
        print(flow.get("error_description", ""))
        sys.exit(1)

    print(f"\n{flow['message']}\n")
    result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        print("ERROR: Authentication failed.")
        print(result.get("error_description", ""))
        sys.exit(1)

    store_secret("msft_tenant_id", tenant_id, passphrase)
    store_secret("msft_client_id", client_id, passphrase)
    store_secret("msft_client_secret", client_secret, passphrase)
    store_secret("msft_refresh_token", result["refresh_token"], passphrase)

    print("\nCredentials stored in vault.")
    print("Commit cortex.secrets.enc to persist across devices.")


# ── Mail ──────────────────────────────────────────────────────────────────────

def cmd_mail(count: int, passphrase: str):
    token = get_access_token(passphrase)
    data = graph(token, "/me/mailFolders/inbox/messages", {
        "$top": count,
        "$filter": "isRead eq false",
        "$orderby": "receivedDateTime desc",
        "$select": "subject,from,receivedDateTime,bodyPreview",
    })

    messages = data.get("value", [])
    if not messages:
        print("No unread messages.")
        return

    print(f"# Outlook Mail — {len(messages)} unread\n")
    for m in messages:
        subject = m.get("subject", "(no subject)")
        sender = m.get("from", {}).get("emailAddress", {}).get("address", "")
        received = m.get("receivedDateTime", "")
        if received:
            received = datetime.fromisoformat(received.replace("Z", "+00:00")).strftime("%d %b %Y %H:%M")
        preview = m.get("bodyPreview", "")[:120]

        print(f"**{subject}**")
        print(f"From: {sender} | {received}")
        if preview:
            print(f"> {preview}...")
        print()


# ── Calendar ──────────────────────────────────────────────────────────────────

def cmd_calendar(days: int, passphrase: str):
    token = get_access_token(passphrase)
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days)

    data = graph(token, "/me/calendarView", {
        "startDateTime": now.isoformat(),
        "endDateTime": end.isoformat(),
        "$top": 50,
        "$orderby": "start/dateTime",
        "$select": "subject,start,end,location,isOnlineMeeting",
    })

    events = data.get("value", [])
    if not events:
        print(f"No events in the next {days} days.")
        return

    print(f"# Outlook Calendar — next {days} days\n")
    for e in events:
        subject = e.get("subject", "(no title)")
        start = e.get("start", {}).get("dateTime", "")
        if start:
            start = datetime.fromisoformat(start).strftime("%a %d %b %H:%M")
        location = e.get("location", {}).get("displayName", "")
        online = " (online)" if e.get("isOnlineMeeting") else ""
        loc_str = f" — {location}" if location else ""
        print(f"- {start}: {subject}{loc_str}{online}")


# ── OneDrive ──────────────────────────────────────────────────────────────────

def cmd_onedrive(count: int, passphrase: str):
    token = get_access_token(passphrase)
    data = graph(token, "/me/drive/recent", {
        "$top": count,
        "$select": "name,lastModifiedDateTime,webUrl,file,folder",
    })

    files = data.get("value", [])
    if not files:
        print("No recent files.")
        return

    print(f"# OneDrive — {count} recently accessed\n")
    for f in files:
        name = f.get("name", "")
        modified = f.get("lastModifiedDateTime", "")
        if modified:
            modified = datetime.fromisoformat(modified.replace("Z", "+00:00")).strftime("%d %b %Y")
        url = f.get("webUrl", "")
        kind = "Folder" if "folder" in f else "File"
        print(f"- [{name}]({url}) ({kind}) — {modified}")


# ── Teams ─────────────────────────────────────────────────────────────────────

def cmd_teams(count: int, passphrase: str):
    token = get_access_token(passphrase)

    chats_data = graph(token, "/me/chats", {
        "$top": 10,
        "$expand": "members",
        "$select": "id,topic,chatType,lastUpdatedDateTime",
    })

    chats = chats_data.get("value", [])
    if not chats:
        print("No Teams chats found.")
        return

    print(f"# Microsoft Teams — recent messages\n")
    shown = 0
    for chat in chats:
        if shown >= count:
            break
        chat_id = chat.get("id")
        topic = chat.get("topic") or "Direct message"
        msgs_data = graph(token, f"/me/chats/{chat_id}/messages", {
            "$top": 5,
            "$select": "from,body,createdDateTime",
        })
        msgs = msgs_data.get("value", [])
        if not msgs:
            continue

        print(f"**{topic}**")
        for msg in msgs:
            sender = msg.get("from", {}).get("user", {}).get("displayName", "Unknown")
            created = msg.get("createdDateTime", "")
            if created:
                created = datetime.fromisoformat(created.replace("Z", "+00:00")).strftime("%d %b %H:%M")
            body = msg.get("body", {}).get("content", "")[:100].replace("\n", " ")
            print(f"  {created} {sender}: {body}")
        print()
        shown += len(msgs)


# ── SharePoint ────────────────────────────────────────────────────────────────

def cmd_sharepoint(count: int, passphrase: str):
    token = get_access_token(passphrase)
    data = graph(token, "/me/followedSites", {
        "$select": "id,name,webUrl,lastModifiedDateTime",
    })

    sites = data.get("value", [])
    if not sites:
        print("No followed SharePoint sites.")
        return

    print(f"# SharePoint — followed sites\n")
    for site in sites[:count]:
        name = site.get("name", "")
        url = site.get("webUrl", "")
        modified = site.get("lastModifiedDateTime", "")
        if modified:
            modified = datetime.fromisoformat(modified.replace("Z", "+00:00")).strftime("%d %b %Y")
        print(f"- [{name}]({url}) — {modified}")


# ── To Do ─────────────────────────────────────────────────────────────────────

def cmd_todo(passphrase: str):
    token = get_access_token(passphrase)
    lists_data = graph(token, "/me/todo/lists", {
        "$select": "id,displayName",
    })

    lists = lists_data.get("value", [])
    if not lists:
        print("No To Do lists found.")
        return

    print("# Microsoft To Do\n")
    for lst in lists:
        list_id = lst.get("id")
        list_name = lst.get("displayName", "")
        tasks_data = graph(token, f"/me/todo/lists/{list_id}/tasks", {
            "$filter": "status ne 'completed'",
            "$select": "title,importance,dueDateTime,status",
            "$top": 20,
        })
        tasks = tasks_data.get("value", [])
        if not tasks:
            continue
        print(f"**{list_name}**")
        for t in tasks:
            title = t.get("title", "")
            importance = t.get("importance", "normal")
            due = t.get("dueDateTime", {})
            due_str = ""
            if due and due.get("dateTime"):
                due_str = f" (due {datetime.fromisoformat(due['dateTime']).strftime('%d %b')})"
            flag = " !" if importance == "high" else ""
            print(f"  - {title}{due_str}{flag}")
        print()


# ── Planner ───────────────────────────────────────────────────────────────────

def cmd_planner(passphrase: str):
    token = get_access_token(passphrase)
    plans_data = graph(token, "/me/planner/tasks", {
        "$select": "title,percentComplete,dueDateTime,planId,bucketId",
        "$filter": "percentComplete lt 100",
        "$top": 50,
    })

    tasks = plans_data.get("value", [])
    if not tasks:
        print("No open Planner tasks.")
        return

    print("# Microsoft Planner — open tasks\n")
    for t in tasks:
        title = t.get("title", "")
        pct = t.get("percentComplete", 0)
        due = t.get("dueDateTime", "")
        due_str = ""
        if due:
            due_str = f" (due {datetime.fromisoformat(due.replace('Z', '+00:00')).strftime('%d %b')})"
        progress = f" [{pct}%]" if pct else ""
        print(f"- {title}{due_str}{progress}")


# ── OneNote ───────────────────────────────────────────────────────────────────

def cmd_onenote(count: int, passphrase: str):
    token = get_access_token(passphrase)
    data = graph(token, "/me/onenote/pages", {
        "$top": count,
        "$orderby": "lastModifiedDateTime desc",
        "$select": "title,lastModifiedDateTime,parentNotebook,webUrl",
    })

    pages = data.get("value", [])
    if not pages:
        print("No OneNote pages found.")
        return

    print(f"# OneNote — {count} recently modified\n")
    for p in pages:
        title = p.get("title", "(untitled)")
        modified = p.get("lastModifiedDateTime", "")
        if modified:
            modified = datetime.fromisoformat(modified.replace("Z", "+00:00")).strftime("%d %b %Y")
        notebook = p.get("parentNotebook", {}).get("displayName", "")
        url = p.get("webUrl", "")
        nb_str = f" [{notebook}]" if notebook else ""
        print(f"- [{title}]({url}){nb_str} — {modified}")


# ── Main ──────────────────────────────────────────────────────────────────────

def prompt_passphrase() -> str:
    return getpass.getpass("Vault passphrase: ")


def main():
    parser = argparse.ArgumentParser(description="Cortex Microsoft 365 integration")
    parser.add_argument("--passphrase", default=None)
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("auth", help="Azure OAuth setup — run once")

    p_mail = sub.add_parser("mail", help="Unread Outlook mail")
    p_mail.add_argument("--count", type=int, default=20)

    p_cal = sub.add_parser("calendar", help="Upcoming calendar events")
    p_cal.add_argument("--days", type=int, default=7)

    p_od = sub.add_parser("onedrive", help="Recently accessed OneDrive files")
    p_od.add_argument("--count", type=int, default=20)

    p_teams = sub.add_parser("teams", help="Recent Teams messages")
    p_teams.add_argument("--count", type=int, default=20)

    p_sp = sub.add_parser("sharepoint", help="Followed SharePoint sites")
    p_sp.add_argument("--count", type=int, default=20)

    sub.add_parser("todo", help="Open To Do tasks")
    sub.add_parser("planner", help="Open Planner tasks")

    p_on = sub.add_parser("onenote", help="Recently modified OneNote pages")
    p_on.add_argument("--count", type=int, default=20)

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    passphrase = args.passphrase or prompt_passphrase()

    if args.cmd == "auth":
        cmd_auth(passphrase)
    elif args.cmd == "mail":
        cmd_mail(args.count, passphrase)
    elif args.cmd == "calendar":
        cmd_calendar(args.days, passphrase)
    elif args.cmd == "onedrive":
        cmd_onedrive(args.count, passphrase)
    elif args.cmd == "teams":
        cmd_teams(args.count, passphrase)
    elif args.cmd == "sharepoint":
        cmd_sharepoint(args.count, passphrase)
    elif args.cmd == "todo":
        cmd_todo(passphrase)
    elif args.cmd == "planner":
        cmd_planner(passphrase)
    elif args.cmd == "onenote":
        cmd_onenote(args.count, passphrase)


if __name__ == "__main__":
    main()
