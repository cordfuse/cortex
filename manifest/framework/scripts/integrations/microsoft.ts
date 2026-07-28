#!/usr/bin/env bun
/**
 * Cortex Microsoft 365 integration — Mail, Calendar, OneDrive, Teams,
 * SharePoint, To Do, Planner, OneNote.
 *
 * One-time setup:
 *   1. Go to https://portal.azure.com → Azure Active Directory → App registrations
 *   2. New registration — set redirect URI to http://localhost
 *   3. Under API permissions, add Microsoft Graph delegated permissions
 *   4. Under Certificates & secrets, create a client secret
 *   5. Run: bun manifest/framework/scripts/integrations/microsoft.ts auth
 *
 * Usage:
 *   bun manifest/framework/scripts/integrations/microsoft.ts [--passphrase <p>] auth
 *   bun manifest/framework/scripts/integrations/microsoft.ts [--passphrase <p>] mail [--count 20]
 *   bun manifest/framework/scripts/integrations/microsoft.ts [--passphrase <p>] calendar [--days 7]
 *   bun manifest/framework/scripts/integrations/microsoft.ts [--passphrase <p>] onedrive [--count 20]
 *   bun manifest/framework/scripts/integrations/microsoft.ts [--passphrase <p>] teams [--count 20]
 *   bun manifest/framework/scripts/integrations/microsoft.ts [--passphrase <p>] sharepoint [--count 20]
 *   bun manifest/framework/scripts/integrations/microsoft.ts [--passphrase <p>] todo
 *   bun manifest/framework/scripts/integrations/microsoft.ts [--passphrase <p>] planner
 *   bun manifest/framework/scripts/integrations/microsoft.ts [--passphrase <p>] onenote [--count 20]
 *
 * `--passphrase` must come BEFORE the subcommand.
 * No npm dependencies — uses fetch only.
 */

import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import * as readline from 'node:readline'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '../../../..')
const GRAPH_BASE = 'https://graph.microsoft.com/v1.0'

const SCOPES = [
  'Mail.Read',
  'Calendars.Read',
  'Files.Read.All',
  'Chat.Read',
  'ChannelMessage.Read.All',
  'Sites.Read.All',
  'Tasks.Read',
  'Notes.Read.All',
  'offline_access',
  'User.Read',
].join(' ')

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

// --- Vault helpers ---

async function getSecret(name: string, passphrase: string): Promise<string> {
  const proc = Bun.spawn(
    ['bun', join(ROOT, 'manifest/framework/scripts/secrets.ts'), 'get', name, '--passphrase', passphrase],
    { stdout: 'pipe', stderr: 'pipe' }
  )
  const code = await proc.exited
  if (code !== 0) {
    console.error(`ERROR: Could not retrieve '${name}' from vault.`)
    console.error('Run: bun manifest/framework/scripts/integrations/microsoft.ts auth')
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

// --- Token refresh ---

async function getAccessToken(passphrase: string): Promise<{ token: string; passphrase: string }> {
  const clientId = await getSecret('msft_client_id', passphrase)
  const clientSecret = await getSecret('msft_client_secret', passphrase)
  const refreshToken = await getSecret('msft_refresh_token', passphrase)
  const tenantId = await getSecret('msft_tenant_id', passphrase)

  const resp = await fetch(
    `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/token`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        client_id: clientId,
        client_secret: clientSecret,
        refresh_token: refreshToken,
        grant_type: 'refresh_token',
        // FOOTGUN: `.default` requests the app registration's *statically
        // configured* permissions, which can differ from the delegated scopes
        // actually consented at auth time — on a dynamic-consent flow
        // (`common` tenant / personal accounts) this can silently drop or
        // change scopes vs. the original grant. It works for the current
        // registration; if scope-related 401s ever appear, refresh with the
        // original `SCOPES` (or omit `scope` to inherit the prior grant).
        scope: 'https://graph.microsoft.com/.default offline_access',
      }),
    }
  )

  if (!resp.ok) {
    const body = await resp.text()
    console.error(`ERROR: Microsoft token refresh failed (${resp.status}): ${body.slice(0, 300)}`)
    process.exit(1)
  }

  const data = await resp.json() as {
    access_token?: string
    refresh_token?: string
    error_description?: string
  }

  if (!data.access_token) {
    console.error(`ERROR: Token refresh failed: ${data.error_description ?? 'unknown'}`)
    process.exit(1)
  }

  // Store updated refresh token if rotated
  if (data.refresh_token && data.refresh_token !== refreshToken) {
    await storeSecret('msft_refresh_token', data.refresh_token, passphrase)
  }

  return { token: data.access_token, passphrase }
}

// --- Graph API helper ---

async function graph(token: string, path: string, params?: Record<string, string | number>): Promise<unknown> {
  const url = new URL(`${GRAPH_BASE}${path}`)
  if (params) {
    for (const [k, v] of Object.entries(params)) url.searchParams.set(k, String(v))
  }
  const resp = await fetch(url.toString(), {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!resp.ok) {
    const body = await resp.text()
    console.error(`ERROR: Graph API ${path} returned ${resp.status}: ${body.slice(0, 300)}`)
    process.exit(1)
  }
  return resp.json()
}

// --- Auth (device code flow) ---

async function cmdAuth(passphrase: string): Promise<void> {
  console.log('Microsoft 365 / Azure OAuth setup')
  console.log('You need an Azure App Registration with Microsoft Graph permissions.')
  console.log('https://portal.azure.com → Azure Active Directory → App registrations\n')

  const tenantId = await promptLine("Tenant ID (or 'common' for personal accounts)")
  const clientId = await promptLine('Client ID (Application ID)')
  const clientSecret = await promptLine('Client Secret')

  // Step 1: get device code
  const dcResp = await fetch(
    `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/devicecode`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ client_id: clientId, scope: SCOPES }),
    }
  )
  if (!dcResp.ok) {
    const body = await dcResp.text()
    console.error(`ERROR: Failed to create device flow (${dcResp.status}): ${body}`)
    process.exit(1)
  }
  const flow = await dcResp.json() as {
    user_code?: string
    device_code?: string
    verification_uri?: string
    message?: string
    interval?: number
    expires_in?: number
  }
  if (!flow.user_code || !flow.device_code) {
    console.error('ERROR: Failed to create device flow.')
    process.exit(1)
  }

  console.log(`\n${flow.message ?? `Go to ${flow.verification_uri} and enter code: ${flow.user_code}`}\n`)

  // Step 2: poll until authorized
  const interval = (flow.interval ?? 5) * 1000
  const expiresAt = Date.now() + (flow.expires_in ?? 900) * 1000

  let accessToken: string | undefined
  let refreshToken: string | undefined

  while (Date.now() < expiresAt) {
    await new Promise(r => setTimeout(r, interval))
    const pollResp = await fetch(
      `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/token`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          client_id: clientId,
          client_secret: clientSecret,
          device_code: flow.device_code,
          grant_type: 'urn:ietf:params:oauth:grant-type:device_code',
        }),
      }
    )
    const data = await pollResp.json() as {
      access_token?: string
      refresh_token?: string
      error?: string
      error_description?: string
    }
    if (data.access_token) {
      accessToken = data.access_token
      refreshToken = data.refresh_token
      break
    }
    if (data.error && data.error !== 'authorization_pending' && data.error !== 'slow_down') {
      console.error(`ERROR: Authentication failed: ${data.error_description ?? data.error}`)
      process.exit(1)
    }
  }

  if (!accessToken || !refreshToken) {
    console.error('ERROR: Authentication timed out or failed.')
    process.exit(1)
  }

  await storeSecret('msft_tenant_id', tenantId, passphrase)
  await storeSecret('msft_client_id', clientId, passphrase)
  await storeSecret('msft_client_secret', clientSecret, passphrase)
  await storeSecret('msft_refresh_token', refreshToken, passphrase)

  console.log('\nCredentials stored in vault.')
  console.log('Commit cortex.secrets/ to persist across devices.')
}

// --- Mail ---

async function cmdMail(count: number, passphrase: string): Promise<void> {
  const { token } = await getAccessToken(passphrase)
  const data = await graph(token, '/me/mailFolders/inbox/messages', {
    $top: count,
    $filter: 'isRead eq false',
    $orderby: 'receivedDateTime desc',
    $select: 'subject,from,receivedDateTime,bodyPreview',
  }) as { value?: Array<{
    subject?: string
    from?: { emailAddress?: { address?: string } }
    receivedDateTime?: string
    bodyPreview?: string
  }> }

  const messages = data.value ?? []
  if (messages.length === 0) {
    console.log('No unread messages.')
    return
  }

  console.log(`# Outlook Mail — ${messages.length} unread\n`)
  for (const m of messages) {
    const subject = m.subject ?? '(no subject)'
    const sender = m.from?.emailAddress?.address ?? ''
    const received = m.receivedDateTime
      ? new Date(m.receivedDateTime).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
      : ''
    const preview = (m.bodyPreview ?? '').slice(0, 120)
    console.log(`**${subject}**`)
    console.log(`From: ${sender} | ${received}`)
    if (preview) console.log(`> ${preview}...`)
    console.log()
  }
}

// --- Calendar ---

async function cmdCalendar(days: number, passphrase: string): Promise<void> {
  const { token } = await getAccessToken(passphrase)
  const now = new Date()
  const end = new Date(now.getTime() + days * 24 * 60 * 60 * 1000)

  const data = await graph(token, '/me/calendarView', {
    startDateTime: now.toISOString(),
    endDateTime: end.toISOString(),
    $top: 50,
    $orderby: 'start/dateTime',
    $select: 'subject,start,end,location,isOnlineMeeting',
  }) as { value?: Array<{
    subject?: string
    start?: { dateTime?: string }
    location?: { displayName?: string }
    isOnlineMeeting?: boolean
  }> }

  const events = data.value ?? []
  if (events.length === 0) {
    console.log(`No events in the next ${days} days.`)
    return
  }

  console.log(`# Outlook Calendar — next ${days} days\n`)
  for (const e of events) {
    const subject = e.subject ?? '(no title)'
    const startDt = e.start?.dateTime
    const startFmt = startDt
      ? new Date(startDt).toLocaleDateString('en-GB', { weekday: 'short', day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
      : ''
    const location = e.location?.displayName ?? ''
    const online = e.isOnlineMeeting ? ' (online)' : ''
    const locStr = location ? ` — ${location}` : ''
    console.log(`- ${startFmt}: ${subject}${locStr}${online}`)
  }
}

// --- OneDrive ---

async function cmdOnedrive(count: number, passphrase: string): Promise<void> {
  const { token } = await getAccessToken(passphrase)
  const data = await graph(token, '/me/drive/recent', {
    $top: count,
    $select: 'name,lastModifiedDateTime,webUrl,file,folder',
  }) as { value?: Array<{
    name?: string
    lastModifiedDateTime?: string
    webUrl?: string
    file?: unknown
    folder?: unknown
  }> }

  const files = data.value ?? []
  if (files.length === 0) {
    console.log('No recent files.')
    return
  }

  console.log(`# OneDrive — ${count} recently accessed\n`)
  for (const f of files) {
    const name = f.name ?? ''
    const modified = f.lastModifiedDateTime
      ? new Date(f.lastModifiedDateTime).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
      : ''
    const url = f.webUrl ?? ''
    const kind = f.folder ? 'Folder' : 'File'
    console.log(`- [${name}](${url}) (${kind}) — ${modified}`)
  }
}

// --- Teams ---

async function cmdTeams(count: number, passphrase: string): Promise<void> {
  const { token } = await getAccessToken(passphrase)

  // `--count` = number of chats to summarise, uniform with the other
  // subcommands where it means "N items". Each chat shows its most recent
  // messages. Previously `count` was treated as a message budget while the
  // chat query was hardcoded to `$top: 10`, so any `--count` above ~10 chats'
  // worth of messages was silently capped regardless of what the user asked.
  const chatsData = await graph(token, '/me/chats', {
    $top: count,
    $expand: 'members',
    $select: 'id,topic,chatType,lastUpdatedDateTime',
  }) as { value?: Array<{ id?: string; topic?: string }> }

  const chats = chatsData.value ?? []
  if (chats.length === 0) {
    console.log('No Teams chats found.')
    return
  }

  console.log('# Microsoft Teams — recent messages\n')
  for (const chat of chats) {
    const chatId = chat.id ?? ''
    const topic = chat.topic ?? 'Direct message'
    const msgsData = await graph(token, `/me/chats/${chatId}/messages`, {
      $top: 5,
      $select: 'from,body,createdDateTime',
    }) as { value?: Array<{
      from?: { user?: { displayName?: string } }
      body?: { content?: string }
      createdDateTime?: string
    }> }
    const msgs = msgsData.value ?? []
    if (msgs.length === 0) continue

    console.log(`**${topic}**`)
    for (const msg of msgs) {
      const sender = msg.from?.user?.displayName ?? 'Unknown'
      const created = msg.createdDateTime
        ? new Date(msg.createdDateTime).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
        : ''
      const body = (msg.body?.content ?? '').slice(0, 100).replace(/\n/g, ' ')
      console.log(`  ${created} ${sender}: ${body}`)
    }
    console.log()
  }
}

// --- SharePoint ---

async function cmdSharepoint(count: number, passphrase: string): Promise<void> {
  const { token } = await getAccessToken(passphrase)
  const data = await graph(token, '/me/followedSites', {
    $select: 'id,name,webUrl,lastModifiedDateTime',
  }) as { value?: Array<{
    name?: string
    webUrl?: string
    lastModifiedDateTime?: string
  }> }

  const sites = (data.value ?? []).slice(0, count)
  if (sites.length === 0) {
    console.log('No followed SharePoint sites.')
    return
  }

  console.log('# SharePoint — followed sites\n')
  for (const site of sites) {
    const name = site.name ?? ''
    const url = site.webUrl ?? ''
    const modified = site.lastModifiedDateTime
      ? new Date(site.lastModifiedDateTime).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
      : ''
    console.log(`- [${name}](${url}) — ${modified}`)
  }
}

// --- To Do ---

async function cmdTodo(passphrase: string): Promise<void> {
  const { token } = await getAccessToken(passphrase)
  const listsData = await graph(token, '/me/todo/lists', {
    $select: 'id,displayName',
  }) as { value?: Array<{ id?: string; displayName?: string }> }

  const lists = listsData.value ?? []
  if (lists.length === 0) {
    console.log('No To Do lists found.')
    return
  }

  console.log('# Microsoft To Do\n')
  for (const lst of lists) {
    const listId = lst.id ?? ''
    const listName = lst.displayName ?? ''
    const tasksData = await graph(token, `/me/todo/lists/${listId}/tasks`, {
      $filter: "status ne 'completed'",
      $select: 'title,importance,dueDateTime,status',
      $top: 20,
    }) as { value?: Array<{
      title?: string
      importance?: string
      dueDateTime?: { dateTime?: string }
    }> }
    const tasks = tasksData.value ?? []
    if (tasks.length === 0) continue
    console.log(`**${listName}**`)
    for (const t of tasks) {
      const title = t.title ?? ''
      const importance = t.importance ?? 'normal'
      const dueDt = t.dueDateTime?.dateTime
      const dueStr = dueDt
        ? ` (due ${new Date(dueDt).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })})`
        : ''
      const flag = importance === 'high' ? ' !' : ''
      console.log(`  - ${title}${dueStr}${flag}`)
    }
    console.log()
  }
}

// --- Planner ---

async function cmdPlanner(passphrase: string): Promise<void> {
  const { token } = await getAccessToken(passphrase)
  const plansData = await graph(token, '/me/planner/tasks', {
    $select: 'title,percentComplete,dueDateTime,planId,bucketId',
    $filter: 'percentComplete lt 100',
    $top: 50,
  }) as { value?: Array<{
    title?: string
    percentComplete?: number
    dueDateTime?: string
  }> }

  const tasks = plansData.value ?? []
  if (tasks.length === 0) {
    console.log('No open Planner tasks.')
    return
  }

  console.log('# Microsoft Planner — open tasks\n')
  for (const t of tasks) {
    const title = t.title ?? ''
    const pct = t.percentComplete ?? 0
    const dueStr = t.dueDateTime
      ? ` (due ${new Date(t.dueDateTime).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })})`
      : ''
    const progress = pct ? ` [${pct}%]` : ''
    console.log(`- ${title}${dueStr}${progress}`)
  }
}

// --- OneNote ---

async function cmdOnenote(count: number, passphrase: string): Promise<void> {
  const { token } = await getAccessToken(passphrase)
  const data = await graph(token, '/me/onenote/pages', {
    $top: count,
    $orderby: 'lastModifiedDateTime desc',
    $select: 'title,lastModifiedDateTime,parentNotebook,webUrl',
  }) as { value?: Array<{
    title?: string
    lastModifiedDateTime?: string
    parentNotebook?: { displayName?: string }
    webUrl?: string
  }> }

  const pages = data.value ?? []
  if (pages.length === 0) {
    console.log('No OneNote pages found.')
    return
  }

  console.log(`# OneNote — ${count} recently modified\n`)
  for (const p of pages) {
    const title = p.title ?? '(untitled)'
    const modified = p.lastModifiedDateTime
      ? new Date(p.lastModifiedDateTime).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
      : ''
    const notebook = p.parentNotebook?.displayName ?? ''
    const url = p.webUrl ?? ''
    const nbStr = notebook ? ` [${notebook}]` : ''
    console.log(`- [${title}](${url})${nbStr} — ${modified}`)
  }
}

// --- Main ---

async function main(): Promise<void> {
  const argv = process.argv.slice(2)
  if (argv.length === 0) {
    console.log('Usage: bun manifest/framework/scripts/integrations/microsoft.ts [--passphrase <p>] <subcommand> [options]')
    console.log('Subcommands: auth, mail, calendar, onedrive, teams, sharepoint, todo, planner, onenote')
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
  } else if (cmd === 'mail') {
    await cmdMail(Number(cmdArgs['count'] ?? 20), passphrase)
  } else if (cmd === 'calendar') {
    await cmdCalendar(Number(cmdArgs['days'] ?? 7), passphrase)
  } else if (cmd === 'onedrive') {
    await cmdOnedrive(Number(cmdArgs['count'] ?? 20), passphrase)
  } else if (cmd === 'teams') {
    await cmdTeams(Number(cmdArgs['count'] ?? 20), passphrase)
  } else if (cmd === 'sharepoint') {
    await cmdSharepoint(Number(cmdArgs['count'] ?? 20), passphrase)
  } else if (cmd === 'todo') {
    await cmdTodo(passphrase)
  } else if (cmd === 'planner') {
    await cmdPlanner(passphrase)
  } else if (cmd === 'onenote') {
    await cmdOnenote(Number(cmdArgs['count'] ?? 20), passphrase)
  } else {
    console.error(`ERROR: Unknown subcommand '${cmd}'.`)
    process.exit(1)
  }
}

main().catch(err => {
  console.error(`ERROR: ${(err as Error).message}`)
  process.exit(1)
})
