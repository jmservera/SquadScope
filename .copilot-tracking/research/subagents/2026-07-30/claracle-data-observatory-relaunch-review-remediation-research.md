---
title: Claracle Data Observatory Relaunch Review Remediation Research
description: Implementation-ready research for remediation of PR 623 review findings
ms.date: 2026-07-30
ms.topic: reference
---
<!-- markdownlint-disable-file -->

## Research Status

Complete as of 2026-07-30. No implementation files were modified.

## Research Questions

1. Define safe lifecycle semantics for date-omitted deletion overrides, deterministic history seeding while repository pages are disabled, and rendered idempotence acceptance.
2. Define Podcaster remediation for the invalid workflow heredoc, exact promoted bytes above 50,000 articles, executable embedded-logic tests, and protected-run dependencies.
3. Define blocking analytics CI, real browser behavior checks, likely causes of hosted run 30502305707 failures, and preserved Lighthouse sequencing.
4. Define candidate-title sanitization and tests, Zizmor high and medium remediation ownership, and hosted versus local scan reconciliation.
5. Define required Phase 4 runtime evidence, isolated two-run generator proof, three-run timing evidence, traceability updates, visuals, and external acceptance.
6. Resolve the disabled topic decision, external dataset path formatting, and embed limitation runbook placement.
7. Separate repository implementation from external Actions, platform, reviewer, and sponsor work, then recommend phase ordering and parallel execution.
8. Identify why the visible breadcrumb renders as a numbered list, select an existing construct to reuse, separate visible navigation from JSON-LD, and define the cheapest rendered regression.

## Source Inventory

Primary review evidence:

* `.copilot-tracking/reviews/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-review.md:1-186`
* `.copilot-tracking/reviews/quality/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-quality.md:1-91`
* `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-001-validation.md:1-174`
* `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-002-validation.md:1-139`
* `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-003-validation.md:1-162`
* `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-004-validation.md:1-170`
* `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-005-validation.md:1-154`
* `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-006-validation.md:1-139`
* `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-007-validation.md:1-197`
* `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-008-validation.md:1-124`
* `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-009-validation.md:1-179`
* `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-010-validation.md:1-170`

Original planning evidence:

* `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md`
* `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:1-522`
* `.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:1-68`
* `.copilot-tracking/research/subagents/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:1-700`
* `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:1-230`
* `.copilot-tracking/plans/logs/2026-07-29/claracle-data-observatory-relaunch-remediation-log.md:1-92`

The current source paths and executable checks are cited under each finding. A
read-only corpus inspection found 22 source files, 4,602 repository observations,
zero observations with a GitHub `id`, 2,242 name-fallback histories, 263 qualified
histories, 263 generated repository pages, and 263 derived repository entries.

The repository-wide Zizmor verification used version 1.27.0 and returned exit code
14 with one low, twelve medium, and one high finding. Hosted CI does not run the
same scope.

Breadcrumb research also inspected pinned PaperMod commit
`154d006e0182dfc7da38008323976b02e6bfab4a`. Its
`layouts/_partials/breadcrumbs.html` and `assets/css/common/post-single.css` are
available in the upstream tree even though the local submodule is not initialized.

## Findings

### Lifecycle retention semantics

Controlling paths:

* `scripts/observatory_repos.py:153-174` loads the flag, threshold, retention,
	overrides, and ledger path
* `scripts/observatory_repos.py:280-479` merges ledger and checked-in observations,
	migrates a `name:` key when a future stable ID appears, and applies reviewed
	overrides
* `scripts/observatory_repos.py:704-727` serializes every history into the ledger
* `scripts/observatory_repos.py:729-750` derives deletion confirmation and expiry
* `scripts/observatory_repos.py:852-865` exits before loading the ledger when page
	creation is disabled
* `tests/test_observatory_repos.py:224-278` currently accepts a date-omitted
	deletion based on the last-seen week
* `tests/test_observatory_repos.py:352-390` covers the safe explicit-date path
* `data/derived/observatory/repository-lifecycle.json:1-4` is empty
* `config/observatory.toml:1-12` keeps creation disabled and defines the override
	boundary

The safest date-omitted behavior is fail closed. A reviewed override with
`status = "deleted"` must include a valid ISO `deletion_confirmed_at`. The
generator must reject a missing, invalid, or future confirmation date before any
page, ledger, taxonomy, or derived write. `retained_until` must remain derived as
`add_years(deletion_confirmed_at, retention_years)` and must not accept an
operator-supplied earlier deadline. Using `last_seen_week` violates the minimum;
using `date.today()` makes checked-in generation nondeterministic and hides the
review event that establishes deletion.

Recommended repository changes:

* Validate lifecycle overrides in or immediately after `load_config()` at
	`scripts/observatory_repos.py:153-174`
* Remove the fallback at `scripts/observatory_repos.py:738-744`
* Preserve `last_seen_week` only as page provenance, never as confirmation
* Update the runbook override example at `docs/data-observatory-runbook.md:94-114`
	to state that deletion confirmation is mandatory

Required tests in `tests/test_observatory_repos.py`:

* Last seen in 2024, reviewed deletion in 2026, and retention through the same
	date in 2029
* Missing confirmation date fails without modifying pre-existing pages or ledger
* Invalid and future dates fail closed
* A configured `retained_until` cannot shorten the derived deadline
* The explicit-date boundary retains on the deadline and removes only when
	`as_of > retained_until`

### Deterministic lifecycle seed while rollout is disabled

The existing gate at `scripts/observatory_repos.py:856-862` correctly prevents
page mutation, but it also prevents migration. Do not weaken that gate. Add an
explicit ledger-only migration operation, preferably `--seed-lifecycle`, whose
contract is separate from normal generation:

1. Require `repo_pages.enabled = false` unless an explicit temporary test config
	 is supplied.
2. Load the prior ledger and checked-in raw/archive observations through the
	 existing `raw_week_files()` and `load_repository_histories()` paths at
	 `scripts/observatory_repos.py:176-479`.
3. Mark histories qualified by the configured threshold, but do not reconcile
	 expiry, delete a history, generate a page, refresh taxonomy, or rewrite
	 `data/derived/observatory/repositories.json`.
4. Verify the qualified names and slugs match the 263 existing generated pages
	 and derived entries before writing the seed. Treat any mismatch as a migration
	 failure requiring review.
5. Write only the deterministic ledger payload from
	 `scripts/observatory_repos.py:704-727`, using atomic replacement.
6. Report counts for name-fallback keys, stable-ID keys, qualified histories,
	 existing pages, and mismatches.

The current seed must contain 2,242 deterministic `name:<normalized-full-name>`
keys because none of the 4,602 historical observations has a GitHub ID. This is
not a reason to invent IDs or query GitHub during migration. The existing path at
`scripts/observatory_repos.py:408-417` can migrate a fallback key when a future
captured observation supplies a stable ID. Add a collision test proving that one
future ID absorbs the matching fallback history without losing prior slugs,
observations, qualification, or lifecycle state.

Seed acceptance:

* Run the migration twice with a frozen corpus; the second run must produce the
	same ledger bytes and no diff
* Assert all 2,242 histories and all 263 qualified histories are represented
* Assert all 263 current page files and `repositories.json` remain byte-identical
* In an isolated copy with a temporary enabled config, run normal generation
	twice and require no second-run diff
* Run Hugo and assert the canonical page, prior-name alias fixture, lifecycle
	notice, raw tag links, and promoted topic links resolve
* Keep the committed production flag false throughout migration and rendered
	acceptance

### Podcaster exact-release path

Controlling paths:

* `scripts/podcaster_handoff.py:17-23` defines the 50,000-character normal limit
* `scripts/podcaster_handoff.py:524-555` truncates article content
* `scripts/podcaster_handoff.py:654-705` builds the normal payload and attaches the
	full manifest hash
* `.github/workflows/podcaster-handoff-smoke.yml:69-171` validates the promotion
	record and checked-out article bytes
* `.github/workflows/podcaster-handoff-smoke.yml:186-230` contains the malformed
	second heredoc and invokes the normal payload builder
* `.github/workflows/deploy-site.yml:122-210` resolves the promoted release and
	calls the smoke only after build and deployment
* `tests/test_pipeline.py:656-711` checks strings rather than executing workflow
	programs
* `tests/test_podcaster_handoff.py:288-318` proves exact bytes only below the
	limit
* `tests/test_podcaster_handoff.py:1072-1092` intentionally preserves normal
	truncation

Preserve the normal shared payload contract. Add an opt-in exact-release mode to
the shared builder and CLI, such as `exact_article_content=False` and
`--exact-article-content`. The default remains truncated and every existing
normal handoff test must remain unchanged. The protected release smoke alone sets
the option. In exact mode, read the complete UTF-8 article, require its round-trip
bytes to equal the promoted file bytes, and require `article_sha256` to match
those bytes before any HTTP request. The payload field names remain unchanged.

This approach changes the shared implementation but not the normal payload shape
or default size behavior. It is safer than replacing `article_content` in the
workflow after `build_payload()`, which would let CLI and workflow behavior
diverge. It also avoids raising the normal 50,000-character ceiling for every
Podcaster call.

Repair the invalid indentation immediately. The stronger maintainable change is
to extract both embedded validators into a checked-in Python entry point or
testable functions, then make the workflow invoke them. If the heredocs remain,
tests must parse the YAML block scalar, extract each heredoc, compile it, and
execute it in a temporary repository.

Executable test matrix:

* Valid promotion transaction and valid publish-eligibility manifest
* Path traversal, missing article, wrong week, wrong path, wrong article hash,
	wrong source-manifest hash, and invalid transaction ID
* Short normal payload remains unchanged
* Normal payload above 50,000 characters remains truncated
* Exact-release payload above 50,000 characters contains the full promoted UTF-8
	bytes and matching hash
* Payload-content mismatch fails before `post_handoff()`; mock the network call
	and assert it was not called
* Missing required payload fields and empty `source_artifacts` fail before
	network access
* The workflow contract test asserts the CLI passes the exact-release option

Protected execution still depends on the `podcaster-release-smoke` environment,
`PODCASTER_ENDPOINT`, `PODCASTER_API_KEY`, GitHub Pages deployment approval, the
retained `publish` promotion record, and downstream acceptance of a body above
50,000 characters. The downstream body-size/schema limit belongs to
SquadScope-Podcaster and must be verified before the protected run. No successful
run can be claimed from repository tests.

### Analytics and browser acceptance

Controlling paths:

* `.github/workflows/ci.yml:58-121` pins browser dependencies but installs only
	Chromium
* `.github/workflows/ci.yml:123-190` builds once, runs Playwright before
	Lighthouse, and uploads reports
* `.github/workflows/ci.yml:171-172` omits the dedicated analytics specification
* `tests/visual/playwright.config.mjs:53-87` uses Desktop Chrome for desktop and
	the iPhone 13 device profile for mobile
* `tests/visual/observatory-analytics.spec.mjs:10-116` replaces `gtag` and calls
	the adapter directly
* `layouts/partials/analytics.html:1-10` emits the configured measurement ID and
	starts GA disabled
* `layouts/partials/cookie-consent.html:44-136` owns actual accept, persisted
	state, withdrawal, GA script loading, and analytics disablement
* `data/cookieconsent.json:1-66` defines the UI and `_ga` auto-clear policy
* `assets/js/observatory-analytics.js:4-144` bounds events and no-ops without
	consent

Add `tests/visual/observatory-analytics.spec.mjs` to the existing blocking
Playwright command. Preserve sequencing: browser suites remain before Lighthouse,
the report upload remains `if: always()`, and Lighthouse executes only after all
privacy, axe, interaction, and responsive checks pass. This keeps one production
build and prevents a privacy failure from being hidden by a later performance
result.

Build CI with a non-secret test measurement ID, for example through
`HUGO_PARAMS_GA_MEASUREMENT_ID`, so the actual GA loader path is present. Browser
tests should intercept and abort or fulfill Google endpoints while recording
requests. They must use Cookie Consent buttons and preferences rather than
calling `ObservatoryAnalytics.setConsent()` directly.

Required browser scenarios:

* Fresh context: no GA script element, Google request, `_ga` cookie, custom event,
	or queued pre-consent telemetry
* Reject all: consent cookie persists, analytics remains disabled, and reload
	sends nothing
* Accept all: GA script request occurs, bounded events enter the real `gtag`
	queue, and no repository name or search term enters a payload
* Reload after acceptance: the accepted category restores through Cookie Consent
	and GA initializes once
* Withdrawal through preferences: `ga-disable-<id>` becomes true, a seeded `_ga`
	test cookie is removed by the configured auto-clear rule, and future custom
	events and requests stop
* Dataset, tool, and standalone chart events use the existing UI and delegated
	handlers rather than direct adapter calls

The strongest source-supported cause of hosted run `30502305707`, job
`90744394455`, is browser-install mismatch. The iPhone 13 profile at
`tests/visual/playwright.config.mjs:73-86` selects WebKit, while CI installs only
Chromium at `.github/workflows/ci.yml:121`. The Phase 2 validator independently
reported WebKit attempts. The smallest deterministic remediation is to make all
four blocking projects Chromium-backed, using a Chromium mobile device profile
or explicit mobile viewport/touch settings. If Safari compatibility is a release
requirement, install WebKit and keep it as a separately named project instead.

Artifact `8744139176` is still required to distinguish launch errors from any
real axe, tap-target, overflow, or focus failures. Public source evidence cannot
identify every failed assertion. After the browser matrix is corrected, rerun
the same revision and require both Playwright and all Lighthouse route summaries
to pass.

### Visible breadcrumb navigation

Controlling paths:

* `layouts/partials/breadcrumbs.html:1-14` builds one repository-owned visible
	`nav.breadcrumbs` containing an ordered list, linked ancestors, and a final
	`span[aria-current="page"]`
* `layouts/partials/breadcrumbs.html:15-22` also emits a `BreadcrumbList` script
	immediately after the visible navigation
* `layouts/partials/seo.html:154-168`, called from
	`layouts/partials/head.html:11`, independently emits the canonical
	`BreadcrumbList` in the document head
* `assets/css/common/post-single.css:19-39` carries PaperMod's class-level
	breadcrumb styling but applies flex layout to the `nav`, not its child `ol`
* `assets/css/core/reset.css:80-100` resets `ul` padding and `ul` margins only;
	it does not reset an ordered list
* `assets/css/extended/squadscope.css:400-413` only removes breadcrumb margin
	inside article headers and does not style the list
* `layouts/_default/list.html:4`, `layouts/_default/single.html:6`,
	`layouts/_default/taxonomy.html:3`, `layouts/_default/terms.html:3`,
	`layouts/charts/list.html:3`, `layouts/data/list.html:3`,
	`layouts/data/single.html:6`, `layouts/repo/list.html:3`,
	`layouts/repo/single.html:6`, `layouts/search/list.html:3`,
	`layouts/search/search.html:3`, `layouts/tools/list.html:6`,
	`layouts/tools/single.html:6`, `layouts/topics/list.html:4`,
	`layouts/topics/terms.html:6`, `layouts/weekly/list.html:4`, and
	`layouts/weekly/single.html:6` each invoke the same visible partial once
* `tests/test_rendered_seo_metadata.py:59-78,154-218` parses JSON-LD and checks
	positions, but accepts multiple `BreadcrumbList` documents and does not parse
	the visible navigation
* `tests/visual/observatory-a11y.spec.mjs:4-38` covers axe and page overflow on
	Observatory routes but has no breadcrumb-specific semantic or computed-style
	assertion

The visible numbering is the browser's default `<ol>` marker. The parent
`.breadcrumbs` element is flex, but its only flex child is the ordered list. No
rule removes `list-style`, the list retains user-agent padding and margin, and its
items remain block list items. A representative rendered data page contains
`Home`, `Data`, and the current title in that unstyled list. It also contains two
JSON-LD `BreadcrumbList` scripts, one from `seo.html` and one from the visible
partial.

The pinned PaperMod partial at
<https://github.com/adityatelange/hugo-PaperMod/blob/154d006e0182dfc7da38008323976b02e6bfab4a/layouts/_partials/breadcrumbs.html>
provides the existing visual construct: `.breadcrumbs` with chevron-right SVGs
between inline links. Its CSS is the source of the repository's current
`.breadcrumbs` flex, wrapping, link-size, and SVG-size rules. Do not replace the
local partial with that theme partial. The theme version is gated by
`ShowBreadCrumbs`, has no ordered-list semantics, omits current-page text and
`aria-current`, adds a redundant `role="navigation"`, and does not emit JSON-LD.

Selected reuse approach:

* Keep `layouts/partials/breadcrumbs.html` as the sole visible breadcrumb
	component and preserve its stronger `nav[aria-label="Breadcrumb"]`, `ol`, and
	terminal `aria-current="page"` semantics
* Reuse PaperMod's established `.breadcrumbs` class and chevron visual language,
	but put each separator inside the following `li` and mark its SVG or separator
	span `aria-hidden="true"`; do not add separators as ordered-list children or
	accessible text
* Move flex, wrapping, gap, zero margin, zero padding, and `list-style: none` to
	`.breadcrumbs ol`; make each `li` inline-flex so its separator and label remain
	together
* Let long current-page labels wrap with `min-width: 0` and
	`overflow-wrap: anywhere`; do not truncate the accessible current title or add
	horizontal breadcrumb scrolling on mobile
* Keep ancestors as links and render the current page as non-link text. Use the
	existing `.Ancestors.Reverse` Hugo construct, already used by `seo.html` and
	PaperMod, when hierarchy beyond section depth is required
* Remove only the JSON-LD block at `layouts/partials/breadcrumbs.html:15-22`.
	Keep structured-data ownership in `layouts/partials/seo.html:154-168`, so
	visible navigation and machine-readable schema coexist without one renderer
	producing the other
* Do not add breadcrumb calls to shared base layouts. The 17 current layout call
	sites already render one visible partial per applicable page; base-level
	insertion would create duplicate UI

Required tests:

* Extend `tests/test_rendered_seo_metadata.py` with a small visible-breadcrumb
	parser and a representative nested data-page assertion: exactly one
	`nav.breadcrumbs` with the accessible name `Breadcrumb`, exactly one direct
	`ol`, at least two `li` items, linked ancestors in order, one terminal non-link
	`[aria-current="page"]`, and one decorative separator per boundary
* Tighten the site-wide schema contract at
	`tests/test_rendered_seo_metadata.py:203-218` from at least one to exactly one
	`BreadcrumbList` on each non-home page, while retaining contiguous positions
	and absolute URL checks
* Add the cheapest visual regression to
	`tests/visual/observatory-a11y.spec.mjs`: on one nested data route in
	`desktop-light` and `mobile-light`, inspect computed style and require the
	ordered list to have `list-style-type: none`, flex wrapping, no horizontal
	overflow, exactly one visible breadcrumb nav, and the final item to remain
	visible. This two-project computed-style check directly fails on the current
	ugly numbered list without adding screenshots or a new browser suite
* Preserve the existing axe checks. They validate the navigation landmark and
	list structure, while the focused rendered and computed-style assertions cover
	semantics, duplicate UI/schema, separators, and mobile presentation that axe
	does not distinguish

### Candidate-title sanitization

Controlling paths:

* `scripts/manage_topic_hubs.py:111-127` performs a narrow phrase and length
	filter
* `scripts/discover_topic_candidates.py:92-121` stores the accepted title in
	evidence
* `scripts/manage_topic_hubs.py:211-234` interpolates candidate text into YAML
	and Markdown manually
* `scripts/sanitize_repo_content.py:15-39,68-105` owns the standard boundary,
	injection phrase, and length sanitizer
* `tests/test_topic_hubs.py:141-173,198-377` covers normal discovery and promotion
* `docs/review/data-observatory-relaunch/security-review.md:45-56,140-169`
	records SEC-01 as rollout-blocking

Make `safe_candidate_title()` call `sanitize_text(value, max_length=80,
label="candidate title")`, then apply title-specific rules to the sanitized
value. Reject, rather than silently promote, any value containing control
characters, multiline text, escaped boundary markers, or a sanitizer-detected
injection phrase. A display title is an identifier and page heading, so suspicious
text should not be shortened into an eligible new title.

Replace handwritten YAML interpolation in `render_hub()` with `yaml.safe_dump()`
for a structured frontmatter dictionary. Escape candidate text for Markdown prose
or avoid placing untrusted text in generated prose beyond the sanitized title.
Keep `topic_hubs.dynamic_creation.enabled = false` until Hermes accepts the
adversarial suite and generated diff.

Add focused cases for quotes, colons, YAML document markers, newlines, tabs,
control characters, Markdown links/images, HTML, boundary markers, every standard
injection phrase class, Unicode-only titles, length boundaries, and a benign title
containing punctuation. Assert rejected inputs create no candidate, registry
entry, log, weekly assignment, directory, or page. Parse every accepted generated
frontmatter document with YAML and run Hugo against representative accepted
titles.

### Zizmor ownership and reconciliation

Current repository-wide Zizmor 1.27.0 findings:

* High `excessive-permissions`: `.github/workflows/squad-promote.yml:14-15`
* Medium `artipacked`: `.github/workflows/squad-ci.yml:17-18`
* Medium `artipacked`: `.github/workflows/squad-docs.yml:20-21`
* Medium `artipacked`: `.github/workflows/squad-heartbeat.yml:27-28`
* Medium `artipacked`: `.github/workflows/squad-insider-release.yml:14-15`
* Medium `artipacked`: `.github/workflows/squad-issue-assign.yml:16-17`
* Medium `artipacked`: `.github/workflows/squad-label-enforce.yml:14-15`
* Medium `artipacked`: `.github/workflows/squad-preview.yml:14-15`
* Medium `artipacked`: `.github/workflows/squad-promote.yml:21-22,73-74`
* Medium `artipacked`: `.github/workflows/squad-release.yml:14-15`
* Medium `artipacked`: `.github/workflows/squad-triage.yml:15-16`
* Medium `artipacked`: `.github/workflows/sync-squad-labels.yml:17-18`

The hosted/local difference is intentional scope drift:
`.github/workflows/security-scanning.yml:102-115` excludes `squad-*.yml` and
`sync-squad-labels.yml`, while Phase 10 runs `zizmor .github/workflows/`.
`docs/devsecops/zizmor-baseline.md:22-47,73-82` documents the narrower hosted
baseline. Hosted success therefore does not satisfy the plan's repository-wide
gate.

Smallest safe remediation:

* Move workflow-level `contents: write` in `squad-promote.yml` to only the two
	jobs that push, leaving the workflow default at `contents: read`
* Add `persist-credentials: false` to checkout steps that never push
* For the promote and release jobs that push, also disable persisted checkout
	credentials and supply short-lived authentication only to the specific push
	command; remove it immediately afterward
* Regenerate or upstream the same changes through the Squad workflow source so a
	later Squad refresh cannot reintroduce them
* Change hosted Zizmor input collection to scan all committed workflows, or
	explicitly change the Phase 10 contract and document an approved generated-file
	exception. A green narrow scan must not be described as repository-wide
* Pin the same Zizmor version/persona locally and in Actions, then update the
	baseline with exact scope, version, date, and finding count

URL owns repository guardrail and workflow changes. The Squad generator owner
owns the durable upstream fix. Hermes reviews token lifetime and push
authentication. The high finding should not be suppressed. Medium suppressions
are appropriate only for a reviewed push job whose credentials cannot be
narrowed further, with a path-specific rationale.

### Operational runtime evidence

Phase 4 source wiring is substantial:

* `.github/workflows/crawl-and-publish.yml:1051-1080` hydrates prior generated
	state
* `.github/workflows/crawl-and-publish.yml:1100-1207` runs and freshness-checks
	generators in dependency order
* `.github/workflows/crawl-and-publish.yml:1210-1307` archives, restores, stages,
	commits once, and pushes with a lease
* `.github/workflows/crawl-and-publish.yml:1309-1325` retains generated artifacts
* `.github/workflows/deploy-site.yml:89-116` hydrates the matching publish paths
* `tests/test_pipeline.py:432-547` verifies workflow shape but cannot prove remote
	branch behavior

Required Actions scenarios must run against a controlled acceptance branch or
repository with recorded pre-run `publish` SHA:

1. Normal success: retain run URL, input revision, promotion reference, generated
	 commit SHA, changed-path list, and proof that exactly one generated commit was
	 added.
2. Controlled generator failure before the commit step: retain the failed step
	 and prove the remote `publish` SHA is unchanged.
3. Identical rerun with the same hydrated inputs: prove the commit step reports
	 no generated changes and the remote SHA remains unchanged.
4. Deploy from the successful run: retain deploy URL and compare every hydrated
	 generated path to the accepted publish tree.

Do not add a production bypass or weaken promotion guards to manufacture these
scenarios. A dedicated acceptance repository, branch, or temporary workflow
revision with a deterministic pre-commit failure fixture is safer than a hidden
runtime flag in the production transaction.

### Literal all-generator two-run proof

Use a clean detached worktree at the reviewed commit, install pinned dependencies,
and copy only the required retained input artifacts. Freeze the candidate current
date through the existing `--current-date` option. Use a temporary Observatory
config when enabled topic and repository paths must be proven; do not change the
committed rollout flags.

Run the same dependency order represented at
`.github/workflows/crawl-and-publish.yml:1100-1207`: weekly content fixture,
candidate discovery, topic assignment/promotion, final rehash and guard, taxonomy,
rollups, repository pages, data pages, dataset export, and trend explorer export.
Capture a manifest of every generated path and SHA-256 after pass one. Run the
complete sequence again, then require the second manifest to match and
`git diff --exit-code` to be clean for all generated paths. Retain the command
log, commit SHA, config hash, tool versions, first and second manifests, and diff
result as one artifact.

The proof should include the lifecycle ledger seed mode and both flags-off
non-mutation checks. A separate enabled fixture should prove one four-week topic
promotion, one threshold-crossing repository, rename, archive, confirmed
deletion, source absence, retention boundary, and expiry.

### Timing, traceability, visuals, and acceptance

Timing instrumentation at `.github/workflows/ci.yml:123-151` is correctly
report-only. `docs/design/data-observatory-model.md:413-433` contains one local
sample and explicitly leaves the baseline open. Collect two more successful,
comparable Production site artifacts after browser remediation, at stable page
volume and the same tool versions. Record each commit and runner context,
calculate separate Hugo and Pagefind median and p95 values, propose separate
budgets, and obtain owner approval before changing `blocking_threshold_ms`.

Update the traceability log at
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:13-37,121-224`:

* Replace descriptions with exact paths and immutable run, job, artifact, commit,
	or external evidence identifiers
* Correct Phase 3 and Phase 8 completion claims
* Record run `30502305707`, job `90744394455`, artifact `8744139176`, the failed
	browser gate, and skipped Lighthouse state
* Resolve the stale dataset-drift note with a dated current result
* Record the Zizmor version, full input scope, exit code, and disposition per
	finding
* Link the two-run manifests, Phase 4 run matrix, three timing artifacts, and
	protected Podcaster run

Visual acceptance remains governed by
`docs/review/data-observatory-relaunch/screenshots/README.md:14-69`. Replace the
historical captures only after the accepted revision has populated content and
passing browser gates. Record revision, browser, viewport, theme, consent state,
interaction state, and source week. Capture desktop light, mobile light, desktop
dark, interactions, empty/loading/error states, and unobscured content. Visuals
cannot substitute for network, schema, lifecycle, accessibility, or protected-run
evidence.

The external acceptance matrix at
`docs/review/data-observatory-relaunch/README.md:48-63` correctly remains pending.
Repository work can create evidence slots and automation, but only named actors
can supply GA4 Realtime, GSC, social and schema debugger, production response,
screen-reader, Hermes, URL, Podcaster, and sponsor conclusions.

### Minor defects

Disabled topic decision:

* `scripts/manage_topic_hubs.py:387-394` silently returns for disabled and dry-run
	cases
* `tests/test_topic_hubs.py:443-507` verifies non-mutation but not output
* Emit a stable machine-readable decision before return, distinguishing
	`disabled` from `dry-run`, and assert exact output plus unchanged files

External dataset path formatting:

* `scripts/export_observatory_dataset.py:380-409` correctly computes stale files
* `scripts/export_observatory_dataset.py:405-409` assumes every output is below
	`PROJECT_ROOT`
* Add a display helper that returns a repository-relative path when possible and
	otherwise returns the supplied or resolved external path without raising
* Add a stale external temporary-directory case to
	`tests/test_export_observatory_dataset.py:11-69` and invoke `main()` to verify
	exit code, stderr, and non-mutation

Embed limitation placement:

* `docs/review/data-observatory-relaunch/security-review.md:93-102,140-153`
	documents the unresolved cross-origin consent and referrer boundary
* Add the operational limitation under routine dashboards and evidence at
	`docs/data-observatory-runbook.md:129-145`, including the chosen SEC-02 policy,
	expected network behavior, ownership, and escalation
* Keep the security review as the disposition record and the runbook as the
	operator-facing behavior; do not duplicate sign-off claims

## Responsibility and Dependencies

| Work item | Repository implementation owner | Executable repository evidence | External dependency or acceptance owner |
| --- | --- | --- | --- |
| Deletion confirmation and ledger seed | Bender | Lifecycle unit tests, seed counts, two-run byte comparison, rendered fixture | Hermes disposition of override policy |
| Podcaster exact-release mode | URL with Podcaster maintainers | Short, normal over-limit, exact over-limit, mismatch, and no-network tests | Protected environment and downstream size-contract acceptance |
| Analytics privacy gate | Amy and Fry | Cookie Consent browser suite in blocking CI | Hermes privacy review and jmservera GA4 Realtime observation |
| Browser and Lighthouse gate | Fry and Amy | Passing Playwright and Lighthouse reports from one revision | Authenticated artifact access and human accessibility review |
| Visible breadcrumb navigation | Amy and Fry | Rendered semantic/schema contract plus desktop and mobile computed-style check | Human visual and screen-reader acceptance in the existing accessibility review |
| Candidate-title security | Farnsworth and Hermes | Adversarial sanitizer, YAML parse, non-mutation, and Hugo tests | Hermes SEC-01 approval |
| Zizmor findings | URL | Full-scope pinned scan with no unreviewed high or medium findings | Squad generator owner for durable generated-workflow fixes; Hermes token review |
| Phase 4 atomic runtime | URL and Bender | Workflow contracts and isolated generated manifests | GitHub Actions remote branch, lease, deploy, and retained run evidence |
| Timing baseline | Fry and URL | Three comparable timing JSON artifacts and computed statistics | jmservera budget approval |
| Visual evidence | Amy and Fry | Revision-bound capture matrix | Accessibility reviewer and sponsor acceptance |
| Platform evidence | jmservera | Repository wiring and bounded evidence index | GA4, GSC, debugger, production, and sponsor access |

Implementation dependencies are Python 3.12 and repository requirements, Hugo
Extended 0.161.1, Pagefind 1.5.2, Node 24, Playwright 1.54.2, axe-playwright
4.10.2, Lighthouse 12.8.2, and a pinned Zizmor version shared by local and hosted
scans. Tests that mutate generated state require an isolated worktree or temporary
workspace. Protected smoke and platform acceptance additionally require GitHub
environment variables, masked secrets, reviewer approvals, network access, and a
designated deployed promotion record.

## Recommended Phase Order

1. Correct repository-critical semantics serially: deletion confirmation,
	lifecycle seed mode, exact-release payload mode, and malformed Podcaster
	verifier. Keep both rollout flags false.
2. Run focused lifecycle and Podcaster tests, then create the deterministic seed
	artifact and isolated rendered lifecycle proof.
3. In parallel, remediate candidate sanitization, disabled-topic observability,
	external dataset path formatting, and Zizmor workflow permissions and checkout
	credentials. URL and Hermes review the security-sensitive branches.
4. In parallel with step 3, fix the Chromium/WebKit matrix, add the analytics spec
	to blocking CI, and replace adapter-direct tests with Cookie Consent lifecycle
	tests. Repair visible breadcrumb styling and duplicate schema in the same
	frontend slice. Preserve browser-before-Lighthouse sequencing.
5. Merge the repository fixes into one reviewable revision and run Ruff, full
	pytest, Hugo, Pagefind, rendered contracts, internal links, full-scope Zizmor,
	Playwright including analytics, and Lighthouse.
6. Execute the isolated all-generator two-run proof and Phase 4 remote runtime
	scenarios. These can run in parallel after the revision is frozen.
7. Collect three comparable timing reports, the protected Podcaster result, and
	refreshed visual evidence in parallel against the same accepted revision.
8. Complete platform, accessibility, security, URL, and sponsor reviews. Enable
	dynamic topics and repository pages only in separate later changes after each
	flag's own approval.

The lifecycle and Podcaster changes should not be parallelized within their own
workstreams because each changes a single end-to-end contract. Analytics/browser,
candidate security, workflow security, minor defects, and evidence preparation
have independent ownership and can proceed concurrently after the critical
semantics are fixed.

## Unresolved External Boundaries

* Authenticated access to artifact `8744139176` is required to enumerate the exact
	hosted Playwright failures
* SquadScope-Podcaster must confirm that its dry-run endpoint accepts complete
	promoted article content above 50,000 characters without a request-size or
	schema limit
* The protected `podcaster-release-smoke` environment must contain its endpoint
	variable, masked API key, approval policy, and authorized reviewer
* GitHub Actions or an acceptance repository is required for remote publish lease,
	failure rollback, no-op rerun, deploy hydration, and retained run evidence
* URL and the Squad generator owner must decide where durable fixes to generated
	Squad workflows are maintained
* Hermes must disposition SEC-01 through SEC-06, including the embed analytics
	policy and deletion-override policy
* jmservera must approve separate Hugo and Pagefind budgets after three comparable
	reports
* GA4, GSC, social preview, Rich Results, Schema.org, production feed, and
	production response evidence requires external service access
* Accessibility acceptance requires a named keyboard and screen-reader reviewer
* Sponsor approval must identify dynamic-topic creation and repository-page
	creation separately
* An approved evidence location is needed for redacted platform, browser, and
	protected-run artifacts that should not be committed publicly

## Clarifying Questions

* Should embedded endpoints omit analytics entirely, or will Amy and Hermes
	approve an explicit cross-origin consent and referrer policy?
* Which promotion record and deployed revision are the designated relaunch
	acceptance state for Podcaster, platform, visual, and accessibility evidence?
* Is the Phase 10 contract intended to scan generated Squad workflows? If yes,
	which upstream repository or generator owns durable remediation?
* Who is the named owner for the final Hugo and Pagefind budget approval and the
	human accessibility conclusion?
* Where should authenticated artifact `8744139176` and redacted external evidence
	be retained so reviewers can audit them without exposing secrets?
