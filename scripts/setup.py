#!/usr/bin/env python3
"""
Cortex setup script.
Detects environment, writes cortex.config, creates .gitignore, verifies repo structure.

Usage:
  python scripts/setup.py              # environment check only
  python scripts/setup.py --system     # also install system dependencies (may use sudo)

Run once on first use, or re-run any time to repair the environment.
Invoked automatically by setup.sh (Linux/macOS) and setup.ps1 (Windows).
"""

import os
import sys
import shutil
import subprocess
import json
import argparse
import platform

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "cortex.config")
GITIGNORE_PATH = os.path.join(ROOT, ".gitignore")

REQUIRED_FILES = [
    "protocol/CORTEX.md",
    "protocol/GUARDRAILS.md",
    "protocol/DISCLAIMER.md",
    "protocol/ROE.md",
]

GITIGNORE_ENTRIES = ["cortex.config", ".env"]


# ── OS / package manager detection ───────────────────────────────────────────

def detect_pkg_manager():
    if sys.platform == "darwin":
        return "brew"
    if sys.platform == "win32":
        return "winget"
    # Linux — check /etc/os-release
    try:
        with open("/etc/os-release") as f:
            content = f.read()
        for line in content.splitlines():
            if line.startswith("ID="):
                distro = line.split("=", 1)[1].strip().strip('"').lower()
                if distro in ("arch", "cachyos", "manjaro", "endeavouros"):
                    return "pacman"
                if distro in ("ubuntu", "debian", "linuxmint", "pop"):
                    return "apt"
                if distro in ("fedora", "rhel", "centos"):
                    return "dnf"
    except FileNotFoundError:
        pass
    return None


def sudo(cmd: list) -> int:
    print(f"  [sudo] {' '.join(cmd)}")
    return subprocess.run(["sudo"] + cmd).returncode


def run(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, **kwargs)


# ── Dependency installers ─────────────────────────────────────────────────────

def ensure_cryptography(pkg: str) -> bool:
    """Returns True if already present or successfully installed."""
    try:
        import cryptography  # noqa: F401
        return True
    except ImportError:
        pass

    print("  cryptography: not installed — installing...")
    if pkg == "pacman":
        return sudo(["pacman", "-S", "--noconfirm", "python-cryptography"]) == 0
    if pkg == "apt":
        return sudo(["apt-get", "install", "-y", "python3-cryptography"]) == 0
    if pkg == "dnf":
        return sudo(["dnf", "install", "-y", "python3-cryptography"]) == 0
    if pkg in ("brew", "winget"):
        # pip is the right path on macOS/Windows
        return run([sys.executable, "-m", "pip", "install", "cryptography"]).returncode == 0
    print("  cryptography: cannot auto-install — run: pip install cryptography")
    return False


def ensure_rclone(pkg: str) -> bool:
    if shutil.which("rclone"):
        return True
    print("  rclone: not installed — installing...")
    if pkg == "pacman":
        return sudo(["pacman", "-S", "--noconfirm", "rclone"]) == 0
    if pkg == "apt":
        return sudo(["apt-get", "install", "-y", "rclone"]) == 0
    if pkg == "dnf":
        return sudo(["dnf", "install", "-y", "rclone"]) == 0
    if pkg == "brew":
        return run(["brew", "install", "rclone"]).returncode == 0
    if pkg == "winget":
        return run(["winget", "install", "-e", "--id", "Rclone.Rclone", "--silent"]).returncode == 0
    # Universal fallback
    print("  rclone: cannot auto-install — see https://rclone.org/install/")
    return False


def ensure_tailscale(pkg: str) -> bool:
    if not shutil.which("tailscale"):
        print("  tailscale: not installed — installing...")
        if pkg == "pacman":
            ok = sudo(["pacman", "-S", "--noconfirm", "tailscale"]) == 0
        elif pkg == "apt":
            # Official install script is the safest cross-distro method
            ok = run(
                ["sh", "-c", "curl -fsSL https://tailscale.com/install.sh | sh"]
            ).returncode == 0
        elif pkg == "dnf":
            ok = run(
                ["sh", "-c", "curl -fsSL https://tailscale.com/install.sh | sh"]
            ).returncode == 0
        elif pkg == "brew":
            ok = run(["brew", "install", "tailscale"]).returncode == 0
        elif pkg == "winget":
            ok = run(
                ["winget", "install", "-e", "--id", "tailscale.tailscale", "--silent"]
            ).returncode == 0
        else:
            print("  tailscale: cannot auto-install — see https://tailscale.com/download")
            return False
        if not ok:
            return False

    # Set operator so tailscale runs without sudo going forward
    if sys.platform not in ("darwin", "win32") and shutil.which("tailscale"):
        user = os.environ.get("USER") or os.environ.get("USERNAME") or ""
        if user:
            result = run(
                ["tailscale", "debug", "prefs"],
                capture_output=True, text=True
            )
            # Only set if not already operator
            if "OperatorUser" not in result.stdout or user not in result.stdout:
                print(f"  tailscale: setting operator={user} (allows non-root use)...")
                sudo(["tailscale", "set", f"--operator={user}"])

    return True


# ── System deps ───────────────────────────────────────────────────────────────

def install_system_deps():
    pkg = detect_pkg_manager()
    if not pkg:
        print("WARNING: Could not detect package manager. Some deps may need manual install.")

    print("\nSystem dependencies:")

    results = {}

    results["cryptography"] = ensure_cryptography(pkg)
    print(f"  cryptography: {'OK' if results['cryptography'] else 'FAILED'}")

    results["rclone"] = ensure_rclone(pkg)
    print(f"  rclone: {'OK' if results['rclone'] else 'FAILED — install manually: https://rclone.org/install/'}")

    results["tailscale"] = ensure_tailscale(pkg)
    print(f"  tailscale: {'OK' if results['tailscale'] else 'FAILED — install manually: https://tailscale.com/download'}")

    return results


# ── Core setup ────────────────────────────────────────────────────────────────

def detect_environment():
    env = {}
    env["python"] = shutil.which("python3") or shutil.which("python")
    env["git"] = shutil.which("git")
    env["shell"] = "powershell" if sys.platform == "win32" else (
        "bash" if shutil.which("bash") else "sh"
    )
    env["node"] = shutil.which("node")
    env["ollama"] = shutil.which("ollama")
    env["rclone"] = shutil.which("rclone")
    env["tailscale"] = shutil.which("tailscale")
    return env


def check_required_files():
    return [f for f in REQUIRED_FILES if not os.path.exists(os.path.join(ROOT, f))]


def ensure_gitignore():
    existing = []
    if os.path.exists(GITIGNORE_PATH):
        with open(GITIGNORE_PATH) as f:
            existing = f.read().splitlines()
    added = []
    with open(GITIGNORE_PATH, "a") as f:
        for entry in GITIGNORE_ENTRIES:
            if entry not in existing:
                f.write(f"{entry}\n")
                added.append(entry)
    return added


def write_config(env):
    config = {k: v for k, v in env.items()}
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def setup_git():
    result = run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT, capture_output=True, text=True
    )
    if result.returncode != 0:
        print("\nWARNING: Not a git repo.")
        print("Run: git init && git remote add origin <your-private-repo-url>")
        return

    print("git repo: OK")
    remotes = run(["git", "remote"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    if "upstream" not in remotes:
        run(["git", "remote", "add", "upstream", "https://github.com/cordfuse/cortex.git"],
            cwd=ROOT, capture_output=True)
        print("upstream remote: added (https://github.com/cordfuse/cortex.git)")
    else:
        print("upstream remote: OK")


def main():
    parser = argparse.ArgumentParser(description="Cortex setup")
    parser.add_argument(
        "--system",
        action="store_true",
        help="Install system dependencies (cryptography, rclone, tailscale). May use sudo."
    )
    args = parser.parse_args()

    print("Cortex setup")
    print("------------")

    # Protocol files
    missing = check_required_files()
    if missing:
        print(f"ERROR: Required protocol files missing: {', '.join(missing)}")
        print("Your Cortex repo is incomplete. Re-clone from the template.")
        sys.exit(1)
    print("Protocol files: OK")

    # Environment
    env = detect_environment()
    print(f"\nEnvironment:")
    print(f"  Shell:      {env['shell']}")
    print(f"  Python:     {env['python'] or 'not found'}")
    print(f"  Git:        {env['git'] or 'not found'}")
    print(f"  Node:       {env['node'] or 'not found'}")
    print(f"  Ollama:     {env['ollama'] or 'not found'}")
    print(f"  rclone:     {env['rclone'] or 'not found'}")
    print(f"  tailscale:  {env['tailscale'] or 'not found'}")

    if not env["git"]:
        print("\nERROR: git is required.")
        sys.exit(1)

    # Cryptography check (without --system, just warn)
    if not args.system:
        try:
            import cryptography  # noqa: F401
            print("  cryptography: OK")
        except ImportError:
            print("  cryptography: NOT INSTALLED")
            print("  Re-run with --system to install, or: pip install cryptography")

    # System deps
    if args.system:
        install_system_deps()

    # Config + gitignore
    write_config(env)
    print(f"\ncortex.config: written (gitignored)")

    added = ensure_gitignore()
    if added:
        print(f".gitignore: updated ({', '.join(added)})")
    else:
        print(".gitignore: OK")

    # Git + upstream
    setup_git()

    print("\nSetup complete. Open this directory in your AI agent and say hello.")


if __name__ == "__main__":
    main()
