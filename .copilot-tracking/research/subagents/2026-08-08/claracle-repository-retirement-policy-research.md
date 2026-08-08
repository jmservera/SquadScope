---
title: Claracle Repository Retirement Policy Research
description: Assessment of the proposed BR-003 direct-404 retirement policy for repository detail URLs
ms.date: 2026-08-08
ms.topic: concept
---

## Research Scope

Assess the proposed V1 policy change for BR-003 against the approved business
baseline, status record, repository inventory, GSC evidence, deployed URL behavior,
and authoritative Google Search guidance.

## Status

Complete. Research only was performed. No approved policy, source content, generated
content, configuration, workflow, or hosting resource was changed.

## Questions

* Is direct HTTP 404 technically and SEO appropriate when a URL is not indexed,
  has no impressions or clicks, has no inbound links, and has no meaningful replacement?
* Is HTTP 410 required, or is HTTP 404 sufficient?
* What URL-level evidence is required before bulk retirement?
* Should permanent redirects remain conditional for exceptional URLs with external
  value or a genuine equivalent?
* What exact BRD amendments are required for BR-003, approved decisions,
  constraints, risk mitigation, and impacted acceptance criteria?
* Is the proposed V1 policy change material and subject to sponsor reapproval?
* How does the policy change affect the selected hosting recommendation and
  implementation gates?

## Evidence Register

### Controlled local evidence

* The approved business baseline is BRD-CLARACLE-003 version 1.0. It requires a
  keep, merge, or retire disposition for every URL, one-hop hosting-layer 301/308
  redirects for genuine replacements, and 404/410 for URLs without equivalents.
  It also defines material policy and acceptance-criteria changes as requiring
  sponsor reapproval and a new version.
  Source: `docs/brds/claracle-post-relaunch-consolidation-brd.md:20-30`,
  `docs/brds/claracle-post-relaunch-consolidation-brd.md:117-165`, and
  `docs/brds/claracle-post-relaunch-consolidation-brd.md:197-212`.
* The accepted inventory contains 266 repository detail records, 267 repository
  source pages, 274 local rendered `/repo/` URLs, and seven aliases. The 274 URLs
  are 267 canonical source pages plus seven alias outputs. A local build cannot
  establish external link value.
  Source: `.copilot-tracking/research/subagents/2026-08-08/claracle-codebase-surfaces-research.md:120-163`.
* Repository-page generation remains disabled. Its lifecycle configuration says
  that absence from a weekly crawl is not deletion evidence.
  Source: `config/observatory.toml:1-12`.
* Seven source bundles contain aliases. For example,
  `content/repo/affaan-m-ecc/index.md:275-284` maps the former
  `/repo/affaan-m-everything-claude-code/` path to the current detail page.
  Alias URLs therefore need independent dispositions rather than inheriting a
  blanket corpus decision.
* Normal pages emit self-referential canonicals from `.Permalink`.
  Source: `layouts/partials/seo.html:110-119`.
* Hugo aliases are HTTP 200 documents with `noindex`, a canonical target, and a
  zero-second meta refresh. They are not origin-level 301/308 responses.
  Source: `layouts/alias.html:10-32`.
* Claracle currently builds with Hugo and deploys through GitHub Actions to
  GitHub Pages. GitHub Pages serves a true HTTP 404 for missing paths, but the
  Hugo artifact cannot configure per-path hosting-layer redirects.
  Source: `architecture.md:3-14`, `architecture.md:39-41`, and
  `.copilot-tracking/research/subagents/2026-08-08/claracle-redirect-boundary-alternatives-research.md:64-113`.
* The checked-in GA4/GSC baseline is aggregate, not URL-level. It reports 149
  impressions, zero clicks, 294 indexed pages, and 1,190 not-indexed pages for
  the site. Raw exports are retained outside the repository. These totals cannot
  establish that each repository URL was never indexed, never earned an
  impression, or has no links.
  Source: `docs/growth/ga4-gsc-baseline-2026-07-29.md:15-26` and
  `docs/growth/ga4-gsc-baseline-2026-07-29.md:70-110`.
* The relaunch status is NO-GO / SUPERSEDED. Repository-page activation was
  cancelled, the generation flag remains disabled, and retained lifecycle,
  identity, alias, and rollback evidence is migration input.
  Source: `docs/review/data-observatory-relaunch/status-of-record.md:27-39`,
  `docs/review/data-observatory-relaunch/status-of-record.md:85-100`, and
  `docs/review/data-observatory-relaunch/status-of-record.md:175-184`.

### Authoritative external evidence

* Google says a permanent server-side redirect is appropriate when a page moves,
  while a `404` or `410` response is appropriate when content is removed and has
  no replacement. Redirecting many old URLs to an irrelevant destination can be
  treated as a soft 404.
  Sources: [Redirects and Google Search](https://developers.google.com/search/docs/crawling-indexing/301-redirects)
  and [HTTP status codes and network errors](https://developers.google.com/search/docs/crawling-indexing/http-network-errors).
* Google removes URLs returning `4xx` responses from its index over time and does
  not use their content. Google treats all `4xx` codes except `429` the same for
  indexing purposes. This makes `404` sufficient for search retirement; `410` is
  not an SEO requirement.
  Source: [HTTP status codes and network errors](https://developers.google.com/search/docs/crawling-indexing/http-network-errors).
* RFC 9110 defines `404` as no current representation without asserting whether
  that state is temporary or permanent. It prefers `410` when permanence is
  known, but explicitly says it is unnecessary to mark all permanently
  unavailable resources as gone. Both responses are heuristically cacheable.
  Source: [RFC 9110 sections 15.5.5 and 15.5.11](https://www.rfc-editor.org/rfc/rfc9110.html#status.404).
* The Search Console URL Inspection API returns the indexed status available in
  Google's index for a supplied URL. The quota is 2,000 inspection requests per
  site per day, so the complete 274-URL inventory fits within one daily quota.
  It reports current index state, not proof that a URL was never indexed.
  Sources: [URL Inspection API](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect)
  and [Search Console API usage limits](https://developers.google.com/webmaster-tools/limits).
* The Search Analytics API supports page dimensions and page filters for clicks
  and impressions. It returns top rows rather than guaranteeing every row, so a
  zero result is evidence from that query and date window, not proof of
  historical nonexistence.
  Source: [Search Analytics query](https://developers.google.com/webmaster-tools/v1/searchanalytics/query).
* Search Console's Links report is sampled. Its absence of a URL or link is not
  proof that no external link exists.
  Source: [Links report](https://support.google.com/webmasters/answer/9049606).
* A sitemap communicates preferred canonical URLs but does not guarantee
  indexing. Removing a URL from a sitemap is required cleanup, not evidence that
  the URL was never indexed.
  Source: [Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap).

## Findings

### Decision

Adopt the proposed V1 policy change with an evidence qualification. Direct HTTP
404 retirement is appropriate for a repository URL when the approved URL record
shows no observed search or link value in the named evidence sources, no
meaningful unique content, and no genuine replacement. Do not state that a URL
was "never indexed" or "has no inbound links" unless a source with that scope
actually proves the claim. The available sources do not.

The policy must remain per URL. It does not justify blanket deletion of the
repository corpus, blanket redirects to `/repo/`, or treating the seven aliases
as duplicates of their current canonical dispositions without review.

### Determinations

1. Direct HTTP 404 is technically and SEO appropriate for a no-equivalent URL
   after the evidence gate below passes. GitHub Pages already supplies a real
   404 response for a removed path. The custom 404 representation may help a
   person recover, but it must retain the 404 status and must not imitate a
   repository replacement page.
2. HTTP 410 is optional, not required. It communicates stronger permanent intent
   at the HTTP layer, but Google treats the relevant 4xx responses the same for
   indexing. Adding a Worker or Function solely to emit 410 would create hosting
   complexity without a demonstrated V1 outcome benefit.
3. The checked-in aggregate baseline is insufficient for bulk retirement. It
   cannot be used to infer URL-level index, performance, or link state for all
   repository URLs.
4. Permanent redirects remain mandatory when an approved destination is a
   genuine equivalent and the old URL has migration value. A filtered explorer
   state qualifies only if it preserves the old URL's repository-specific intent
   in useful rendered or progressively enhanced content. The generic explorer,
   homepage, a GitHub repository URL, or a topic page is not automatically an
   equivalent.
5. A known inbound link or search signal does not create an equivalent where
   none exists. When value exists but no equivalent exists, Leela and URL must
   choose between retaining a differentiated profile and intentional 404
   retirement, document the expected loss, and obtain sponsor disposition for a
   release-blocking SEO exception when applicable. An irrelevant redirect is not
   the fallback.
6. The change is material. It changes approved product policy, the practical
   redirect requirement, acceptance evidence, risk mitigation, and potentially
   the production hosting prerequisite. Section 10 requires sponsor reapproval
   and a new controlled BRD version before implementation.
7. The selected Cloudflare Pages recommendation becomes conditional rather than
   an unconditional prerequisite. If the approved final map contains any 301/308
   rows, Cloudflare Pages remains the preferred host because it deploys generated
   redirect rules and site bytes as one versioned artifact. If every removed URL
   is independently approved for 404 and no permanent redirects remain, GitHub
   Pages can satisfy the retirement status requirement and a hosting migration is
   not justified by BR-003 alone.

### Minimum URL-level evidence gate

Create one immutable migration record for each of the 274 inventoried local URLs
and any additional production-only URL discovered during reconciliation. A URL
may receive direct-404 approval only when the record contains all of the
following evidence:

* Normalized source URL, URL class (canonical, alias, or production-only), source
  identity, current production status, canonical target, sitemap membership, and
  internal-link count
* Current URL Inspection result and inspection timestamp
* Exact-page Search Analytics results for the maximum available period relevant
  to the URL, including the queried date range, clicks, and impressions
* Search Console Links report export date and whether the sampled report contains
  the URL, supplemented by available first-party referral or request evidence;
  the conclusion must say "no observed inbound link in named sources," not "no
  inbound links"
* Review of differentiated repository-specific content and a recorded
  equivalence decision for every proposed destination
* Explicit keep, merge, redirect, or retire disposition, destination when
  applicable, evidence-source identifiers, reviewer, approval date, and rationale
* Separate rows for aliases and canonical URLs, with no inherited decision unless
  the evidence and rationale are recorded for both

If URL Inspection or exact-page performance evidence is unavailable, stale, or
ambiguous, the URL does not pass the low-evidence bulk-404 path. Hold it for
manual disposition. Do not convert missing evidence into a zero.

### Release and monitoring gates

Before release:

* Reconcile source, clean-build, production, sitemap, canonical, alias, and
  internal-link inventories to one approved URL map
* Assert one-hop 301/308 plus the exact `Location` target for every redirect row
* Assert true 404, no redirect, no sitemap entry, and no internal link for every
  retire row
* Verify retained pages and the consolidated summary emit the intended canonical
  URLs and useful server-rendered content
* Verify the 404 page retains HTTP 404 and offers non-deceptive recovery links
* Deploy site and redirect rules atomically when redirects exist, then probe all
  changed URLs before promoting the release
* Retain the prior artifact, URL map, DNS or host configuration, and a tested
  rollback path

After release, compare the approved map with GSC at 28 days and three months.
Track unexpected indexed 404s, soft 404s, redirect errors, canonical divergence,
clicks, impressions, and referral failures. A discovered valuable URL triggers a
new reviewed disposition; it does not silently receive a generic redirect.

## Recommended Amendment

Issue BRD-CLARACLE-003 version 1.1 only after sponsor approval. Preserve all
unaffected version 1.0 text. Apply the following controlled amendments.

### Change history entry

> | 1.1 | 2026-08-08 | jmservera, SquadScope Squad | Permitted evidence-gated
> direct HTTP 404 retirement for repository URLs with no observed search or link
> value, no differentiated content, and no genuine equivalent; retained
> conditional one-hop redirects for genuine replacements; made redirect-capable
> hosting conditional on the approved URL map |

### Replace BR-003 acceptance criteria

> Every inventoried canonical, alias, and production-only URL receives an
> approved keep, merge, redirect, or retire disposition before removal. Retain an
> individual profile only when it has differentiated content plus demonstrated
> GSC demand or a known inbound link. Use a one-hop hosting-layer 301/308 only
> when the approved destination preserves the old URL's repository-specific
> intent. A URL may retire directly with HTTP 404 when URL Inspection, exact-page
> Search Analytics for the recorded window, sampled Search Console link evidence,
> available first-party referral evidence, internal-link and sitemap inventory,
> content review, and destination-equivalence review show no observed value and
> no genuine replacement. Evidence absence is recorded as "not observed in named
> sources," never as an absolute historical claim. HTTP 410 is optional and is
> not a V1 requirement. The production build emits no low-information details;
> the explorer works with keyboard and assistive technology, provides useful
> non-JavaScript output, handles empty and error states, and validates its
> documented schema and freshness metadata.

### Add to Section 7.3 constraints and dependencies

> Repository retirement evidence is URL-level. Aggregate GA4/GSC totals, sitemap
> membership, local-build absence, and sampled link-report absence cannot alone
> prove that a URL was never indexed or has no inbound links. Missing or ambiguous
> evidence blocks the evidence-gated direct-404 path and requires manual
> disposition.
>
> Redirect-capable hosting is required only when the approved final URL map
> contains a genuine-equivalent redirect. The selected host must deploy site
> content and generated redirect rules atomically. When the approved map contains
> no redirect rows, a host that returns true HTTP 404 for absent paths satisfies
> the BR-003 retirement-status requirement.

### Replace the repository migration decision in Section 7.4

> The repository explorer uses topic, language, status, and period filters;
> recent momentum as its default sort; URL-persisted state; sanitized
> generated-context summaries; direct GitHub links; and URL-level keep, merge,
> redirect, or retire migration. Direct 404 retirement is permitted only through
> the approved evidence gate. Permanent redirects remain conditional and require
> a genuine equivalent. Blanket explorer redirects, Hugo meta refresh as the
> production redirect mechanism, and absolute "never indexed" or "no inbound
> links" claims from incomplete sources are prohibited.

### Replace the repository-consolidation risk mitigation in Section 8

> Reconcile every canonical, alias, and production-only URL; retain the named
> URL Inspection, Search Analytics, sampled link, first-party referral,
> internal-link, sitemap, content, and equivalence evidence; require approved
> dispositions; generate one-hop hosting redirects only for genuine equivalents;
> verify true 404 for direct retirements; validate canonicals, internal links,
> sitemap, custom 404 behavior, atomic deployment, and rollback; review GSC at 28
> days and three months. Missing evidence, an irrelevant redirect, a soft 404,
> redirect failure, or an unapproved URL disposition is release-blocking.

### Amend OBJ-03's approved target

> Zero low-information detail pages emitted and 100% of canonical, alias, and
> production-only URLs reconciled to approved evidence-backed keep, merge,
> redirect, or retire treatments before release; review migration at 28 days and
> three months.

### Governance disposition

The amendment changes approved product and operational policy, acceptance
criteria, release mitigation, and the condition that can force a hosting change.
It is material under Section 10. jmservera must approve version 1.1 before URL
disposition or implementation work relies on it. Leela and URL should approve the
URL evidence contract and hosting decision. Workflow, infrastructure, or hosting
changes still require URL pipeline review and Hermes security review under the
repository instructions.

## Remaining Questions

The research questions are answered. These delivery inputs remain unavailable
and must be resolved before implementation planning closes:

* Who will export or query URL Inspection, exact-page Search Analytics, and the
  Links report, and where will the sanitized immutable evidence be retained?
* What is the maximum relevant Search Analytics window for URLs with different
  first-publication dates?
* Does first-party hosting or CDN request/referrer history exist for Claracle, or
  must the link conclusion rely on GSC's sampled report plus known stakeholder
  links?
* Which, if any, old canonical or alias URL has a genuinely equivalent filtered
  explorer destination after the consolidated experience is designed?
* After the final map is approved, does at least one redirect row remain? That
  answer selects Cloudflare Pages or permits GitHub Pages to remain for BR-003.

<!-- End of research ledger. -->
