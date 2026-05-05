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

# ── Bun ──────────────────────────────────────────────────────────────────────

if ! command -v bun &>/dev/null; then
    echo ""
    echo "Bun not found. Installing..."
    case "$OS" in
        macos)  brew install bun ;;
        arch)   sudo pacman -S --noconfirm bun ;;
        *)      curl -fsSL https://bun.sh/install | bash
                export PATH="$HOME/.bun/bin:$PATH" ;;
    esac
fi

echo "Bun: $(bun --version)"

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

# ── Hand off to setup.ts --system ─────────────────────────────────────────────

echo ""
bun "$SCRIPT_DIR/manifest/framework/scripts/setup.ts" --system

# ── .claude/settings.json starter (v4.0.0-alpha.34+) ──────────────────────────
# If the consumer is using Claude Code, write a starter settings.json from
# the template. This prevents silent permission-prompt hangs in
# remote-control / mobile sessions where prompts can't be answered.
# Skip if .claude/settings.json already exists (don't overwrite user customizations).

REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CLAUDE_DIR="$REPO_ROOT/.claude"
CLAUDE_SETTINGS="$CLAUDE_DIR/settings.json"
TEMPLATE="$REPO_ROOT/manifest/framework/templates/claude-settings.json"

if [[ -f "$TEMPLATE" && ! -f "$CLAUDE_SETTINGS" ]]; then
    echo ""
    echo "Writing starter .claude/settings.json (Claude Code permissions)..."
    mkdir -p "$CLAUDE_DIR"
    cp "$TEMPLATE" "$CLAUDE_SETTINGS"
    echo "  Wrote: $CLAUDE_SETTINGS"
    echo "  Edit it to customize Claude Code permissions for this cortex."
fi
