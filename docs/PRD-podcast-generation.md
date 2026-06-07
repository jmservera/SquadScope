# PRD: Weekly Podcast Generation from SquadScope Articles

**Author:** Leela (Lead/Architect)  
**Date:** 2026-06-07  
**Status:** Accepted / amended after rubber-duck review for issue #299
**Type:** Product Requirements Document  
**Depends on:** content/methodology/_index.md, content/privacy/_index.md, docs/analysis-spec.md, docs/pipeline-validation.md, hugo.toml

---

## Executive Summary

SquadScope should add a weekly short-form podcast that turns each published weekly article into an 8-12 minute, two-host, scripted tech show. The recommended show is **SquadScope: Signal Check**: Host A is the Curator who explains the signal; Host B is the Skeptic who challenges hype, asks practical questions, and adds light jokes. The podcast should extend the article, not replace it, and it must keep SquadScope's evidence-first editorial standard.

The MVP recommendation is:

1. Generate a human-reviewed script from the already-published weekly article and its source-backed evidence.
2. Run the Phase 2 TTS proof of concept before full storage/RSS build-out: compare Azure Speech Standard neural voices, Azure Speech HD/OpenAI voices in Azure if available, and OpenAI `tts-1` or `gpt-4o-mini-tts`; choose the MVP provider from a documented listening test plus cost/privacy review.
3. Store MP3s, transcripts, show manifests, and RSS media metadata in **Azure Blob Storage**, which is designed for unstructured objects, streaming media, and HTTP(S) access (https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction).
4. Publish a podcast RSS feed at `/podcast/index.xml` and embed each episode in the matching weekly article only after gates pass.
5. Keep podcast generation in a separate non-blocking workflow, `podcast-generate.yml`, started by explicit dispatch from `crawl-and-publish.yml` only after a confirmed normal publish, plus manual dispatch for operators.

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
- Use low-cost, automatable TTS selected by an early Phase 2 listening-test comparison before storage/RSS implementation.
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
  -> GitHub Environment podcast-review approval
  -> final script
  -> TTS synthesis
  -> ffmpeg post-process
  -> upload audio/transcript/manifest to Blob Storage
  -> update podcast RSS
  -> embed episode in weekly article
```

### Required artifacts per episode

- `episode_manifest.json`: week, article URL, article hash, script prompt version, voice config hash, TTS provider, duration, file length, cost, license/disclosure status, publish status.
- `claim_ledger.json`: every substantive claim derived from the published article, source URL, article paragraph/source, validation status against existing analysis/publish artifacts where available, support status, and reviewer decision.
- `script.md`: final reviewed script.
- `transcript.txt` or `transcript.md`: public transcript generated from the final script.
- `show_notes.md`: article link, source URLs, AI disclosure, corrections link, sponsor/affiliate disclosures if any.
- `episode.mp3`: hosted in Blob Storage, not git.

If future implementation stores manifests under `data/`, `hugo.toml` must add explicit module mounts because this repo uses custom data mounts.


### Human review mechanism

MVP uses a single concrete review mechanism: the GitHub Environment `podcast-review` with required reviewers. `podcast-generate.yml` uploads the generated script package as workflow artifacts, then pauses before any non-dry-run TTS call by entering the `podcast-review` environment. TTS cannot proceed until the environment approval is granted. Reviewers inspect `script.md`, `claim_ledger.json`, `show_notes.md`, `transcript.md`, and `episode_manifest.json`, with attention to source support, disclosure, tone, privacy readiness, and budget status.


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
| Azure Speech Standard neural TTS | Mature SDK/REST, neural voices, SSML, batch synthesis, enterprise auth, billable characters (https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech) | Voice quality may be less expressive than newest generative voices | Include in Phase 2 POC |
| Azure Speech HD/OpenAI voices in Azure, if available | Higher-quality experiment path, Azure operational surface, OpenAI voices/formats with SSML differences (https://learn.microsoft.com/en-us/azure/ai-services/speech-service/openai-voices) | Availability/format differences; privacy/commercial terms must be confirmed | Include in Phase 2 POC |
| OpenAI `tts-1` or `gpt-4o-mini-tts` | Strong controllability and built-in voices; docs require disclosure that the voice is AI-generated (https://developers.openai.com/api/docs/guides/text-to-speech) | Another provider/privacy path; commercial terms must be reviewed | Include in Phase 2 POC |
| MAI Voice or other providers | Potential quality upside | Unknown licensing/availability/cost in this repo | Research later |
| Human narration | Best disclosure simplicity | Cost and cadence burden | Defer |

### Hosting options

| Option | Pros | Cons | Decision |
| --- | --- | --- | --- |
| Commit MP3s to git/Pages | Very simple URLs | Bloats repo; Pages limits; not CDN/business hosting (https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) | Reject |
| Azure Blob Storage | Designed for unstructured data, audio/video streaming, HTTP(S) access (https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) | Requires storage account/secrets/CORS/headers | **Select** |
| External podcast host | Turnkey analytics/distribution | Cost, lock-in, privacy review | Defer |
| CDN in front of Blob | Better scaling and stable public URLs | Extra configuration | Optional later; acceptable if URLs are stable |

---

## Technical Requirements

### Generation workflow

- Add a future separate workflow: `.github/workflows/podcast-generate.yml`.
- Trigger modes:
  - Preferred automated path: after `crawl-and-publish.yml` confirms a normal weekly publish, it explicitly dispatches `podcast-generate.yml` with the week, article path/URL, source run ID, publish mode, and article artifact identifiers.
  - `workflow_dispatch` with selected week and optional dry-run flag for operators.
- Do not rely on a naive `workflow_run` trigger. If a future implementation uses `workflow_run`, it must fetch and validate the triggering run inputs/artifacts and prove the run was a normal publish before synthesis.
- Dry-run, candidate-only, restore, failed, or no-AI fallback replacement runs must not synthesize audio or publish podcast artifacts.
- Podcast failures must not block article publishing.
- Manual reruns must be idempotent.

### Idempotency key

Episode generation identity is:

```text
week + article_hash + script_prompt_version + voice_config_hash
```

If the key is unchanged, reruns should reuse the existing reviewed script/audio unless explicitly forced. If the article changes materially, derive a new podcast claim ledger from the published article, validate those claims against available analysis/publish artifacts, and require review again.

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
- `enclosure` with stable public HTTPS URL, exact byte length, and `audio/mpeg` type.
- RFC 2822 publication date.
- ASCII-only filenames and URLs.
- Feed/image metadata ready for podcast directories.
- Validation that the audio endpoint supports `HEAD` and byte-range requests before publishing.
- Enclosure URLs must use public anonymous Blob read access or CDN-backed stable public URLs; expiring SAS URLs are explicitly prohibited for RSS enclosures.
- If MVP writes `static/podcast/index.xml`, it must not coexist ambiguously with a future Hugo `content/podcast/` section. If a Hugo podcast section is added, remove or replace static XML generation so only one feed owner exists.

### Hugo article embed

Weekly articles must use a Hugo `podcast-episode` shortcode/partial, not raw HTML. The embed renders the audio player, transcript link, show notes link, correction path, and AI-generated voice disclosure while leaving Hugo `unsafe = false` unchanged.

### Cost controls

Expected scripts are about 4,500-9,000 billable characters for 5-10 minutes, which keeps many TTS options at cents-level per episode, depending on provider, region, and free allowance. Operations must track total podcast cost, not just TTS: TTS, storage, egress/download bandwidth, script generation, validation, and any CDN charges. Egress may dominate if downloads grow.

MVP guardrails:

- Max 5 episodes per month.
- Max $5/month total podcast budget for TTS, storage, egress, script generation, validation, and CDN if used.
- Max 10 minutes per episode.
- Cost ledger entry per episode with per-category estimates/actuals.
- Workflow fails closed before non-dry-run synthesis or publish when limits would be exceeded.

---

## Safety, Legal, and Editorial Gates

### Hard launch gates

No public episode may ship unless all are true:

1. AI voice disclosure appears in the first 60 seconds and show notes. OpenAI's TTS guide explicitly requires clear disclosure that TTS voice is AI-generated and not human (https://developers.openai.com/api/docs/guides/text-to-speech).
2. Paid/commercial-use voice license is documented for the selected provider and voices.
3. No real-person voice cloning, no celebrity/podcast-host imitation, and no Hard Fork/NYT marks or copied expression.
4. MVP is voice-only: no music or SFX unless/until a licensed track/effect is selected and recorded in the manifest. Licensed music/SFX is a later issue with explicit acceptance criteria.
5. Human script review is complete through the GitHub Environment `podcast-review` gate before synthesis for MVP.
6. Claim ledger shows every factual claim is supported or removed.
7. Show notes include source URLs and corrections link.
8. No unsupported facts, no defamatory motive claims, and no fake sponsorship language.
9. Sponsorship/affiliate disclosures appear before any sponsor or affiliate segment.
10. Privacy policy is updated before any non-dry-run TTS call or before using podcast analytics, ad tech, or payment redirects.
11. GDPR/cookie consent covers non-essential podcast analytics before analytics tags or third-party players are enabled.

### FTC and monetization compliance

FTC endorsement guidance requires endorsements and ads to be honest, not misleading, and to disclose material connections clearly and conspicuously (https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking). Therefore:

- Sponsor segments must be labeled before the segment starts.
- Affiliate links must be disclosed near the link and in show notes.
- Hosts must not claim personal use or endorsement unless true.
- Sponsored influence must not affect repo selection/ranking unless the entire product strategy changes and is disclosed.

### Privacy requirements

Before Phase 2 performs any non-dry-run TTS call, update `content/privacy/_index.md` to document the selected voice-provider candidates and data flow. This privacy update is a prerequisite to Phase 2, not a launch cleanup item. Also update it before analytics, ad tech, or payment redirects are enabled to document:

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
- TTS provider selected after a Phase 2 listening-test POC.
- MP3 post-processing and Blob Storage hosting.
- Podcast RSS feed and weekly article embed.
- AI voice disclosure and correction path.
- Cost ledger and monthly budget guardrail covering TTS, storage, egress, script generation, validation, and CDN if used.
- Manual dispatch and post-publish workflow trigger.

### Out of scope for MVP

- Dynamic ad insertion.
- Premium/private feeds.
- Real-time/daily episodes.
- Multiple languages.
- Listener analytics beyond basic hosting logs, unless privacy/consent work is done.
- Fully automated publish without human review.
- Voice cloning or real-person mimicry.
- CDN optimization, unless needed for stable public enclosure URLs.

---

## Acceptance Criteria

### Product acceptance

- A reviewer can inspect the reviewed script artifact, claim ledger, show notes, transcript, manifest, and generated audio, then map every substantive factual claim to the published article and cited source/artifact validation.
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
- Cost ledger records provider, character count, duration, TTS/storage/egress/script-generation/validation/CDN estimated or actual costs, and monthly budget status.
- Secrets are not logged or committed.

### Safety acceptance

- Human reviewer approval is recorded via GitHub Environment `podcast-review` before synthesis; reviewers inspect `script.md`, `claim_ledger.json`, `show_notes.md`, `transcript.md`, and `episode_manifest.json` before allowing TTS.
- Provider voice license and AI disclosure are documented.
- No real-person voice cloning or protected podcast imitation occurs.
- Sponsorship/affiliate text, if present, is disclosed before the relevant segment.
- Privacy policy changes are merged before any non-dry-run TTS call and before production analytics/providers beyond current hosting are enabled.

---

## Implementation Phases

1. **Design and contracts:** Define manifest, claim ledger, show notes, RSS fields, storage naming, and review statuses.
2. **Script generation dry run:** Generate script/ledger/show notes from existing weekly articles without TTS or publishing.
3. **TTS proof of concept:** After the privacy update, synthesize reviewed private samples with Azure Speech Standard, Azure Speech HD/OpenAI voices in Azure if available, and OpenAI `tts-1` or `gpt-4o-mini-tts`; run a listening test and select the provider before full storage/RSS infrastructure.
4. **Audio hosting and RSS:** Upload approved MP3s to Blob Storage, generate `/podcast/index.xml`, and validate enclosures.
5. **Article embed:** Add a Hugo `podcast-episode` shortcode/partial so weekly articles can render audio player, transcript link, show notes, and AI disclosure while keeping `unsafe = false` unchanged.
6. **MVP launch:** Enable non-blocking post-publish podcast workflow with human review gate.
7. **Quality experiments:** Revisit voices, providers, music/SFX, and production polish after the Phase 2 provider decision and MVP reliability are proven.
8. **Monetization experiments:** Add support/donation links first; defer ads/premium until disclosure, privacy, and audience metrics justify them.

---

## Open Questions

- Which Azure region and Speech resource should be used for production?
- Which provider/voice pair wins the Phase 2 listening test while avoiding real-person mimicry?
- Which required reviewers should be configured on the GitHub Environment `podcast-review`?
- Should RSS stay as standalone `static/podcast/index.xml`, or should a future Hugo `content/podcast/` section replace static XML generation?
- What public podcast cover art should be used, and does it require a new design asset?
- What is the minimum listener metric needed before monetization moves beyond donations?

---

## Decision

Proceed with this amended docs-only design. For implementation, build **SquadScope: Signal Check** as a human-reviewed, source-backed, two-host weekly podcast using the GitHub Environment `podcast-review` gate, explicit post-publish dispatch from `crawl-and-publish.yml`, a Phase 2 TTS listening-test provider decision, stable public Blob/CDN enclosure URLs, a Hugo `podcast-episode` shortcode/partial, and strict disclosure/privacy/safety/cost gates. Defer analytics, ads, premium feeds, music/SFX, and full automation until the MVP proves reliable and trustworthy.
