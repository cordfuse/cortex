#!/usr/bin/env python3
"""
Cortex make-private script.
Flips your Cortex repo from public to private using a stored GitHub PAT.

Prerequisites:
  pip install cryptography
  python scripts/secrets.py store github-pat

Run:
  python scripts/make_private.py

The PAT needs the 'repo' scope on GitHub.
"""

import os
import sys
import json
import getpass
import argparse
import subprocess
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

try:
    from secrets import unified_get, perfile_names, LEGACY_VAULT
except ImportError as e:
    print(f"ERROR: Could not import from scripts/secrets.py: {e}")
    sys.exit(1)


def get_remote_url() -> str:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=ROOT, capture_output=True, text=True
    )
    if result.returncode != 0:
        print("ERROR: Could not read git remote. Is this a git repo with an origin?")
        sys.exit(1)
    return result.stdout.strip()


def parse_owner_repo(remote_url: str) -> tuple:
    url = remote_url
    if url.startswith("git@"):
        # SSH: git@github.com:owner/repo.git or git@alias:owner/repo.git
        path = url.split(":", 1)[1]
    elif "github.com/" in url:
        # HTTPS: https://github.com/owner/repo.git
        path = url.split("github.com/", 1)[1]
    else:
        print(f"ERROR: Only GitHub remotes are supported. Got: {url}")
        sys.exit(1)
    path = path.removesuffix(".git")
    parts = path.split("/")
    if len(parts) != 2:
        print(f"ERROR: Could not parse owner/repo from: {url}")
        sys.exit(1)
    return parts[0], parts[1]


def print_manual_instructions(owner: str, repo: str) -> None:
    print()
    print("Cannot reach the GitHub API from this environment.")
    print("Expected on Claude mobile and other sandboxed agents — only git is permitted.")
    print()
    print(f"Flip {owner}/{repo} private manually:")
    print(f"  1. Open https://github.com/{owner}/{repo}/settings")
    print("  2. Scroll to the Danger Zone at the bottom")
    print("  3. Change repository visibility → Make private")
    print("  4. Confirm by typing the repo name")
    print()


def github_api_reachable() -> bool:
    # Preflight before prompting for the vault passphrase — on mobile/sandboxed agents
    # egress to api.github.com is blocked, and we should bail before the user types
    # their passphrase into chat for nothing.
    try:
        req = urllib.request.Request("https://api.github.com", method="HEAD")
        with urllib.request.urlopen(req, timeout=5):
            return True
    except urllib.error.URLError:
        return False


def main():
    parser = argparse.ArgumentParser(description="Flip Cortex repo to private via GitHub API")
    parser.add_argument("--passphrase", default=None, help="Vault passphrase (prompted if omitted)")
    args = parser.parse_args()

    remote_url = get_remote_url()
    owner, repo = parse_owner_repo(remote_url)
    print(f"Repo: {owner}/{repo}")

    if not github_api_reachable():
        print_manual_instructions(owner, repo)
        sys.exit(0)

    # Cheap pre-flight on v2 vault — spares the passphrase prompt when we can be
    # certain the secret isn't there. Legacy users (no per-file entry but legacy
    # blob present) fall through to unified_get, which decrypts the blob.
    if "github-pat" not in perfile_names() and not os.path.exists(LEGACY_VAULT):
        print("ERROR: No 'github-pat' in vault.")
        print("Store it first: python scripts/secrets.py store github-pat")
        sys.exit(1)

    passphrase = args.passphrase or getpass.getpass("Vault passphrase: ")
    pat = unified_get("github-pat", passphrase)

    payload = json.dumps({"private": True}).encode()
    req = urllib.request.Request(
        f"https://api.github.com/repos/{owner}/{repo}",
        data=payload,
        method="PATCH",
        headers={
            "Authorization": f"Bearer {pat}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
            if body.get("private"):
                print(f"Done. {owner}/{repo} is now private.")
            else:
                print("WARNING: Request succeeded but repo does not appear private. Check GitHub.")
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"ERROR: GitHub API {e.code}: {err}")
        sys.exit(1)
    except urllib.error.URLError as e:
        # Reached here despite preflight — network dropped mid-flight, or egress opened
        # up for the HEAD but not the PATCH. Don't leak a traceback.
        print(f"ERROR: Could not reach GitHub API: {e.reason}")
        print_manual_instructions(owner, repo)
        sys.exit(1)


if __name__ == "__main__":
    main()
