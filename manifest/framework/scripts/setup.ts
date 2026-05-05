#!/usr/bin/env bun
/**
 * Cortex setup script.
 * Detects environment, writes cortex.config, creates .gitignore, verifies repo structure.
 *
 * Usage:
 *   bun manifest/framework/scripts/setup.ts              # environment check only
 *   bun manifest/framework/scripts/setup.ts --system     # also install system dependencies (may use sudo)
 *
 * Run once on first use, or re-run any time to repair the environment.
 */

import { existsSync, readFileSync, writeFileSync, appendFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { platform } from 'node:os'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const CONFIG_PATH = join(ROOT, 'cortex.config')
const GITIGNORE_PATH = join(ROOT, '.gitignore')

const REQUIRED_FILES = [
  'manifest/framework/protocol/CORTEX.md',
  'manifest/framework/protocol/GUARDRAILS.md',
  'manifest/framework/protocol/DISCLAIMER.md',
  'manifest/framework/protocol/ROE.md',
]

const GITIGNORE_ENTRIES = ['cortex.config', '.env', 'cortex.secrets.enc']

// --- OS / package manager detection ---

function detectPkgManager(): string | null {
  const os = platform()
  if (os === 'darwin') return 'brew'
  if (os === 'win32') return 'winget'
  // Linux — check /etc/os-release
  try {
    const content = readFileSync('/etc/os-release', 'utf8')
    for (const line of content.split('\n')) {
      if (line.startsWith('ID=')) {
        const distro = line.split('=')[1].trim().replace(/"/g, '').toLowerCase()
        if (['arch', 'cachyos', 'manjaro', 'endeavouros'].includes(distro)) return 'pacman'
        if (['ubuntu', 'debian', 'linuxmint', 'pop'].includes(distro)) return 'apt'
        if (['fedora', 'rhel', 'centos'].includes(distro)) return 'dnf'
      }
    }
  } catch {
    // ignore
  }
  return null
}

function which(cmd: string): string | null {
  try {
    const proc = Bun.spawnSync(['which', cmd], { stdout: 'pipe', stderr: 'pipe' })
    if (proc.exitCode === 0) {
      return proc.stdout.toString().trim() || null
    }
  } catch {
    // ignore
  }
  return null
}

function sudo(cmd: string[]): number {
  console.log(`  [sudo] ${cmd.join(' ')}`)
  const proc = Bun.spawnSync(['sudo', ...cmd], { stdout: 'inherit', stderr: 'inherit', stdin: 'inherit' })
  return proc.exitCode ?? 1
}

function run(cmd: string[]): number {
  const proc = Bun.spawnSync(cmd, { stdout: 'inherit', stderr: 'inherit', stdin: 'inherit' })
  return proc.exitCode ?? 1
}

// --- Dependency installers ---

function ensureRclone(pkg: string | null): boolean {
  if (which('rclone')) return true
  console.log('  rclone: not installed — installing...')
  if (pkg === 'pacman') return sudo(['pacman', '-S', '--noconfirm', 'rclone']) === 0
  if (pkg === 'apt') return sudo(['apt-get', 'install', '-y', 'rclone']) === 0
  if (pkg === 'dnf') return sudo(['dnf', 'install', '-y', 'rclone']) === 0
  if (pkg === 'brew') return run(['brew', 'install', 'rclone']) === 0
  if (pkg === 'winget') return run(['winget', 'install', '-e', '--id', 'Rclone.Rclone', '--silent']) === 0
  console.log('  rclone: cannot auto-install — see https://rclone.org/install/')
  return false
}

function ensureTailscale(pkg: string | null): boolean {
  if (!which('tailscale')) {
    console.log('  tailscale: not installed — installing...')
    let ok = false
    if (pkg === 'pacman') ok = sudo(['pacman', '-S', '--noconfirm', 'tailscale']) === 0
    else if (pkg === 'apt') ok = run(['sh', '-c', 'curl -fsSL https://tailscale.com/install.sh | sh']) === 0
    else if (pkg === 'dnf') ok = run(['sh', '-c', 'curl -fsSL https://tailscale.com/install.sh | sh']) === 0
    else if (pkg === 'brew') ok = run(['brew', 'install', 'tailscale']) === 0
    else if (pkg === 'winget') ok = run(['winget', 'install', '-e', '--id', 'tailscale.tailscale', '--silent']) === 0
    else {
      console.log('  tailscale: cannot auto-install — see https://tailscale.com/download')
      return false
    }
    if (!ok) return false
  }

  // Set operator so tailscale runs without sudo
  const os = platform()
  if (os !== 'darwin' && os !== 'win32' && which('tailscale')) {
    const user = process.env.USER || process.env.USERNAME || ''
    if (user) {
      const proc = Bun.spawnSync(['tailscale', 'debug', 'prefs'], { stdout: 'pipe', stderr: 'pipe' })
      const out = proc.stdout.toString()
      if (!out.includes('OperatorUser') || !out.includes(user)) {
        console.log(`  tailscale: setting operator=${user} (allows non-root use)...`)
        sudo(['tailscale', 'set', `--operator=${user}`])
      }
    }
  }
  return true
}

function installSystemDeps(): void {
  const pkg = detectPkgManager()
  if (!pkg) console.log('WARNING: Could not detect package manager. Some deps may need manual install.')
  console.log('\nSystem dependencies:')

  const rcloneOk = ensureRclone(pkg)
  console.log(`  rclone: ${rcloneOk ? 'OK' : 'FAILED — install manually: https://rclone.org/install/'}`)

  const tailscaleOk = ensureTailscale(pkg)
  console.log(`  tailscale: ${tailscaleOk ? 'OK' : 'FAILED — install manually: https://tailscale.com/download'}`)
}

// --- Core setup ---

interface EnvConfig {
  bun: string | null
  git: string | null
  shell: string
  ollama: string | null
  rclone: string | null
  tailscale: string | null
}

function detectEnvironment(): EnvConfig {
  const os = platform()
  return {
    bun: which('bun'),
    git: which('git'),
    shell: os === 'win32' ? 'powershell' : (which('bash') ? 'bash' : 'sh'),
    ollama: which('ollama'),
    rclone: which('rclone'),
    tailscale: which('tailscale'),
  }
}

function checkRequiredFiles(): string[] {
  return REQUIRED_FILES.filter(f => !existsSync(join(ROOT, f)))
}

function ensureGitignore(): string[] {
  let existing: string[] = []
  if (existsSync(GITIGNORE_PATH)) {
    existing = readFileSync(GITIGNORE_PATH, 'utf8').split('\n')
  }
  const added: string[] = []
  for (const entry of GITIGNORE_ENTRIES) {
    if (!existing.includes(entry)) {
      appendFileSync(GITIGNORE_PATH, `${entry}\n`)
      added.push(entry)
    }
  }
  return added
}

function writeConfig(env: EnvConfig): void {
  writeFileSync(CONFIG_PATH, JSON.stringify(env, null, 2) + '\n')
}

function setupGit(): void {
  const proc = Bun.spawnSync(['git', 'rev-parse', '--is-inside-work-tree'], {
    cwd: ROOT,
    stdout: 'pipe',
    stderr: 'pipe',
  })
  if (proc.exitCode !== 0) {
    console.log('\nWARNING: Not a git repo.')
    console.log('Run: git init && git remote add origin <your-private-repo-url>')
    return
  }

  console.log('git repo: OK')
  const remotesProc = Bun.spawnSync(['git', 'remote'], { cwd: ROOT, stdout: 'pipe', stderr: 'pipe' })
  const remotes = remotesProc.stdout.toString().split('\n')
  if (!remotes.includes('upstream')) {
    Bun.spawnSync(
      ['git', 'remote', 'add', 'upstream', 'https://github.com/cordfuse/cortex.git'],
      { cwd: ROOT, stdout: 'pipe', stderr: 'pipe' }
    )
    console.log('upstream remote: added (https://github.com/cordfuse/cortex.git)')
  } else {
    console.log('upstream remote: OK')
  }
}

// --- Main ---

function main(): void {
  const args = process.argv.slice(2)
  const installSystem = args.includes('--system')

  console.log('Cortex setup')
  console.log('------------')

  // Protocol files
  const missing = checkRequiredFiles()
  if (missing.length > 0) {
    console.error(`ERROR: Required protocol files missing: ${missing.join(', ')}`)
    console.error('Your Cortex repo is incomplete. Re-clone from the template.')
    process.exit(1)
  }
  console.log('Protocol files: OK')

  // Environment
  const env = detectEnvironment()
  console.log('\nEnvironment:')
  console.log(`  Shell:      ${env.shell}`)
  console.log(`  Bun:        ${env.bun ?? 'not found'}`)
  console.log(`  Git:        ${env.git ?? 'not found'}`)
  console.log(`  Ollama:     ${env.ollama ?? 'not found'}`)
  console.log(`  rclone:     ${env.rclone ?? 'not found'}`)
  console.log(`  tailscale:  ${env.tailscale ?? 'not found'}`)

  if (!env.git) {
    console.error('\nERROR: git is required.')
    process.exit(1)
  }

  // System deps
  if (installSystem) {
    installSystemDeps()
  }

  // Config + gitignore
  writeConfig(env)
  console.log('\ncortex.config: written (gitignored)')

  const added = ensureGitignore()
  if (added.length > 0) {
    console.log(`.gitignore: updated (${added.join(', ')})`)
  } else {
    console.log('.gitignore: OK')
  }

  // Git + upstream
  setupGit()

  console.log('\nSetup complete. Open this directory in your AI agent and say hello.')
}

main()
