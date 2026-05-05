#!/usr/bin/env bun
/**
 * Cortex rclone integration — universal filesystem connector.
 *
 * The rclone config is stored encrypted in the Cortex vault. It is written
 * to a temp file per command and deleted immediately after — credentials
 * never persist on disk outside the vault.
 *
 * Setup:
 *   bun manifest/framework/scripts/integrations/rclone.ts auth
 *
 * Usage:
 *   bun manifest/framework/scripts/integrations/rclone.ts [--passphrase <p>] auth
 *   bun manifest/framework/scripts/integrations/rclone.ts [--passphrase <p>] remotes
 *   bun manifest/framework/scripts/integrations/rclone.ts [--passphrase <p>] ls <remote:path>
 *   bun manifest/framework/scripts/integrations/rclone.ts [--passphrase <p>] pull <remote:path> [--dest docs/]
 *   bun manifest/framework/scripts/integrations/rclone.ts [--passphrase <p>] push <remote:path> [--src docs/]
 *   bun manifest/framework/scripts/integrations/rclone.ts [--passphrase <p>] mount <remote:path> [--mountpoint <path>]
 *
 * Requires: rclone installed — https://rclone.org/install/
 */

import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { tmpdir, homedir } from 'node:os'
import { writeFileSync, unlinkSync, mkdirSync } from 'node:fs'
import * as readline from 'node:readline'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '../..')
const DOCS_DIR = join(ROOT, 'docs')

// --- Arg parser ---

function parseArgs(argv: string[]): Record<string, string | boolean | undefined> {
  const result: Record<string, string | boolean | undefined> = {}
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i]
    if (arg.startsWith('--')) {
      const key = arg.slice(2)
      const next = argv[i + 1]
      if (next && !next.startsWith('--')) {
        result[key] = next
        i++
      } else {
        result[key] = true
      }
    } else if (!result['_cmd']) {
      result['_cmd'] = arg
    } else if (!result['_pos1']) {
      result['_pos1'] = arg
    }
  }
  return result
}

// --- Interactive prompts ---

async function promptPassphrase(label = 'Vault passphrase'): Promise<string> {
  if (!process.stdin.isTTY) {
    console.error('ERROR: No passphrase provided and stdin is not a TTY. Use --passphrase.')
    process.exit(1)
  }
  return new Promise(resolve => {
    process.stderr.write(`${label}: `)
    let value = ''
    const tty = process.stdin as NodeJS.ReadStream & { setRawMode?: (mode: boolean) => void }
    if (tty.setRawMode) {
      process.stdin.setRawMode(true)
      process.stdin.resume()
      process.stdin.setEncoding('utf8')
      const onData = (ch: string) => {
        if (ch === '\r' || ch === '\n') {
          process.stdin.setRawMode!(false)
          process.stdin.pause()
          process.stdin.removeListener('data', onData)
          process.stderr.write('\n')
          resolve(value)
        } else if (ch === '') {
          process.exit(1)
        } else if (ch === '') {
          value = value.slice(0, -1)
        } else {
          value += ch
        }
      }
      process.stdin.on('data', onData)
    } else {
      const rl = readline.createInterface({ input: process.stdin, output: process.stderr })
      rl.question('', answer => { rl.close(); resolve(answer) })
    }
  })
}

// --- rclone check ---

function requireRclone(): void {
  const proc = Bun.spawnSync(['which', 'rclone'], { stdout: 'pipe', stderr: 'pipe' })
  if (proc.exitCode !== 0) {
    console.error('ERROR: rclone is not installed.')
    console.error('  macOS:   brew install rclone')
    console.error('  Linux:   sudo apt install rclone')
    console.error('  Windows: winget install Rclone.Rclone')
    console.error('  Or:      curl https://rclone.org/install.sh | sudo bash')
    process.exit(1)
  }
}

// --- Vault helpers ---

async function getSecret(name: string, passphrase: string): Promise<string> {
  const proc = Bun.spawn(
    ['bun', join(ROOT, 'manifest/framework/scripts/secrets.ts'), 'get', name, '--passphrase', passphrase],
    { stdout: 'pipe', stderr: 'pipe' }
  )
  const code = await proc.exited
  if (code !== 0) {
    console.error(`ERROR: Could not retrieve '${name}' from vault.`)
    console.error('Run: bun manifest/framework/scripts/integrations/rclone.ts auth')
    process.exit(1)
  }
  return (await new Response(proc.stdout).text()).trim()
}

async function tryGetSecret(name: string, passphrase: string): Promise<string | null> {
  const proc = Bun.spawn(
    ['bun', join(ROOT, 'manifest/framework/scripts/secrets.ts'), 'get', name, '--passphrase', passphrase],
    { stdout: 'pipe', stderr: 'pipe' }
  )
  const code = await proc.exited
  if (code !== 0) return null
  return (await new Response(proc.stdout).text()).trim()
}

async function storeSecret(name: string, value: string, passphrase: string): Promise<void> {
  const proc = Bun.spawn(
    ['bun', join(ROOT, 'manifest/framework/scripts/secrets.ts'), 'store', name, '--value', value, '--passphrase', passphrase],
    { stdout: 'inherit', stderr: 'inherit' }
  )
  const code = await proc.exited
  if (code !== 0) {
    console.error(`ERROR: Failed to store secret '${name}'.`)
    process.exit(1)
  }
}

// --- Config temp file ---

function writeTempConfig(configData: string): string {
  const tmpPath = join(tmpdir(), `cortex_rclone_${Date.now()}.conf`)
  writeFileSync(tmpPath, configData, { mode: 0o600 })
  return tmpPath
}

async function runRclone(args: string[], configPath: string): Promise<number> {
  const proc = Bun.spawn(['rclone', '--config', configPath, ...args], {
    stdout: 'inherit',
    stderr: 'inherit',
    stdin: 'inherit',
  })
  return proc.exited
}

// --- Auth ---

async function cmdAuth(passphrase: string): Promise<void> {
  requireRclone()

  const existing = await tryGetSecret('rclone_config', passphrase)
  if (existing) {
    console.log('Existing rclone config found in vault — adding to it.\n')
  } else {
    console.log('No existing rclone config in vault — starting fresh.\n')
  }

  const tmpPath = writeTempConfig(existing ?? '')
  try {
    console.log("Opening rclone config wizard. Add or edit remotes, then quit when done.")
    console.log("Type 'n' to add a new remote, 'q' to quit.\n")

    const proc = Bun.spawn(['rclone', '--config', tmpPath, 'config'], {
      stdout: 'inherit',
      stderr: 'inherit',
      stdin: 'inherit',
    })
    await proc.exited

    const newConfig = await Bun.file(tmpPath).text()
    await storeSecret('rclone_config', newConfig, passphrase)
    console.log('\nrclone config stored in vault.')
    console.log('Commit cortex.secrets/ to persist across devices.')
    console.log('\nRemotes configured:')
    const listProc = Bun.spawn(['rclone', '--config', tmpPath, 'listremotes'], {
      stdout: 'inherit',
      stderr: 'inherit',
    })
    await listProc.exited
  } finally {
    unlinkSync(tmpPath)
  }
}

// --- Remotes ---

async function cmdRemotes(passphrase: string): Promise<void> {
  requireRclone()
  const configData = await getSecret('rclone_config', passphrase)
  const tmpPath = writeTempConfig(configData)
  try {
    console.log('# Configured remotes\n')
    await runRclone(['listremotes'], tmpPath)
  } finally {
    unlinkSync(tmpPath)
  }
}

// --- ls ---

async function cmdLs(remotePath: string, passphrase: string): Promise<void> {
  requireRclone()
  const configData = await getSecret('rclone_config', passphrase)
  const tmpPath = writeTempConfig(configData)
  try {
    console.log(`# ${remotePath}\n`)
    await runRclone(['lsf', '--human-readable', remotePath], tmpPath)
  } finally {
    unlinkSync(tmpPath)
  }
}

// --- pull ---

async function cmdPull(remotePath: string, dest: string, passphrase: string): Promise<void> {
  requireRclone()
  mkdirSync(dest, { recursive: true })
  const configData = await getSecret('rclone_config', passphrase)
  const tmpPath = writeTempConfig(configData)
  try {
    console.log(`Pulling ${remotePath} → ${dest}`)
    const code = await runRclone(['copy', '--progress', remotePath, dest], tmpPath)
    if (code === 0) {
      console.log(`\nDone. Files are in ${dest}`)
      console.log("File this? Add them to docs/ and commit with: git add docs/ && git commit -m 'docs: pull from <remote>'")
    } else {
      console.error(`\nERROR: rclone exited with code ${code}`)
      process.exit(code)
    }
  } finally {
    unlinkSync(tmpPath)
  }
}

// --- push ---

async function cmdPush(remotePath: string, src: string, passphrase: string): Promise<void> {
  requireRclone()
  const configData = await getSecret('rclone_config', passphrase)
  const tmpPath = writeTempConfig(configData)
  try {
    console.log(`Pushing ${src} → ${remotePath}`)
    const code = await runRclone(['sync', '--progress', src, remotePath], tmpPath)
    if (code === 0) {
      console.log('\nDone.')
    } else {
      console.error(`\nERROR: rclone exited with code ${code}`)
      process.exit(code)
    }
  } finally {
    unlinkSync(tmpPath)
  }
}

// --- mount ---

async function cmdMount(remotePath: string, mountpoint: string, passphrase: string): Promise<void> {
  requireRclone()
  mkdirSync(mountpoint, { recursive: true })
  const configData = await getSecret('rclone_config', passphrase)
  const tmpPath = writeTempConfig(configData)
  console.log(`Mounting ${remotePath} at ${mountpoint}`)
  console.log('Press Ctrl+C to unmount.\n')
  try {
    const code = await runRclone(['mount', remotePath, mountpoint, '--vfs-cache-mode', 'writes'], tmpPath)
    if (code !== 0) {
      console.error(`\nERROR: rclone mount exited with code ${code}`)
    } else {
      console.log('\nUnmounted.')
    }
  } finally {
    try { unlinkSync(tmpPath) } catch { /* already gone */ }
  }
}

// --- Main ---

async function main(): Promise<void> {
  const argv = process.argv.slice(2)
  if (argv.length === 0) {
    console.log('Usage: bun manifest/framework/scripts/integrations/rclone.ts [--passphrase <p>] <subcommand> [options]')
    console.log('Subcommands: auth, remotes, ls, pull, push, mount')
    process.exit(1)
  }

  // Pull out top-level --passphrase before subcommand
  let passphrase: string | undefined
  const rest: string[] = []
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--passphrase' && argv[i + 1]) {
      passphrase = argv[i + 1]
      i++
    } else {
      rest.push(argv[i])
    }
  }

  const cmd = rest[0]
  const cmdArgs = parseArgs(rest.slice(1))

  if (!cmd) {
    console.error('ERROR: No subcommand provided.')
    process.exit(1)
  }

  if (!passphrase) passphrase = await promptPassphrase()

  if (cmd === 'auth') {
    await cmdAuth(passphrase)
  } else if (cmd === 'remotes') {
    await cmdRemotes(passphrase)
  } else if (cmd === 'ls') {
    const remotePath = cmdArgs['_cmd'] as string
    if (!remotePath) { console.error('ERROR: ls requires <remote:path>'); process.exit(1) }
    await cmdLs(remotePath, passphrase)
  } else if (cmd === 'pull') {
    const remotePath = cmdArgs['_cmd'] as string
    if (!remotePath) { console.error('ERROR: pull requires <remote:path>'); process.exit(1) }
    await cmdPull(remotePath, (cmdArgs['dest'] as string) ?? DOCS_DIR, passphrase)
  } else if (cmd === 'push') {
    const remotePath = cmdArgs['_cmd'] as string
    if (!remotePath) { console.error('ERROR: push requires <remote:path>'); process.exit(1) }
    await cmdPush(remotePath, (cmdArgs['src'] as string) ?? DOCS_DIR, passphrase)
  } else if (cmd === 'mount') {
    const remotePath = cmdArgs['_cmd'] as string
    if (!remotePath) { console.error('ERROR: mount requires <remote:path>'); process.exit(1) }
    const defaultMountpoint = join(homedir(), 'mnt', 'cortex-remote')
    await cmdMount(remotePath, (cmdArgs['mountpoint'] as string) ?? defaultMountpoint, passphrase)
  } else {
    console.error(`ERROR: Unknown subcommand '${cmd}'.`)
    process.exit(1)
  }
}

main().catch(err => {
  console.error(`ERROR: ${(err as Error).message}`)
  process.exit(1)
})
