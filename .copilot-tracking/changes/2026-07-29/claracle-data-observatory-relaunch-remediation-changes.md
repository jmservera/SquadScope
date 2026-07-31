<!-- markdownlint-disable-file -->
# Release Changes: Claracle Data Observatory Relaunch Remediation

**Related Plan**: claracle-data-observatory-relaunch-remediation-plan.instructions.md
**Implementation Date**: 2026-07-29

## Summary

Implementation is in progress. This log separates repository-executed validation from pending external acceptance evidence.

## Finding Traceability

| ID | Severity | Finding | Requirement | Owning Phase | Status | Validation | Evidence |
|---|---|---|---|---:|---|---|---|
| CR-01 | Critical | Weekly content does not populate topic hubs | FR-001 through FR-003 | 2 | Complete | Backfill, corpus, hub membership, and idempotence tests passed | W21-W31 frontmatter and Phase 2 validation |
| CR-02 | Critical | Dynamic topic creation is not operational | FR-004 | 2 | Complete behind rollout gate | Candidate discovery and enabled-only promotion tests passed; production flag remains off | Candidate registry and Phase 2 validation |
| CR-03 | Critical | Repository lifecycle and retention are not enforced | FR-022 | 3 | Complete behind rollout gate | Rename, archive, deletion, absence, retention, expiry, check-mode, and idempotence tests passed | Lifecycle ledger and Phase 3 validation |
| CR-04 | Critical | Topic hubs lack page-appropriate entity schema | FR-033 | 5 | Complete | Nine rendered SEO tests passed under Hugo Extended 0.161.1 | SEO partial and rendered metadata tests |
| CR-05 | Critical | GSC and GA4 operational acceptance is incomplete | FR-035, NFR-007 | 9 | Pending external acceptance | Evidence matrix created; platform verification remains pending | Dated baseline and evidence index |
| CR-06 | Critical | Generated surfaces have no recurring publish integration | FR-003, FR-011, FR-021 | 4 | Complete | Ordered generation, atomic path coverage, lease, failure, and idempotence contracts passed | Weekly publish and deploy workflows plus pipeline tests |
| CR-07 | Critical | Podcaster compatibility lacks release evidence | NFR-002 | 8 | Implementation complete; external acceptance pending | 72 focused tests passed; protected downstream run not yet executed | Pending Actions run URL |
| MAJ-01 | Major | Required implementation traceability artifacts are missing | Implementation governance | 1 | Complete | All 23 findings mapped to phases, statuses, validation, and evidence | This file and related plan |
| MAJ-02 | Major | Topic highlights are manually authored | FR-003 | 2 | Complete | Latest weekly signals render alongside retained authored dataset highlights | Hub template and focused tests |
| MAJ-03 | Major | Repository pages omit curated topic-hub links | FR-020 | 3 | Complete behind rollout gate | Promoted aliases produce curated hub links while raw topics remain tags | Repository generator, template, and focused tests |
| MAJ-04 | Major | Social image dimensions are incomplete | FR-032 | 5 | Complete | Local, fallback, explicit remote, and missing-dimension rendered contracts passed | SEO partial and rendered metadata tests |
| MAJ-05 | Major | SEO regression coverage is narrower than launch contract | FR-030 through FR-034 | 5 | Complete | Canonical, social, schema, XML, feed, and no-news-sitemap rendered contracts passed | Preview workflow and rendered tests |
| MAJ-06 | Major | Weekly-link presence is not regression-tested | FR-040 | 5 | Complete | Required previous/next, canonical topic, and applicable repository groups covered | Weekly rendered-link tests |
| MAJ-07 | Major | Required client-tool design spike is absent | FR-052 | 9 | Complete | Static-hosting, discoverability, effort, alternatives, and consequences documented | Star Velocity Explorer ADR |
| MAJ-08 | Major | Performance, accessibility, and scalability gates lack evidence | NFR-001, NFR-005, NFR-009 | 7 | Partially complete | Static and route checks passed; browser execution and three-run timing approval remain pending | CI reports and owner-approved timing budget |
| MAJ-09 | Major | Analytics instrumentation is incomplete | NFR-008 | 6 | Complete pending browser CI | Consent, withdrawal, sanitization, syntax, rendering, and bounded payload smoke passed | Analytics module, templates, tool instrumentation, and browser spec |
| MAJ-10 | Major | Required security review is absent | NFR-004 | 9 | Review documented; external sign-off pending | Trust boundaries and owned dispositions documented | Pending Hermes and URL sign-off |
| MAJ-11 | Major | Rollout state conflicts with the PRD | Rollout gates | 1 | Partially complete | Creation defaults and disabled continuity verified; dates and sign-offs remain in Phase 9 | `config/observatory.toml`, focused tests, and Phase 9 acceptance evidence |
| MAJ-12 | Major | Visual acceptance claims exceed screenshot evidence | NFR-005 through NFR-007 | 9 | Claims corrected; refreshed evidence pending | Capture matrix documents required populated and unobscured views | Pending refreshed screenshots and review |
| MAJ-13 | Major | Data regeneration still requires intervention | FR-011 | 4 | Complete | Weekly transaction is the sole writer; scheduled data workflow is read-only freshness validation | Workflow contracts and pipeline tests |
| MIN-01 | Minor | Social debugger and feed acceptance evidence is absent | FR-031 through FR-035 | 9 | Pending external acceptance | Evidence slots created; external checks remain pending | Dated evidence index |
| MIN-02 | Minor | Operational ownership is not actionable | Operations | 9 | Complete | Generation, recovery, rollback, dashboards, escalation, and ownership documented | Observatory runbook |
| MIN-03 | Minor | BRD, PRD, and visual-review statuses are inconsistent | Release governance | 9 | Documents reconciled; sponsor acceptance pending | Statuses now reflect unresolved gates and disabled rollout | PRD, BRD, and evidence index |

## Changes

### Added

* `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md` - Progressive implementation, validation, and acceptance traceability for all 23 review findings
* `scripts/backfill_weekly_topics.py` - Deterministic frontmatter-only weekly topic backfill and freshness mode
* `scripts/discover_topic_candidates.py` - Deterministic candidate discovery and freshness mode
* `tests/test_weekly_topic_backfill.py` - Backfill preservation, assignment, stale-check, and idempotence coverage
* `data/taxonomy/topic-candidates.json` - Auditable candidate evidence for 2,176 candidates, including 5 eligible candidates
* `data/derived/observatory/repository-lifecycle.json` - Versioned durable repository identity and lifecycle state
* `assets/js/observatory-analytics.js` - Consent-aware bounded Observatory event dispatcher
* `tests/visual/observatory-analytics.spec.mjs` - Consent, withdrawal, payload, and network browser contracts
* `tests/visual/observatory-a11y.spec.mjs` - WCAG, keyboard, focus, consent, chart alternative, overflow, mobile, and dark-theme checks
* `docs/data-observatory-runbook.md` - Operating, recovery, lifecycle, rollback, dashboard, and escalation procedures
* `docs/decisions/adr-star-velocity-explorer.md` - Auditable client-tool selection decision
* `docs/review/data-observatory-relaunch/security-review.md` - Security trust boundaries, findings, owners, dispositions, and pending sign-offs
* `docs/review/data-observatory-relaunch/screenshots/README.md` - Required populated visual evidence capture matrix

### Modified

* `config/observatory.toml` - Defaulted dynamic topic and repository page creation off
* `scripts/manage_topic_hubs.py` - Enforced explicit non-mutating disabled behavior for dynamic topic creation
* `scripts/observatory_repos.py` - Enforced explicit non-mutating disabled behavior for repository page generation
* `tests/test_topic_hubs.py` - Covered disabled-state continuity and decision output
* `tests/test_observatory_repos.py` - Covered disabled-state non-deletion and decision output
* `scripts/generate_content.py` - Reused canonical topic derivation for historical and future generation contracts
* `scripts/manage_topic_hubs.py` - Consumed candidate evidence and implemented guarded durable promotion and assignment
* `tests/test_generate_content_topics.py` - Added future-generation topic corpus contracts
* `tests/test_topic_hubs.py` - Added candidate, promotion, history, continuity, and feed coverage
* `layouts/topics/list.html` - Rendered latest weekly signals while retaining authored dataset highlights
* `data/taxonomy/topics.json` - Refreshed canonical usage counts
* `content/weekly/2026/W21.md` through `content/weekly/2026/W31.md` - Added resolvable canonical topic membership without changing article bodies
* `scripts/crawl.py` - Retained stable GitHub identity, lifecycle evidence, timestamps, and canonical URLs with legacy fallback
* `scripts/observatory_repos.py` - Added lifecycle reconciliation, aliases, tombstones, retention expiry, curated topic links, and freshness mode
* `tests/test_crawl.py` - Covered retained metadata and backward-compatible records
* `tests/test_observatory_repos.py` - Covered rename, archive, deletion, absence, retention, expiry, stability, and curated links
* `layouts/repo/single.html` - Rendered curated Claracle topic links separately from raw tags
* `config/observatory.toml` - Added reviewed lifecycle and retention configuration inputs
* `.github/workflows/crawl-and-publish.yml` - Added ordered generation, hydration, rollback, atomic staging, and final-byte manifest coverage
* `.github/workflows/deploy-site.yml` - Hydrated all generated Observatory paths from the publish branch
* `.github/workflows/generate-data-pages.yml` - Converted the competing writer to a read-only freshness workflow with required dependencies
* `scripts/observatory_repos.py` - Added workflow-facing freshness behavior
* `scripts/export_observatory_dataset.py` - Added workflow-facing freshness behavior
* `tests/test_pipeline.py` - Enforced command order, generated-path coverage, lease behavior, sole-writer behavior, and freshness dependencies
* `layouts/partials/seo.html` - Added page-class schema and universal social image dimensions and alt metadata
* `tests/test_rendered_seo_metadata.py` - Added canonical, social, schema, XML, feed, and social-image contracts
* `tests/test_rendered_weekly_links.py` - Added required weekly previous/next, canonical topic, and repository link presence checks
* `tests/test_topic_hubs.py` - Expanded promoted topic feed contracts
* `.github/workflows/site-preview.yml` - Runs Phase 5 rendered contracts in a Hugo-enabled preview build
* `assets/js/star-velocity-explorer.js` - Added bounded tool interaction events without query or repository values
* `layouts/partials/cookie-consent.html` - Enables and disables Observatory analytics with consent lifecycle
* `layouts/partials/head.html` - Loads the shared analytics asset through Hugo
* `layouts/partials/visuals/observatory-chart.html` - Emits bounded chart identity for analytics
* `layouts/embeds/baseof.html` - Adds consent-respecting embed load behavior and limitation notice
* `layouts/alias.html` - Emits complete social metadata and breadcrumbs for topic aliases
* `.github/workflows/ci.yml` - Owns the production build, rendered contracts, browser gates, timing capture, and report uploads
* `scripts/design/lighthouse-gates.mjs` - Covers five Observatory routes with performance, accessibility, and CLS thresholds
* `tests/visual/a11y-perf.spec.mjs` - Expands Observatory responsive and performance route coverage
* `tests/visual/playwright.config.mjs` - Defines stable desktop/mobile and light/dark browser projects
* `docs/design/data-observatory-model.md` - Documents report-only timing collection without an unapproved blocking budget
* `.github/workflows/podcaster-handoff-smoke.yml` - Adds reusable exact-release smoke while retaining manual dispatch
* `.github/workflows/deploy-site.yml` - Invokes the protected downstream smoke after successful deployment
* `tests/test_pipeline.py` - Covers exact-release workflow inputs and blocking post-deploy invocation
* `tests/test_podcaster_handoff.py` - Confirms the shared payload contract remains unchanged
* `docs/growth/ga4-gsc-baseline-2026-07-29.md` - Replaced unsupported claims with dated pending platform evidence
* `docs/review/data-observatory-relaunch/README.md` - Indexed repository and external acceptance evidence with bounded claims
* `docs/prds/claracle-data-observatory-relaunch.md` - Reconciled actual delivery, rollout, and open acceptance state
* `docs/brds/claracle-data-observatory-relaunch-brd.md` - Reconciled sponsor lifecycle and pending approvals

### Removed

* None

## Additional or Deviating Changes

* Phase 1 validation used `python3` because the `python` executable is unavailable in the local environment.
	* Equivalent Ruff, pytest, and generator checks passed under the available interpreter.
* `hugo --minify` was not executed because Hugo is unavailable in the local environment.
	* The Hugo baseline remains pending until an environment with Hugo is available.

## Validation History

### Phase 1: Traceability and Rollout Baseline

* Focused rollout tests: 11 passed, 3 skipped
* Ruff lint: passed
* Ruff format check: passed after formatting the two edited test files; 135 files formatted correctly
* Full pytest suite: 1319 passed, 10 skipped, 2 warnings, and 8 subtests passed
* Data-page freshness check: passed
* Trend-explorer freshness check: passed
* Hugo build: skipped because Hugo is unavailable
* `git diff --check`: passed

### Phase 2: Weekly Topic Through-Line

* Focused backfill, generation-topic, and topic-hub tests: 24 passed, 2 Hugo-dependent skips
* Full pytest suite: 1334 passed, 10 skipped, and 8 subtests passed
* Ruff lint and format checks: passed
* Backfill and candidate freshness checks: passed
* Second-generation artifact hashes: byte-identical
* Canonical usage counts: agents 11, LLMs 4, developer tools 3, MCP 2, healthcare 1
* Hugo-rendered hub and feed checks: skipped because Hugo is unavailable

### Phase 3: Durable Repository Lifecycle

* Crawl tests: 17 passed
* Repository lifecycle tests: 10 passed, 1 Hugo-dependent skip
* Full pytest suite: 1340 passed, 10 skipped, and 8 subtests passed
* Ruff lint and format checks: passed
* Generator normal, freshness, and idempotence behavior: passed
* Disabled normal and freshness runs: byte-identical and non-mutating
* Hugo-rendered repository check: skipped because Hugo is unavailable
* `git diff --check`: passed

### Phase 4: Atomic Publish Orchestration

* Complete pipeline tests: 20 passed and 8 subtests passed
* Focused Phase 4 tests: 3 passed, 17 deselected, and 8 subtests passed
* Generator tests: 12 passed, 1 skipped
* Ruff lint and format checks: passed
* Zizmor: no medium or high findings; one pre-existing low-severity unpinned global Copilot install finding
* Freshness commands: four passed; dataset freshness reported timestamp-only drift in `CITATION.md` and `dataset-metadata.json`
* `git diff --check`: passed

### Phase 5: SEO and Rendered Link Contracts

* Focused tests: 11 passed, 13 Hugo-dependent skips
* Ruff lint and format checks: passed
* Zizmor offline workflow scan: no findings
* Rendered SEO contracts after repair: 9 passed under Hugo Extended 0.161.1
* `git diff --check`: passed

### Phase 6: Consent-Gated Observatory Analytics

* JavaScript syntax, dispatcher VM smoke, and Prettier checks: passed
* Consent, withdrawal, and bounded payload smoke: passed
* Hugo minified build: passed with 2669 pages and existing deprecation warnings
* Rendered analytics asset and chart marker assertions: passed
* Playwright browser assertions: blocked before execution by missing host library `libnspr4.so`
* `git diff --check`: passed

### Phase 7: Performance, Accessibility, and Timing Gates

* Static tests: 1332 passed, 4 skipped
* Playwright discovery: 428 tests across desktop/mobile and light/dark projects
* Five Observatory routes: HTTP 200
* Local report-only timing: Hugo 6668 ms; Pagefind 6207 ms
* Checkov: 96 passed, 0 failed
* Zizmor: no findings, with one documented pinned-package exception
* Rendered contracts: 21 passed, 3 SEO failures routed back to Phase 5
* Lighthouse and axe browser execution: blocked locally by missing `libnspr4` and `libnss3`; CI installs pinned dependencies
* Three-run timing median/p95 and owner-approved budget: pending external CI evidence

### Phase 8: Podcaster Release Smoke

* Focused pipeline and handoff tests: 72 passed and 8 subtests passed
* Ruff: passed
* Zizmor: no findings in modified workflows
* Checkov: 91 passed, 0 failed, 1 intentional skip
* Protected downstream Actions execution and run URL: pending deployment
* `git diff --check`: passed

### Phase 9: Documentation and Acceptance Evidence

* Documentation and contract tests: 208 passed, 6 Hugo-dependent skips, and 8 subtests passed
* Markdown structure, aligned tables, frontmatter, and whitespace: passed for all eight files
* All seven local documentation links: resolved
* Checked-in public internal-link check: passed
* Rollout flags: both remain false
* Hermes, URL, GA4, GSC, production response, debugger, Podcaster, accessibility, visual, and sponsor evidence: pending named external owners

### Phase 10: Final Validation

* Ruff lint and format checks: passed
* Full pytest suite: 1362 passed, 2 warnings, and 16 subtests passed
* Hugo Extended 0.161.1 minified build: passed in 6128 ms
* Pagefind 1.5.2: passed in 1534 ms
* Internal link checker: passed
* Checkov: passed with the documented exact-release manual-dispatch skip
* Focused topic, repository lifecycle, crawl, pipeline, and Podcaster acceptance: 111 passed and 8 subtests passed
* Backfill, candidate, data-page, and trend-explorer freshness checks: passed
* Playwright and Lighthouse: blocked by missing local Chromium host libraries `libnspr4` and `libnss3`
* Zizmor: failed with 1 low, 12 medium, and 1 high finding; the high and medium findings are in pre-existing Squad workflows, while the crawl workflow has the low finding
* Literal two-run generation diff proof: pending; focused idempotence and freshness contracts pass

## Release Summary

Implemented the repository-verifiable relaunch foundation across weekly topic membership, candidate promotion, durable repository lifecycle, atomic publication, SEO, consent analytics, browser-quality gates, Podcaster smoke orchestration, and operational documentation.

The current workspace reports 78 changed paths (4 added, 74 modified, 0 removed), including unrelated pre-existing changes that were preserved. No shared Podcaster payload or podcast configuration contract changed. Rollout flags remain disabled.

Phases 1 through 6 are complete. Phases 7 through 10 remain partially open for three-run timing approval, protected downstream execution, external platform and reviewer evidence, refreshed visuals, browser execution on a compatible host, Zizmor remediation, and literal two-run generator proof. The relaunch is not yet accepted.
