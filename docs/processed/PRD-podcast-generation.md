# PRD: Weekly Podcast Generation from SquadScope Articles

**Author:** Leela (Lead/Architect)
**Date:** 2026-06-07
**Status:** Accepted / amended for issue #310 platform-podcast scope. Archived 2026-06-10 — remaining execution work is tracked by issue #355 and its linked issues (#335–#350); this document is retained as the reference PRD.
**Type:** Product Requirements Document
**Depends on:** content/methodology/_index.md, content/privacy/_index.md, docs/analysis-spec.md, docs/pipeline-validation.md
**Companion plan:** `docs/processed/podcast-generation-plan.md`

---

## Executive Summary

SquadScope should enable **SquadScope: Signal Check**, an 8-12 minute weekly two-host podcast generated from the already-published weekly article. The podcast/Podcaster capability is a **sister product/tool**, not a SquadScope website feature. It should be distributed through Spotify and/or a podcast platform, not hosted inside the SquadScope website. The website MVP only adds a configurable link to the external podcast page once that page exists.

The MVP recommendation is:

1. Generate a human-reviewed script, transcript, show notes, and publishing packet from the published weekly article and its source-backed evidence.
2. Run the Phase 2 TTS proof of concept before production synthesis: compare Azure Speech Standard neural voices, Azure Speech HD/OpenAI voices in Azure if available, and OpenAI `tts-1` or `gpt-4o-mini-tts`; choose the MVP provider from a documented listening test plus cost/privacy review.
3. Store generated MP3s and working artifacts temporarily in **Azure Blob Storage** as staging storage with retention and cleanup controls. Blob Storage is not the final public podcast host for MVP unless a later delivery decision explicitly approves it.
4. Prepare a manual Spotify publishing packet for the operator: MP3, title, description, transcript/show notes, AI disclosure, sponsor/affiliate disclosures if any, source article URL, and corrections link.
5. Investigate whether Spotify supports episode upload/publish automation. Initial documentation research suggests the Spotify Web API is primarily for streaming-service interactions such as metadata, playlists, playback, and user library operations, not clearly for podcast episode upload; this must be verified against Spotify for Creators and current podcast delivery docs.
6. Keep SquadScope's publishing path unchanged. Any temporary workflow in this repo may only be manually invoked or emit/consume post-publish artifacts after normal publishing is complete; the production podcast generation workflow should live in the separate Podcaster project once the project boundary is defined.

Do **not** commit MP3s to git. Do **not** build website-hosted podcast pages, audio players, article audio embeds, or a site-owned feed as MVP scope; those website-hosted consumption patterns are explicitly deferred/non-MVP. If an RSS feed exists during MVP, it is for podcast-platform ingestion or a future podcast host migration, not for SquadScope website consumption.

---

## Problem Statement

SquadScope publishes weekly AI-assisted articles from GitHub and press signals. Some users may prefer an audio product they can follow in their podcast app. A plain article readout would be low-value; the opportunity is to create a short, dynamic, funny, source-backed podcast that makes the weekly trend analysis more approachable without weakening evidence quality.

The clarified product scope changes delivery:

- The podcast is not hosted in the same SquadScope website.
- Spotify or another podcast platform is the launch destination.
- Initial Spotify publishing is manual.
- Automation feasibility must be researched before promising automatic publish.
- The website only links out to the external podcast/platform page.
- The current weekly crawl/analyze/generate/deploy publishing process must not be modified, gated, delayed, or made dependent on podcast generation.

Key risks:

- Audio can make unsupported claims sound more authoritative than text.
- Jokes can distort nuance or target individuals unfairly.
- Synthetic voices require clear disclosure and licensing discipline.
- Platform publishing workflows may require manual steps or third-party hosting APIs.
- Azure podcast resources belong to the future Podcaster project, not the SquadScope publishing runtime, unless a later architecture decision explicitly says otherwise.
- Temporary audio artifacts need retention, cleanup, and access controls.
- Monetization adds FTC disclosure, privacy, and trust obligations for both podcast and website.

---

## Goals and Non-Goals

### Goals

- Convert each published weekly article into one short podcast episode.
- Treat Podcaster as a separate sister product/tool with Spotify/podcast-platform publishing as the target.
- Preserve SquadScope's source-backed methodology, correction path, and no-paid-placement editorial stance unless explicitly changed and disclosed.
- Require a claim ledger, source-backed show notes, publishing packet, and human review for MVP.
- Use low-cost, automatable TTS selected by an early listening-test comparison.
- Store generated audio temporarily in Azure Blob Storage with retention and cleanup.
- Support manual Spotify publishing first, then research and design automation if available.
- Limit website integration to a configurable external podcast link.
- Preserve zero impact on existing weekly crawl/analyze/generate/deploy behavior.
- Define safe monetization phases for podcast and website.

### Non-Goals

- Implementing code, workflows, templates, storage, publishing integrations, Azure infrastructure, or RSS generation in this issue.
- Hosting the podcast inside the SquadScope website.
- Website-hosted audio players, article audio embeds, Hugo podcast shortcodes, or podcast landing/player pages are non-MVP/deferred.
- Publishing a SquadScope-site-owned `/podcast/index.xml` feed for listener consumption is non-MVP/deferred.
- Replacing the written weekly article.
- Creating a daily show, long-form interview show, or news desk.
- Cloning or imitating real people, Hard Fork hosts, NYT marks, jingles, segment names, or protected expression.
- Committing MP3s or other generated audio binaries to git.
- Launching paid ads, dynamic ad insertion, premium feeds, or analytics before privacy and disclosure work is complete.
- Changing the current weekly crawl/analyze/generate/deploy pipeline, publish manifests, article publishing gates, or critical-path behavior for podcast needs.

---

## Audience and Use Cases

| Audience | Need | Podcast value |
| --- | --- | --- |
| Busy developers | Understand what mattered this week without reading the whole article | 10-minute signal summary with source-backed examples |
| Tech leads | Separate real adoption from hype | Skeptic host challenges weak claims and asks impact questions |
| Open-source maintainers | Hear where their ecosystem sits in broader momentum | Contextualized trends, not just rankings |
| Sponsors/supporters later | Reach a niche technical audience | Clear disclosed support/sponsorship only after trust phase |

Primary listener job: "Tell me what changed in open-source and developer tools this week, what is hype, what is real, and what I should watch next."

---

## Editorial Product Recommendation

### Show

**Name:** SquadScope: Signal Check
**Length:** 8-12 minutes overall; MVP automated runs target 8-10 minutes
**Script length:** about 1,200-1,700 words
**Format:** two-host scripted banter
**Tone:** sharp, curious, evidence-first, lightly funny
**Disclosure:** AI-generated voices in the first 60 seconds and in show notes/publishing description

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
7. **Outro:** Correction path, article link, external podcast follow prompt, and disclosure reminder.

### Similarity guardrail

The show may use broad conversational tech-podcast energy, but it must not copy Hard Fork/NYT names, segment labels, jingles, host identities, recurring bits, phrasing, or trade dress. "Signal Check" and the segments above are SquadScope-specific.

---

### Product boundary

Podcaster is a sister product/tool that consumes SquadScope outputs; it is not a SquadScope website feature. SquadScope remains responsible for publishing the weekly article and, at most, exposing stable post-publish artifacts such as article URL, article content, source artifact references, or a manifest. Podcaster is responsible for script generation, TTS, audio staging, platform publishing packets, Azure resources, podcast operations, and any future podcast workflow once separated.

### Zero-impact publishing principle

Podcast work must have zero impact on existing publishing:

- No changes to the current weekly crawl/analyze/generate/deploy behavior.
- No gating, delaying, rolling back, or replacing article publishing because of podcast generation.
- No changes to existing publish manifests for podcast-only metadata unless a separate backward-compatible contract is approved.
- No audio generation, TTS provider calls, Blob uploads, or podcast validation inside the article publishing critical path.
- No requirement that podcast artifacts exist before an article is considered published.
- Any future SquadScope workflow may only emit a post-publish event/artifact or be manually invoked; the podcast generation workflow should live in Podcaster once the project is separated.

---

## Article-to-Episode Workflow

```text
SquadScope normal weekly publish completes unchanged
  -> SquadScope exports stable post-publish article URL/content/artifact manifest
  -> Podcaster consumes the artifact asynchronously or via manual invocation
  -> Podcaster performs claim and source extraction
  -> Podcaster creates claim ledger, outline, two-host script, show notes, transcript, and publishing packet
  -> Podcaster review gate approves script package
  -> Podcaster performs TTS synthesis and ffmpeg post-process outside SquadScope critical path
  -> Podcaster uploads MP3/transcript/manifest to its temporary Azure Blob staging
  -> operator manually publishes to Spotify or selected podcast platform
  -> SquadScope website external podcast link is updated only when a platform page exists
```

### Required artifacts per episode

- `episode_manifest.json`: week, article URL, article/content/artifact manifest reference, article hash, script prompt version, voice config hash, TTS provider, duration, file length, cost, license/disclosure status, staging storage URI, retention expiry, reviewer, and publish status.
- `claim_ledger.json`: every substantive claim derived from the published article, source URL, article paragraph/source, validation status against existing analysis/publish artifacts where available, support status, and reviewer decision.
- `script.md`: final reviewed script.
- `transcript.txt` or `transcript.md`: transcript generated from the final script.
- `show_notes.md`: article link, source URLs, AI disclosure, corrections link, sponsor/affiliate disclosures if any.
- `publishing_packet.md` or equivalent operator summary: MP3 path, title, description, transcript/show notes, disclosures, source article URL, corrections link, and manual publish checklist.
- `episode.mp3`: temporary staging artifact in Azure Blob Storage, not git.

If a temporary prototype stores docs or sample manifests under `data/`, `hugo.toml` must add explicit module mounts because this repo uses custom data mounts. Production podcast manifests should belong to Podcaster or the selected podcast platform/host, not SquadScope's existing publish manifests.

### Human review mechanism

MVP uses a concrete review mechanism before synthesis. If a temporary prototype remains in this repo, the GitHub Environment `podcast-review` can pause that manually invoked/post-publish workflow before any non-dry-run TTS call. Once separated, Podcaster should own the equivalent review gate in its own deployment lifecycle. TTS cannot proceed until approval is granted. Reviewers inspect `script.md`, `claim_ledger.json`, `show_notes.md`, `transcript.md`, `publishing_packet.md`, and `episode_manifest.json`, with attention to source support, disclosure, tone, privacy readiness, budget status, and manual publishing readiness.

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

### Publishing and storage options

| Option | Pros | Cons | Decision |
| --- | --- | --- | --- |
| Commit MP3s to git/Pages | Very simple URLs | Bloats repo; not appropriate for audio product delivery | Reject |
| SquadScope website podcast hosting | Full control | Contradicts clarified product scope; adds feed/player/site maintenance | Reject for MVP |
| Azure Blob Storage as temporary staging | Designed for unstructured objects and workflow artifacts (https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) | Needs retention, cleanup, access controls | **Select for staging** |
| Manual Spotify for Creators/platform upload | Fastest path to validate product | Operator step; no full automation | **Select for initial launch** |
| Podcast host/provider RSS | Standard distribution path; may expose APIs | Cost, lock-in, privacy review | Research alongside Spotify API |
| Direct Spotify/API automation | Could reduce weekly operator work | Upload/publish API support is unclear | Research before implementation |

---

### Architecture and repository boundary options

| Option | Description | Pros | Cons | Decision |
| --- | --- | --- | --- | --- |
| Option A: temporary folder in this repo | Keep docs, contracts, sample artifacts, and possibly throwaway prototypes in a clearly isolated folder. | Fastest learning path; keeps article contract close to SquadScope. | Easy to blur product ownership; must not affect publishing, manifests, workflows, or deploys. | Accept only for prototypes/docs that cannot affect publishing. |
| Option B: separate repo/project from the start | Create a `Podcaster` project/repo for implementation, tests, workflow, secrets, and release process. | Clean ownership; protects SquadScope publishing; easier independent roadmap. | Slight setup overhead before first prototype. | Preferred before implementation grows beyond contracts/prototypes. |
| Option C: Azure-native project/resource group | Build Podcaster as its own Azure resource group/subscription boundary with IaC and independent deployment lifecycle. | Best fit for Azure Speech/Blob/identity/cost governance; clear resource ownership. | Requires infrastructure governance and cost controls up front. | Required before any Azure resource deployment. |

**Recommendation:** Keep the SquadScope repo as the source of article export contracts, PRD, and planning now. Move implementation to a separate **Podcaster** project/repo before deploying Azure resources. Use a temporary folder in this repo only for prototypes that cannot affect publishing and do not add audio steps to the article critical path.

---

## Technical Requirements

### Generation workflow

- SquadScope must not add podcast generation to the weekly crawl/analyze/generate/deploy critical path.
- SquadScope may expose a stable post-publish artifact/API/URL contract containing week, article URL/path, content or content hash, source artifact references, run ID, and publish mode after normal publishing completes.
- Communication is by stable artifact, API, URL, or manual input. Podcaster must not directly mutate SquadScope publishing flow, publish manifests, article content, or deploy state.
- Any future workflow that remains in SquadScope may only emit a post-publish event/artifact or be manually invoked for a prototype; production podcast generation should live in Podcaster once separated.
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

### Integration boundary requirements

- SquadScope exports article URL/content/artifact manifest after a successful normal publish.
- Podcaster consumes that export asynchronously and owns all podcast-specific processing.
- Integration must be additive and backward-compatible; existing publish manifests remain unchanged unless a separate contract version is approved.
- The Podcaster implementation must use least-privilege access to read only the exported article/artifacts it needs.

### Temporary Azure Blob Storage requirements

- Use Podcaster-owned Blob Storage for staging generated MP3s, transcripts, manifests, and publishing packets.
- Apply least-privilege access; public anonymous read is not required for MVP staging.
- Configure retention/cleanup so generated audio is removed after publishing is confirmed or after a defined expiry.
- Do not use expiring staging URLs in any public podcast feed or platform field.
- Record staging path and expiry in `episode_manifest.json`.
- If a future RSS/provider integration needs public enclosures, make a separate delivery decision for a podcast host, provider API, or approved stable enclosure strategy.

### Manual Spotify/platform publishing packet

Before a human publishes the episode, the workflow must produce a packet containing:

- Final MP3.
- Episode title.
- Episode description.
- Transcript and/or show notes.
- AI voice disclosure.
- Sponsor, affiliate, or support disclosures, if any.
- Source weekly article URL.
- Corrections link.
- Claim ledger and reviewer identity/time for audit.
- Post-publish fields to fill in: external episode URL, platform, publish time, and corrections/update notes.

### Spotify/API research requirement

Create a research phase before any automated publishing implementation:

1. Verify current Spotify for Creators, Spotify podcast delivery, and Spotify Web API docs.
2. Confirm whether Spotify exposes an upload/publish API for podcast episodes.
3. If Spotify does not support direct upload/publish automation, research podcast host/provider RSS APIs, hosting APIs, or a documented manual Spotify for Creators flow.
4. Record authentication, privacy, retention, approval, rollback/correction, and rate-limit implications.
5. Do not promise or build automated Spotify publishing until this research is accepted.

Caveat: initial documentation research suggests the Spotify Web API is for streaming-service interactions like metadata, playlists, playback, and library operations, not clearly podcast episode upload. This must be verified against current Spotify for Creators and podcast delivery documentation.

### Website integration requirement

The SquadScope website MVP only needs a configurable link to the external podcast page once available, such as a Spotify show page or selected platform page. The link should be easy to disable until launch. No site-hosted feed, no article audio embed, and no embedded player are MVP requirements.

### Cost controls

Expected scripts are about 4,500-9,000 billable characters for 5-10 minutes, which keeps many TTS options at cents-level per episode, depending on provider, region, and free allowance. Operations must track total podcast cost, not just TTS: TTS, storage, egress/download bandwidth if any, script generation, validation, platform/provider costs, and future CDN charges if approved.

MVP guardrails:

- Max 5 episodes per month.
- Max $5/month total podcast budget unless manually raised.
- Max 10 minutes per episode.
- Cost ledger entry per episode with per-category estimates/actuals.
- Workflow fails closed before non-dry-run synthesis or publish-packet generation when limits would be exceeded.

---

## Safety, Legal, and Editorial Gates

### Hard launch gates

No public episode may ship unless all are true:

1. AI voice disclosure appears in the first 60 seconds and show notes/platform description. OpenAI's TTS guide explicitly requires clear disclosure that TTS voice is AI-generated and not human (https://developers.openai.com/api/docs/guides/text-to-speech).
2. Paid/commercial-use voice license is documented for the selected provider and voices.
3. No real-person voice cloning, no celebrity/podcast-host imitation, and no Hard Fork/NYT marks or copied expression.
4. MVP is voice-only: no music or SFX unless/until a licensed track/effect is selected and recorded in the manifest.
5. Human script review is complete through the Podcaster review gate before synthesis for MVP; a temporary in-repo prototype may use the GitHub Environment `podcast-review`.
6. Claim ledger shows every factual claim is supported or removed.
7. Show notes include source URLs and corrections link.
8. No unsupported facts, no defamatory motive claims, and no fake sponsorship language.
9. Sponsorship/affiliate/support disclosures appear before any sponsor, affiliate, or paid support segment.
10. Privacy policy is updated before any non-dry-run TTS call or before any future/deferred use of podcast analytics, ad tech, payment redirects, or third-party embedded players.
11. GDPR/cookie consent covers non-essential podcast analytics before analytics tags or third-party players are enabled.

### FTC and monetization compliance

FTC endorsement guidance requires endorsements and ads to be honest, not misleading, and to disclose material connections clearly and conspicuously (https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking). Therefore:

- Sponsor segments must be labeled before the segment starts.
- Affiliate links must be disclosed near the link and in show notes.
- Hosts must not claim personal use or endorsement unless true.
- Sponsored influence must not affect repo selection/ranking unless the entire product strategy changes and is disclosed.
- Support/donation links must not imply editorial influence.

### Privacy requirements

Before Phase 2 performs any non-dry-run TTS call, update `content/privacy/_index.md` to document the selected voice-provider candidates and data flow. This privacy update is a prerequisite to Phase 2, not a launch cleanup item. Also update it before analytics, ad tech, payment redirects, or external players are enabled to document:

- Voice provider(s), data sent, retention, and region if configurable.
- Temporary Azure Blob Storage staging, access controls, logs, and cleanup policy.
- Spotify/podcast platform or host, if selected.
- Podcast analytics vendors, if any.
- Whether IP/user-agent data is processed by external podcast links, widgets, or players.
- Payment processors for donations/premium offerings.

SquadScope should not store payment data. Use Stripe, PayPal, Ko-fi, Patreon, GitHub Sponsors, or similar redirects if monetization needs payment handling.

---

## Monetization Roadmap

### Phase 1: Manual/support-first launch

- Keep episodes free.
- Launch manually on Spotify or the selected platform while audience and quality are validated.
- Add optional website support links only after privacy copy and disclosure language are updated.
- Consider GitHub Sponsors, Ko-fi, Patreon, PayPal, Stripe, or newsletter/support redirects; do not store payment data in SquadScope.
- Make clear that support does not influence article ranking, claims, or episode coverage.

### Phase 2: Sponsorships with controls

- Add host-read sponsor spots only after listener traction, privacy review, and disclosure templates exist.
- Sponsorship copy must be reviewed and clearly labeled in the audio and show notes.
- Website sponsorship/support placements must be clearly labeled and must not weaken the no-paid-placement editorial promise.
- Website ads require cookie/consent and privacy review before activation.

### Phase 3: Advanced monetization

- Dynamic ad insertion, premium feeds, sponsored deep dives, or live events can be explored after the core podcast cadence is reliable and listener metrics justify complexity.
- Premium feeds require authentication/payment provider design and privacy review.
- Dynamic ads require privacy, consent, retention, vendor, and disclosure review before implementation.

---

## MVP Scope

### In scope

- One episode per weekly article.
- Separate podcast product targeting Spotify or a podcast platform.
- Two-host script generated from article plus existing evidence artifacts.
- Claim ledger and source-backed show notes.
- Human review before synthesis.
- TTS provider selected after a Phase 2 listening-test POC.
- MP3 post-processing and temporary Azure Blob Storage staging with retention/cleanup.
- Manual Spotify/platform publishing packet.
- Spotify/API and podcast-provider automation research.
- Website configurable external podcast link only.
- AI voice disclosure and correction path.
- Cost ledger and monthly budget guardrail covering TTS, staging storage, script generation, validation, and platform/provider costs.
- Manual invocation and safe post-publish artifact/event handoff.
- Repository/project boundary defined before infrastructure code is written.

### Out of scope for MVP

- Hosting the podcast in the SquadScope website.
- Website-hosted podcast RSS for listener consumption.
- Article audio embeds, embedded players, Hugo podcast shortcodes, and website-hosted player pages are non-MVP/deferred.
- Automated Spotify publishing before API feasibility is verified.
- Dynamic ad insertion.
- Premium/private feeds.
- Real-time/daily episodes.
- Multiple languages.
- Listener analytics beyond platform basics, unless privacy/consent work is done.
- Fully automated publish without human review.
- Voice cloning or real-person mimicry.
- CDN optimization for audio delivery.

---

## Acceptance Criteria

### Product acceptance

- A reviewer can inspect the reviewed script artifact, claim ledger, show notes, transcript, publishing packet, manifest, and generated audio, then map every substantive factual claim to the published article and cited source/artifact validation.
- Episode length fits the 8-12 minute show format, and automated MVP runs are no more than 10 minutes unless manually overridden.
- The show sounds distinct from copied podcasts and uses the approved `Signal Check` structure.
- Jokes clarify or compress analysis without adding unsupported claims or targeting individuals unfairly.
- AI voice disclosure is audible in the first 60 seconds and visible in show notes/platform description.
- Corrections path and source article URL are present in the manual publishing packet.
- Website integration, if present, is only an external configurable podcast link.

### Technical acceptance

- Podcaster workflow can be rerun for a selected week without duplicate episodes.
- Article publishing behavior, publish manifests, deploy timing, and success criteria are unchanged even if podcast generation fails or never runs.
- MP3 is staged outside git, under the size/duration/audio constraints.
- Temporary Blob artifacts have documented access controls, retention, and cleanup.
- Manual publishing packet includes MP3, title, description, transcript/show notes, disclosures, source article URL, and corrections link.
- Spotify/API research documents whether direct upload/publish automation exists and what fallback path is recommended.
- Cost ledger records provider, character count, duration, TTS/staging/script-generation/validation/platform estimated or actual costs, and monthly budget status.
- Secrets are not logged or committed.

### Safety acceptance

- Human reviewer approval is recorded via the Podcaster review gate before synthesis; a temporary in-repo prototype may use GitHub Environment `podcast-review`. Reviewers inspect `script.md`, `claim_ledger.json`, `show_notes.md`, `transcript.md`, `publishing_packet.md`, and `episode_manifest.json` before allowing TTS.
- Provider voice license and AI disclosure are documented.
- No real-person voice cloning or protected podcast imitation occurs.
- Sponsorship/affiliate/support text, if present, is disclosed before the relevant segment.
- Privacy policy changes are merged before any non-dry-run TTS call and before production analytics/providers beyond current hosting are enabled.

---

## Implementation Phases

1. **Design and contracts:** Define the SquadScope export contract, Podcaster-owned manifest, claim ledger, show notes, publishing packet, staging storage, retention, review statuses, and website external-link configuration.
2. **Repository/project boundary gate:** Decide the Podcaster repo/project boundary and Azure resource ownership before infrastructure code, secrets, or deploy workflows are written.
3. **Script generation dry run:** Generate script/ledger/show notes/transcript/publishing packet from existing weekly articles without TTS or publishing, using only exported artifacts or manual input.
4. **TTS proof of concept:** After the privacy update, synthesize reviewed private samples with Azure Speech Standard, Azure Speech HD/OpenAI voices in Azure if available, and OpenAI `tts-1` or `gpt-4o-mini-tts`; run a listening test and select the provider.
5. **Temporary staging:** Upload approved MP3s and packet artifacts to Podcaster-owned Azure Blob Storage with access controls, manifest recording, retention, and cleanup.
6. **Spotify/API research:** Verify direct Spotify upload/publish support; if unsupported, document manual Spotify for Creators flow and/or podcast host/provider RSS/API options.
7. **Manual launch:** Generate the publishing packet and manually publish to Spotify or selected platform.
8. **Website external link:** Add a configurable link to the external podcast/platform page once available.
9. **Quality experiments:** Revisit voices, providers, music/SFX, and production polish after the Phase 2 provider decision and MVP reliability are proven.
10. **Monetization experiments:** Add support/donation links first; defer sponsorships, ads, premium feeds, and dynamic insertion until disclosure, privacy, and audience metrics justify them.

---

## Open Questions

- Which repository/project owns Podcaster implementation before Azure infrastructure is written?
- Which Azure resource group/subscription, region, Speech resource, Blob account, identities, and budget alerts should Podcaster own for production?
- Which provider/voice pair wins the Phase 2 listening test while avoiding real-person mimicry?
- Which required reviewers should be configured on the GitHub Environment `podcast-review`?
- Does Spotify currently support episode upload/publish automation, or is manual Spotify for Creators / provider RSS the right MVP path?
- Which external podcast/platform page should the website link to after launch?
- What public podcast cover art should be used, and does it require a new design asset?
- What is the minimum listener metric needed before monetization moves beyond donations/support?

---

## Decision

Proceed with this amended docs-only design. For implementation, build **SquadScope: Signal Check** through **Podcaster**, a human-reviewed, source-backed, two-host sister product/tool that consumes SquadScope's published article artifacts asynchronously and is distributed as a separate podcast product. Keep SquadScope's existing publishing behavior, gates, manifests, deploys, and critical path unchanged. Define the repository/project boundary and Azure resource ownership before infrastructure code is written; keep only docs/contracts and harmless prototypes in SquadScope until Podcaster is separated. Use a review gate, post-publish artifact/API/URL handoff or manual invocation, a Phase 2 TTS listening-test provider decision, Podcaster-owned temporary Azure Blob Storage staging with retention/cleanup, a manual Spotify/platform publishing packet, Spotify/API automation research, a website external-link-only integration, and strict disclosure/privacy/safety/cost gates. Defer site-hosted podcast consumption, embedded players, ads, premium feeds, music/SFX, and full publish automation until the MVP proves reliable and trustworthy.
