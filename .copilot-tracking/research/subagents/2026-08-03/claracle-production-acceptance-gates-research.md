<!-- markdownlint-disable-file -->
# Claracle Production Acceptance Gates Research

## Status

Complete as of 2026-08-03 for current `main` SHA
`4b7c5cf506b2e8b73350ff94ce80669c93810e66`.

## Research Scope

Assess which production-facing Claracle relaunch acceptance gates can be evidenced on current `main` without credentials or secret disclosure:

* GA consent behavior
* Google Search Console and sitemap processing observable state
* Social, Open Graph, and Twitter metadata
* Schema.org and JSON-LD
* Production feeds
* Visual capture
* Automated accessibility

For each gate, identify exact executable checks, expected outputs, limitations, and actions that still require human authority.

## Sources

### Owning and follow-up records

* .copilot-tracking/plans/2026-08-02/claracle-relaunch-followup-execution-plan.instructions.md
* docs/review/data-observatory-relaunch/owner-action-register.md
* docs/review/data-observatory-relaunch/README.md
* docs/review/data-observatory-relaunch/status-of-record.md
* docs/review/data-observatory-relaunch/screenshots/README.md
* .copilot-tracking/research/subagents/2026-08-02/claracle-ga4-gsc-followup-research.md
* .copilot-tracking/research/subagents/2026-08-02/claracle-acceptance-gates-followup-research.md

### Implementation and executable contracts

* hugo.toml
* layouts/partials/analytics.html
* layouts/partials/cookie-consent.html
* layouts/partials/seo.html
* tests/test_rendered_seo_metadata.py
* tests/test_topic_hubs.py
* tests/visual/observatory-analytics.spec.mjs
* tests/visual/observatory-a11y.spec.mjs
* tests/visual/a11y-perf.spec.mjs
* tests/visual/playwright.config.mjs
* scripts/design/verify-visual.mjs
* scripts/design/lighthouse-gates.mjs
* .github/workflows/ci.yml

### Live and external surfaces

* <https://claracle.com/>
* <https://claracle.com/weekly/2026/w31/>
* <https://claracle.com/topics/ai-coding-agents/>
* <https://claracle.com/data/most-starred-mcp-projects/>
* <https://claracle.com/repo/anthropics-claude-code/>
* <https://claracle.com/robots.txt>
* <https://claracle.com/sitemap.xml>
* <https://claracle.com/index.xml>
* <https://claracle.com/weekly/index.xml>
* <https://claracle.com/topics/ai-coding-agents/index.xml>
* [Current main CI run 30839710156](https://github.com/jmservera/SquadScope/actions/runs/30839710156)
* [Schema.org Validator](https://validator.schema.org/)
* [Google Rich Results Test](https://search.google.com/test/rich-results)
* [Meta Sharing Debugger](https://developers.facebook.com/tools/debug/)
* [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/)

## Findings

### Executive conclusion

Three production-facing surfaces have strong credential-free evidence now:

1. Representative live pages emit complete, internally consistent Open Graph and Twitter metadata and parseable, page-appropriate JSON-LD.
2. The production sitemap and site, weekly, and topic feeds return valid XML with current absolute Claracle links.
3. The exact current `main` SHA has a successful production-equivalent CI job whose rendered SEO, axe/responsive, analytics, and Lighthouse steps all passed.

These results do not close the acceptance record by themselves. Production consent behavior still needs a live browser observation; GSC processing is private property state; social and structured-data debuggers still need retained conclusions; visual and accessibility acceptance still require named reviewers. The absence of a production GSC verification meta tag is not a failure after ownership has already been verified, but it also cannot prove property or sitemap-processing state.

### Gate assessment

| Gate | Credential-free evidence available now | Current result | Remaining limitation or authority |
| --- | --- | --- | --- |
| GA consent behavior | Repository contract and exact-current-SHA CI evidence | Production source has GA configuration and consent UI. CI passes fresh, reject, accept, reload, withdrawal, cookie clearing, bounded-event, and frame-local consent tests using `G-TEST-OBSERVATORY` | CI tests a local production build, not the live origin. A production Playwright attempt was blocked before navigation by missing `libnspr4` and `libnss3`. jmservera and Hermes must retain denied and granted live network/cookie observations without identifiers |
| GSC and sitemap processing | Public robots, sitemap HTTP, XML parsing, and owner attestation in the existing register | `robots.txt` advertises the root sitemap. The sitemap returns `200 application/xml`, root `urlset`, 1,477 URLs, and absolute Claracle locations. Production has no GSC verification meta tag | Public probes cannot reveal GSC Submitted/Success processing, discovered URLs, indexed URLs, excluded URLs, or inspection state. jmservera or a delegated Search Console user must review the property and record the processed conclusion |
| Social, Open Graph, and Twitter metadata | Live source parsing plus rendered site contract | Home, weekly, topic, data, and repository pages had no missing required fields; `og:url` matched canonical; Twitter image and alt matched Open Graph; dimensions were `1200x630` | Source correctness does not prove a platform scraper's preview. Meta explicitly requires Facebook login. Amy or a named reviewer must retain homepage and representative-article debugger conclusions; LinkedIn inspection also needs a retained reviewer result |
| Schema.org and JSON-LD | Live JSON parsing plus page-type rendered tests | Home had no page schema by design. Weekly emitted `BreadcrumbList` and `Article`; topic emitted `BreadcrumbList`, `CollectionPage`, and `ItemList`; data emitted `BreadcrumbList`, `Dataset`, and `ItemList`; repository emitted `BreadcrumbList`, `WebPage`, and `SoftwareSourceCode` | Parseability and type presence do not equal Google rich-result eligibility. Schema.org Validator is public; Google Rich Results accepts public URLs and may require reCAPTCHA. Amy or a named reviewer must retain tool conclusions |
| Production feeds | Public HTTP and XML parsing | Site feed: `200 application/xml`, RSS, 52 items. Weekly feed: `200 application/xml`, RSS, 12 items. AI Coding Agents feed: `200 application/xml`, RSS, 1 current W32 item. All inspected link/guid values were absolute Claracle URLs | The response gate can be evidenced now. The owning acceptance record still needs the tested targets, date, revision or deployed-content marker, reviewer, and conclusion |
| Visual capture | Public pages are reachable and W32 now populates the AI Coding Agents hub with one weekly issue | The content prerequisite that was missing from the historical capture is now present | No refreshed matrix was captured. `verify-visual.mjs` covers only five pages, eight viewports, and two themes (80 static screenshots), not the ten-surface interaction matrix. Local Chromium lacks host libraries. The visible footer still says `Generated 2026-05-25`, which should be dispositioned in visual review. Amy must accept or reject the final matrix |
| Automated accessibility | Exact-current-SHA public CI job and checked-in axe/responsive contracts | CI run 30839710156, Production site job 91773480737, passed `Run axe and responsive browser gates` and `Run Lighthouse gates`. The axe contract rejects serious or critical WCAG 2.1 A/AA findings on topic, data, repository, chart, and tool routes; responsive tests cover overflow, labels, keyboard focus, modal focus, chart alternatives, and 44 px targets | This is production-equivalent source evidence, not a live-origin audit or NFR-005 acceptance. Fry and a named accessibility reviewer must retain production URL, keyboard-only, and screen-reader conclusions |

### Current main CI evidence

The public Actions API identifies run `30839710156` as completed successfully for the exact current SHA. Its Production site job `91773480737` completed successfully on 2026-08-03 and includes these successful steps:

* `Run rendered SEO and link contracts`
* `Check internal links`
* `Run axe and responsive browser gates`
* `Run Lighthouse gates`
* `Upload production quality reports`

The `production-quality-reports` artifact is unexpired, is tied to the exact SHA, and expires on 2026-09-02. Artifact retention strengthens reproducibility but does not convert a local production build into a live-origin observation.

## Executable Checks

### Public production response and XML check

```bash
for url in \
  https://claracle.com/sitemap.xml \
  https://claracle.com/index.xml \
  https://claracle.com/weekly/index.xml \
  https://claracle.com/topics/ai-coding-agents/index.xml
do
  curl --fail --silent --show-error --location \
    --output /dev/null \
    --write-out "$url status=%{http_code} type=%{content_type}\n" \
    "$url"
done
```

Expected output: every target reports `status=200 type=application/xml`.

Parse the returned documents with an XML parser, not regular expressions. Expected roots and minimum current observations are:

```text
sitemap: root=urlset entries=1477 absolute_claracle_links=True
site_feed: root=rss entries=52 absolute_claracle_links=True
weekly_feed: root=rss entries=12 absolute_claracle_links=True
topic_feed: root=rss entries=1 absolute_claracle_links=True
```

Counts are point-in-time evidence and will change after publication. Structural expectations should remain stable.

### Public discovery check

```bash
curl --fail --silent --show-error https://claracle.com/robots.txt
```

Expected relevant output:

```text
User-agent: *
Disallow:
Sitemap: https://claracle.com/sitemap.xml
```

This proves discovery and availability, not Search Console processing or indexing.

### Rendered metadata and schema contract

```bash
python3 -m pytest -q tests/test_rendered_seo_metadata.py
```

Expected output: all tests pass with Hugo installed. The suite checks every rendered HTML page for canonical and required social fields, image dimensions, Twitter/Open Graph consistency, JSON-LD parseability, absolute schema URLs, unique breadcrumbs, page-type schemas, valid XML, and the deliberate absence of a news sitemap.

For production, fetch representative HTML with `urllib.request` or `curl`, parse it with `html.parser.HTMLParser`, and parse each `script[type="application/ld+json"]` with `json.loads`. Do not print `gaMeasurementId` or `google-site-verification` values. The observed 2026-08-03 production summary is:

```text
home: ga_config=True gsc_meta=False missing_social=[] social_consistent=True dimensions=('1200', '630') jsonld_types=[]
weekly: ga_config=True gsc_meta=False missing_social=[] social_consistent=True dimensions=('1200', '630') jsonld_types=['BreadcrumbList', 'Article']
topic: ga_config=True gsc_meta=False missing_social=[] social_consistent=True dimensions=('1200', '630') jsonld_types=['BreadcrumbList', 'CollectionPage', 'ItemList']
data: ga_config=True gsc_meta=False missing_social=[] social_consistent=True dimensions=('1200', '630') jsonld_types=['BreadcrumbList', 'Dataset', 'ItemList']
repo: ga_config=True gsc_meta=False missing_social=[] social_consistent=True dimensions=('1200', '630') jsonld_types=['BreadcrumbList', 'WebPage', 'SoftwareSourceCode']
```

### Production consent-denied check

The narrow production-compatible Playwright check is:

```bash
BASE_URL=https://claracle.com \
  npx --no-install playwright test \
  --config tests/visual/playwright.config.mjs \
  tests/visual/observatory-analytics.spec.mjs \
  --project desktop-light \
  --grep 'fresh and rejected consent send no analytics data'
```

Expected output: `1 passed`. The test intercepts Google endpoints before navigation and expects no script request, collect request, custom event, or `_ga*` cookie before or after rejection. It expects only the first-party consent cookie after rejection.

Observed on this host: browser launch failed before navigation because `libnspr4` and `libnss3` are absent. Do not install system packages without operator approval. The full analytics file is not directly production-compatible because its reload fixture adds cookies for `127.0.0.1`; use the local CI contract for that path and a separately retained live granted-consent observation.

### Production-equivalent accessibility and analytics check

Build and serve exactly as `.github/workflows/ci.yml`, then run:

```bash
BASE_URL=http://127.0.0.1:1313 \
  npx --no-install playwright test \
  --config tests/visual/playwright.config.mjs \
  tests/visual/a11y-perf.spec.mjs \
  tests/visual/observatory-a11y.spec.mjs \
  tests/visual/observatory-analytics.spec.mjs
```

Expected output: all projects pass. Blocking axe findings are serious or critical WCAG 2.1 A/AA violations. Current-main evidence is the successful step in CI run 30839710156.

To audit the live origin rather than the local build, set `BASE_URL=https://claracle.com` and run the two accessibility files. Retain the Playwright JSON/HTML report and identify the deployed revision separately. Local execution remains blocked by missing browser host libraries.

### Visual capture capability check

```bash
node scripts/design/verify-visual.mjs \
  --base https://claracle.com \
  --date 2026-08-03 \
  --out /tmp/claracle-production-visual-2026-08-03
```

Expected output from the existing script: 80 screenshots and a `manifest.json`, with zero capture failures. This is a capability smoke only. It omits topic, data, repository, chart, tool, consent, and interaction coverage required by docs/review/data-observatory-relaunch/screenshots/README.md. A compliant capture must use that checklist and record revision, origin, browser, viewport, theme, consent state, interaction state, source week, limitations, reviewer, date, and conclusion.

### External validators

Credential-free structured-data checks:

* Submit the homepage and representative page types to <https://validator.schema.org/>
* Submit the representative weekly article and breadcrumb-bearing pages to <https://search.google.com/test/rich-results>

Expected output: JSON-LD parses without errors; supported types have no blocking errors; warnings are recorded and dispositioned rather than silently ignored. Google may require reCAPTCHA.

Social preview checks:

* Meta Sharing Debugger requires Facebook login
* LinkedIn Post Inspector accepts a URL for preview and cache inspection, but acceptance still needs a retained reviewer conclusion
* Raw source checks remain the credential-free fallback when a platform debugger cannot be used

## Human Authority Boundaries

| Decision or observation | Required actor | Why automation or public probing cannot close it |
| --- | --- | --- |
| Production denied and granted analytics behavior | jmservera with Hermes privacy review | Requires a private first visit, live browser network/cookie inspection, and reviewer judgment. IDs and cookie values must not enter the evidence record |
| GSC processed sitemap, indexed, and excluded state | jmservera or delegated GSC property user | Search Console property state is not public. Sitemap HTTP success and `site:` searches are not substitutes |
| Social debugger acceptance | Amy or named metadata reviewer; platform account where required | A scraper preview and cache result are platform state. Meta explicitly requires login |
| Structured-data external conclusion | Amy or named metadata reviewer | Public validators can execute without site credentials, but the acceptance record requires tested URLs, tool conclusions, reviewer, and date |
| Feed acceptance record | jmservera or delegated production reviewer | HTTP/XML evidence is available now, but only the owner can append the dated conclusion to the owning acceptance record under the current process |
| Visual acceptance | Amy or named visual reviewer | Screenshot generation is mechanical; layout, content fidelity, stale footer text, interaction states, and accept/reject disposition require review |
| NFR-005 accessibility acceptance | Fry plus a named accessibility reviewer | Automated axe, responsive, and Lighthouse success does not cover complete keyboard-only or screen-reader behavior |
| Relaunch acceptance or rollout authorization | jmservera | This research does not grant acceptance or enable either rollout flag |

No secret value, analytics identifier, GSC token, private cookie value, or protected account output is needed in any retained record.

## Follow-On Questions

* [ ] Can the final production deploy expose a non-sensitive revision marker so live-origin evidence can be tied to source without inference?
* [ ] Should the fixed `Generated 2026-05-25` footer value be corrected before the final visual matrix, or explicitly accepted as a known limitation?
* [ ] Which browser and screen-reader combination is the required NFR-005 manual target?
* [ ] Who will retain the Schema.org, Rich Results, Meta, and LinkedIn conclusions in the owning acceptance package?
* [ ] When will GSC finish sitemap processing, and what indexed/excluded counts will be recorded for the chosen baseline date range?

## Clarifying Questions

None block this research. The follow-on items require owner scheduling or acceptance decisions rather than additional repository investigation.
