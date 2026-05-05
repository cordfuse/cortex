#!/usr/bin/env bun
/**
 * Cortex make-private script.
 * Flips your Cortex repo from public to private using a stored GitHub PAT.
 *
 * Prerequisites:
 *   bun manifest/framework/scripts/secrets.ts store github-pat
 *
 * Run:
 *   bun manifest/framework/scripts/make_private.ts [--passphrase <p>]
 *
 * The PAT needs the 'repo' scope on GitHub.
 */

import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import * as readline from 'node:readline'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')

function parseArgs(argv: string[]): Record<string, string | undefined> {
  const result: Record<string, string | undefined> = {}
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i]
    if (arg.startsWith('--')) {
      const key = arg.slice(2)
      const next = argv[i + 1]
      if (next && !next.startsWith('--')) {
        result[key] = next
        i++
      }
    }
  }
  return result
}

async function getRemoteUrl(): Promise<string> {
  const proc = Bun.spawn(['git', 'remote', 'get-url', 'origin'], {
    cwd: ROOT,
    stdout: 'pipe',
    stderr: 'pipe',
  })
  const code = await proc.exited
  if (code !== 0) {
    console.error('ERROR: Could not read git remote. Is this a git repo with an origin?')
    process.exit(1)
  }
  return (await new Response(proc.stdout).text()).trim()
}

function parseOwnerRepo(remoteUrl: string): [string, string] {
  let path: string
  if (remoteUrl.startsWith('git@')) {
    // SSH: git@github.com:owner/repo.git or git@alias:owner/repo.git
    path = remoteUrl.split(':').slice(1).join(':')
  } else if (remoteUrl.includes('github.com/')) {
    path = remoteUrl.split('github.com/')[1]
  } else {
    console.error(`ERROR: Only GitHub remotes are supported. Got: ${remoteUrl}`)
    process.exit(1)
  }
  path = path.replace(/\.git$/, '')
  const parts = path.split('/')
  if (parts.length !== 2) {
    console.error(`ERROR: Could not parse owner/repo from: ${remoteUrl}`)
    process.exit(1)
  }
  return [parts[0], parts[1]]
}

function printManualInstructions(owner: string, repo: string): void {
  console.log()
  console.log('Cannot reach the GitHub API from this environment.')
  console.log('Expected on Claude mobile and other sandboxed agents — only git is permitted.')
  console.log()
  console.log(`Flip ${owner}/${repo} private manually:`)
  console.log(`  1. Open https://github.com/${owner}/${repo}/settings`)
  console.log('  2. Scroll to the Danger Zone at the bottom')
  console.log('  3. Change repository visibility → Make private')
  console.log('  4. Confirm by typing the repo name')
  console.log()
}

async function githubApiReachable(): Promise<boolean> {
  try {
    const resp = await fetch('https://api.github.com', { method: 'HEAD', signal: AbortSignal.timeout(5000) })
    return resp.ok || resp.status < 500
  } catch {
    return false
  }
}

async function promptPassphrase(): Promise<string> {
  if (!process.stdin.isTTY) {
    console.error('ERROR: No passphrase provided and stdin is not a TTY. Use --passphrase.')
    process.exit(1)
  }
  return new Promise(resolve => {
    process.stderr.write('Vault passphrase: ')
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
      rl.question('', answer => {
        rl.close()
        resolve(answer)
      })
    }
  })
}

async function getSecret(name: string, passphrase: string): Promise<string> {
  const proc = Bun.spawn(
    ['bun', join(ROOT, 'manifest/framework/scripts/secrets.ts'), 'get', name, '--passphrase', passphrase],
    { stdout: 'pipe', stderr: 'pipe' }
  )
  const code = await proc.exited
  if (code !== 0) {
    const errText = await new Response(proc.stderr).text()
    console.error(`ERROR: Could not retrieve '${name}' from vault.`)
    console.error(errText.trim())
    process.exit(1)
  }
  return (await new Response(proc.stdout).text()).trim()
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2))

  const remoteUrl = await getRemoteUrl()
  const [owner, repo] = parseOwnerRepo(remoteUrl)
  console.log(`Repo: ${owner}/${repo}`)

  if (!(await githubApiReachable())) {
    printManualInstructions(owner, repo)
    process.exit(0)
  }

  const passphrase = args['passphrase'] ?? await promptPassphrase()
  const pat = await getSecret('github-pat', passphrase)

  try {
    const resp = await fetch(`https://api.github.com/repos/${owner}/${repo}`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${pat}`,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ private: true }),
    })

    if (!resp.ok) {
      const body = await resp.text()
      console.error(`ERROR: GitHub API ${resp.status}: ${body}`)
      process.exit(1)
    }

    const body = await resp.json() as { private?: boolean }
    if (body.private) {
      console.log(`Done. ${owner}/${repo} is now private.`)
    } else {
      console.log('WARNING: Request succeeded but repo does not appear private. Check GitHub.')
    }
  } catch (err) {
    console.error(`ERROR: Could not reach GitHub API: ${(err as Error).message}`)
    printManualInstructions(owner, repo)
    process.exit(1)
  }
}

main().catch(err => {
  console.error(`ERROR: ${err.message}`)
  process.exit(1)
})
