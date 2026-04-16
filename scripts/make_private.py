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
import subprocess
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

try:
    from secrets import decrypt_vault
except ImportError:
    print("ERROR: Could not import secrets.py. Make sure scripts/secrets.py exists.")
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


def main():
    remote_url = get_remote_url()
    owner, repo = parse_owner_repo(remote_url)
    print(f"Repo: {owner}/{repo}")

    passphrase = getpass.getpass("Vault passphrase: ")
    vault = decrypt_vault(passphrase)

    if "github-pat" not in vault:
        print("ERROR: No 'github-pat' in vault.")
        print("Store it first: python scripts/secrets.py store github-pat")
        sys.exit(1)

    pat = vault["github-pat"]

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


if __name__ == "__main__":
    main()
