# Podcast Generation Execution Plan

**Issue:** #297  
**Date:** 2026-06-07  
**Lead:** Leela  
**Companion PRD:** docs/PRD-podcast-generation.md

---

## Recommendation Snapshot

Build **SquadScope: Signal Check**, an 8-12 minute weekly two-host podcast generated from the published weekly article; automated MVP runs should target 8-10 minutes to honor the cost guardrail. Select the TTS provider in Phase 2 after a listening-test POC comparing Azure Speech Standard, Azure Speech HD/OpenAI voices in Azure if available, and OpenAI `tts-1` or `gpt-4o-mini-tts`; use Azure Blob Storage or CDN-backed stable public URLs for MP3s/transcripts/manifests and a separate non-blocking `podcast-generate.yml` workflow. Require claim ledger, source-backed show notes, AI voice disclosure, GitHub Environment review, cost guardrails, and RSS validation before public publish.

Key references: Azure Speech TTS (https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech), Azure Blob Storage (https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction), GitHub Pages limits (https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits), Apple podcast requirements (https://podcasters.apple.com/support/823-podcast-requirements), OpenAI TTS disclosure guidance (https://developers.openai.com/api/docs/guides/text-to-speech), FTC endorsement guidance (https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking).

---

## Guiding Constraints

- Do not commit MP3s or generated audio binaries to git.
- Podcast failures must not block weekly article publishing.
- MVP generation must require GitHub Environment `podcast-review` approval before TTS.
- Every substantive claim must be source-backed in a claim ledger.
- Disclose AI-generated voices in the first 60 seconds and in show notes.
- Do not clone or mimic real people, Hard Fork hosts, NYT branding, segment names, jingles, or phrasing.
- Keep MVP to max 5 episodes/month, max $5/month total podcast spend, and max 10 minutes/episode.
- If new Hugo data paths are added, update `hugo.toml` module mounts explicitly.
- Update privacy policy before any non-dry-run TTS provider call and before adding podcast analytics, payment providers, or non-essential tracking.

---

## Target Architecture

```text
crawl-and-publish.yml confirms normal weekly publish
  -> explicitly dispatch podcast-generate.yml with publish inputs, or operator manual dispatch
  -> load content/weekly/YYYY/Www.md and source artifacts
  -> reject dry-run/candidate-only/restore/no-AI fallback replacement modes
  -> compute article hash and idempotency key
  -> derive claims from published article and validate against available artifacts
  -> generate outline, script, show notes, transcript
  -> GitHub Environment podcast-review gate
  -> selected TTS provider synthesis
  -> ffmpeg normalize/transcode
  -> upload MP3/transcript/manifest to Azure Blob Storage
  -> generate/update /podcast/index.xml
  -> embed episode in weekly article or data-driven episode block
```

Idempotency key:

```text
week + article_hash + script_prompt_version + voice_config_hash
```

---

## Phase 0: Product and Contract Finalization

**Goal:** Lock the product contract before implementation.

### Issues

1. **Define podcast artifact schemas**
   - Files: `episode_manifest.json`, `claim_ledger.json`, `show_notes.md`, `transcript.md`, reviewed `script.md`.
   - Include week, article URL, article hash, prompt version, voice config, provider, cost, duration, byte length, disclosure status, reviewer, and publish status.
   - Acceptance: sample schema fixtures exist and document required/optional fields.

2. **Define editorial script prompt and style guide**
   - Use `SquadScope: Signal Check` format.
   - Segment order: cold open, The Signal, The Noise Check, The Gap, Receipts Round, Week Ahead, Outro.
   - Host A Curator, Host B Skeptic.
   - Acceptance: prompt requires citations, bans unsupported facts, bans copied podcast expression, and includes joke safety rules.

3. **Configure GitHub Environment `podcast-review`**
   - Use required reviewers as the MVP review mechanism.
   - Workflow uploads `script.md`, `claim_ledger.json`, `show_notes.md`, `transcript.md`, and `episode_manifest.json` for inspection, then pauses before non-dry-run TTS.
   - Acceptance: TTS cannot proceed without environment approval, and approval identity/time is recorded in the manifest.

---

## Phase 1: Script Dry Run, No Audio

**Goal:** Prove articles can become safe, useful scripts before adding TTS.

### Issues

4. **Implement claim/source extraction**
   - Input: published weekly article plus available source artifacts.
   - Output: claim ledger derived from the published article, then validated against existing analysis/publish artifacts where available, with support status and source URLs.
   - Acceptance: unsupported claims fail the gate or are marked for removal.

5. **Generate episode outline and script**
   - Output 1,200-1,700 word two-host script.
   - Include AI voice disclosure in first 60 seconds.
   - Keep jokes aimed at hype cycles, not individuals.
   - Acceptance: script passes length, segment, disclosure, and banned-phrase checks.

6. **Generate show notes and transcript**
   - Show notes include article link, source links, AI disclosure, corrections link, and sponsorship disclosure placeholder.
   - Transcript is derived from final script.
   - Acceptance: every source URL in the ledger appears in show notes or is intentionally excluded with reason.

7. **Add dry-run validation command**
   - Validate ASCII filenames, required fields, claim support, disclosure, script length, and no fake sponsor language.
   - Acceptance: command exits non-zero on missing ledger/support/disclosure.

---

## Phase 2: TTS Proof of Concept

**Goal:** Select the TTS provider using private samples before full storage/RSS infrastructure.

### Issues

8. **Update privacy policy for TTS candidates before synthesis**
   - Document candidate voice providers, data sent, retention/region if configurable, and operator-facing disclosure before any non-dry-run TTS call.
   - Acceptance: privacy PR is merged before provider credentials are used for non-dry-run synthesis.

9. **Run TTS provider listening-test POC**
   - Compare Azure Speech Standard neural voices, Azure Speech HD/OpenAI voices in Azure if available, and OpenAI `tts-1` or `gpt-4o-mini-tts`.
   - Use the same reviewed sample script, record billable characters, latency, licensing/privacy notes, voice naturalness, pronunciation, SSML/control support, and estimated total monthly cost.
   - Acceptance: provider decision is documented before storage/RSS implementation; private MP3 artifacts are generated only after `podcast-review` approval.

10. **Post-process audio with ffmpeg**
   - Mono, 44.1 kHz, 64-96 kbps, `audio/mpeg`, target -16 LUFS, under 10 MB.
   - Acceptance: validation reports duration, loudness, sample rate, bitrate, channels, and byte length.

11. **Add cost ledger and guardrails**
   - Track per-episode and monthly TTS, storage, egress/download bandwidth, script generation, validation, and CDN costs if used.
   - Enforce max 5 episodes/month, max $5/month total podcast spend, max 10 minutes; call out that egress may dominate if downloads grow.
   - Acceptance: workflow fails before non-dry-run synthesis or publish if limits would be exceeded.

---

## Phase 3: Storage and RSS

**Goal:** Publish standards-compliant podcast assets without bloating git.

### Issues

12. **Provision Azure Blob Storage path conventions**
   - Example: `podcast/YYYY/Www/squadscope-signal-check-YYYY-Www.mp3`.
   - ASCII filenames only.
   - Configure content type `audio/mpeg` and stable public anonymous read access, or CDN-backed stable public URLs. Expiring SAS URLs are prohibited for RSS enclosures.
   - Acceptance: uploaded MP3 is reachable over stable HTTPS without expiring query credentials.

13. **Validate HTTP serving requirements**
   - Apple requires public feed assets, HEAD, and byte-range support for episodes (https://podcasters.apple.com/support/823-podcast-requirements).
   - Acceptance: validation checks `HEAD`, `Accept-Ranges`, byte length, and content type.

14. **Generate podcast RSS**
   - Output `/podcast/index.xml` with RSS 2.0, stable GUID, enclosure URL/length/type, RFC 2822 pubDate, title, description, show image, transcript/show-note links.
   - Acceptance: feed validates locally and with at least one podcast-feed validator.

15. **Generate static feed without future Hugo section conflict**
   - Start with standalone static XML under `static/podcast/index.xml` for isolated MVP.
   - Document that this must not conflict with a future Hugo `content/podcast/` section; if that section is added, remove or replace static XML generation so one feed owner remains.
   - Acceptance: no missing module mounts if data files are added, and build/feed validation proves only one `/podcast/index.xml` owner exists.

---

## Phase 4: Site Integration

**Goal:** Make episodes discoverable from the article and site.

### Issues

16. **Add Hugo `podcast-episode` shortcode/partial**
   - Add audio player or link block to matching weekly article after episode publish.
   - Include transcript, show notes, AI voice disclosure, and correction link.
   - Acceptance: weekly article renders through the shortcode/partial while `unsafe = false` remains unchanged.

17. **Add podcast landing page**
   - Explain show format, disclosure, feed link, correction path, and methodology.
   - Acceptance: page builds in Hugo and links to `/podcast/index.xml`.

18. **Update methodology and privacy pages**
   - Methodology: explain article-to-podcast transformation and safety gates.
   - Privacy: document selected voice provider before non-dry-run TTS, Blob hosting logs, analytics/payment providers if used.
   - Acceptance: public docs match actual providers and data flows before launch.

---

## Phase 5: Launch Controls

**Goal:** Enable reliable weekly operation.

### Issues

19. **Create `podcast-generate.yml` with safe triggering**
   - Preferred automated trigger: `crawl-and-publish.yml` explicitly dispatches `podcast-generate.yml` only after confirmed normal publish, passing week, article path/URL, source run ID, publish mode, and artifact identifiers.
   - Include manual `workflow_dispatch` for selected week. Do not naively use `workflow_run`; if used later, fetch and verify triggering run inputs/artifacts before synthesis.
   - Dry-run, candidate-only, restore, failed, or no-AI fallback replacement runs must not synthesize audio.
   - Must be non-blocking relative to `crawl-and-publish.yml`.
   - Acceptance: failed podcast run does not fail or roll back article publishing, and unsafe publish modes are rejected before TTS.

20. **Add GitHub Environment `podcast-review` gate**
   - Require environment approval after script generation and before TTS.
   - Reviewers inspect `script.md`, `claim_ledger.json`, `show_notes.md`, `transcript.md`, and `episode_manifest.json`.
   - Acceptance: unapproved scripts stop before synthesis.

21. **Add observability**
   - Log episode key, provider, duration, cost estimate, byte length, validation results, and publish URL.
   - Do not log secrets or full provider credentials.
   - Acceptance: operator can diagnose failures from workflow summary.

22. **Pilot launch with one back-catalog episode**
   - Generate one recent weekly episode as a pilot.
   - Do not submit to directories until RSS and safety checks pass.
   - Acceptance: reviewer signs off on audio quality, citations, disclosure, and feed validity.

---

## Phase 6: Quality and Monetization Experiments

**Goal:** Improve quality and revenue only after trust and reliability.

### Issues

23. **Add licensed music/SFX later, if desired**
   - MVP is voice-only. Select a licensed track/effect only in a later issue, and record license details in the episode manifest.
   - Acceptance: no music/SFX ships until license, attribution/disclosure, loop/edit rules, and reviewer approval criteria are documented.

24. **Add support/donation links**
   - Ko-fi/Patreon/PayPal/Stripe redirects only; do not store payment data.
   - Acceptance: privacy page and disclosure copy are updated.

25. **Define sponsorship policy**
   - FTC requires material connections to be disclosed clearly and conspicuously (https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking).
   - Acceptance: sponsor copy template discloses before sponsor segment and forbids sponsor influence over rankings.

26. **Evaluate premium feed or dynamic ads**
   - Defer until audience metrics justify complexity.
   - Acceptance: privacy, consent, payment, RSS auth, and disclosure designs are approved before implementation.

---

## Implementation Issue Creation Gate

Before implementation begins, create or update GitHub issues for every P0/P1 row below. This correction pass only amends the docs; it does not need to create the implementation issues. The P0/P1 set must include the rubber-duck P0s: `podcast-review` environment approval, safe explicit dispatch/trigger gating, privacy-before-TTS sequencing, Phase 2 provider comparison, stable enclosure URL strategy, Hugo shortcode/partial embed, static RSS/Hugo section conflict guard, voice-only MVP/music licensing deferral, claim-ledger derivation/validation, and total podcast cost guardrails.

## Suggested Issue Breakdown

| Priority | Issue title | Owner | Depends on |
| --- | --- | --- | --- |
| P0 | Define podcast artifact schemas and idempotency key | Leela/Bender | PRD approval |
| P0 | Define Signal Check editorial prompt and safety style guide | Farnsworth/Hermes | PRD approval |
| P0 | Implement claim ledger extraction and validation | Farnsworth/Fry | schemas |
| P0 | Generate dry-run scripts/show notes/transcripts | Farnsworth | prompt, ledger |
| P0 | Configure GitHub Environment `podcast-review` gate | Hermes/Leela | dry run |
| P1 | Update privacy policy for TTS provider candidates | Hermes/Leela | prompt, ledger |
| P1 | Run TTS provider listening-test POC and select provider | Bender/Farnsworth | privacy update, review gate |
| P1 | Add safe explicit podcast workflow dispatch gating | Hermes/Bender | dry run |
| P1 | Add ffmpeg audio validation and normalization | Bender/Fry | TTS POC |
| P1 | Add total podcast cost ledger and monthly guardrails | Hermes/Bender | TTS POC |
| P1 | Upload podcast assets with stable public Blob/CDN URLs | Bender | audio validation |
| P1 | Generate static podcast RSS without Hugo section conflict | Bender/Fry | storage |
| P1 | Add Hugo podcast-episode shortcode/partial embed | Bender | RSS/storage |
| P1 | Update methodology and privacy pages for podcast launch | Hermes/Leela | provider choices |
| P2 | Pilot one back-catalog episode | Leela/Farnsworth | P1 complete |
| P2 | Add licensed music/SFX only after manifest license design | Farnsworth/Hermes | MVP pilot |
| P2 | Add support/donation links | Hermes | privacy update |
| P3 | Evaluate ads, premium feed, or live events | Hermes/Leela | audience metrics |

---

## Phase Acceptance Criteria

- Phase 0 is complete when schemas, prompts, and review status are documented well enough for implementation without product ambiguity.
- Phase 1 is complete when a weekly article can produce a reviewed script, transcript, show notes, and claim ledger without audio synthesis.
- Phase 2 is complete when privacy docs are updated, reviewed sample scripts are synthesized privately across candidate providers, a listening-test decision selects the MVP provider, and output fits duration, size, loudness, and total cost limits.
- Phase 3 is complete when storage and RSS validation prove public episode delivery meets podcast-client requirements.
- Phase 4 is complete when the article embed, landing page, methodology, and privacy updates accurately describe the launched experience.
- Phase 5 is complete when the non-blocking workflow can publish a pilot episode and leave article publishing unaffected by podcast failures.

## Validation Checklist for First Public Episode

- [ ] Script is 1,200-1,700 words and target duration fits the 8-12 minute format, with automated MVP output at or below 10 minutes.
- [ ] AI voice disclosure is in first 60 seconds and show notes.
- [ ] Claim ledger has no unsupported public claims.
- [ ] GitHub Environment `podcast-review` approved script artifacts before synthesis.
- [ ] Provider voice license/privacy terms are documented before non-dry-run TTS.
- [ ] No real-person voice cloning or protected podcast imitation.
- [ ] No fake sponsor language.
- [ ] No music/SFX in MVP unless a later licensed-track manifest issue is complete.
- [ ] Show notes include source URLs and corrections link.
- [ ] MP3 is mono, 44.1 kHz, 64-96 kbps, `audio/mpeg`, normalized near -16 LUFS, and under 10 MB.
- [ ] Audio is hosted outside git.
- [ ] RSS includes stable GUID, enclosure URL/length/type, RFC 2822 pubDate, and ASCII URLs.
- [ ] Audio endpoint supports HEAD and byte-range requests.
- [ ] Total cost ledger is updated for TTS, storage, egress, script generation, validation, CDN if used, and monthly guardrails pass.
- [ ] Privacy and methodology pages match actual providers and analytics.

---

## Definition of Done for MVP

The MVP is done when a confirmed normal weekly article publish explicitly dispatches a non-blocking podcast workflow that creates a reviewed, source-backed two-host episode; passes the GitHub Environment `podcast-review` gate; synthesizes it with the Phase 2-selected provider; uploads validated MP3/transcript/show notes/manifests to stable public Blob/CDN URLs; publishes a valid RSS item; embeds the episode through the Hugo `podcast-episode` shortcode/partial; records total cost; and leaves weekly article publishing unaffected if podcast generation fails.
