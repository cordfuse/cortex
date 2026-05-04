#!/usr/bin/env python3
"""
Cortex Google integration — Calendar, Gmail, Drive, Tasks, Contacts.

Credentials are stored in the Cortex secrets vault (cortex.secrets.enc).
Run once to set up:
  python scripts/integrations/google.py auth

Usage (read):
  python scripts/integrations/google.py [--passphrase <p>] auth
  python scripts/integrations/google.py [--passphrase <p>] calendar [--days 7]
  python scripts/integrations/google.py [--passphrase <p>] gmail [--count 20]
  python scripts/integrations/google.py [--passphrase <p>] drive [--count 20]
  python scripts/integrations/google.py [--passphrase <p>] tasks
  python scripts/integrations/google.py [--passphrase <p>] contacts [--count 50]

Usage (write — v4.1.0+):
  python scripts/integrations/google.py [--passphrase <p>] send-mail --to <addr> --subject <s> --body <b>
  python scripts/integrations/google.py [--passphrase <p>] create-event --summary <s> --start <ISO> --end <ISO> [--calendar primary] [--description <d>] [--location <l>] [--attendees a@b,c@d]
  python scripts/integrations/google.py [--passphrase <p>] create-task --title <t> [--list @default] [--notes <n>] [--due <YYYY-MM-DD>]

`--passphrase` is a top-level flag and must come BEFORE the subcommand.

Write commands require the broader OAuth scopes shipped in v4.1.0+. If you previously
auth'd with v4.0.x read-only scopes, re-run `auth` to upgrade the grant. Calls that
need a scope you didn't grant return a 403 with a fallback message (per ROE Rule 19).

Requires: pip install google-auth google-auth-oauthlib google-api-python-client
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime, timezone, timedelta

# Prevent this script's directory from shadowing the google PyPI package.
# The script is named google.py — without this guard, `from google.oauth2 import ...`
# below resolves to THIS file (which has no oauth2 submodule) instead of the
# real google package in site-packages, producing a misleading ImportError.
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir in sys.path:
    sys.path.remove(_script_dir)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SCOPES = [
    # Calendar — read all calendars + read/write events
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
    # Gmail — read, label, draft, AND send (the four things a scribe needs)
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    # Drive — file-scoped (least-privilege; cortex sees what it creates + what user opens through it)
    "https://www.googleapis.com/auth/drive.file",
    # Drive read-only retained for "scan all my files" use cases
    "https://www.googleapis.com/auth/drive.readonly",
    # Tasks — full RW
    "https://www.googleapis.com/auth/tasks",
    # Contacts — full RW
    "https://www.googleapis.com/auth/contacts",
]

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: Google client libraries not installed.")
    print("Run: pip install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)


# ── Graceful error handler (per ROE Rule 19) ──────────────────────────────────

def _is_insufficient_scope(err: Exception) -> bool:
    """True if the error indicates the OAuth grant is missing required scopes."""
    if not isinstance(err, HttpError):
        return False
    if err.resp.status != 403:
        return False
    body = (err.error_details if hasattr(err, "error_details") else str(err))
    return "insufficient" in str(body).lower() or "scope" in str(body).lower()


def _handle_api_error(err: Exception, service: str, operation: str):
    """Translate API errors into plain-English fallback messages and exit non-zero.
    Per ROE Rule 19: never surface stack traces; always include next concrete action."""
    if isinstance(err, HttpError):
        status = err.resp.status
        body = err.error_details if hasattr(err, "error_details") else str(err)
        if _is_insufficient_scope(err):
            print(f"ERROR: {service} {operation} requires a scope you didn't grant.")
            print("Re-run auth to upgrade the grant: python scripts/integrations/google.py auth")
            sys.exit(1)
        if status == 401:
            print(f"ERROR: {service} auth expired. Re-run: python scripts/integrations/google.py auth")
            sys.exit(1)
        if status == 429:
            print(f"ERROR: {service} rate-limited. Try again in a few minutes.")
            sys.exit(1)
        if 500 <= status < 600:
            print(f"ERROR: {service} returned {status}. Try again later (Google-side issue).")
            sys.exit(1)
        print(f"ERROR: {service} {operation} failed ({status}): {body}")
        sys.exit(1)
    # Network / other
    msg = str(err)
    if "ConnectionError" in type(err).__name__ or "TLS" in msg or "SSL" in msg:
        print(f"ERROR: {service} unreachable from this environment. Check network / sandbox egress.")
        sys.exit(1)
    print(f"ERROR: {service} {operation} failed: {msg}")
    sys.exit(1)


def _run_with_reauth_retry(action_fn, passphrase: str, service: str, operation: str):
    """Run a Google API action with auto-re-auth-and-retry on insufficient_scope.

    `action_fn(creds)` builds the service, makes the API call, and returns the result.
    On the first 403/insufficient_scope (typical when SCOPES expanded but the user's
    refresh token is bound to a narrower grant), prompt the user to re-authorize
    interactively. If they accept, run cmd_auth(passphrase) inline (overwrites the
    refresh token in the vault), then retry action_fn() ONCE with fresh creds.

    Non-interactive contexts (cron, headless): no prompt. Falls through to the
    existing _handle_api_error path so the user sees the "re-run auth" message and
    exits non-zero. Same UX as v4.1.0.

    Per ROE Rule 19: no stack traces, every error path includes a concrete next action.
    """
    try:
        creds = get_credentials(passphrase)
        return action_fn(creds)
    except HttpError as err:
        if _is_insufficient_scope(err) and sys.stdin.isatty():
            print()
            print(f"Cortex's {service.lower()} connector needs a scope your current OAuth grant doesn't have.")
            print(f"(This happens after upgrading from a read-only cortex; '{operation}' was added in v4.1.0+.)")
            try:
                answer = input("Re-authorize now to upgrade the grant? [y/N]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                _handle_api_error(err, service, operation)
                return None  # _handle_api_error sys.exits, but mypy
            if answer in ("y", "yes"):
                print()
                print("Running auth flow — your browser will open. Approve the new scope list to continue.")
                print()
                cmd_auth(passphrase)
                print()
                print(f"Re-auth complete. Retrying {operation}...")
                print()
                try:
                    creds = get_credentials(passphrase)
                    return action_fn(creds)
                except Exception as retry_err:
                    _handle_api_error(retry_err, service, operation)
                    return None
            else:
                _handle_api_error(err, service, operation)
                return None
        else:
            _handle_api_error(err, service, operation)
            return None
    except Exception as err:
        _handle_api_error(err, service, operation)
        return None


# ── Vault helpers ─────────────────────────────────────────────────────────────

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


# ── Auth ──────────────────────────────────────────────────────────────────────

def cmd_auth(passphrase: str):
    print("Google OAuth setup")
    print("Requires a Google Cloud project with Calendar, Gmail, Drive, Tasks, and People APIs enabled.")
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
    print("Commit cortex.secrets/ to persist across devices.")


# ── Calendar ──────────────────────────────────────────────────────────────────

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


# ── Gmail ─────────────────────────────────────────────────────────────────────

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


# ── Drive ─────────────────────────────────────────────────────────────────────

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


# ── Tasks ─────────────────────────────────────────────────────────────────────

def cmd_tasks(passphrase: str):
    creds = get_credentials(passphrase)
    service = build("tasks", "v1", credentials=creds)

    lists_result = service.tasklists().list(maxResults=20).execute()
    task_lists = lists_result.get("items", [])

    if not task_lists:
        print("No task lists found.")
        return

    print("# Google Tasks\n")
    for lst in task_lists:
        list_id = lst.get("id")
        list_title = lst.get("title", "")
        tasks_result = service.tasks().list(
            tasklist=list_id,
            showCompleted=False,
            maxResults=20,
        ).execute()
        tasks = tasks_result.get("items", [])
        if not tasks:
            continue
        print(f"**{list_title}**")
        for t in tasks:
            title = t.get("title", "")
            due = t.get("due", "")
            due_str = ""
            if due:
                due_str = f" (due {datetime.fromisoformat(due.replace('Z', '+00:00')).strftime('%d %b')})"
            notes = t.get("notes", "")
            note_str = f"\n    {notes}" if notes else ""
            print(f"  - {title}{due_str}{note_str}")
        print()


# ── Contacts ──────────────────────────────────────────────────────────────────

def cmd_contacts(count: int, passphrase: str):
    creds = get_credentials(passphrase)
    service = build("people", "v1", credentials=creds)

    result = service.people().connections().list(
        resourceName="people/me",
        pageSize=count,
        personFields="names,emailAddresses,phoneNumbers,organizations",
        sortOrder="LAST_MODIFIED_DESCENDING",
    ).execute()

    connections = result.get("connections", [])
    if not connections:
        print("No contacts found.")
        return

    print(f"# Google Contacts — {len(connections)} recently modified\n")
    for person in connections:
        names = person.get("names", [])
        name = names[0].get("displayName", "(no name)") if names else "(no name)"

        emails = person.get("emailAddresses", [])
        email_str = emails[0].get("value", "") if emails else ""

        phones = person.get("phoneNumbers", [])
        phone_str = phones[0].get("value", "") if phones else ""

        orgs = person.get("organizations", [])
        org_str = orgs[0].get("name", "") if orgs else ""

        details = " | ".join(filter(None, [email_str, phone_str, org_str]))
        print(f"- **{name}**{' — ' + details if details else ''}")


# ── Send mail (v4.1.0+) ───────────────────────────────────────────────────────

def cmd_send_mail(to: str, subject: str, body: str, passphrase: str):
    """Send a Gmail message via the authenticated user's account.
    Requires gmail.send scope (granted automatically in v4.1.0+ auth flow).
    On insufficient_scope, prompts to re-auth + retries (v4.1.1+)."""
    from email.mime.text import MIMEText
    import base64

    def action(creds):
        service = build("gmail", "v1", credentials=creds)
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return service.users().messages().send(
            userId="me",
            body={"raw": raw},
        ).execute()

    result = _run_with_reauth_retry(action, passphrase, "Gmail", "send")
    if result is None:
        return
    msg_id = result.get("id", "unknown")
    print(f"Sent. Gmail message ID: {msg_id}")
    print(f"To:      {to}")
    print(f"Subject: {subject}")


# ── Create calendar event (v4.1.0+) ───────────────────────────────────────────

def cmd_create_event(
    summary: str,
    start: str,
    end: str,
    calendar: str,
    description: str,
    location: str,
    attendees: str,
    passphrase: str,
):
    """Create a Calendar event. start and end are ISO 8601 strings; if they include
    'T' they're treated as datetime, otherwise as all-day dates.
    Requires calendar.events scope (granted automatically in v4.1.0+ auth flow).
    On insufficient_scope, prompts to re-auth + retries (v4.1.1+)."""
    def action(creds):
        service = build("calendar", "v3", credentials=creds)

        # All-day vs timed
        if "T" in start:
            start_obj = {"dateTime": start}
            end_obj = {"dateTime": end}
        else:
            start_obj = {"date": start}
            end_obj = {"date": end}

        event_body = {
            "summary": summary,
            "start": start_obj,
            "end": end_obj,
        }
        if description:
            event_body["description"] = description
        if location:
            event_body["location"] = location
        if attendees:
            event_body["attendees"] = [
                {"email": a.strip()} for a in attendees.split(",") if a.strip()
            ]

        return service.events().insert(
            calendarId=calendar,
            body=event_body,
            sendUpdates="all" if attendees else "none",
        ).execute()

    result = _run_with_reauth_retry(action, passphrase, "Calendar", "create event")
    if result is None:
        return
    link = result.get("htmlLink", "")
    event_id = result.get("id", "unknown")
    print(f"Created. Event ID: {event_id}")
    print(f"Calendar: {calendar}")
    print(f"Summary:  {summary}")
    print(f"When:     {start} -> {end}")
    if link:
        print(f"URL:      {link}")


# ── Create task (v4.1.0+) ─────────────────────────────────────────────────────

def cmd_create_task(
    title: str,
    tasklist: str,
    notes: str,
    due: str,
    passphrase: str,
):
    """Create a Google Task. tasklist defaults to '@default' (the user's primary list).
    due is YYYY-MM-DD; the API expects ISO 8601 datetime so the script appends T00:00:00Z.
    Requires tasks scope (granted automatically in v4.1.0+ auth flow).
    On insufficient_scope, prompts to re-auth + retries (v4.1.1+)."""
    # Normalize due once before building the closure
    if due and "T" not in due:
        due = due + "T00:00:00.000Z"

    def action(creds):
        service = build("tasks", "v1", credentials=creds)
        task_body = {"title": title}
        if notes:
            task_body["notes"] = notes
        if due:
            task_body["due"] = due
        return service.tasks().insert(
            tasklist=tasklist,
            body=task_body,
        ).execute()

    result = _run_with_reauth_retry(action, passphrase, "Tasks", "create task")
    if result is None:
        return
    task_id = result.get("id", "unknown")
    print(f"Created. Task ID: {task_id}")
    print(f"List:  {tasklist}")
    print(f"Title: {title}")
    if due:
        print(f"Due:   {due}")


# ── Main ──────────────────────────────────────────────────────────────────────

def prompt_passphrase() -> str:
    import getpass
    return getpass.getpass("Vault passphrase: ")


def main():
    parser = argparse.ArgumentParser(description="Cortex Google integration")
    parser.add_argument("--passphrase", default=None)
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("auth", help="OAuth setup — run once")

    p_cal = sub.add_parser("calendar", help="Upcoming calendar events")
    p_cal.add_argument("--days", type=int, default=7)

    p_gmail = sub.add_parser("gmail", help="Unread Gmail messages")
    p_gmail.add_argument("--count", type=int, default=20)

    p_drive = sub.add_parser("drive", help="Recently modified Drive files")
    p_drive.add_argument("--count", type=int, default=20)

    sub.add_parser("tasks", help="Open Google Tasks")

    p_contacts = sub.add_parser("contacts", help="Recently modified contacts")
    p_contacts.add_argument("--count", type=int, default=50)

    # Write subcommands (v4.1.0+)
    p_send = sub.add_parser("send-mail", help="Send an email via Gmail (v4.1.0+)")
    p_send.add_argument("--to", required=True)
    p_send.add_argument("--subject", required=True)
    p_send.add_argument("--body", required=True, help="Plain-text body")

    p_event = sub.add_parser("create-event", help="Create a calendar event (v4.1.0+)")
    p_event.add_argument("--summary", required=True)
    p_event.add_argument("--start", required=True, help="ISO 8601 datetime (with 'T') or date (YYYY-MM-DD for all-day)")
    p_event.add_argument("--end", required=True, help="Same format as --start")
    p_event.add_argument("--calendar", default="primary", help="Calendar ID (default: primary)")
    p_event.add_argument("--description", default="")
    p_event.add_argument("--location", default="")
    p_event.add_argument("--attendees", default="", help="Comma-separated email addresses")

    p_task = sub.add_parser("create-task", help="Create a Google Task (v4.1.0+)")
    p_task.add_argument("--title", required=True)
    p_task.add_argument("--list", dest="tasklist", default="@default", help="Tasklist ID (default: @default)")
    p_task.add_argument("--notes", default="")
    p_task.add_argument("--due", default="", help="YYYY-MM-DD or ISO 8601")

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
    elif args.cmd == "tasks":
        cmd_tasks(passphrase)
    elif args.cmd == "contacts":
        cmd_contacts(args.count, passphrase)
    elif args.cmd == "send-mail":
        cmd_send_mail(args.to, args.subject, args.body, passphrase)
    elif args.cmd == "create-event":
        cmd_create_event(
            args.summary, args.start, args.end,
            args.calendar, args.description, args.location, args.attendees,
            passphrase,
        )
    elif args.cmd == "create-task":
        cmd_create_task(args.title, args.tasklist, args.notes, args.due, passphrase)


if __name__ == "__main__":
    main()
