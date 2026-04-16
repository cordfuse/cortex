#!/usr/bin/env python3
"""
Cortex secrets vault.
AES-256-GCM encrypted key/value store. Vault file committed to repo — safe because encrypted.

Usage:
  python scripts/secrets.py store <name>        # prompt for value and passphrase
  python scripts/secrets.py get <name>          # decrypt and print value
  python scripts/secrets.py list                # list stored secret names (not values)
  python scripts/secrets.py delete <name>       # remove a secret from the vault

Requires: pip install cryptography
"""

import os
import sys
import json
import base64
import getpass

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


def cmd_store(name: str):
    value = getpass.getpass(f"Value for '{name}': ")
    if not value:
        print("ERROR: Value cannot be empty.")
        sys.exit(1)

    if os.path.exists(VAULT_PATH):
        passphrase = getpass.getpass("Vault passphrase: ")
        vault = decrypt_vault(passphrase)
    else:
        print("No vault found — creating a new one.")
        passphrase = getpass.getpass("Choose a passphrase: ")
        confirm = getpass.getpass("Confirm passphrase: ")
        if passphrase != confirm:
            print("ERROR: Passphrases do not match.")
            sys.exit(1)
        vault = {}

    vault[name] = value
    save_vault(vault, passphrase)
    print(f"Stored '{name}'. Vault saved to cortex.secrets.enc")
    print("Commit and push to persist across devices.")


def cmd_get(name: str):
    if not os.path.exists(VAULT_PATH):
        print("ERROR: No vault found.")
        sys.exit(1)
    passphrase = getpass.getpass("Vault passphrase: ")
    vault = decrypt_vault(passphrase)
    if name not in vault:
        print(f"ERROR: No secret named '{name}'.")
        sys.exit(1)
    print(vault[name])


def cmd_list():
    if not os.path.exists(VAULT_PATH):
        print("No vault found.")
        return
    passphrase = getpass.getpass("Vault passphrase: ")
    vault = decrypt_vault(passphrase)
    if not vault:
        print("Vault is empty.")
        return
    print("Stored secrets:")
    for k in sorted(vault):
        print(f"  {k}")


def cmd_delete(name: str):
    if not os.path.exists(VAULT_PATH):
        print("ERROR: No vault found.")
        sys.exit(1)
    passphrase = getpass.getpass("Vault passphrase: ")
    vault = decrypt_vault(passphrase)
    if name not in vault:
        print(f"ERROR: No secret named '{name}'.")
        sys.exit(1)
    del vault[name]
    save_vault(vault, passphrase)
    print(f"Deleted '{name}'.")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    cmd = args[0]

    if cmd == "store" and len(args) == 2:
        cmd_store(args[1])
    elif cmd == "get" and len(args) == 2:
        cmd_get(args[1])
    elif cmd == "list" and len(args) == 1:
        cmd_list()
    elif cmd == "delete" and len(args) == 2:
        cmd_delete(args[1])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
