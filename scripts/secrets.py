#!/usr/bin/env python3
"""
Cortex secrets vault — v2 per-file format with v1 legacy read support.

Write: always per-file (cortex.secrets/<n>.enc)
Read:  per-file first, falls back to legacy blob (cortex.secrets.enc)
List:  union of both — per-file takes precedence on duplicate keys

DESIGN NOTE (2026-04-17):
  The original vault used a single encrypted blob (cortex.secrets.enc).
  This was a design mistake — a single blob cannot be merged by git, causing
  sync conflicts when two agents write simultaneously.

  v2 uses one encrypted file per secret (cortex.secrets/<n>.enc).
  Git merges per-file independently. Conflicts only occur if two agents write
  the SAME key at the same time — surfaces as a standard git conflict.

  The legacy blob reader below exists ONLY for backwards compatibility with
  repos that have not yet migrated. It is deprecated and will be removed in
  a future version. Run `python scripts/secrets.py migrate` to clean up.

Requires: pip install cryptography
"""

import os
import sys
import json
import base64
import getpass
import argparse
import datetime

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except ImportError:
    print("ERROR: 'cryptography' package not installed.")
    print("Run: pip install cryptography")
    sys.exit(1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_DIR = os.path.join(ROOT, "cortex.secrets")
MANIFEST_PATH = os.path.join(VAULT_DIR, "vault.json")
LEGACY_VAULT = os.path.join(ROOT, "cortex.secrets.enc")  # DEPRECATED — do not write to this

PBKDF2_ITERATIONS = 600_000
SALT_LEN = 16
NONCE_LEN = 12


# --- Crypto primitives ---

def derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(passphrase.encode())


def encrypt_value(value: str, passphrase: str) -> bytes:
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = derive_key(passphrase, salt)
    payload = json.dumps({
        "value": value,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }).encode()
    ciphertext = AESGCM(key).encrypt(nonce, payload, None)
    return base64.b64encode(salt + nonce + ciphertext)


def _raw_decrypt(data: bytes, passphrase: str, label: str = "file") -> bytes:
    raw = base64.b64decode(data.strip())
    salt = raw[:SALT_LEN]
    nonce = raw[SALT_LEN:SALT_LEN + NONCE_LEN]
    ciphertext = raw[SALT_LEN + NONCE_LEN:]
    key = derive_key(passphrase, salt)
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, None)
    except Exception:
        print(f"ERROR: Wrong passphrase or {label} is corrupt.")
        sys.exit(1)


# --- Per-file (v2) --- current format ---

def secret_path(name: str) -> str:
    safe = name.replace("/", "_").replace("\\", "_")
    return os.path.join(VAULT_DIR, f"{safe}.enc")


def ensure_vault_dir():
    os.makedirs(VAULT_DIR, exist_ok=True)


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read_manifest() -> dict:
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    return {"version": 2, "created_at": now_iso(), "passphrase_rotated_at": None, "secrets": {}}


def write_manifest(passphrase_rotated: bool = False, name: str = None, description: str = None):
    existing = read_manifest()
    # Migrate old list format to dict format
    existing_secrets = existing.get("secrets", {})
    if isinstance(existing_secrets, list):
        existing_secrets = {k: "" for k in existing_secrets}
    # Remove entries for deleted files
    names = perfile_names()
    secrets = {k: existing_secrets.get(k, "") for k in names}
    # Update description for the current key if provided
    if name and description is not None:
        secrets[name] = description
    manifest = {
        "version": 2,
        "created_at": existing.get("created_at", now_iso()),
        "passphrase_rotated_at": now_iso() if passphrase_rotated else existing.get("passphrase_rotated_at"),
        "secrets": secrets,
    }
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def perfile_names() -> list:
    if not os.path.isdir(VAULT_DIR):
        return []
    return sorted(f[:-4] for f in os.listdir(VAULT_DIR) if f.endswith(".enc") and f != "vault.json")


def perfile_get(name: str, passphrase: str) -> str:
    path = secret_path(name)
    plaintext = _raw_decrypt(open(path, "rb").read(), passphrase, label=f"cortex.secrets/{name}.enc")
    return json.loads(plaintext)["value"]


def perfile_delete(name: str, passphrase: str):
    path = secret_path(name)
    perfile_get(name, passphrase)  # verify passphrase before deleting
    os.remove(path)


# ---------------------------------------------------------------------------
# DEPRECATED: Legacy v1 single-blob support
# This code exists only to read repos that have not yet migrated from the
# original cortex.secrets.enc blob format. It will never write to the blob.
# Run `python scripts/secrets.py migrate` to eliminate this code path.
# ---------------------------------------------------------------------------

def _legacy_read(passphrase: str) -> dict:
    """DEPRECATED. Read legacy cortex.secrets.enc blob. Returns {} if not present."""
    if not os.path.exists(LEGACY_VAULT):
        return {}
    plaintext = _raw_decrypt(open(LEGACY_VAULT, "rb").read(), passphrase, label="legacy vault")
    return json.loads(plaintext)


def _legacy_delete(name: str, passphrase: str):
    """DEPRECATED. Delete a key from legacy blob by rewriting it without that key."""
    legacy = _legacy_read(passphrase)
    if name not in legacy:
        return False
    del legacy[name]
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = derive_key(passphrase, salt)
    plaintext = json.dumps(legacy).encode()
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)
    with open(LEGACY_VAULT, "wb") as f:
        f.write(base64.b64encode(salt + nonce + ciphertext))
    return True

# --- End deprecated legacy block ---


# --- Unified read layer (v2 first, legacy fallback) ---

def unified_list(passphrase: str = None) -> list:
    pf = set(perfile_names())
    if os.path.exists(LEGACY_VAULT):
        if passphrase is None:
            if pf:
                print("Note: legacy vault also present — provide --passphrase to include its keys.")
            legacy = {}
        else:
            legacy = _legacy_read(passphrase)  # DEPRECATED path
    else:
        legacy = {}
    all_names = pf | set(legacy.keys())
    return sorted(all_names)


def unified_get(name: str, passphrase: str) -> str:
    """Per-file first, legacy fallback (DEPRECATED path)."""
    path = secret_path(name)
    if os.path.exists(path):
        return perfile_get(name, passphrase)
    if os.path.exists(LEGACY_VAULT):  # DEPRECATED fallback
        legacy = _legacy_read(passphrase)
        if name in legacy:
            return legacy[name]
    print(f"ERROR: No secret named '{name}'.")
    sys.exit(1)


def unified_delete(name: str, passphrase: str):
    """Delete from whichever format the key lives in."""
    path = secret_path(name)
    if os.path.exists(path):
        perfile_delete(name, passphrase)
        return
    if os.path.exists(LEGACY_VAULT):  # DEPRECATED fallback
        if _legacy_delete(name, passphrase):
            return
    print(f"ERROR: No secret named '{name}'.")
    sys.exit(1)


# --- CLI commands ---

def prompt(label: str, confirm_label: str = None) -> str:
    value = getpass.getpass(f"{label}: ")
    if confirm_label:
        confirm = getpass.getpass(f"{confirm_label}: ")
        if value != confirm:
            print("ERROR: Values do not match.")
            sys.exit(1)
    return value


def cmd_store(name: str, value: str = None, passphrase: str = None, description: str = None):
    if value is None:
        value = prompt(f"Value for '{name}'")
    if not value:
        print("ERROR: Value cannot be empty.")
        sys.exit(1)
    if passphrase is None:
        existing = unified_list()
        if existing:
            passphrase = prompt("Vault passphrase")
        else:
            print("No vault found — creating a new one.")
            passphrase = prompt("Choose a passphrase", "Confirm passphrase")
    ensure_vault_dir()
    path = secret_path(name)
    blob = encrypt_value(value, passphrase)
    with open(path, "wb") as f:
        f.write(blob)
    write_manifest(name=name, description=description or "")
    print(f"Stored '{name}' -> cortex.secrets/{name}.enc")
    print("Commit and push to persist across devices.")


def cmd_get(name: str, passphrase: str = None):
    if passphrase is None:
        passphrase = prompt("Vault passphrase")
    print(unified_get(name, passphrase))


def cmd_list(passphrase: str = None):
    names = unified_list(passphrase)
    if not names:
        print("No secrets stored.")
        return
    manifest = read_manifest()
    descriptions = manifest.get("secrets", {})
    if isinstance(descriptions, list):
        descriptions = {k: "" for k in descriptions}
    print("Stored secrets:")
    for n in names:
        desc = descriptions.get(n, "")
        print(f"  {n}" + (f"  — {desc}" if desc else ""))


def cmd_delete(name: str, passphrase: str = None, force: bool = False):
    if passphrase is None:
        passphrase = prompt("Vault passphrase")
    if not force:
        confirm = input(f"WARNING: Delete '{name}'? This cannot be undone. Type the secret name to confirm: ")
        if confirm != name:
            print("Aborted.")
            sys.exit(0)
    unified_delete(name, passphrase)
    write_manifest()
    print(f"Deleted '{name}'.")


def cmd_repassphrase(old_passphrase: str = None, new_passphrase: str = None):
    names = perfile_names()
    if not names:
        print("No secrets in vault.")
        return
    if old_passphrase is None:
        old_passphrase = prompt("Current passphrase")
    # Verify old passphrase decrypts all secrets before touching anything
    values = {}
    for name in names:
        try:
            values[name] = perfile_get(name, old_passphrase)
        except SystemExit:
            print(f"ERROR: Could not decrypt '{name}' — aborting. No changes made.")
            sys.exit(1)
    if new_passphrase is None:
        new_passphrase = prompt("New passphrase", "Confirm new passphrase")
    ensure_vault_dir()
    for name, value in values.items():
        path = secret_path(name)
        blob = encrypt_value(value, new_passphrase)
        with open(path, "wb") as f:
            f.write(blob)
        print(f"  Re-encrypted '{name}'")
    write_manifest(passphrase_rotated=True)
    print(f"\nAll {len(names)} secret(s) re-encrypted with new passphrase.")
    print("Commit and push to persist across devices.")


def cmd_migrate(passphrase: str = None):
    """
    DEPRECATED path cleanup: migrate all legacy blob secrets to per-file format.
    Safe to run multiple times. Per-file secrets are not touched.
    """
    if not os.path.exists(LEGACY_VAULT):
        print("No legacy vault found. Nothing to migrate.")
        return
    if passphrase is None:
        passphrase = prompt("Vault passphrase")
    legacy = _legacy_read(passphrase)
    if not legacy:
        print("Legacy vault is empty. Nothing to migrate.")
        return
    ensure_vault_dir()
    for name, value in legacy.items():
        path = secret_path(name)
        blob = encrypt_value(value, passphrase)
        with open(path, "wb") as f:
            f.write(blob)
        print(f"  Migrated '{name}' -> cortex.secrets/{name}.enc")
    print(f"\nMigrated {len(legacy)} secret(s).")
    print("Next steps:")
    print("  1. git add cortex.secrets/")
    print("  2. git rm cortex.secrets.enc")
    print("  3. git commit -m 'vault: migrate to per-file format (v2)'")
    print("  4. git push")
    print("\ncortex.secrets.enc remains in git history (encrypted, safe).")


def main():
    parser = argparse.ArgumentParser(
        description="Cortex secrets vault (v2 per-file, v1 backwards-compatible)",
        add_help=True
    )
    sub = parser.add_subparsers(dest="cmd")

    p_store = sub.add_parser("store")
    p_store.add_argument("name")
    p_store.add_argument("--value", default=None)
    p_store.add_argument("--passphrase", default=None)
    p_store.add_argument("--description", default=None, help="Short description of what this secret is")

    p_get = sub.add_parser("get")
    p_get.add_argument("name")
    p_get.add_argument("--passphrase", default=None)

    p_list = sub.add_parser("list")
    p_list.add_argument("--passphrase", default=None)

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("name")
    p_delete.add_argument("--passphrase", default=None)
    p_delete.add_argument("--force", action="store_true", help="Skip confirmation prompt")

    p_repassphrase = sub.add_parser("repassphrase", help="Re-encrypt all secrets with a new passphrase")
    p_repassphrase.add_argument("--old-passphrase", default=None)
    p_repassphrase.add_argument("--new-passphrase", default=None)

    p_migrate = sub.add_parser("migrate", help="Migrate v1 blob to per-file format (cleanup deprecated path)")
    p_migrate.add_argument("--passphrase", default=None)

    args = parser.parse_args()

    if args.cmd == "store":
        cmd_store(args.name, value=args.value, passphrase=args.passphrase, description=args.description)
    elif args.cmd == "get":
        cmd_get(args.name, passphrase=args.passphrase)
    elif args.cmd == "list":
        cmd_list(passphrase=args.passphrase)
    elif args.cmd == "delete":
        cmd_delete(args.name, passphrase=args.passphrase, force=args.force)
    elif args.cmd == "repassphrase":
        cmd_repassphrase(old_passphrase=args.old_passphrase, new_passphrase=args.new_passphrase)
    elif args.cmd == "migrate":
        cmd_migrate(passphrase=args.passphrase)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
