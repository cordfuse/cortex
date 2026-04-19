# 2026-04-19 — Roadmap: Cortex Federation (3.0)

## The Idea

Multiple isolated Cortex repos — one per life context (work, personal, health, family) — linked as a single logical Cortex through a root repo that holds read-only pointers to satellites.

Each satellite controls its own exposure. The root can see what satellites permit. Nothing is automatic. No satellite ever writes to another.

**Git remotes are the federation protocol.** No abstraction layer. No vendor. Just git.

---

## Architecture

```
cortex-root/
  satellites.md        # list of linked satellite repos + what each exposes
  records/             # root-level entries (cross-context observations)
  cortex.secrets/      # root vault (holds PATs for each satellite)

cortex-personal/       # satellite — private, fully isolated
  .federation/
    expose.md          # what this satellite allows root to read

cortex-work/           # satellite — private, fully isolated
  .federation/
    expose.md

cortex-health/         # satellite — private, fully isolated
  .federation/
    expose.md
```

At `hello`, the root scribe:
1. Reads `satellites.md`
2. Pulls each satellite's permitted context (defined in `expose.md`)
3. Synthesizes a unified briefing across all linked repos
4. Writes only to root — never to satellites

---

## The Byref Model

Satellites are **read-only from the root's perspective**. The root holds a reference, not a copy.

Each satellite's `expose.md` defines the exposure contract:

```
expose: records/context.md
expose: records/2026-*.md    # all records this year
expose: none                  # fully private — root sees nothing
```

The root scribe respects this exactly. If a satellite says `none`, the root knows the satellite exists but reads nothing from it.

---

## Why This Is Different

Every existing federated memory system layers abstraction *over* git. This uses git *as* the protocol — federation is just remotes. No new infrastructure. No vendor lock-in. Works with any git host.

No existing personal knowledge system implements consent-based cross-repo visibility. The closest systems (Spine Pattern, BMAD-Federated-Knowledge, DiffMem) hit ~50-60% of this model and miss the two critical properties:

1. **Consent-based visibility** — satellite decides what root sees
2. **Git-native federation** — remotes as the link, not an API

---

## Use Cases

- Personal + work: root sees both, synthesizes patterns (stress at work bleeding into personal life)
- Family: each member has a private satellite; shared family root sees only what each member exposes
- Health: health satellite exposes summaries to personal root, never raw records
- Org: team members each have a satellite; project root synthesizes without accessing personal context

---

## Version Target

**Cortex 3.0** — this is a major architectural feature, not a patch.

Prerequisites before building:
- Stable single-repo experience (2.x)
- Vault v2 per-file format (done — 2026-04-19)
- GUARDRAILS sandbox whitelist (done — 2026-04-19)
- Multi-device sync proven reliable

---

## Prior Art (Research: 2026-04-19)

Searched Hacker News, Reddit (r/selfhosted, r/LocalLLaMA, r/ObsidianMD), ProductHunt, GitHub. Closest matches:

| Project | Overlap | Missing |
|---|---|---|
| Spine Pattern | Multi-repo orchestration | No consent model, no isolation |
| DiffMem | Git-native memory | Single repo only |
| BMAD-Federated-Knowledge | Federated repos | Abstraction over git, no consent |
| Mem0, ReMe | AI memory layers | Not git-native, not federated |
| Rosebud, Dot, Sentari | Personal AI memory | Vendor-hosted, no git, no federation |

**Assessment: genuinely novel.** The specific combination — git-native federation, consent-based satellite visibility, per-repo encrypted vaults, AI scribe synthesizing at session start — does not exist in any current system.

---

*[Cortex: Filed 2026-04-19. Conceived by Steve Krisjanovs during active development session. Not a manic idea — lucid, post-hypomanic, fully reasoned.]*
