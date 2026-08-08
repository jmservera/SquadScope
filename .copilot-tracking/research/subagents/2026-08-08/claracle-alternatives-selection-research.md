---
title: Claracle BRD-CLARACLE-003 Alternatives Selection Research
description: Phase 2 comparison and selection of coherent end-to-end implementation, URL migration, and release sequencing approaches
author: GitHub Copilot
ms.date: 2026-08-08
ms.topic: reference
keywords:
  - claracle
  - alternatives analysis
  - progressive enhancement
  - URL migration
  - release sequencing
estimated_reading_time: 18
---

<!-- markdownlint-disable-file -->

## Research Status

Status: Complete

## Research Questions

* Which coherent end-to-end implementation approach best satisfies BRD-CLARACLE-003 while preserving Claracle's current Hugo, data-generation, accessibility, search, and delivery conventions?
* Should Claracle use progressive enhancement, a client-first JSON application, or enriched repository detail pages as the primary experience architecture?
* Should repository URL migration use blanket redirects, URL-level keep/merge/retire decisions, or deletion without redirects?
* Should the old relaunch close before redesign, or should an explicit supersession decision replace old-release acceptance?
* Which approach and sequencing policy should proceed to implementation planning, and which evidence gaps remain?

## Authoritative Inputs

* `.copilot-tracking/research/subagents/2026-08-08/claracle-codebase-surfaces-research.md`
* `.copilot-tracking/research/subagents/2026-08-08/claracle-external-standards-research.md`
* `.copilot-tracking/research/subagents/2026-08-08/claracle-delivery-quality-research.md`

## Decision Summary

Select Alternative A: progressive enhancement from shared normalized and versioned
data, with useful server-rendered HTML and scoped JavaScript enhancements. Use one
deterministic source contract to generate both the HTML baseline and JSON payloads.
Keep essential content, links, provenance, downloads, metadata, and table or list
alternatives in HTML; use JavaScript for search, sort, filters, chart exploration,
shareable state, and accessible disclosures.

For repository URLs, select URL-level keep, merge, or retire treatment. A retained URL
must remain useful and canonical. A merged URL receives a direct server-side 301 or 308
only when the destination preserves its useful context. A retired URL with no equivalent
returns 404 or 410. Blanket redirects and blanket no-redirect deletion are rejected.

For sequencing, select explicit supersession of the unaccepted relaunch revision before
redesign implementation. The sponsor should record a dated NO-GO/supersession against an
immutable revision, preserve the 64-screen and 68-check evidence as the historical
baseline, carry open accessibility and interaction findings forward, and supersede CR-05
with the BR-003 migration gate. This is governance closure without falsely claiming that
the old release passed final acceptance.

The recommendation is an integrated product and delivery architecture, not an isolated
frontend choice. It aligns the design shell, homepage, repository consolidation, data
exploration, embeds, yearly content, cost provenance, URL migration, deterministic
generation, automated gates, named human acceptance, and post-release measurement.

## Decision Criteria

The alternatives are compared against these end-to-end criteria:

* Direct satisfaction of BR-001 through BR-009 and resolution of CR-05 against BR-003
* One authoritative data path across generation, server HTML, client interaction, and downloads
* Crawlable content and controlled URL migration
* Useful no-JavaScript output and equivalent keyboard, touch, and assistive-technology access
* Deterministic builds, bounded client cost, explicit empty and error behavior, and rollback
* Compatibility with Hugo, checked-in generated data, current tests, current delivery gates, and Squad ownership
* Binary acceptance evidence at decision, repository-contract, human-acceptance, and outcome-measurement levels

| Alternative | Requirements fit | Search and accessibility | Convention alignment | Delivery risk | Decision |
|---|---|---|---|---|---|
| A. Shared data, server HTML, scoped JavaScript | High | High | High | Moderate and bounded | Select |
| B. Client-first JSON application | Partial | Low without duplicative mitigation | Low | High | Reject |
| C. Activate and enrich detail pages | Conflicts with BR-003 as the target state | Mixed | Partial | High migration and maintenance cost | Reject as primary architecture |

## End-to-End Implementation Alternatives

### Alternative A: Shared versioned data with progressive enhancement

#### Principles, architecture, and flow

This approach treats normalized, versioned artifacts as the shared contract, Hugo as the
authoritative renderer, and page-scoped JavaScript as an optional interaction layer.

1. Bender-owned generators normalize repository, ranking, freshness, provenance, and
   summary fields into explicit schema versions with deterministic ordering.
2. Hugo consumes the same normalized source to emit meaningful homepage modules,
   repository listings, data tables, embed alternatives, yearly metadata, and cost
   provenance in HTML.
3. Amy-owned JavaScript loads only on selected interactive surfaces. It enhances the
   existing HTML with repository search, filters, sorting, reset, stable URL state,
   chart exploration, and hover, focus, and touch disclosures.
4. Enhancement failures leave the server result usable. Empty, malformed, unavailable,
   and incompatible payloads produce explicit status text without removing the baseline.
5. Zapp-owned canonical, sitemap, internal-link, and redirect rules operate on the same
   URL inventory. Fry-owned tests compare artifact identities, emitted URLs, HTML
   fallbacks, enhanced states, and production observations.

The repository already supports this direction. The generated repository artifact holds
266 records (`data/derived/observatory/repositories.json:1-89172`), current ranking pages
have a crawlable table and provenance (`layouts/data/single.html:13-59`), and the Star
Velocity Explorer provides a nearby deterministic JSON and client-state pattern
(`scripts/export_trend_explorer_data.py:1-220`,
`assets/js/star-velocity-explorer.js:1-260`, and
`tests/test_trend_explorer_tool.py:12-109`). Hugo can emit HTML and JSON and consume
structured data from a shared source ([Hugo output formats](https://gohugo.io/configuration/output-formats/),
[Hugo data sources](https://gohugo.io/content-management/data-sources/)).

#### Advantages

* Preserves the current useful HTML baseline while adding the requested interaction
* Prevents independent HTML and JSON content paths from drifting
* Makes repository, data, embed, freshness, and provenance contracts testable before browser execution
* Keeps essential links and summaries available to users and crawlers when JavaScript is delayed, blocked, malformed, or disabled
* Limits bundle and interaction cost because scripts are loaded by page type rather than converting the publication into one application
* Supports staged vertical slices and URL migration without coupling every page to one client release
* Reuses existing generator, Hugo, test, accessibility, performance, and visual-review conventions

#### Ideal use

This is ideal for Claracle because its primary product is a statically generated
publication with data-rich views, not a session-oriented application. It works best for
the homepage hierarchy, consolidated repository explorer, selected ranking pages,
embeds, yearly article metadata, and cost dashboard where readable content precedes
interaction.

#### Limitations

* The team must define schema compatibility, HTML-versus-client responsibility, and URL-state behavior explicitly
* Large complete listings may need server pagination, bounded initial subsets, or carefully measured client rendering
* Interactive controls require custom focus, status, touch, and error handling even when the underlying HTML is sound
* Shared normalization does not settle product choices such as the homepage job, repository fields, first data slice, chart form, editorial voice, or freshness threshold
* Hugo aliases are not sufficient server redirects by themselves; deployment configuration remains necessary

#### Project-convention alignment

Alignment is strong. `layouts/index.html:1-111` already renders a useful homepage;
`layouts/data/single.html:13-59` renders the complete ranking and provenance;
`scripts/generate_data_pages.py:85-260` already normalizes observations and writes
deterministic page data; and `docs/design/visual-verification.md:122-180` supplies
existing overflow, target-size, Lighthouse, and CLS gates. Repository policy also
requires generated outputs to change with their owning metadata and checksums, which a
single normalized contract supports.

The approach follows Google guidance that static or server rendering gives crawlers
immediate HTML and that essential content and metadata should not depend on JavaScript
([JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)).
It also follows web.dev guidance to prefer static or server rendering where practical
and limit client JavaScript ([Rendering on the web](https://web.dev/articles/rendering-on-the-web)).

#### Implementation surfaces

* Design and shell: `hugo.toml:1-106`, `layouts/index.html:1-111`,
  `assets/css/extended/squadscope.css:1-1117`, and
  `docs/design/visual-verification.md:1-190`
* Repository contract and lifecycle: `config/observatory.toml:1-13`,
  `scripts/observatory_repos.py:209-226`, `scripts/observatory_repos.py:537-666`,
  `scripts/observatory_repos.py:736-864`, and
  `scripts/observatory_repos.py:1061-1180`
* Repository source and migration inventory: `content/repo/_index.md`, the 266 bundles
  under `content/repo/`, and `data/derived/observatory/repositories.json:1-89172`
* Data generation and baseline: `scripts/generate_data_pages.py:18-260`,
  `layouts/data/single.html:13-59`, and
  `layouts/partials/visuals/observatory-chart.html:14-56`
* Scoped interaction pattern: `scripts/export_trend_explorer_data.py:1-220`,
  `assets/js/star-velocity-explorer.js:1-260`, and
  `tests/test_trend_explorer_tool.py:12-109`
* Yearly article pipeline: `scripts/month_synthesis.py:117-121`,
  `scripts/month_synthesis.py:247-346`, and
  `scripts/generate_yearly_narrative.py:561-889`
* Cost projection: `scripts/track_token_usage.py:14-16`,
  `scripts/track_token_usage.py:167-217`, `data/metrics/token-usage.jsonl:1-6`,
  `data/metrics/cost-summary.json:1-9`, and
  `layouts/partials/cost-dashboard.html:1-18`
* Cross-cutting gates: `tests/test_pipeline.py:580-694`,
  `.github/workflows/security-scanning.yml:1-100`, and
  `.github/workflows/checkov.yml:1-86`

#### Validation

* Validate schemas, unique identities, deterministic regeneration, freshness, and compatibility policy
* Assert that JavaScript-disabled HTML exposes useful content, direct links, count, period, provenance, and downloads
* Test valid, empty, malformed, unavailable, and future-version JSON plus reset and stable-state behavior
* Verify semantic tables, chart alternatives, redundant non-color encoding, keyboard operation, visible focus, accessible names and states, touch disclosure, and 24 by 24 CSS pixel targets or an approved spacing exception
* Run `ruff check .`, `ruff format --check .`, focused and full `pytest`, `hugo --minify`, rendered-link checks, the visual matrix, axe, Lighthouse, and required security scans
* Preserve the current good field targets at the 75th percentile: LCP no more than 2.5 seconds, INP no more than 200 milliseconds, and CLS no more than 0.1, measured separately for mobile and desktop ([Web Vitals](https://web.dev/articles/vitals))
* Complete manual keyboard, screen-reader, touch, zoom, reduced-motion, tooltip persistence, and focus-restoration review

#### Risks and evidence

The main risk is an apparent shared contract that still allows HTML and JavaScript to
interpret fields differently. Contract fixtures must therefore render both outputs and
compare identities, periods, summaries, links, and provenance. A second risk is loading
all 266 records or dense charts without a budget; bounded defaults and field measurement
are required.

The evidence favors this risk profile. Existing data pages already provide strong HTML
tables, while no repository-summary schema or no-JavaScript acceptance test exists. The
codebase research identifies the missing work as contracts and browser behavior rather
than a need to replace Hugo. Accessibility guidance also favors actual tables for chart
data and equivalent keyboard semantics ([WAI complex images guidance](https://www.w3.org/WAI/tutorials/images/complex/),
[WCAG 2.2 SC 2.1.1](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html), and
[WCAG 2.2 SC 4.1.2](https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html)).

### Alternative B: Client-first JSON application replacing rendered content

#### Principles, architecture, and flow

This approach turns the homepage, repository explorer, priority data pages, charts, and
possibly embeds into client-rendered views. Hugo emits an application shell and asset
references; the browser fetches JSON, constructs primary content and links, owns state
and routing, and presents loading or error states.

The architecture centralizes browser interaction but makes JavaScript execution the
precondition for the product's principal discovery experience. Server rendering,
pre-rendering, or a parallel static fallback would have to be added later to recover
the current search and no-JavaScript properties.

#### Advantages

* Gives the interaction layer one component and state model
* Supports rich cross-view filtering and client navigation when most sessions remain inside the explorer
* Can simplify highly dynamic updates after the initial payload loads
* May be appropriate if Claracle changes into a continuously updated authenticated application

#### Ideal use

This is ideal for a product whose primary value requires long-lived client state,
high-frequency API updates, authenticated workflows, or application-like navigation.
The authoritative research provides no evidence that Claracle currently has those
requirements.

#### Limitations

* Replaces already useful homepage and ranking HTML with loading, failure, and hydration states
* Makes essential content and links dependent on successful script and payload execution
* Requires duplicate SSR or pre-render infrastructure to recover crawlability, social metadata, and no-JavaScript utility
* Increases bundle, interaction, accessibility, caching, version-skew, and observability scope
* Couples editorial pages, repository migration, embeds, and data tools to one client release model
* Does not solve upstream yearly truncation, cost-source divergence, URL disposition, or design approval

#### Project-convention alignment

Alignment is weak. Claracle's current boundary is a Hugo publication with deterministic
checked-in artifacts and selective client behavior. `layouts/index.html:12-111` and
`layouts/data/single.html:13-59` already provide meaningful HTML. Replacing them discards
a proven baseline and conflicts with the delivery research's requirement to keep
decision, data, server-rendered experience, client enhancement, QA, and outcome evidence
as separate story boundaries.

Google documents that JavaScript rendering can be delayed or fail, while static and
server rendering provide immediate HTML ([JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)).
web.dev also notes the interaction and main-thread costs of client rendering
([Rendering on the web](https://web.dev/articles/rendering-on-the-web)).

#### Implementation surfaces

* Replace primary output in `layouts/index.html:1-111` and
  `layouts/data/single.html:13-59` with client bootstraps
* Introduce an application entry point, component and state system, route handling,
  payload-version negotiation, loading and error boundaries, and build integration under `assets/js/`
* Rework `layouts/partials/visuals/observatory-chart.html:14-56` and embed output around client rendering
* Add server or pre-render infrastructure for titles, descriptions, canonicals,
  Article JSON-LD, social metadata, crawlable links, and no-JavaScript alternatives
* Expand browser, bundle, hydration, caching, deployment, and runtime telemetry gates beyond
  `tests/test_trend_explorer_tool.py:12-109` and `docs/qa-gates.md:14-45`

#### Validation

Validation would require all Alternative A contract and accessibility checks plus
application-shell loading, hydration, route, cache invalidation, offline or unavailable
payload, script failure, client exception, bundle, long-task, memory, and crawler-rendering
tests. It would also require proof that the generated or pre-rendered HTML contains
equivalent content before browser execution.

#### Risks and evidence

The dominant risks are regressions in crawlable content, accessibility, first render,
interaction latency, and failure isolation. The client would also become responsible for
Article metadata and other visible-content parity requirements
([Article structured data](https://developers.google.com/search/docs/appearance/structured-data/article),
[Structured-data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)).

No authoritative input identifies an application-only workflow that offsets those
costs. The external research instead says the current server tables are a stronger
baseline than a client-only chart or grid. Alternative B is therefore rejected for this
BRD. Scoped tools may still use richer client components when they retain an equivalent
server result.

### Alternative C: Activate repository detail pages and enrich them

#### Principles, architecture, and flow

This approach activates CR-05, continues generating one page per repository, and
improves those pages with richer history, summaries, charts, related repositories,
provenance, and GitHub actions. The `/repo/` section remains an index into 266 detail
records, and each record becomes an independently maintained search destination.

#### Advantages

* Preserves stable repository-specific URLs and can protect value where a page has useful content, links, or search demand
* Provides generous space for history, provenance, related records, and a canonical repository narrative
* Reuses existing lifecycle generation and seven aliases
* Can work well for a small, curated set of genuinely differentiated repository profiles

#### Ideal use

This is ideal when repository-specific pages have distinct search intent, sufficient
unique content, stable update economics, and demonstrated inbound or query value. The
live samples are not uniformly empty, so selected high-value pages may qualify after a
URL inventory.

#### Limitations

* Directly conflicts with BR-003's target to stop emitting the low-information detail corpus
* Activating CR-05 before consolidation creates avoidable indexing, redirect, QA, and content-maintenance churn
* Requires 266 page-level completeness and freshness decisions rather than one explorer contract
* Risks thin or repetitive content, inconsistent histories, stale summaries, and a larger sitemap without proven discovery value
* Does not provide one coherent cross-repository search, filter, sort, and comparison experience by itself
* Enrichment does not solve the homepage, data-page, yearly, embed, cost, or design requirements

#### Project-convention alignment

Alignment is partial. The generator and content corpus already exist:
`config/observatory.toml:1-13` keeps activation disabled;
`scripts/observatory_repos.py:537-864` builds histories and metadata; and
`scripts/observatory_repos.py:1061-1180` writes outputs and enforces rollout state.
However, delivery research establishes that CR-05 and BR-003 are mutually exclusive
target states. The current inventory is 266 detail records, 267 source pages including
the index, and 274 rendered URLs including seven aliases, so activation is not a small
toggle.

#### Implementation surfaces

* Activate and revise `config/observatory.toml:1-13`
* Extend `scripts/observatory_repos.py:537-864` and
  `scripts/observatory_repos.py:1061-1180`
* Maintain 266 bundles under `content/repo/`, the section index, seven alias
  dispositions, and `data/derived/observatory/repositories.json:1-89172`
* Add page-level unique summaries, canonical metadata, freshness, structured data,
  related links, and accessibility behavior
* Extend `tests/test_pipeline.py:580-694` with completeness, duplicate-content,
  internal-link, sitemap, and page-inventory checks

#### Validation

Validation must prove useful unique content, accurate freshness and provenance, direct
GitHub links, complete keyboard and assistive-technology behavior, one canonical per
page, sitemap accuracy, no unexplained record-to-page differences, and acceptable build,
Pagefind, Lighthouse, and crawl budgets across the entire corpus. GSC page and query
performance plus inbound-link evidence must justify retention.

#### Risks and evidence

The principal risk is investing in a target state the BRD explicitly replaces. A second
risk is treating all pages alike when sampled production pages vary in usefulness.
`docs/review/data-observatory-relaunch/owner-action-register.md:289-343` records sponsor
approval but disabled rollout, while the newer BR-003 direction requires consolidation.

Alternative C is rejected as the primary architecture. Its valid insight is retained
inside the recommended URL-level policy: a small number of proven, differentiated pages
may remain as canonical editorial profiles, but low-information pages must not be
activated or enriched indiscriminately.

## Repository URL Migration Alternatives

### Migration Alternative 1: Blanket redirect to the consolidated explorer

#### Principles, architecture, and flow

Remove all detail pages and send every legacy repository URL, including aliases, through
a direct 301 or 308 to `/repo/` or one generic explorer state.

#### Advantages and ideal use

This is operationally simple, preserves a response path for every legacy URL, and may be
appropriate only when every old page has one genuinely equivalent consolidated
destination that preserves repository-specific context.

#### Limitations and project alignment

Claracle cannot establish equivalence from page count. Sampled pages contain varying
amounts of history, velocity, topics, related repositories, direct links, and provenance.
A generic redirect can discard useful intent, and seven aliases need dispositions
separate from their canonical details. This conflicts with the project's evidence-first
rollout convention.

Google warns that redirecting many URLs to an irrelevant destination can be treated as
a soft 404 ([Redirects and Google Search](https://developers.google.com/search/docs/crawling-indexing/301-redirects)).
The approach is rejected unless a future inventory proves equivalent parameterized
destinations for every URL.

#### Implementation surfaces and validation

Surfaces include `content/repo/`, aliases generated by
`scripts/observatory_repos.py:736-864`, deployment redirect configuration, internal
links, canonical metadata, and the sitemap. Validation must crawl all 274 currently
renderable URL forms, assert one-hop redirects with no loops, verify the final 200
canonical, and compare pre/post GSC page and query data. The unresolved equivalence risk
remains unacceptable without the URL inventory.

### Migration Alternative 2: URL-level keep, merge, or retire

#### Principles, architecture, and flow

Inventory every emitted and externally observed repository URL, then assign one approved
disposition:

* Keep pages that retain differentiated content, demand, or inbound-link value; make them useful 200-status self-canonical destinations
* Merge pages only when a repository-specific explorer state or retained profile preserves the old page's useful context; use a direct server-side 301 or 308
* Retire pages with no equivalent through 404 or 410, remove their internal links and sitemap entries, and preserve the disposition record

The inventory records status, indexability, canonical, sitemap membership, useful
fields, GSC clicks and impressions, inbound links, alias relationships, final action,
destination, and approval.

#### Advantages and ideal use

This minimizes avoidable search harm, honors actual content value, supports selective
retained profiles, and lets the consolidated explorer replace only what it genuinely
supersedes. It is ideal for Claracle's mixed corpus and count discrepancy: 263 pages
reported live versus 266 generated records, 267 source pages, and 274 local rendered
URLs including aliases.

#### Limitations and project alignment

It requires analytics and backlink access, human review, deployment-layer redirect
support, and a maintained map. Those costs align with current sponsor-gated rollout,
deterministic inventory, and Zapp/URL review conventions. Hugo aliases emit client-side
meta refresh by default, so the deployment host must implement permanent server
redirects ([Hugo URL management](https://gohugo.io/content-management/urls/)).

#### Implementation surfaces and validation

Use `content/repo/`, `data/derived/observatory/repositories.json:1-89172`,
`scripts/observatory_repos.py:736-864`, the seven alias declarations, internal-link
generation, sitemap configuration, and deployment redirect rules. Validate complete
inventory reconciliation, direct one-hop redirects, expected final canonicals, no loops,
only canonical 200 URLs in the sitemap, accurate significant-change `lastmod`, no links
to retired URLs, deterministic regeneration, and rollback.

Google recommends direct permanent redirects to genuine replacements, consistent
canonical signals, updated internal links and sitemaps, and migration monitoring
([Canonical URL consolidation](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls),
[Site moves with URL changes](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes), and
[Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)).
Retain approved permanent redirects for at least one year and compare page-level and
query-level GSC evidence over 28-day and three-month windows
([Search Console Performance report](https://support.google.com/webmasters/answer/7576553)).

#### Risks and evidence

The major risk is incomplete external evidence leading to a wrong disposition. No URL
should leave the pending state until the crawl, GSC, and inbound-link inputs are present
or the sponsor explicitly accepts the uncertainty. This is the selected migration
approach because it contains that uncertainty rather than converting it into blanket
behavior.

### Migration Alternative 3: Delete without redirects

#### Principles, architecture, and flow

Remove all repository detail bundles, aliases, internal links, and sitemap entries, then
allow every former URL to return 404 or 410 without a replacement.

#### Advantages and ideal use

This is the cleanest implementation and truthfully signals that content with no
replacement is gone. It is appropriate at the individual retire disposition when a URL
has no useful content, demand, links, or equivalent destination.

#### Limitations and project alignment

As a blanket policy it discards any value held by richer sampled pages and aliases,
creates unnecessary broken external links, and ignores the sponsor-gated migration and
rollback conventions. It also prevents useful legacy URLs from landing in a
repository-specific explorer state.

#### Implementation surfaces and validation

Surfaces are deletion of `content/repo/` detail bundles, alias removal, sitemap and
internal-link cleanup, lifecycle-ledger updates, and deployed HTTP behavior. Validation
must assert 404 or 410, absence from sitemap and internal links, correct custom error
experience, and no accidental redirect or 200 soft-404 page.

Google explicitly permits 404 or 410 when content has no replacement
([Redirects and Google Search](https://developers.google.com/search/docs/crawling-indexing/301-redirects)).
The risk is over-applying a correct per-URL retirement mechanism. Blanket no-redirect
deletion is rejected; 404 or 410 remains part of selected Alternative 2.

## Release Sequencing Alternatives

### Sequencing Alternative 1: Close the old release before redesign

#### Principles, architecture, and flow

Finish CR-01 through CR-03 against one immutable current revision before approving the
new design. Capture live keyboard and screen-reader findings, add the missing interaction
states, reconcile the status record, obtain final visual acceptance, record sponsor GO
or NO-GO, and freeze the accepted release as the redesign baseline. Keep CR-04 and CR-06
in separate operational lanes; do not activate CR-05 because it conflicts with BR-003.

#### Advantages and ideal use

This gives the old release a clean historical disposition, proves current accessibility
and interaction behavior, and provides a formally accepted regression baseline. It is
ideal if the sponsor intends to operate the current experience for a meaningful period
or needs formal acceptance for contractual reasons.

#### Limitations and project alignment

The remaining work includes manual interaction captures and live assistive-technology
review for surfaces BR-001 and BR-003 may replace. Completing acceptance can delay the
new direction and spend reviewer effort on a short-lived state. It also cannot include
CR-05 activation coherently because `config/observatory.toml:1-13` remains disabled and
BR-003 requires the opposite final state.

#### Implementation surfaces and validation

Primary evidence surfaces are
`docs/review/data-observatory-relaunch/status-of-record.md:15-49`,
`docs/review/data-observatory-relaunch/status-of-record.md:85-135`,
`docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md:15-19`,
`docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md:60-147`,
and `docs/review/data-observatory-relaunch/owner-action-register.md:237-270`.
The gate requires dated named dispositions, retained manual evidence, corrected status,
and a sponsor decision against the tested revision.

#### Risks and evidence

The risk is schedule and evidence churn, not technical infeasibility. Delivery research
shows automated checks and Amy/Fry matrix acceptance exist, while retained interaction
captures and live AT review remain open. This sequencing is defensible but not selected
because the sponsor's stated BRD direction replaces the affected experience and CR-05
target.

### Sequencing Alternative 2: Explicit supersession before redesign

#### Principles, architecture, and flow

Record a dated sponsor NO-GO/supersession decision against an immutable relaunch
revision. State that the release was feature-complete but never received final
acceptance. Preserve current automated and visual evidence as a historical baseline,
carry unresolved accessibility and interaction findings into redesign entry criteria,
and replace CR-05 activation with BR-003 inventory and migration gates. Then amend the
BRD's owners, objective measures, open product decisions, and evidence classes before
implementation.

#### Advantages and ideal use

This resolves governance honestly, avoids polishing an experience that will be
replaced, prevents CR-05 from creating disposable search churn, and retains useful
baseline evidence. It is ideal when a newer approved product direction intentionally
supersedes an unaccepted release and no contractual rule requires retroactive GO.

#### Limitations and project alignment

Supersession is not permission to discard open findings. The redesign must still close
live keyboard, screen-reader, touch, reduced-motion, and interaction requirements on its
release candidate. The status record, design baseline, and migration decision must be
explicit enough that future readers cannot infer old-release acceptance.

This aligns with the delivery model's binary G0 alternative and evidence classification.
`docs/brds/claracle-post-relaunch-consolidation-brd.md:24-48` already combines a
feature-complete relaunch with the next experience phase;
`docs/brds/claracle-post-relaunch-consolidation-brd.md:73-102` mixes acceptance,
rollouts, cost work, and redesign without sequencing; and
`docs/brds/claracle-post-relaunch-consolidation-brd.md:113-149` leaves product decisions
and objective measures unresolved.

#### Implementation surfaces and validation

The policy changes governance records only during this phase: status-of-record,
owner-action register, BRD decision and ownership fields, the frozen visual evidence
reference, and CR-05 disposition. Validation is documentary but binary: one immutable
revision, one dated sponsor disposition, explicit non-acceptance wording, every open
finding carried into a named redesign gate, CR-05 marked superseded, and no rollout flag
changed.

CR-06 remains a prerequisite shared-contract experiment, and CR-04 remains independent.
The redesign starts only after the BRD has baseline, target, source, owner, window, and
dated dispositions for the homepage, repository fields and URL policy, data slice,
visualization questions, yearly editorial contract, and cost freshness policy.

#### Risks and evidence

The principal risk is using supersession as a shortcut around accessibility or review.
The mitigation is traceable carry-forward: every open old-release finding maps to the
new release's automated or named human gate. A second risk is ambiguity about historical
status, mitigated by explicit NO-GO/supersession rather than silence.

This is the selected sequencing policy. It satisfies the delivery research's requirement
that silence cannot count as acceptance and avoids activating the 266-page corpus only
to remove it in the next phase.

## Selected Approach

### Architecture decision

Proceed with Alternative A. Establish shared normalized and versioned repository, data,
and freshness contracts; render authoritative HTML through Hugo; add scoped enhancement
scripts to selected surfaces; and preserve complete semantics, provenance, links,
downloads, and useful fallback content without JavaScript.

Use these delivery slices:

1. Record explicit old-release supersession and amend the BRD's measures, owners,
   decisions, evidence classes, and CR-05 disposition.
2. Approve the BR-001 design brief, homepage hierarchy, repository schema and migration
   inventory, first data slice, visualization questions, yearly editorial contract, and
   cost source and freshness policy.
3. Deliver the responsive shell, navigation, server-rendered homepage, yearly article,
   and cost provenance before repository migration.
4. Generate the repository artifact and useful HTML summary, add scoped explorer
   interaction, and execute the approved keep, merge, or retire map. Do not activate CR-05.
5. Extend the same contract pattern to priority data pages, selected visualizations, and
   linked accessible embed summaries.
6. Release one tested revision, complete a seven-day smoke, then review GSC and product
   evidence at 28 days, three months, and six months.

### Migration decision

Use URL-level keep, merge, or retire dispositions. Do not use Hugo meta refresh as the
production migration mechanism. Use deployment-layer 301 or 308 redirects for genuine
replacements, direct them to the final canonical in one hop, retain them for at least one
year, and use 404 or 410 where no replacement exists.

### Sequencing decision

Use explicit supersession. The sponsor should record that the old revision did not reach
final acceptance, freeze its evidence as historical, and carry all unresolved interaction
and accessibility requirements into the redesigned release. This decision must precede
redesign implementation and must not change rollout flags.

### Rejected alternatives

* Reject a client-first replacement because it introduces crawlability, accessibility,
  performance, failure-state, and operational costs without an application-only requirement
* Reject broad activation and enrichment of repository details because it conflicts with
  BR-003, creates disposable migration work, and lacks per-URL value evidence
* Reject blanket redirects because generic destinations may be irrelevant soft 404s
* Reject blanket deletion without redirects because some sampled pages and aliases may
  have useful content, query intent, or links
* Reject mandatory old-release GO before redesign because it spends authority-bound review
  effort on a superseded target; choose a documented NO-GO/supersession instead

## Remaining Gaps

* Export GSC page and query data for all `/repo/` URLs and establish known inbound links
  before approving the migration map
* Run a deployed URL crawl covering HTTP status, redirect chains, response and HTML
  canonicals, indexability, sitemap membership, and the live 263-versus-source 266 discrepancy
* Obtain sponsor approval of the explicit supersession policy and immutable relaunch revision
* Approve the homepage audience, primary job, hierarchy, module selection, and freshness rules
* Approve repository fields, summary source, default sort, filter taxonomy, URL-state
  behavior, schema compatibility policy, and criteria for a retained profile
* Select the first BR-004 pages, state each chart's analytical question, compare at least
  two representations, and approve the comprehension threshold and participants
* Approve the BR-007 summary source, maximum displayed length, touch pattern, and destination
* Approve yearly article length, voice, cadence, claim standard, and named editor
* Confirm the authoritative cost ledger, retry and inclusion policy, pricing basis,
  accountable owner, freshness threshold, and exception handling
* Execute and retain JavaScript-disabled, keyboard, screen-reader, touch, zoom,
  reduced-motion, narrow-embed, malformed-data, and production field-performance evidence

## Evidence and External References

### Local evidence

* Homepage and section architecture: `hugo.toml:1-106`, `layouts/index.html:1-111`,
  and `layouts/data/single.html:1-69`
* Repository generation and counts: `config/observatory.toml:1-13`,
  `scripts/observatory_repos.py:209-226`, `scripts/observatory_repos.py:537-666`,
  `scripts/observatory_repos.py:736-864`, `scripts/observatory_repos.py:1061-1180`,
  and `data/derived/observatory/repositories.json:1-89172`
* Existing progressive-enhancement pattern: `scripts/export_trend_explorer_data.py:1-220`,
  `assets/js/star-velocity-explorer.js:1-260`, and
  `tests/test_trend_explorer_tool.py:12-109`
* Data and visualization baseline: `scripts/generate_data_pages.py:18-260`,
  `layouts/data/single.html:13-59`, and
  `layouts/partials/visuals/observatory-chart.html:14-56`
* Delivery and acceptance state:
  `docs/review/data-observatory-relaunch/status-of-record.md:15-49`,
  `docs/review/data-observatory-relaunch/status-of-record.md:85-135`,
  `docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md:15-19`,
  `docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md:60-147`,
  and `docs/review/data-observatory-relaunch/owner-action-register.md:237-343`
* Search and outcome baseline: `docs/growth/ga4-gsc-baseline-2026-07-29.md:17-23`,
  `docs/growth/ga4-gsc-baseline-2026-07-29.md:73-86`, and
  `docs/brds/claracle-data-observatory-relaunch-brd.md:88-101`
* Existing quality gates: `docs/review/data-observatory-relaunch/timing-analysis.md:114-174`,
  `docs/qa-gates.md:14-45`, `docs/design/visual-verification.md:107-180`,
  `tests/test_pipeline.py:580-694`, `.github/workflows/security-scanning.yml:1-100`,
  and `.github/workflows/checkov.yml:1-86`
* Yearly and cost root causes: `scripts/month_synthesis.py:117-121`,
  `scripts/month_synthesis.py:247-346`,
  `scripts/generate_yearly_narrative.py:561-889`,
  `content/yearly/2026.md:12-15`, `scripts/track_token_usage.py:14-16`,
  `scripts/track_token_usage.py:167-217`, `data/metrics/token-usage.jsonl:1-6`,
  `data/metrics/cost-summary.json:1-10`, and
  `layouts/partials/cost-dashboard.html:1-18`
* Ownership: `.squad/team.md:5-24`, `.squad/routing.md:5-24`, and
  `docs/data-observatory-runbook.md:28-45`

### External references

* [Redirects and Google Search](https://developers.google.com/search/docs/crawling-indexing/301-redirects)
* [Canonical URL consolidation](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
* [Site moves with URL changes](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes)
* [Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
* [JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
* [Article structured data](https://developers.google.com/search/docs/appearance/structured-data/article)
* [Structured-data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)
* [Search Console Performance report](https://support.google.com/webmasters/answer/7576553)
* [Rendering on the web](https://web.dev/articles/rendering-on-the-web)
* [Web Vitals](https://web.dev/articles/vitals)
* [Interaction to Next Paint](https://web.dev/articles/inp)
* [Largest Contentful Paint](https://web.dev/articles/lcp)
* [WCAG 2.2 SC 1.1.1](https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html)
* [WCAG 2.2 SC 1.3.1](https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html)
* [WCAG 2.2 SC 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)
* [WCAG 2.2 SC 1.4.13](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html)
* [WCAG 2.2 SC 2.1.1](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html)
* [WCAG 2.2 SC 2.4.7](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html)
* [WCAG 2.2 SC 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
* [WCAG 2.2 SC 4.1.2](https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html)
* [WAI complex images guidance](https://www.w3.org/WAI/tutorials/images/complex/)
* [Hugo data sources](https://gohugo.io/content-management/data-sources/)
* [Hugo output formats](https://gohugo.io/configuration/output-formats/)
* [Hugo URL management](https://gohugo.io/content-management/urls/)
* [Hugo sitemap configuration](https://gohugo.io/configuration/sitemap/)