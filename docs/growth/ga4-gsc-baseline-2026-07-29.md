---
title: GA4 and GSC Launch Baseline for 2026-07-29
description: Dated Claracle analytics and search baseline record that separates repository wiring from pending external platform evidence
author: SquadScope Squad
ms.date: 2026-08-02
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
submitted the root sitemap, and linked the GA4 stream to GSC. A Search Console
performance export was supplied for the dated baseline, but its numeric values have not
yet been transcribed into this record.

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
| Consent denied behavior     | Pending | jmservera and Hermes | Private first-visit network and cookie evidence showing no GA4 request or cookie |
| Consent granted behavior    | Pending | jmservera and Hermes | Network evidence showing the expected GA4 request after consent                  |
| GA4 Realtime receipt        | Complete by owner attestation | jmservera | GA4 declared operational on 2026-08-02; retain a redacted platform capture if formal audit evidence is required |
| GSC property verification   | Complete | jmservera           | Owner confirmed verified property on 2026-08-02                                  |
| GSC sitemap submission      | Complete | jmservera           | `https://claracle.com/sitemap.xml` submitted on 2026-08-02                       |
| GA4 and GSC product link    | Complete | jmservera           | Owner confirmed the production stream is linked to the GSC property              |
| Production sitemap response | Complete | jmservera            | HTTP 200 with `application/xml` observed on 2026-08-02                            |
| Production feed responses   | Pending | jmservera            | Dated site and topic feed response status and content types                      |

## Baseline values

Use the platform-reported date range when access is available. Do not replace missing
values with estimates such as “near zero.”

| Metric                   | Source | Date range | Baseline value | Status       |
| ------------------------ | ------ | ---------- | -------------- | ------------ |
| Total sessions           | GA4    | Pending    | Pending        | Not captured |
| Organic search sessions  | GA4    | Pending    | Pending        | Not captured |
| Referral sessions        | GA4    | Pending    | Pending        | Not captured |
| Direct sessions          | GA4    | Pending    | Pending        | Not captured |
| Search impressions       | GSC    | Pending    | Pending        | Not captured |
| Search clicks            | GSC    | Pending    | Pending        | Not captured |
| Indexed pages            | GSC    | Pending    | Pending        | Not captured |
| Queries with impressions | GSC    | Pending    | Pending        | Not captured |

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

## Acceptance rule

FR-035 connection and submission are complete. NFR-007 baseline measurement and the
production-consent portion of NFR-008 remain pending until the supplied performance
export is transcribed and dated consent observations are retained.
