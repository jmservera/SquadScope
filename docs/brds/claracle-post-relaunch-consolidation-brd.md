---
title: Claracle Post-Relaunch Consolidation BRD
description: Consolidated business requirements for Claracle post-relaunch acceptance, design, content, and data-experience improvements
author: SquadScope Squad
ms.date: 2026-08-08
ms.topic: reference
keywords:
  - business requirements
  - claracle
  - data observatory
  - post-relaunch
  - consolidation
estimated_reading_time: 8
---

<!-- markdownlint-disable-file -->

# Claracle Post-Relaunch Consolidation BRD

## Document Control

| Field | Value |
|-------|-------|
| BRD ID | BRD-CLARACLE-003 |
| Status | Approved business baseline |
| Version | 1.1 |
| Author | SquadScope Squad |
| Sponsor | jmservera (also the human approval authority) |
| Last updated | 2026-08-08 |
| Related repositories | SquadScope, SquadScope-Podcaster, SquadScope-Coordinator |
| Supersedes (context) | [BRD-CLARACLE-002](claracle-data-observatory-relaunch-brd.md), [PRD relaunch](../prds/claracle-data-observatory-relaunch.md) |

### Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 0.1 | 2026-08-08 | SquadScope Squad | Initial consolidation of the remaining relaunch acceptance gates, rollout activations, and one engineering follow-up; placeholder for new requirements |
| 0.2 | 2026-08-08 | SquadScope Squad | Added post-relaunch requirements for visual design, homepage and yearly editorial content, repository and data experiences, visualization, embeds, navigation, and cost freshness |
| 0.3 | 2026-08-08 | jmservera, SquadScope Squad | Approved objectives and product contracts; superseded the unaccepted relaunch and repository-page activation; assigned accountable owners; closed the remaining business decisions |
| 1.0 | 2026-08-08 | jmservera, SquadScope Squad | Approved the business baseline, governance and change control, release severity policy, repository retention and redirect rules, chart participant model, cost identity, risks, delivery scope, and traceability |
| 1.1 | 2026-08-08 | jmservera, SquadScope Squad | Approved evidence-gated direct HTTP 404 retirement for repository URLs without observed value or a genuine replacement; retained conditional redirects for exceptional genuine replacements |

---

## 1. Purpose

The Claracle Data Observatory relaunch (BRD-CLARACLE-002 / the relaunch PRD) is **feature-complete
and its planning is closed**. All prior implementation plans under `.copilot-tracking/plans/` are
marked done or cancelled; any remaining items are carried into this document so the older plans can
be retired. This BRD is the single forward-looking backlog for the remaining relaunch items and the
next phase of Claracle's design, editorial, and interactive data experience.

## 2. Delivered Baseline (context, not in scope here)

Recorded as delivered in the [relaunch status of record](../review/data-observatory-relaunch/status-of-record.md):

- Discovery IA: topic hubs, data pages (monthly regen), 266 repository pages, internal linking.
- Technical SEO (FR-030..035) including the `author.url` structured-data completion (2026-08-08).
- Analytics and search: GA4/GSC connection, dated launch baseline (NFR-007) and consent behaviour
  (NFR-008), captured 2026-08-08.
- Security acceptance (NFR-004) approved 2026-08-06.
- CI timing budget approved and **enforced** (NFR-009) 2026-08-08 (Hugo 6,000 / Pagefind 5,500 /
  total 11,500 ms).
- Deploy/hydration parity and embed-reference guards (NFR-011/012).
- Linkable assets: MIT dataset, embeddable chart, Star Velocity Explorer tool, State-of page.
- External metadata validation (FR-032/033, NFR-006): home/article/repo pass (2026-08-08).

## 3. Carried-Over Requirements (remaining relaunch work)

> Priority: **Must** (blocks final release acceptance), **Should** (high value), **Could** (opportunistic).

### 3.1 Historical acceptance disposition

| ID | Requirement | Owner(s) | Priority | Acceptance |
|----|-------------|----------|----------|------------|
| CR-01 | Carry the unresolved NFR-005 keyboard and live screen-reader findings into the redesigned-release acceptance plan; do not treat them as blockers to historical supersession | Fry + named a11y reviewer | Must | Every historical finding maps to a redesigned-release test or named review with owner and severity; release follows the Section 8 severity policy |
| CR-02 | Freeze the reviewed 64-screenshot matrix as historical evidence and carry the missing interaction states (filter combinations, expanded detail, copy actions, visible keyboard focus) into the redesigned-release acceptance plan | Amy, Fry | Must | Historical revision and evidence remain immutable; every missing interaction state maps to redesigned-release evidence; see [visual review handoff](../review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md) |
| CR-03 | Record the 2026-08-08 sponsor NO-GO/supersession of the unaccepted relaunch against its immutable revision; preserve existing evidence as historical and carry unresolved interaction and accessibility findings into the redesigned release | jmservera | Must | Dated supersession recorded in the status of record without claiming final relaunch acceptance; historical evidence frozen and every open finding mapped to a redesigned-release gate |

### 3.2 Rollout activations (staged, sponsor-gated)

| ID | Requirement | Owner(s) | Priority | Acceptance |
|----|-------------|----------|----------|------------|
| CR-04 | Dynamic-topic canary activation: approve the staged `allow_topics = ["local-first"]` revision, flip `enabled = true`, review the resulting transaction, then expand one reviewed slug at a time | Amy, Hermes, jmservera | Should | Hermes + sponsor approval of the exact revision; the promotion transaction reviewed (sanitization, YAML, evidence-backed assignments, taxonomy, logging, rendering, disabled rollback) |
| CR-05 | Superseded by BR-003 on 2026-08-08. Do not activate the generated repository-detail corpus; preserve its identity, lifecycle, alias, and rollback evidence as input to the consolidated repository migration | jmservera, Leela, URL | Must | `[repo_pages] enabled` remains `false`; BR-003 inventory accounts for 266 detail records, 267 source pages, 274 local rendered URLs, seven aliases, and the live-count discrepancy before migration |

### 3.3 Engineering follow-up

| ID | Requirement | Owner(s) | Priority | Acceptance |
|----|-------------|----------|----------|------------|
| CR-06 | Fix the cost-experiment harness so Q-01 can complete: the deploy/experiment hydration `rm -rf content/topics/ && git checkout publish -- content/topics/` collapses topic hubs to the single stale `ai-ml` hub carried on `publish`. Either publish the 5 seed-hub `_index.md` files to `publish`, or scope `content/topics/` out of the experiment's `topic_hubs` expected count. Production is unaffected (term pages are taxonomy-driven). | URL, Leela | Should | A clean `build-cost-experiment.yml` run on `main` with retained artifacts and a dated budget-owner conclusion (Q-01 / NFR-009 incremental cost) |

## 4. Out of Scope

- Re-delivery of anything in Section 2 (already shipped and accepted).
- Changing the deploy hydration semantics beyond the narrowly-scoped CR-06 fix without URL review.
- The retired implementation plans themselves (closed; see Section 6).

## 5. Success Criteria

- CR-01 and CR-02 evidence is preserved and its open findings are carried into the redesigned release; CR-03 records explicit supersession rather than final relaunch acceptance.
- CR-04 executes only under sponsor approval; CR-05 remains disabled and is superseded by BR-003.
- CR-06 produces an admissible cost-experiment result.
- The redesigned experience meets the objectives and acceptance criteria in Section 7.

## 6. Retired Plans

All plans under `.copilot-tracking/plans/` are closed as of 2026-08-08. Fully-delivered plans are
marked **DONE**; plans whose only open items were human-gated are marked **CLOSED** with those items
migrated to Section 3 of this BRD. See each plan's status banner for its final state.

## 7. Post-Relaunch Experience Requirements

### 7.1 Business objectives and success measures

| ID | Objective | Owner | Baseline and source | Approved target and window |
|----|-----------|-------|---------------------|----------------------------|
| OBJ-01 | Give Claracle a distinctive, credible visual identity suited to a GitHub trend observatory | Calculon | 64 screenshots and 68/68 visual-regression checks; one local analytics check failed, axe and Lighthouse evidence were unavailable, and manual interaction plus live assistive-technology work remain open | Approved design brief; zero unresolved severity-1 or severity-2 visual or accessibility defects; all applicable automated and named human gates pass before release, followed by a seven-day production smoke |
| OBJ-02 | Improve discovery and organic-search value by presenting useful summaries and clear paths into weekly, monthly, yearly, repository, and data coverage | Leela | 0 organic sessions, 149 impressions, 0 clicks, 294 indexed pages, and 17 impression-bearing queries in the dated GA4/GSC baseline | At least 250 organic sessions per complete 28-day month and at least 15 queries in the top 20 by six months; capture release-day, 28-day, three-month, and six-month evidence |
| OBJ-03 | Replace low-value generated pages with faster, more useful exploration experiences | Leela | 266 detail records, 267 source pages, 274 local rendered URLs, seven aliases, and a live count of 263 requiring reconciliation | Zero low-information detail pages emitted and 100% of canonical, alias, and production-only URLs receive approved evidence-backed keep, merge, redirect, or retire treatment before release; review migration at 28 days and three months |
| OBJ-04 | Make Claracle's data easier to explore and interpret | Amy | Three server-rendered ranking pages and a shared bar-chart representation; no comprehension baseline | All three ranking pages pass server-rendering, provenance, download, state, error, accessibility, and timing contracts before merge; selected representations support correct inference for at least four of five representative readers during prototype selection, followed by a seven-day production smoke |
| OBJ-05 | Keep published operational facts current and traceable to their source | Bender | Static W19-W21 cost summary without provenance while the active ledger reaches W23 | Every public cost record includes source, period, generation time, pricing basis, and approved freshness; missing, malformed, unreconciled, or more than 30 days stale input fails publication on every owning pipeline run |

### 7.2 Business requirements

| ID | Requirement | Linked objective(s) | Accountable owner | Evidence | Priority | Acceptance criteria |
|----|-------------|---------------------|-------------------|----------|----------|---------------------|
| BR-001 | Claracle shall adopt a cohesive visual direction across the Hugo site that expresses the character of a GitHub trend observatory rather than a generic publication template. The primary audience is technology decision-makers who need to understand what is changing in open-source technology and enter the strongest current evidence. | OBJ-01 | Calculon | Sponsor input (E0); historical visual baseline (E1/E3) | Must | Sponsor approves the design brief and representative homepage, article, repository summary, and data-page views at mobile and desktop widths; typography, color, spacing, motion, focus, reduced-motion, and contrast behavior are consistent and pass applicable accessibility and visual gates |
| BR-002 | The homepage shall help technology decision-makers quickly understand the most important current changes and enter weekly, monthly, yearly, topic, repository, and data evidence through concise, original summaries. Its rendered HTML shall remain useful without client-side JavaScript and shall support search discovery without duplicated or padded content. | OBJ-01, OBJ-02 | Leela | Sponsor input (E0); homepage and GA4/GSC baselines (E1/E4) | Must | An approved content hierarchy defines selection, freshness, ownership, and fallback rules for every module; rendered output contains crawlable summaries and internal links, unique title and description metadata, valid structured data, one clear page heading, and no layout shift or empty optional module |
| BR-003 | Claracle shall replace 266 low-information repository detail records with a consolidated repository summary backed by a versioned JSON data artifact, subject to a complete inventory of 267 source pages, 274 local rendered URLs, seven aliases, and the live-count discrepancy. The summary shall support search; topic, language, status, and period filters; default sorting by recent momentum; URL-persisted state; sanitized generated-context summaries; and direct GitHub links. | OBJ-02, OBJ-03 | Leela | Sponsor input (E0); repository inventory and generated artifact (E1/E2) | Must | Every canonical, alias, and production-only URL receives an approved keep, merge, redirect, or retire disposition before removal. Retain a profile only when it has differentiated content plus demonstrated GSC demand or a known inbound link. A URL may retire directly with HTTP 404 when URL Inspection, exact-page Search Analytics for the recorded window, sampled Search Console link evidence, available first-party referral evidence, internal-link and sitemap inventory, content review, and destination-equivalence review show no observed value and no genuine replacement. Record evidence absence as "not observed in named sources," not as an absolute historical claim. Use a one-hop hosting-layer 301/308 only when an exceptional approved destination preserves the old URL's repository-specific intent. HTTP 410 is optional and is not a V1 requirement. The production build emits no low-information details; the explorer works with keyboard and assistive technology, provides useful non-JavaScript output, handles empty/error states, and validates its documented schema and freshness metadata |
| BR-004 | All three generated ranking pages shall use versioned JSON artifacts to provide interactive filtering, sorting, and chart exploration without sacrificing crawlable summaries, source attribution, download access, or accessibility. Shared behavior and schema shall be reused with the repository summary where practical. | OBJ-02, OBJ-04 | Amy | Sponsor input (E0); existing ranking pages and generator (E1/E2) | Should | All three pages provide responsive controls, stable shareable state where useful, keyboard operation, screen-reader labels, empty/error states, provenance and freshness details, and a meaningful server-rendered summary; approved interaction, rendering, and field-performance budgets pass |
| BR-005 | The current bar-chart representation shall be replaced on all three ranking pages where another representation better answers the page's analytical question. Dot plots, slope or trend views, and ranked-table treatments shall be compared against representative dense, sparse, tied, zero, long-label, and mobile data before selection. | OBJ-01, OBJ-04 | Calculon | Sponsor input (E0); current chart baseline (E1/E2) | Should | At least two suitable alternatives are evaluated per analytical question; an internal five-member squad proxy performs the initial comprehension test; the selected representation supports correct inference for at least four participants, retains an equivalent accessible table, renders responsively, uses non-color-only encoding, and states what the reader should infer; production evidence remains the external outcome check |
| BR-006 | The yearly summary generation process shall produce a complete 1,200-1,800-word analytical journalistic article annually, using monthly evidence, rather than clipped excerpts. Farnsworth is accountable and jmservera is the final editor. Every substantive claim shall remain traceable to source data. | OBJ-02 | Farnsworth | Sponsor input (E0); broken 2026 output and generator trace (E1/E2) | Must | Cumulative truncation is corrected across monthly and yearly generation; the 2026 page contains no raw, clipped, or incomplete artifacts; headline, description, headings, canonical metadata, Article structured data, internal/source links, byline, dates, and social preview are validated; named editorial approval and claim-to-source review are retained |
| BR-007 | Embeddable reports shall make every displayed repository name a direct GitHub link and expose a sanitized generated-context summary of approximately 160 characters through hover, keyboard focus, touch disclosure, and the accessibility tree. | OBJ-03, OBJ-04 | Amy | Sponsor input (E0); embed data and rendering baseline (E1/E2) | Should | Links use safe embed navigation; summaries use the approved source and sanitization rule; hover, focus, touch, Escape dismissal, persistence, screen-reader access, collision handling, zoom, and narrow embeds are verified; supplementary content does not obscure controls or become the only source of essential information |
| BR-008 | The primary navigation shall place Weekly, Monthly, and Yearly destinations first, in that order, while preserving clear access to the remaining top-level destinations. | OBJ-02 | Amy | Sponsor input (E0); current menu configuration (E1) | Must | The order is consistent across desktop, mobile, keyboard, and assistive-technology navigation; active states and URLs remain correct; no item is clipped or inaccessible at supported widths |
| BR-009 | The About page shall display current cost information generated from `data/metrics/token-usage.jsonl`. Aggregation shall identify records by workflow run ID, stage, and attempt; count only the accepted attempt for each stage; exclude retries and `model: none` billing; and use a 30-day freshness threshold. jmservera approves pricing-basis changes and exceptions. | OBJ-05 | Bender | Sponsor input (E0); stale summary and active ledger (E1/E2) | Must | The generated record includes covered period, generation timestamp, currency, pricing basis, provenance, accepted workflow/run/stage identities, and reconciliation result; the owning pipeline and site build fail when required data is missing, malformed, unreconciled, or more than 30 days stale; the About page no longer consumes an independently maintained total |

### 7.3 Constraints and dependencies

* Hugo remains the publishing platform, and rendered pages must retain useful server-generated HTML for search engines, no-JavaScript access, and resilience.
* JSON artifacts must have documented schemas, deterministic generation, provenance, publication paths, and freshness metadata. They must not expose secrets or unreviewed raw content.
* Repository retirement evidence is URL-level. Aggregate GA4/GSC totals, sitemap membership, local-build absence, and sampled link-report absence cannot alone prove that a URL was never indexed or has no inbound links. Missing or ambiguous evidence blocks the evidence-gated direct-404 path and requires manual disposition.
* Redirect-capable hosting is required only when the approved final URL map contains a genuine-equivalent redirect. The selected host must deploy site content and generated redirect rules atomically. When the approved map contains no redirect rows, a host that returns true HTTP 404 for absent paths satisfies BR-003.
* Interactive views must meet the existing accessibility, privacy, performance, content-security, and responsive-design gates.
* Generated editorial text remains subject to factual, prompt-injection, and human editorial review.

### 7.4 Approved decisions

* The unaccepted relaunch and CR-05 are superseded. Historical evidence remains preserved, and unresolved interaction and accessibility findings carry into the redesigned release.
* Technology decision-makers are the primary homepage audience. The homepage's main job is to explain what is changing in open-source technology and lead readers to the strongest current evidence.
* The repository explorer uses topic, language, status, and period filters; recent momentum as its default sort; URL-persisted state; sanitized generated-context summaries; direct GitHub links; and URL-level keep, merge, redirect, or retire migration.
* An individual repository profile survives only when differentiated content plus GSC demand or a known inbound link is demonstrated. Direct HTTP 404 retirement is permitted only through the approved evidence gate. Permanent redirects are conditional and require a genuine equivalent. Blanket explorer redirects, Hugo meta refresh as the production redirect mechanism, and absolute "never indexed" or "no inbound links" claims from incomplete sources are prohibited.
* All three generated ranking pages form the first interactive data slice. Visualization selection compares dot plots, slope or trend views, and ranked-table treatments against each page's analytical question.
* An internal five-member squad proxy performs the initial visualization comprehension test. Production evidence validates the external outcome after release.
* The yearly article is an annual 1,200-1,800-word analytical journalistic feature based on monthly evidence. Farnsworth is accountable, and jmservera provides final editorial approval.
* Embeds link directly to GitHub and expose sanitized generated-context summaries of approximately 160 characters through equivalent pointer, keyboard, touch, and assistive-technology interactions.
* `data/metrics/token-usage.jsonl` is the authoritative public cost ledger. Workflow run ID, stage, and attempt form the identity key; only the accepted attempt counts; retries and `model: none` billing are excluded; 30 days is the publication freshness threshold; jmservera owns pricing-basis changes and exceptions.

### 7.5 Implementation guidance

* Follow the repository's `frontend-design` skill during design discovery and implementation, including a documented subject, audience, page purpose, token system, layout concept, signature element, and self-critique.
* Use shared normalized and versioned data contracts, authoritative server-rendered Hugo HTML, and scoped progressive JavaScript enhancement.
* Treat BR-001 through BR-009 as epics. Split decision, generator or data, server-rendered experience, client enhancement, automated validation, named human acceptance, migration, and outcome-measurement work into independently deliverable stories.

## 8. Risks and Release Policy

| Risk | Owner | Required mitigation and gate |
|------|-------|------------------------------|
| Repository consolidation causes search loss or broken inbound links | Leela, Zapp, URL | Reconcile every canonical, alias, and production-only URL; retain URL Inspection, Search Analytics, sampled link, available first-party referral, internal-link, sitemap, content, and equivalence evidence; require approved dispositions; generate one-hop hosting redirects only for genuine equivalents; verify true HTTP 404 for direct retirements; validate canonicals, internal links, sitemap, custom 404 behavior, atomic deployment where redirects exist, and rollback; review GSC at 28 days and three months |
| Interactive redesign excludes keyboard, touch, screen-reader, zoom, reduced-motion, or no-JavaScript users | Amy, Fry | Preserve server-rendered content; validate equivalent interactions and visible focus; complete automated and named manual accessibility evidence before release |
| Generated yearly or repository summaries contain unsupported, clipped, unsafe, or inaccurate claims | Farnsworth, Nibbler | Preserve claim-to-source traceability, sanitization, prompt-injection review, fixture tests, and named human editorial approval |
| Cost, repository, or ranking data is stale, malformed, duplicated, or unreconciled | Bender, URL | Use versioned deterministic contracts, provenance, freshness and reconciliation gates, accepted-record identity, and fail-closed publication behavior |
| Progressive enhancement or external assets fail and remove essential content | Amy, URL | Keep essential content and links in Hugo HTML; test unavailable, malformed, empty, stale, and future-version payloads; preserve rollback and bounded client budgets |

Severity 1 and severity 2 findings in visual design, accessibility, security, data integrity,
or SEO migration block release. Lower-severity findings require an accountable owner and
due date. Any exception to a blocking finding requires a documented sponsor decision,
rationale, compensating control, and expiry date.

## 9. Delivery Scope and Traceability

| Delivery epic | Requirements | Included outcome | Explicitly deferred evidence |
|---------------|--------------|------------------|------------------------------|
| Governance and operational closure | CR-01 through CR-06 | Historical supersession, carried-forward acceptance findings, independent dynamic canary, representative cost experiment, and disabled repository-page rollout | Production redesign evidence and long-term outcome measurement |
| Experience foundation | BR-001, BR-008 | Approved design system, shared shell, and Weekly/Monthly/Yearly-first navigation | Repository and data interaction behavior |
| Editorial discovery | BR-002, BR-006 | Homepage hierarchy and complete yearly journalistic article with crawlable metadata | Six-month organic outcome conclusion |
| Repository consolidation | BR-003 | Versioned repository contract, server-rendered summary, progressive explorer, evidence-backed direct HTTP 404 retirement, and conditional redirects for genuine equivalents | 28-day and three-month migration observations |
| Data exploration and embeds | BR-004, BR-005, BR-007 | All three ranking pages, evidence-selected visualizations, and accessible linked embed summaries | Seven-day production outcome evidence |
| Cost provenance | BR-009 | Deterministic ledger projection, accepted-attempt identity, freshness gate, and current About display | Future pricing-basis changes |

| Objective | Satisfied by |
|-----------|--------------|
| OBJ-01 | BR-001, BR-005 |
| OBJ-02 | BR-002, BR-003, BR-004, BR-006, BR-008 |
| OBJ-03 | BR-003, BR-007 |
| OBJ-04 | BR-004, BR-005, BR-007 |
| OBJ-05 | BR-009 |

## 10. Approval and Change Control

| Field | Approved value |
|-------|----------------|
| Approved by | jmservera, sponsor and human approval authority |
| Approval date | 2026-08-08 |
| Approved version | 1.1 |
| Approval meaning | Approved business baseline for implementation planning; designs, schemas, story decomposition, migration evidence, implementation, and release evidence remain delivery work |
| Approved scope | CR-01 through CR-06, OBJ-01 through OBJ-05, BR-001 through BR-009, approved decisions, constraints, risks, delivery scope, and release policy in this document |

Version 1.1 is the controlled business baseline. Material changes require sponsor
reapproval and a new document version. Material changes include additions or removals
of scope, objectives, targets, priorities, accountable owners, approved product or
operational policy, acceptance criteria, release-blocking severity, or change-control
rules. Implementation details may change through normal architecture, code, security,
and review workflows when they remain within this baseline.
