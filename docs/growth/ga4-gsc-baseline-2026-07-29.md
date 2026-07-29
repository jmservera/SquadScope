# GA4 + GSC launch baseline — 2026-07-29

Issue: jmservera/SquadScope#599
Production domain: `https://claracle.com/`
Sitemap URL: `https://claracle.com/sitemap.xml`

## Status

- Agent-complete: GA4 wiring is present and consent-gated.
- Human-blocked: jmservera must create the GA4 property, fill the measurement ID, verify Google Search Console ownership, submit the sitemap, and capture the real dashboard values.
- Privacy note: no new custom analytics events or user identifiers were added. The default page view can include path, referrer, and UTM parameters only after analytics consent.

## GA4 setup for jmservera

1. In Google Analytics, create or select the Claracle GA4 property for `claracle.com`.
2. Create a Web data stream for `https://claracle.com/`.
3. Copy the measurement ID (`G-XXXXXXXXXX`).
4. Set the production value by either:
   - adding/updating the GitHub Pages deployment secret `GA_MEASUREMENT_ID`, or
   - filling `params.ga_measurement_id` in `hugo.toml` for a direct config-based deployment.
5. Deploy, open the site in a private browser, reject analytics, and confirm no `_ga` cookies appear.
6. Accept analytics, then confirm the GA4 Realtime report receives a page view.

## Google Search Console verification for jmservera

Recommended method: Domain property with DNS TXT verification.

1. In Google Search Console, add a Domain property for `claracle.com`.
2. Copy the TXT record Google provides. It will look like:

   ```text
   google-site-verification=PASTE_GOOGLE_VALUE_HERE
   ```

3. Add that TXT record at the DNS provider for `claracle.com`.
4. Wait for DNS propagation, then click **Verify** in Search Console.
5. In Search Console, submit `https://claracle.com/sitemap.xml`.

Fallback method: URL-prefix property with HTML tag verification.

1. Add a URL-prefix property for `https://claracle.com/`.
2. Copy Google's HTML meta tag value.
3. Add the value to `params.analytics.google.SiteVerificationTag` in Hugo config, then deploy.
4. Click **Verify** in Search Console.
5. Submit `https://claracle.com/sitemap.xml`.

## Near-zero launch baseline template

Fill this after GA4 is receiving data and GSC is verified.

| Metric | Source | Date range | Baseline value | Notes |
| --- | --- | --- | --- | --- |
| Total sessions | GA4 | 2026-07-29 to 2026-07-29 | TBD | Expected near-zero before discovery work compounds. |
| Organic search sessions | GA4 | 2026-07-29 to 2026-07-29 | TBD | Use Traffic acquisition. |
| Referral sessions | GA4 | 2026-07-29 to 2026-07-29 | TBD | Use Traffic acquisition. |
| Direct sessions | GA4 | 2026-07-29 to 2026-07-29 | TBD | Use Traffic acquisition. |
| Search impressions | GSC | 2026-07-29 to 2026-07-29 | TBD | Performance report. |
| Search clicks | GSC | 2026-07-29 to 2026-07-29 | TBD | Performance report. |
| Indexed pages | GSC | 2026-07-29 | TBD | Pages indexing report. |
| Top queries | GSC | 2026-07-29 to 2026-07-29 | TBD | Record query, impressions, clicks, average position. |

### Top query rows

| Query | Impressions | Clicks | Average position |
| --- | ---: | ---: | ---: |
| TBD | TBD | TBD | TBD |
