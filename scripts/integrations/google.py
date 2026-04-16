#!/usr/bin/env python3
"""
Cortex Google integration — Calendar, Gmail, Drive.

Credentials are stored in the Cortex secrets vault (cortex.secrets.enc).
Run once to set up:
  python scripts/secrets.py store google_client_id
  python scripts/secrets.py store google_client_secret
  python scripts/secrets.py store google_refresh_token

To get a refresh token, run:
  python scripts/integrations/google.py auth

Usage:
  python scripts/integrations/google.py calendar [--days 7] [--passphrase <p>]
  python scripts/integrations/google.py gmail [--count 20] [--passphrase <p>]
  python scripts/integrations/google.py drive [--count 20] [--passphrase <p>]
  python scripts/integrations/google.py auth [--passphrase <p>]

Requires: pip install google-auth google-auth-oauthlib google-api-python-client
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Google client libraries not installed.")
    print("Run: pip install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)


def get_secret(name: str, passphrase: str) -> str:
    secrets_script = os.path.join(ROOT, "scripts", "secrets.py")
    result = subprocess.run(
        [sys.executable, secrets_script, "get", name, "--passphrase", passphrase],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR: Could not retrieve '{name}' from vault.")
        print("Run: python scripts/integrations/google.py auth")
        sys.exit(1)
    return result.stdout.strip()


def store_secret(name: str, value: str, passphrase: str):
    secrets_script = os.path.join(ROOT, "scripts", "secrets.py")
    subprocess.run(
        [sys.executable, secrets_script, "store", name,
         "--value", value, "--passphrase", passphrase],
        check=True
    )


def get_credentials(passphrase: str) -> Credentials:
    client_id = get_secret("google_client_id", passphrase)
    client_secret = get_secret("google_client_secret", passphrase)
    refresh_token = get_secret("google_refresh_token", passphrase)

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def cmd_auth(passphrase: str):
    """Interactive OAuth flow — run once to generate a refresh token."""
    import getpass as gp

    print("Google OAuth setup")
    print("You need a Google Cloud project with Calendar, Gmail, and Drive APIs enabled.")
    print("https://console.cloud.google.com/apis/credentials\n")

    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)

    store_secret("google_client_id", client_id, passphrase)
    store_secret("google_client_secret", client_secret, passphrase)
    store_secret("google_refresh_token", creds.refresh_token, passphrase)

    print("\nCredentials stored in vault.")
    print("Commit cortex.secrets.enc to persist across devices.")


def cmd_calendar(days: int, passphrase: str):
    creds = get_credentials(passphrase)
    service = build("calendar", "v3", credentials=creds)

    now = datetime.now(timezone.utc)
    time_min = now.isoformat()
    time_max = (now + timedelta(days=days)).isoformat()

    result = service.events().list(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
        maxResults=50,
    ).execute()

    events = result.get("items", [])

    if not events:
        print(f"No events in the next {days} days.")
        return

    print(f"# Google Calendar — next {days} days\n")
    for e in events:
        start = e.get("start", {})
        dt = start.get("dateTime") or start.get("date", "")
        if "T" in dt:
            dt_fmt = datetime.fromisoformat(dt.replace("Z", "+00:00")).strftime("%a %d %b %H:%M")
        else:
            dt_fmt = datetime.fromisoformat(dt).strftime("%a %d %b")
        summary = e.get("summary", "(no title)")
        location = e.get("location", "")
        loc_str = f" — {location}" if location else ""
        print(f"- {dt_fmt}: {summary}{loc_str}")


def cmd_gmail(count: int, passphrase: str):
    creds = get_credentials(passphrase)
    service = build("gmail", "v1", credentials=creds)

    result = service.users().messages().list(
        userId="me",
        maxResults=count,
        labelIds=["INBOX"],
        q="is:unread",
    ).execute()

    messages = result.get("messages", [])

    if not messages:
        print("No unread messages.")
        return

    print(f"# Gmail — {len(messages)} unread\n")
    for msg in messages:
        detail = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
        subject = headers.get("Subject", "(no subject)")
        sender = headers.get("From", "")
        date = headers.get("Date", "")
        snippet = detail.get("snippet", "")[:120]

        print(f"**{subject}**")
        print(f"From: {sender} | {date}")
        if snippet:
            print(f"> {snippet}...")
        print()


def cmd_drive(count: int, passphrase: str):
    creds = get_credentials(passphrase)
    service = build("drive", "v3", credentials=creds)

    result = service.files().list(
        pageSize=count,
        orderBy="modifiedTime desc",
        fields="files(id, name, mimeType, modifiedTime, webViewLink)",
        q="trashed = false",
    ).execute()

    files = result.get("files", [])

    if not files:
        print("No files found.")
        return

    MIME_LABELS = {
        "application/vnd.google-apps.document": "Doc",
        "application/vnd.google-apps.spreadsheet": "Sheet",
        "application/vnd.google-apps.presentation": "Slides",
        "application/vnd.google-apps.folder": "Folder",
        "application/pdf": "PDF",
    }

    print(f"# Google Drive — {count} recently modified\n")
    for f in files:
        name = f.get("name", "")
        mime = f.get("mimeType", "")
        label = MIME_LABELS.get(mime, "File")
        modified = f.get("modifiedTime", "")
        if modified:
            modified = datetime.fromisoformat(modified.replace("Z", "+00:00")).strftime("%d %b %Y")
        link = f.get("webViewLink", "")
        print(f"- [{name}]({link}) ({label}) — modified {modified}")


def prompt_passphrase() -> str:
    import getpass
    return getpass.getpass("Vault passphrase: ")


def main():
    parser = argparse.ArgumentParser(description="Cortex Google integration")
    parser.add_argument("--passphrase", default=None)
    sub = parser.add_subparsers(dest="cmd")

    p_auth = sub.add_parser("auth", help="OAuth setup — run once")

    p_cal = sub.add_parser("calendar", help="Upcoming calendar events")
    p_cal.add_argument("--days", type=int, default=7)

    p_gmail = sub.add_parser("gmail", help="Unread Gmail messages")
    p_gmail.add_argument("--count", type=int, default=20)

    p_drive = sub.add_parser("drive", help="Recently modified Drive files")
    p_drive.add_argument("--count", type=int, default=20)

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    passphrase = args.passphrase or prompt_passphrase()

    if args.cmd == "auth":
        cmd_auth(passphrase)
    elif args.cmd == "calendar":
        cmd_calendar(args.days, passphrase)
    elif args.cmd == "gmail":
        cmd_gmail(args.count, passphrase)
    elif args.cmd == "drive":
        cmd_drive(args.count, passphrase)


if __name__ == "__main__":
    main()
