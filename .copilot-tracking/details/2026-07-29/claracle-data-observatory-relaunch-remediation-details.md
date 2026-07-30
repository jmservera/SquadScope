<!-- markdownlint-disable-file -->
# Implementation Details: Claracle Data Observatory Relaunch Remediation

## Context Reference

Sources: `.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md`, the six RPI validation reports, the relaunch PRD and BRD, and delegated codebase research.

## Implementation Phase 1: Traceability and Rollout Baseline

<!-- parallelizable: false -->

### Step 1.1: Establish implementation tracking

Create the remediation changes log named by the plan frontmatter. Record every critical, major, and minor review finding, requirement ID, owning phase, implementation status, validation result, and evidence path. Preserve unrelated working-tree changes.

Files:
* `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md` - progressive implementation record

Success criteria:
* All 23 review findings map to one implementation phase or one intentional deferral with an external acceptance checkpoint
* Validation results distinguish executed evidence from pending evidence

Dependencies:
* Approved implementation plan

### Step 1.2: Restore rollout flags to the approved default

Add `repo_pages.enabled = false` and set `topic_hubs.dynamic_creation.enabled = false`. Ensure disabled generators create no new dynamic pages, delete no durable pages, and emit a clear disabled decision. Seed-topic backfill remains active.

Files:
* `config/observatory.toml` - rollout flags and existing thresholds
* `scripts/manage_topic_hubs.py` - dynamic topic flag enforcement
* `scripts/observatory_repos.py` - repository generation flag enforcement
* `tests/test_topic_hubs.py` - disabled-state continuity tests
* `tests/test_observatory_repos.py` - disabled-state non-deletion tests

Success criteria:
* Both creation flags default off
* Existing pages survive disabled runs
* Thresholds remain configuration-only

Dependencies:
* None

### Step 1.3: Capture the executable baseline

Run focused and full Python gates, generator freshness checks, and available Hugo/Pagefind checks. Record unavailable tools and pre-existing failures without weakening gates.

Validation commands:
* `python -m ruff check .`
* `python -m ruff format --check .`
* `python -m pytest -q tests/`
* `python scripts/generate_data_pages.py --check`
* `python scripts/export_trend_explorer_data.py --check`
* `hugo --minify`

## Implementation Phase 2: Weekly Topic Through-Line

<!-- parallelizable: false -->

### Step 2.1: Add deterministic weekly topic backfill

Create a frontmatter-only utility that reuses canonical topic derivation, preserves article bodies and unrelated metadata, validates that mapped hubs exist, and supports `--check`. Backfill W21 through W31 with the assignments verified in research.

Files:
* `scripts/backfill_weekly_topics.py` - deterministic backfill and freshness mode
* `content/weekly/2026/W21.md` through `content/weekly/2026/W31.md` - canonical topic membership
* `tests/test_weekly_topic_backfill.py` - idempotence, body preservation, expected assignments, and stale check
* `tests/test_generate_content_topics.py` - future-generation corpus contract

Success criteria:
* All 11 weekly issues contain resolvable canonical topics
* A second backfill run is byte-stable
* `--check` fails for stale topic frontmatter

Dependencies:
* Phase 1 rollout contract

### Step 2.2: Discover noncanonical topic candidates

Build a deterministic candidate registry from weekly summary tags, headings, raw signal topics, and correlation labels. Exclude known aliases, apply safety and ignore-list rules, count distinct evidence weeks, and persist supporting-signal evidence. Eligibility requires `min_weekly_issues` distinct weeks plus at least one recurring repository-cluster, analysis-summary, or strong press-correlation signal.

Files:
* `scripts/discover_topic_candidates.py` - candidate extraction and `--check`
* `data/taxonomy/topic-candidates.json` - versioned deterministic candidate evidence
* `config/observatory.toml` - existing threshold and ignore-list inputs
* `tests/test_topic_hubs.py` - mixed-signal, ignored, stale, and threshold fixtures

Success criteria:
* Unknown candidates can cross the configured weekly threshold without prior canonical membership only when one qualifying supporting signal is present
* Known aliases never create duplicate hubs
* Candidate output is byte-stable and auditable by week and source

Dependencies:
* Step 2.1 canonical assignment rules

### Step 2.3: Promote candidates and update hubs automatically

Refactor topic management to consume candidate evidence, create and log eligible hubs only when enabled, promote registry entries, and assign promoted topics to qualifying historical and current weekly issues. Add render-time latest weekly signals while retaining authored dataset highlights.

Files:
* `scripts/manage_topic_hubs.py` - candidate consumption, assignment, logging, continuity
* `scripts/taxonomy_registry.py` - post-assignment canonical counts
* `data/taxonomy/topics.json` - refreshed nonzero usage
* `data/topic-hubs/` - promotion logs
* `layouts/topics/list.html` - current weekly signals
* `tests/test_topic_hubs.py` - end-to-end hub, history, RSS, and continuity tests

Success criteria:
* Seed hubs show weekly members and nonempty feeds after backfill
* A four-week enabled candidate creates one logged durable hub and historical assignments
* Quiet weeks do not remove a hub

Dependencies:
* Steps 2.1 and 2.2

## Implementation Phase 3: Durable Repository Lifecycle

<!-- parallelizable: false -->

### Step 3.1: Preserve stable identity and lifecycle fields

Retain GitHub `id`, `node_id`, `archived`, `disabled`, update timestamps, and canonical URL fields in normal crawl records. Update schema validation and fixtures without changing crawl topology or the Podcaster contract.

Files:
* `scripts/crawl.py` - retained GitHub metadata and payload validation
* `tests/test_crawl.py` - schema and compatibility fixtures

Success criteria:
* New artifacts carry stable identity and positive archive/disabled evidence
* Existing reduced records remain readable through a documented fallback
* No authenticated client-side or on-demand recrawl path is introduced

Dependencies:
* Phase 1 baseline

### Step 3.2: Persist lifecycle state and enforce retention

Create and merge a versioned lifecycle ledger keyed by stable GitHub ID with prior names/slugs, first/last seen, status evidence, dates, and retention deadline. Replace unconditional cleanup with reconciliation that preserves missing, archived, renamed, and confirmed-deleted histories until policy permits removal.

Files:
* `scripts/observatory_repos.py` - ledger merge, rename aliases, tombstones, retention-aware reconciliation, `--check`
* `data/derived/observatory/repository-lifecycle.json` - durable lifecycle state
* `config/observatory.toml` - reviewed lifecycle overrides and retention policy
* `tests/test_observatory_repos.py` - rename, archive, deletion, absence, retention, expiry, threshold, and stability tests

Success criteria:
* Same stable ID with a new name produces the new canonical page and old alias
* Absence alone never marks deletion
* Confirmed deleted pages survive source removal for at least three years
* Only expired tombstones are removed, with a logged reason

Dependencies:
* Step 3.1 identity fields

### Step 3.3: Add curated repository-to-topic links

Map recurring repository signals only through promoted topic aliases, preserve raw `/tags/` links, emit a separate curated topic-link collection, and render it on repository pages.

Files:
* `scripts/observatory_repos.py` - promoted-topic mapping
* `layouts/repo/single.html` - Claracle topic hub section
* `tests/test_observatory_repos.py` - known alias and unknown raw-topic behavior

Success criteria:
* Registered aliases produce resolvable `/topics/<slug>/` links
* Unknown raw topics remain tags and never become hubs implicitly

Dependencies:
* Phase 2 registry contract

## Implementation Phase 4: Atomic Publish Orchestration

<!-- parallelizable: false -->

### Step 4.1: Move all weekly-derived generation into the guarded transaction

Hydrate prior generated state before current generation. Run weekly generation, topic discovery/promotion/assignment, manifest rehash, promotion guard, taxonomy refresh, rollups, repository pages, data pages, dataset export, and trend-explorer export in dependency order.

Files:
* `.github/workflows/crawl-and-publish.yml` - authoritative generation transaction
* `scripts/observatory_repos.py` - freshness mode used by workflow
* `scripts/export_observatory_dataset.py` - freshness mode used by workflow
* `tests/test_pipeline.py` - command order and transaction contracts

Success criteria:
* Final promoted content bytes are the bytes hashed in the manifest
* Every generated surface derives from the same hydrated weekly state
* A failed generator prevents branch publication

Dependencies:
* Phases 2 and 3

### Step 4.2: Publish and deploy every generated path atomically

Expand backup, restore, stage, artifact upload, and deploy hydration to include topics, repositories, data pages, taxonomy, topic logs, derived Observatory state, datasets, and tool JSON.

Files:
* `.github/workflows/crawl-and-publish.yml` - backup, restore, stage, and diagnostics
* `.github/workflows/deploy-site.yml` - publish-branch hydration
* `tests/test_pipeline.py` - generated-path coverage and lease behavior

Success criteria:
* One lease-protected commit contains all generated changes
* Deployment renders exactly the generated state from `publish`
* An identical second run produces no generated commit

Dependencies:
* Step 4.1

### Step 4.3: Remove the competing publication path

Convert the monthly data-page workflow to a read-only scheduled freshness check, or retire it if the weekly transaction provides equivalent alerting. It must no longer create an independent publication pull request.

Files:
* `.github/workflows/generate-data-pages.yml` - freshness-only schedule or removal
* `tests/test_pipeline.py` - single-writer contract

Success criteria:
* The weekly transaction is the only writer for Observatory outputs
* Scheduled freshness failures remain visible without branch races

Dependencies:
* Steps 4.1 and 4.2

## Implementation Phase 5: SEO and Rendered Link Contracts

<!-- parallelizable: true -->

### Step 5.1: Emit page-appropriate metadata and schema

Update the active SEO partial to emit `CollectionPage` and weekly `ItemList` for topic terms, `Dataset` and ranking `ItemList` for data pages, and `WebPage` with `SoftwareSourceCode` for repository pages. Preserve `Article` for editorial time-based content and BreadcrumbList for hierarchies.

Files:
* `layouts/partials/seo.html` - active metadata and schema implementation
* `tests/test_rendered_seo_metadata.py` - schema contracts by page class

Success criteria:
* JSON-LD parses for representative and site-wide pages
* Every hierarchy has correct breadcrumb positions and absolute URLs
* Data and repository pages are no longer classified as generic articles

Dependencies:
* Stable generated page shapes from Phases 2 and 3

### Step 5.2: Require dimensions for every social image

Resolve local resource dimensions where possible, retain configured fallback dimensions, and require explicit dimensions for remote or uninspectable custom images.

Files:
* `layouts/partials/seo.html` - universal Open Graph image dimensions
* `tests/test_rendered_seo_metadata.py` - local, fallback, and remote image fixtures

Success criteria:
* Every rendered `og:image` has positive width, height, and alt text
* Missing remote dimensions fail the rendered contract

Dependencies:
* Step 5.1 shared partial edits

### Step 5.3: Expand rendered SEO, sitemap, feed, and weekly-link tests

Audit canonical correctness, complete social fields, JSON-LD types, XML validity, all promoted topic feeds, and absence of a news sitemap. Add required-link presence checks for chronological, canonical topic, and applicable repository links.

Files:
* `tests/test_rendered_seo_metadata.py` - site-wide SEO and XML contract
* `tests/test_rendered_weekly_links.py` - required weekly-link presence
* `tests/test_internal_link_checker.py` - retained target-resolution behavior
* `.github/workflows/site-preview.yml` - preview contract execution
* `tests/test_topic_hubs.py` - promoted topic feed coverage

Success criteria:
* Removing a required weekly link fails tests even when all remaining links resolve
* Every promoted topic feed parses and contains absolute Claracle URLs
* No news sitemap is generated

Dependencies:
* Steps 5.1 and 5.2; Phase 4 build path

## Implementation Phase 6: Consent-Gated Observatory Analytics

<!-- parallelizable: true -->

### Step 6.1: Add a shared consent-aware event API

Create a bounded event dispatcher that no-ops before analytics consent, can be disabled after consent withdrawal, and never queues pre-consent telemetry.

Files:
* `assets/js/observatory-analytics.js` - consent-aware event API
* `layouts/partials/cookie-consent.html` - enable and disable lifecycle
* `layouts/partials/head.html` - normal Hugo asset loading

Success criteria:
* No custom event reaches `dataLayer` or the network before consent
* Consent withdrawal stops future dispatch

Dependencies:
* Existing cookie-consent flow

### Step 6.2: Instrument dataset, chart, and tool interactions

Emit `dataset_download`, `chart_embed_view`, and bounded `tool_interaction` actions. Send only normalized IDs, paths, action names, and sanitized referrer host; never send search terms or repository names.

Files:
* `assets/js/observatory-analytics.js` - delegated dataset tracking
* `assets/js/star-velocity-explorer.js` - bounded tool actions
* `layouts/partials/visuals/observatory-chart.html` - embed chart identity
* `layouts/embeds/baseof.html` - standalone embed load hook
* `tests/visual/observatory-analytics.spec.mjs` - consent, payload, and network assertions

Success criteria:
* Expected events fire after consent with bounded payloads
* Raw user input and repository names never appear in analytics payloads
* Off-site embed limitations are documented without bypassing consent

Dependencies:
* Step 6.1

## Implementation Phase 7: Performance, Accessibility, and Timing Gates

<!-- parallelizable: true -->

### Step 7.1: Expand Lighthouse and browser coverage

Add topic, data, repository, chart, and tool routes. Enforce Performance at least 0.90, retain accessibility at least 0.95 and CLS at most 0.1, and upload machine-readable reports.

Files:
* `scripts/design/lighthouse-gates.mjs` - expanded page matrix and thresholds
* `tests/visual/a11y-perf.spec.mjs` - Observatory page coverage
* `tests/visual/playwright.config.mjs` - stable browser matrix
* `.github/workflows/ci.yml` - single production-build job owning rendered SEO, weekly links, Lighthouse, axe, and responsive checks

Success criteria:
* Required Observatory page classes meet the PRD Lighthouse threshold
* Reports identify route and failed category

Dependencies:
* Phase 4 production-equivalent build

### Step 7.2: Add WCAG-oriented axe and interaction checks

Test WCAG 2.1 A/AA violations, labels, keyboard operation, focus visibility, consent modal behavior, chart text alternatives, responsive overflow, mobile, and dark theme.

Files:
* `tests/visual/observatory-a11y.spec.mjs` - axe and interaction coverage
* `tests/visual/a11y-perf.spec.mjs` - shared responsive assertions
* `.github/workflows/ci.yml` - pinned browser dependencies and report upload

Success criteria:
* No unreviewed serious or critical axe violations
* Core controls work by keyboard and retain visible focus
* Charts have accessible text alternatives

Dependencies:
* Step 7.1 shared build job

### Step 7.3: Measure Hugo and Pagefind separately

Record separate durations in report-only mode for at least three representative CI runs. Calculate median and p95, then require owner approval before introducing a blocking regression budget.

Files:
* `.github/workflows/ci.yml` - timing capture and artifact upload
* `docs/design/data-observatory-model.md` - measured baseline and approved budget

Success criteria:
* Three comparable timing reports exist
* The approved budget is explicit before enforcement
* No invented threshold is presented as acceptance evidence

Dependencies:
* Stable page volume after Phase 4

## Implementation Phase 8: Podcaster Release Smoke

<!-- parallelizable: true -->

### Step 8.1: Make the smoke workflow reusable

Retain manual dispatch and add `workflow_call`. Accept the exact published article path, URL, hash, and manifest or promotion-record reference rather than synthesizing release evidence.

Files:
* `.github/workflows/podcaster-handoff-smoke.yml` - reusable release smoke
* `tests/test_pipeline.py` - workflow shape and exact-release inputs
* `tests/test_podcaster_handoff.py` - unchanged payload contract

Success criteria:
* No changes are required in `config/podcast.json` or `scripts/podcaster_handoff.py`
* The smoke validates exact promoted bytes against the downstream dry-run endpoint

Dependencies:
* Phase 4 transaction output

### Step 8.2: Invoke and retain release evidence

Call the reusable smoke after successful publication and deployment for relaunch acceptance. Keep secrets in the protected environment and record the Actions run URL.

Files:
* `.github/workflows/deploy-site.yml` or a dedicated caller workflow - post-deploy invocation
* `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md` - external run evidence

Success criteria:
* A downstream success is retained for the relaunch state
* Smoke failure blocks relaunch acceptance

Dependencies:
* Step 8.1 and protected environment access

## Implementation Phase 9: Documentation and Acceptance Evidence

<!-- parallelizable: false -->

### Step 9.1: Record operational and design decisions

Create the Observatory runbook and Star Velocity Explorer ADR. Include generation order, flags, outputs, freshness checks, lifecycle overrides, deletion confirmation, retention expiry, dashboards, recovery, rollback, escalation, and the tool comparison.

Files:
* `docs/data-observatory-runbook.md` - operating and recovery procedures
* `docs/decisions/adr-star-velocity-explorer.md` - discoverability, effort, static-hosting fit, alternatives, and consequences

Success criteria:
* Operators can identify ownership, recover a failed run, and roll back creation without deleting durable pages
* FR-052 selection rationale is auditable from repository evidence

Dependencies:
* Final contracts from Phases 2 through 8

### Step 9.2: Complete and sign the security review

Document trust boundaries, sanitization, candidate-title abuse, lifecycle evidence, dataset exposure, embed privacy, tool URL/DOM handling, and secret handling. Hermes must record findings and sign-off.

Files:
* `docs/review/data-observatory-relaunch/security-review.md` - review evidence and disposition

Success criteria:
* All findings have owners and dispositions
* NFR-004 is not marked accepted before Hermes sign-off

Dependencies:
* Implemented code paths from Phases 2, 3, and 6

### Step 9.3: Gather external launch evidence

Verify GSC and sitemap submission, GA4 consent behavior and Realtime receipt, social previews, Rich Results and Schema.org validation, production sitemap/feed responses, Podcaster success, and accessibility review. Record dated evidence links and values.

Files:
* `docs/growth/ga4-gsc-baseline-2026-07-29.md` - actual status and baseline values
* `docs/review/data-observatory-relaunch/README.md` - evidence index with bounded claims
* `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md` - acceptance checklist

Success criteria:
* Every external claim has dated evidence
* Pending evidence remains visibly incomplete
* Screenshots are not used as proof of metadata, schema, network, or lifecycle behavior

Dependencies:
* External platform access and Phases 5 through 8

### Step 9.4: Reconcile release status and visuals

Replace empty or obscured screenshots with populated, mobile, desktop, dark-theme, interaction, and unobscured captures. Update PRD, BRD, risks, dates, flags, open questions, and review status only to the level supported by evidence.

Files:
* `docs/review/data-observatory-relaunch/screenshots/` - refreshed visual evidence
* `docs/review/data-observatory-relaunch/README.md` - honest evidence descriptions
* `docs/prds/claracle-data-observatory-relaunch.md` - actual delivery and rollout state
* `docs/brds/claracle-data-observatory-relaunch-brd.md` - sponsor-approved lifecycle state

Success criteria:
* Topic screenshots show real weekly membership
* Statuses no longer contradict unresolved launch gates
* Dynamic topics and repository pages are enabled in separate approved rollout changes

Dependencies:
* Steps 9.1 through 9.3

## Implementation Phase 10: Final Validation

<!-- parallelizable: false -->

### Step 10.1: Run full repository validation

Execute all project and security gates with repository-pinned versions.

Validation commands:
* `python -m ruff check .`
* `python -m ruff format --check .`
* `python -m pytest -q tests/`
* `hugo --minify`
* `npx "pagefind@1.5.2" --site public/`
* `python scripts/check_internal_links.py public --base-url "https://claracle.com/"`
* `npx playwright test --config tests/visual/playwright.config.mjs`
* Start `python -m http.server 8080 --directory public`, then run `node scripts/design/lighthouse-gates.mjs --base http://127.0.0.1:8080`
* `checkov --directory . --framework github_actions dockerfile secrets --skip-path node_modules --skip-path .venv --compact --soft-fail`
* `zizmor .github/workflows/`

### Step 10.2: Prove idempotence and lifecycle acceptance

Run all generators twice and require byte-stable output on the second run. Exercise flags-off behavior, four-week topic promotion, repository threshold creation, rename/archive/delete fixtures, retention after source removal, and expiry.

Success criteria:
* Second generation produces no diff
* No flag-off run deletes existing pages
* Topic, repository, deploy, and Podcaster evidence all refer to the same release state

### Step 10.3: Fix minor validation issues and report blockers

Apply isolated corrections and rerun the affected check. Document failures requiring architecture or product decisions instead of weakening checks or making large unplanned changes.

## Dependencies

* Python and project dependencies from `requirements.txt` and `pyproject.toml`
* Hugo Extended version used by CI
* Node.js with pinned Pagefind, Playwright, Lighthouse, and axe dependencies
* Protected GitHub environment secrets for deploy, GA4/GSC configuration, and Podcaster smoke
* External reviewer access for GSC, GA4, social/schema tools, accessibility review, and Hermes sign-off

## Success Criteria

* All seven critical, thirteen major, and three minor review findings are closed or intentionally deferred with explicit rationale and an acceptance checkpoint
* FR-001 through FR-004, FR-011, FR-020 through FR-022, FR-030 through FR-035, FR-040, FR-041, FR-052, and NFR-001 through NFR-010 have traceable evidence
* Existing accepted FR-010, FR-050, FR-051, FR-053, and FR-060 behavior remains intact
* The static Hugo architecture and Podcaster payload contract remain unchanged
