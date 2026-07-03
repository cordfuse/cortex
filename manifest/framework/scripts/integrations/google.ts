#!/usr/bin/env bun
/**
 * Cortex Google integration — Calendar, Gmail, Drive, Tasks, Contacts.
 *
 * Credentials are stored in the Cortex secrets vault.
 * Run once to set up:
 *   bun manifest/framework/scripts/integrations/google.ts auth
 *
 * Usage (read):
 *   bun manifest/framework/scripts/integrations/google.ts [--passphrase <p>] auth
 *   bun manifest/framework/scripts/integrations/google.ts [--passphrase <p>] calendar [--days 7]
 *   bun manifest/framework/scripts/integrations/google.ts [--passphrase <p>] gmail [--count 20]
 *   bun manifest/framework/scripts/integrations/google.ts [--passphrase <p>] drive [--count 20]
 *   bun manifest/framework/scripts/integrations/google.ts [--passphrase <p>] tasks
 *   bun manifest/framework/scripts/integrations/google.ts [--passphrase <p>] contacts [--count 50]
 *
 * Usage (write):
 *   bun manifest/framework/scripts/integrations/google.ts [--passphrase <p>] send-mail --to <addr> --subject <s> --body <b>
 *   bun manifest/framework/scripts/integrations/google.ts [--passphrase <p>] create-event --summary <s> --start <ISO> --end <ISO> [--calendar primary] [--description <d>] [--location <l>] [--attendees a@b,c@d]
 *   bun manifest/framework/scripts/integrations/google.ts [--passphrase <p>] create-task --title <t> [--list @default] [--notes <n>] [--due <YYYY-MM-DD>]
 *
 * `--passphrase` must come BEFORE the subcommand.
 * No npm dependencies — uses fetch + node:crypto.
 */

import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import * as readline from 'node:readline'
import { createServer } from 'node:http'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '../../../..')

const SCOPES = [
  'https://www.googleapis.com/auth/calendar.readonly',
  'https://www.googleapis.com/auth/calendar.events',
  'https://www.googleapis.com/auth/gmail.modify',
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/drive.file',
  'https://www.googleapis.com/auth/drive.readonly',
  'https://www.googleapis.com/auth/tasks',
  'https://www.googleapis.com/auth/contacts',
]

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
    const err = await new Response(proc.stderr).text()
    console.error(`ERROR: Could not retrieve '${name}' from vault.`)
    console.error('Run: bun manifest/framework/scripts/integrations/google.ts auth')
    if (err.trim()) console.error(err.trim())
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

// --- OAuth token refresh ---

async function refreshAccessToken(clientId: string, clientSecret: string, refreshToken: string): Promise<string> {
  const resp = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: 'refresh_token',
    }),
  })
  if (!resp.ok) {
    const body = await resp.text()
    console.error(`ERROR: Google token refresh failed (${resp.status}): ${body}`)
    process.exit(1)
  }
  const data = await resp.json() as { access_token?: string; error?: string; error_description?: string }
  if (!data.access_token) {
    console.error(`ERROR: Google token refresh failed: ${data.error_description ?? data.error ?? 'unknown'}`)
    process.exit(1)
  }
  return data.access_token
}

async function getAccessToken(passphrase: string): Promise<string> {
  const clientId = await getSecret('google_client_id', passphrase)
  const clientSecret = await getSecret('google_client_secret', passphrase)
  const refreshToken = await getSecret('google_refresh_token', passphrase)
  return refreshAccessToken(clientId, clientSecret, refreshToken)
}

// --- Google API helper ---

async function gapi(token: string, path: string, params?: Record<string, string | number>): Promise<unknown> {
  const url = new URL(`https://www.googleapis.com${path}`)
  if (params) {
    for (const [k, v] of Object.entries(params)) url.searchParams.set(k, String(v))
  }
  const resp = await fetch(url.toString(), {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!resp.ok) {
    const body = await resp.text()
    if (resp.status === 401) {
      console.error('ERROR: Google auth expired. Re-run: bun manifest/framework/scripts/integrations/google.ts auth')
      process.exit(1)
    }
    if (resp.status === 403) {
      console.error('ERROR: Google access denied. Re-run auth to upgrade the grant: bun manifest/framework/scripts/integrations/google.ts auth')
      process.exit(1)
    }
    console.error(`ERROR: Google API ${path} returned ${resp.status}: ${body.slice(0, 300)}`)
    process.exit(1)
  }
  return resp.json()
}

async function gapiPost(token: string, path: string, body: unknown, params?: Record<string, string>): Promise<unknown> {
  const url = new URL(`https://www.googleapis.com${path}`)
  if (params) {
    for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v)
  }
  const resp = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  if (!resp.ok) {
    const text = await resp.text()
    if (resp.status === 403) {
      console.error('ERROR: Google access denied. Re-run auth to upgrade the grant: bun manifest/framework/scripts/integrations/google.ts auth')
      process.exit(1)
    }
    console.error(`ERROR: Google API ${path} returned ${resp.status}: ${text.slice(0, 300)}`)
    process.exit(1)
  }
  return resp.json()
}

// --- Auth ---

async function cmdAuth(passphrase: string): Promise<void> {
  console.log('Google OAuth setup')
  console.log('Requires a Google Cloud project with Calendar, Gmail, Drive, Tasks, and People APIs enabled.')
  console.log('https://console.cloud.google.com/apis/credentials\n')

  const existingId = await tryGetSecret('google_client_id', passphrase)
  const existingSecret = await tryGetSecret('google_client_secret', passphrase)

  let clientId: string
  let clientSecret: string

  if (existingId && existingSecret) {
    console.log(`Using existing OAuth client from vault (client_id ends in ...${existingId.slice(-12)}).`)
    console.log('To use a different OAuth client, delete the vault entries first:')
    console.log('  bun manifest/framework/scripts/secrets.ts delete google_client_id')
    console.log('  bun manifest/framework/scripts/secrets.ts delete google_client_secret\n')
    clientId = existingId
    clientSecret = existingSecret
  } else {
    clientId = await promptLine('Client ID')
    clientSecret = await promptLine('Client Secret')
  }

  const redirectUri = 'http://localhost:8080'
  const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth')
  authUrl.searchParams.set('client_id', clientId)
  authUrl.searchParams.set('redirect_uri', redirectUri)
  authUrl.searchParams.set('response_type', 'code')
  authUrl.searchParams.set('scope', SCOPES.join(' '))
  authUrl.searchParams.set('access_type', 'offline')
  authUrl.searchParams.set('prompt', 'consent')

  console.log('\nOpen this URL in your browser to authorize:')
  console.log(authUrl.toString())
  console.log('\nWaiting for callback on http://localhost:8080 ...')

  const code = await new Promise<string>((resolve, reject) => {
    const server = createServer((req, res) => {
      const url = new URL(req.url ?? '/', 'http://localhost:8080')
      const code = url.searchParams.get('code')
      res.writeHead(200, { 'Content-Type': 'text/html' })
      res.end('<html><body><h2>Authorization complete. You can close this tab.</h2></body></html>')
      server.close()
      if (code) resolve(code)
      else reject(new Error('No code in callback'))
    })
    server.listen(8080, () => {})
    server.on('error', reject)
  })

  // Exchange code for tokens
  const tokenResp = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      code,
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uri: redirectUri,
      grant_type: 'authorization_code',
    }),
  })
  if (!tokenResp.ok) {
    const body = await tokenResp.text()
    console.error(`ERROR: Token exchange failed (${tokenResp.status}): ${body}`)
    process.exit(1)
  }
  const tokens = await tokenResp.json() as { refresh_token?: string }
  if (!tokens.refresh_token) {
    console.error('ERROR: No refresh token in response. Make sure prompt=consent was set.')
    process.exit(1)
  }

  await storeSecret('google_client_id', clientId, passphrase)
  await storeSecret('google_client_secret', clientSecret, passphrase)
  await storeSecret('google_refresh_token', tokens.refresh_token, passphrase)

  console.log('\nCredentials stored in vault.')
  console.log('Commit cortex.secrets/ to persist across devices.')
}

// --- Calendar ---

async function cmdCalendar(days: number, passphrase: string): Promise<void> {
  const token = await getAccessToken(passphrase)
  const now = new Date()
  const timeMax = new Date(now.getTime() + days * 24 * 60 * 60 * 1000)

  const result = await gapi(token, '/calendar/v3/calendars/primary/events', {
    timeMin: now.toISOString(),
    timeMax: timeMax.toISOString(),
    singleEvents: 'true',
    orderBy: 'startTime',
    maxResults: 50,
  }) as { items?: Array<{
    start?: { dateTime?: string; date?: string }
    summary?: string
    location?: string
  }> }

  const events = result.items ?? []
  if (events.length === 0) {
    console.log(`No events in the next ${days} days.`)
    return
  }

  console.log(`# Google Calendar — next ${days} days\n`)
  for (const e of events) {
    const start = e.start ?? {}
    const dt = start.dateTime ?? start.date ?? ''
    let dtFmt: string
    if (dt.includes('T')) {
      dtFmt = new Date(dt).toLocaleDateString('en-GB', { weekday: 'short', day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
    } else {
      dtFmt = new Date(dt + 'T00:00:00').toLocaleDateString('en-GB', { weekday: 'short', day: '2-digit', month: 'short' })
    }
    const summary = e.summary ?? '(no title)'
    const location = e.location ?? ''
    const locStr = location ? ` — ${location}` : ''
    console.log(`- ${dtFmt}: ${summary}${locStr}`)
  }
}

// --- Gmail ---

async function cmdGmail(count: number, passphrase: string): Promise<void> {
  const token = await getAccessToken(passphrase)

  const result = await gapi(token, '/gmail/v1/users/me/messages', {
    maxResults: count,
    labelIds: 'INBOX',
    q: 'is:unread',
  }) as { messages?: Array<{ id: string }> }

  const messages = result.messages ?? []
  if (messages.length === 0) {
    console.log('No unread messages.')
    return
  }

  console.log(`# Gmail — ${messages.length} unread\n`)
  for (const msg of messages) {
    const detail = await gapi(
      token,
      `/gmail/v1/users/me/messages/${msg.id}`,
      { format: 'metadata', metadataHeaders: 'From,Subject,Date' }
    ) as {
      payload?: { headers?: Array<{ name: string; value: string }> }
      snippet?: string
    }

    const headers: Record<string, string> = {}
    for (const h of detail.payload?.headers ?? []) {
      headers[h.name] = h.value
    }
    const subject = headers['Subject'] ?? '(no subject)'
    const sender = headers['From'] ?? ''
    const date = headers['Date'] ?? ''
    const snippet = (detail.snippet ?? '').slice(0, 120)

    console.log(`**${subject}**`)
    console.log(`From: ${sender} | ${date}`)
    if (snippet) console.log(`> ${snippet}...`)
    console.log()
  }
}

// --- Drive ---

async function cmdDrive(count: number, passphrase: string): Promise<void> {
  const token = await getAccessToken(passphrase)

  const result = await gapi(token, '/drive/v3/files', {
    pageSize: count,
    orderBy: 'modifiedTime desc',
    fields: 'files(id,name,mimeType,modifiedTime,webViewLink)',
    q: 'trashed = false',
  }) as { files?: Array<{ name?: string; mimeType?: string; modifiedTime?: string; webViewLink?: string }> }

  const files = result.files ?? []
  if (files.length === 0) {
    console.log('No files found.')
    return
  }

  const MIME_LABELS: Record<string, string> = {
    'application/vnd.google-apps.document': 'Doc',
    'application/vnd.google-apps.spreadsheet': 'Sheet',
    'application/vnd.google-apps.presentation': 'Slides',
    'application/vnd.google-apps.folder': 'Folder',
    'application/pdf': 'PDF',
  }

  console.log(`# Google Drive — ${count} recently modified\n`)
  for (const f of files) {
    const name = f.name ?? ''
    const mime = f.mimeType ?? ''
    const label = MIME_LABELS[mime] ?? 'File'
    const modified = f.modifiedTime
      ? new Date(f.modifiedTime).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
      : ''
    const link = f.webViewLink ?? ''
    console.log(`- [${name}](${link}) (${label}) — modified ${modified}`)
  }
}

// --- Tasks ---

async function cmdTasks(passphrase: string): Promise<void> {
  const token = await getAccessToken(passphrase)

  const listsResult = await gapi(token, '/tasks/v1/users/@me/lists', { maxResults: 20 }) as {
    items?: Array<{ id: string; title?: string }>
  }
  const taskLists = listsResult.items ?? []

  if (taskLists.length === 0) {
    console.log('No task lists found.')
    return
  }

  console.log('# Google Tasks\n')
  for (const lst of taskLists) {
    const listId = lst.id
    const listTitle = lst.title ?? ''
    const tasksResult = await gapi(token, `/tasks/v1/lists/${listId}/tasks`, {
      showCompleted: 'false',
      maxResults: 20,
    }) as { items?: Array<{ title?: string; due?: string; notes?: string }> }
    const tasks = tasksResult.items ?? []
    if (tasks.length === 0) continue
    console.log(`**${listTitle}**`)
    for (const t of tasks) {
      const title = t.title ?? ''
      const due = t.due ?? ''
      const dueStr = due
        ? ` (due ${new Date(due).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })})`
        : ''
      const notes = t.notes ?? ''
      const noteStr = notes ? `\n    ${notes}` : ''
      console.log(`  - ${title}${dueStr}${noteStr}`)
    }
    console.log()
  }
}

// --- Contacts ---

async function cmdContacts(count: number, passphrase: string): Promise<void> {
  const token = await getAccessToken(passphrase)

  const result = await gapi(token, '/v1/people/me/connections', {
    pageSize: count,
    personFields: 'names,emailAddresses,phoneNumbers,organizations',
    sortOrder: 'LAST_MODIFIED_DESCENDING',
  }) as {
    connections?: Array<{
      names?: Array<{ displayName?: string }>
      emailAddresses?: Array<{ value?: string }>
      phoneNumbers?: Array<{ value?: string }>
      organizations?: Array<{ name?: string }>
    }>
  }

  const connections = result.connections ?? []
  if (connections.length === 0) {
    console.log('No contacts found.')
    return
  }

  console.log(`# Google Contacts — ${connections.length} recently modified\n`)
  for (const person of connections) {
    const name = person.names?.[0]?.displayName ?? '(no name)'
    const email = person.emailAddresses?.[0]?.value ?? ''
    const phone = person.phoneNumbers?.[0]?.value ?? ''
    const org = person.organizations?.[0]?.name ?? ''
    const details = [email, phone, org].filter(Boolean).join(' | ')
    console.log(`- **${name}**${details ? ` — ${details}` : ''}`)
  }
}

// --- Send mail ---

async function cmdSendMail(to: string, subject: string, body: string, passphrase: string): Promise<void> {
  const token = await getAccessToken(passphrase)

  // Construct RFC 2822 message
  const message = [
    `To: ${to}`,
    `Subject: ${subject}`,
    'Content-Type: text/plain; charset=utf-8',
    '',
    body,
  ].join('\r\n')

  const raw = Buffer.from(message).toString('base64url')

  const result = await gapiPost(token, '/gmail/v1/users/me/messages/send', { raw }) as { id?: string }
  const msgId = result.id ?? 'unknown'
  console.log(`Sent. Gmail message ID: ${msgId}`)
  console.log(`To:      ${to}`)
  console.log(`Subject: ${subject}`)
}

// --- Create event ---

async function cmdCreateEvent(opts: {
  summary: string
  start: string
  end: string
  calendar: string
  description: string
  location: string
  attendees: string
  passphrase: string
}): Promise<void> {
  const token = await getAccessToken(opts.passphrase)

  const startObj = opts.start.includes('T') ? { dateTime: opts.start } : { date: opts.start }
  const endObj = opts.end.includes('T') ? { dateTime: opts.end } : { date: opts.end }

  const eventBody: Record<string, unknown> = {
    summary: opts.summary,
    start: startObj,
    end: endObj,
  }
  if (opts.description) eventBody['description'] = opts.description
  if (opts.location) eventBody['location'] = opts.location
  if (opts.attendees) {
    eventBody['attendees'] = opts.attendees.split(',')
      .map(a => a.trim())
      .filter(Boolean)
      .map(email => ({ email }))
  }

  const result = await gapiPost(
    token,
    `/calendar/v3/calendars/${opts.calendar}/events`,
    eventBody,
    { sendUpdates: opts.attendees ? 'all' : 'none' }
  ) as { id?: string; htmlLink?: string }

  console.log(`Created. Event ID: ${result.id ?? 'unknown'}`)
  console.log(`Calendar: ${opts.calendar}`)
  console.log(`Summary:  ${opts.summary}`)
  console.log(`When:     ${opts.start} -> ${opts.end}`)
  if (result.htmlLink) console.log(`URL:      ${result.htmlLink}`)
}

// --- Create task ---

async function cmdCreateTask(opts: {
  title: string
  tasklist: string
  notes: string
  due: string
  passphrase: string
}): Promise<void> {
  const token = await getAccessToken(opts.passphrase)

  let due = opts.due
  if (due && !due.includes('T')) due = `${due}T00:00:00.000Z`

  const taskBody: Record<string, unknown> = { title: opts.title }
  if (opts.notes) taskBody['notes'] = opts.notes
  if (due) taskBody['due'] = due

  const result = await gapiPost(token, `/tasks/v1/lists/${opts.tasklist}/tasks`, taskBody) as { id?: string }
  console.log(`Created. Task ID: ${result.id ?? 'unknown'}`)
  console.log(`List:  ${opts.tasklist}`)
  console.log(`Title: ${opts.title}`)
  if (due) console.log(`Due:   ${due}`)
}

// --- Main ---

async function main(): Promise<void> {
  const argv = process.argv.slice(2)
  if (argv.length === 0) {
    console.log('Usage: bun manifest/framework/scripts/integrations/google.ts [--passphrase <p>] <subcommand> [options]')
    console.log('Subcommands: auth, calendar, gmail, drive, tasks, contacts, send-mail, create-event, create-task')
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

  // Commands that need passphrase
  if (!passphrase) passphrase = await promptPassphrase()

  if (cmd === 'auth') {
    await cmdAuth(passphrase)
  } else if (cmd === 'calendar') {
    await cmdCalendar(Number(cmdArgs['days'] ?? 7), passphrase)
  } else if (cmd === 'gmail') {
    await cmdGmail(Number(cmdArgs['count'] ?? 20), passphrase)
  } else if (cmd === 'drive') {
    await cmdDrive(Number(cmdArgs['count'] ?? 20), passphrase)
  } else if (cmd === 'tasks') {
    await cmdTasks(passphrase)
  } else if (cmd === 'contacts') {
    await cmdContacts(Number(cmdArgs['count'] ?? 50), passphrase)
  } else if (cmd === 'send-mail') {
    const to = cmdArgs['to'] as string
    const subject = cmdArgs['subject'] as string
    const body = cmdArgs['body'] as string
    if (!to || !subject || !body) {
      console.error('ERROR: send-mail requires --to, --subject, --body')
      process.exit(1)
    }
    await cmdSendMail(to, subject, body, passphrase)
  } else if (cmd === 'create-event') {
    const summary = cmdArgs['summary'] as string
    const start = cmdArgs['start'] as string
    const end = cmdArgs['end'] as string
    if (!summary || !start || !end) {
      console.error('ERROR: create-event requires --summary, --start, --end')
      process.exit(1)
    }
    await cmdCreateEvent({
      summary,
      start,
      end,
      calendar: (cmdArgs['calendar'] as string) ?? 'primary',
      description: (cmdArgs['description'] as string) ?? '',
      location: (cmdArgs['location'] as string) ?? '',
      attendees: (cmdArgs['attendees'] as string) ?? '',
      passphrase,
    })
  } else if (cmd === 'create-task') {
    const title = cmdArgs['title'] as string
    if (!title) {
      console.error('ERROR: create-task requires --title')
      process.exit(1)
    }
    await cmdCreateTask({
      title,
      tasklist: (cmdArgs['list'] as string) ?? '@default',
      notes: (cmdArgs['notes'] as string) ?? '',
      due: (cmdArgs['due'] as string) ?? '',
      passphrase,
    })
  } else {
    console.error(`ERROR: Unknown subcommand '${cmd}'.`)
    process.exit(1)
  }
}

main().catch(err => {
  console.error(`ERROR: ${(err as Error).message}`)
  process.exit(1)
})
