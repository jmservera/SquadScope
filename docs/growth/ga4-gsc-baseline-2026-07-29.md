---
title: GA4 and GSC Launch Baseline for 2026-07-29
description: Dated Claracle analytics and search baseline record that separates repository wiring from pending external platform evidence
author: SquadScope Squad
ms.date: 2026-08-08
ms.topic: reference
keywords:
  - google analytics 4
  - google search console
  - launch baseline
  - acceptance evidence
estimated_reading_time: 6
---

## Baseline status

The production GA4 stream and Google Search Console property are connected. On
2026-08-02, jmservera confirmed the intended GA4 stream, verified the GSC property,
submitted the root sitemap, and linked the GA4 stream to GSC. The supplied GA4 report
snapshot and the GSC Performance and Coverage exports were transcribed into this record
on 2026-08-08; numeric values now appear in the Baseline values table below. The raw
exports are retained outside the repository (they are not committed) per the evidence
policy.

The configured production target is `https://claracle.com/`, and the expected standard
sitemap target is `https://claracle.com/sitemap.xml`.

## Credential-free production observations

| Observation | Result | Date | Acceptance boundary |
| ----------- | ------ | ---- | ------------------- |
| GA configuration rendered | Present | 2026-08-02 | Does not reveal or validate the identifier, property, stream, consent behavior, or receipt |
| GSC verification meta tag | Absent | 2026-08-02 | GSC ownership remains unverified |
| Sitemap response | HTTP 200, `application/xml` | 2026-08-02 | Does not prove submission or processing in GSC |
| `GA_MEASUREMENT_ID` secret name | Present | 2026-08-02 | Secret value is not observable and must not be recorded |
| GSC property verification | Complete by owner attestation | 2026-08-02 | Property verified without requiring a public verification meta tag |
| Root sitemap submission | Complete by owner attestation | 2026-08-02 | Root `sitemap.xml` is a complete `<urlset>`, not an index of child sitemaps |
| GA4 and GSC product link | Complete by owner attestation | 2026-08-02 | Does not replace GA4 or GSC baseline values |
| Standalone embed GA configuration | Present | 2026-08-02 | The affected embed renders the same secret-backed configuration as the main site |

## Repository-verifiable implementation

| Surface                    | Repository status                         | Evidence boundary                                                                               |
| -------------------------- | ----------------------------------------- | ----------------------------------------------------------------------------------------------- |
| GA4 build parameter        | Implemented and present in production      | `deploy-site.yml` reads `GA_MEASUREMENT_ID`; public presence does not validate the protected value |
| GSC verification parameter | Available but not required by the completed verification method | `deploy-site.yml` supports `GSC_SITE_VERIFICATION` when HTML-tag verification is selected |
| Fork-safe defaults         | Implemented                               | Hugo parameters default empty, so an unconfigured build does not inherit production identifiers |
| Analytics consent gate     | Implemented in templates and browser code | Production requests and cookies require browser evidence                                        |
| Observatory events         | Implemented with a consent check          | GA4 receipt and payload inspection require browser and Realtime evidence                        |
| Sitemap generation         | Configured through Hugo                   | Production response and GSC processing require external evidence                                |

Secret values must not be copied into this file. A masked secret name or workflow
reference is implementation evidence, not proof that the protected environment contains
the secret.

## External evidence matrix

| Evidence                    | Status  | Owner                | Required proof                                                                   |
| --------------------------- | ------- | -------------------- | -------------------------------------------------------------------------------- |
| GA4 property and web stream | Complete | jmservera           | Owner confirmed the intended production stream on 2026-08-02                     |
| Consent denied behavior     | Complete | jmservera and Hermes | Private first-visit HAR (2026-08-08) shows no GA4 request and no Google host before a consent choice |
| Consent granted behavior    | Complete | jmservera and Hermes | Private-session HAR (2026-08-08) shows `gtag/js` load and two `g/collect` beacons after "Accept all", with `anonymize_ip: true` |
| GA4 Realtime receipt        | Complete by owner attestation | jmservera | GA4 declared operational on 2026-08-02; retain a redacted platform capture if formal audit evidence is required |
| GSC property verification   | Complete | jmservera           | Owner confirmed verified property on 2026-08-02                                  |
| GSC sitemap submission      | Complete | jmservera           | `https://claracle.com/sitemap.xml` submitted on 2026-08-02                       |
| GA4 and GSC product link    | Complete | jmservera           | Owner confirmed the production stream is linked to the GSC property              |
| Production sitemap response | Complete | jmservera            | HTTP 200 with `application/xml` observed on 2026-08-02                            |
| Production feed responses   | Pending | jmservera            | Dated site and topic feed response status and content types                      |

## Baseline values

Use the platform-reported date range when access is available. Do not replace missing
values with estimates such as “near zero.”

| Metric                   | Source | Date range | Baseline value | Status    |
| ------------------------ | ------ | ---------- | -------------- | --------- |
| Total sessions           | GA4    | 2026-07-11 to 2026-08-07 | 51 | Captured |
| Organic search sessions  | GA4    | 2026-07-11 to 2026-08-07 | 0 | Captured |
| Referral sessions        | GA4    | 2026-07-11 to 2026-08-07 | 33 | Captured |
| Direct sessions          | GA4    | 2026-07-11 to 2026-08-07 | 15 | Captured |
| Search impressions       | GSC    | 2026-07-09 to 2026-08-05 (last 28 days) | 149 | Captured |
| Search clicks            | GSC    | 2026-07-09 to 2026-08-05 (last 28 days) | 0 | Captured |
| Indexed pages            | GSC    | as of 2026-08-05 | 294 | Captured |
| Queries with impressions | GSC    | 2026-07-09 to 2026-08-05 (last 28 days) | 17 | Captured |

## Transcription notes (2026-08-08)

Source exports (retained outside the repository; not committed): GA4 "Instantané des
rapports" (account Blog, property claracle, window 2026-07-11 to 2026-08-07); GSC
"Performance on Search" and "Coverage" exports dated 2026-08-08 (Web search, last-28-day
window through 2026-08-05). No analytics identifier appears in these exports or in this
record.

* **GA4 sessions by source/medium** (total 51): `teams.public.onecdn.static.microsoft /
  referral` 18, `(direct) / (none)` 15, `localhost:1313 / referral` 14, `google / cpc` 2,
  `127.0.0.1:1313 / referral` 1, `chatgpt.com / ai-assistant` 1.
* **Organic search = 0**: no organic medium is present; `google / cpc` is Paid Search (2
  sessions), not organic.
* **Referral = 33** by GA4 channel grouping, but 15 of those (`localhost:1313` +
  `127.0.0.1:1313`) are the local Hugo dev server, i.e. developer testing rather than
  audience. Genuine external referral excluding local dev is **18**, all Microsoft Teams
  shares. One `chatgpt.com / ai-assistant` session is an AI-assistant referral.
* **Audience scale (GA4)**: 10 active users, 7 new; average engagement time 294.6 s.
* **GSC clicks = 0** across every day in the window. Impressions cross-check: 127 desktop
  and 22 mobile sum to 149. Average position ~12.1 desktop, ~8.4 mobile. Top page by impressions
  `https://claracle.com/weekly/2026/w25/` (58); top query `baskduf/fablecodex` (3).
* **GSC indexing (2026-08-05)**: 294 indexed, 1190 not indexed — 1182 "Discovered,
  currently not indexed", 2 "Crawled, currently not indexed", 3 redirect, 2 not found
  (404), 1 excluded by `noindex`.
* Reviewer: jmservera (owner), SquadScope Squad reconciliation, 2026-08-08.

### Structured dataset and trend convention

The numeric baseline is also stored as a machine-readable record at
`data/metrics/growth/launch-baseline-2026-07-29.json` (matching the `data/metrics/`
convention; no measurement identifier). Future GA4/GSC pulls should be appended, not
overwritten: add a new dated file `data/metrics/growth/launch-baseline-<YYYY-MM-DD>.json`
with the same schema so the set trends over time. A later reader can glob
`data/metrics/growth/*.json` to compare against this launch baseline.

## Capture procedure

1. Confirm the protected deployment environment contains the intended GA4 and GSC
   configuration without revealing either value.
2. Deploy the reviewed release revision.
3. Record consent-denied network and cookie behavior in a private browser session.
4. Grant analytics consent and record the expected request.
5. Correlate that visit with GA4 Realtime and record the observation date.
6. Confirm the submitted sitemap is processed successfully and review indexed versus
   excluded URLs in GSC.
7. Capture GA4 acquisition values and transcribe the supplied GSC performance export for the same documented
   baseline window.
8. Link the evidence from the relaunch review index and retain redacted artifacts in the
   approved evidence location.

## Production consent observations (NFR-008)

These require a live browser session against `https://claracle.com/`; they cannot be
derived from the GA4/GSC exports. The expected signals below are grounded in the shipped
implementation: the consent modal is rendered from `data/cookieconsent.json` (category
`analytics`, default off; buttons "Accept all" / "Reject all" / "Customize"), GA4 loads
through `layouts/partials/google_analytics.html`, and the same contract is asserted in
`tests/visual/observatory-analytics.spec.mjs`.

Signals to verify (DevTools → Network filtered to `gtag|collect`, and Application → Cookies):

* **Script load**: `https://www.googletagmanager.com/gtag/js?id=G-…`
* **Event beacon**: `https://www.google-analytics.com/g/collect?…`
* **Cookies**: `_ga` and `_ga_*` (auto-cleared when analytics consent is withdrawn)

Procedure:

1. Open a private window (no prior consent state) and open DevTools before loading the site.
2. Load `https://claracle.com/`; the "We use cookies" modal appears with analytics off.
3. **Denied**: click "Reject all", then navigate and trigger a tool/CSV action. Confirm no
   `gtag/js` request, no `g/collect` request, and no `_ga*` cookie. Record the date.
4. **Granted**: in a fresh private window, click "Accept all". Confirm `gtag/js?id=G-…`
   loads once, `g/collect` fires on navigation/events, and `_ga*` cookies are set. Record
   the date and retain a redacted screenshot.
5. **Withdrawal (optional)**: footer "Manage cookies" → turn Analytics off → confirm `_ga*`
   is cleared and no further `g/collect` fires.

Do not paste the measurement identifier into this record; redact the `id=` query parameter
in any screenshot.

| Scenario | Expected signal (code-grounded) | Observed | Date | Notes |
| -------- | -------------------------------- | -------- | ---- | ----- |
| Fresh / denied consent | No `gtag/js`, no `g/collect`, no `_ga*` cookie | Confirmed | 2026-08-08 | Private-session HAR before any consent choice: 10 requests, zero Google hosts, no `gtag/js`, no `g/collect` |
| Granted consent        | `gtag/js?id=G-…` loads, `g/collect` fires, `_ga*` set | Confirmed | 2026-08-08 | Private-session HAR after "Accept all": one `googletagmanager.com/gtag/js?id=G-…` load and two `g/collect` beacons (`region1.analytics.google.com`, `stats.g.doubleclick.net`); config sent `anonymize_ip: true` |
| Consent withdrawal (optional) | `_ga*` auto-cleared, no new `g/collect` | Pending | Pending | Not captured; optional |

Reviewer / date: jmservera, 2026-08-08 (private-session HAR capture; `_ga*` cookies are
set via client-side `document.cookie` rather than HTTP Set-Cookie, so the network beacons
above are the conclusive grant evidence). Raw HAR files are retained outside the
repository and are not committed.

## Acceptance rule

FR-035 connection and submission are complete. **NFR-007 baseline measurement is now
complete**: the GA4 acquisition values and the GSC Performance and Coverage exports were
transcribed on 2026-08-08 (see Baseline values and Transcription notes). The
production-consent portion of **NFR-008 is now complete**: private-session HAR captures on
2026-08-08 confirm no analytics request before consent and the expected `gtag/js` load
plus `g/collect` beacons after granting consent (see Production consent observations). The
optional consent-withdrawal capture remains outstanding but is not required for NFR-008.
