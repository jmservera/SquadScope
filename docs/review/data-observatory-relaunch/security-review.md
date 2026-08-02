---
title: Data Observatory Relaunch Security Review
description: Repository security and privacy review of Observatory generation, lifecycle, datasets, embeds, browser tools, analytics, and deployment secrets
author: SquadScope Squad
ms.date: 2026-08-02
ms.topic: reference
keywords:
  - security review
  - privacy
  - prompt injection
  - data observatory
estimated_reading_time: 10
---

## Review status

Repository review was reconciled with current controls on 2026-08-02. Hermes review and sign-off are pending.
NFR-004 is not accepted, and the relaunch security gate remains open until Hermes records a
disposition for every open finding.

This record does not claim production behavior, secret presence, external service configuration,
or sponsor approval.

## Scope and trust boundaries

The review covers the following data path:

1. Public GitHub metadata and external article text enter checked-in crawl artifacts.
2. Sanitizers and prompt boundaries constrain untrusted text before analysis.
3. Generated weekly content, taxonomy registries, candidate evidence, repository histories, and
   lifecycle state become repository-reviewed inputs.
4. Generators produce public Markdown, JSON, CSV, and Hugo pages.
5. Hugo publishes static HTML, same-origin datasets, browser scripts, and embeddable chart frames.
6. Optional analytics loads only through the consent and build-secret path.
7. GitHub Actions holds deployment and Podcaster credentials outside generated content.

The principal boundaries are external text to the analysis prompt, analysis output to generated
frontmatter, repository data to public datasets, generated JSON to browser DOM, Claracle pages to
GitHub links, third-party sites to Claracle embed frames, and Actions secrets to public build output.

## Surface review

### Sanitization and prompt injection

`scripts/sanitize_repo_content.py` detects known injection phrases, escapes untrusted boundary
markers, applies length limits, and recursively sanitizes repository payloads. Prompt assembly fences
untrusted content, adds closing constraints, and uses canary leak detection. The standard test suite
contains prompt lint and red-team coverage.

`scripts/generate_content.py` revalidates generated frontmatter length, injection phrases, and
boundary markers. Hugo keeps `markup.goldmark.renderer.unsafe = false`, so generated Markdown cannot
introduce arbitrary raw HTML through normal rendering.

Residual risk remains because phrase matching cannot identify every semantic injection. New external
fields must pass through the same sanitization and boundary path before prompt use.

**SEC-05 recommendation for human decision:** accept the semantic false-negative risk only as a
defense-in-depth residual risk while retaining input sanitization, untrusted-content fencing, closing
prompt constraints, canary leak detection, output and frontmatter validation, prompt lint, and the
red-team corpus. Phrase matching detects known lexical patterns; it cannot reliably identify novel
wording, translation, encoding, or semantic paraphrases with equivalent intent. The retained controls
reduce the chance that one miss reaches publication but do not prove semantic detection. This is an
implementation-supported recommendation, not an accepted risk; Hermes must approve, reject, or
require an additional semantic classifier.

### Candidate-title abuse

Candidate discovery combines repository-controlled topics, weekly tags, and analyzed headings.
Canonical and ignored terms reduce noise, and dynamic creation is disabled. `manage_topic_hubs.py`
now bounds candidate titles through `sanitize_text()`, rejects line breaks, boundary markers, HTML,
Markdown syntax, control characters, and known injection phrases, and serializes frontmatter through
structured YAML. `tests/test_topic_hubs.py` verifies that unsafe titles fail before any mutation.

The implementation condition for this finding is complete. Dynamic creation remains disabled until
Hermes verifies the control and a human reviews the evidence and exact output for the approved canary.

### Lifecycle evidence and deletion

Repository creation is disabled. When separately enabled, `observatory_repos.py` treats absence from
a crawl as insufficient deletion evidence. Reviewed lifecycle overrides and a persisted ledger carry
status. Confirmed deletions receive `deletion_confirmed_at` and `retained_until`; removal occurs only
after the configured three-year retention period and only for generator-owned pages.

The remaining risk is operator error in a lifecycle override. Review must pair the override, source
evidence, ledger diff, aliases, generated page, and any expiry removal. Hermes must review deletion
evidence policy before NFR-004 acceptance.

`tests/test_observatory_repos.py` now exercises rename aliases, archive evidence, confirmed deletion,
three-year retention, expiry removal, absence that fails closed, and stable-ID migration. These
fixtures prove implementation behavior, not that the production corpus contains stable IDs or a
reviewed lifecycle transition.

### Public dataset exposure

Observatory JSON and CSV outputs are intentionally public. They contain public repository metadata,
weekly observations, topics, derived metrics, and provenance. They must not contain Actions inputs,
private repository data, prompt transcripts, credentials, email addresses, analytics identifiers,
or local filesystem paths.

`scripts/export_observatory_dataset.py` now defines exact production allowlists for the CSV,
top-repository metadata objects, and the metadata document. It also restricts `source_files` to the
eleven expected checked-in paths under `data/raw/` and
`data/archive/recovered-W23-W29/`. Runtime validation rejects added or missing keys, keeps
`metadata.fields` synchronized with the CSV schema, and requires weekly count keys to equal the
exported week list.

| Classification | Allowed fields |
| -------------- | -------------- |
| Public source identity | `repository`, `url`, `primary_language`, `latest_license`, `top_topics` |
| Public observations | `latest_stars`, `first_observed_stars`, `max_forks_observed`, `seen_in_trending`, `seen_in_new` |
| Derived public metrics | `rank_by_latest_stars`, `first_seen_week`, `last_seen_week`, `weeks_observed`, `observed_star_change` |
| Release metadata | Dataset/version/timestamp/source/selection/license, bounded counts and rankings, exact CSV fields, allowlisted source paths, exposure statement |

Publication remains a data-classification boundary. Any new CSV, metadata, or nested-object field
requires an intentional allowlist change, an exact-schema test update, and Hermes privacy review.
The executable policy is implementation evidence, not approval.

### Embed privacy and attribution

Embeddable charts are static Claracle iframe endpoints with visible attribution. The official
snippet now sets `referrerpolicy="no-referrer"`, so a publisher using it unchanged does not send the
embedding page URL as the iframe request referrer. Publishers control their own markup and can remove
or replace this attribute; Claracle cannot enforce the policy after a snippet is copied.

Analytics inside the iframe is frame-local, default-off, and enabled only after the visitor explicitly
accepts Claracle analytics in the consent UI rendered inside that frame. Consent collected by the
embedding site is neither inferred nor transferred. Browser third-party-storage restrictions may
prevent the Claracle consent choice from persisting, which can cause the frame to ask again, but
storage failure never enables analytics. The adapter records `chart_embed_view` only after the
frame-local consent callback enables it.

Rendered-snippet assertions, consent-wiring tests, and the Observatory browser analytics test provide
repository-executable evidence for this model. Production network/storage behavior and publisher
modifications remain outside repository control, so Hermes privacy disposition is still pending.

### Browser tool URL and DOM handling

The Star Velocity Explorer fetches a rendered same-origin dataset, checks for a repository array,
and uses DOM creation plus `textContent` for repository-controlled labels. It does not assign source
data through `innerHTML`. Outbound repository URLs are parsed and accepted only for HTTPS links on
`github.com`; invalid values become `#`. The browser sends no authenticated GitHub request and stores
no user query.

The result list is limited to 25 rendered rows, but the full generated dataset is downloaded and
filtered in memory. Dataset size and malformed numeric values are availability concerns, not a
credential boundary. Amy and Fry own performance and malformed-payload regression coverage.

### Analytics and privacy

The analytics identifier defaults empty and enters the production build through
`GA_MEASUREMENT_ID`. Cookie Consent controls analytics state, and Observatory events return without
sending when consent is absent or `gtag` is unavailable. Tool events contain bounded action names,
tool ID, and page path. Chart events may include a referrer host.

Repository inspection does not prove first-visit network behavior, cookie behavior, GA4 receipt, or
production secret configuration. Those checks remain external acceptance evidence.

### Secret handling and cross-repository calls

The deploy workflow maps `GA_MEASUREMENT_ID` and `GSC_SITE_VERIFICATION` from GitHub Actions secrets
to Hugo parameters. Forks do not inherit those secrets. Podcaster smoke and publish workflows use
`PODCASTER_API_KEY` from protected Actions contexts. Generated browser code contains no credential
for GitHub, GA4 administration, GSC, or Podcaster.

Secret values must never be copied into evidence, screenshots, command output, fixtures, or generated
datasets. Workflow logs and environment scoping require URL review. A successful repository test
does not prove protected-environment configuration or a downstream Podcaster run.

## Findings and dispositions

| ID     | Finding                                                                                    | Severity      | Owner                 | Disposition                                                                                                 |
| ------ | ------------------------------------------------------------------------------------------ | ------------- | --------------------- | ----------------------------------------------------------------------------------------------------------- |
| SEC-01 | Dynamic hub candidate titles require bounded sanitization and structured serialization      | High          | Farnsworth and Hermes | Implemented; adversarial rejection and structured YAML are tested, Hermes verification pending             |
| SEC-02 | Embed snippets require an explicit referrer policy and cross-origin consent does not transfer | Medium        | Amy and Hermes        | Implemented and tested: official snippet uses no-referrer; frame-local analytics remains default-off until explicit Claracle consent; Hermes disposition pending |
| SEC-03 | Public export fields need a documented allowlist to prevent future accidental expansion    | Medium        | Bender and Hermes     | Implemented and tested: exact CSV, metadata, nested-object, and source-path allowlists; Hermes policy approval pending |
| SEC-04 | Lifecycle deletion depends on manually reviewed overrides                                  | Medium        | Bender and Hermes     | Rename, archive, deletion, retention, expiry, and fail-closed fixtures pass; production-policy disposition pending |
| SEC-05 | Phrase-based injection detection has known semantic false-negative risk                    | Medium        | Hermes and Farnsworth | Defense-in-depth accepted-risk recommendation is documented and executable controls are retained; no risk acceptance has been granted |
| SEC-06 | GA4, GSC, and Podcaster secret behavior is not proven by repository inspection             | Medium        | URL and jmservera     | External verification pending; never record secret values                                                   |
| SEC-07 | Browser tool uses safe DOM and a restricted outbound URL policy                            | Informational | Amy                   | Repository control verified; production and accessibility behavior pending                                  |
| SEC-08 | Raw HTML rendering remains disabled                                                        | Informational | Amy and Hermes        | Repository control verified; Hermes sign-off pending                                                        |

## Required evidence before acceptance

- Hermes records approval, rejection, or accepted-risk rationale for SEC-01 through SEC-06
- Hermes verifies the implemented candidate-title sanitizer and adversarial rejection before dynamic topic creation is enabled
- Embed privacy behavior has a documented and tested disposition
- Public dataset schema receives a field-level privacy review
- Lifecycle fixtures demonstrate rename, archive, confirmed deletion, retention, and expiry
- A private first visit proves no analytics request or cookie before consent
- A consented visit proves only the expected bounded analytics events
- Workflow review confirms secrets remain scoped and masked
- Podcaster evidence records a downstream conclusion without exposing its API key

## Sign-off

| Reviewer  | Role                                 | Status  | Date    | Notes                                                     |
| --------- | ------------------------------------ | ------- | ------- | --------------------------------------------------------- |
| Hermes    | Security and threat analysis         | Pending | Pending | Required for NFR-004; no sign-off has been supplied       |
| URL       | DevSecOps workflow and secret review | Pending | Pending | Required for protected workflow and secret-scope evidence |
| jmservera | Sponsor and production owner         | Pending | Pending | Required for production rollout acceptance                |

NFR-004 status: **Pending security acceptance**. Repository implementation alone does not close it.
