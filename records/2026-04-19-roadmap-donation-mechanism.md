# 2026-04-19 — Roadmap: Donation Mechanism

## The Idea

Bake a donation mechanism directly into the Cortex session experience — not as a monetization play, but as a quiet advocate for mental health.

A custom verb `/donate` surfaces a link and a one-liner. No popup, no guilt, no pressure. Just there when you want it.

The donation goes to a specific mental health nonprofit — not to Cordfuse.

---

## Recipient

**CAMH Foundation** — Centre for Addiction and Mental Health, Toronto.
Canada's largest mental health teaching hospital and research centre.

camhfoundation.ca

Rationale: specific, reputable, Canadian, directly connected to the lived experience that motivated this app.

---

## Implementation

### `/donate` verb (VERBS.md default entry)

```markdown
## /donate
Surface the Cortex donation link — a one-liner about why it's there and a direct link to CAMH Foundation.
```

### README donation badge

Add a CAMH donation badge to the README header. Visible immediately. No friction.

### Why it belongs here

Cortex was built because personal health records — especially mental health records — disappear when you need them most. You re-explain your history to every new doctor, every new therapist, every new crisis worker. Every AI conversation starts from zero.

The people who need continuity most are the ones least likely to get it. This app is one small fix. The donation is acknowledgement that the bigger problem needs more than software.

---

## Version Target

**2.5.0** — small feature, high signal value. Ship before federation.

---

*[Cortex: Filed 2026-04-19. Conceived by Steve Krisjanovs.]*
