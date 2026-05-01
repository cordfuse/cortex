#!/usr/bin/env bash
# Cortex installer — macOS and Linux
#
# Pipe:   curl -fsSL https://github.com/cordfuse/cortex/releases/latest/download/install.sh | bash
# Local:  bash install.sh

set -e

# ── Colours ───────────────────────────────────────────────────────────────────

if [ -t 1 ]; then
    BOLD='\033[1m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; RESET='\033[0m'
else
    BOLD=''; GREEN=''; YELLOW=''; RED=''; RESET=''
fi

ok()   { printf "  ${GREEN}✓${RESET} %s\n" "$1"; }
warn() { printf "  ${YELLOW}!${RESET} %s\n" "$1"; }
err()  { printf "  ${RED}✗${RESET} %s\n" "$1" >&2; }

open_url() {
    if command -v open &>/dev/null; then
        open "$1"
    elif command -v xdg-open &>/dev/null; then
        xdg-open "$1" &>/dev/null &
    fi
}

# ── Prompt helpers (safe when stdin is a pipe) ────────────────────────────────

ask() {
    # ask <var> <prompt> [default]
    local _var="$1" _prompt="$2" _default="$3" _val
    if [ -n "$_default" ]; then
        printf "  %s [%s]: " "$_prompt" "$_default" >/dev/tty
    else
        printf "  %s: " "$_prompt" >/dev/tty
    fi
    IFS= read -r _val </dev/tty
    [ -z "$_val" ] && _val="$_default"
    eval "$_var=\"\$_val\""
}

ask_yn() {
    # ask_yn <var> <prompt>  — result is "y" or empty
    local _var="$1" _prompt="$2" _val
    printf "  %s [y/N]: " "$_prompt" >/dev/tty
    IFS= read -r _val </dev/tty
    eval "$_var=\"\$_val\""
}

# ── Header ────────────────────────────────────────────────────────────────────

echo ""
printf "${BOLD}Cortex installer${RESET}\n"
echo "────────────────────────────────────"
echo ""

# ── OS detection ──────────────────────────────────────────────────────────────

OS="unknown"
PKG=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ -f /etc/os-release ]]; then
    . /etc/os-release
    case "${ID:-}" in
        arch|cachyos|manjaro|endeavouros) OS="arch";  PKG="pacman" ;;
        ubuntu|debian|linuxmint|pop)     OS="debian"; PKG="apt"    ;;
        fedora|rhel|centos)              OS="fedora"; PKG="dnf"    ;;
        *)                               OS="linux"               ;;
    esac
fi

# ── Scan ──────────────────────────────────────────────────────────────────────

printf "${BOLD}Scanning...${RESET}\n"

GIT_OK=false
if command -v git &>/dev/null; then
    ok "git $(git --version | awk '{print $3}')"
    GIT_OK=true
else
    warn "git: not found — will install"
fi

PYTHON=""
for _cmd in python3 python; do
    if command -v "$_cmd" &>/dev/null && "$_cmd" --version &>/dev/null 2>&1; then
        PYTHON="$_cmd"; break
    fi
done
if [[ -n "$PYTHON" ]]; then
    ok "python $($PYTHON --version 2>&1 | awk '{print $2}')"
else
    warn "python: not found — will install"
fi

if [[ -n "$PYTHON" ]] && "$PYTHON" -c "import cryptography" 2>/dev/null; then
    ok "cryptography: installed"
else
    warn "cryptography: not installed (setup will install)"
fi

if command -v rclone &>/dev/null; then
    ok "rclone $(rclone --version 2>&1 | head -1 | awk '{print $2}')"
else
    warn "rclone: not found (setup will install)"
fi

if command -v tailscale &>/dev/null; then
    ok "tailscale: installed"
else
    warn "tailscale: not found (optional — setup will install)"
fi

echo ""

# ── Install git if missing ────────────────────────────────────────────────────

if ! $GIT_OK; then
    printf "${BOLD}Installing git...${RESET}\n"
    case "$OS" in
        macos)
            if command -v brew &>/dev/null; then brew install git
            else err "Homebrew not found. Install git from https://git-scm.com/download/mac"; exit 1; fi
            ;;
        arch)   sudo pacman -S --noconfirm git ;;
        debian) sudo apt-get install -y git ;;
        fedora) sudo dnf install -y git ;;
        *) err "Cannot auto-install git. Install it manually then re-run."; exit 1 ;;
    esac
    ok "git installed"
    echo ""
fi

# ── Install Python if missing ─────────────────────────────────────────────────

if [[ -z "$PYTHON" ]]; then
    printf "${BOLD}Installing Python...${RESET}\n"
    case "$OS" in
        macos)
            if command -v brew &>/dev/null; then brew install python3
            else err "Homebrew not found. Install Python from https://python.org/downloads/"; exit 1; fi
            PYTHON="python3"
            ;;
        arch)   sudo pacman -S --noconfirm python; PYTHON="python3" ;;
        debian) sudo apt-get install -y python3; PYTHON="python3" ;;
        fedora) sudo dnf install -y python3; PYTHON="python3" ;;
        *) err "Cannot auto-install Python. Install Python 3.9+ then re-run."; exit 1 ;;
    esac
    ok "Python installed"
    echo ""
fi

# ── Repo input ────────────────────────────────────────────────────────────────

printf "${BOLD}Your Cortex repo${RESET}\n"
echo "  Accepted formats:"
echo "    username/repo-name              (GitHub shorthand)"
echo "    https://github.com/user/repo    (HTTPS URL)"
echo "    git@github.com:user/repo.git    (SSH URL)"
echo ""

ask REPO_INPUT "Repo"
REPO_INPUT="${REPO_INPUT// /}"

if [[ -z "$REPO_INPUT" ]]; then
    err "No repo entered."; exit 1
fi

USE_SSH=false
USE_GH=false
GH_PAT=""

if [[ "$REPO_INPUT" =~ ^git@ ]]; then
    CLONE_URL="$REPO_INPUT"
    HTTPS_PROBE="https://$(echo "$REPO_INPUT" | sed 's|git@||; s|:|/|; s|\.git$||')"
    USE_SSH=true
elif [[ "$REPO_INPUT" =~ ^https:// ]]; then
    CLONE_URL="${REPO_INPUT%.git}.git"
    HTTPS_PROBE="${REPO_INPUT%.git}"
elif [[ "$REPO_INPUT" =~ ^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$ ]]; then
    CLONE_URL="https://github.com/${REPO_INPUT}.git"
    HTTPS_PROBE="https://github.com/${REPO_INPUT}"
else
    err "Could not parse: $REPO_INPUT"; exit 1
fi

echo ""

# ── Visibility check ──────────────────────────────────────────────────────────

printf "${BOLD}Checking repo visibility...${RESET}\n"

IS_PUBLIC=false
if GIT_TERMINAL_PROMPT=0 git ls-remote --exit-code "$CLONE_URL" HEAD &>/dev/null 2>&1; then
    IS_PUBLIC=true
fi

if $IS_PUBLIC && ! $USE_SSH; then
    echo ""
    warn "Your repo is PUBLIC."
    echo ""
    echo "  Cortex records are personal and sensitive — your repo should be private."
    echo "  Make it private at: ${HTTPS_PROBE}/settings"
    echo "  Settings → Danger Zone → Change visibility → Make private"
    echo ""
    printf "  Press Enter to open your repo settings in the browser (n to skip): " >/dev/tty
    IFS= read -r _open_now </dev/tty
    if [[ ! "$_open_now" =~ ^[Nn] ]]; then
        open_url "${HTTPS_PROBE}/settings"
    fi
    echo ""
    ask_yn CONT "Continue with a public repo anyway?"
    if [[ ! "$CONT" =~ ^[Yy] ]]; then
        echo ""
        echo "  Make it private, then re-run:"
        echo "  curl -fsSL https://github.com/cordfuse/cortex/releases/latest/download/install.sh | bash"
        echo ""
        exit 0
    fi
    echo ""
elif ! $IS_PUBLIC && ! $USE_SSH; then
    ok "Repo is private."
    echo ""
    if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
        ok "GitHub CLI authenticated — will use gh for clone."
        USE_GH=true
    else
        warn "Private repo — authentication needed."
        echo ""
        echo "  Options:"
        echo "    1) Personal Access Token (PAT) — generate at https://github.com/settings/tokens/new"
        echo "       Required scope: repo (read)"
        echo "    2) SSH — re-run using git@github.com:user/repo.git format"
        echo "    3) GitHub CLI — run: gh auth login, then re-run this installer"
        echo ""
        ask GH_PAT "PAT (leave blank to try SSH fallback)"
        if [[ -z "$GH_PAT" ]]; then
            CLONE_URL="git@github.com:$(echo "$CLONE_URL" | sed 's|https://github.com/||')"
            ok "Using SSH fallback."
        fi
    fi
    echo ""
else
    ok "SSH URL — skipping visibility probe."
    echo ""
fi

# ── Clone destination ─────────────────────────────────────────────────────────

printf "${BOLD}Clone destination${RESET}\n"
ask CLONE_DEST "Path" "$HOME/cortex"
CLONE_DEST="${CLONE_DEST/#\~/$HOME}"
echo ""

if [[ -d "$CLONE_DEST/.git" ]]; then
    warn "A git repo already exists at $CLONE_DEST."
    ask_yn REUSE "Skip clone and run setup only?"
    if [[ "$REUSE" =~ ^[Yy] ]]; then
        echo ""
        COMMIT_COUNT=$(git -C "$CLONE_DEST" rev-list --count HEAD 2>/dev/null || echo "0")
        if [[ "$COMMIT_COUNT" -le 1 ]]; then
            echo "  Fresh Cortex — running first-time setup."
        else
            echo "  Existing Cortex ($COMMIT_COUNT commits) — repairing environment. Your records are untouched."
        fi
        echo ""
        printf "${BOLD}Running setup...${RESET}\n"
        "$PYTHON" "$CLONE_DEST/scripts/setup.py" --system
        echo ""
        printf "${BOLD}${GREEN}Done.${RESET}\n"
        echo ""
        echo "  Open $CLONE_DEST in your AI agent and say hello."
        echo ""
        exit 0
    else
        err "Aborted. Choose a different path."; exit 1
    fi
fi

# ── Clone ─────────────────────────────────────────────────────────────────────

printf "${BOLD}Cloning...${RESET}\n"

if $USE_GH; then
    gh repo clone "$REPO_INPUT" "$CLONE_DEST"
elif [[ -n "$GH_PAT" ]]; then
    AUTHED_URL=$(echo "$CLONE_URL" | sed "s|https://|https://${GH_PAT}@|")
    git clone "$AUTHED_URL" "$CLONE_DEST"
    git -C "$CLONE_DEST" remote set-url origin "$CLONE_URL"
else
    git clone "$CLONE_URL" "$CLONE_DEST"
fi

ok "Cloned to $CLONE_DEST"
echo ""

# ── Fresh vs existing ─────────────────────────────────────────────────────────

COMMIT_COUNT=$(git -C "$CLONE_DEST" rev-list --count HEAD 2>/dev/null || echo "0")
if [[ "$COMMIT_COUNT" -le 1 ]]; then
    echo "  Fresh Cortex — this is your first session."
else
    echo "  Existing Cortex detected ($COMMIT_COUNT commits) — environment repair only. Your records are untouched."
fi
echo ""

# ── Setup ─────────────────────────────────────────────────────────────────────

printf "${BOLD}Running setup...${RESET}\n"
"$PYTHON" "$CLONE_DEST/scripts/setup.py" --system

# ── Upstream remote + .cortex-version ────────────────────────────────────────

printf "${BOLD}Wiring upstream framework...${RESET}\n"

UPSTREAM_URL="https://github.com/cordfuse/cortex.git"

if ! git -C "$CLONE_DEST" remote get-url upstream &>/dev/null 2>&1; then
    git -C "$CLONE_DEST" remote add upstream "$UPSTREAM_URL"
    ok "Upstream remote added (cordfuse/cortex)"
else
    ok "Upstream remote already set"
fi

git -C "$CLONE_DEST" fetch upstream --quiet 2>/dev/null || warn "Could not reach upstream — .cortex-version will be set from local version.txt"

FRAMEWORK_VERSION=""
if git -C "$CLONE_DEST" cat-file -e upstream/main:version.txt 2>/dev/null; then
    FRAMEWORK_VERSION=$(git -C "$CLONE_DEST" show upstream/main:version.txt 2>/dev/null | tr -d '[:space:]')
fi

if [[ -z "$FRAMEWORK_VERSION" ]] && [[ -f "$CLONE_DEST/version.txt" ]]; then
    FRAMEWORK_VERSION=$(cat "$CLONE_DEST/version.txt" | tr -d '[:space:]')
fi

if [[ -n "$FRAMEWORK_VERSION" ]]; then
    echo "$FRAMEWORK_VERSION" > "$CLONE_DEST/.cortex-version"
    git -C "$CLONE_DEST" add .cortex-version
    git -C "$CLONE_DEST" commit -m "install: set .cortex-version to framework v${FRAMEWORK_VERSION}" --quiet
    ok ".cortex-version set to v${FRAMEWORK_VERSION}"
else
    warn "Could not determine framework version — .cortex-version not written"
fi

echo ""
printf "${BOLD}${GREEN}Done.${RESET}\n"
echo ""
echo "  Open $CLONE_DEST in your AI agent and say hello."
echo ""

# ── Post-install public repo reminder ────────────────────────────────────────

if $IS_PUBLIC; then
    echo "  ┌─────────────────────────────────────────────────────────────────┐"
    printf "  │ ${YELLOW}REMINDER: Your repo is still PUBLIC.${RESET}                            │\n"
    echo "  │                                                                 │"
    echo "  │  Your Cortex will store personal records. Make it private now.  │"
    echo "  └─────────────────────────────────────────────────────────────────┘"
    echo ""
    printf "  Press Enter to open your repo settings in the browser (n to skip): " >/dev/tty
    IFS= read -r _open_reminder </dev/tty
    if [[ ! "$_open_reminder" =~ ^[Nn] ]]; then
        open_url "${HTTPS_PROBE}/settings"
        echo ""
        echo "  Settings → Danger Zone → Change visibility → Make private"
    fi
    echo ""
fi
