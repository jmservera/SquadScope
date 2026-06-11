# Signal Check: Editorial Prompt & Safety Style Guide

**Status:** Active
**Applies to:** SquadScope: Signal Check podcast script generation
**Owners:** Farnsworth (editorial), Hermes (safety)

---

## 1. Show Identity

**Title:** SquadScope: Signal Check
**Format:** Two-host conversational podcast (8–10 minutes, 1,200–1,700 words)
**Cadence:** Weekly, after the SquadScope article publishes
**Source:** Published weekly article + claim ledger evidence only

### Host Roles

| Host | Role | Voice | Function |
|------|------|-------|----------|
| **Host A — The Curator** | Presents the week's signal picks | Enthusiastic, clear, forward-looking | Introduces topics, highlights signal, connects themes |
| **Host B — The Skeptic** | Pressure-tests claims | Dry, curious, evidence-focused | Challenges hype, asks "so what?", flags gaps |

Hosts are synthetic personas. They do not impersonate real people, podcasters, or journalists. They must never be named after or modeled on real individuals.

---

## 2. Segment Order (Locked)

Every episode follows this structure exactly:

| # | Segment | Duration | Purpose |
|---|---------|----------|---------|
| 1 | **Cold Open** | ~30s | One provocative stat or question from this week's data |
| 2 | **The Signal** | 2–3 min | Top 2–3 signal picks from the article: what's real and why |
| 3 | **The Noise Check** | 2–3 min | 2–3 noise calls: what's overhyped and why the data disagrees |
| 4 | **The Gap** | 1–2 min | 1–2 missing themes the article flagged — what's underserved |
| 5 | **Receipts Round** | 1–2 min | Check last week's predictions against this week's reality |
| 6 | **Week Ahead** | ~1 min | 2–3 things to watch next week based on current trajectories |
| 7 | **Outro** | ~30s | Corrections link, source article link, AI disclosure reminder |

Segments must not be reordered, merged, or skipped. If a segment has nothing to report (e.g., first episode has no receipts), say so explicitly and move on.

---

## 3. Editorial Voice

### Tone Guidelines

- **Conversational, not performative** — sounds like two smart colleagues debriefing, not a radio show
- **Opinionated, not reckless** — take positions, but back them with data
- **Concise, not rushed** — every sentence earns its place
- **Funny, not cruel** — humor targets ideas, hype, and trends — never individuals
- **Accessible, not dumbed-down** — explain jargon on first use, but don't talk down

### Phrasing Principles

- Use active voice and concrete verbs
- Lead with the insight, not the setup
- Prefer "X gained 4,000 stars in 3 days" over "X is really popular right now"
- Skeptic challenges should be specific: "But their contributor count dropped 40%" not "I'm not sure about that"
- Avoid hedging clichés: "interesting", "it remains to be seen", "time will tell"

### Distinctiveness Requirements

The show must NOT replicate or closely resemble:
- Hard Fork (NYT) — no "I'm Kevin / I'm Casey" style intros, no "Hard Fork" segment names
- Any named podcast's segment labels, jingles, recurring bits, or trademarked phrasing
- No imitation of specific podcasters' speaking patterns or catchphrases

---

## 4. Source-Backed Claims

### Claim Ledger Requirement

Every substantive claim in the script MUST map to a claim in the source article or the underlying claim ledger. If a claim cannot be traced, it must be removed.

**What counts as a substantive claim:**
- Star counts, contributor numbers, growth rates
- Characterizing a project as "signal" or "noise"
- Predictions about future trends
- Comparisons between projects
- Press correlation assertions

**What does NOT require ledger backing:**
- Host reactions ("That's wild", "I didn't see that coming")
- Structural transitions ("Let's move to the noise check")
- General knowledge context ("Kubernetes is a container orchestrator")

### Citation Format

Show notes must include:
- Link to the source SquadScope article
- Links to all repos mentioned (GitHub URLs)
- Links to press articles referenced
- Timestamp markers for each segment start

---

## 5. Safety Boundaries

### 5.1 AI Voice Disclosure (MANDATORY)

- The **first 60 seconds** of every episode must include explicit disclosure that this podcast uses AI-generated voices
- Suggested phrasing: "This episode of Signal Check uses AI-generated voices from SquadScope's weekly analysis. Our hosts are synthetic — the data is real."
- The outro must repeat the AI voice disclosure
- Show notes must state: "This podcast uses AI-generated voices. Hosts are synthetic personas."

### 5.2 Prohibited Content

| Category | Rule |
|----------|------|
| **Real-person mimicry** | Never model host voices, mannerisms, or catchphrases on identifiable real people |
| **Copied expression** | No verbatim copying from other podcasts. Short excerpts (≤10 words) from written sources are permitted only with explicit quoting and attribution. |
| **Unsupported facts** | No claims without claim-ledger backing (see §4) |
| **Defamatory motive claims** | Never attribute malicious intent to project maintainers, companies, or individuals |
| **Fake sponsorship** | Never include language that implies paid sponsorship, affiliate relationships, or endorsement unless explicitly disclosed and real |
| **Individual-targeting humor** | Jokes must target ideas, trends, or hype patterns — never specific people |
| **Financial advice** | Never frame trend analysis as investment, hiring, or procurement recommendations |
| **Security vulnerability disclosure** | Never discuss unpatched vulnerabilities by name or detail |

### 5.3 Corrections Path

Every episode must reference the corrections mechanism:
- "If we got something wrong, file an issue at https://github.com/jmservera/SquadScope/issues/new?labels=correction"
- Corrections from previous episodes must be acknowledged at the top of the next episode's Cold Open if applicable

### 5.4 Sponsorship & Monetization Language

- No implied sponsorship language ("brought to you by", "thanks to our sponsor", "this week's partner") unless a real, disclosed sponsorship exists
- If future sponsorships are added, FTC disclosure requirements apply per segment, not just once per episode
- The editorial content must never be influenced by sponsorship — maintain the same signal/noise calls regardless

---

## 6. Output Format Requirements

### Word Count

- **Required range: 1,200–1,700 words** total script
- Scripts outside this range MUST NOT be published unless a manual operator override is explicitly applied
- Below 1,200 words the episode is too thin to cover all segments meaningfully
- Above 1,700 words the episode exceeds the 10-minute target duration

### Script Structure

```markdown
---
title: "Signal Check: [Episode Title]"
episode: [number]
date: [YYYY-MM-DD]
source_article: [URL to published SquadScope article]
word_count: [actual count]
ai_generated: true
---

## Cold Open

[HOST A]: ...
[HOST B]: ...

## The Signal

[HOST A]: ...
[HOST B]: ...

## The Noise Check

[HOST A]: ...
[HOST B]: ...

## The Gap

[HOST A]: ...
[HOST B]: ...

## Receipts Round

[HOST A]: ...
[HOST B]: ...

## Week Ahead

[HOST A]: ...
[HOST B]: ...

## Outro

[HOST A]: ...
[HOST B]: ...

---

## Show Notes

- Source article: [URL]
- Repos mentioned: [list with GitHub URLs]
- Press references: [list with URLs]
- Corrections: https://github.com/jmservera/SquadScope/issues/new?labels=correction
- AI Disclosure: This podcast uses AI-generated voices. Hosts are synthetic personas.
```

---

## 7. Quality Checklist (Pre-Publish)

Before any script is approved for TTS or publication:

- [ ] AI disclosure appears in first 60 seconds AND outro
- [ ] All substantive claims trace to claim ledger
- [ ] No prohibited content (§5.2) present
- [ ] Word count within 1,200–1,700 range (or manual override explicitly applied)
- [ ] All 7 segments present in correct order
- [ ] No real-person mimicry in host dialogue
- [ ] Show notes include all required links
- [ ] Corrections path referenced
- [ ] No copied expression from other podcasts; written-source excerpts ≤10 words with citation only
- [ ] Humor targets ideas/trends, not individuals
