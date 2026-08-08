---
title: Claracle External Standards Research
description: Evidence and acceptance measures supporting BRD-CLARACLE-003
ms.date: 2026-08-08
ms.topic: reference
---

<!-- markdownlint-disable-file -->

## Status

Complete. Production observations and source material were collected on
2026-08-08. Items that require analytics access, HTTP-header inspection, or
manual assistive-technology testing remain explicitly identified as gaps.

## Research Questions

* What behavior is observable on the live Claracle homepage, yearly 2026 page, repository pages and summary, data pages, embeds, and About page?
* How should thin repository pages be replaced without avoidable search harm, including redirects, canonicals, and sitemap changes?
* How should Hugo deliver server-rendered progressive enhancement for JSON-backed filtering and sorting?
* What interaction and semantic requirements apply to tooltips across hover, keyboard focus, touch, and assistive technology?
* Which accessible visualization patterns can replace ineffective bar charts, and what alternatives must accompany charts?
* Which SEO and structured-data practices apply to a journalistic yearly article?
* How should homepage and search improvements be measured?

## Observed Live Behavior

The following findings describe the live Claracle experience observed on
2026-08-08. They are evidence about the current product, not general guidance.

### Homepage and navigation

* The homepage exposes current weekly coverage and paths into the site's
	archive, data, repository, and topic material. The production navigation does
	not yet reflect BR-008's required Weekly, Monthly, Yearly first ordering.
* The homepage is rendered as HTML rather than an empty JavaScript shell. Its
	existing server-rendered links and summaries provide a viable baseline for
	BR-002, although originality, module-selection rules, and search performance
	require editorial and analytics review rather than markup inspection alone.
* The production `robots.txt` permits crawling and declares the XML sitemap.

### Repository experience

* The live `/repo/` summary reports 263 generated repository pages. The relaunch
	status of record and source transaction evidence report 266. This is a dated
	count discrepancy, not evidence that either value should be normalized to the
	BRD's approximate 267 without an inventory.
* Sampled repository detail pages are not uniformly empty. They include weekly
	history, velocity, topics, related repositories, a direct GitHub link, and
	provenance. Some URLs may therefore carry useful content, search value, or
	inbound links that a consolidated explorer must replace before redirection.
* The observed pages support a URL-level keep, merge, or retire decision. Page
	count alone does not support redirecting every repository URL to one generic
	destination.

### Data pages and embeds

* Sampled ranking data pages already deliver the complete ranking as a
	server-rendered table with source and provenance information. JavaScript can
	add filtering, sorting, and chart exploration without replacing that useful
	HTML baseline.
* Repository names in sampled embed output appear as text rather than direct
	repository links. The requested concise summaries were not available through
	hover or keyboard focus in the observed embed.
* The existing HTML tables establish a stronger progressive-enhancement
	baseline than a client-only chart or data grid would provide.

### Yearly article

* The 2026 yearly page contains clipped generated fragments and does not read as
	a complete journalistic article. Repository inspection found that
	`scripts/generate_yearly_narrative.py` compresses output to approximately 480
	words and appends an ellipsis, while some upstream excerpts are already
	clipped.
* Increasing only the final word cap would not reliably satisfy BR-006 because
	truncated source excerpts can survive into a longer article. The owning
	generation stages and editorial review need end-to-end acceptance.

### About-page costs

* The About cost dashboard reads `data/metrics/cost-summary.json`. The published
	summary stops at W21 and displays a cumulative cost of $0.95, while site
	content extends materially beyond that period.
* Repository evidence shows the active workflow updating
	`data/metrics/token-usage.jsonl`, not the About page's summary file. At the
	time of inspection, the ledger extended beyond the summary. This supports a
	stale derived-copy root cause, subject to owner confirmation of the intended
	source of record.
* The public value does not provide a freshness contract capable of detecting
	silent staleness.

## Authoritative Guidance

This section separates first-party standards and platform guidance from the
production observations above and the product recommendations below.

### Repository URL migration

Google Search Central recommends server-side permanent redirects, such as 301
or 308, when a URL has a genuine replacement. Redirects should point directly
to the final destination, avoid chains, and generally remain in place for at
least one year. Google warns that redirecting many old URLs to an irrelevant
destination can be treated as a soft 404. Content with no replacement can
return 404 or 410 instead.

Canonical signals should agree. Google recommends absolute, self-referential
canonical URLs, consistent internal links, and sitemaps containing only the
preferred canonical URLs. During a move, update internal links and sitemaps,
monitor indexing and traffic, and use accurate `lastmod` values only for
significant page changes.

Hugo aliases generate client-side meta-refresh pages by default. Hugo can also
emit host-specific redirect configuration from alias data. Claracle therefore
needs deployment-layer 301 or 308 behavior for search migration rather than an
assumption that a default Hugo alias is an equivalent server redirect.

### Progressive enhancement with Hugo

Google states that static rendering and server-side rendering give crawlers
HTML immediately; JavaScript rendering can be delayed or fail. Essential
content, links, titles, descriptions, canonical metadata, and structured data
should therefore exist in the rendered HTML rather than depend on interaction.

web.dev recommends static or server rendering where practical and limiting
client JavaScript. Static HTML can improve first render and interaction costs,
but field data is required because lab tests do not replace real-user
measurement.

Hugo supports multiple output formats, including HTML and JSON, and can consume
local or remote structured data. Claracle can generate a versioned JSON artifact
and authoritative HTML fallback from the same normalized source instead of
maintaining two independent content paths.

### Accessible charts, tables, and controls

WCAG 2.2 requires non-text content to have a text alternative. WAI guidance for
complex images recommends a short identification plus a nearby long
description; for data charts, an actual data table is preferable where
practical. Table headers and data relationships must be programmatically
determinable.

Color cannot be the only visual means of conveying a value or state. Chart
series therefore need text, shape, line style, direct labels, or another
redundant encoding. Keyboard operation and visible focus are required for
interactive controls. Custom controls must expose programmatic names, roles,
states, and values. WCAG 2.2 AA target-size guidance sets a 24 by 24 CSS pixel
minimum unless an exception, including sufficient spacing, applies.

### Tooltips and embed summaries

WCAG Success Criterion 1.4.13 applies when hover or keyboard focus reveals
additional content. The content must be dismissible without moving focus,
hoverable when pointer movement is needed to reach it, and persistent until the
trigger is removed, the user dismisses it, or the information is no longer
valid.

Hover alone does not satisfy keyboard, touch, or assistive-technology access.
The repository link must have an accessible name, and its concise summary must
be available through focus and a touch-operable disclosure or equivalent
always-available text. Tooltip content cannot be the only location of essential
information.

### Yearly article search treatment

Google's Article structured-data guidance recommends properties that describe
the visible article, including a representative headline, author identity,
publication and modification dates, and representative images where available.
Structured data must describe content visible on the page and follow the
general structured-data policies. Valid markup does not guarantee a rich
result.

The article's canonical, title, description, heading structure, byline, dates,
images, and JSON-LD should agree with the reviewed visible article. Factual
traceability and completeness are editorial requirements; schema validation
alone cannot establish them.

### Search and performance measurement

Google Search Console's Performance report provides clicks, impressions,
click-through rate, and average position, with dimensions including query,
page, device, country, search appearance, and date. Migration evaluation should
compare equivalent pre-release and post-release windows and preserve page-level
and query-level detail rather than relying only on site-wide totals.

Current Core Web Vitals good thresholds are Largest Contentful Paint at or
below 2.5 seconds, Interaction to Next Paint at or below 200 milliseconds, and
Cumulative Layout Shift at or below 0.1, evaluated at the 75th percentile.
Mobile and desktop should be assessed separately with field data.

## Concrete Acceptance Measures

These measures are recommendations for making BRD-CLARACLE-003 testable. They
are not claims that Google, W3C, or Hugo mandates Claracle's product scope.

### BR-002 homepage and BR-008 navigation

* Capture a fixture-backed HTML response with JavaScript disabled. It must
	contain one page heading, an original summary and valid internal link for
	every enabled coverage module, and no empty wrapper for unavailable modules.
* Record module selection, freshness, and fallback rules in an approved content
	hierarchy. Test each optional-data state from deterministic fixtures.
* Validate unique title, description, self-canonical, and applicable structured
	data against the final rendered HTML.
* Verify Weekly, Monthly, and Yearly appear first, in that order, in desktop,
	mobile, keyboard, and accessibility-tree navigation.
* Establish a 28-day pre-release GSC baseline and compare it with the first 28
	complete post-release days, retaining page, query, device, clicks,
	impressions, click-through rate, and average-position exports. Use a longer
	comparison window when seasonality or low volume makes 28 days inconclusive.

### BR-003 repository consolidation

* Produce a dated inventory of every emitted repository URL with HTTP status,
	indexability, canonical, sitemap membership, useful fields, GSC clicks and
	impressions, known inbound links, and proposed keep, merge, or retire action.
* Require human approval for the inventory before removing pages. A merged URL
	receives a direct 301 or 308 only when the explorer preserves its useful
	context or offers a clearly equivalent destination. A URL without an
	equivalent returns 404 or 410 rather than redirecting to a generic page.
* Test that redirects have one hop, no loops, and the expected final canonical.
	Retain approved permanent redirects for at least one year.
* Remove retired URLs from internal links and the sitemap. Include only 200
	status canonical URLs in the new sitemap and use accurate `lastmod` values.
* Reconcile the live count of 263 with the 266-record source transaction in the
	inventory. The build gate must compare generated URLs with the versioned JSON
	record set and explain every excluded or retained record.
* Publish and validate a versioned JSON schema with repository identity,
	destination URL, summary source, data period, generation timestamp,
	provenance, and compatibility policy. Deterministic regeneration must produce
	no unexplained diff.
* With JavaScript disabled, expose the repository count, freshness, provenance,
	direct source links, and a useful browsable subset or complete paginated
	listing. With JavaScript enabled, test search, sort, filters, empty results,
	malformed or unavailable JSON, shareable state if selected, and focus
	restoration.

### BR-004 and BR-005 data exploration

* Keep the server-rendered ranking table and summary as the authoritative
	baseline. The enhanced view must not remove data, provenance, download links,
	or meaningful context from no-JavaScript output.
* Select the first delivery pages and state each chart's analytical question.
	Evaluate at least two representations using the same representative dense,
	sparse, tied, zero, long-label, and mobile-width fixtures.
* Require semantic headers and captions for tables, equivalent data access for
	charts, redundant non-color encoding, keyboard-operable controls, visible
	focus, accessible names and states, and 24 by 24 CSS pixel targets or a
	documented WCAG spacing exception.
* Define performance budgets before implementation. At minimum, the production
	release must meet good field thresholds at the 75th percentile separately on
	mobile and desktop: LCP no more than 2.5 seconds, INP no more than 200
	milliseconds, and CLS no more than 0.1. Record bundle size and lab interaction
	regressions as diagnostics, not substitutes for field results.

### BR-006 yearly article

* Add fixture-based generation tests that reject an ellipsis or clipped-source
	marker at section boundaries, incomplete sentences, raw generation artifacts,
	missing sections, and claims without source references.
* Exercise the complete pipeline from source excerpts through final article.
	Passing only a larger final word limit is insufficient when upstream excerpts
	remain truncated.
* Require named editorial approval of the complete 2026 article and retain a
	claim-to-source review record.
* Validate one visible headline, a unique description, logical headings,
	self-canonical, internal and source links, social preview, byline,
	`datePublished`, `dateModified`, representative image metadata, and Article
	JSON-LD parity with visible content. Run structured-data validation and an
	HTTP-level metadata check against the deployed page.

### BR-007 embeds

* Render every repository name as a real link to the approved GitHub or
	Claracle destination. Test safe navigation behavior in both standalone and
	embedded contexts.
* Define one summary source, sanitization rule, and maximum displayed length.
	Preserve access to the complete accessible name and summary when visual text
	is shortened.
* Verify the same summary by pointer hover, keyboard focus, and touch disclosure,
	and in the accessibility tree. Test Escape dismissal, hover transfer,
	persistence, focus order, viewport-edge collision, zoom, and narrow embeds.
* Prohibit tooltip content from obscuring its trigger or becoming the only
	source of essential repository information.

### BR-009 cost freshness

* Name the authoritative ledger and accountable owner, then generate the public
	summary from that source in the owning pipeline. Do not accept a second
	manually maintained total.
* Display covered period, generation timestamp, currency, pricing basis, and
	provenance next to the value.
* Set an owner-approved freshness threshold. The pipeline must fail closed when
	the source is missing or malformed, when the latest period exceeds the
	threshold, or when the derived cumulative value does not reconcile with the
	source ledger.
* Add a fixture that reproduces the observed W21 and $0.95 stale-summary state
	while the ledger is newer; the freshness gate must fail that fixture.

## Gaps and Clarifying Questions

The following evidence could not be established from public pages or repository
inspection and remains necessary before implementation acceptance:

* Export GSC page and query data for repository URLs, the homepage, and the 2026
	article, including the chosen pre-release baseline. Public inspection cannot
	establish indexed-query or click value.
* Inventory external inbound links to repository pages. Search Console links,
	analytics, and any available backlink source should supplement repository
	content inspection.
* Verify production HTTP status, redirect chains, response-header canonicals,
	HTML self-canonicals, and sitemap membership with an automated URL crawl. The
	current research did not approve a redirect-host implementation.
* Run the primary pages with JavaScript disabled and retain screenshots plus DOM
	assertions. Existing HTML was inspected, but a complete disabled-JavaScript
	interaction matrix was not executed.
* Complete manual keyboard, screen-reader, touch, zoom, and reduced-motion tests
	for the selected explorer, charts, and embeds. Automated semantics checks do
	not prove usable interaction.
* Decide which repository fields, default sort, filter taxonomy, summary source,
	and URL-state behavior belong in the first explorer release.
* Decide which data pages and chart questions form the first BR-004/BR-005 slice.
* Approve the yearly article's length, voice, publication cadence, and named
	editor. Standards do not determine those editorial choices.
* Confirm the cost ledger of record, pricing basis, owner, update cadence, and
	maximum acceptable age. The observed divergence identifies a defect but does
	not set the business freshness threshold.

## Sources

### Production and repository evidence

* [Claracle](https://claracle.com/)
* [Claracle repository summary](https://claracle.com/repo/)
* [Claracle 2026 yearly summary](https://claracle.com/yearly/2026/)
* [Claracle data section](https://claracle.com/data/)
* [Claracle embeds](https://claracle.com/embeds/)
* [Claracle About page](https://claracle.com/about/)
* [Claracle robots.txt](https://claracle.com/robots.txt)
* `docs/brds/claracle-post-relaunch-consolidation-brd.md`
* `scripts/generate_yearly_narrative.py`
* `data/metrics/cost-summary.json`
* `data/metrics/token-usage.jsonl`
* `layouts/partials/cost-dashboard.html`

### Search and structured data

* [Redirects and Google Search](https://developers.google.com/search/docs/crawling-indexing/301-redirects)
* [Canonical URL consolidation](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
* [Site moves with URL changes](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes)
* [Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
* [JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
* [Article structured data](https://developers.google.com/search/docs/appearance/structured-data/article)
* [Structured-data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)
* [Search Console Performance report](https://support.google.com/webmasters/answer/7576553)

### Rendering and performance

* [Rendering on the web](https://web.dev/articles/rendering-on-the-web)
* [Web Vitals](https://web.dev/articles/vitals)
* [Interaction to Next Paint](https://web.dev/articles/inp)
* [Largest Contentful Paint](https://web.dev/articles/lcp)

### Accessibility

* [WCAG 2.2 Success Criterion 1.1.1](https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html)
* [WCAG 2.2 Success Criterion 1.3.1](https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html)
* [WCAG 2.2 Success Criterion 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)
* [WCAG 2.2 Success Criterion 1.4.13](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html)
* [WCAG 2.2 Success Criterion 2.1.1](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html)
* [WCAG 2.2 Success Criterion 2.4.7](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html)
* [WCAG 2.2 Success Criterion 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
* [WCAG 2.2 Success Criterion 4.1.2](https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html)
* [WAI complex images guidance](https://www.w3.org/WAI/tutorials/images/complex/)

### Hugo

* [Hugo data sources](https://gohugo.io/content-management/data-sources/)
* [Hugo output formats](https://gohugo.io/configuration/output-formats/)
* [Hugo URL management](https://gohugo.io/content-management/urls/)
* [Hugo sitemap configuration](https://gohugo.io/configuration/sitemap/)
* [Hugo embedded templates](https://gohugo.io/templates/embedded/)
