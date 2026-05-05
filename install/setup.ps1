# Cortex bootstrap — Windows (PowerShell)
# Usage: .\setup.ps1
# Run once on first use, or re-run any time to repair the environment.
# Requires PowerShell 5.1+ (built into Windows 10/11).

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Cortex bootstrap"
Write-Host "----------------"

# ── Bun ──────────────────────────────────────────────────────────────────────

if (-not (Get-Command bun -ErrorAction SilentlyContinue)) {
    Write-Host ""
    Write-Host "Bun not found. Installing..."
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install -e --id Oven-sh.Bun --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                    [System.Environment]::GetEnvironmentVariable("Path", "User")
    } else {
        irm bun.sh/install.ps1 | iex
    }
}

Write-Host "Bun: $(bun --version)"

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

# ── Hand off to setup.ts --system ─────────────────────────────────────────────

Write-Host ""
& bun "$ScriptDir\manifest\framework\scripts\setup.ts" --system
