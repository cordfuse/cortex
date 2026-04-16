#!/usr/bin/env python3
"""
Cortex setup script.
Detects environment, writes cortex.config, creates .gitignore, verifies repo structure.
Run once on first use: python scripts/setup.py
"""

import os
import sys
import shutil
import subprocess
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "cortex.config")
GITIGNORE_PATH = os.path.join(ROOT, ".gitignore")

REQUIRED_FILES = ["CORTEX.md", "GUARDRAILS.md", "DISCLAIMER.md", "ROE.md"]

GITIGNORE_ENTRIES = ["cortex.config", ".env"]


def detect_environment():
    env = {}

    # Python
    env["python"] = shutil.which("python3") or shutil.which("python")

    # Git
    env["git"] = shutil.which("git")

    # Shell
    if sys.platform == "win32":
        env["shell"] = "powershell"
    else:
        env["shell"] = "bash" if shutil.which("bash") else "sh"

    # Node
    env["node"] = shutil.which("node")

    # Ollama
    env["ollama"] = shutil.which("ollama")

    return env


def check_required_files():
    missing = []
    for f in REQUIRED_FILES:
        if not os.path.exists(os.path.join(ROOT, f)):
            missing.append(f)
    return missing


def ensure_gitignore():
    existing = []
    if os.path.exists(GITIGNORE_PATH):
        with open(GITIGNORE_PATH, "r") as f:
            existing = f.read().splitlines()

    added = []
    with open(GITIGNORE_PATH, "a") as f:
        for entry in GITIGNORE_ENTRIES:
            if entry not in existing:
                f.write(f"{entry}\n")
                added.append(entry)

    return added


def write_config(env):
    config = {
        "shell": env["shell"],
        "python": env["python"],
        "git": env["git"],
        "node": env["node"],
        "ollama": env["ollama"],
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    return config


def main():
    print("Cortex setup\n")

    # Check required protocol files
    missing = check_required_files()
    if missing:
        print(f"ERROR: Required protocol files missing: {', '.join(missing)}")
        print("Your Cortex repo is incomplete. Re-clone from the template.")
        sys.exit(1)
    print(f"Protocol files: OK ({', '.join(REQUIRED_FILES)})")

    # Detect environment
    env = detect_environment()
    print(f"\nEnvironment detected:")
    print(f"  Shell:   {env['shell']}")
    print(f"  Python:  {env['python'] or 'not found'}")
    print(f"  Git:     {env['git'] or 'not found'}")
    print(f"  Node:    {env['node'] or 'not found'}")
    print(f"  Ollama:  {env['ollama'] or 'not found'}")

    if not env["git"]:
        print("\nERROR: git is required. Install it and run setup again.")
        sys.exit(1)

    # Check cryptography package (required for secrets vault)
    try:
        import cryptography  # noqa: F401
        print(f"  cryptography: OK")
    except ImportError:
        print(f"  cryptography: NOT INSTALLED")
        print("  Run: pip install cryptography  (required for secrets vault)")

    # Write cortex.config
    write_config(env)
    print(f"\nWrote cortex.config (gitignored — machine-specific)")

    # Ensure .gitignore
    added = ensure_gitignore()
    if added:
        print(f"Updated .gitignore: {', '.join(added)}")
    else:
        print(f".gitignore: OK")

    # Check git repo
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT, capture_output=True, text=True
    )
    if result.returncode != 0:
        print("\nWARNING: This directory is not a git repo.")
        print("Run: git init && git remote add origin <your-private-repo-url>")
    else:
        print("Git repo: OK")

    print("\nSetup complete. Open this directory in your AI agent and say hello.")


if __name__ == "__main__":
    main()
