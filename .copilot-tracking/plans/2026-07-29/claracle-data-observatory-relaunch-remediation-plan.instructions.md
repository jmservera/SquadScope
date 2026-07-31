---
applyTo: '.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md'
---
<!-- markdownlint-disable-file -->
# Implementation Plan: Claracle Data Observatory Relaunch Remediation

## Overview

Operationalize the existing Claracle Data Observatory implementation, close every critical and major review finding, and gather evidence required for an honest relaunch decision.

## Objectives

### User Requirements

* Plan all missing tasks identified by the attached relaunch implementation review and RPI validation reports - Source: user request, 2026-07-29
* Produce implementation-ready planning artifacts for later `/task-implement` execution - Source: conversation context after the missing-plan halt

### Derived Objectives

* Repair the weekly-to-topic path before validating downstream hub, feed, and SEO behavior - Derived from: FR-001 through FR-004 failures and the empty-hub evidence
* Make the guarded weekly `publish` transaction the single writer for all Observatory outputs - Derived from: recurring-generation and manual-publication findings
* Persist stable repository identity and lifecycle state so rename, archive, deletion, and retention are enforced rather than described - Derived from: FR-022 failure
* Expand automated contracts for metadata, schema, links, accessibility, performance, privacy, timing, and downstream handoff - Derived from: launch gate evidence gaps
* Separate repository-verifiable implementation from external platform acceptance and sign-off - Derived from: GSC, GA4, social/schema debugger, security, and Podcaster evidence boundaries
* Preserve already accepted data pages, dataset, chart, State-of report, README, and client-tool runtime - Derived from: review strengths and passed requirements

## Context Summary

### Project Files

* `scripts/generate_content.py` - canonical weekly topic derivation and frontmatter emission
* `scripts/taxonomy_registry.py` - canonical topic usage registry
* `scripts/manage_topic_hubs.py` - dynamic hub promotion and continuity
* `scripts/observatory_repos.py` - repository history, generation, and current lifecycle behavior
* `scripts/crawl.py` - source GitHub metadata reduction and validation
* `.github/workflows/crawl-and-publish.yml` - guarded weekly publication transaction
* `.github/workflows/deploy-site.yml` - production deployment hydration
* `layouts/partials/seo.html` - active SEO and structured-data controller
* `layouts/topics/list.html` - topic aggregation and highlights
* `layouts/repo/single.html` - repository page links and lifecycle presentation
* `scripts/design/lighthouse-gates.mjs` - current browser quality thresholds
* `.github/workflows/podcaster-handoff-smoke.yml` - downstream compatibility smoke

### References

* `.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md` - primary planning synthesis
* `.copilot-tracking/research/subagents/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md` - verified codebase research and implementation recommendations
* `.copilot-tracking/reviews/2026-07-29/claracle-data-observatory-relaunch-review.md` - seven critical, thirteen major, and three minor findings
* `.copilot-tracking/reviews/rpi/2026-07-29/claracle-data-observatory-relaunch-001-validation.md` through `claracle-data-observatory-relaunch-006-validation.md` - requirement-level evidence
* `docs/prds/claracle-data-observatory-relaunch.md` - functional, non-functional, rollout, and acceptance requirements
* `docs/brds/claracle-data-observatory-relaunch-brd.md` - business acceptance criteria
* `architecture.md` - static Hugo and weekly pipeline architecture

### Standards References

* `.github/copilot-instructions.md` - repository testing, workflow, security, and cross-repository conventions
* `vscode-local:/c%3A/Users/juanserv/.vscode/extensions/ise-hve-essentials.hve-core-all-3.2.2/.github/instructions/hve-core/markdown.instructions.md` - Markdown requirements
* `vscode-local:/c%3A/Users/juanserv/.vscode/extensions/ise-hve-essentials.hve-core-all-3.2.2/.github/instructions/coding-standards/python-script.instructions.md` - Python implementation requirements

## Architecture Overview

```text
weekly crawl + analysis
        |
        v
canonical weekly topics --> candidate evidence --> guarded hub promotion
        |                                           |
        +------------------ final topic membership -+
                            |
                            v
stable repository identity --> lifecycle ledger --> retained repo pages
                            |
                            v
single guarded publish transaction
  topics + repo pages + rankings + dataset + tool JSON
                            |
                            v
publish branch hydration --> Hugo/Pagefind --> deploy --> Podcaster smoke
                            |
                            v
SEO/link/privacy/a11y/performance/external acceptance evidence
```

## Affected Files Tree

```text
.github/workflows/
  ci.yml
  crawl-and-publish.yml
  deploy-site.yml
  generate-data-pages.yml
  podcaster-handoff-smoke.yml
assets/js/
  observatory-analytics.js
  star-velocity-explorer.js
config/observatory.toml
content/weekly/2026/W21.md ... W31.md
data/derived/observatory/repository-lifecycle.json
data/taxonomy/topic-candidates.json
docs/
  data-observatory-runbook.md
  decisions/adr-star-velocity-explorer.md
  design/data-observatory-model.md
  growth/ga4-gsc-baseline-2026-07-29.md
  review/data-observatory-relaunch/
layouts/
  partials/seo.html
  partials/cookie-consent.html
  partials/visuals/observatory-chart.html
  topics/list.html
  repo/single.html
scripts/
  backfill_weekly_topics.py
  discover_topic_candidates.py
  crawl.py
  manage_topic_hubs.py
  observatory_repos.py
  taxonomy_registry.py
  design/lighthouse-gates.mjs
tests/
  test_weekly_topic_backfill.py
  test_rendered_weekly_links.py
  test_rendered_seo_metadata.py
  test_topic_hubs.py
  test_observatory_repos.py
  test_pipeline.py
  visual/observatory-analytics.spec.mjs
  visual/observatory-a11y.spec.mjs
```

## Design Patterns Applied

* Deterministic generated artifacts with `--check` freshness modes
* Single-writer, lease-protected publication transaction
* Versioned durable ledgers for state that cannot be reconstructed safely from a current sample
* Positive-evidence lifecycle transitions; absence is not deletion
* Editorial canonical topics separated from raw source tags
* Off-by-default creation flags with non-destructive disable behavior
* Rendered contract tests for user-visible and crawler-visible output
* Consent-gated, bounded analytics payloads
* Evidence-based rollout with external checkpoints kept explicit

## Implementation Checklist

### [x] Implementation Phase 1: Traceability and Rollout Baseline

<!-- parallelizable: false -->

* [x] Step 1.1: Establish implementation tracking
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 12-25)
* [x] Step 1.2: Restore rollout flags to the approved default
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 26-44)
* [x] Step 1.3: Capture the executable baseline
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 45-56)

### [x] Implementation Phase 2: Weekly Topic Through-Line

<!-- parallelizable: false -->

* [x] Step 2.1: Add deterministic weekly topic backfill
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 61-78)
* [x] Step 2.2: Discover candidates with threshold and supporting evidence
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 79-96)
* [x] Step 2.3: Promote candidates and update hubs automatically
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 97-116)

### [x] Implementation Phase 3: Durable Repository Lifecycle

<!-- parallelizable: false -->

* [x] Step 3.1: Preserve stable identity and lifecycle fields
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 121-136)
* [x] Step 3.2: Persist lifecycle state and enforce retention
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 137-155)
* [x] Step 3.3: Add curated repository-to-topic links
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 156-171)

### [x] Implementation Phase 4: Atomic Publish Orchestration

<!-- parallelizable: false -->

* [x] Step 4.1: Move weekly-derived generation into the guarded transaction
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 176-193)
* [x] Step 4.2: Publish and deploy every generated path atomically
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 194-210)
* [x] Step 4.3: Remove the competing publication path
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 211-225)

### [x] Implementation Phase 5: SEO and Rendered Link Contracts

<!-- parallelizable: true -->

* [x] Step 5.1: Emit page-appropriate metadata and schema
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 230-245)
* [x] Step 5.2: Require dimensions for every social image
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 246-260)
* [x] Step 5.3: Expand rendered SEO, feed, and weekly-link tests
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 261-279)

### [x] Implementation Phase 6: Consent-Gated Observatory Analytics

<!-- parallelizable: true -->

* [x] Step 6.1: Add a shared consent-aware event API
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 284-299)
* [x] Step 6.2: Instrument dataset, chart, and tool interactions
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 300-318)

### [ ] Implementation Phase 7: Performance, Accessibility, and Timing Gates

<!-- parallelizable: true -->

* [x] Step 7.1: Expand Lighthouse and browser coverage
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 323-339)
* [x] Step 7.2: Add WCAG-oriented axe and interaction checks
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 340-356)
* [ ] Step 7.3: Measure Hugo and Pagefind separately
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 357-372)

### [ ] Implementation Phase 8: Podcaster Release Smoke

<!-- parallelizable: true -->

* [x] Step 8.1: Make the smoke workflow reusable
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 377-392)
* [ ] Step 8.2: Invoke and retain release evidence
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 393-407)

### [ ] Implementation Phase 9: Documentation and Acceptance Evidence

<!-- parallelizable: false -->

* [x] Step 9.1: Record operational and design decisions
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 412-426)
* [ ] Step 9.2: Complete and sign the security review
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 427-440)
* [ ] Step 9.3: Gather external launch evidence
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 441-457)
* [ ] Step 9.4: Reconcile release status and visuals
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 458-475)

### [ ] Implementation Phase 10: Final Validation

<!-- parallelizable: false -->

* [ ] Step 10.1: Run full repository validation
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 480-495)
* [ ] Step 10.2: Prove idempotence and lifecycle acceptance
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 496-504)
* [x] Step 10.3: Fix minor issues and report blockers
  * Details: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md` (Lines 505-508)

## Parallelization Summary

* Phases 1 through 4 are sequential because they establish shared state formats and the publication transaction.
* Phases 5 through 8 can execute in parallel after Phase 4; Phase 7 exclusively owns the shared `.github/workflows/ci.yml` integration while the other phases deliver their scoped tests and workflows.
* Phase 9 is sequential after automated gates because status and evidence must describe final behavior.
* Phase 10 is the combined final gate.

## Planning Log

See `.copilot-tracking/plans/logs/2026-07-29/claracle-data-observatory-relaunch-remediation-log.md` for discrepancy tracking, implementation paths considered, and suggested follow-on work.

## Dependencies

* Python dependencies and pinned Ruff configuration from `pyproject.toml`
* Hugo Extended and Pagefind versions used by CI
* Node.js with pinned Playwright, Lighthouse, and axe dependencies
* Protected deploy and Podcaster environment secrets
* GSC, GA4, social preview, schema validation, and security-review access
* Owner approval for rollout dates, timing budgets, and final lifecycle status

## Success Criteria

* All seven critical, thirteen major, and three minor review findings are implemented or intentionally deferred with rationale and an explicit acceptance checkpoint - Traces to: attached implementation review
* Weekly W21 through W31 populate canonical topic hubs and feeds; future candidates can be discovered and promoted safely - Traces to: FR-001 through FR-004
* All generated Observatory surfaces publish atomically from one hydrated weekly state - Traces to: FR-003, FR-011, FR-021, and operational findings
* Repository rename, archive, confirmed deletion, and three-year retention behavior is durable and tested - Traces to: FR-022
* Metadata, canonical URLs, social dimensions, schema, sitemap, feeds, and weekly required links have blocking rendered tests - Traces to: FR-030 through FR-034 and FR-040 through FR-041
* Observatory analytics remains consent-gated and emits only bounded payloads - Traces to: instrumentation plan and NFR-008
* New page classes meet Lighthouse Performance at least 90 and reviewed WCAG checks; build timing has measured evidence - Traces to: NFR-001, NFR-005, and NFR-009
* A downstream Podcaster smoke proves the exact relaunch state without changing the shared payload contract - Traces to: NFR-002
* GSC, GA4, schema/social tools, security review, accessibility review, and final visuals have dated evidence before acceptance - Traces to: FR-035 and NFR-004 through NFR-007
* Existing accepted data pages and linkable assets remain regression-free - Traces to: FR-010 and FR-050 through FR-060
