---
title: Claracle Data Observatory Relaunch Unit 006 Validation
description: RPI validation of PRD sections 7 through 14 against repository evidence
author: GitHub Copilot
ms.date: 2026-07-29
ms.topic: review
---

## Validation scope

* Phase: PRD unit 6, sections 7 through 14
* Status: Failed
* Implementation plan: Missing
* Changes log: Missing
* Primary requirements: `docs/prds/claracle-data-observatory-relaunch.md`,
	`docs/brds/claracle-data-observatory-relaunch-brd.md`, and `architecture.md`
* Evidence: Current workflows, scripts, tests, documentation, and visual artifacts
* Validation date: 2026-07-29

The implementation has substantial working capability, but required launch gates
are unmet or lack executable evidence. The visual review is not sufficient to
claim final acceptance because it contains a visibly empty topic hub, while GSC,
performance, accessibility, security review, Podcaster smoke, and measured build
capacity remain unverified.

## Requirements traceability

### Section 7 non-functional requirements

* NFR-001 performance: Not evidenced. The required Lighthouse Performance score
	of at least 90 applies to hub, data, and repository pages
	(`docs/prds/claracle-data-observatory-relaunch.md:157-158`). The runner does not
	enforce a performance score and targets only home, weekly, monthly, and yearly
	pages (`scripts/design/lighthouse-gates.mjs:13-28,48-65`). No committed results
	exist under `screenshots/lighthouse-results/`.
* NFR-002 reliability: Partial. Unit tests cover the payload builder
	(`tests/test_podcaster_handoff.py:133-284`), but the smoke workflow is manual-only
	(`.github/workflows/podcaster-handoff-smoke.yml:1-24`) and no passing run is in
	the supplied evidence. Production deploy does not depend on that smoke
	(`.github/workflows/deploy-site.yml:90-123`).
* NFR-003 maintainability: Met for threshold configuration. Repository and topic
	thresholds are in `config/observatory.toml:1-24`; behavior is tested in
	`tests/test_observatory_repos.py:55-85` and `tests/test_topic_hubs.py:50-151`.
* NFR-004 security: Partial. Goldmark remains safe
	(`hugo.toml:154-156`), repository text uses the sanitizer
	(`scripts/generate_content.py:13-67`), and the client tool uses DOM text APIs,
	same-origin fetch, and URL validation (`assets/js/star-velocity-explorer.js:64-79,131`).
	No relaunch-specific Hermes review was found, and PRD risk R-05 remains open
	(`docs/prds/claracle-data-observatory-relaunch.md:210`).
* NFR-005 accessibility: Partial implementation, no acceptance result. Charts
	include hidden textual summaries (`layouts/partials/visuals/repo-trend.html:44-55`),
	but no axe or Lighthouse report covers the new page types. The documented runner
	targets legacy page types only (`scripts/design/lighthouse-gates.mjs:21-28`).
* NFR-006 SEO correctness: Partial. A strict rendered title and description test
	exists (`tests/test_rendered_seo_metadata.py:47-83`) and the preview workflow
	invokes it (`.github/workflows/site-preview.yml:97-102`). No Rich Results result
	was supplied. Local rendered tests skipped because Hugo is unavailable.
* NFR-007 observability: Not met. The dated baseline states GSC verification,
	sitemap submission, and real dashboard capture are still human-blocked
	(`docs/growth/ga4-gsc-baseline-2026-07-29.md:7-12`), and every launch baseline
	value remains TBD (`docs/growth/ga4-gsc-baseline-2026-07-29.md:48-62`).
* NFR-008 privacy: Implemented, acceptance incomplete. Analytics starts disabled
	and loads only after consent (`layouts/partials/cookie-consent.html:44-95`),
	with analytics off by default (`data/cookieconsent.json:7-24`). Screenshots show
	the consent UI, but no browser network or cookie assertion was supplied.
* NFR-009 scalability: Not evidenced. Design estimates explicitly require actual
	Hugo and Pagefind timings (`docs/design/data-observatory-model.md:420-449`). CI
	builds the site but records no timing budget or regression gate
	(`.github/workflows/ci.yml:94-106`).
* NFR-010 portability: Met at the implementation level. Architecture retains Hugo
	and GitHub Pages (`architecture.md:9-15`); the tool reads one same-origin static
	JSON file (`content/tools/star-velocity-explorer/index.md:6-13`), and its
	deterministic export is tested (`tests/test_trend_explorer_tool.py:16-35`).

### Sections 8 through 14

* Data inputs and deterministic output: Partial to strong. Data pages, repository
	pages, and the trend explorer derive from checked-in artifacts and have
	deterministic tests (`tests/test_generate_data_pages.py:55-80`,
	`tests/test_observatory_repos.py:128-165`, and
	`tests/test_trend_explorer_tool.py:16-35`). The monthly data-page workflow states
	that no crawl is performed (`.github/workflows/generate-data-pages.yml:3-8,34-56`).
* Analytics events: Not met. Consent-gated `page_view` is supported, but no
	`dataset_download`, `chart_embed_view`, or `tool_interaction` implementation was
	found for the instrumentation plan at
	`docs/prds/claracle-data-observatory-relaunch.md:175-181`.
* Dependencies and contracts: Partial. Hugo, checked-in data, and static hosting
	are preserved. The documented handoff fields remain in the payload builder
	(`scripts/podcaster_handoff.py:654-735`), but no current cross-repository smoke
	result proves compatibility with SquadScope-Podcaster.
* Risks: Partial. Sanitization, static-only tooling, provenance, and internal-link
	checks mitigate R-02, R-03, and part of R-05. R-01 is realized by the empty MCP
	hub; R-04 lacks smoke evidence; R-05 lacks the named review; R-06 lacks measured
	build cost. All seven risks remain marked open in the PRD
	(`docs/prds/claracle-data-observatory-relaunch.md:204-211`).
* Privacy, security, and compliance: Partial. Consent gating and MIT dataset
	licensing are implemented (`content/state-of/open-source-ai-2026.md:13-18` and
	`scripts/export_observatory_dataset.py:298-347`). The required security review
	is absent.
* Operations: Partial. CI enforces tests, build, image checks, and internal links
	(`.github/workflows/ci.yml:33-50,94-106`), and data pages regenerate monthly
	(`.github/workflows/generate-data-pages.yml:3-8`). No workflow invokes
	`manage_topic_hubs.py`, `observatory_repos.py`,
	`export_observatory_dataset.py`, or `export_trend_explorer_data.py`, so those
	surfaces do not have the required recurring operational cadence.
* Rollout: Not met. Wave dates remain TBD and Wave 1 requires populated topic
	hubs, validated SEO, internal links, and verified GSC
	(`docs/prds/claracle-data-observatory-relaunch.md:240-246`). GSC is unverified,
	and current weekly content still lacks `topics`
	(`content/weekly/2026/W31.md:1-13`). The configured dynamic topic behavior is
	already enabled (`config/observatory.toml:22-24`) despite the rollout table
	specifying off until validation; no `repo_pages` feature flag exists
	(`docs/prds/claracle-data-observatory-relaunch.md:248-252`).
* Open questions: Not resolved. Actual incremental build cost remains unmeasured,
	and the PRD still labels tool selection as an open design spike even though the
	Star Velocity Explorer has shipped
	(`docs/prds/claracle-data-observatory-relaunch.md:257-261`).

## Findings

### Critical findings

#### Launch acceptance is contradicted by required Wave 1 evidence

The visual acceptance review calls the gallery a final pass and claims a dynamic
MCP hub (`docs/review/data-observatory-relaunch/README.md:3-18`), but
`docs/review/data-observatory-relaunch/screenshots/03-topic-hub-mcp.png` visibly
shows `Recent weekly issues (0)`. The latest weekly issue has no `topics`
frontmatter (`content/weekly/2026/W31.md:1-13`). GSC verification, sitemap
submission, and baseline metrics also remain incomplete
(`docs/growth/ga4-gsc-baseline-2026-07-29.md:7-12,48-62`). These are explicit Wave
1 gates, so launch acceptance cannot be claimed.

#### Required operational regeneration is absent for most new surfaces

Only data pages have a scheduled generator
(`.github/workflows/generate-data-pages.yml:3-8,34`). No workflow invokes topic
lifecycle, repository-page, dataset, or trend-explorer generation. The repository
therefore contains deterministic generators without an operational path that
updates those outputs from each new weekly source artifact. This breaks the
future-state pipeline and weekly operational cadence required by PRD sections 8
and 12.

#### Podcaster contract preservation lacks release evidence

NFR-002 requires unchanged weekly pipeline and handoff smoke behavior
(`docs/prds/claracle-data-observatory-relaunch.md:159`). The smoke workflow can
exercise the real payload but is dispatch-only
(`.github/workflows/podcaster-handoff-smoke.yml:1-24,153-189`), does not gate CI or
deploy, and has no supplied passing run. Unit tests demonstrate local payload
behavior but cannot prove current downstream compatibility.

### Major findings

#### Performance, accessibility, and scalability acceptance gates are missing

There is no Lighthouse result for hub, data, or repository pages, no axe result,
and no recorded build timing. The Lighthouse script omits the required page types
and does not fail on Performance below 90
(`scripts/design/lighthouse-gates.mjs:13-28,48-65`). NFR-001, NFR-005, and NFR-009
therefore remain unvalidated.

#### Analytics instrumentation and launch baseline are incomplete

Only consent-gated GA4 loading is implemented. Three named custom events are
absent, and the dated baseline contains only TBD values. This prevents measurement
of dataset, embed, and tool adoption and fails NFR-007 plus the section 8
instrumentation plan.

#### Security controls exist, but the required review is absent

`unsafe=false`, sanitization, static data, and safe DOM construction reduce the
technical risk. The PRD nevertheless requires a Hermes review and keeps R-05 open
(`docs/prds/claracle-data-observatory-relaunch.md:160,210`). No relaunch-specific
review artifact was found, so security acceptance is incomplete.

#### Rollout flags and state do not match the approved launch plan

Dynamic topic creation is enabled before its stated validation gate, and repository
page generation has no off-by-default feature flag. Wave dates and gate completion
records are absent. The implementation cannot be rolled out or rolled back using
the controls described in section 13.

#### Visual evidence is insufficient for rendered acceptance

The screenshots prove that representative pages render, but they are desktop-only,
the consent modal obscures central content in several captures, and they provide no
dark-theme, mobile, interaction, performance, accessibility, structured-data, or
network evidence. The gallery's prose claims strict SEO and clean links without
including the corresponding command or CI results
(`docs/review/data-observatory-relaunch/README.md:30-41`).

#### Required RPI traceability artifacts are missing

No implementation plan or changes log exists under `.copilot-tracking/plans/` or
`.copilot-tracking/changes/`. Requirement-to-change comparison had to be inferred
from the current tree and issue references in the visual review. This prevents
verification that the shipped changes match an approved phase through-line.

### Minor findings

#### Operational ownership is named but not made actionable

The PRD assigns Amy, Bender, Farnsworth, and Fry and calls for weekly GA4/GSC
review (`docs/prds/claracle-data-observatory-relaunch.md:232-238`), but no relaunch
runbook defines the review ritual, escalation path, dashboard location, or owner
handoff for failed generation.

## Coverage assessment

Implementation capability is approximately 60% covered for this unit; launch
acceptance evidence is approximately 35% covered.

Verified strengths:

* Static, no-backend architecture and no on-demand recrawl
* Configurable thresholds
* Deterministic data-page, repository-page, and tool exports
* Consent-gated GA4 implementation
* `unsafe=false`, repository-text sanitization, and safe client rendering
* MIT dataset license and citations
* CI Hugo build and internal-link gate definitions

Unverified or missing launch evidence:

* Populated current topic hubs
* GSC verification, sitemap submission, and real baseline values
* Custom analytics events
* Lighthouse Performance at least 90 on new page types
* WCAG 2.1 AA audit and chart alternatives across rendered pages
* Rich Results validation
* Measured build-time budget
* Passing Podcaster handoff smoke against the downstream service
* Hermes security review
* Scheduled regeneration for hubs, repository pages, dataset, and tool data
* Rollout gate sign-off and feature-flag conformance

## Executed validation

* `python3 -m pytest -q tests/test_generate_data_pages.py`: 8 passed, 1 skipped
* Focused repository, topic, tool, dataset, sanitizer, and link-check tests:
	34 passed, 4 skipped
* Rendered SEO tests: 4 skipped because Hugo is not installed locally
* `hugo --minify`: not run because the Hugo executable is unavailable
* Fresh rendered internal-link check: not run because Hugo could not build
* Initial combined execution was interrupted, and one retry failed at the
	execution-service transport layer; neither result was counted as product evidence

## Clarifying questions

* Which GitHub Actions run proves the current Podcaster smoke passed against the
	downstream service after the relaunch changes?
* Has GSC verification and sitemap submission occurred outside the repository, and
	where are the dated GA4/GSC baseline values stored?
* Where is the Hermes review for dataset, embed, and client-tool exposure?
* Were the PRD feature flags intentionally superseded, or should dynamic topic and
	repository generation still be gated?
* What workflow is intended to regenerate topic hubs, repository pages, dataset
	exports, and trend-explorer JSON after each weekly crawl?
* Where are the Lighthouse, accessibility, Rich Results, mobile, and dark-theme
	acceptance reports for the new page types?

## Recommended next validations

* Run the Podcaster smoke against the current downstream service and retain the run
	URL and payload-schema result
* Run Hugo, Pagefind, and internal-link checks from a clean checkout using the CI
	tool versions
* Run Lighthouse and axe on hub, data, repository, chart, and tool pages at desktop
	and mobile sizes
* Validate Article and Breadcrumb output with Rich Results and retain results
* Capture measured Hugo and Pagefind timings and define a regression budget
* Verify GSC, submit the sitemap, confirm GA4 consent behavior in network storage,
	and fill the launch baseline
* Execute the missing scheduled generators twice and compare byte-identical output
* Re-capture visual evidence after current weekly topics populate the hubs