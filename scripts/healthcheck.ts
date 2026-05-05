#!/usr/bin/env bun
/**
 * Cortex healthcheck script.
 * Verifies all required protocol files exist and are non-empty.
 * Called by the scribe at session start.
 * Run manually: bun scripts/healthcheck.ts
 */

import { existsSync, statSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')

const REQUIRED: Record<string, string> = {
  'manifest/framework/protocol/CORTEX.md': 'Protocol engine',
  'manifest/framework/protocol/GUARDRAILS.md': 'Safety guardrails',
  'manifest/framework/protocol/DISCLAIMER.md': 'Disclaimer and legal warnings',
  'manifest/framework/protocol/ROE.md': 'Rules of engagement',
}

const errors: string[] = []

for (const [filename, description] of Object.entries(REQUIRED)) {
  const path = join(ROOT, filename)

  if (!existsSync(path)) {
    errors.push(`MISSING: ${filename} — ${description}`)
    continue
  }

  if (statSync(path).size === 0) {
    errors.push(`EMPTY: ${filename} — ${description}`)
    continue
  }
}

if (errors.length > 0) {
  console.log('Cortex healthcheck FAILED\n')
  for (const e of errors) {
    console.log(`  ${e}`)
  }
  console.log()

  if (errors.some(e => e.includes('manifest/framework/protocol/GUARDRAILS.md'))) {
    console.log('WARNING: GUARDRAILS.md is missing or empty.')
    console.log('Cortex has no safety guardrails. Cordfuse accepts zero liability for any consequences.')
    console.log('Do not proceed without restoring this file.')
  }

  process.exit(1)
}

console.log('Cortex healthcheck OK')
for (const filename of Object.keys(REQUIRED)) {
  console.log(`  ${filename}: OK`)
}

process.exit(0)
