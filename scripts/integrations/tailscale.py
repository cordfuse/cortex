#!/usr/bin/env python3
"""
Cortex Tailscale integration — mesh network connector.

Brings up Tailscale headlessly using an auth key stored in the Cortex vault.
Makes home network resources (NAS, SFTP, SMB) reachable from anywhere —
enabling rclone local/SFTP backends to work on mobile, Chromebook, or laptop
away from home.

Mobile devices use the Tailscale app directly — this connector is for
Linux / macOS / Windows CLI environments (steve-cachyos, Chromebook, laptop).

Setup:
  python scripts/integrations/tailscale.py auth

Usage:
  python scripts/integrations/tailscale.py auth              [--passphrase <p>]
  python scripts/integrations/tailscale.py status            [--passphrase <p>]
  python scripts/integrations/tailscale.py up                [--passphrase <p>]
  python scripts/integrations/tailscale.py down
  python scripts/integrations/tailscale.py ip <hostname>     [--passphrase <p>]
  python scripts/integrations/tailscale.py peers             [--passphrase <p>]

Requires: tailscale installed and in PATH
  Linux:   curl -fsSL https://tailscale.com/install.sh | sh
  macOS:   brew install tailscale
  ChromeOS (Crostini): curl -fsSL https://tailscale.com/install.sh | sh
"""

import os
import sys
import json
import argparse
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

VAULT_KEY = "tailscale-auth-key"


# ── tailscale check ───────────────────────────────────────────────────────────

def require_tailscale():
    if subprocess.run(["which", "tailscale"], capture_output=True).returncode != 0:
        print("ERROR: tailscale is not installed.")
        print("  Linux / ChromeOS: curl -fsSL https://tailscale.com/install.sh | sh")
        print("  macOS:            brew install tailscale")
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
        print("Run: python scripts/integrations/tailscale.py auth")
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

def cmd_auth(passphrase: str):
    """Store a Tailscale auth key in the vault."""
    print("Tailscale auth key setup")
    print("Generate a reusable auth key at: https://login.tailscale.com/admin/settings/keys")
    print("Settings: Reusable ON, Ephemeral OFF\n")

    key = input("Paste auth key: ").strip()
    if not key.startswith("tskey-"):
        print("WARNING: key doesn't look like a Tailscale auth key (expected tskey-...)")

    store_secret(VAULT_KEY, key, passphrase)
    print(f"\nStored as '{VAULT_KEY}' in vault.")
    print("Run: python scripts/integrations/tailscale.py up")


# ── Status ────────────────────────────────────────────────────────────────────

def cmd_status():
    require_tailscale()
    result = subprocess.run(["tailscale", "status"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Tailscale is not running or not connected.")
        print("Run: python scripts/integrations/tailscale.py up")
        return
    print(result.stdout)


# ── Up ────────────────────────────────────────────────────────────────────────

def cmd_up(passphrase: str):
    require_tailscale()
    auth_key = get_secret(VAULT_KEY, passphrase)

    print("Bringing Tailscale up...")
    result = subprocess.run(
        ["tailscale", "up", "--authkey", auth_key],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print("Tailscale is up.")
        cmd_status()
    else:
        print(f"ERROR: {result.stderr.strip()}")
        sys.exit(1)


# ── Down ──────────────────────────────────────────────────────────────────────

def cmd_down():
    require_tailscale()
    result = subprocess.run(["tailscale", "down"], capture_output=True, text=True)
    if result.returncode == 0:
        print("Tailscale is down.")
    else:
        print(f"ERROR: {result.stderr.strip()}")
        sys.exit(1)


# ── IP ────────────────────────────────────────────────────────────────────────

def cmd_ip(hostname: str):
    """Get the Tailscale IP of a peer by hostname. Use this in rclone SFTP config."""
    require_tailscale()
    result = subprocess.run(
        ["tailscale", "ip", hostname],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        ip = result.stdout.strip()
        print(f"{hostname}: {ip}")
        print(f"\nUse this IP in your rclone SFTP remote config:")
        print(f"  host = {ip}")
    else:
        print(f"ERROR: {result.stderr.strip()}")
        print("Is Tailscale up? Run: python scripts/integrations/tailscale.py up")
        sys.exit(1)


# ── Peers ─────────────────────────────────────────────────────────────────────

def cmd_peers():
    """List all peers in the tailnet with their IPs and hostnames."""
    require_tailscale()
    result = subprocess.run(
        ["tailscale", "status", "--json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Tailscale is not running. Run: python scripts/integrations/tailscale.py up")
        sys.exit(1)

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("ERROR: Could not parse tailscale status output.")
        sys.exit(1)

    peers = data.get("Peer", {})
    self_node = data.get("Self", {})

    print("# Tailnet peers\n")

    # Self
    self_ips = self_node.get("TailscaleIPs", [])
    self_host = self_node.get("HostName", "this device")
    self_ip = self_ips[0] if self_ips else "unknown"
    print(f"  {self_ip}  {self_host}  (this device)")

    # Peers
    for _, peer in peers.items():
        ips = peer.get("TailscaleIPs", [])
        ip = ips[0] if ips else "unknown"
        hostname = peer.get("HostName", "unknown")
        online = "online" if peer.get("Online") else "offline"
        os_name = peer.get("OS", "")
        os_str = f" [{os_name}]" if os_name else ""
        print(f"  {ip}  {hostname}{os_str}  ({online})")

    print(f"\nTo get IP for rclone: python scripts/integrations/tailscale.py ip <hostname>")


# ── Main ──────────────────────────────────────────────────────────────────────

def prompt_passphrase() -> str:
    import getpass
    return getpass.getpass("Vault passphrase: ")


def main():
    parser = argparse.ArgumentParser(
        description="Cortex Tailscale integration — mesh network connector"
    )
    parser.add_argument("--passphrase", default=None)
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("auth", help="Store Tailscale auth key in vault")
    sub.add_parser("status", help="Show Tailscale connection status")
    sub.add_parser("up", help="Bring Tailscale up using vaulted auth key")
    sub.add_parser("down", help="Bring Tailscale down")

    p_ip = sub.add_parser("ip", help="Get Tailscale IP of a peer (use in rclone config)")
    p_ip.add_argument("hostname", help="Peer hostname (e.g. steve-cachyos, nas)")

    sub.add_parser("peers", help="List all peers in the tailnet")

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    # Commands that don't need the vault
    if args.cmd == "status":
        cmd_status()
        return
    if args.cmd == "down":
        cmd_down()
        return
    if args.cmd == "peers":
        cmd_peers()
        return
    if args.cmd == "ip":
        cmd_ip(args.hostname)
        return

    # Commands that need the vault
    passphrase = args.passphrase or prompt_passphrase()

    if args.cmd == "auth":
        cmd_auth(passphrase)
    elif args.cmd == "up":
        cmd_up(passphrase)


if __name__ == "__main__":
    main()
