---
title: Claracle Data Observatory Relaunch Remediation Research
description: Planning research for remediation work identified by the relaunch reviews
ms.date: 2026-07-29
ms.topic: reference
---

## Research Scope

Status: Complete

Research questions:

* What implementation work closes every missing task in the supplied review and six RPI validation reports?
* Which exact files and line ranges control each required behavior?
* What dependencies, sequencing, and parallel workstreams minimize rework?
* Which validation commands provide sufficient implementation evidence?
* Which decisions are resolvable from repository evidence, and which acceptance tasks must remain external or manual?

Required workstreams:

* Weekly topic backfill, emission, and candidate discovery
* Publish orchestration for topic, repository, dataset, and tool generators
* Durable repository lifecycle and retention
* Topic highlights and repository-to-topic links
* SEO, schema, social dimensions, and rendered regression tests
* Weekly link presence tests
* Analytics events
* Rollout flags
* Performance, accessibility, and build timing gates
* Podcaster smoke integration
* External and manual acceptance evidence
* Security review, runbook, and design decision
* Status and evidence reconciliation

## Sources

Primary requirements and architecture:

* `docs/prds/claracle-data-observatory-relaunch.md:1-276`
* `docs/brds/claracle-data-observatory-relaunch-brd.md:1-324`
* `architecture.md:1-86`
* `.github/copilot-instructions.md:1-69`
* `AGENTS.md:1-29`

Supplied reviews:

* `.copilot-tracking/reviews/2026-07-29/claracle-data-observatory-relaunch-review.md:1-173`
* `.copilot-tracking/reviews/rpi/2026-07-29/claracle-data-observatory-relaunch-001-validation.md:1-208`
* `.copilot-tracking/reviews/rpi/2026-07-29/claracle-data-observatory-relaunch-002-validation.md:1-204`
* `.copilot-tracking/reviews/rpi/2026-07-29/claracle-data-observatory-relaunch-003-validation.md:1-178`
* `.copilot-tracking/reviews/rpi/2026-07-29/claracle-data-observatory-relaunch-004-validation.md:1-124`
* `.copilot-tracking/reviews/rpi/2026-07-29/claracle-data-observatory-relaunch-005-validation.md:1-119`
* `.copilot-tracking/reviews/rpi/2026-07-29/claracle-data-observatory-relaunch-006-validation.md:1-207`

Implementation and evidence sources are cited by workstream below. No
implementation files were modified during this research.

## Findings

### Executive assessment

The remediation is not one large feature build. It is an operationalization and
acceptance program around substantial existing code. The critical implementation
path is:

1. Make topic assignment deterministic for existing and future weekly issues.
2. Discover noncanonical topic candidates from weekly signals without confusing
   raw GitHub tags with editorial topic hubs.
3. Run all weekly-derived generators in the guarded publish transaction and
   hydrate their outputs during deployment.
4. Replace ephemeral repository regeneration with a durable identity and
   lifecycle ledger.
5. Expand rendered contracts and CI quality gates.
6. Gather external acceptance evidence and reconcile release status.

Four asset requirements are already functionally complete and should not be
reimplemented: downloadable dataset FR-050, chart embed FR-051, State-of page
FR-053, and README discovery FR-060. The Star Velocity Explorer runtime is also
complete; FR-052 only lacks its selection decision record.

### Weekly topic backfill and emission

Controlling code and evidence:

* `scripts/generate_content.py:194-255` loads the canonical topic vocabulary and
  maps analysis tags and explicit topics to it
* `scripts/generate_content.py:285-293` emits `topics` in weekly frontmatter
* `scripts/generate_content.py:320-340` derives topics during summary transform
* `tests/test_generate_content_topics.py:25-57` covers alias mapping, rejection,
  safety, and empty-topic compatibility
* `content/weekly/2026/W21.md:1-12` through
  `content/weekly/2026/W31.md:1-12` have tags but no `topics`
* `data/taxonomy/topics.json:1-103` defines the five promoted hubs and aliases but
  records zero use

The emission implementation is valid for future generation, but accepted content
predates or bypasses it. Add a deterministic frontmatter-only backfill utility,
recommended as `scripts/backfill_weekly_topics.py`, that reuses
`derive_canonical_topics()`, preserves article bodies and unrelated frontmatter,
supports `--check`, and fails if a mapped topic lacks a content hub. Do not
regenerate entire articles from analysis summaries because W21 content tags differ
from its analyzed-summary tags and article body changes are outside remediation.

Expected backfill from the checked-in aliases:

| Week | Canonical topics |
|------|------------------|
| 2026-W21 | AI Coding Agents; MCP Ecosystem |
| 2026-W22 | AI Coding Agents; Open-Source LLMs; Developer Tools |
| 2026-W23 | AI Coding Agents |
| 2026-W24 | AI Coding Agents |
| 2026-W25 | AI Coding Agents; Open-Source LLMs |
| 2026-W26 | AI Coding Agents; MCP Ecosystem; Open-Source LLMs |
| 2026-W27 | AI Coding Agents |
| 2026-W28 | AI Coding Agents |
| 2026-W29 | AI Coding Agents; Developer Tools |
| 2026-W30 | AI Coding Agents; Open-Source LLMs |
| 2026-W31 | AI Coding Agents; Developer Tools; AI Agents in Healthcare |

After backfill, run `scripts/taxonomy_registry.py` and verify nonzero counts,
nonempty topic RSS, and rendered issue cards. Add corpus assertions to
`tests/test_generate_content_topics.py` or a focused
`tests/test_weekly_topic_backfill.py` for idempotence, body preservation, expected
W21/W26/W31 assignments, and `--check` failure on stale content.

### Candidate discovery and dynamic topic promotion

Current control path:

* `scripts/taxonomy_registry.py:150-163` counts canonical `topics` from weekly
  frontmatter
* `scripts/taxonomy_registry.py:167-179` records raw repository topics only as
  tags
* `scripts/taxonomy_registry.py:249-283` rebuilds topic and tag registries
* `scripts/manage_topic_hubs.py:120-148` only reads non-hub entries already in
  the topic registry
* `scripts/manage_topic_hubs.py:211-258` applies threshold, continuity, logging,
  hub creation, and promotion
* `config/observatory.toml:18-31` holds dynamic threshold and ignore-list values
* `docs/design/data-observatory-model.md:307-337` already defines the intended
  multi-signal heuristic

The circular dependency is real: unknown signals cannot enter canonical weekly
`topics`, and only canonical weekly `topics` can become candidates. Preserve the
editorial separation between raw tags and promoted hubs by adding a separate
candidate artifact, recommended as
`data/taxonomy/topic-candidates.json`, generated by a focused module such as
`scripts/discover_topic_candidates.py`.

The discovery module should:

* Normalize weekly summary tags, recurring heading terms, raw
  `signals.top_topics`, and correlation labels by ISO week
* Map known aliases to existing hubs and exclude them from candidate promotion
* Count unknown candidates by distinct week within `lookback_days`
* Require `min_weekly_issues` plus one supporting signal already specified in
  `docs/design/data-observatory-model.md:323-335`: a recurring repository
  cluster, analysis-summary usage, or a strong press correlation
* Apply `safe_candidate_title()` and the configured ignore list before writing
* Persist evidence weeks, source paths, supporting-signal classes, aliases,
  first/last seen dates, and a deterministic display name
* Produce byte-stable output and support `--check`

Refactor `manage_topic_hubs.py:120-148` to consume that candidate artifact rather
than fabricated registry-count week names. On promotion it must create the hub,
promote the canonical registry entry, retain the candidate evidence in the log,
and assign the new canonical topic to all qualifying historical weekly issues.
Those assignments are required for taxonomy aggregation and per-topic RSS. Future
runs must also attach the promoted topic whenever its candidate signal appears,
even when that signal came from raw data rather than a summary tag.

Extend `tests/test_topic_hubs.py:46-212` with an end-to-end fixture containing
four recent distinct weeks, mixed signal sources, one supporting signal, one
ignored candidate, and one stale candidate. Assert historical assignment, current
assignment, hub creation, registry promotion, log evidence, RSS membership, and
continuity. Add threshold-change coverage without code edits.

### Publish orchestration for generated surfaces

Current control path and defect:

* `.github/workflows/crawl-and-publish.yml:1038-1110` generates and promotes the
  weekly candidate
* `.github/workflows/crawl-and-publish.yml:1112-1131` hydrates only prior analyzed
  files before rollups
* `.github/workflows/crawl-and-publish.yml:1133-1219` backs up, switches to
  `publish`, restores, stages, and commits only weekly/rollup and selected data
  paths
* `.github/workflows/deploy-site.yml:85-98` hydrates only weekly/rollup and core
  data paths from `publish`
* `.github/workflows/generate-data-pages.yml:1-57` is the only scheduled
  Observatory generator and stops at an unmerged pull request
* No workflow invokes `taxonomy_registry.py`, `manage_topic_hubs.py`,
  `observatory_repos.py`, `export_observatory_dataset.py`, or
  `export_trend_explorer_data.py`

Use the weekly publish transaction as the authoritative cadence for all outputs
derived from weekly artifacts. Weekly refresh is a valid and stronger defined
cadence than the PRD's monthly example. Hydrate prior `publish` data before
generation, not after the current candidate is finalized.

Recommended transaction order:

1. Check out the default branch and hydrate prior `content/weekly`, `data/raw`,
   `data/analyzed`, `data/taxonomy`, `data/derived`, and lifecycle state from
   `publish`.
2. Download the current raw and analyzed artifacts over that history.
3. Generate the weekly candidate with known canonical topics.
4. Discover candidate topics, promote eligible hubs, and enrich historical and
   current weekly topic assignments before final content provenance is recorded.
5. Update the candidate content hash in the publish manifest, then run
   `promotion_guard.py` so the transaction record describes final bytes.
6. Refresh taxonomy registries after all topic assignments.
7. Generate rollups, repository pages, data pages, the downloadable dataset, and
   trend-explorer JSON in that order. Repository output depends on taxonomy for
   curated hub links; dataset and tool outputs depend only on hydrated raw data.
8. Run every generator's freshness check and focused tests before branch switch.
9. Back up all generated paths, switch to `publish` with the existing lease
   protection, restore them, and stage one atomic generated-content commit.
10. Upload generated artifacts for diagnosis and allow deployment to run only
    after the transaction succeeds.

Paths added to backup, restore, stage, artifact upload, and deployment hydration:

* `content/topics/`
* `content/repo/`
* `content/data/`
* `data/taxonomy/`
* `data/topic-hubs/`
* `data/derived/observatory/`
* `static/datasets/open-source-ai-github-projects-2026/`
* `static/tools/star-velocity-explorer.json`

Add `--check` support to `scripts/observatory_repos.py:543-559` and
`scripts/export_observatory_dataset.py:358-390`, matching
`scripts/generate_data_pages.py:472-496` and
`scripts/export_trend_explorer_data.py:180-201`. Update workflow-contract tests
in `tests/test_pipeline.py:329-380` to assert command order, hydrated paths,
backup/restore/stage coverage, flags, and deployment hydration.

Once this path is active, retire `.github/workflows/generate-data-pages.yml` or
convert it to a read-only scheduled freshness check. Keeping an independent
writer creates branch-race and publication-policy ambiguity.

### Durable repository identity, lifecycle, and retention

Current control path:

* `scripts/crawl.py:935-956` drops stable IDs, archive state, disabled state, and
  update timestamps even though GitHub search results contain them
* `scripts/crawl.py:1039-1073` validates the reduced repository schema
* `scripts/observatory_repos.py:167-245` keys histories by normalized full name
  and applies optional manual lifecycle overrides
* `scripts/observatory_repos.py:253-278` merges configured renames
* `scripts/observatory_repos.py:367-373` calculates a retention date
* `scripts/observatory_repos.py:465-470` deletes all generated pages before
  rewriting only currently eligible histories
* `scripts/observatory_repos.py:505-540` writes page output and a derived snapshot,
  not durable lifecycle state
* `tests/test_observatory_repos.py:166-220` proves only synthetic overrides
* `docs/design/data-observatory-model.md:339-387` lists the required identity and
  lifecycle fields

Extend the normal crawl record, without changing crawl topology, to retain
`id`, `node_id`, `archived`, `disabled`, `updated_at`, `pushed_at`, and canonical
URL fields. Update payload validation and crawl fixtures. Use GitHub ID as the
durable key and normalized `full_name` only as a backward-compatible fallback.

Create a versioned lifecycle ledger, recommended as
`data/derived/observatory/repository-lifecycle.json`, containing stable ID,
current and prior full names/slugs, first/last seen week, last successful URL,
status, status evidence, archive date, deletion confirmation date, and
`retained_until`. Merge the previous ledger before each generation.

Absence from weekly search is not deletion evidence. Mark archive/disabled from
positive API fields. Infer rename when the same stable ID changes full name.
Mark deletion only from an explicit bounded metadata result such as 404/410 for
a previously tracked repository, or a reviewed lifecycle override. If the
weekly crawl cannot add that bounded status check within scope, deletion remains
operator-confirmed but must still be persisted and enforced by the ledger.

Replace unconditional cleanup with retention-aware reconciliation:

* Generate active, archived, and renamed targets from merged history
* Generate aliases for every prior slug of the same stable ID
* Preserve deleted pages and historical observations while current date is not
  later than `retained_until`
* Delete only expired tombstones, with a logged reason
* Never drop a page merely because observations age out of the current raw
  loader or the recurrence threshold changes

Extend `tests/test_observatory_repos.py` with stable-ID rename, archive field,
confirmed deletion, missing-but-not-deleted, regeneration after source removal,
retention expiry, threshold change, and byte-stability cases.

### Topic highlights and repository-to-topic links

Topic highlight control is `layouts/topics/list.html:33-53`. It renders manually
authored `dataset_highlights`; it does not derive current highlights. Keep those
editorial bullets as durable context, but add a “Latest weekly signals” block
from the newest matching weekly pages. Use existing weekly parameters such as
summary, `top_repo`, `repos_featured`, `stars_tracked`, and week, with no hub
frontmatter edit. This makes highlights update as part of Hugo rendering after
topic assignment. Test a seeded hub and a dynamically created hub in
`tests/test_topic_hubs.py:281-304`.

Repository link control is:

* `scripts/observatory_repos.py:376-421` emits raw tag links but no curated hubs
* `layouts/repo/single.html:63-75` renders raw GitHub topic tags
* `data/taxonomy/topics.json:1-103` supplies curated aliases and promoted state
* `tests/test_observatory_repos.py:93-132` currently asserts that raw topics do
  not become curated topics

Preserve raw `/tags/` links, then derive an additional `topic_links` collection
only when a repository's recurring raw topic signals match aliases of a promoted
hub. Render a separate “Claracle topic hubs” section and assert every URL resolves.
Do not promote arbitrary raw GitHub topics as hubs. Update the existing test to
assert both behaviors: unknown raw topics remain tags, while `llm`, `mcp`,
`ai-agents`, or other registered aliases add curated hub links.

### SEO, schema, social dimensions, and rendered contracts

The active metadata controller is `layouts/partials/seo.html:1-166`, called from
`layouts/partials/head.html:10`. Older theme template partials are not active.

Implement these page semantics in the active partial:

* Weekly, monthly, and yearly pages: `Article` plus `BreadcrumbList`
* Topic terms: `CollectionPage` with an `ItemList` of recent weekly issues plus
  `BreadcrumbList`
* Data ranking pages: `Dataset` with an `ItemList` ranking as `mainEntity`, plus
  `BreadcrumbList`
* Repository pages: `WebPage` with `SoftwareSourceCode` as `mainEntity`, plus
  `BreadcrumbList`
* Tool and chart pages: `WebApplication` or `WebPage` according to page purpose,
  plus breadcrumbs where hierarchical

This removes data and repository pages from the generic article classifier at
`layouts/partials/seo.html:74-77`. Rich Results acceptance remains focused on
supported Article and Breadcrumb features; use Schema Markup Validator for
other valid Schema.org types.

At `layouts/partials/seo.html:40-58,84-94`, emit width and height for every social
image. Resolve dimensions from a local Hugo image resource where possible. Keep
configured fallback dimensions for the static default. Require explicit
`og_image_width` and `og_image_height` for remote or otherwise uninspectable
custom images, and fail the rendered contract when they are absent.

Expand `tests/test_rendered_seo_metadata.py:13-80` from title/description parsing
to a rendered-site contract that records:

* One correct absolute canonical per HTML page
* Complete Open Graph and Twitter fields, including positive dimensions
* Correct `og:type`, author fields, image alt, and creator by page class
* Parseable JSON-LD and required schema types/properties by representative page
  class
* Breadcrumb item positions and URLs
* Valid XML for `sitemap.xml`, root RSS, and every promoted topic RSS
* No news sitemap

Keep the site-wide unique title/description test. Add fixture pages for custom
local and remote social images so future custom images cannot bypass dimensions.
Run this suite in both `.github/workflows/ci.yml:49-106` and
`.github/workflows/site-preview.yml:90-111`.

### Weekly required-link presence

The generic checker at `scripts/check_internal_links.py:48-144` correctly rejects
broken emitted links, and CI runs it at `.github/workflows/ci.yml:49-106`. It
cannot detect a required link that was never emitted.

Add `tests/test_rendered_weekly_links.py` using a fresh Hugo destination. For each
source article:

* Sort weekly pages and require prior/next links except at legitimate endpoints
* Require a link for every explicit canonical `topics` entry
* Extract GitHub repository URLs from article Markdown, compute the established
  repo slug, and require links for targets with a generated page
* Assert no duplicate link groups and valid link text
* Run the generic checker against the same render

The rendering path is `layouts/weekly/single.html:1-39`,
`layouts/partials/article-footer.html:11-36`, and
`layouts/partials/article-related-links.html:1-81`. Keep
`tests/test_internal_link_checker.py:10-59` for target-resolution unit behavior.

### Consent-gated analytics events

Current analytics control is:

* `layouts/partials/analytics.html:1-10` exposes the configured measurement ID
* `layouts/partials/cookie-consent.html:44-126` disables GA4 until analytics
  consent and initializes `gtag` after consent
* `assets/js/star-velocity-explorer.js:92-147` handles tool filters and load
* `layouts/partials/visuals/observatory-chart.html:29-65` renders chart/embed
  content
* `content/state-of/open-source-ai-2026.md:11-17` contains dataset links

Add a small shared event API, recommended as
`assets/js/observatory-analytics.js`, which no-ops and does not queue telemetry
until analytics consent is active. Load it through the normal Hugo asset path and
let cookie-consent state enable or disable dispatch.

Implement the PRD events:

* `dataset_download`: delegated click handling for same-origin `/datasets/`
  assets; payload `dataset_id` and normalized path
* `tool_interaction`: explicit calls for explorer load, search, language/topic
  filter, and repository-open actions; payload `tool_id` and bounded action name,
  without query text or repository names
* `chart_embed_view`: standalone embed load after consent; payload `chart_id` and
  sanitized `document.referrer` host only

Add browser tests asserting no GA script, cookies, data-layer event, or network
request before consent; expected events after consent; bounded payloads; and no
raw search input. Off-site embed telemetry is best-effort because browsers may
block third-party consent cookies. Record that limitation in the runbook and do
not weaken consent to improve event counts.

### Rollout flags

`config/observatory.toml:18-24` currently enables dynamic creation contrary to
the PRD, and `config/observatory.toml:1-11` has no repository generation flag.

Add and enforce:

```toml
[repo_pages]
enabled = false

[topic_hubs.dynamic_creation]
enabled = false
```

The orchestrator may always invoke generators, but a disabled flag must produce
no new dynamic hubs or repository pages, must not delete existing durable pages,
and must log a disabled decision. Seed-topic backfill and rendering are not gated
by `dynamic_topic_creation`. Add config and workflow tests, validate with flags
off, enable each flag in a dedicated rollout commit after its acceptance gate,
and document rollback as disabling future creation rather than deleting pages.

### Performance, accessibility, and build timing gates

Existing but incomplete controls:

* `scripts/design/lighthouse-gates.mjs:12-65` enforces accessibility, best
  practices, and CLS but not Performance, and only covers legacy page classes
* `tests/visual/a11y-perf.spec.mjs:12-112` covers overflow and tap targets only on
  home/weekly/monthly/yearly pages
* `tests/visual/playwright.config.mjs:19-76` defines the browser matrix
* `.github/workflows/ci.yml:49-106` builds Hugo and Pagefind without timing or
  browser gates
* `docs/design/data-observatory-model.md:420-449` gives estimates but explicitly
  requires measured timing

Extend the page matrix with topic, data, repository, chart, and tool routes. Add
`performance: 0.90` to Lighthouse thresholds and output. Preserve the existing
stronger accessibility threshold of 0.95 and CLS limit 0.1. Add axe-core browser
tests for WCAG 2.1 A/AA violations, image alt, chart text alternatives, form
labels, keyboard operation, visible focus, and consent-modal behavior.

Create one CI job that builds once, runs Pagefind, serves `public/`, and executes
rendered SEO, weekly links, Lighthouse, axe, and responsive tests. Pin Node tools
instead of relying on floating `npx` versions. Upload machine-readable reports.

Instrument Hugo and Pagefind durations separately. First run the timing check in
report-only mode for at least three representative CI runs, record median and
p95, then set a reviewed regression budget. The repository does not contain an
actual baseline or an approved numeric budget, so a blocking build-time threshold
cannot be selected from current evidence alone.

### Podcaster smoke integration

Local contract coverage is strong in `tests/test_podcaster_handoff.py:133-284`.
The workflow at `.github/workflows/podcaster-handoff-smoke.yml:1-189` is manual,
checks out `main`, creates a synthetic manifest, and calls the downstream dry-run
endpoint. `tests/test_pipeline.py:503-535` only validates that workflow shape.

Convert the smoke body into a reusable `workflow_call` while retaining manual
dispatch. Invoke it for the promoted week after the generated publish transaction
and production deploy are successful. Pass the exact published article path,
URL, hash, and retained publish manifest or promotion record rather than creating
a synthetic manifest for release evidence. Keep secrets in a protected
environment, make smoke failure block relaunch acceptance, retain the Actions run
URL, and do not change `config/podcast.json` or `scripts/podcaster_handoff.py`.

Because the downstream repository and endpoint are external to this workspace,
the successful run itself remains external acceptance evidence.

### Security review, runbook, and design decisions

Technical controls already exist in `hugo.toml:154-156`,
`scripts/generate_content.py:13-67`,
`assets/js/star-velocity-explorer.js:39-79,126-132`, and
`docs/prompt-injection-guardrails.md:1-219`. They do not replace the required
Hermes review.

Create these planning and operational artifacts:

* `docs/review/data-observatory-relaunch/security-review.md`: threat boundaries,
  generated-content sanitization, candidate-title abuse, lifecycle metadata
  trust, dataset exposure, embed analytics/privacy, tool URL/DOM handling,
  secrets, findings, owner, and Hermes sign-off
* `docs/data-observatory-runbook.md`: weekly generation order, flags, output
  paths, freshness checks, lifecycle overrides and deletion confirmation,
  retention expiry, dashboards, GA4/GSC weekly review, failed-generation
  recovery, Podcaster smoke, rollback, escalation, and owner handoffs
* `docs/decisions/adr-star-velocity-explorer.md`: candidate tools considered,
  discoverability value, build effort, static-hosting fit, selected tool,
  alternatives, consequences, and status

The Star Velocity Explorer decision is recoverable from repository evidence:
same-origin static JSON, deterministic local exporter, no backend, no external
API, safe DOM construction, and existing shipped UI are documented in
`content/tools/star-velocity-explorer/index.md:1-21`,
`scripts/export_trend_explorer_data.py:130-201`, and
`tests/test_trend_explorer_tool.py:13-109`. The ADR should record, not reopen,
that selection unless the product owner has contrary issue evidence.

### Status and evidence reconciliation

The repository currently has no relaunch implementation plan or changes log.
Create them before remediation execution so each finding has an owner, status,
validation command, and evidence link:

* `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation.md`
* `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation.md`

After implementation and external acceptance:

* Update `docs/prds/claracle-data-observatory-relaunch.md:1-16,204-261` with
  actual phase status, closed/open risks, dates, flag state, measured build cost,
  resolved tool decision, and changelog
* Update `docs/brds/claracle-data-observatory-relaunch-brd.md:12-18,308-324`
  from “Ready for review” to the sponsor-approved lifecycle state
* Rewrite `docs/review/data-observatory-relaunch/README.md:1-42` so screenshots
  are visual evidence only; remove claims that screenshots prove metadata,
  schema, dynamic lifecycle, or final acceptance
* Update `docs/growth/ga4-gsc-baseline-2026-07-29.md:7-67` with actual dated
  status and values, or explicitly retain it as incomplete
* Replace empty-hub screenshots and add mobile, dark-theme, interaction,
  consent/network, and unobscured captures after all gates pass
* Add links to CI, Lighthouse, axe, schema, social debugger, GSC, GA4, security,
  and Podcaster evidence rather than transcribing unsupported pass claims

## Recommended Sequence and Parallelism

### Phase 0: Traceability and safety baseline

* Create the implementation plan and changes log
* Record current full pytest, Ruff, Hugo, Pagefind, link, and timing results
* Add rollout flags in the off state
* Confirm the branch transaction and deployment hydration design

This phase is serial because all later work depends on a stable evidence and
rollout model.

### Phase 1: Weekly topic through-line

* Implement backfill utility and backfill W21 through W31
* Implement candidate discovery artifact and promotion assignments
* Add dynamic highlights and topic end-to-end tests
* Refresh registries and verify nonempty hubs/RSS

Backfill and candidate-discovery implementation can proceed in parallel after
the shared topic assignment format is agreed. Integration and rendered tests are
serial afterward.

### Phase 2: Durable repository model

* Extend crawl record fields and validation
* Add lifecycle ledger and retention-aware reconciliation
* Add curated topic links
* Add repository generator freshness mode and lifecycle tests

Crawl schema work and ledger/generator work can proceed in parallel against an
agreed versioned fixture. Curated hub links can proceed independently once the
taxonomy registry format is stable.

### Phase 3: Publish orchestration

* Hydrate publish history before generation
* Order and invoke all generators
* Expand backup, restore, stage, artifact, and deployment paths
* Add workflow-contract and idempotence tests
* Retire or convert the monthly PR workflow

This phase must follow Phases 1 and 2 because it wires their final contracts.

### Phase 4: Rendered contracts and instrumentation

Run these workstreams in parallel:

* SEO/schema/social implementation and rendered SEO tests
* Weekly required-link presence tests
* Consent-gated analytics events and browser privacy tests
* Lighthouse, axe, responsive, and timing job implementation
* Podcaster reusable smoke workflow

Merge only after a combined production-equivalent Hugo build proves the jobs do
not duplicate or conflict with one another.

### Phase 5: Documentation and acceptance

Security review, runbook, and tool ADR can be drafted during Phase 4. Final
sign-off, external platform evidence, screenshots, status reconciliation, and
flag enablement follow successful automated gates. Enable dynamic topics and
repository generation separately so rollback scope remains small.

## Validation Plan

Focused Python validation after implementation:

```bash
python -m pytest -q \
  tests/test_generate_content_topics.py \
  tests/test_weekly_topic_backfill.py \
  tests/test_taxonomy_registry.py \
  tests/test_topic_hubs.py \
  tests/test_crawl.py \
  tests/test_observatory_repos.py \
  tests/test_generate_data_pages.py \
  tests/test_export_observatory_dataset.py \
  tests/test_trend_explorer_tool.py \
  tests/test_rendered_seo_metadata.py \
  tests/test_rendered_weekly_links.py \
  tests/test_internal_link_checker.py \
  tests/test_pipeline.py \
  tests/test_podcaster_handoff.py
```

Generator freshness and idempotence:

```bash
python scripts/backfill_weekly_topics.py --check
python scripts/discover_topic_candidates.py --check
python scripts/taxonomy_registry.py
python scripts/manage_topic_hubs.py --dry-run --current-date 2026-07-29
python scripts/observatory_repos.py --check
python scripts/generate_data_pages.py --check
python scripts/export_observatory_dataset.py --check
python scripts/export_trend_explorer_data.py --check
```

Production-equivalent static validation:

```bash
hugo --minify
npx "pagefind@1.5.2" --site public/
python scripts/check_internal_links.py public --base-url "https://claracle.com/"
python -m pytest -q tests/test_rendered_seo_metadata.py tests/test_rendered_weekly_links.py
```

Browser quality gates against a served production build:

```bash
npx playwright test --config tests/visual/playwright.config.mjs
npx playwright test --config tests/visual/playwright.config.mjs tests/visual/a11y-perf.spec.mjs tests/visual/observatory-a11y.spec.mjs
node scripts/design/lighthouse-gates.mjs --base http://127.0.0.1:8080
```

Repository gates:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest -q tests/
hugo --minify
checkov --directory . --framework github_actions dockerfile secrets --skip-path node_modules --skip-path .venv --compact --soft-fail
zizmor .github/workflows/
```

Workflow acceptance must additionally prove:

* Flags off produce no new dynamic hubs or repository pages and delete nothing
* A four-week candidate produces one logged hub and historical assignments
* A repository crossing the threshold appears in the same publish transaction
* A deleted repository survives regeneration after source observations are
  removed and disappears only after retention expiry
* Two identical runs are byte-stable and the second produces no commit
* Deployment renders the exact generated artifacts from `publish`
* The required Podcaster smoke succeeds against the downstream dry-run endpoint

## Repository-Resolvable Decisions

* Backfill is required for all 11 committed weekly issues. The acceptance wording
  and current empty hubs make W31-only remediation insufficient.
* Weekly generation should be the authoritative cadence for weekly-derived
  topic, repository, ranking, dataset, and tool outputs. It removes manual
  publication and branch-writer ambiguity.
* Raw GitHub topics remain tags. Only aliases of promoted editorial topics become
  repository-to-hub links.
* Topic highlights can be derived at Hugo render time from newest matching weekly
  pages; seed `dataset_highlights` remain durable editorial context.
* Topic schema is `CollectionPage`, data ranking schema is `Dataset` with
  `ItemList`, and repository schema is `WebPage` with `SoftwareSourceCode` as
  main entity. Generic `Article` is inappropriate for these surfaces.
* Analytics remains opt-in. No custom event may bypass the existing consent gate.
* Dynamic topic and repository creation flags default off until their separate
  validation gates pass. Disabling a flag never deletes durable pages.
* The Star Velocity Explorer remains the selected client-side tool. The missing
  task is to record the decision and alternatives, not repeat implementation.
* No Google News sitemap should be created.
* Existing FR-050, FR-051, FR-053, and FR-060 implementations should be retained
  and regression-tested rather than rebuilt.

## External or Manual Tasks

These tasks cannot be completed or truthfully accepted from repository code
alone:

* Product owner chooses whether any residual scheduled-PR publication is an
  intentional review control. The recommended unified weekly transaction removes
  this ambiguity for current Observatory outputs.
* Product owner approves Wave dates, launch state, rollout flag enablement, and
  the final BRD/PRD lifecycle status.
* GSC owner verifies the production property, submits the sitemap, records
  accepted status, indexed-page count, impressions, clicks, and top queries.
* GA4 owner accepts consent in production, confirms Realtime receipt, verifies
  rejection sends no analytics, and records dated baseline values.
* Reviewer runs Facebook Sharing Debugger and current X/Twitter preview tooling
  for homepage and representative article, then retains URLs or screenshots.
* Reviewer runs Google Rich Results Test for Article and Breadcrumb and Schema
  Markup Validator for topic/data/repository entities.
* Operator fetches production sitemap, root feed, and every topic feed and retains
  HTTP/XML validation evidence.
* Hermes performs and signs the relaunch-specific security review.
* The Podcaster protected-environment smoke runs against the downstream service,
  and its successful Actions URL is retained.
* Accessibility reviewer examines any axe exceptions, keyboard interaction,
  focus behavior, contrast, chart alternatives, mobile, and dark theme.
* Product/technical owner approves the blocking Hugo and Pagefind timing budget
  after measured baseline runs.
* Human reviewer replaces screenshots and approves the final visual evidence
  without treating screenshots as SEO, schema, network, or lifecycle proof.

## Remaining Gaps and Clarifying Questions

Research answered all code-location and implementation-shape questions. These
delivery decisions still require owner input:

1. What blocking CI budgets should apply to Hugo and Pagefind after the required
   three-run timing baseline? The repository has estimates but no approved value.
2. May the normal weekly crawl perform a bounded metadata lookup for previously
   tracked repositories to confirm 301/404/410 lifecycle transitions, or must
   deletion remain an operator-confirmed override? Absence from search results is
   not safe deletion evidence.
3. Should the Podcaster smoke block every weekly deployment or only relaunch and
   contract-changing releases? NFR-002 requires retained release evidence, but
   the desired steady-state frequency is not specified.
4. Are issue or PR artifacts outside the repository the authoritative source for
   the Star Velocity Explorer comparison? If so, preserve that evidence in the
   ADR rather than replacing it.
5. Who is the named operational owner for weekly GA4/GSC review and generation
   failure escalation after the role-level assignments are converted into the
   runbook?
