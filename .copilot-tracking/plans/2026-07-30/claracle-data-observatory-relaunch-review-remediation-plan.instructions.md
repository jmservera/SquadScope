---
applyTo: '.copilot-tracking/changes/2026-07-30/claracle-data-observatory-relaunch-review-remediation-changes.md'
---
<!-- markdownlint-disable-file -->
# Implementation Plan: Claracle Data Observatory Relaunch Review Remediation

> **STATUS — DONE / CLOSED 2026-08-08.** All items delivered. Retired per [BRD-CLARACLE-003](../../../docs/brds/claracle-post-relaunch-consolidation-brd.md).

## Overview

Correct PR #623's repository defects, render the existing breadcrumb construct as an accessible visual breadcrumb, restore blocking quality and security gates, and complete the evidence required for a defensible relaunch decision.

## Objectives

### User Requirements

* Plan remediation of the 2026-07-30 task review findings - Source: conversation and attached task-plan prompt
* Fix the visible numbered breadcrumb so it renders as a real breadcrumb, reusing an existing template construct where possible - Source: user request, 2026-07-30
* Keep planning grounded in existing research and conversation context - Source: attached task-plan prompt

### Derived Objectives

* Correct deletion retention and seed durable lifecycle state before repository-page rollout - Derived from: review CR-01 and MAJ-02
* Preserve normal Podcaster behavior while adding a testable exact-release path - Derived from: review CR-02
* Make analytics privacy, accessibility, breadcrumb presentation, and Lighthouse behavior blocking on one production-equivalent build - Derived from: review CR-03 and MAJ-03
* Close candidate-title and workflow security gaps without weakening gates - Derived from: review CR-04 and CR-05
* Separate repository corrections from protected Actions, platform, reviewer, visual, and sponsor acceptance - Derived from: review CR-06, CR-07, and research boundaries
* Replace descriptive completion claims with immutable evidence and re-review all original findings - Derived from: review MAJ-08

## Context Summary

### Project Files

* `layouts/partials/breadcrumbs.html` - existing accessible visible breadcrumb component and duplicate schema emission
* `assets/css/common/post-single.css` - existing PaperMod-derived `.breadcrumbs` styles that currently target the wrong element
* `layouts/partials/seo.html` - canonical JSON-LD breadcrumb owner
* `scripts/observatory_repos.py` - lifecycle retention, seed, and generation behavior
* `scripts/podcaster_handoff.py` - normal and exact-release payload behavior
* `.github/workflows/podcaster-handoff-smoke.yml` - protected exact-release verifier
* `.github/workflows/ci.yml` - production browser, analytics, Lighthouse, timing, and report gates
* `scripts/manage_topic_hubs.py` - candidate sanitization, structured generation, and disabled decision
* `.github/workflows/squad-*.yml` - repository-wide Zizmor findings and workflow ownership
* `docs/review/data-observatory-relaunch/` - security, platform, visual, and acceptance evidence

### References

* `.copilot-tracking/research/2026-07-30/claracle-data-observatory-relaunch-review-remediation-research.md` - primary planning synthesis
* `.copilot-tracking/research/subagents/2026-07-30/claracle-data-observatory-relaunch-review-remediation-research.md` - verified implementation paths and breadcrumb research
* `.copilot-tracking/reviews/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-review.md` - seven critical, eight major, and four minor findings
* `.copilot-tracking/reviews/quality/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-quality.md` - direct source-quality findings
* `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-001-validation.md` through `claracle-data-observatory-relaunch-remediation-plan-010-validation.md` - phase evidence
* `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md` - original implementation plan
* `docs/prds/claracle-data-observatory-relaunch.md` and `docs/brds/claracle-data-observatory-relaunch-brd.md` - requirements and sponsor acceptance

### Standards References

* `.github/copilot-instructions.md` - repository testing, workflow, security, and cross-repository conventions
* `vscode-local:/c%3A/Users/juanserv/.vscode/extensions/ise-hve-essentials.hve-core-all-3.2.2/.github/instructions/hve-core/markdown.instructions.md` - Markdown requirements
* `vscode-local:/c%3A/Users/juanserv/.vscode/extensions/ise-hve-essentials.hve-core-all-3.2.2/.github/instructions/hve-core/writing-style.instructions.md` - documentation voice and style
* `vscode-local:/c%3A/Users/juanserv/.vscode/extensions/ise-hve-essentials.hve-core-all-3.2.2/.github/instructions/coding-standards/python-script.instructions.md` - Python requirements

## Architecture Overview

```text
review defects
    |
    +--> lifecycle fail-closed + ledger-only seed
    +--> exact-release Podcaster mode + executable verifier
    +--> existing breadcrumb partial + PaperMod chevrons + single SEO schema
    +--> real consent tests + deterministic browser matrix
    +--> candidate sanitization + workflow security
                         |
                         v
atomic/runtime/idempotence proofs
                         |
                         v
security + platform + visual + sponsor acceptance
                         |
                         v
full validation + RPI re-review
```

## Affected Files Tree

```text
.github/workflows/
  ci.yml
  podcaster-handoff-smoke.yml
  crawl-and-publish.yml
  deploy-site.yml
  squad-*.yml
assets/css/common/post-single.css
assets/js/observatory-analytics.js
config/observatory.toml
data/derived/observatory/repository-lifecycle.json
layouts/partials/
  breadcrumbs.html
  seo.html
scripts/
  observatory_repos.py
  podcaster_handoff.py
  manage_topic_hubs.py
  discover_topic_candidates.py
  export_observatory_dataset.py
tests/
  test_observatory_repos.py
  test_podcaster_handoff.py
  test_pipeline.py
  test_topic_hubs.py
  test_rendered_seo_metadata.py
  visual/
    observatory-a11y.spec.mjs
    observatory-analytics.spec.mjs
    playwright.config.mjs
docs/
  data-observatory-runbook.md
  design/data-observatory-model.md
  review/data-observatory-relaunch/
  growth/ga4-gsc-baseline-2026-07-29.md
```

## Design Patterns Applied

* Fail-closed reviewed state transitions
* Ledger-only migration separated from page publication
* Opt-in exact-release behavior preserving default cross-repository contracts
* Existing semantic breadcrumb partial with PaperMod-compatible visual language
* Single ownership for visible navigation and structured data
* Real consent-boundary browser tests rather than adapter-only mocks
* Browser project and installed-engine parity
* Structured serialization for untrusted generated content
* Least-privilege workflow permissions and explicit credential persistence
* Immutable evidence references and staged rollout acceptance

## Implementation Checklist

### [x] Implementation Phase 1: Lifecycle Safety and Durable Seed

<!-- parallelizable: true -->

* [x] Step 1.1: Fail closed on deletion confirmation
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 12-30)
* [x] Step 1.2: Add a ledger-only lifecycle seed mode
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 32-52)
* [x] Step 1.3: Validate lifecycle rendering and idempotence
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 54-68)

### [x] Implementation Phase 2: Exact-Release Podcaster Contract

<!-- parallelizable: true -->

* [x] Step 2.1: Add an opt-in exact article mode
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 74-91)
* [x] Step 2.2: Replace or execute workflow verifier logic
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 93-112)
* [x] Step 2.3: Validate the protected exact-release workflow locally
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 114-128)

### [x] Implementation Phase 3: Breadcrumb and Browser Quality

<!-- parallelizable: false -->

* [x] Step 3.1: Render a real visible breadcrumb using the existing partial
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 134-156)
* [x] Step 3.2: Make analytics privacy tests end to end and blocking
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 158-178)
* [x] Step 3.3: Repair the browser matrix and rerun production quality
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 180-201)

### [x] Implementation Phase 4: Dynamic Topic and Minor Repository Corrections

<!-- parallelizable: false -->

* [x] Step 4.1: Sanitize candidate titles and generate structured frontmatter
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 207-227)
* [x] Step 4.2: Correct reusable freshness error reporting
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 229-245)
* [x] Step 4.3: Document embed privacy and update traceability
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 247-265)

### [x] Implementation Phase 5: Workflow Security Remediation

<!-- parallelizable: true -->

* [x] Step 5.1: Align repository-wide and hosted Zizmor scope
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 271-288)
* [x] Step 5.2: Remove excessive permissions and credential persistence
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 290-314)

### [x] Implementation Phase 6: Runtime and Determinism Evidence

<!-- parallelizable: false -->

* [x] Step 6.1: Prove atomic publish behavior
  * Reconciliation: Run `31040602642` passed against `211f0974ce375e427591803cc3f3dfd39e169ead` on 2026-08-05. The retained `atomic-publish-proof` artifact records one normal commit, an unchanged identical rerun, injected-failure exit `23` with an unchanged ref, equal candidate and accepted digests, equal accepted and hydrated digests, and no reference problems. jmservera reviewed the artifact during this reconciliation.
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 320-336)
* [x] Step 6.2: Prove all-generator idempotence in isolation
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 338-352)
* [x] Step 6.3: Collect timing and protected Podcaster evidence
  * Reconciliation: Both halves of the evidence collection are complete. The protected downstream run `30908778884` succeeded for `2026-W32` and publish run `30782430176`; downstream job `podcast-2026-W32-d07bb05dc073` returned `accepted`, with Hermes and URL dispositions retained by `#658` and `#659`. Timing collection is now delivered: three comparable production `main` runs (`31039618366`, `31079871801`, `31081291997`) are transcribed with per-tool median and p95 computed in `docs/review/data-observatory-relaunch/timing-analysis.md`. The remaining budget-owner threshold approval is a human gate tracked separately (owner: timing-budget owner / URL / jmservera).
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 354-369)

### [ ] Implementation Phase 7: Security and External Acceptance

<!-- parallelizable: false -->

* [x] Step 7.1: Close security findings and sign-off
  * Reconciliation: NFR-004 is fully closed. All ten findings SEC-01 through SEC-10 carry dated Hermes or URL dispositions (SEC-01–SEC-05 and SEC-09 on 2026-08-04; SEC-06, SEC-07, SEC-08, SEC-10 on 2026-08-06), and the jmservera production-owner acceptance is recorded 2026-08-06 in `docs/review/data-observatory-relaunch/security-sign-off-checklist.md`.
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 375-389)
* [ ] Step 7.2: Gather platform and accessibility evidence
  * Reconciliation: human-authority (owners: Amy, Fry, jmservera). Current-main CI run `31039618366` passed production Hugo, Pagefind, rendered metadata and links, browser accessibility and analytics contracts, and Lighthouse. GA4 stream operation, GSC verification, root sitemap submission, and the GA4-to-GSC link are owner-confirmed. Live denied and granted consent observations, GSC processing and baseline values, external debugger conclusions, and named keyboard and screen-reader review remain a human reviewer step.
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 391-404)
* [ ] Step 7.3: Replace visuals and obtain rollout approvals
  * Reconciliation: human-authority (owners: Amy, Fry). `#669` records separate sponsor decisions: `repo_pages` is approved and `dynamic_topic_creation` is approved in principle subject to security disposition and an approved canary. The revision-tagged desktop, mobile, light, dark, and interaction visual matrix plus named visual acceptance remain open; neither flag is enabled by this plan and the `allow_topics` allowlist now bounds any dynamic-topic canary.
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 406-424)

### [ ] Implementation Phase 8: Final Validation and Re-Review

<!-- parallelizable: false -->

* [x] Step 8.1: Run full repository validation
  * Reconciliation: Exact-main run `31039618366` passed Python, publish-hydration parity, Hugo, Pagefind, rendered metadata and links, internal links, Playwright accessibility and analytics, and Lighthouse. Ruff run `31039618827`, Checkov run `31039617650`, security-scanning run `31039617802`, and deploy plus dry-run Podcaster run `31039617808` also passed for `211f0974ce375e427591803cc3f3dfd39e169ead`.
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 430-444)
* [x] Step 8.2: Repair and rerun validation failures
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 446-456)
* [ ] Step 8.3: Revalidate every review finding
  * Reconciliation: human-authority (owners: Amy, Fry, jmservera). Later reviews close the repository-executable portions of CR-01 through CR-05 and MAJ-01 through MAJ-03, plus the protected Podcaster portion of CR-06, and NFR-004 security is now fully accepted (2026-08-06). Final disposition remains open for timing budget-owner approval, named visual acceptance, and the external launch evidence.
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 458-473)
* [x] Step 8.4: Report blocking issues
  * Details: `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` (Lines 475-485)

## Parallelization Summary

* Phases 1, 2, and 5 can begin in parallel because they own separate implementation and test surfaces.
* Phase 3 is sequential internally because breadcrumb, analytics, browser projects, CI, and Lighthouse share one production-quality job.
* Phase 4 remains sequential because its traceability step consumes results from Phases 1 through 3.
* Phase 6 waits for all repository corrections and security workflow changes.
* Phases 7 and 8 are sequential because acceptance evidence must reference one validated deployed revision.

## Planning Log

See `.copilot-tracking/plans/logs/2026-07-30/claracle-data-observatory-relaunch-review-remediation-log.md` for discrepancy tracking, implementation paths considered, and suggested follow-on work.

## Dependencies

* Python dependencies and pinned Ruff configuration from `pyproject.toml`
* Hugo Extended 0.161.1 and Pagefind 1.5.2
* Node.js with pinned Playwright, axe, and Lighthouse packages
* Access to Production site artifact `8744139176`
* URL and Squad ownership for generated workflow security changes
* Protected deploy and Podcaster environment secrets
* GA4, GSC, social/schema debugger, and production endpoint access
* Hermes, URL, accessibility, timing-budget, and sponsor approvers
* Coordination with SquadScope-Podcaster for exact-content body-size acceptance

## Success Criteria

* Every review critical and major repository finding is resolved with executable evidence - Traces to: 2026-07-30 review
* Deleted pages retain for at least three years after explicit confirmation and the current corpus has deterministic durable lifecycle state - Traces to: CR-01 and MAJ-02
* Protected Podcaster smoke compiles, transmits exact bytes above 50,000 characters only in opt-in mode, and succeeds downstream - Traces to: CR-02
* Visible breadcrumbs reuse the existing partial, display marker-free chevrons, wrap on mobile, remain accessible, and emit no duplicate schema - Traces to: user request and breadcrumb research
* Analytics consent, accessibility, responsive, breadcrumb, and Lighthouse gates pass on one production-equivalent build - Traces to: CR-03 and MAJ-03
* Candidate generation and all workflows meet sanitization and repository-wide security gates - Traces to: CR-04 and CR-05
* Atomicity, all-generator idempotence, timing, platform, visual, accessibility, security, and sponsor evidence is immutable and tied to one revision - Traces to: CR-06, CR-07, and MAJ-04 through MAJ-08
* Both rollout flags remain disabled until separately approved - Traces to: PRD and BRD rollout requirements
