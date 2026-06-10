# Podcast Generation Execution Plan

**Issue:** #310
**Date:** 2026-06-07
**Lead:** Leela
**Status:** Archived 2026-06-10 — remaining execution work is tracked by issue #355 and its linked issues; retained as reference.
**Companion PRD:** `docs/processed/PRD-podcast-generation.md`

---

## Recommendation Snapshot

Build **SquadScope: Signal Check**, an 8-12 minute weekly two-host podcast generated from the published weekly article; automated MVP runs should target 8-10 minutes to honor the cost guardrail. Podcaster is a **sister product/tool**, not a SquadScope website feature, and the podcast is published to Spotify or another podcast platform. SquadScope's website MVP only exposes a configurable external link to the podcast/platform page once available.

Select the TTS provider in Phase 2 after a listening-test POC comparing Azure Speech Standard, Azure Speech HD/OpenAI voices in Azure if available, and OpenAI `tts-1` or `gpt-4o-mini-tts`. Use Podcaster-owned Azure Blob Storage as temporary/staging artifact storage for generated MP3s, transcripts, manifests, and publishing packets, with retention and cleanup. Initial Spotify publishing is manual through an operator packet. Research whether Spotify supports podcast episode upload/publish automation before designing any automated publishing path. Keep only docs/contracts and harmless prototypes in SquadScope until the repository/project boundary is defined.

Key references: Azure Speech TTS (https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech), Azure Blob Storage (https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction), OpenAI TTS disclosure guidance (https://developers.openai.com/api/docs/guides/text-to-speech), FTC endorsement guidance (https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking). Spotify/API work must verify current Spotify for Creators and podcast delivery documentation; initial docs research suggests Spotify Web API is for streaming-service interactions such as metadata/playlists/playback, not clearly for episode upload.

---

## Guiding Constraints

- Do not commit MP3s or generated audio binaries to git.
- Do not host the podcast in the SquadScope website for MVP.
- Website work is limited to a configurable external podcast/platform link.
- Zero impact on existing publishing: no changes to weekly crawl/analyze/generate/deploy behavior, no article-publish gating, no publish-manifest changes, and no audio steps in the critical path.
- Podcast failures must not block weekly article publishing.
- MVP generation must require Podcaster-owned review approval before TTS; a temporary in-repo prototype may use GitHub Environment `podcast-review`.
- Every substantive claim must be source-backed in a claim ledger.
- Disclose AI-generated voices in the first 60 seconds and in show notes/platform descriptions.
- Do not clone or mimic real people, Hard Fork hosts, NYT branding, segment names, jingles, or phrasing.
- Keep MVP to max 5 episodes/month, max $5/month total podcast spend unless manually raised, and max 10 minutes/episode.
- Azure Blob Storage is temporary staging with retention/cleanup, not final public hosting for MVP; Azure resources must be owned by Podcaster once implementation moves beyond prototype/docs.
- If an RSS feed is generated during MVP, it is for podcast-platform ingestion or future host/provider migration, not site-hosted consumption.
- Update privacy policy before any non-dry-run TTS provider call and before adding podcast analytics, payment providers, external players, or non-essential tracking.
- Define the repository/project boundary and Azure resource ownership before infrastructure code is written.

---

## Target Architecture

```text
SquadScope normal weekly publish completes unchanged
  -> SquadScope emits stable post-publish article URL/content/artifact manifest, or operator provides it manually
  -> Podcaster consumes that artifact/API/URL asynchronously
  -> reject dry-run/candidate-only/restore/no-AI fallback replacement modes
  -> Podcaster computes article hash and idempotency key
  -> Podcaster derives claims from published article and validates against exported artifacts
  -> Podcaster generates outline, script, show notes, transcript, publishing packet draft
  -> Podcaster-owned review gate approves script package
  -> selected TTS provider synthesis outside SquadScope critical path
  -> ffmpeg normalize/transcode
  -> upload MP3/transcript/manifest/packet to Podcaster-owned temporary Azure Blob staging
  -> operator downloads/reviews publishing packet
  -> operator manually publishes to Spotify or selected platform
  -> record external episode URL and optionally update website external podcast link
```

Idempotency key:

```text
week + article_hash + script_prompt_version + voice_config_hash
```

---

## Architecture Options and Recommendation

| Option | Description | Pros | Cons | Recommendation |
| --- | --- | --- | --- | --- |
| Option A: temporary folder in this repo | Keep planning, contracts, sample artifacts, and possibly throwaway prototypes in SquadScope. | Fastest way to iterate on the article export contract. | Risk of accidental coupling to publishing; cannot own Azure resources or critical workflows. | Allow only for docs/prototypes that cannot affect publishing. |
| Option B: separate repo/project from the start | Create a `Podcaster` repo/project for implementation, tests, secrets, workflows, and releases. | Clean lifecycle and ownership; protects SquadScope publishing. | Requires setup before implementation. | Recommended before real implementation grows. |
| Option C: Azure-native project/resource group | Give Podcaster its own Azure resource group/subscription boundary, IaC, identities, budget alerts, and deployment lifecycle. | Best governance for Speech, Blob, costs, and secrets. | Requires infra design and ownership decisions. | Required before any Azure resource deployment. |

**Selected path:** keep PRD, plan, and artifact/API contract documentation in SquadScope now. Move implementation to a separate **Podcaster** project/repo before Azure resource deployment. Use a temporary folder in this repo only for prototypes that are manually invoked, isolated from publish manifests, and unable to affect crawl/analyze/generate/deploy.

---

## Phase 0: Product and Contract Finalization

**Goal:** Lock the separate-product contract and zero-impact boundary before implementation.

### Issues

1. **Define SquadScope export contract and podcast artifact schemas**
   - SquadScope exports only stable post-publish data: week, article URL/path, article content or hash, source artifact references, run ID, publish mode, and optional artifact manifest.
   - Podcaster owns `episode_manifest.json`, `claim_ledger.json`, `show_notes.md`, `transcript.md`, reviewed `script.md`, and `publishing_packet.md`.
   - Include week, article URL, article hash, prompt version, voice config, provider, cost, duration, byte length, disclosure status, reviewer, temporary Blob staging path, retention expiry, external publish URL, and publish status.
   - Acceptance: sample schema fixtures exist, document required/optional fields, and do not require changes to existing SquadScope publish manifests.

2. **Define repository/project boundary and Azure ownership gate**
   - Decide whether implementation starts in a separate `Podcaster` repo/project or a temporary isolated folder for prototypes only.
   - Decide Azure resource group/subscription, identities, Blob/Speech ownership, budget alerts, and deployment lifecycle before IaC or secrets are written.
   - Acceptance: no infrastructure code, Azure deployment workflow, or production credential is added until this gate is resolved.

3. **Define editorial script prompt and style guide**
   - Use `SquadScope: Signal Check` format.
   - Segment order: cold open, The Signal, The Noise Check, The Gap, Receipts Round, Week Ahead, Outro.
   - Host A Curator, Host B Skeptic.
   - Acceptance: prompt requires citations, bans unsupported facts, bans copied podcast expression, and includes joke safety rules.

4. **Configure review gate for temporary prototype / Podcaster**
   - Use required reviewers as the MVP review mechanism.
   - A temporary SquadScope prototype or the separated Podcaster workflow uploads `script.md`, `claim_ledger.json`, `show_notes.md`, `transcript.md`, `publishing_packet.md`, and `episode_manifest.json` for inspection, then pauses before non-dry-run TTS.
   - Acceptance: TTS cannot proceed without environment approval, and approval identity/time is recorded in the manifest.

---

## Phase 1: Script Dry Run and Publishing Packet, No Audio

**Goal:** Prove articles can become safe, useful scripts and operator-ready publishing packets before adding TTS.

### Issues

5. **Implement claim/source extraction**
   - Input: published weekly article plus SquadScope's exported URL/content/artifact manifest.
   - Output: claim ledger derived from the published article, then validated against existing analysis/publish artifacts where available, with support status and source URLs.
   - Acceptance: unsupported claims fail the gate or are marked for removal.

6. **Generate episode outline and script**
   - Output 1,200-1,700 word two-host script.
   - Include AI voice disclosure in first 60 seconds.
   - Keep jokes aimed at hype cycles, not individuals.
   - Acceptance: script passes length, segment, disclosure, and banned-phrase checks.

7. **Generate show notes, transcript, and manual publishing packet**
   - Show notes include article link, source links, AI disclosure, corrections link, and sponsorship/support disclosure placeholder.
   - Transcript is derived from final script.
   - Publishing packet includes MP3 placeholder/path, title, description, transcript/show notes, disclosures, source article URL, corrections link, reviewer info, and post-publish fields.
   - Acceptance: every source URL in the ledger appears in show notes or is intentionally excluded with reason; packet is sufficient for manual Spotify/platform publishing once audio exists.

8. **Add dry-run validation command**
   - Validate ASCII filenames, required fields, claim support, disclosure, script length, packet completeness, and no fake sponsor language.
   - Acceptance: command exits non-zero on missing ledger/support/disclosure/packet fields.

---

## Phase 2: TTS Proof of Concept

**Goal:** Select the TTS provider using private reviewed samples before staging/publishing implementation.

### Issues

9. **Update privacy policy for TTS candidates before synthesis**
   - Document candidate voice providers, data sent, retention/region if configurable, and operator-facing disclosure before any non-dry-run TTS call.
   - Acceptance: privacy PR is merged before provider credentials are used for non-dry-run synthesis.

10. **Run TTS provider listening-test POC**
   - Compare Azure Speech Standard neural voices, Azure Speech HD/OpenAI voices in Azure if available, and OpenAI `tts-1` or `gpt-4o-mini-tts`.
   - Use the same reviewed sample script, record billable characters, latency, licensing/privacy notes, voice naturalness, pronunciation, SSML/control support, and estimated total monthly cost.
   - Acceptance: provider decision is documented before production staging/publish-packet implementation; private MP3 artifacts are generated only after review approval and outside SquadScope's publishing critical path.

11. **Post-process audio with ffmpeg**
    - Mono, 44.1 kHz, 64-96 kbps, `audio/mpeg`, target -16 LUFS, under 10 MB.
    - Acceptance: validation reports duration, loudness, sample rate, bitrate, channels, and byte length.

12. **Add cost ledger and guardrails**
    - Track per-episode and monthly TTS, temporary storage, script generation, validation, provider/platform costs, and any egress/download bandwidth if later introduced.
    - Enforce max 5 episodes/month, max $5/month total podcast spend unless manually raised, max 10 minutes; call out that hosting/provider/egress costs may dominate if downloads grow.
    - Acceptance: workflow fails before non-dry-run synthesis or publish-packet completion if limits would be exceeded.

---

## Phase 3: Temporary Staging and Manual Publish Readiness

**Goal:** Produce validated audio and a complete manual publishing packet in Podcaster without making the website or SquadScope publishing flow the podcast host.

### Issues

13. **Provision Podcaster-owned Azure Blob Storage staging conventions**
    - Example: `podcast-staging/YYYY/Www/squadscope-signal-check-YYYY-Www.mp3`.
    - ASCII filenames only.
    - Configure least-privilege workflow access, content type `audio/mpeg`, retention tags/metadata, and cleanup policy.
    - Acceptance: uploaded MP3 is available to authorized operators for manual publish and has a documented expiry/cleanup path.

14. **Implement staging retention and cleanup**
    - Delete or archive staging artifacts after successful platform publish, rejected review, or retention expiry.
    - Keep manifest metadata needed for audit without retaining unnecessary audio forever.
    - Acceptance: cleanup can run safely and records what was deleted or retained.

15. **Generate final manual Spotify/platform publishing packet**
    - Include final MP3, title, description, transcript/show notes, AI disclosure, sponsor/affiliate/support disclosures if any, source article URL, corrections link, reviewer identity/time, and post-publish fields.
    - Acceptance: an operator can publish using Spotify for Creators or the selected platform without reading workflow internals.

16. **Record external publish result**
    - After manual publish, record external episode URL, platform/show URL, publish time, and any corrections/update notes in the manifest or issue comment.
    - Acceptance: website link work has a reliable external target when launch is approved, without modifying article publish manifests or critical path behavior.

---

## Phase 4: Spotify/API and Podcast Host Research

**Goal:** Determine whether publishing can be automated after the manual MVP.

### Issues

17. **Research Spotify upload/publish API support**
    - Verify current Spotify for Creators, Spotify podcast delivery, and Spotify Web API docs.
    - Caveat to test: initial docs research suggests Spotify Web API is for streaming-service interactions like metadata, playlists, playback, and library operations, not clearly podcast episode upload.
    - Acceptance: documented yes/no answer with links, auth model, required accounts, limitations, and operational risk.

18. **Research fallback automation paths**
    - If Spotify direct upload/publish is unavailable, evaluate podcast host/provider RSS APIs, provider-hosted distribution to Spotify, or a documented manual Spotify for Creators flow.
    - Include privacy, retention, analytics, cost, corrections/rollback, and disclosure implications.
    - Acceptance: recommendation chooses manual continuation, provider API, or future direct API with rationale.

19. **Decide whether any RSS is needed for MVP operations**
    - If RSS is needed, scope it as platform/provider ingestion or future host migration only.
    - Do not publish a SquadScope-site-owned feed for listener consumption as MVP.
    - Acceptance: RSS decision explicitly states owner, consumer, URL strategy, and why it does not turn the website into the podcast host.

---

## Phase 5: Website External Link Only

**Goal:** Make the external podcast discoverable with a simple website link only, without hosting it on SquadScope or changing article publishing.

### Issues

20. **Add configurable external podcast link**
    - Link target can be Spotify show page or selected platform page.
    - Link must be easy to disable until launch.
    - Include concise AI/generated podcast disclosure if needed near the link or in methodology/privacy updates.
    - Acceptance: site builds with link enabled/disabled and does not add an audio player, article embed, website-hosted player page, or site-owned listener feed; those website-hosted consumption patterns remain non-MVP/deferred.

21. **Update methodology and privacy pages**
    - Methodology: explain article-to-podcast transformation, safety gates, manual/platform publishing, and correction path.
    - Privacy: document selected voice provider, temporary Blob staging logs/retention, platform/provider links, analytics/payment providers if used.
    - Acceptance: public docs match actual providers and data flows before launch.

---

## Phase 6: Launch Controls

**Goal:** Enable reliable weekly operation with manual platform publishing while leaving SquadScope publishing unaffected.

### Issues

22. **Create post-publish handoff or Podcaster workflow**
    - In SquadScope, any future workflow should only emit a post-publish event/artifact after confirmed normal publish, or be manually invoked for prototypes.
    - The podcast generation workflow should live in Podcaster once separated and consume week, article path/URL, source run ID, publish mode, and artifact identifiers asynchronously.
    - Do not naively use `workflow_run`; if used later, fetch and verify triggering run inputs/artifacts before synthesis.
    - Dry-run, candidate-only, restore, failed, or no-AI fallback replacement runs must not synthesize audio.
    - Must be non-blocking relative to `crawl-and-publish.yml` and must not change existing publish manifests.
    - Acceptance: failed podcast run does not fail or roll back article publishing, and unsafe publish modes are rejected before TTS.

23. **Add Podcaster review gate**
    - Require approval after script generation and before TTS; a temporary in-repo prototype may use GitHub Environment `podcast-review`, while separated Podcaster owns its equivalent gate.
    - Reviewers inspect `script.md`, `claim_ledger.json`, `show_notes.md`, `transcript.md`, `publishing_packet.md`, and `episode_manifest.json`.
    - Acceptance: unapproved scripts stop before synthesis.

24. **Add observability**
    - Log episode key, provider, duration, cost estimate, byte length, staging path, retention expiry, validation results, and external publish URL when known.
    - Do not log secrets or full provider credentials.
    - Acceptance: operator can diagnose failures from workflow summary.

25. **Pilot launch with one back-catalog episode**
    - Generate one recent weekly episode as a pilot.
    - Publish manually to Spotify or selected platform after safety checks pass.
    - Acceptance: reviewer signs off on audio quality, citations, disclosure, publishing packet, staging cleanup, and external episode URL.

---

## Phase 7: Quality and Monetization Experiments

**Goal:** Improve quality and revenue only after trust and reliability.

### Issues

26. **Add licensed music/SFX later, if desired**
    - MVP is voice-only. Select a licensed track/effect only in a later issue, and record license details in the episode manifest.
    - Acceptance: no music/SFX ships until license, attribution/disclosure, loop/edit rules, and reviewer approval criteria are documented.

27. **Add support/donation links**
    - GitHub Sponsors/Ko-fi/Patreon/PayPal/Stripe redirects only; do not store payment data.
    - Website can link to support options once privacy and disclosure copy are updated.
    - Acceptance: privacy page, website copy, and show notes make clear support does not influence coverage or rankings.

28. **Define sponsorship policy**
    - FTC requires material connections to be disclosed clearly and conspicuously (https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking).
    - Acceptance: sponsor copy template discloses before sponsor segment and forbids sponsor influence over rankings.

29. **Evaluate premium feed or dynamic ads**
    - Defer until audience metrics justify complexity.
    - Acceptance: privacy, consent, payment, provider, RSS/auth if applicable, and disclosure designs are approved before implementation.

---

## Existing Issue Mapping

| Issue | Status | Role in corrected scope |
| --- | --- | --- |
| #301 Podcast: decide and enforce script human-review gate | Open | Keep; maps to `podcast-review` gate. |
| #302 Podcast: implement safe trigger handoff from weekly publish | Open | Amend; SquadScope may emit only a post-publish artifact/event, while generation belongs in Podcaster once separated. |
| #303 Podcast: add Hugo-safe episode embed shortcode | Closed | Closed as superseded by platform-podcast scope; no MVP embed. |
| #304 Podcast: update privacy policy before TTS provider use | Open | Keep; privacy-before-TTS and future platform/provider/payment disclosures. |
| #305 Podcast: decide Blob Storage public enclosure strategy | Open | Amend to staging/retention strategy; public enclosure is not MVP unless platform/provider path requires it. |
| #306 Podcast: run early TTS quality bakeoff | Open | Keep; Phase 2 provider listening-test POC. |
| #307 Podcast: add website link to external podcast only | Open | Keep; replaces site embed/player work. |
| #308 Podcast: research Spotify publishing API and automation path | Open | Keep; required before automated publishing. |
| #309 Podcast: generate weekly publishing packet after article publish | Open | Keep; manual Spotify/platform publishing packet. |
| #310 Correct podcast PRD scope: platform podcast, website link only | Open | This docs-only correction. |

---

## Implementation Issue Creation Gate

Before implementation begins, create or update GitHub issues for every P0/P1 row below. This correction pass only amends docs; it does not need to create implementation issues. The P0/P1 set must include: repository/project boundary and Azure resource ownership before infrastructure code, Podcaster-owned review approval, safe post-publish artifact/event handoff, privacy-before-TTS sequencing, Phase 2 provider comparison, temporary Blob staging with retention/cleanup, manual publishing packet, Spotify/API research, website external-link-only integration, voice-only MVP/music licensing deferral, claim-ledger derivation/validation, and total podcast cost guardrails.

## Suggested Issue Breakdown

| Priority | Issue | Issue title | Owner | Depends on |
| --- | --- | --- | --- | --- |
| P0 | #310 | Correct PRD/plan to platform podcast scope | Leela | User clarification |
| P0 | New/update | Define Podcaster repository/project boundary and Azure resource ownership | Leela/Bender | PRD approval |
| P0 | #301 | Decide and enforce Podcaster script human-review gate | Leela/Hermes | boundary gate |
| P0 | New/update | Define SquadScope export contract, podcast artifact schemas, idempotency key, and publishing packet contract | Leela/Bender | boundary gate |
| P0 | New/update | Define Signal Check editorial prompt and safety style guide | Farnsworth/Hermes | PRD approval |
| P0 | New/update | Implement claim ledger extraction and validation | Farnsworth/Fry | schemas |
| P0 | #309 | Generate dry-run scripts/show notes/transcripts and manual publishing packet | Farnsworth | prompt, ledger |
| P1 | #304 | Update privacy policy for TTS provider candidates | Hermes/Leela | prompt, ledger |
| P1 | #306 | Run TTS provider listening-test POC and select provider | Bender/Farnsworth | privacy update, review gate |
| P1 | #302 | Add safe post-publish artifact/event handoff or manual invocation | Hermes/Bender | export contract |
| P1 | New/update | Add ffmpeg audio validation and normalization | Bender/Fry | TTS POC |
| P1 | New/update | Add total podcast cost ledger and monthly guardrails | Hermes/Bender | TTS POC |
| P1 | #305 | Upload podcast assets to Podcaster-owned temporary Blob staging with retention/cleanup | Bender | boundary gate, audio validation |
| P1 | #308 | Research Spotify publish API and fallback provider/RSS/manual paths | Leela/Bender | PRD approval |
| P1 | #307 | Add configurable website link to external podcast/platform page | Bender | external show URL |
| P1 | New/update | Update methodology and privacy pages for podcast launch | Hermes/Leela | provider/platform choices |
| P2 | New/update | Pilot one back-catalog episode with manual Spotify/platform publish | Leela/Farnsworth | P1 complete |
| P2 | New/update | Add licensed music/SFX only after manifest license design | Farnsworth/Hermes | MVP pilot |
| P2 | New/update | Add support/donation links | Hermes | privacy update |
| P3 | New/update | Evaluate sponsorships, dynamic ads, premium feeds, or live events | Hermes/Leela | audience metrics |

---

## Phase Acceptance Criteria

- Phase 0 is complete when the SquadScope export contract, Podcaster boundary, Azure ownership, schemas, prompts, review status, staging rules, and publishing packet contract are documented well enough for implementation without product ambiguity.
- Phase 1 is complete when a weekly article can produce a reviewed script, transcript, show notes, claim ledger, and manual publishing packet without audio synthesis.
- Phase 2 is complete when privacy docs are updated, reviewed sample scripts are synthesized privately across candidate providers, a listening-test decision selects the MVP provider, and output fits duration, size, loudness, and total cost limits.
- Phase 3 is complete when Podcaster-owned temporary Blob staging, retention, cleanup, and manual publish packet generation work for validated audio.
- Phase 4 is complete when Spotify/API research determines whether direct upload/publish automation exists and recommends manual, provider API, or future direct API path.
- Phase 5 is complete when the website can show or hide a configurable external podcast/platform link without hosting or embedding the podcast.
- Phase 6 is complete when Podcaster can generate a reviewed episode package from a post-publish artifact/API/URL or manual invocation, support manual platform publishing, record the external URL, and leave article publishing unaffected by podcast failures.

## Validation Checklist for First Public Episode

- [ ] Script is 1,200-1,700 words and target duration fits the 8-12 minute format, with automated MVP output at or below 10 minutes.
- [ ] AI voice disclosure is in first 60 seconds and show notes/platform description.
- [ ] Claim ledger has no unsupported public claims.
- [ ] Podcaster review gate (or temporary prototype `podcast-review` environment) approved script artifacts before synthesis.
- [ ] Provider voice license/privacy terms are documented before non-dry-run TTS.
- [ ] No real-person voice cloning or protected podcast imitation.
- [ ] No fake sponsor language.
- [ ] No music/SFX in MVP unless a later licensed-track manifest issue is complete.
- [ ] Show notes include source URLs and corrections link.
- [ ] Publishing packet includes MP3, title, description, transcript/show notes, disclosures, source article URL, and corrections link.
- [ ] MP3 is mono, 44.1 kHz, 64-96 kbps, `audio/mpeg`, normalized near -16 LUFS, and under 10 MB.
- [ ] Audio is staged outside git in Podcaster-owned storage with retention and cleanup metadata.
- [ ] Manual Spotify/platform publishing path is documented for the operator.
- [ ] External episode URL is recorded after publish.
- [ ] Website, if updated, links only to the external podcast/platform page and does not host podcast consumption.
- [ ] Spotify/API automation remains unimplemented until research verifies support and a design is accepted.
- [ ] Total cost ledger is updated for TTS, staging storage, script generation, validation, platform/provider costs, and monthly guardrails pass.
- [ ] SquadScope weekly crawl/analyze/generate/deploy behavior, publish manifests, article gates, and deploy success criteria are unchanged.
- [ ] Repository/project boundary and Azure resource ownership are approved before any infrastructure code or production secret is added.
- [ ] Privacy and methodology pages match actual providers, storage, platform links, analytics, and support/payment options.

---

## Definition of Done for MVP

The MVP is done when Podcaster consumes a confirmed normal weekly article's post-publish artifact/API/URL or a manual operator input and creates a reviewed, source-backed two-host episode; passes the Podcaster review gate; synthesizes it with the Phase 2-selected provider; stages validated MP3/transcript/show notes/manifests/publishing packet in Podcaster-owned Azure Blob Storage with retention/cleanup; enables an operator to manually publish to Spotify or the selected podcast platform; records the external episode URL; optionally exposes only a configurable website link to that external podcast/page; records total cost; and leaves SquadScope weekly article publishing behavior, manifests, deploys, and success criteria unchanged whether podcast generation succeeds, fails, or never runs.
