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

The 2026-07-29 launch baseline has not been captured from GA4 or Google Search
Console. No numeric baseline value is asserted in this record. Credential-free production
checks on 2026-08-02 confirmed that Claracle renders GA configuration and serves the
sitemap, but they cannot prove the intended property mapping, consent behavior, data
receipt, GSC verification, sitemap submission, or indexing.

The configured production target is `https://claracle.com/`, and the expected standard
sitemap target is `https://claracle.com/sitemap.xml`.

## Credential-free production observations

| Observation | Result | Date | Acceptance boundary |
| ----------- | ------ | ---- | ------------------- |
| GA configuration rendered | Present | 2026-08-02 | Does not reveal or validate the identifier, property, stream, consent behavior, or receipt |
| GSC verification meta tag | Absent | 2026-08-02 | GSC ownership remains unverified |
| Sitemap response | HTTP 200, `application/xml` | 2026-08-02 | Does not prove submission or processing in GSC |
| `GA_MEASUREMENT_ID` secret name | Present | 2026-08-02 | Secret value is not observable and must not be recorded |
| `GSC_SITE_VERIFICATION` secret name | Absent | 2026-08-02 | Requires a token from the intended GSC property |

## Repository-verifiable implementation

| Surface                    | Repository status                         | Evidence boundary                                                                               |
| -------------------------- | ----------------------------------------- | ----------------------------------------------------------------------------------------------- |
| GA4 build parameter        | Implemented and present in production      | `deploy-site.yml` reads `GA_MEASUREMENT_ID`; public presence does not validate the protected value |
| GSC verification parameter | Implemented conditionally                 | `deploy-site.yml` reads `GSC_SITE_VERIFICATION`; verification is not observable                 |
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
| GA4 property and web stream | Pending | jmservera            | Dated property or stream evidence with identifiers redacted where appropriate    |
| Consent denied behavior     | Pending | jmservera and Hermes | Private first-visit network and cookie evidence showing no GA4 request or cookie |
| Consent granted behavior    | Pending | jmservera and Hermes | Network evidence showing the expected GA4 request after consent                  |
| GA4 Realtime receipt        | Pending | jmservera            | Dated Realtime evidence correlated to the consented test visit                   |
| GSC property verification   | Pending | jmservera            | Dated verified-property evidence                                                 |
| GSC sitemap submission      | Pending | jmservera            | Submission URL, date, and platform status                                        |
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
6. Verify the GSC property, submit the configured sitemap, and record platform status.
7. Capture GA4 acquisition values and GSC performance values for the same documented
   baseline window.
8. Link the evidence from the relaunch review index and retain redacted artifacts in the
   approved evidence location.

## Acceptance rule

NFR-007, FR-035, and the analytics portion of NFR-008 remain pending. They may be marked
accepted only after the external evidence matrix contains dated proof and actual values.
