# Cortex installer — Windows (PowerShell)
#
# Pipe:   iex (irm https://github.com/cordfuse/cortex/releases/latest/download/install.ps1)
# Local:  .\install.ps1
#
# Requires PowerShell 5.1+ (built into Windows 10 and 11).

$ErrorActionPreference = "Stop"

function Ok   { param($msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function Warn { param($msg) Write-Host "  [!]  $msg" -ForegroundColor Yellow }
function Err  { param($msg) Write-Host "  [X]  $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "Cortex installer" -ForegroundColor White -BackgroundColor Black
Write-Host "------------------------------------"
Write-Host ""

# ── Scan ──────────────────────────────────────────────────────────────────────

Write-Host "Scanning your system..." -ForegroundColor Cyan

$GitOk = $false
if (Get-Command git -ErrorAction SilentlyContinue) {
    $v = (git --version) -replace "git version ", ""
    Ok "git $v"
    $GitOk = $true
} else { Warn "git: not found — will install" }

$Python = $null
foreach ($cmd in @("python3", "python")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) { $Python = $cmd; break }
}
if ($Python) {
    $v = (& $Python --version 2>&1) -replace "Python ", ""
    Ok "python $v"
} else { Warn "python: not found — will install" }

if ($Python) {
    $cryptoOk = & $Python -c "import cryptography; print('ok')" 2>&1
    if ($cryptoOk -eq "ok") { Ok "cryptography: installed" }
    else { Warn "cryptography: not installed (setup will install)" }
}

if (Get-Command rclone -ErrorAction SilentlyContinue) {
    $v = (rclone --version 2>&1 | Select-Object -First 1) -replace "rclone ", ""
    Ok "rclone $v"
} else { Warn "rclone: not found (setup will install)" }

if (Get-Command tailscale -ErrorAction SilentlyContinue) { Ok "tailscale: installed" }
else { Warn "tailscale: not found (optional — setup will install)" }

Write-Host ""

# ── Install git if missing ────────────────────────────────────────────────────

if (-not $GitOk) {
    Write-Host "Installing git..." -ForegroundColor Cyan
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install -e --id Git.Git --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                    [System.Environment]::GetEnvironmentVariable("Path","User")
        Ok "git installed"
    } else {
        Err "winget not available."
        Write-Host "  Install Git from https://git-scm.com/download/win"
        Write-Host "  Enable 'Add Git to PATH' during install, then re-run this script."
        exit 1
    }
    Write-Host ""
}

# ── Install Python if missing ─────────────────────────────────────────────────

if (-not $Python) {
    Write-Host "Installing Python..." -ForegroundColor Cyan
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install -e --id Python.Python.3 --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                    [System.Environment]::GetEnvironmentVariable("Path","User")
        $Python = "python"
        Ok "Python installed"
    } else {
        Err "winget not available."
        Write-Host "  Install Python from https://python.org/downloads/"
        Write-Host "  Check 'Add Python to PATH' during install, then re-run this script."
        exit 1
    }
    Write-Host ""
}

# ── Repo input ────────────────────────────────────────────────────────────────

Write-Host "Your Cortex repo" -ForegroundColor Cyan
Write-Host "  Accepted formats:"
Write-Host "    username/repo-name              (GitHub shorthand)"
Write-Host "    https://github.com/user/repo    (full HTTPS URL)"
Write-Host "    git@github.com:user/repo.git    (SSH URL)"
Write-Host ""

$RepoInput = (Read-Host "  Repo").Trim()

if (-not $RepoInput) { Err "No repo entered."; exit 1 }

$UseSsh = $false
$UseGh  = $false
$GhPat  = ""

if ($RepoInput -match "^git@") {
    $CloneUrl   = $RepoInput
    $HttpsProbe = "https://" + ($RepoInput -replace "^git@([^:]+):(.+)\.git$", '$1/$2')
    $UseSsh     = $true
} elseif ($RepoInput -match "^https://") {
    $CloneUrl   = ($RepoInput -replace "\.git$") + ".git"
    $HttpsProbe = $RepoInput -replace "\.git$"
} elseif ($RepoInput -match "^[a-zA-Z0-9_.\-]+/[a-zA-Z0-9_.\-]+$") {
    $CloneUrl   = "https://github.com/$RepoInput.git"
    $HttpsProbe = "https://github.com/$RepoInput"
} else {
    Err "Could not parse: $RepoInput"; exit 1
}

Write-Host ""

# ── Visibility check ──────────────────────────────────────────────────────────

Write-Host "Checking repo visibility..." -ForegroundColor Cyan

$env:GIT_TERMINAL_PROMPT = "0"
$IsPublic = $false
try {
    git ls-remote --exit-code $CloneUrl HEAD 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { $IsPublic = $true }
} catch {}
$env:GIT_TERMINAL_PROMPT = $null

if ($IsPublic -and -not $UseSsh) {
    Write-Host ""
    Warn "Your repo is PUBLIC."
    Write-Host ""
    Write-Host "  Cortex records are personal and sensitive — your repo should be private." -ForegroundColor Yellow
    Write-Host "  Make it private at: $HttpsProbe/settings" -ForegroundColor Yellow
    Write-Host ""
    $openNow = Read-Host "  Press Enter to open your repo settings in the browser (n to skip)"
    if ($openNow -notmatch "^[Nn]") { Start-Process "$HttpsProbe/settings" }
    Write-Host ""
    $cont = Read-Host "  Continue with a public repo anyway? [y/N]"
    if ($cont -notmatch "^[Yy]") {
        Write-Host ""
        Write-Host "  Make it private, then re-run:"
        Write-Host "  iex (irm https://github.com/cordfuse/cortex/releases/latest/download/install.ps1)"
        Write-Host ""
        exit 0
    }
    Write-Host ""
} elseif (-not $IsPublic -and -not $UseSsh) {
    Ok "Repo is private."
    Write-Host ""
    $ghAuthed = $false
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        $ghStatus = gh auth status 2>&1
        if ($ghStatus -match "Logged in") { $ghAuthed = $true }
    }
    if ($ghAuthed) {
        Ok "GitHub CLI authenticated — will use gh for clone."
        $UseGh = $true
    } else {
        Warn "Private repo — authentication needed."
        Write-Host ""
        Write-Host "  Options:"
        Write-Host "    1) Personal Access Token (PAT)"
        Write-Host "       Generate at: https://github.com/settings/tokens/new"
        Write-Host "       Required scope: repo (read)"
        Write-Host "    2) SSH — re-run using git@github.com:user/repo.git format"
        Write-Host "    3) GitHub CLI — run: gh auth login, then re-run this installer"
        Write-Host ""
        $GhPat = Read-Host "  PAT (leave blank to try SSH fallback)"
        if (-not $GhPat) {
            $CloneUrl = "git@github.com:" + ($CloneUrl -replace "https://github.com/")
            Ok "Using SSH fallback."
        }
    }
    Write-Host ""
} else {
    Ok "SSH URL — skipping visibility probe."
    Write-Host ""
}

# ── Clone destination ─────────────────────────────────────────────────────────

$DefaultDest = "$env:USERPROFILE\cortex"
Write-Host "Clone destination" -ForegroundColor Cyan
$CloneDest = Read-Host "  Path [$DefaultDest]"
if (-not $CloneDest) { $CloneDest = $DefaultDest }
Write-Host ""

if (Test-Path "$CloneDest\.git") {
    Warn "A git repo already exists at $CloneDest."
    $reuse = Read-Host "  Skip clone and run setup only? [y/N]"
    if ($reuse -match "^[Yy]") {
        Write-Host ""
        $commitCount = [int](git -C $CloneDest rev-list --count HEAD 2>/dev/null)
        if ($commitCount -le 1) {
            Write-Host "  Fresh Cortex detected — running first-time setup." -ForegroundColor Cyan
        } else {
            Write-Host "  Existing Cortex detected ($commitCount commits) — repairing environment. Your records are untouched." -ForegroundColor Cyan
        }
        Write-Host ""
        Write-Host "Running setup..." -ForegroundColor Cyan
        & $Python "$CloneDest\scripts\setup.py" --system
        Write-Host ""
        Write-Host "Done." -ForegroundColor Green
        Write-Host "  Open $CloneDest in your AI agent and say hello."
        Write-Host ""
        exit 0
    } else {
        Err "Aborted. Choose a different path."; exit 1
    }
}

# ── Clone ─────────────────────────────────────────────────────────────────────

Write-Host "Cloning your Cortex..." -ForegroundColor Cyan

if ($UseGh) {
    gh repo clone $RepoInput $CloneDest
} elseif ($GhPat) {
    $AuthedUrl = $CloneUrl -replace "https://", "https://$GhPat@"
    git clone $AuthedUrl $CloneDest
    git -C $CloneDest remote set-url origin $CloneUrl
} else {
    git clone $CloneUrl $CloneDest
}

Ok "Cloned to $CloneDest"
Write-Host ""

# ── Fresh vs existing ─────────────────────────────────────────────────────────

$commitCount = [int](git -C $CloneDest rev-list --count HEAD 2>/dev/null)
if ($commitCount -le 1) {
    Write-Host "  Fresh Cortex — this is your first session." -ForegroundColor Cyan
} else {
    Write-Host "  Existing Cortex detected ($commitCount commits) — environment repair only. Your records are untouched." -ForegroundColor Cyan
}
Write-Host ""

# ── Setup ─────────────────────────────────────────────────────────────────────

Write-Host "Running setup..." -ForegroundColor Cyan
& $Python "$CloneDest\scripts\setup.py" --system

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host ""
Write-Host "  Open $CloneDest in your AI agent and say hello." -ForegroundColor White
Write-Host ""

# ── Post-install public repo reminder ─────────────────────────────────────────

if ($IsPublic) {
    Write-Host "  +-------------------------------------------------------------------+" -ForegroundColor Yellow
    Write-Host "  |  REMINDER: Your repo is still PUBLIC.                             |" -ForegroundColor Yellow
    Write-Host "  |  Your Cortex will store personal records. Make it private now.    |" -ForegroundColor Yellow
    Write-Host "  +-------------------------------------------------------------------+" -ForegroundColor Yellow
    Write-Host ""
    $openReminder = Read-Host "  Press Enter to open your repo settings in the browser (n to skip)"
    if ($openReminder -notmatch "^[Nn]") {
        Start-Process "$HttpsProbe/settings"
        Write-Host "  Settings -> Danger Zone -> Change visibility -> Make private" -ForegroundColor Yellow
    }
    Write-Host ""
}
