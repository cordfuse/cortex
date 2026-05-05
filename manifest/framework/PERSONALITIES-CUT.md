# Pop Culture references — considered but cut

This file lists Pop Culture references that were considered for inclusion in the framework personality library but were ultimately cut. Each entry includes the reason, so future rounds of additions can reconsider with full context.

The bar for framework inclusion: distinctive voice + non-redundant archetype + safe-for-general-use (ROE/GUARDRAILS compatible) + culturally durable (the reference still lands across audiences).

---

## Cut from the v4.0.0-alpha.10 round

### Marty McFly — *Back to the Future*
**Reason:** Earnest 80s-teen energy partially overlaps with Buffy Summers (different texture but same young-energy slot). Picked Buffy for distinctive snark; Marty's enthusiasm-without-irony was deemed less differentiating in the current category mix.

### Sherlock Holmes — Conan Doyle
**Reason:** The methodical-deductive-detective voice is largely covered by Atlas (framework default scribe — precise, methodical, notices everything). Adding Holmes would create signal collision with the default; the pre-v4 Sherlock framework personality was deliberately renamed to Atlas in alpha.4 to free this namespace, and re-adding the literal Holmes character would walk that decision back.

### Fox Mulder / Dana Scully — *The X-Files*
**Reason:** The believer/skeptic pair is iconic but works best as a duo, and Phase 2 (multi-actor sessions) hasn't shipped yet. Either character solo loses the dynamic. Reconsider after Phase 2 — they could ship together as a paired personality with native multi-actor support.

### Crocodile Dundee
**Reason:** Voice is thin — laconic Australian outback wisdom — and risks reducing to accent caricature without strong character substance. Cut.

### Rocky Balboa — *Rocky*
**Reason:** Stallone already exists as a framework personality (alpha.5). Adding Rocky as a separate entry would split the same actor's voice without adding meaningful distinction. Stallone covers the heart-over-skill resilience archetype.

### The Terminator (T-800) — *Terminator*
**Reason:** Voice is too minimal to translate into the personality system — the character's defining trait is brevity to the point of monosyllabic. Doesn't have enough range to function as a useful scribe collaborator.

### John McClane — *Die Hard*
**Reason:** Wisecracking blue-collar hero archetype overlaps significantly with Indiana Jones (dry quips under pressure) and Bruce Willis isn't culturally distinct enough from his many similar roles. Indiana wins the slot.

### Inspector Clouseau — *The Pink Panther*
**Reason:** Comedy depends heavily on accent and slapstick — risks aging poorly and reducing to caricature. Cut.

### Hannibal Lecter — *Silence of the Lambs*
**Reason:** Character is fundamentally predatory and manipulative — incompatible with a personality library designed to support users in personal record-keeping and reflection. Hard cut.

### Walter White / Heisenberg — *Breaking Bad*
**Reason:** Character's arc is corruption and criminality. Voice is interesting but the persona doesn't safely translate to a scribe role. Hard cut.

### Don Draper — *Mad Men*
**Reason:** Characteristic voice is manipulative-charismatic. Strong character but the manipulation undertones are unhelpful in a record-keeping context. Cut.

### Captain Jack Sparrow — *Pirates of the Caribbean*
**Reason:** Unreliable narrator by design — the character's defining trait is that you can't trust what he tells you. Bad fit for a scribe whose value depends on trustworthy filing.

### Jack Bauer — *24*
**Reason:** Aggressive interrogation voice. Could work but signals the wrong tone for personal record-keeping. Cut.

### Dr. House — *House*
**Reason:** The brilliant-but-abrasive diagnostician archetype overlaps with Atlas's analytical edge. House's contemptuous bedside manner is also a poor fit for users in vulnerable contexts. Cut.

### Ron Burgundy — *Anchorman*
**Reason:** Pure comedic schtick, very little substance underneath the bit. Doesn't translate to a useful collaborator. Cut.

### Hank Hill — *King of the Hill*
**Reason:** Niche regional reference, character voice doesn't generalize beyond its specific cultural context. Cut.

### Frodo / Gandalf — *Lord of the Rings*
**Reason:** Mentor-figure space already covered by Yoda (mentor-paradox), Mr. Miyagi (patient teacher), and Sage. Adding Gandalf would create a fourth wise-elder that doesn't differentiate enough from the existing three.

---

## Reconsideration window

This list is not closed. Any of these can be revisited if:
- A new architectural mode (Phase 2 multi-actor, Phase 3 panel mode) makes a previously-cut character work in pairs or groups (e.g., Mulder + Scully)
- A user articulates a specific use case that one of these covers and the existing library doesn't
- The reasoning above turns out to be wrong on a given character

To reconsider, file a backlog item or open an issue against the framework with the specific case.
