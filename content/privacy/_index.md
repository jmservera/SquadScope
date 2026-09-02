---
title: "Privacy Policy"
description: "What data Claracle collects (almost none) and how third-party analytics work."
date: 2026-09-02
draft: false
---

## What we don't collect

Claracle is built to need almost no personal data. There are no accounts, no login, no signup, no comments, no contact form, and no newsletter.

Claracle itself does **not** collect, store, or process personal data on its own servers. We do not keep first-party visitor profiles, we do not run first-party tracking, and we do not store names, email addresses, payment details, or other personally identifying information. We do **not** sell data or share data with advertisers. Period.

The editorial pipeline behind Claracle analyzes public GitHub repository metadata and public press headlines to write weekly trend analysis. It does not ingest private user data.

## Who we are

Claracle is an editorial trend-analysis site published from the [jmservera/SquadScope GitHub repository](https://github.com/jmservera/SquadScope). The site operator, and the controller for the processing described in this policy, is **jmservera**, the maintainer of that repository. Claracle has no separate corporate entity, registered business address, or private contact email; all contact runs through the public GitHub issue route below. For privacy questions, use GitHub issues as the maintainer contact route: [open a SquadScope issue](https://github.com/jmservera/SquadScope/issues/new).

## Google Sign-In, OAuth, and Google Account data

Claracle does **not** implement Google Sign-In or any Google OAuth integration. The site has no accounts, no login, and no feature that requests permission from a Google Account. Claracle does not request, access, receive, store, or share any visitor's Google Account profile or account data, whether through Google Sign-In, OAuth, or any other mechanism.

The Google-related services and repository tooling relevant to Claracle are:

- **Google Analytics 4 (GA4)** — consent-gated, described below.
- **Google Fonts** — used to load the site's typefaces, described below.
- **A static Google Search Console site-ownership verification tag** — connected to the maintainer's Google account for property verification, present only where configured for a given deployment, described below.
- **A repository script that is designed to call the Google Search Console URL Inspection API**, gated behind maintainer credentials, to check indexing status for Claracle's own URLs, described below.

None of these involve Google Sign-In, OAuth, or access to a visitor's Google Account, and none of them provide Claracle with a visitor's Google Account data.

## What is collected by third parties

### GitHub Pages hosting

This site is hosted on GitHub Pages. When your browser loads any page, your IP address, user-agent, requested URL, timestamp, and similar server-log data may transit GitHub's CDN and infrastructure. GitHub controls that hosting data under the [GitHub Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement).

### Google Analytics 4

Claracle uses Google Analytics 4 (GA4) **only if you accept the analytics category** in the cookie banner. If you reject analytics, Claracle does not send GA4 events.

After consent, GA4 helps us understand whether the site is useful: page views, referrers, session duration, device/browser information, and approximate location derived from network data. The GA4 measurement ID is configured per deployment through a repository secret, not hard-coded in this page. Google's processing is governed by [Google's Privacy Policy](https://policies.google.com/privacy). You can also use the [Google Analytics opt-out browser add-on](https://tools.google.com/dlpage/gaoptout).

### Charts embedded on other sites

Claracle's official chart iframe snippet uses `referrerpolicy="no-referrer"`. If a publisher uses the snippet unchanged, the embedding page URL is not sent as the iframe request referrer. Publishers control their copied HTML and may alter that attribute.

Analytics in an embedded Claracle chart starts off. It can be enabled only when you explicitly accept Claracle analytics in the consent controls shown inside the iframe. A choice made on the embedding website is not treated as Claracle consent. Some browsers block third-party storage, so an iframe choice may not persist and the prompt may reappear; storage failure does not turn analytics on.

### Google Fonts

Claracle loads Inter and JetBrains Mono from Google Fonts. When your browser requests those font files, Google may receive request metadata such as your IP address and user-agent under [Google's Privacy Policy](https://policies.google.com/privacy).

### Google Search Console site-ownership verification

Where configured for a given deployment, Claracle includes a static `google-site-verification` meta tag in the page `<head>`. This tag is connected to the maintainer's Search Console/Google account for the purpose of proving domain ownership to Google — that is what a site-verification tag is for. It does not identify, authenticate, or connect to any **visitor's** Google Account: it does not set a cookie, does not collect visitor data, and has no relationship to Google Sign-In, OAuth, or a visitor's own Google Account.

### Google Search Console URL Inspection API (repository tooling, maintainer credential-gated)

Separately from the static site-ownership tag above, this repository includes a maintainer-oriented script (`scripts/capture_repository_url_inspection.py`) that is written to call the Google Search Console URL Inspection API to check indexing status for Claracle's own site URLs. This section discloses what the tooling is designed to request and requires; it is not a claim that authenticated calls are currently succeeding or that this tooling is in active, verified production use.

- **What it is designed to check:** categories of indexing-status data for URLs on Claracle's own site property — verdict, coverage state, robots.txt state, indexing state, page fetch state, last crawl time, canonical URLs, referring URLs, and sitemap associations.
- **What it does not do:** it does not read, request, or return any visitor's Google Account data, browsing activity, or session information. Visitors and their browsers are not involved in this tooling at all; it is scoped only to Claracle's own published URLs.
- **Credentials it requires:** the script requires a maintainer-supplied Google API bearer token (passed via a `--token-file` argument, supplied out of band and never committed to the repository) in order to run at all. No visitor session, cookie, or visitor credential is used, accepted, or capable of substituting for that token.
- **Who would run it:** if operated correctly, a project maintainer runs this on demand as a repository/publishing task. It is not triggered by visitor activity, and it has no connection to any part of the live visitor-facing site.

This disclosure describes what this repository tooling is designed and configured to do, gated behind maintainer credentials. It does not state or imply that Google has reviewed, approved, or certified this use, and it is not a representation that authenticated production calls to the API are currently being made successfully.

## Cookies we use

| Cookie name | Provider | Category | Purpose | Retention |
| --- | --- | --- | --- | --- |
| `squadscope_cookie_consent` | Claracle / Cookie Consent v3 | Essential | Stores your cookie choices so the site can remember whether analytics is allowed. This is the configured Cookie Consent v3 consent record for this site. | 182 days (about 6 months) |
| `_ga` | Google Analytics 4 | Analytics | Measures site usage by distinguishing browsers after you consent to analytics. | 13 months |
| `_ga_<container_id>` | Google Analytics 4 | Analytics | Stores GA4 session and measurement state for this site's analytics container after you consent. | 13 months |

We do **not** use analytics cookies unless you accept analytics in the cookie banner. The consent cookie is necessary because it records your choices and prevents the banner from asking again on every page. This site configures Cookie Consent v3 to keep that consent record for **182 days**, which is approximately 6 months.

GA4 on this site uses Google Tag (`gtag.js`) with GA4 cookies (`_ga` and `_ga_<container_id>`). We do not configure or rely on the legacy `_gid` cookie.

## Legal basis

For analytics, the legal basis is your consent under GDPR Article 6(1)(a). You can refuse analytics and still use the site.

For the essential consent cookie, the legal basis is Claracle's legitimate interest under GDPR Article 6(1)(f): remembering your cookie choice so we can respect it and avoid asking on every page.

## Your rights

Under GDPR Articles 15–22, you may have rights to access, rectify, erase, restrict, port, or object to processing of your personal data. You can also withdraw analytics consent at any time.

Because Claracle holds no first-party visitor data, most practical data-subject requests need to be exercised directly with the third party that controls the data: [GitHub privacy requests](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement) for hosting logs, and [Google privacy controls](https://policies.google.com/privacy#infocontrols) or [Google's privacy request tools](https://support.google.com/policies/troubleshooter/7575787) for GA4 or Fonts data. You can still [open a SquadScope issue](https://github.com/jmservera/SquadScope/issues/new) if you need help identifying the right route.

## Signal Check podcast

Claracle publishes a companion podcast, **Signal Check**, on an external podcast platform (currently Spotify). The podcast is produced using AI text-to-speech; no human voice recordings are collected or stored.

### What data the podcast pipeline processes

- **Public article text and claim ledger:** the podcast script is generated from the published Claracle article and its structured claim data. These are public materials already available on the website.
- **Text-to-speech provider:** the generated script is sent to a third-party TTS provider (currently Azure AI Speech) for audio synthesis. The provider receives the script text. No personal data about readers or listeners is included in TTS requests. Azure AI Speech processing is governed by the [Microsoft Privacy Statement](https://privacy.microsoft.com/privacystatement) and the service's data handling terms.
- **Temporary staging storage:** generated audio files are temporarily stored in Azure Blob Storage for operator review before publishing. Access is restricted to project maintainers; files are retained only until publishing is complete and then deleted per a configured retention policy.
- **Podcast platform:** published episodes are hosted on Spotify (or another platform if changed). When you listen through the platform, that platform's privacy policy applies — Claracle does not control or access listener-identifying personal data from the podcast platform. The platform may provide aggregated, non-identifying listen statistics (such as total play counts) to the podcast owner; Claracle does not use any platform-provided analytics for tracking, profiling, or advertising.

### What we do not do

- We do not collect or store listener-identifying personal data (email addresses, listening habits, or individual profiles) through the podcast.
- We do not use listener data for advertising or share it with third parties.
- We do not embed tracking pixels, analytics beacons, or advertising identifiers in podcast audio.
- We do not run dynamic ad insertion.

### AI-generated voice disclosure

All podcast audio is synthesized using artificial intelligence. The hosts are AI-generated synthetic personas produced by a text-to-speech model; no human narration is used or implied. No voice recordings are collected or stored by Claracle, and the resulting voices do not represent or impersonate any real individual. TTS models may have been trained on licensed voice talent recordings by the provider (see the provider's terms for details). AI-generated voice disclosure is included in each episode's intro, outro, show notes, and platform description.

### Future changes

If Claracle adds podcast analytics, listener support/donations, sponsorships, premium content, or changes the TTS provider or hosting platform, this privacy policy will be updated before those features launch.

## How to withdraw analytics consent

Use the **Manage cookies** button in the footer to reopen cookie preferences, turn off Analytics, and save. You can also delete Claracle cookies in your browser settings. Withdrawal stops future GA4 events from this browser; it does not automatically delete data already controlled by Google.

## Data retention

Claracle retains no first-party visitor data because it does not collect any. The consent cookie lasts 182 days so your choice is remembered.

GA4 data is retained by Google according to the deployment's Analytics settings and Google's defaults. See [Google Analytics data retention](https://support.google.com/analytics/answer/7667196) for details.

## Children's privacy

Claracle is not directed at children. The site has no accounts or first-party data collection, including for children.

## International transfers

GitHub and Google may process data in countries outside your own. GA4 data may be transferred to the United States. Google states that it relies on applicable transfer mechanisms, including the EU-US Data Privacy Framework and Standard Contractual Clauses where relevant.

## Changes to this policy

Last updated: 2026-09-02. Changes are announced through the git history of this page in the public SquadScope repository, so you can review what changed and when.

**2026-09-02:** Fixed a date inconsistency between the page frontmatter and this changelog. Added a section clarifying that Claracle does not implement Google Sign-In or Google OAuth and does not request, access, receive, store, or share any visitor's Google Account profile or account data. Documented the static Google Search Console site-ownership verification tag, clarifying that while it is connected to the maintainer's own Search Console/Google account for property-verification purposes, it does not identify, authenticate, or connect to any visitor's Google Account. Documented `scripts/capture_repository_url_inspection.py`, a repository script that is designed to call the Google Search Console URL Inspection API, gated behind maintainer-supplied credentials, to check indexing-status data for Claracle's own site URLs — worded to disclose the categories of data the tooling is designed to request without claiming that authenticated calls are currently succeeding in production, and to make clear visitor data and visitor Google Accounts are never involved. Corrected the prior list of Google-related services, which omitted this tooling, so it is now a complete and accurate enumeration. Explicitly identified jmservera as the site operator and controller. This page describes Claracle's actual current practices; it does not state or imply any Google approval, certification, or guarantee.
**2026-08-02:** Documented the no-referrer iframe snippet and frame-local, explicit analytics consent model.
**2026-06-12:** Added Signal Check podcast section covering TTS provider, staging storage, and platform disclosures.

## Contact

For privacy questions, [open a new issue in the SquadScope repository](https://github.com/jmservera/SquadScope/issues/new). Please do not include sensitive personal data in a public issue; describe the request briefly and the maintainer can suggest a safer follow-up route if needed.
