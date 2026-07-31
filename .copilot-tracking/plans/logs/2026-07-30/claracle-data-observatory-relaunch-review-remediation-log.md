<!-- markdownlint-disable-file -->
# Planning Log: Claracle Data Observatory Relaunch Review Remediation

## Discrepancy Log

Gaps and differences identified between review research and the implementation plan.

### Unaddressed Research Items

None. All research items and user requirements are addressed by the current plan.

### Plan Deviations from Research

None. The selected implementation paths align with the research recommendations.

## Implementation Paths Considered

### Selected: Staged Fail-Closed Rework and Evidence Closure

* Approach: Correct lifecycle and exact-release semantics, repair the existing breadcrumb and browser/privacy gates, close content and workflow security gaps, then execute runtime and external acceptance against one revision.
* Rationale: This addresses root causes before collecting evidence and keeps rollout controls off until every acceptance boundary is explicit.
* Evidence: `.copilot-tracking/research/2026-07-30/claracle-data-observatory-relaunch-review-remediation-research.md`

### IP-01: Enable Repository Pages to Populate the Ledger

* Approach: Temporarily enable production repository generation and let the normal path create lifecycle state.
* Trade-offs: Reuses normal generation but violates rollout isolation and can mutate pages, taxonomy, and derived state before acceptance.
* Rejection rationale: A ledger-only seed mode provides deterministic migration without publication side effects.

### IP-02: Raise the Normal Podcaster Content Limit

* Approach: Remove the 50,000-character limit for every handoff.
* Trade-offs: Simpler exact-byte behavior but changes the shared normal contract and may exceed downstream limits unexpectedly.
* Rejection rationale: An opt-in exact-release mode limits blast radius and preserves existing callers.

### IP-03: Replace the Breadcrumb With a New Component

* Approach: Add a new div-based or theme-copied breadcrumb renderer.
* Trade-offs: Can remove numbering quickly but duplicates existing layout calls, weakens semantics, and risks a second visual language.
* Rejection rationale: The existing local partial is already accessible; only list styling, chevrons, and schema ownership need correction.

### IP-04: Suppress Squad Workflow Findings

* Approach: Exclude generated Squad workflows or broadly suppress Zizmor findings.
* Trade-offs: Makes the gate green without reducing excessive permissions or credential persistence.
* Rejection rationale: The final plan requires aligned full-scope scans and narrow reviewed dispositions.

## Suggested Follow-On Work

* WI-01: Steady-state lifecycle verifier - Evaluate rate-limited redirect and deletion confirmation for tracked repositories (medium priority, medium effort)
  * Source: Prior planning WI-01
  * Dependency: Accepted lifecycle ledger and crawl policy
* WI-02: Safari compatibility lane - Add separately named WebKit coverage when Safari is an explicit release requirement (low priority, medium effort)
  * Source: Browser matrix research
  * Dependency: Stable Chromium blocking suite and installed WebKit dependencies
* WI-03: Breadcrumb design-system consolidation - Evaluate moving breadcrumb CSS and component contracts into a shared navigation module after relaunch (low priority, small effort)
  * Source: Breadcrumb research
  * Dependency: Accepted visible breadcrumb implementation
* WI-04: Steady-state acceptance cadence - Assign recurring GA4/GSC, Podcaster smoke, timing, accessibility, and workflow-security reviews (medium priority, small effort)
  * Source: External acceptance boundaries
  * Dependency: Relaunch acceptance

## Implementation Deviations

* The production-quality build now passes its local `BASE_URL` to Hugo. This keeps
  CI and manual static-server navigation on the served artifact while production
  deploy builds continue to use the configured `https://claracle.com/` base URL.
* Local Playwright and Lighthouse execution stopped before browser launch because
  the host lacks Playwright shared-library dependencies. The corrected four-project
  Chromium matrix is discoverable, and the refreshed hosted Production site job is
  the required executable evidence.
* The first isolated generator pass refreshed
  `data/taxonomy/topic-candidates.json` after the sanitizer rejected a suspicious
  title. The second complete pass was byte-identical and all freshness checks passed.

## Open Evidence Boundaries

* Controlled publish success, no-op rerun, injected failure, and deployment identity
* Three comparable hosted timing reports and approved budgets
* Protected exact-content Podcaster execution
* Hermes, URL, accessibility, platform, visual, and sponsor acceptance
* Refreshed Production site browser and Lighthouse checks for the candidate revision
