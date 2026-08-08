<!-- markdownlint-disable-file -->
# Task Research: Claracle Post-Relaunch Experience

Research the implementation implications of BRD-CLARACLE-003, resolve contradictions identified during review, and select a coherent implementation approach for Claracle's redesign, repository consolidation, interactive data pages, visualization changes, yearly editorial generation, embeds, navigation, and cost freshness.

## Task Implementation Requests

* Resolve the conflict between enabling generated repository pages and replacing them with a consolidated repository explorer.
* Determine how visual acceptance should work when a site-wide redesign supersedes the existing screenshot baseline.
* Identify measurable success criteria, accountable owners, evidence classifications, dependencies, and delivery boundaries for BR-001 through BR-009.
* Map the requirements to the owning Hugo templates, assets, content generators, data artifacts, tests, and workflows.
* Evaluate implementation alternatives and select one evidence-based delivery approach.

## Scope and Success Criteria

* Scope: BRD-CLARACLE-003 Sections 3 and 7, relevant local implementation surfaces, observed Claracle production behavior on 2026-08-08, and authoritative SEO, accessibility, performance, and Hugo guidance. Implementation is excluded.
* Assumptions: The sponsor's requirements are stakeholder input; claims about reader usefulness remain unvalidated until supported by analytics or usability evidence; Hugo remains the publishing platform; server-rendered content remains required.
* Success Criteria:
  * Every BRD review finding is resolved or converted into an explicit planning decision.
  * Each requirement is mapped to evidence, owner, implementation surfaces, dependencies, and binary acceptance measures.
  * Repository-page migration preserves valuable URLs while eliminating low-value generated output.
  * One coherent architecture and phased delivery approach is selected with rejected alternatives documented.

## Selected Approach

Use shared normalized and versioned data contracts, authoritative server-rendered Hugo HTML, and scoped progressive JavaScript enhancement. Generate both HTML and JSON from the same normalized source. Keep essential summaries, links, provenance, downloads, tables, metadata, and fallback behavior in HTML; use JavaScript only for search, filtering, sorting, chart exploration, shareable state, and accessible disclosures.

For repository migration, inventory every emitted and externally observed URL and assign one keep, merge, redirect, or retire disposition. Retire a URL directly with HTTP 404 when URL-level evidence finds no observed search or link value, no differentiated content, and no genuine replacement. Use a deployment-layer 301 or 308 only for an exceptional URL whose approved destination preserves repository-specific intent. HTTP 410 is optional and unnecessary for V1. This keeps GitHub Pages viable when the final map contains no redirect rows; redirect-capable hosting is conditional rather than a migration prerequisite.

For release sequencing, record a dated sponsor NO-GO/supersession decision against the immutable unaccepted relaunch revision. Preserve its 64-screen and 68-check evidence as historical baseline material, carry all open interaction and accessibility findings into the redesigned release, and supersede CR-05 with BR-003 migration gates. Do not claim that the previous release passed final acceptance.

## Outline

1. Evidence and current architecture
2. Requirement implementation map and root causes
3. Objective measures, evidence classes, and ownership
4. Architecture, migration, and release-sequencing alternatives
5. Selected phased delivery model
6. BRD amendments and planning handoff

## Potential Next Research

* Export URL Inspection, exact-page Search Analytics, sampled Links, and available first-party referral evidence for `/repo/`
  * Reasoning: Aggregate totals cannot establish URL-level eligibility for direct HTTP 404 retirement.
  * Reference: `.copilot-tracking/research/subagents/2026-08-08/claracle-repository-retirement-policy-research.md`
* Reconcile canonical, alias, production-only, sitemap, canonical, and internal-link inventories
  * Reasoning: The final approved map determines whether GitHub Pages can remain or a redirect-capable host is needed for exceptional genuine replacements.
  * Reference: BR-003 migration gate
* Prototype visualization alternatives with representative readers
  * Reasoning: The chart form must follow the analytical question and a comprehension comparison.
  * Reference: BR-005

## Research Executed

### File Analysis

* `layouts/index.html:1-100`
  * The homepage is useful server-rendered HTML but prioritizes the latest weekly report, six recent weeks, topics, and links. It lacks original monthly, yearly, repository, and data modules plus a cross-section freshness contract.
* `config/observatory.toml:1-13` and `scripts/observatory_repos.py:209-226,537-666,736-864,1061-1180`
  * Repository-detail generation is disabled but fully implemented. Enabling CR-05 would activate the corpus that BR-003 requires production to stop emitting.
* `content/repo/` and `data/derived/observatory/repositories.json:1-89172`
  * The authoritative local inventory is 266 detail records, 267 source pages including the section index, and 274 rendered URLs including seven aliases. The JSON artifact is a strong source but lacks a published versioned schema contract.
* `layouts/data/single.html:13-59` and `scripts/generate_data_pages.py:18-260`
  * Current data pages already provide crawlable tables, repository links, and provenance. Rankings are stored in front matter and an inline JSON subset, with no shared public schema, interactive controls, or state contract.
* `layouts/partials/visuals/observatory-chart.html:14-56`
  * All rankings use one maximum-scaled horizontal SVG bar chart. The accessible table is retained, but chart selection is not based on a recorded analytical question.
* `scripts/month_synthesis.py:117-121,247-346` and `scripts/generate_yearly_narrative.py:561-889`
  * Yearly truncation is cumulative: weekly evidence is clipped into monthly prose, monthly prose is clipped again, and the final yearly narrative is compressed to 500 words with ellipses. Raising only the final cap cannot fix upstream clipped fragments.
* `scripts/generate_data_pages.py:200-222`, `layouts/data/single.html:45-54`, and `layouts/partials/visuals/observatory-chart.html:18-49`
  * Embed data already includes URL and context, but SVG labels are plain text. BR-007 is primarily a rendering and equivalent-interaction gap.
* `hugo.toml:57-106`
  * Current navigation is Weekly, Topics, Monthly, Data, Tools, Yearly, Search, Methodology, About. BR-008 is a small configuration change with responsive and accessibility implications.
* `data/metrics/cost-summary.json:1-9`, `data/metrics/token-usage.jsonl:1-6`, `scripts/track_token_usage.py:14-16,167-217`, and `layouts/partials/cost-dashboard.html:1-18`
  * The About page reads a manually shaped summary ending at W21, while the active ledger reaches W23. No generator, provenance contract, retry policy, or stale-data gate joins the two paths.
* `docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md:15-19,58-76,91-147`
  * Automated visual coverage and named matrix review exist, but manual filter, expanded-detail, copy-action, focus, and live assistive-technology evidence remains open.
* `.github/workflows/build-cost-experiment.yml:75-100,135-149`
  * CR-06 is caused by experiment hydration replacing five main seed hubs with one stale publish subtree before timing. Production deploy hydration is separately guarded.

### Code Search Results

* Repository generation and rollout
  * `config/observatory.toml`, `scripts/observatory_repos.py`, `tests/test_pipeline.py:580-694`, and seven alias-bearing bundles under `content/repo/`
* Existing progressive-enhancement pattern
  * `scripts/export_trend_explorer_data.py:1-205`, `assets/js/star-velocity-explorer.js:1-207`, and `tests/test_trend_explorer_tool.py:12-109`
* Existing visual and performance gates
  * `docs/design/visual-verification.md:107-180`, `docs/qa-gates.md:14-45`, and `docs/review/data-observatory-relaunch/timing-analysis.md:114-174`
* Search baseline
  * `docs/growth/ga4-gsc-baseline-2026-07-29.md:73-86` records 51 sessions, 0 organic sessions, 149 impressions, 0 clicks, 294 indexed pages, and 17 impression-bearing queries.

### External Research

* Google Search Central: redirects, canonicals, and site moves
  * Use direct permanent redirects only for genuine replacements, avoid redirect chains and irrelevant blanket destinations, align canonical/internal-link/sitemap signals, and monitor migration. Retain permanent redirects for at least one year.
  * Sources: [Redirects and Google Search](https://developers.google.com/search/docs/crawling-indexing/301-redirects), [Canonical URL consolidation](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls), [Site moves](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes)
* Google and web.dev: rendering and performance
  * Essential content and metadata should be available before JavaScript. Good field targets at the 75th percentile are LCP no more than 2.5 seconds, INP no more than 200 milliseconds, and CLS no more than 0.1, measured separately on mobile and desktop.
  * Sources: [JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics), [Rendering on the web](https://web.dev/articles/rendering-on-the-web), [Web Vitals](https://web.dev/articles/vitals)
* W3C WAI: charts and tooltips
  * Data charts need equivalent text or tables, color cannot be the only encoding, controls require keyboard access and visible focus, and hover/focus content must be dismissible, hoverable, and persistent. Touch and assistive technology require equivalent access.
  * Sources: [Complex images](https://www.w3.org/WAI/tutorials/images/complex/), [WCAG 1.4.13](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html), [WCAG 2.1.1](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html), [WCAG 4.1.2](https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html)
* Google Article structured data
  * Visible article content, headline, author, dates, images, canonical metadata, and JSON-LD must agree. Schema validation does not establish editorial completeness or factual traceability.
  * Source: [Article structured data](https://developers.google.com/search/docs/appearance/structured-data/article)
* Hugo documentation
  * Hugo supports HTML and JSON output from common structured sources. Hugo aliases default to client-side meta refresh and are not equivalent to deployment-layer permanent redirects.
  * Sources: [Hugo output formats](https://gohugo.io/configuration/output-formats/), [Hugo data sources](https://gohugo.io/content-management/data-sources/), [Hugo URL management](https://gohugo.io/content-management/urls/)

### Project Conventions

* Standards referenced: `.github/copilot-instructions.md`, `AGENTS.md`, `.squad/team.md:5-24`, `.squad/routing.md:5-24`, repository Markdown and writing-style instructions, and `.github/skills/frontend-design/SKILL.md`
* Existing validation: Ruff, pytest, Hugo minification, Pagefind timing, visual matrix, axe, Lighthouse, Checkov, Zizmor, and named human acceptance where authority is required
* Research delegation: codebase, live-site, standards, delivery-quality, and alternatives investigation were performed by Researcher Subagent and consolidated here

## Key Discoveries

### Project Structure

* Hugo remains the correct publishing boundary. Existing pages already provide useful HTML and selective client behavior rather than an application shell.
* The Star Velocity Explorer is the nearest reusable interaction pattern, but BR-003 and BR-004 must improve its no-JavaScript fallback and establish shared schema/freshness contracts.
* Repository, data, yearly, cost, and navigation behavior each have distinct owning generators or templates. The BR rows are epics, not implementation-sized stories.

### Implementation Patterns

* Generate deterministic versioned artifacts with identity, reporting period, generation timestamp, provenance, and compatibility policy.
* Render authoritative HTML from the normalized source and layer page-scoped enhancement on top.
* Preserve useful server tables or lists as accessibility, crawlability, and failure-state baselines.
* Test valid, empty, malformed, unavailable, stale, and future-version payloads.
* Separate E0 product decisions, E1 observed baselines, E2 repository contracts, E3 named human acceptance, and E4 production outcomes. One class cannot substitute for another.

### Objective Measurement Contracts

| Objective | Baseline and source | Accountable owner | Recommended target and window |
|---|---|---|---|
| OBJ-01 | 64 screenshots and 68/68 visual-regression checks; one local analytics check failed, axe and Lighthouse evidence were unavailable, and manual interaction plus live AT work remain open. Source: `docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md:58-76,91-147` | Calculon | Approved design brief; zero unresolved severity-1/2 visual or accessibility defects; all applicable automated and named human gates pass before release, followed by a seven-day smoke |
| OBJ-02 | 0 organic sessions, 149 impressions, 0 clicks, 294 indexed pages, 17 impression-bearing queries. Source: `docs/growth/ga4-gsc-baseline-2026-07-29.md:73-86` | Leela | Retain inherited six-month targets of at least 250 organic sessions per 28-day month and 15 top-20 queries; capture release-day, 28-day, three-month, and six-month evidence |
| OBJ-03 | 266 detail records, 267 source pages, 274 rendered URLs, and a live count discrepancy of 263. Sources: `content/repo/`, `data/derived/observatory/repositories.json:1-89172`, and the 2026-08-08 live observation | Leela | Zero low-information detail pages emitted; 100% of canonical, alias, and production-only URLs receive approved evidence-backed treatment; validate before release, then review at 28 days and three months |
| OBJ-04 | Server-rendered rankings and bars; no comprehension baseline. Sources: `layouts/data/single.html:13-59` and `layouts/partials/visuals/observatory-chart.html:14-56` | Amy | Across all three ranking pages, the selected representation supports correct inference for at least four members of the approved internal five-person squad proxy; every page passes SSR, provenance, download, state, error, accessibility, and timing contracts before merge, followed by a seven-day production smoke |
| OBJ-05 | Static W19-W21 summary without provenance while the ledger reaches W23. Sources: `data/metrics/cost-summary.json:1-9` and `data/metrics/token-usage.jsonl:1-6` | Bender | Every public cost record includes source, period, generation time, pricing basis, and approved freshness; missing, malformed, unreconciled, or stale input fails closed on every owning run |

### Ownership and Delivery Prerequisites

| Requirement | Accountable owner | Remaining delivery prerequisite |
|---|---|---|
| BR-001 | Calculon | Produce the approved design brief, representative views, and named acceptance evidence |
| BR-002 | Leela | Implement the approved audience/job through hierarchy, module, freshness, ownership, and fallback contracts |
| BR-003 | Leela | Complete URL-level evidence and dispositions; approve V1.1 direct-404 policy; select redirect-capable hosting only if a redirect row remains |
| BR-004 | Amy | Define the shared envelope, typed page records, URL state, and interaction budgets for all three approved pages |
| BR-005 | Calculon | State each analytical question and execute the approved five-person, four-correct comparison |
| BR-006 | Farnsworth | Repair cumulative clipping and retain the approved editorial, claim, SEO, and safety evidence |
| BR-007 | Amy | Define exact sanitization and implement equivalent pointer, keyboard, touch, and accessibility-tree disclosure |
| BR-008 | Amy | Implement the approved order and validate responsive and assistive-technology behavior |
| BR-009 | Bender | Implement accepted-attempt reconciliation, deterministic projection, and the approved 30-day fail-closed gate |

### Complete Example Contract

```json
{
  "schemaVersion": "1.0",
  "generatedAt": "2026-08-08T00:00:00Z",
  "period": {"start": "2026-01-01", "end": "2026-08-08"},
  "freshness": {"latestObservation": "2026-08-08", "maximumAgeDays": 30},
  "compatibility": {"minimumReaderVersion": "1.0", "unknownFieldPolicy": "ignore"},
  "provenance": {"source": "data/derived/observatory/repositories.json"},
  "summarySource": "normalizedRepositoryContext",
  "records": [
    {
      "id": "owner-repository",
      "name": "owner/repository",
      "url": "https://github.com/owner/repository",
      "summary": "Bounded, sanitized repository context.",
      "language": "Python"
    }
  ]
}
```

V1 fixes repository behavior, source class, filters, sort, URL state, retention policy, and cost identity. Exact field types and compatibility mechanics are E2 architecture work. The required envelope is version, freshness, period, provenance, deterministic records, and an explicit compatibility policy.

## Technical Scenarios

### Architecture and Rendering

**Requirements:** BR-001, BR-002, BR-003, BR-004, BR-005, BR-007, and the server-rendering constraint.

**Preferred Approach:** Shared versioned data with server-rendered Hugo HTML and scoped progressive enhancement.

```text
normalized source
  -> deterministic versioned artifact
  -> Hugo HTML: summaries, tables, links, provenance, metadata
  -> scoped JavaScript: filters, sorting, charts, state, disclosures
  -> tests compare artifact, HTML, and enhanced identities
```

**Implementation Details:** Preserve current data tables, introduce common schema envelopes and status/error semantics, load scripts only on interactive page types, and establish bounded initial rendering for 266 repository records. Validate no-JavaScript output before adding client behavior.

#### Considered Alternatives

* Client-first JSON application: rejected because it discards useful HTML, adds crawler and accessibility failure modes, expands bundle and runtime scope, and does not solve the upstream editorial or cost defects.
* Activate and enrich all repository pages: rejected because it directly conflicts with BR-003, creates avoidable indexing churn, and lacks per-URL value evidence. A small evidence-backed set may remain as differentiated profiles.

### Repository Content Consolidation

**Requirements:** Supersede CR-05, preserve valuable URLs, remove low-value output, and provide one interactive summary.

**Preferred Approach:** URL-level keep, merge, redirect, or retire inventory before deletion, with evidence-qualified HTTP 404 as the default retirement action.

**Implementation Details:** Reconcile 266 records, 267 source pages, 274 local rendered URLs, seven aliases, and the live 263-page report. For each canonical, alias, and production-only URL, record current status, canonical, sitemap and internal-link state, URL Inspection, exact-page Search Analytics, sampled Links evidence, available first-party referral evidence, differentiated content, equivalence, disposition, reviewer, and rationale. Permit direct HTTP 404 only when no value is observed in the named sources and no genuine replacement exists. Do not turn missing or ambiguous evidence into zero. Use one-hop 301/308 only for exceptional genuine equivalents. GitHub Pages remains suitable if no redirect rows survive the review.

#### Considered Alternatives

* Blanket redirect to `/repo/`: rejected because generic destinations can discard intent and be treated as soft 404s.
* Blanket deletion without URL evidence: rejected because aggregate evidence cannot establish the status of canonical, alias, and production-only URLs. Evidence-qualified direct 404 remains the selected per-URL retirement action.

### Visual Redesign and Acceptance Baseline

**Requirements:** Resolve CR-02 against BR-001 without falsely accepting or silently abandoning the old release.

**Preferred Approach:** Explicit dated NO-GO/supersession against one immutable revision, preserve historical evidence, and carry all open interaction and accessibility work into the new release gate.

**Implementation Details:** Freeze the old 64-screen/68-check evidence, mark CR-05 superseded, name the new design brief and acceptance revision, and require live keyboard, screen-reader, touch, zoom, reduced-motion, and interaction-state review on the redesigned candidate.

#### Considered Alternatives

* Complete old-release GO first: defensible only if the current experience will operate meaningfully or contractual acceptance is required. Rejected because it spends named-review effort on a surface the approved direction replaces.

### Homepage and Editorial SEO

**Requirements:** BR-002 and BR-006.

**Preferred Approach:** Decide the homepage job and editorial contract first, then repair generation and render complete original summaries in HTML.

**Implementation Details:** Split homepage decision, selection/freshness data, Hugo rendering, and outcome measurement. For yearly content, separate bounded evidence-pack inputs from complete published prose; remove cumulative mid-thought clipping across monthly and yearly stages; add fixture tests rejecting ellipses, incomplete sentences, raw artifacts, missing sections, and untraceable claims; require named editorial and SEO review.

### Interactive Data and Visualization

**Requirements:** BR-004, BR-005, and BR-007.

**Preferred Approach:** Keep authoritative tables and provenance, select a first slice, state each analytical question, compare two representations on common fixtures, and enhance only after comprehension and accessibility review.

**Implementation Details:** Test dense, sparse, tied, zero, long-label, and mobile fixtures. Require non-color encoding, keyboard operation, visible focus, semantic state, touch equivalence, accessible tables, and good field Web Vitals. Embed summaries must be available by hover, focus, touch disclosure, and accessibility tree, with Escape dismissal and collision handling.

### Cost Freshness and Operational Follow-Up

**Requirements:** BR-009 and CR-06.

**Preferred Approach:** Generate the public summary deterministically from the approved ledger and repair experiment hydration independently.

**Implementation Details:** Define accepted-run and retry semantics before aggregation; include period, currency, pricing basis, generation time, and provenance; fail closed on missing, malformed, stale, or unreconciled data. For CR-06, hydrate representative five-hub content before timing and retain comparable runs plus the dated budget conclusion.

## Phased Delivery and Binary Gates

1. Governance closure: complete. V1 records explicit supersession, freezes historical evidence, carries open findings forward, and supersedes CR-05.
2. Decision closure: complete for V1 product and governance policy. Approve V1.1 only for the evidence-gated direct-404 amendment described below.
3. Shared contracts: CR-06 completes; repository URL evidence and disposition contract, versioned schemas, design brief, editorial contract, and cost reconciliation contract are approved.
4. Editorial and shell vertical slice: deliver BR-001, BR-002, BR-006, BR-008, and BR-009 with visual, accessibility, SEO, timing, freshness, and safety evidence.
5. Repository migration: deliver BR-003 without enabling CR-05; require complete URL dispositions, SSR fallback, explorer states, sitemap/internal-link correctness, true HTTP 404 for retirements, conditional one-hop redirects for genuine equivalents, and rollback.
6. Data and embeds: deliver the agreed BR-004/005/007 slice with comprehension, state, accessibility, privacy, and performance evidence.
7. Outcome measurement: one release revision, seven-day smoke, 28-day functionality/search review, three-month migration review, and six-month organic outcome review.

CR-04 remains an independent sponsor-gated operational lane and does not block redesign delivery.

## V1 Amendments and Proposed V1.1 Change

V1 completed the prior governance, ownership, objective, evidence-classification, inventory, and story-boundary amendments. The sponsor's proposed direct-removal policy is a material change because it changes BR-003 policy, acceptance, risk mitigation, and the condition that could force a hosting migration.

Issue V1.1 with these changes before implementation relies on the new policy:

* Permit direct HTTP 404 retirement when URL Inspection, exact-page Search Analytics, sampled Links evidence, available first-party referral evidence, internal-link and sitemap inventory, content review, and equivalence review find no observed value and no genuine replacement.
* Record evidence conclusions as “not observed in named sources,” not absolute claims that a URL was never indexed or linked.
* Keep one-hop hosting-layer 301/308 conditional only for an exceptional genuine replacement. Prohibit blanket explorer redirects and Hugo meta refresh.
* Make redirect-capable hosting conditional on the final approved map containing at least one redirect row. Keep GitHub Pages when all removals qualify for true HTTP 404.
* Treat HTTP 410 as optional and outside the V1 requirement.

## Remaining Gaps

* Sponsor approval and publication of the proposed V1.1 direct-404 policy
* Per-URL URL Inspection, Search Analytics, sampled Links, available first-party referral, deployed status, canonical, sitemap, internal-link, content, and equivalence evidence
* Reconciliation of 263 live URLs, 266 records, 267 source pages, 274 rendered URLs, seven aliases, and any production-only URLs
* Determination of whether any genuine-equivalent redirect remains; only that result can justify a redirect-capable hosting change
* Exact E2 schemas, compatibility rules, sanitization behavior, design artifacts, prototypes, and automated tests
* Manual JavaScript-disabled, keyboard, screen-reader, touch, zoom, reduced-motion, narrow-embed, malformed-data, and production field-performance evidence
* CR-06 experiment evidence and independent CR-04 canary approvals
* Reconciliation of stale source-plan, deferred-work, and external-metadata wording in the historical status record before issue generation cites it

## Research Artifacts

* `.copilot-tracking/research/subagents/2026-08-08/claracle-codebase-surfaces-research.md`
* `.copilot-tracking/research/subagents/2026-08-08/claracle-external-standards-research.md`
* `.copilot-tracking/research/subagents/2026-08-08/claracle-delivery-quality-research.md`
* `.copilot-tracking/research/subagents/2026-08-08/claracle-alternatives-selection-research.md`
* `.copilot-tracking/research/subagents/2026-08-08/claracle-v1-implementation-handoff-research.md`
* `.copilot-tracking/research/subagents/2026-08-08/claracle-redirect-boundary-alternatives-research.md`
* `.copilot-tracking/research/subagents/2026-08-08/claracle-repository-retirement-policy-research.md`
