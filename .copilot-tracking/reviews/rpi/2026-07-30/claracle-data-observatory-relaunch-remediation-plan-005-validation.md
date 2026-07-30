<!-- markdownlint-disable-file -->
# RPI Validation: Claracle Data Observatory Relaunch Remediation Phase 5

## Validation Summary

* Status: Passed
* Phase: 5, SEO and Rendered Link Contracts
* Validation date: 2026-07-30
* Plan: `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md`
* Changes log: `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md`
* Research: `.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md`
* Current PR branch: `feat/observatory-relaunch-remediation`
* Inspected commit: `f7adea1`, matching `origin/feat/observatory-relaunch-remediation`
* Merge base: `83000a4ffab8ee83906b81a3f6bb3034a14156b4` against `origin/main`

## Phase Requirements

Phase 5 contains three completed checklist items in the plan at
`.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md:189-197`:

1. Emit page-appropriate metadata and schema.
2. Require dimensions for every social image.
3. Expand rendered SEO, sitemap, feed, and weekly-link tests.

The detailed plan requires parseable page-class JSON-LD, correct absolute
breadcrumbs, non-Article data and repository pages, positive social image
dimensions and alt text, a hard failure for missing remote dimensions,
canonical and social contracts, valid XML, every promoted topic feed, no news
sitemap, and required weekly chronological, topic, and repository links at
`.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:226-278`.

These requirements match the research findings at
`.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:26-27`
and the selected entity types at
`.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:58`.

## Plan-to-Changes Comparison

| Plan item | Changes-log claim | Verified status | Evidence |
|-----------|-------------------|-----------------|----------|
| Step 5.1, page-class metadata and schema | CR-04 complete with nine rendered SEO tests | Complete | `layouts/partials/seo.html:177-275`; `tests/test_rendered_seo_metadata.py:122-218` |
| Step 5.2, dimensions for every social image | MAJ-04 complete for fallback, local, explicit remote, and invalid remote images | Complete | `layouts/partials/seo.html:53-89`; `layouts/partials/seo.html:125-127`; `tests/test_rendered_seo_metadata.py:279-325` |
| Step 5.3, rendered SEO, XML, feed, and weekly-link coverage | MAJ-05 and MAJ-06 complete | Complete | `tests/test_rendered_seo_metadata.py:154-238`; `tests/test_rendered_weekly_links.py:110-140`; `tests/test_topic_hubs.py:580-616`; `.github/workflows/ci.yml:153-159` |

The claims are recorded in
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:18`
and
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:25-27`.
All five Phase 5 implementation paths are committed changes relative to the
merge base: `.github/workflows/site-preview.yml`,
`layouts/partials/seo.html`, `tests/test_rendered_seo_metadata.py`,
`tests/test_rendered_weekly_links.py`, and `tests/test_topic_hubs.py`.

## Verified Repository Evidence

### Metadata and schema

* Editorial weekly, monthly, and yearly pages retain `Article` at
	`layouts/partials/seo.html:177-194`.
* Topic terms emit `CollectionPage` plus a weekly `ItemList` at
	`layouts/partials/seo.html:195-220`.
* Data pages emit `Dataset` plus a ranking `ItemList` at
	`layouts/partials/seo.html:222-255`.
* Repository pages emit `WebPage` plus `SoftwareSourceCode` at
	`layouts/partials/seo.html:257-277`.
* Rendered tests parse JSON-LD, require representative page-class entities,
	reject generic `Article` classification for data and repository pages, and
	validate site-wide absolute schema URLs and breadcrumb positions at
	`tests/test_rendered_seo_metadata.py:122-218`.

### Social images

* The SEO partial resolves configured, page-resource, global-resource, and
	static-file dimensions, then stops the Hugo build unless both dimensions
	are positive at `layouts/partials/seo.html:53-91`.
* Every page emits Open Graph image alt, width, and height fields at
	`layouts/partials/seo.html:125-127`.
* Rendered fixtures cover default, local, explicit remote, and missing remote
	dimensions at `tests/test_rendered_seo_metadata.py:240-325`.

### Rendered SEO, feed, and links

* Site-wide tests require canonical and complete social fields, positive
	dimensions, parseable JSON-LD, absolute schema URLs, and sequential
	breadcrumbs at `tests/test_rendered_seo_metadata.py:154-218`.
* XML tests parse every generated XML file, require absolute Claracle URLs,
	and reject a news sitemap at `tests/test_rendered_seo_metadata.py:220-238`.
* Weekly-link tests derive and require previous and next weeks, promoted
	canonical topics, and generated repository pages. A mutation-style check
	proves removal of any required link is detected at
	`tests/test_rendered_weekly_links.py:67-140`.
* Topic-hub tests require every currently promoted hub feed to exist, parse,
	and contain absolute Claracle URLs at `tests/test_topic_hubs.py:580-616`.
* Preview CI runs all four rendered modules at
	`.github/workflows/site-preview.yml:103-109`. Production CI installs Hugo
	Extended 0.161.1 and runs the same modules as a blocking step at
	`.github/workflows/ci.yml:62-109` and `.github/workflows/ci.yml:153-159`.

### Execution evidence

* The changes log records 11 focused passes with 13 Hugo-dependent skips,
	followed by nine rendered SEO passes under Hugo Extended 0.161.1 at
	`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:163-169`.
* The planning log records a later complete rendered run with 21 passing
	contracts and three Phase 5 failures, followed by all nine focused repaired
	SEO tests passing at
	`.copilot-tracking/plans/logs/2026-07-29/claracle-data-observatory-relaunch-remediation-log.md:54-57`.
* Static editor diagnostics report no errors in the five Phase 5 files.
* An independent rerun during this validation could not complete because the
	shared terminal repeatedly executed and interrupted unrelated queued
	commands. This is an evidence-provenance limitation, not a test failure.

## Findings

### Critical

None.

### Major

None.

### Minor

#### RPI-005-01: Phase 5 execution evidence is not linked to an immutable run

The changes log gives aggregate pass counts and the Hugo version at
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:163-169`,
but it does not retain a GitHub Actions run URL or artifact for the complete
post-repair four-module suite. The planning log provides composable evidence
that the only three failures were repaired at
`.copilot-tracking/plans/logs/2026-07-29/claracle-data-observatory-relaunch-remediation-log.md:54-57`,
and both preview and production workflows enforce the complete suite. This is
a traceability gap, not a missing implementation.

## Coverage Assessment

Repository implementation coverage is 100 percent: all three Phase 5 plan
items have matching committed implementation, focused rendered contracts, and
blocking CI integration. CR-04, MAJ-04, MAJ-05, and MAJ-06 are supported by
current source evidence. No Phase 5 plan item is missing or partially
implemented.

Validation confidence is high for source and workflow coverage and moderate
for retained execution provenance because no immutable current-PR run was
available in the supplied artifacts and the local shared terminal could not
produce a clean independent rerun.

## Repository Implementation and External Acceptance

Phase 5 repository implementation passes. The SEO controller, rendered
contracts, and blocking CI ownership are present in the current PR.

External acceptance remains separate and does not reduce Phase 5 repository
coverage. GSC ownership, production sitemap submission, GA4 receipt, and
social debugger evidence cannot be proven from repository tests, as stated at
`.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:50-53`.
The changes log correctly assigns GSC and GA4 acceptance to Phase 9 at
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:19`
and social debugger and feed acceptance evidence to Phase 9 at
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:35`.
Those external checks remain required for relaunch acceptance, but they are
not missing Phase 5 code.

## Clarifying Questions

None required to grade Phase 5. A GitHub Actions run URL for commit `f7adea1`
would close the minor evidence-provenance finding.

## Recommended Next Validations

* Retain the current PR production-site or site-preview run URL showing the
	complete four-module rendered suite passing after the SEO repair.
* Validate production canonical, sitemap, RSS, Schema.org, and social-card
	output after deployment as Phase 9 external acceptance evidence.
* Complete GSC sitemap submission and GA4 verification under their named
	external owners before relaunch acceptance.