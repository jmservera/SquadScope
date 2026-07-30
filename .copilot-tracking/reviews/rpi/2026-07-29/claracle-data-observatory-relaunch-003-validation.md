---
title: Claracle Data Observatory Relaunch Unit 3 Validation
description: RPI validation of PRD unit 3 requirements FR-030 through FR-035
ms.date: 2026-07-29
ms.topic: review
---

## Validation Scope

* Phase: PRD unit 3
* Requirements: FR-030 through FR-035
* Implementation plan: Missing
* Changes log: Missing
* Primary sources: PRD, BRD, repository implementation, tests, built output, and screenshots
* Status: Partial
* Validation basis: Requirements were reconstructed from the PRD and BRD because the implementation plan and changes log are missing
* Execution constraint: No checked-in `public/` output exists, and local pytest/Hugo commands were interrupted with exit 130 before producing results

## Requirement Coverage

| Requirement | Code status | Operational status | Evidence | Notes |
|-------------|-------------|--------------------|----------|-------|
| FR-030 | Ready, not re-executed | Partial | `layouts/partials/seo.html:1-37,79-82`; `tests/test_rendered_seo_metadata.py:46-80`; `.github/workflows/ci.yml:32-45`; `.github/workflows/site-preview.yml:90-104` | The renderer creates non-empty titles/descriptions and the test rejects duplicates and empties across rendered HTML. No fresh result was available in this session. |
| FR-031 | Ready, incompletely tested | Partial | `layouts/partials/seo.html:79-84`; `layouts/alias.html:8`; `layouts/embeds/baseof.html:14`; `tests/test_topic_hubs.py:281-304` | Canonicals are emitted by the active head path, aliases, and embeds. Only a representative topic canonical has a focused assertion; no all-page correctness audit exists. |
| FR-032 | Partial | Not accepted | `hugo.toml:27-31,40-42`; `layouts/partials/seo.html:40-77,84-123`; `static/images/squadscope-social-card.png`; `docs/growth/distribution-strategy.md:274-321` | All named tags are present for fallback-image pages. Width/height are omitted when a page uses a custom OG, featured, or cover image. No Facebook or X debugger evidence was found. |
| FR-033 | Partial | Not accepted | `layouts/partials/seo.html:74-77,124-166`; `tests/test_generate_data_pages.py:140-165`; `docs/review/data-observatory-relaunch/screenshots/03-topic-hub-mcp.png`; `docs/review/data-observatory-relaunch/screenshots/04-repo-ollama.png`; `docs/review/data-observatory-relaunch/screenshots/05-data-trend-page.png` | Breadcrumb JSON-LD is emitted on non-home pages and generic Article JSON-LD is emitted for weekly, monthly, yearly, data, and repo pages. Topic hubs have no hub-specific entity schema. No Rich Results Test evidence was found. |
| FR-034 | Ready, not re-executed | Partial | `hugo.toml:12-19`; `layouts/topics/list.html:14-22`; `tests/test_topic_hubs.py:281-304`; `docs/review/data-observatory-relaunch/screenshots/01-home.png`; `docs/review/data-observatory-relaunch/screenshots/03-topic-hub-mcp.png` | Hugo built-in sitemap behavior is enabled and home, section, taxonomy, and term RSS outputs are configured. Topic RSS has a focused build assertion. Reachability and XML validity were not independently established, and no news sitemap configuration was found. |
| FR-035 | Wiring ready | Failed | `hugo.toml:22-26`; `.github/workflows/deploy-site.yml:30-36,100-103`; `layouts/partials/analytics.html:1-10`; `layouts/partials/cookie-consent.html:35-83`; `layouts/partials/head.html:20-28`; `docs/growth/ga4-gsc-baseline-2026-07-29.md:7-12,39-56`; `docs/setup-secrets.md:3-28` | Secret injection, guarded verification metadata, and consent-gated GA4 loading are implemented. The repository explicitly records GSC verification, sitemap submission, GA4 Realtime receipt, and baseline values as incomplete human steps. |

## Findings

### Critical

1. FR-035 has not reached external operational acceptance. The launch baseline says GSC verification and sitemap submission remain human-blocked (`docs/growth/ga4-gsc-baseline-2026-07-29.md:7-12`), instructs the operator to verify and submit (`docs/growth/ga4-gsc-baseline-2026-07-29.md:23-37`), and leaves every GA4/GSC baseline value as `TBD` (`docs/growth/ga4-gsc-baseline-2026-07-29.md:39-56`). The setup guide likewise describes actions to perform after deployment (`docs/setup-secrets.md:17-28`). Code readiness cannot satisfy the acceptance criteria that the property is verified, the sitemap is submitted, and GA4 is receiving data.

2. FR-033 lacks an appropriate entity schema for topic hubs. The active renderer limits Article schema to `weekly`, `monthly`, `yearly`, `data`, and `repo` sections (`layouts/partials/seo.html:74-77`) and emits only BreadcrumbList for other non-home pages (`layouts/partials/seo.html:124-136`). A topic term therefore receives breadcrumbs but no hub entity such as CollectionPage. This is missing required functionality for a Must requirement, independent of the visually rendered hub shown in `docs/review/data-observatory-relaunch/screenshots/03-topic-hub-mcp.png`.

### Major

1. FR-032 does not guarantee image dimensions for every social image. The active partial emits `og:image:width` and `og:image:height` only when `$usesDefaultSocialImage` is true (`layouts/partials/seo.html:90-94`). Pages using `og_image`, `featured_image`, or `cover.image` still receive image and alt tags but no dimensions (`layouts/partials/seo.html:40-58,84-94`). The current fallback asset is present and visually matches the declared 1200 by 630 format, but the implementation does not meet the universal tag requirement for custom images.

2. FR-033 uses generic Article schema for data and repository pages without evidence that this is the intended appropriate schema. The page classifier includes both sections in `$articleSections` (`layouts/partials/seo.html:74-77`) and the only page entity emitted is Article (`layouts/partials/seo.html:138-166`). The screenshots and layouts confirm these are specialized data and repository surfaces (`layouts/data/single.html:1-35`; `layouts/repo/single.html:1-35`), but there is no Dataset, ItemList, CollectionPage, or other explicit page-type representation. The PRD does not name the exact types, so this is a specification deviation requiring product clarification rather than a definitive invalid-type claim.

3. Automated acceptance coverage stops short of FR-031 through FR-034. The rendered metadata parser records only title, description, and Google verification (`tests/test_rendered_seo_metadata.py:13-43`), while its site-wide test checks only title/description uniqueness (`tests/test_rendered_seo_metadata.py:46-80`). It does not assert canonical correctness, required Open Graph/Twitter tags, JSON-LD parseability and type by page class, sitemap validity, or root/topic feed validity. The topic test covers one canonical and one feed (`tests/test_topic_hubs.py:281-304`), and the data test only checks that the text `BreadcrumbList` appears (`tests/test_generate_data_pages.py:140-165`). This weakens regression protection for four launch-blocking requirements.

### Minor

1. FR-032 debugger acceptance is undocumented. The repository contains the fallback social card and code for all named fallback tags, but no captured Facebook Sharing Debugger or X Card Validator result for the homepage and an article. Screenshots of rendered pages cannot validate head metadata or crawler behavior.

2. FR-034 reachability and XML-validity acceptance is undocumented. Configuration and a representative topic-feed test establish code readiness, but no checked-in build output or production response evidence demonstrates that `sitemap.xml`, root `index.xml`, and every topic `index.xml` are reachable and valid.

3. The visual acceptance README overstates structured SEO verification. It says metadata and structured data are visible in screenshots and enforced by a strict uniqueness gate (`docs/review/data-observatory-relaunch/README.md:30-42`), but screenshots do not expose head tags or JSON-LD, and the uniqueness test does not validate schema.

## Evidence Review

### Requirements Sources

* FR-030 through FR-035 are defined at `docs/prds/claracle-data-observatory-relaunch.md:123-128`
* The BRD acceptance criteria are at `docs/brds/claracle-data-observatory-relaunch-brd.md:187-205`
* The seven social metadata gaps are enumerated at `docs/growth/distribution-strategy.md:274-321`
* NFR-006 requires Rich Results Test success and no duplicate titles/meta at `docs/prds/claracle-data-observatory-relaunch.md:148-151`
* NFR-007 and NFR-008 require connected discovery measurement and consent-gated GA4 at `docs/prds/claracle-data-observatory-relaunch.md:151-153`

### Active Rendering Path

`layouts/partials/head.html:10` calls `seo.html`, making `layouts/partials/seo.html` the controlling metadata and schema implementation. The older `layouts/partials/templates/opengraph.html`, `twitter_cards.html`, and `schema_json.html` files are not called by this active head path and were not treated as implementation evidence.

### Social Metadata Matrix

| Explicit requirement | Active implementation | Result |
|----------------------|-----------------------|--------|
| `og:image` with homepage fallback | `layouts/partials/seo.html:40-58,89`; `hugo.toml:27` | Met for current fallback path |
| `og:image:alt` | `layouts/partials/seo.html:59,90` | Met |
| `og:image:width` and `og:image:height` | `layouts/partials/seo.html:91-94` | Partial; fallback only |
| `article:author` | `layouts/partials/seo.html:98-100` | Met for classified article pages |
| `twitter:creator` | `layouts/partials/seo.html:66-73,121-123`; `hugo.toml:40-42` | Met |
| Homepage/fallback image asset | `static/images/squadscope-social-card.png` | Met; inspected as a 1200 by 630 Claracle card |
| Unique trend description from summary | `layouts/partials/seo.html:12-37` | Met in renderer |

### Sitemap and Feed Configuration

Hugo outputs HTML and RSS for home, sections, taxonomies, and terms (`hugo.toml:12-19`). The topic layout links its term feed (`layouts/topics/list.html:14-22`), and the focused test expects `topics/ai-coding-agents/index.xml` with absolute Claracle URLs (`tests/test_topic_hubs.py:281-304`). No news sitemap configuration or artifact was found, which matches the explicit exclusion.

### Analytics and Search Console Separation

The deploy workflow maps repository secrets to Hugo parameters (`.github/workflows/deploy-site.yml:30-36`). The analytics partial exposes a measurement ID only when configured (`layouts/partials/analytics.html:1-10`), and cookie consent initially disables GA4 and loads it only after analytics consent (`layouts/partials/cookie-consent.html:35-83`). The GSC meta tag is also conditional (`layouts/partials/head.html:20-28`). These facts establish deployable code, not ownership verification, sitemap submission, or incoming telemetry.

### Screenshots

The review gallery demonstrates visually rendered homepage, topic, repository, and data surfaces, plus the consent prompt. It corroborates page-type existence and visible RSS links. It provides no evidence for canonical tags, Open Graph/Twitter tags, JSON-LD validity, sitemap XML, feed XML, GSC state, or GA4 receipt.

### Execution Results

No implementation files were modified. Two focused pytest attempts and a Hugo command were interrupted with exit code 130 in the shared terminal before producing a result. No checked-in `public/`, sitemap, or feed output was available. Static source, workflow, test, documentation, asset, and screenshot evidence was therefore used without claiming a fresh pass.

## Coverage Assessment

Unit 3 is partially implemented and not launch-accepted.

* Code readiness is strongest for FR-030, FR-031, FR-034, and the wiring portion of FR-035
* FR-032 is complete for the current fallback-image path but incomplete for custom social images
* FR-033 emits Article and BreadcrumbList but misses a hub entity schema and leaves specialized data/repository schema semantics unresolved
* External acceptance is absent for social debuggers, Rich Results Test, production sitemap/feed reachability, GSC verification/submission, and GA4 data receipt
* Overall status is Partial because at least one required implementation is missing and FR-035's explicit acceptance criteria are not met

## Clarifying Questions

1. Which schema types are intended for topic hubs, data rankings, and repository pages? Proposed defaults for validation are CollectionPage for hubs, Dataset plus ItemList for data rankings, and ProfilePage or WebPage with a SoftwareSourceCode main entity for repository pages.

2. Is there external evidence outside the repository for a verified GSC property, accepted sitemap submission, GA4 Realtime traffic, Facebook debugger output, X card output, or Google Rich Results Test results?

3. Was the latest CI run for the implementation commit successful, especially `tests/test_rendered_seo_metadata.py` and `tests/test_topic_hubs.py`?

## Recommended Next Validations

* [ ] Run the focused pytest suite in a clean environment and attach the result
* [ ] Build the production-equivalent Hugo site and audit every HTML page for title, description, canonical, social tags, and parseable JSON-LD
* [ ] Validate schema types on one weekly article, topic hub, data page, and repository page with Google Rich Results Test or Schema Markup Validator
* [ ] Validate the homepage and a weekly article with Facebook Sharing Debugger and X card tooling
* [ ] Fetch and XML-parse production `sitemap.xml`, root `index.xml`, and every topic `index.xml`; confirm no news sitemap
* [ ] Verify the GSC property and record accepted sitemap status
* [ ] Accept analytics consent in production and capture a GA4 Realtime page view
* [ ] Replace the `TBD` GA4/GSC launch baseline values with dated measurements
