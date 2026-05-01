#!/usr/bin/env bash
# Cortex bootstrap — Linux and macOS
# Usage: bash setup.sh
# Run once on first use, or re-run any time to repair the environment.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Cortex bootstrap"
echo "----------------"

# ── Detect OS ─────────────────────────────────────────────────────────────────

OS="unknown"
PKG=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ -f /etc/os-release ]]; then
    . /etc/os-release
    case "$ID" in
        arch|cachyos|manjaro|endeavouros) OS="arch";  PKG="pacman" ;;
        ubuntu|debian|linuxmint|pop)     OS="debian"; PKG="apt"    ;;
        fedora|rhel|centos)              OS="fedora"; PKG="dnf"    ;;
        *)                               OS="linux"               ;;
    esac
fi

echo "OS: $OS"

# ── Python ────────────────────────────────────────────────────────────────────

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [[ -z "$PYTHON" ]]; then
    echo ""
    echo "Python not found. Installing..."
    case "$OS" in
        macos)  brew install python3 ;;
        arch)   sudo pacman -S --noconfirm python ;;
        debian) sudo apt-get install -y python3 ;;
        fedora) sudo dnf install -y python3 ;;
        *)
            echo "ERROR: Cannot install Python automatically on this system."
            echo "Install Python 3.9+ manually, then re-run this script."
            exit 1
            ;;
    esac
    PYTHON="$(command -v python3 || command -v python)"
fi

echo "Python: $PYTHON ($($PYTHON --version 2>&1))"

# ── Git ───────────────────────────────────────────────────────────────────────

if ! command -v git &>/dev/null; then
    echo ""
    echo "git not found. Installing..."
    case "$OS" in
        macos)  brew install git ;;
        arch)   sudo pacman -S --noconfirm git ;;
        debian) sudo apt-get install -y git ;;
        fedora) sudo dnf install -y git ;;
        *)
            echo "ERROR: Cannot install git automatically. Install it manually."
            exit 1
            ;;
    esac
fi

echo "git: $(git --version)"

# ── Hand off to setup.py --system ─────────────────────────────────────────────

echo ""
"$PYTHON" "$SCRIPT_DIR/scripts/setup.py" --system
