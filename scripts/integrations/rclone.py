#!/usr/bin/env python3
"""
Cortex rclone integration — universal filesystem connector.

Supports any rclone backend: SFTP, NFS, SMB, Google Drive, OneDrive,
S3-compatible, Backblaze B2, local disk, and more.

The rclone config (containing all remote credentials) is stored encrypted
in the Cortex vault. It is written to a temp file per command and deleted
immediately after — credentials never persist on disk outside the vault.

Setup:
  python scripts/integrations/rclone.py auth

Usage:
  python scripts/integrations/rclone.py auth       [--passphrase <p>]
  python scripts/integrations/rclone.py remotes    [--passphrase <p>]
  python scripts/integrations/rclone.py ls   <remote:path>            [--passphrase <p>]
  python scripts/integrations/rclone.py pull <remote:path> [--dest docs/]  [--passphrase <p>]
  python scripts/integrations/rclone.py push <remote:path> [--src docs/]   [--passphrase <p>]
  python scripts/integrations/rclone.py mount <remote:path> [--mountpoint <path>] [--passphrase <p>]

Requires: rclone installed — https://rclone.org/install/
  macOS:   brew install rclone
  Linux:   sudo apt install rclone  OR  curl https://rclone.org/install.sh | sudo bash
  Windows: winget install Rclone.Rclone
"""

import os
import sys
import argparse
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS_DIR = os.path.join(ROOT, "docs")


# ── rclone check ──────────────────────────────────────────────────────────────

def require_rclone():
    if subprocess.run(["which", "rclone"], capture_output=True).returncode != 0:
        print("ERROR: rclone is not installed.")
        print("  macOS:   brew install rclone")
        print("  Linux:   sudo apt install rclone")
        print("  Windows: winget install Rclone.Rclone")
        print("  Or:      curl https://rclone.org/install.sh | sudo bash")
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
        print("Run: python scripts/integrations/rclone.py auth")
        sys.exit(1)
    return result.stdout.strip()


def store_secret(name: str, value: str, passphrase: str):
    secrets_script = os.path.join(ROOT, "scripts", "secrets.py")
    subprocess.run(
        [sys.executable, secrets_script, "store", name,
         "--value", value, "--passphrase", passphrase],
        check=True
    )


def has_secret(name: str, passphrase: str) -> bool:
    secrets_script = os.path.join(ROOT, "scripts", "secrets.py")
    result = subprocess.run(
        [sys.executable, secrets_script, "get", name, "--passphrase", passphrase],
        capture_output=True, text=True
    )
    return result.returncode == 0


# ── Config temp file ──────────────────────────────────────────────────────────

class RcloneConfig:
    """Context manager: writes rclone config to a temp file, deletes it on exit."""

    def __init__(self, passphrase: str):
        self.passphrase = passphrase
        self._tmp = None

    def __enter__(self) -> str:
        config_data = get_secret("rclone_config", self.passphrase)
        self._tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".conf", delete=False, prefix="cortex_rclone_"
        )
        self._tmp.write(config_data)
        self._tmp.flush()
        self._tmp.close()
        return self._tmp.name

    def __exit__(self, *_):
        if self._tmp and os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)


def run_rclone(args: list, config_path: str) -> int:
    cmd = ["rclone", "--config", config_path] + args
    result = subprocess.run(cmd)
    return result.returncode


# ── Auth ──────────────────────────────────────────────────────────────────────

def cmd_auth(passphrase: str):
    """
    Interactive rclone remote setup. Runs `rclone config` with a temp config,
    then stores the resulting config in the vault.
    """
    require_rclone()

    # Load existing config if present, else start empty
    existing = ""
    if has_secret("rclone_config", passphrase):
        existing = get_secret("rclone_config", passphrase)
        print("Existing rclone config found in vault — adding to it.\n")
    else:
        print("No existing rclone config in vault — starting fresh.\n")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".conf", delete=False, prefix="cortex_rclone_"
    ) as tmp:
        tmp.write(existing)
        tmp_path = tmp.name

    try:
        print("Opening rclone config wizard. Add or edit remotes, then quit when done.")
        print("Type 'n' to add a new remote, 'q' to quit.\n")
        subprocess.run(["rclone", "--config", tmp_path, "config"])

        with open(tmp_path, "r") as f:
            new_config = f.read()

        store_secret("rclone_config", new_config, passphrase)
        print("\nrclone config stored in vault.")
        print("Commit cortex.secrets.enc to persist across devices.")
        print("\nRemotes configured:")
        subprocess.run(["rclone", "--config", tmp_path, "listremotes"])
    finally:
        os.unlink(tmp_path)


# ── Remotes ───────────────────────────────────────────────────────────────────

def cmd_remotes(passphrase: str):
    require_rclone()
    with RcloneConfig(passphrase) as cfg:
        print("# Configured remotes\n")
        run_rclone(["listremotes"], cfg)


# ── ls ────────────────────────────────────────────────────────────────────────

def cmd_ls(remote_path: str, passphrase: str):
    require_rclone()
    with RcloneConfig(passphrase) as cfg:
        print(f"# {remote_path}\n")
        run_rclone(["lsf", "--human-readable", remote_path], cfg)


# ── pull ──────────────────────────────────────────────────────────────────────

def cmd_pull(remote_path: str, dest: str, passphrase: str):
    """Copy a file or directory from a remote into a local destination."""
    require_rclone()
    os.makedirs(dest, exist_ok=True)

    with RcloneConfig(passphrase) as cfg:
        print(f"Pulling {remote_path} → {dest}")
        code = run_rclone(["copy", "--progress", remote_path, dest], cfg)

    if code == 0:
        print(f"\nDone. Files are in {dest}")
        print("File this? Add them to docs/ and commit with: git add docs/ && git commit -m 'docs: pull from <remote>'")
    else:
        print(f"\nERROR: rclone exited with code {code}")
        sys.exit(code)


# ── push ──────────────────────────────────────────────────────────────────────

def cmd_push(remote_path: str, src: str, passphrase: str):
    """Push a local directory to a remote (backup)."""
    require_rclone()

    if not os.path.exists(src):
        print(f"ERROR: Source path does not exist: {src}")
        sys.exit(1)

    with RcloneConfig(passphrase) as cfg:
        print(f"Pushing {src} → {remote_path}")
        code = run_rclone(["sync", "--progress", src, remote_path], cfg)

    if code == 0:
        print("\nDone.")
    else:
        print(f"\nERROR: rclone exited with code {code}")
        sys.exit(code)


# ── mount ─────────────────────────────────────────────────────────────────────

def cmd_mount(remote_path: str, mountpoint: str, passphrase: str):
    """Mount a remote as a local filesystem. Desktop/laptop only."""
    require_rclone()
    os.makedirs(mountpoint, exist_ok=True)

    print(f"Mounting {remote_path} at {mountpoint}")
    print("Press Ctrl+C to unmount.\n")

    with RcloneConfig(passphrase) as cfg:
        try:
            run_rclone(["mount", remote_path, mountpoint, "--vfs-cache-mode", "writes"], cfg)
        except KeyboardInterrupt:
            print("\nUnmounted.")


# ── Main ──────────────────────────────────────────────────────────────────────

def prompt_passphrase() -> str:
    import getpass
    return getpass.getpass("Vault passphrase: ")


def main():
    parser = argparse.ArgumentParser(description="Cortex rclone integration — universal filesystem connector")
    parser.add_argument("--passphrase", default=None)
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("auth", help="Configure remotes — run once per device")
    sub.add_parser("remotes", help="List configured remotes")

    p_ls = sub.add_parser("ls", help="List files on a remote")
    p_ls.add_argument("remote_path", help="e.g. nas:documents or gdrive:")

    p_pull = sub.add_parser("pull", help="Pull files from a remote into docs/")
    p_pull.add_argument("remote_path", help="e.g. nas:bills/2026")
    p_pull.add_argument("--dest", default=DOCS_DIR, help=f"Local destination (default: {DOCS_DIR})")

    p_push = sub.add_parser("push", help="Push local folder to a remote (backup)")
    p_push.add_argument("remote_path", help="e.g. b2:cortex-backup/docs")
    p_push.add_argument("--src", default=DOCS_DIR, help=f"Local source (default: {DOCS_DIR})")

    p_mount = sub.add_parser("mount", help="Mount a remote as a local filesystem (desktop only)")
    p_mount.add_argument("remote_path", help="e.g. nas:")
    p_mount.add_argument("--mountpoint", default=os.path.expanduser("~/mnt/cortex-remote"),
                         help="Local mountpoint (default: ~/mnt/cortex-remote)")

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    passphrase = args.passphrase or prompt_passphrase()

    if args.cmd == "auth":
        cmd_auth(passphrase)
    elif args.cmd == "remotes":
        cmd_remotes(passphrase)
    elif args.cmd == "ls":
        cmd_ls(args.remote_path, passphrase)
    elif args.cmd == "pull":
        cmd_pull(args.remote_path, args.dest, passphrase)
    elif args.cmd == "push":
        cmd_push(args.remote_path, args.src, passphrase)
    elif args.cmd == "mount":
        cmd_mount(args.remote_path, args.mountpoint, passphrase)


if __name__ == "__main__":
    main()
