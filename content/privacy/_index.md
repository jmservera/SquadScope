---
title: "Privacy Policy"
description: "What data Claracle collects (almost none) and how third-party analytics work."
date: 2026-05-25
draft: false
---

## What we don't collect

Claracle is built to need almost no personal data. There are no accounts, no login, no signup, no comments, no contact form, and no newsletter.

Claracle itself does **not** collect, store, or process personal data on its own servers. We do not keep first-party visitor profiles, we do not run first-party tracking, and we do not store names, email addresses, payment details, or other personally identifying information. We do **not** sell data or share data with advertisers. Period.

The editorial pipeline behind Claracle analyzes public GitHub repository metadata and public press headlines to write weekly trend analysis. It does not ingest private user data.

## Who we are

Claracle is an editorial trend-analysis site published from the [jmservera/SquadScope GitHub repository](https://github.com/jmservera/SquadScope). For privacy questions, use GitHub issues as the maintainer contact route: [open a SquadScope issue](https://github.com/jmservera/SquadScope/issues/new).

## What is collected by third parties

### GitHub Pages hosting

This site is hosted on GitHub Pages. When your browser loads any page, your IP address, user-agent, requested URL, timestamp, and similar server-log data may transit GitHub's CDN and infrastructure. GitHub controls that hosting data under the [GitHub Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement).

### Google Analytics 4

Claracle uses Google Analytics 4 (GA4) **only if you accept the analytics category** in the cookie banner. If you reject analytics, Claracle does not send GA4 events.

After consent, GA4 helps us understand whether the site is useful: page views, referrers, session duration, device/browser information, and approximate location derived from network data. The GA4 measurement ID is configured per deployment through a repository secret, not hard-coded in this page. Google's processing is governed by [Google's Privacy Policy](https://policies.google.com/privacy). You can also use the [Google Analytics opt-out browser add-on](https://tools.google.com/dlpage/gaoptout).

### Google Fonts

Claracle loads Inter and JetBrains Mono from Google Fonts. When your browser requests those font files, Google may receive request metadata such as your IP address and user-agent under [Google's Privacy Policy](https://policies.google.com/privacy).

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
- **Podcast platform:** published episodes are hosted on Spotify (or another platform if changed). When you listen through the platform, that platform's privacy policy applies — Claracle does not control or receive listener analytics or personal data from the podcast platform.

### What we do not do

- We do not collect listener email addresses, listening habits, or personal data through the podcast.
- We do not use listener data for advertising or share it with third parties.
- We do not embed tracking pixels, analytics beacons, or advertising identifiers in podcast audio.
- We do not run dynamic ad insertion.

### AI-generated voice disclosure

All podcast audio is synthesized using artificial intelligence. The voices are not recordings of real people. This is disclosed in each episode's outro, show notes, and platform description.

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

Last updated: 2026-06-12. Changes are announced through the git history of this page in the public SquadScope repository, so you can review what changed and when.

**2026-06-12:** Added Signal Check podcast section covering TTS provider, staging storage, and platform disclosures.

## Contact

For privacy questions, [open a new issue in the SquadScope repository](https://github.com/jmservera/SquadScope/issues/new). Please do not include sensitive personal data in a public issue; describe the request briefly and the maintainer can suggest a safer follow-up route if needed.
