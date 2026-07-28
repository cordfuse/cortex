#!/usr/bin/env bun
/**
 * Cortex Tailscale integration — mesh network connector.
 *
 * Brings up Tailscale headlessly using an auth key stored in the Cortex vault.
 *
 * Setup:
 *   bun manifest/framework/scripts/integrations/tailscale.ts auth
 *
 * Usage:
 *   bun manifest/framework/scripts/integrations/tailscale.ts [--passphrase <p>] auth
 *   bun manifest/framework/scripts/integrations/tailscale.ts status
 *   bun manifest/framework/scripts/integrations/tailscale.ts [--passphrase <p>] up
 *   bun manifest/framework/scripts/integrations/tailscale.ts down
 *   bun manifest/framework/scripts/integrations/tailscale.ts ip <hostname>
 *   bun manifest/framework/scripts/integrations/tailscale.ts peers
 *
 * Requires: tailscale installed and in PATH
 */

import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { tmpdir } from 'node:os'
import { writeFileSync, unlinkSync } from 'node:fs'
import * as readline from 'node:readline'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '../../../..')
const VAULT_KEY = 'tailscale-auth-key'

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

async function promptLine(label: string): Promise<string> {
  if (!process.stdin.isTTY) {
    console.error(`ERROR: ${label} required but stdin is not a TTY.`)
    process.exit(1)
  }
  return new Promise(resolve => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
    rl.question(`${label}: `, answer => {
      rl.close()
      resolve(answer.trim())
    })
  })
}

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

// --- tailscale check ---

function requireTailscale(): void {
  const proc = Bun.spawnSync(['which', 'tailscale'], { stdout: 'pipe', stderr: 'pipe' })
  if (proc.exitCode !== 0) {
    console.error('ERROR: tailscale is not installed.')
    console.error('  Linux / ChromeOS: curl -fsSL https://tailscale.com/install.sh | sh')
    console.error('  macOS:            brew install tailscale')
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
    console.error('Run: bun manifest/framework/scripts/integrations/tailscale.ts auth')
    process.exit(1)
  }
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

// --- Auth ---

async function cmdAuth(passphrase: string): Promise<void> {
  console.log('Tailscale auth key setup')
  console.log('Generate a reusable auth key at: https://login.tailscale.com/admin/settings/keys')
  console.log('Settings: Reusable ON, Ephemeral OFF\n')

  const key = await promptLine('Paste auth key')
  if (!key.startsWith('tskey-')) {
    console.log("WARNING: key doesn't look like a Tailscale auth key (expected tskey-...)")
  }

  await storeSecret(VAULT_KEY, key, passphrase)
  console.log(`\nStored as '${VAULT_KEY}' in vault.`)
  console.log('Run: bun manifest/framework/scripts/integrations/tailscale.ts up')
}

// --- Status ---

function cmdStatus(): void {
  requireTailscale()
  const proc = Bun.spawnSync(['tailscale', 'status'], { stdout: 'pipe', stderr: 'pipe' })
  if (proc.exitCode !== 0) {
    console.log('Tailscale is not running or not connected.')
    console.log('Run: bun manifest/framework/scripts/integrations/tailscale.ts up')
    return
  }
  console.log(proc.stdout.toString())
}

// --- Up ---

async function cmdUp(passphrase: string): Promise<void> {
  requireTailscale()
  const authKey = await getSecret(VAULT_KEY, passphrase)

  // Passing the key as `--authkey <value>` exposes it in the tailscale
  // process's argv — readable via `ps` / /proc/<pid>/cmdline by any local
  // user for the life of the call. Hand it over through a mode-0600 temp file
  // and tailscale's `file:` form instead, and scrub the file even on interrupt.
  const keyPath = join(tmpdir(), `cortex_tsauth_${process.pid}_${Date.now()}.key`)
  const scrub = () => { try { unlinkSync(keyPath) } catch { /* already gone */ } }
  let scrubbing = false
  const onSignal = (sig: string) => {
    if (scrubbing) return
    scrubbing = true
    scrub()
    process.exit(sig === 'SIGTERM' ? 143 : 130)
  }
  process.on('SIGINT', () => onSignal('SIGINT'))
  process.on('SIGTERM', () => onSignal('SIGTERM'))

  writeFileSync(keyPath, authKey, { mode: 0o600 })
  console.log('Bringing Tailscale up...')
  try {
    const proc = Bun.spawnSync(['tailscale', 'up', '--authkey', `file:${keyPath}`], {
      stdout: 'pipe',
      stderr: 'pipe',
    })

    if (proc.exitCode === 0) {
      console.log('Tailscale is up.')
      cmdStatus()
    } else {
      console.error(`ERROR: ${proc.stderr.toString().trim()}`)
      process.exit(1)
    }
  } finally {
    scrub()
  }
}

// --- Down ---

function cmdDown(): void {
  requireTailscale()
  const proc = Bun.spawnSync(['tailscale', 'down'], { stdout: 'pipe', stderr: 'pipe' })
  if (proc.exitCode === 0) {
    console.log('Tailscale is down.')
  } else {
    console.error(`ERROR: ${proc.stderr.toString().trim()}`)
    process.exit(1)
  }
}

// --- IP ---

function cmdIp(hostname: string): void {
  requireTailscale()
  const proc = Bun.spawnSync(['tailscale', 'ip', hostname], { stdout: 'pipe', stderr: 'pipe' })
  if (proc.exitCode === 0) {
    const ip = proc.stdout.toString().trim()
    console.log(`${hostname}: ${ip}`)
    console.log('\nUse this IP in your rclone SFTP remote config:')
    console.log(`  host = ${ip}`)
  } else {
    console.error(`ERROR: ${proc.stderr.toString().trim()}`)
    console.error('Is Tailscale up? Run: bun manifest/framework/scripts/integrations/tailscale.ts up')
    process.exit(1)
  }
}

// --- Peers ---

function cmdPeers(): void {
  requireTailscale()
  const proc = Bun.spawnSync(['tailscale', 'status', '--json'], { stdout: 'pipe', stderr: 'pipe' })
  if (proc.exitCode !== 0) {
    console.error('Tailscale is not running. Run: bun manifest/framework/scripts/integrations/tailscale.ts up')
    process.exit(1)
  }

  let data: {
    Self?: { TailscaleIPs?: string[]; HostName?: string }
    Peer?: Record<string, { TailscaleIPs?: string[]; HostName?: string; Online?: boolean; OS?: string }>
  }
  try {
    data = JSON.parse(proc.stdout.toString())
  } catch {
    console.error('ERROR: Could not parse tailscale status output.')
    process.exit(1)
  }

  const peers = data.Peer ?? {}
  const selfNode = data.Self ?? {}

  console.log('# Tailnet peers\n')

  const selfIps = selfNode.TailscaleIPs ?? []
  const selfHost = selfNode.HostName ?? 'this device'
  const selfIp = selfIps[0] ?? 'unknown'
  console.log(`  ${selfIp}  ${selfHost}  (this device)`)

  for (const peer of Object.values(peers)) {
    const ips = peer.TailscaleIPs ?? []
    const ip = ips[0] ?? 'unknown'
    const hostname = peer.HostName ?? 'unknown'
    const online = peer.Online ? 'online' : 'offline'
    const osName = peer.OS ?? ''
    const osStr = osName ? ` [${osName}]` : ''
    console.log(`  ${ip}  ${hostname}${osStr}  (${online})`)
  }

  console.log('\nTo get IP for rclone: bun manifest/framework/scripts/integrations/tailscale.ts ip <hostname>')
}

// --- Main ---

async function main(): Promise<void> {
  const argv = process.argv.slice(2)
  if (argv.length === 0) {
    console.log('Usage: bun manifest/framework/scripts/integrations/tailscale.ts [--passphrase <p>] <subcommand>')
    console.log('Subcommands: auth, status, up, down, ip <hostname>, peers')
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

  // Commands that don't need the vault
  if (cmd === 'status') { cmdStatus(); return }
  if (cmd === 'down') { cmdDown(); return }
  if (cmd === 'peers') { cmdPeers(); return }
  if (cmd === 'ip') {
    const hostname = cmdArgs['_cmd'] as string ?? rest[1]
    if (!hostname) { console.error('ERROR: ip requires <hostname>'); process.exit(1) }
    cmdIp(hostname)
    return
  }

  // Commands that need the vault
  if (!passphrase) passphrase = await promptPassphrase()

  if (cmd === 'auth') {
    await cmdAuth(passphrase)
  } else if (cmd === 'up') {
    await cmdUp(passphrase)
  } else {
    console.error(`ERROR: Unknown subcommand '${cmd}'.`)
    process.exit(1)
  }
}

main().catch(err => {
  console.error(`ERROR: ${(err as Error).message}`)
  process.exit(1)
})
