# PRD: Weekly Podcast Generation from SquadScope Articles

**Author:** Leela (Lead/Architect)  
**Date:** 2026-06-07  
**Status:** Draft for issue #297  
**Type:** Product Requirements Document  
**Depends on:** content/methodology/_index.md, content/privacy/_index.md, docs/analysis-spec.md, docs/pipeline-validation.md, hugo.toml

---

## Executive Summary

SquadScope should add a weekly short-form podcast that turns each published weekly article into an 8-12 minute, two-host, scripted tech show. The recommended show is **SquadScope: Signal Check**: Host A is the Curator who explains the signal; Host B is the Skeptic who challenges hype, asks practical questions, and adds light jokes. The podcast should extend the article, not replace it, and it must keep SquadScope's evidence-first editorial standard.

The MVP recommendation is:

1. Generate a human-reviewed script from the already-published weekly article and its source-backed evidence.
2. Use **Azure AI Speech neural TTS** for synthesis by default because SquadScope already expects Azure-friendly operations, Azure Speech supports neural voices, SSML, batch synthesis, and billable-character pricing (https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech).
3. Store MP3s, transcripts, show manifests, and RSS media metadata in **Azure Blob Storage**, which is designed for unstructured objects, streaming media, and HTTP(S) access (https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction).
4. Publish a podcast RSS feed at `/podcast/index.xml` and embed each episode in the matching weekly article only after gates pass.
5. Keep podcast generation in a separate non-blocking workflow, `podcast-generate.yml`, triggered after weekly article publishing and by manual dispatch.

Do **not** commit MP3s to git. GitHub Pages has 1 GB site/repository guidance, a 100 GB monthly soft bandwidth limit, and is not intended as free business or CDN hosting (https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits). Pages can host the RSS XML and player pages; object storage should host audio.

---

## Problem Statement

SquadScope publishes weekly AI-assisted articles from GitHub and press signals. Readers who commute, exercise, or skim while working may prefer audio, but a plain article readout would be low-value. The opportunity is to create a short, dynamic, funny, source-backed podcast that makes the weekly trend analysis more approachable without weakening evidence quality.

The risks are real:

- Audio can make unsupported claims sound more authoritative than text.
- Jokes can distort nuance or target individuals unfairly.
- Synthetic voices require clear disclosure and licensing discipline.
- Podcast RSS clients require strict feed/enclosure behavior.
- Audio binaries can bloat the repository and exceed Pages' intended hosting model.
- Monetization adds FTC disclosure, privacy, and trust obligations.

This PRD defines the recommended editorial format, technical path, safety gates, monetization approach, and phased implementation plan.

---

## Goals and Non-Goals

### Goals

- Convert each published weekly article into one short podcast episode.
- Make episodes useful and entertaining: dynamic, conversational, lightly funny, and technically grounded.
- Preserve SquadScope's source-backed methodology, correction path, and no-paid-placement editorial stance unless explicitly changed and disclosed.
- Require a claim ledger, source-backed show notes, and human review for the MVP.
- Use low-cost, automatable TTS with future quality experiments isolated from MVP reliability.
- Publish standards-compliant podcast RSS with stable episode identity.
- Avoid blocking weekly article publishing when podcast generation fails.
- Define safe monetization phases that protect reader/listener trust.

### Non-Goals

- Implementing code, workflows, templates, storage, or RSS generation in this issue.
- Replacing the written weekly article.
- Creating a daily show, long-form interview show, or news desk.
- Cloning or imitating real people, Hard Fork hosts, NYT marks, jingles, segment names, or protected expression.
- Committing MP3s or other generated audio binaries to git.
- Launching paid ads, dynamic ad insertion, premium feeds, or analytics before privacy and disclosure work is complete.

---

## Audience and Use Cases

| Audience | Need | Podcast value |
| --- | --- | --- |
| Busy developers | Understand what mattered this week without reading the whole article | 10-minute signal summary with source-backed examples |
| Tech leads | Separate real adoption from hype | Skeptic host challenges weak claims and asks impact questions |
| Open-source maintainers | Hear where their ecosystem sits in broader momentum | Contextualized trends, not just rankings |
| Sponsors/supporters later | Reach a niche technical audience | Clear disclosed sponsorship only after trust phase |

Primary listener job: "Tell me what changed in open-source and developer tools this week, what is hype, what is real, and what I should watch next."

---

## Editorial Product Recommendation

### Show

**Name:** SquadScope: Signal Check  
**Length:** 8-12 minutes overall; MVP automated runs target 8-10 minutes  
**Script length:** about 1,200-1,700 words  
**Format:** two-host scripted banter  
**Tone:** sharp, curious, evidence-first, lightly funny  
**Disclosure:** AI-generated voices in the first 60 seconds and in show notes

### Host roles

- **Host A, Curator:** Explains the signal, gives context, cites evidence, keeps the episode moving.
- **Host B, Skeptic:** Challenges hype, asks "so what?", surfaces caveats, and adds jokes that compress analysis.

Jokes should punch up at hype cycles, dashboard theater, benchmark theater, and vague launch language. They should not punch down at individuals, imply motives, mock protected classes, or turn uncertainty into fact.

### Segment structure

1. **Cold open:** One quick hook plus AI voice disclosure.
2. **The Signal:** The most important repo/ecosystem movement from the article.
3. **The Noise Check:** What sounds exciting but may be over-claimed.
4. **The Gap:** Press narrative versus GitHub/developer evidence.
5. **Receipts Round:** Fast source-backed facts, with show-note citations.
6. **Week Ahead:** What to watch next week.
7. **Outro:** Correction path, article link, and disclosure reminder.

### Similarity guardrail

The show may use broad conversational tech-podcast energy, but it must not copy Hard Fork/NYT names, segment labels, jingles, host identities, recurring bits, phrasing, or trade dress. "Signal Check" and the segments above are SquadScope-specific.

---

## Article-to-Episode Workflow

```text
published weekly article
  -> claim and source extraction
  -> claim ledger
  -> episode outline
  -> two-host conversational script
  -> citation and fact check
  -> editorial/safety review
  -> final script
  -> TTS synthesis
  -> ffmpeg post-process
  -> upload audio/transcript/manifest to Blob Storage
  -> update podcast RSS
  -> embed episode in weekly article
```

### Required artifacts per episode

- `episode_manifest.json`: week, article URL, article hash, script prompt version, voice config hash, TTS provider, duration, file length, cost, license/disclosure status, publish status.
- `claim_ledger.json`: every substantive claim, source URL, article paragraph/source, support status, and reviewer decision.
- `script.md`: final reviewed script.
- `transcript.txt` or `transcript.md`: public transcript generated from the final script.
- `show_notes.md`: article link, source URLs, AI disclosure, corrections link, sponsor/affiliate disclosures if any.
- `episode.mp3`: hosted in Blob Storage, not git.

If future implementation stores manifests under `data/`, `hugo.toml` must add explicit module mounts because this repo uses custom data mounts.

---

## Options Considered

### Editorial format options

| Option | Pros | Cons | Decision |
| --- | --- | --- | --- |
| Single-host article readout | Simplest, cheapest, lowest editorial transformation | Boring; weak differentiation; less funny | Reject for MVP |
| Two-host scripted show | Dynamic, clear roles, good for hype checks and jokes | Requires stronger script review | **Select** |
| Fully improvised AI hosts | Fast, possibly lively | High risk of unsupported claims, inconsistent tone | Reject |
| Human-recorded show | Highest authenticity | More operational burden; harder weekly cadence | Defer |

### TTS provider options

| Option | Pros | Cons | Decision |
| --- | --- | --- | --- |
| Azure AI Speech neural TTS | Mature SDK/REST, neural voices, SSML, batch synthesis, enterprise auth, billable characters (https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech) | Voice quality may be less expressive than newest generative voices | **Default MVP** |
| Azure OpenAI voices via Azure Speech | Higher-quality experiment path, Azure operational surface, OpenAI voices/formats with SSML differences (https://learn.microsoft.com/en-us/azure/ai-services/speech-service/openai-voices) | Availability/format differences; should not block MVP | Experiment after MVP |
| OpenAI `gpt-4o-mini-tts` | Strong controllability and built-in voices; docs require disclosure that the voice is AI-generated (https://developers.openai.com/api/docs/guides/text-to-speech) | Another provider/privacy path; commercial terms must be reviewed | Experiment after MVP |
| MAI Voice or other providers | Potential quality upside | Unknown licensing/availability/cost in this repo | Research later |
| Human narration | Best disclosure simplicity | Cost and cadence burden | Defer |

### Hosting options

| Option | Pros | Cons | Decision |
| --- | --- | --- | --- |
| Commit MP3s to git/Pages | Very simple URLs | Bloats repo; Pages limits; not CDN/business hosting (https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) | Reject |
| Azure Blob Storage | Designed for unstructured data, audio/video streaming, HTTP(S) access (https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) | Requires storage account/secrets/CORS/headers | **Select** |
| External podcast host | Turnkey analytics/distribution | Cost, lock-in, privacy review | Defer |
| CDN in front of Blob | Better scaling | Not needed for MVP | Optional later |

---

## Technical Requirements

### Generation workflow

- Add a future separate workflow: `.github/workflows/podcast-generate.yml`.
- Trigger modes:
  - `workflow_run` after successful weekly article publish.
  - `workflow_dispatch` with selected week and optional dry-run flag.
- Podcast failures must not block article publishing.
- Manual reruns must be idempotent.

### Idempotency key

Episode generation identity is:

```text
week + article_hash + script_prompt_version + voice_config_hash
```

If the key is unchanged, reruns should reuse the existing reviewed script/audio unless explicitly forced. If the article changes materially, regenerate the claim ledger and require review again.

### Audio requirements

- Format: MP3.
- MIME type: `audio/mpeg`.
- Channels: mono.
- Sample rate: 44.1 kHz.
- Bitrate: 64-96 kbps.
- Duration: max 10 minutes for MVP unless manually approved.
- Size: target under 10 MB.
- Loudness: normalize around -16 LUFS.
- Post-processing: use `ffmpeg` for normalization, metadata, and deterministic output checks.

### RSS requirements

Apple's podcast requirements include RSS 2.0, a public feed, correct enclosure URL/length/type, stable GUIDs, RFC 2822 `pubDate`, ASCII URLs, and server support for HEAD and byte-range requests (https://podcasters.apple.com/support/823-podcast-requirements). MVP RSS must include:

- `/podcast/index.xml` generated from manifests.
- One stable GUID per episode.
- `enclosure` with public HTTPS URL, exact byte length, and `audio/mpeg` type.
- RFC 2822 publication date.
- ASCII-only filenames and URLs.
- Feed/image metadata ready for podcast directories.
- Validation that the audio endpoint supports `HEAD` and byte-range requests before publishing.

### Cost controls

Expected scripts are about 4,500-9,000 billable characters for 5-10 minutes, which keeps Azure Speech neural TTS and likely OpenAI/Azure OpenAI mini TTS at cents-level per episode, depending on provider, region, and free allowance. Annual weekly TTS should likely stay under $10, but operations must track actual costs.

MVP guardrails:

- Max 5 episodes per month.
- Max $5/month TTS budget.
- Max 10 minutes per episode.
- Cost ledger entry per episode.
- Workflow fails closed before synthesis when limits would be exceeded.

---

## Safety, Legal, and Editorial Gates

### Hard launch gates

No public episode may ship unless all are true:

1. AI voice disclosure appears in the first 60 seconds and show notes. OpenAI's TTS guide explicitly requires clear disclosure that TTS voice is AI-generated and not human (https://developers.openai.com/api/docs/guides/text-to-speech).
2. Paid/commercial-use voice license is documented for the selected provider and voices.
3. No real-person voice cloning, no celebrity/podcast-host imitation, and no Hard Fork/NYT marks or copied expression.
4. Music/SFX are absent or licensed for commercial podcast use, with license recorded.
5. Human script review is complete before synthesis for MVP.
6. Claim ledger shows every factual claim is supported or removed.
7. Show notes include source URLs and corrections link.
8. No unsupported facts, no defamatory motive claims, and no fake sponsorship language.
9. Sponsorship/affiliate disclosures appear before any sponsor or affiliate segment.
10. Privacy policy is updated before using voice providers, podcast analytics, ad tech, or payment redirects.
11. GDPR/cookie consent covers non-essential podcast analytics before analytics tags or third-party players are enabled.

### FTC and monetization compliance

FTC endorsement guidance requires endorsements and ads to be honest, not misleading, and to disclose material connections clearly and conspicuously (https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking). Therefore:

- Sponsor segments must be labeled before the segment starts.
- Affiliate links must be disclosed near the link and in show notes.
- Hosts must not claim personal use or endorsement unless true.
- Sponsored influence must not affect repo selection/ranking unless the entire product strategy changes and is disclosed.

### Privacy requirements

Before launch with production providers, update `content/privacy/_index.md` to document:

- Voice provider(s), data sent, retention, and region if configurable.
- Audio hosting provider and logs.
- Podcast analytics vendors, if any.
- Whether IP/user-agent data is processed by embedded players.
- Payment processors for donations/premium offerings.

SquadScope should not store payment data. Use Stripe, PayPal, Ko-fi, Patreon, or similar redirects if monetization needs payment handling.

---

## Monetization Roadmap

### Phase 1: Audience and trust

- Keep episodes free.
- Add Ko-fi/Patreon/support links only after privacy copy is updated.
- Consider newsletter sponsorship if clearly disclosed.
- Allow affiliate links only when directly relevant and disclosed.
- No dynamic ad insertion.

### Phase 2: Ads with controls

- Add host-read sponsor spots or dynamic ad insertion only after listener traction, privacy review, and disclosure templates exist.
- Website ads require cookie/consent review before activation.
- Maintain a sponsor policy: no paid influence over article ranking or episode claims.

### Phase 3: Premium and events

- Premium feed, sponsored deep dives, or live events can be explored after the core feed has reliable cadence and listener metrics.
- Premium feeds require authentication/payment provider design and privacy review.

---

## MVP Scope

### In scope

- One episode per weekly article.
- Two-host script generated from article plus existing evidence artifacts.
- Claim ledger and source-backed show notes.
- Human review before synthesis.
- Azure AI Speech neural TTS.
- MP3 post-processing and Blob Storage hosting.
- Podcast RSS feed and weekly article embed.
- AI voice disclosure and correction path.
- Cost ledger and monthly budget guardrail.
- Manual dispatch and post-publish workflow trigger.

### Out of scope for MVP

- Dynamic ad insertion.
- Premium/private feeds.
- Real-time/daily episodes.
- Multiple languages.
- Listener analytics beyond basic hosting logs, unless privacy/consent work is done.
- Fully automated publish without human review.
- Voice cloning or real-person mimicry.
- CDN optimization.

---

## Acceptance Criteria

### Product acceptance

- A reviewer can listen to a generated episode and map every substantive factual claim to the article, claim ledger, or cited source.
- Episode length fits the 8-12 minute show format, and automated MVP runs are no more than 10 minutes unless manually overridden.
- The show sounds distinct from copied podcasts and uses the approved `Signal Check` structure.
- Jokes clarify or compress analysis without adding unsupported claims or targeting individuals unfairly.
- AI voice disclosure is audible in the first 60 seconds and visible in show notes.
- Corrections path is present in show notes and article embed.

### Technical acceptance

- Podcast workflow can be rerun for a selected week without duplicate episodes.
- Article publishing succeeds even if podcast generation fails.
- MP3 is hosted outside git, under the size/duration/audio constraints.
- RSS validates against Apple-style requirements: public RSS 2.0, stable GUID, enclosure URL/length/type, RFC 2822 date, ASCII URL, HEAD and byte-range support (https://podcasters.apple.com/support/823-podcast-requirements).
- Cost ledger records provider, character count, duration, estimated/actual cost, and monthly budget status.
- Secrets are not logged or committed.

### Safety acceptance

- Human reviewer approval is recorded before synthesis.
- Provider voice license and AI disclosure are documented.
- No real-person voice cloning or protected podcast imitation occurs.
- Sponsorship/affiliate text, if present, is disclosed before the relevant segment.
- Privacy policy changes are merged before production analytics/providers beyond current hosting are enabled.

---

## Implementation Phases

1. **Design and contracts:** Define manifest, claim ledger, show notes, RSS fields, storage naming, and review statuses.
2. **Script generation dry run:** Generate script/ledger/show notes from existing weekly articles without TTS or publishing.
3. **TTS proof of concept:** Synthesize reviewed scripts with Azure Speech in a private artifact path; measure cost, duration, and quality.
4. **Audio hosting and RSS:** Upload approved MP3s to Blob Storage, generate `/podcast/index.xml`, and validate enclosures.
5. **Article embed:** Add a Hugo partial/shortcode or content data path to embed the latest episode on weekly articles.
6. **MVP launch:** Enable non-blocking post-publish podcast workflow with human review gate.
7. **Quality experiments:** Compare Azure OpenAI/OpenAI `gpt-4o-mini-tts` or MAI Voice against Azure Speech after MVP reliability is proven.
8. **Monetization experiments:** Add support/donation links first; defer ads/premium until disclosure, privacy, and audience metrics justify them.

---

## Open Questions

- Which Azure region and Speech resource should be used for production?
- Which two neural voices best represent Curator and Skeptic while avoiding real-person mimicry?
- Should script review happen through a GitHub PR, issue checklist, environment approval, or repository artifact approval file?
- Should RSS be generated by Hugo from data files or by a standalone script that writes static XML?
- What public podcast cover art should be used, and does it require a new design asset?
- What is the minimum listener metric needed before monetization moves beyond donations?

---

## Decision

Proceed with a docs-only design now. For implementation, build **SquadScope: Signal Check** as a human-reviewed, source-backed, two-host weekly podcast using Azure AI Speech neural TTS by default, Blob Storage for audio, a separate non-blocking generation workflow, and strict disclosure/safety/cost gates. Defer higher-quality TTS experiments, analytics, ads, premium feeds, and full automation until the MVP proves reliable and trustworthy.
