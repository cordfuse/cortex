#!/usr/bin/env python3
"""
Cortex secrets vault.
AES-256-GCM encrypted key/value store. Vault file committed to repo — safe because encrypted.

Usage:
  python scripts/secrets.py store <name> [--value <v>] [--passphrase <p>]
  python scripts/secrets.py get <name> [--passphrase <p>]
  python scripts/secrets.py list [--passphrase <p>]
  python scripts/secrets.py delete <name> [--passphrase <p>]

If --value or --passphrase are omitted, they are prompted interactively.
Use the flags when running from an AI agent that cannot handle interactive prompts.

Requires: pip install cryptography
"""

import os
import sys
import json
import base64
import getpass
import argparse

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except ImportError:
    print("ERROR: 'cryptography' package not installed.")
    print("Run: pip install cryptography")
    sys.exit(1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_PATH = os.path.join(ROOT, "cortex.secrets.enc")

PBKDF2_ITERATIONS = 600_000
SALT_LEN = 16
NONCE_LEN = 12


def derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(passphrase.encode())


def encrypt_vault(data: dict, passphrase: str) -> bytes:
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = derive_key(passphrase, salt)
    plaintext = json.dumps(data).encode()
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)
    return base64.b64encode(salt + nonce + ciphertext)


def decrypt_vault(passphrase: str) -> dict:
    if not os.path.exists(VAULT_PATH):
        return {}
    raw = base64.b64decode(open(VAULT_PATH, "rb").read().strip())
    salt = raw[:SALT_LEN]
    nonce = raw[SALT_LEN:SALT_LEN + NONCE_LEN]
    ciphertext = raw[SALT_LEN + NONCE_LEN:]
    key = derive_key(passphrase, salt)
    try:
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
    except Exception:
        print("ERROR: Wrong passphrase or vault is corrupt.")
        sys.exit(1)
    return json.loads(plaintext)


def save_vault(data: dict, passphrase: str):
    blob = encrypt_vault(data, passphrase)
    with open(VAULT_PATH, "wb") as f:
        f.write(blob)


def prompt(label: str, confirm_label: str = None) -> str:
    value = getpass.getpass(f"{label}: ")
    if confirm_label:
        confirm = getpass.getpass(f"{confirm_label}: ")
        if value != confirm:
            print("ERROR: Values do not match.")
            sys.exit(1)
    return value


def cmd_store(name: str, value: str = None, passphrase: str = None):
    if value is None:
        value = prompt(f"Value for '{name}'")
    if not value:
        print("ERROR: Value cannot be empty.")
        sys.exit(1)

    if os.path.exists(VAULT_PATH):
        if passphrase is None:
            passphrase = prompt("Vault passphrase")
        vault = decrypt_vault(passphrase)
    else:
        print("No vault found — creating a new one.")
        if passphrase is None:
            passphrase = prompt("Choose a passphrase", "Confirm passphrase")
        vault = {}

    vault[name] = value
    save_vault(vault, passphrase)
    print(f"Stored '{name}'. Vault saved to cortex.secrets.enc")
    print("Commit and push to persist across devices.")


def cmd_get(name: str, passphrase: str = None):
    if not os.path.exists(VAULT_PATH):
        print("ERROR: No vault found.")
        sys.exit(1)
    if passphrase is None:
        passphrase = prompt("Vault passphrase")
    vault = decrypt_vault(passphrase)
    if name not in vault:
        print(f"ERROR: No secret named '{name}'.")
        sys.exit(1)
    print(vault[name])


def cmd_list(passphrase: str = None):
    if not os.path.exists(VAULT_PATH):
        print("No vault found.")
        return
    if passphrase is None:
        passphrase = prompt("Vault passphrase")
    vault = decrypt_vault(passphrase)
    if not vault:
        print("Vault is empty.")
        return
    print("Stored secrets:")
    for k in sorted(vault):
        print(f"  {k}")


def cmd_delete(name: str, passphrase: str = None):
    if not os.path.exists(VAULT_PATH):
        print("ERROR: No vault found.")
        sys.exit(1)
    if passphrase is None:
        passphrase = prompt("Vault passphrase")
    vault = decrypt_vault(passphrase)
    if name not in vault:
        print(f"ERROR: No secret named '{name}'.")
        sys.exit(1)
    del vault[name]
    save_vault(vault, passphrase)
    print(f"Deleted '{name}'.")


def main():
    parser = argparse.ArgumentParser(description="Cortex secrets vault", add_help=True)
    sub = parser.add_subparsers(dest="cmd")

    p_store = sub.add_parser("store")
    p_store.add_argument("name")
    p_store.add_argument("--value", default=None)
    p_store.add_argument("--passphrase", default=None)

    p_get = sub.add_parser("get")
    p_get.add_argument("name")
    p_get.add_argument("--passphrase", default=None)

    p_list = sub.add_parser("list")
    p_list.add_argument("--passphrase", default=None)

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("name")
    p_delete.add_argument("--passphrase", default=None)

    args = parser.parse_args()

    if args.cmd == "store":
        cmd_store(args.name, value=args.value, passphrase=args.passphrase)
    elif args.cmd == "get":
        cmd_get(args.name, passphrase=args.passphrase)
    elif args.cmd == "list":
        cmd_list(passphrase=args.passphrase)
    elif args.cmd == "delete":
        cmd_delete(args.name, passphrase=args.passphrase)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
