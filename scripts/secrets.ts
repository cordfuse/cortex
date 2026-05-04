#!/usr/bin/env bun
/**
 * Cortex secrets vault — v2 per-file format with v1 legacy read support.
 *
 * Write: always per-file (cortex.secrets/<n>.enc)
 * Read:  per-file first, falls back to legacy blob (cortex.secrets.enc)
 * List:  union of both — per-file takes precedence on duplicate keys
 *
 * Binary format (must match Python implementation exactly):
 *   base64( salt[16] + nonce[12] + ciphertext_with_gcm_tag[*] )
 *   PBKDF2-SHA256, 600,000 iterations, 32-byte key
 *   AES-256-GCM — GCM tag (16 bytes) appended to ciphertext
 *
 * Run: bun scripts/secrets.ts <command> [options]
 */

import {
  pbkdf2Sync,
  createCipheriv,
  createDecipheriv,
  randomBytes,
} from 'node:crypto'
import { existsSync, readdirSync, mkdirSync, readFileSync, writeFileSync, unlinkSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import * as readline from 'node:readline'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const VAULT_DIR = join(ROOT, 'cortex.secrets')
const MANIFEST_PATH = join(VAULT_DIR, 'vault.json')
const LEGACY_VAULT = join(ROOT, 'cortex.secrets.enc')

const PBKDF2_ITERATIONS = 600_000
const SALT_LEN = 16
const NONCE_LEN = 12
const KEY_LEN = 32
const TAG_LEN = 16

// --- Crypto primitives ---

function deriveKey(passphrase: string, salt: Buffer): Buffer {
  return pbkdf2Sync(passphrase, salt, PBKDF2_ITERATIONS, KEY_LEN, 'sha256')
}

function encryptValue(value: string, passphrase: string): Buffer {
  const salt = randomBytes(SALT_LEN)
  const nonce = randomBytes(NONCE_LEN)
  const key = deriveKey(passphrase, salt)
  const payload = Buffer.from(JSON.stringify({
    value,
    updated_at: new Date().toISOString(),
  }))
  const cipher = createCipheriv('aes-256-gcm', key, nonce)
  const encrypted = Buffer.concat([cipher.update(payload), cipher.final()])
  const tag = cipher.getAuthTag()
  // Format: salt + nonce + ciphertext + tag (tag appended, matching Python AESGCM output)
  const raw = Buffer.concat([salt, nonce, encrypted, tag])
  return Buffer.from(raw.toString('base64'))
}

function rawDecrypt(data: Buffer, passphrase: string, label: string = 'file'): Buffer {
  const raw = Buffer.from(data.toString().trim(), 'base64')
  const salt = raw.subarray(0, SALT_LEN)
  const nonce = raw.subarray(SALT_LEN, SALT_LEN + NONCE_LEN)
  // ciphertext includes the GCM tag appended at the end
  const ciphertextWithTag = raw.subarray(SALT_LEN + NONCE_LEN)
  const ciphertext = ciphertextWithTag.subarray(0, ciphertextWithTag.length - TAG_LEN)
  const tag = ciphertextWithTag.subarray(ciphertextWithTag.length - TAG_LEN)
  const key = deriveKey(passphrase, salt)
  try {
    const decipher = createDecipheriv('aes-256-gcm', key, nonce)
    decipher.setAuthTag(tag)
    return Buffer.concat([decipher.update(ciphertext), decipher.final()])
  } catch {
    console.error(`ERROR: Wrong passphrase or ${label} is corrupt.`)
    process.exit(1)
  }
}

// --- Per-file (v2) ---

function secretPath(name: string): string {
  const safe = name.replace(/[/\\]/g, '_')
  return join(VAULT_DIR, `${safe}.enc`)
}

function ensureVaultDir(): void {
  mkdirSync(VAULT_DIR, { recursive: true })
}

function nowIso(): string {
  return new Date().toISOString()
}

interface Manifest {
  version: number
  created_at: string
  passphrase_rotated_at: string | null
  secrets: Record<string, string>
}

function readManifest(): Manifest {
  if (existsSync(MANIFEST_PATH)) {
    const raw = JSON.parse(readFileSync(MANIFEST_PATH, 'utf8'))
    // Migrate old list format to dict
    if (Array.isArray(raw.secrets)) {
      raw.secrets = Object.fromEntries((raw.secrets as string[]).map(k => [k, '']))
    }
    return raw as Manifest
  }
  return { version: 2, created_at: nowIso(), passphrase_rotated_at: null, secrets: {} }
}

function writeManifest(opts: { passphraseRotated?: boolean; name?: string; description?: string } = {}): void {
  const existing = readManifest()
  const names = perfileNames()
  const secrets: Record<string, string> = {}
  for (const k of names) {
    secrets[k] = existing.secrets[k] ?? ''
  }
  if (opts.name !== undefined && opts.description !== undefined) {
    secrets[opts.name] = opts.description
  }
  const manifest: Manifest = {
    version: 2,
    created_at: existing.created_at,
    passphrase_rotated_at: opts.passphraseRotated ? nowIso() : existing.passphrase_rotated_at,
    secrets,
  }
  writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2) + '\n')
}

function perfileNames(): string[] {
  if (!existsSync(VAULT_DIR)) return []
  return readdirSync(VAULT_DIR)
    .filter(f => f.endsWith('.enc') && f !== 'vault.json')
    .map(f => f.slice(0, -4))
    .sort()
}

function perfileGet(name: string, passphrase: string): string {
  const path = secretPath(name)
  const data = readFileSync(path)
  const plaintext = rawDecrypt(data, passphrase, `cortex.secrets/${name}.enc`)
  return JSON.parse(plaintext.toString()).value as string
}

function perfileDelete(name: string, passphrase: string): void {
  const path = secretPath(name)
  perfileGet(name, passphrase) // verify passphrase before deleting
  unlinkSync(path)
}

// --- Legacy v1 single-blob support (DEPRECATED) ---

function legacyRead(passphrase: string): Record<string, string> {
  if (!existsSync(LEGACY_VAULT)) return {}
  const data = readFileSync(LEGACY_VAULT)
  const plaintext = rawDecrypt(data, passphrase, 'legacy vault')
  return JSON.parse(plaintext.toString()) as Record<string, string>
}

function legacyDelete(name: string, passphrase: string): boolean {
  const legacy = legacyRead(passphrase)
  if (!(name in legacy)) return false
  delete legacy[name]
  const salt = randomBytes(SALT_LEN)
  const nonce = randomBytes(NONCE_LEN)
  const key = deriveKey(passphrase, salt)
  const payload = Buffer.from(JSON.stringify(legacy))
  const cipher = createCipheriv('aes-256-gcm', key, nonce)
  const encrypted = Buffer.concat([cipher.update(payload), cipher.final()])
  const tag = cipher.getAuthTag()
  const raw = Buffer.concat([salt, nonce, encrypted, tag])
  writeFileSync(LEGACY_VAULT, Buffer.from(raw.toString('base64')))
  return true
}

// --- Unified read layer ---

function unifiedList(passphrase?: string): string[] {
  const pf = new Set(perfileNames())
  let legacy: Record<string, string> = {}
  if (existsSync(LEGACY_VAULT)) {
    if (!passphrase) {
      if (pf.size > 0) {
        console.log('Note: legacy vault also present — provide --passphrase to include its keys.')
      }
    } else {
      legacy = legacyRead(passphrase)
    }
  }
  const all = new Set([...pf, ...Object.keys(legacy)])
  return [...all].sort()
}

function unifiedGet(name: string, passphrase: string): string {
  const path = secretPath(name)
  if (existsSync(path)) return perfileGet(name, passphrase)
  if (existsSync(LEGACY_VAULT)) {
    const legacy = legacyRead(passphrase)
    if (name in legacy) return legacy[name]
  }
  console.error(`ERROR: No secret named '${name}'.`)
  process.exit(1)
}

function unifiedDelete(name: string, passphrase: string): void {
  const path = secretPath(name)
  if (existsSync(path)) {
    perfileDelete(name, passphrase)
    return
  }
  if (existsSync(LEGACY_VAULT)) {
    if (legacyDelete(name, passphrase)) return
  }
  console.error(`ERROR: No secret named '${name}'.`)
  process.exit(1)
}

// --- Interactive prompts ---

async function promptSecret(label: string, confirmLabel?: string): Promise<string> {
  if (!process.stdin.isTTY) {
    console.error('ERROR: No passphrase provided and stdin is not a TTY. Use --passphrase.')
    process.exit(1)
  }
  const rl = readline.createInterface({ input: process.stdin, output: process.stderr })
  // Hide input for passphrase-like prompts
  const hideInput = (prompt: string): Promise<string> => new Promise(resolve => {
    process.stderr.write(prompt)
    const stdin = process.openStdin()
    const tty = process.stdin as NodeJS.ReadStream & { setRawMode?: (mode: boolean) => void }
    if (tty.setRawMode) {
      let value = ''
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
        } else if (ch === '') {
          process.exit(1)
        } else if (ch === '') {
          value = value.slice(0, -1)
        } else {
          value += ch
        }
      }
      process.stdin.on('data', onData)
    } else {
      rl.question(prompt, (answer) => {
        rl.close()
        resolve(answer)
      })
    }
  })

  const value = await hideInput(`${label}: `)
  if (confirmLabel) {
    const confirm = await hideInput(`${confirmLabel}: `)
    if (value !== confirm) {
      console.error('ERROR: Values do not match.')
      process.exit(1)
    }
  }
  rl.close()
  return value
}

async function promptLine(label: string): Promise<string> {
  if (!process.stdin.isTTY) {
    console.error('ERROR: No value provided and stdin is not a TTY.')
    process.exit(1)
  }
  return new Promise(resolve => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
    rl.question(`${label}: `, answer => {
      rl.close()
      resolve(answer)
    })
  })
}

// --- CLI commands ---

async function cmdStore(name: string, value?: string, passphrase?: string, description?: string): Promise<void> {
  if (!value) {
    value = await promptSecret(`Value for '${name}'`)
  }
  if (!value) {
    console.error('ERROR: Value cannot be empty.')
    process.exit(1)
  }
  if (!passphrase) {
    const existing = unifiedList()
    if (existing.length > 0) {
      passphrase = await promptSecret('Vault passphrase')
    } else {
      console.log('No vault found — creating a new one.')
      passphrase = await promptSecret('Choose a passphrase', 'Confirm passphrase')
    }
  }
  ensureVaultDir()
  const path = secretPath(name)
  const blob = encryptValue(value, passphrase)
  writeFileSync(path, blob)
  writeManifest({ name, description: description ?? '' })
  console.log(`Stored '${name}' -> cortex.secrets/${name}.enc`)
  console.log('Commit and push to persist across devices.')
}

async function cmdGet(name: string, passphrase?: string): Promise<void> {
  if (!passphrase) passphrase = await promptSecret('Vault passphrase')
  console.log(unifiedGet(name, passphrase))
}

async function cmdList(passphrase?: string): Promise<void> {
  const names = unifiedList(passphrase)
  if (names.length === 0) {
    console.log('No secrets stored.')
    return
  }
  const manifest = readManifest()
  const descriptions = manifest.secrets
  console.log('Stored secrets:')
  for (const n of names) {
    const desc = descriptions[n] ?? ''
    console.log(`  ${n}${desc ? `  — ${desc}` : ''}`)
  }
}

async function cmdDelete(name: string, passphrase?: string, force = false): Promise<void> {
  if (!passphrase) passphrase = await promptSecret('Vault passphrase')
  if (!force) {
    const confirm = await promptLine(`WARNING: Delete '${name}'? This cannot be undone. Type the secret name to confirm`)
    if (confirm !== name) {
      console.log('Aborted.')
      process.exit(0)
    }
  }
  unifiedDelete(name, passphrase)
  writeManifest()
  console.log(`Deleted '${name}'.`)
}

async function cmdRepassphrase(oldPassphrase?: string, newPassphrase?: string): Promise<void> {
  const names = perfileNames()
  if (names.length === 0) {
    console.log('No secrets in vault.')
    return
  }
  if (!oldPassphrase) oldPassphrase = await promptSecret('Current passphrase')
  const values: Record<string, string> = {}
  for (const name of names) {
    try {
      values[name] = perfileGet(name, oldPassphrase)
    } catch {
      console.error(`ERROR: Could not decrypt '${name}' — aborting. No changes made.`)
      process.exit(1)
    }
  }
  if (!newPassphrase) newPassphrase = await promptSecret('New passphrase', 'Confirm new passphrase')
  ensureVaultDir()
  for (const [name, value] of Object.entries(values)) {
    const path = secretPath(name)
    const blob = encryptValue(value, newPassphrase)
    writeFileSync(path, blob)
    console.log(`  Re-encrypted '${name}'`)
  }
  writeManifest({ passphraseRotated: true })
  console.log(`\nAll ${names.length} secret(s) re-encrypted with new passphrase.`)
  console.log('Commit and push to persist across devices.')
}

async function cmdMigrate(passphrase?: string): Promise<void> {
  if (!existsSync(LEGACY_VAULT)) {
    console.log('No legacy vault found. Nothing to migrate.')
    return
  }
  if (!passphrase) passphrase = await promptSecret('Vault passphrase')
  const legacy = legacyRead(passphrase)
  if (Object.keys(legacy).length === 0) {
    console.log('Legacy vault is empty. Nothing to migrate.')
    return
  }
  ensureVaultDir()
  for (const [name, value] of Object.entries(legacy)) {
    const path = secretPath(name)
    const blob = encryptValue(value, passphrase)
    writeFileSync(path, blob)
    console.log(`  Migrated '${name}' -> cortex.secrets/${name}.enc`)
  }
  console.log(`\nMigrated ${Object.keys(legacy).length} secret(s).`)
  console.log('Next steps:')
  console.log('  1. git add cortex.secrets/')
  console.log('  2. git rm cortex.secrets.enc')
  console.log("  3. git commit -m 'vault: migrate to per-file format (v2)'")
  console.log('  4. git push')
  console.log('\ncortex.secrets.enc remains in git history (encrypted, safe).')
}

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

// --- Main ---

async function main(): Promise<void> {
  const argv = process.argv.slice(2)
  if (argv.length === 0) {
    console.log('Usage: bun scripts/secrets.ts <command> [options]')
    console.log('Commands: store, get, list, delete, repassphrase, migrate')
    process.exit(1)
  }

  const cmd = argv[0]
  const args = parseArgs(argv.slice(1))

  const passphrase = args['passphrase'] as string | undefined

  if (cmd === 'store') {
    const name = args['_cmd'] as string
    if (!name) { console.error('ERROR: Missing secret name.'); process.exit(1) }
    await cmdStore(name, args['value'] as string | undefined, passphrase, args['description'] as string | undefined)
  } else if (cmd === 'get') {
    const name = args['_cmd'] as string
    if (!name) { console.error('ERROR: Missing secret name.'); process.exit(1) }
    await cmdGet(name, passphrase)
  } else if (cmd === 'list') {
    await cmdList(passphrase)
  } else if (cmd === 'delete') {
    const name = args['_cmd'] as string
    if (!name) { console.error('ERROR: Missing secret name.'); process.exit(1) }
    await cmdDelete(name, passphrase, args['force'] === true)
  } else if (cmd === 'repassphrase') {
    await cmdRepassphrase(
      args['old-passphrase'] as string | undefined,
      args['new-passphrase'] as string | undefined,
    )
  } else if (cmd === 'migrate') {
    await cmdMigrate(passphrase)
  } else {
    console.error(`ERROR: Unknown command '${cmd}'.`)
    console.log('Commands: store, get, list, delete, repassphrase, migrate')
    process.exit(1)
  }
}

main().catch(err => {
  console.error(`ERROR: ${err.message}`)
  process.exit(1)
})
