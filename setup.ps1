# Cortex bootstrap — Windows (PowerShell)
# Usage: .\setup.ps1
# Run once on first use, or re-run any time to repair the environment.
# Requires PowerShell 5.1+ (built into Windows 10/11).

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Cortex bootstrap"
Write-Host "----------------"

# ── Python ────────────────────────────────────────────────────────────────────

$Python = $null
foreach ($cmd in @("python3", "python")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $Python = $cmd
        break
    }
}

if (-not $Python) {
    Write-Host ""
    Write-Host "Python not found. Installing via winget..."
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install -e --id Python.Python.3 --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                    [System.Environment]::GetEnvironmentVariable("Path", "User")
        $Python = "python"
    } else {
        Write-Host "ERROR: winget not available."
        Write-Host "Install Python 3.9+ from https://python.org/downloads"
        Write-Host "Enable 'Add Python to PATH' during install, then re-run this script."
        exit 1
    }
}

$PyVersion = & $Python --version 2>&1
Write-Host "Python: $Python ($PyVersion)"

# ── Git ───────────────────────────────────────────────────────────────────────

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host ""
    Write-Host "git not found. Installing via winget..."
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install -e --id Git.Git --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                    [System.Environment]::GetEnvironmentVariable("Path", "User")
    } else {
        Write-Host "ERROR: winget not available."
        Write-Host "Install Git from https://git-scm.com/download/win, then re-run this script."
        exit 1
    }
}

Write-Host "git: $(git --version)"

# ── Hand off to setup.py --system ─────────────────────────────────────────────

Write-Host ""
& $Python "$ScriptDir\scripts\setup.py" --system
