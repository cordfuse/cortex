#!/usr/bin/env bun
// Tier 3 fallback for the Cortex `get_current_time` contract.
// Returns current system time in ISO 8601 format with timezone offset.
// No arguments. No network. Stateless. Fast.
// Output example: 2026-04-23T19:09:38-04:00

function formatTzOffset(): string {
  const offset = -new Date().getTimezoneOffset()
  const sign = offset >= 0 ? '+' : '-'
  const abs = Math.abs(offset)
  const h = String(Math.floor(abs / 60)).padStart(2, '0')
  const m = String(abs % 60).padStart(2, '0')
  return `${sign}${h}:${m}`
}

const now = new Date()
const iso = now.toISOString() // ends in Z
const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
  .toISOString()
  .replace('Z', formatTzOffset())
console.log(local)
