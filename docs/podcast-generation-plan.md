# Podcast Generation Execution Plan

**Issue:** #297  
**Date:** 2026-06-07  
**Lead:** Leela  
**Companion PRD:** docs/PRD-podcast-generation.md

---

## Recommendation Snapshot

Build **SquadScope: Signal Check**, an 8-12 minute weekly two-host podcast generated from the published weekly article; automated MVP runs should target 8-10 minutes to honor the cost guardrail. Use Azure AI Speech neural TTS for MVP, Azure Blob Storage for MP3s/transcripts/manifests, and a separate non-blocking `podcast-generate.yml` workflow. Require claim ledger, source-backed show notes, AI voice disclosure, human review, cost guardrails, and RSS validation before public publish.

Key references: Azure Speech TTS (https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech), Azure Blob Storage (https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction), GitHub Pages limits (https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits), Apple podcast requirements (https://podcasters.apple.com/support/823-podcast-requirements), OpenAI TTS disclosure guidance (https://developers.openai.com/api/docs/guides/text-to-speech), FTC endorsement guidance (https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking).

---

## Guiding Constraints

- Do not commit MP3s or generated audio binaries to git.
- Podcast failures must not block weekly article publishing.
- MVP generation must require human script review before TTS.
- Every substantive claim must be source-backed in a claim ledger.
- Disclose AI-generated voices in the first 60 seconds and in show notes.
- Do not clone or mimic real people, Hard Fork hosts, NYT branding, segment names, jingles, or phrasing.
- Keep MVP to max 5 episodes/month, max $5/month TTS, and max 10 minutes/episode.
- If new Hugo data paths are added, update `hugo.toml` module mounts explicitly.
- Update privacy policy before adding voice providers, podcast analytics, payment providers, or non-essential tracking.

---

## Target Architecture

```text
crawl-and-publish.yml publishes weekly article
  -> podcast-generate.yml starts after success or manual dispatch
  -> load content/weekly/YYYY/Www.md and source artifacts
  -> compute article hash and idempotency key
  -> extract claims and citations
  -> generate outline, script, show notes, transcript
  -> human review gate
  -> Azure Speech TTS
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

3. **Choose review mechanism**
   - Options: PR-based reviewed script, GitHub environment approval, issue checklist, or signed manifest.
   - Recommendation: PR or issue checklist for MVP because it is auditable and easy to operate.
   - Acceptance: reviewer approval is machine-readable before synthesis.

---

## Phase 1: Script Dry Run, No Audio

**Goal:** Prove articles can become safe, useful scripts before adding TTS.

### Issues

4. **Implement claim/source extraction**
   - Input: published weekly article plus available source artifacts.
   - Output: claim ledger with support status and source URLs.
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

**Goal:** Synthesize private test episodes cheaply and repeatably.

### Issues

8. **Configure Azure Speech credentials and voice config**
   - Use repository secrets for keys/region or managed identity if available.
   - Document selected voices and commercial license status.
   - Acceptance: no secrets in logs; voice config hash included in manifest.

9. **Add Azure Speech synthesis step**
   - Use neural TTS with SSML for two voices.
   - Track billable characters as Azure Speech bills by characters (https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech).
   - Acceptance: private MP3 artifact generated from reviewed script.

10. **Post-process audio with ffmpeg**
   - Mono, 44.1 kHz, 64-96 kbps, `audio/mpeg`, target -16 LUFS, under 10 MB.
   - Acceptance: validation reports duration, loudness, sample rate, bitrate, channels, and byte length.

11. **Add cost ledger and guardrails**
   - Track per-episode and monthly cost.
   - Enforce max 5 episodes/month, max $5/month, max 10 minutes.
   - Acceptance: workflow fails before synthesis if limits would be exceeded.

---

## Phase 3: Storage and RSS

**Goal:** Publish standards-compliant podcast assets without bloating git.

### Issues

12. **Provision Azure Blob Storage path conventions**
   - Example: `podcast/YYYY/Www/squadscope-signal-check-YYYY-Www.mp3`.
   - ASCII filenames only.
   - Configure content type `audio/mpeg` and public or signed access strategy.
   - Acceptance: uploaded MP3 is reachable over HTTPS.

13. **Validate HTTP serving requirements**
   - Apple requires public feed assets, HEAD, and byte-range support for episodes (https://podcasters.apple.com/support/823-podcast-requirements).
   - Acceptance: validation checks `HEAD`, `Accept-Ranges`, byte length, and content type.

14. **Generate podcast RSS**
   - Output `/podcast/index.xml` with RSS 2.0, stable GUID, enclosure URL/length/type, RFC 2822 pubDate, title, description, show image, transcript/show-note links.
   - Acceptance: feed validates locally and with at least one podcast-feed validator.

15. **Decide feed generation location**
   - Option A: Hugo template reads mounted data files.
   - Option B: standalone script writes static XML under `static/podcast/index.xml`.
   - Recommendation: start with standalone static XML for isolated MVP; revisit Hugo data if templates need richer integration.
   - Acceptance: no missing module mounts if data files are added.

---

## Phase 4: Site Integration

**Goal:** Make episodes discoverable from the article and site.

### Issues

16. **Add article embed**
   - Add audio player or link block to matching weekly article after episode publish.
   - Include transcript, show notes, AI voice disclosure, and correction link.
   - Acceptance: weekly article renders without raw HTML unsafe mode changes.

17. **Add podcast landing page**
   - Explain show format, disclosure, feed link, correction path, and methodology.
   - Acceptance: page builds in Hugo and links to `/podcast/index.xml`.

18. **Update methodology and privacy pages**
   - Methodology: explain article-to-podcast transformation and safety gates.
   - Privacy: document voice provider, Blob hosting logs, analytics/payment providers if used.
   - Acceptance: public docs match actual providers and data flows.

---

## Phase 5: Launch Controls

**Goal:** Enable reliable weekly operation.

### Issues

19. **Create `podcast-generate.yml`**
   - Trigger on successful article publish via `workflow_run` and manual `workflow_dispatch` for selected week.
   - Must be non-blocking relative to `crawl-and-publish.yml`.
   - Acceptance: failed podcast run does not fail or roll back article publishing.

20. **Add manual approval gate**
   - Require reviewed script status before TTS.
   - Acceptance: unreviewed scripts stop before synthesis.

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

23. **Compare higher-quality TTS providers**
   - Test Azure OpenAI voices via Azure Speech (https://learn.microsoft.com/en-us/azure/ai-services/speech-service/openai-voices) and OpenAI `gpt-4o-mini-tts` (https://developers.openai.com/api/docs/guides/text-to-speech) against Azure Speech baseline.
   - Acceptance: compare cost, license/disclosure, latency, voice quality, SSML/control, and privacy terms.

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

## Suggested Issue Breakdown

| Priority | Issue title | Owner | Depends on |
| --- | --- | --- | --- |
| P0 | Define podcast artifact schemas and idempotency key | Leela/Bender | PRD approval |
| P0 | Define Signal Check editorial prompt and safety style guide | Farnsworth/Hermes | PRD approval |
| P0 | Implement claim ledger extraction and validation | Farnsworth/Fry | schemas |
| P0 | Generate dry-run scripts/show notes/transcripts | Farnsworth | prompt, ledger |
| P0 | Add human review gate for podcast scripts | Hermes/Leela | dry run |
| P1 | Add Azure Speech synthesis proof of concept | Bender | review gate |
| P1 | Add ffmpeg audio validation and normalization | Bender/Fry | TTS POC |
| P1 | Add cost ledger and monthly guardrails | Hermes/Bender | TTS POC |
| P1 | Upload podcast assets to Azure Blob Storage | Bender | audio validation |
| P1 | Generate and validate podcast RSS | Bender/Fry | storage |
| P1 | Add weekly article episode embed | Bender | RSS/storage |
| P1 | Update methodology and privacy pages for podcast launch | Hermes/Leela | provider choices |
| P2 | Pilot one back-catalog episode | Leela/Farnsworth | P1 complete |
| P2 | Evaluate OpenAI/Azure OpenAI/MAI voice quality | Bender | MVP pilot |
| P2 | Add support/donation links | Hermes | privacy update |
| P3 | Evaluate ads, premium feed, or live events | Hermes/Leela | audience metrics |

---

## Phase Acceptance Criteria

- Phase 0 is complete when schemas, prompts, and review status are documented well enough for implementation without product ambiguity.
- Phase 1 is complete when a weekly article can produce a reviewed script, transcript, show notes, and claim ledger without audio synthesis.
- Phase 2 is complete when a reviewed script can synthesize a private validated MP3 under duration, size, loudness, and cost limits.
- Phase 3 is complete when storage and RSS validation prove public episode delivery meets podcast-client requirements.
- Phase 4 is complete when the article embed, landing page, methodology, and privacy updates accurately describe the launched experience.
- Phase 5 is complete when the non-blocking workflow can publish a pilot episode and leave article publishing unaffected by podcast failures.

## Validation Checklist for First Public Episode

- [ ] Script is 1,200-1,700 words and target duration fits the 8-12 minute format, with automated MVP output at or below 10 minutes.
- [ ] AI voice disclosure is in first 60 seconds and show notes.
- [ ] Claim ledger has no unsupported public claims.
- [ ] Human reviewer approved script before synthesis.
- [ ] Provider voice license is documented.
- [ ] No real-person voice cloning or protected podcast imitation.
- [ ] No fake sponsor language.
- [ ] Show notes include source URLs and corrections link.
- [ ] MP3 is mono, 44.1 kHz, 64-96 kbps, `audio/mpeg`, normalized near -16 LUFS, and under 10 MB.
- [ ] Audio is hosted outside git.
- [ ] RSS includes stable GUID, enclosure URL/length/type, RFC 2822 pubDate, and ASCII URLs.
- [ ] Audio endpoint supports HEAD and byte-range requests.
- [ ] Cost ledger is updated and monthly guardrails pass.
- [ ] Privacy and methodology pages match actual providers and analytics.

---

## Definition of Done for MVP

The MVP is done when a successful weekly article can trigger a non-blocking podcast workflow that creates a reviewed, source-backed two-host episode; synthesizes it with documented Azure Speech voices; uploads validated MP3/transcript/show notes/manifests to Blob Storage; publishes a valid RSS item; embeds the episode in the article; records cost; and leaves weekly article publishing unaffected if podcast generation fails.
