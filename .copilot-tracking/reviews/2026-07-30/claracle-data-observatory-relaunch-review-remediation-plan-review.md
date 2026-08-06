<!-- markdownlint-disable-file -->
# Review: Claracle Data Observatory Relaunch Review Remediation

## Review Metadata

| Field | Value |
|---|---|
| Review date | 2026-07-30 |
| Plan | `.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md` |
| Changes | `.copilot-tracking/changes/2026-07-30/claracle-data-observatory-relaunch-review-remediation-changes.md` |
| Pull request | `jmservera/SquadScope#623` |
| Review status | Iterate |

## Request Fulfillment

| Request | Status | Evidence |
|---|---|---|
| Implement the review-remediation plan | Partial | Repository phases 1 through 5, atomic proof Step 6.1, deterministic Step 6.2, protected Podcaster execution, and full validation are complete; timing and named external acceptance remain open |
| Render a real breadcrumb using the existing construct | Complete | Existing partial retained; marker-free chevrons, wrapping, accessibility, and single schema ownership pass rendered tests |
| Generate a PR or parallel PRs | Complete | Existing PR #623 owns the branch; one PR preserves the coupled remediation and validation history |
| Keep rollout controls disabled until approval | Complete | Both production flags remain false |
| Support correct local navigation | Complete | CI and documented static builds override Hugo `baseURL` with the local server URL |

## Repository Finding Disposition

* CR-01 is resolved in repository code: deletion confirmation is required, validated, non-future, and cannot shorten configured retention.
* CR-02 is resolved in repository code: exact article content is opt-in, byte-hashed, verified before transport, and invoked by checked-in workflow logic.
* CR-03 is resolved: current-main run `31039618366` passed the blocking browser, analytics privacy, and Lighthouse jobs.
* CR-04 is resolved at blocking severity: full-scope Zizmor reports zero high and medium findings. One pinned-package low finding has a narrow documented disposition.
* CR-05 repository sanitization is resolved. SEC-01 through SEC-05, SEC-09, and SEC-10 have dated dispositions; SEC-06 production analytics evidence, SEC-08, and production-owner acceptance remain pending.
* CR-06 is resolved for the protected Podcaster run and repository automation. External platform, accessibility, and visual evidence remains open because it requires protected access and named actors.
* CR-07 sponsor decisions are resolved: repository pages are approved, and dynamic topic creation is approved in principle subject to security disposition and an approved canary. Both flags correctly remain disabled.
* MAJ-01 through MAJ-03 and the external dataset-path defect are resolved in repository code and tests.
* MAJ-04 is resolved by run `31040602642`. MAJ-05 and MAJ-07 remain open for timing-budget and visual acceptance. MAJ-06 is resolved. MAJ-08 remains partial until all external evidence is immutable and directly linked.

## Validation Review

* Full Python validation passed: 1,396 tests and 34 subtests.
* Hugo 0.161.1 rendered validation passed: 37 contract tests plus the lifecycle fixture.
* The isolated publication generator sequence is byte-clean on its second pass.
* Hugo, Pagefind, and internal-link validation passed on one isolated artifact.
* Checkov passed with 724 checks and no failures.
* Zizmor has zero high or medium findings across `.github/workflows/`.
* Exact-current-main hosted run `31039618366` passed Python, publish hydration parity, Hugo, Pagefind, rendered metadata and links, internal links, Playwright accessibility and analytics, and Lighthouse.
* Atomic proof run `31040602642` passed and retained the reviewed JSON and tree manifests.
* Protected Podcaster run `30908778884` succeeded with downstream status `accepted`.

## Placement and Quality

The changes are placed in the owning abstractions: lifecycle validation and seeding remain in the repository generator; exact-content behavior remains opt-in in the Podcaster handoff; visible navigation remains in the existing breadcrumb partial; structured data remains in the SEO partial; privacy behavior is tested through the real consent UI; and workflow permissions are scoped at their jobs and checkouts.

No rollout flag, threshold, assertion, or security scan scope was weakened to obtain a pass.

## Blocking Issues

| Blocker | Owner or access | Required next action |
|---|---|---|
| Three-run timing and approved budgets | Timing owner | Retain three comparable reports and approve median/p95 budgets |
| Platform and accessibility evidence | GA4/GSC actors and accessibility reviewer | Record dated analytics, search, debugger, keyboard, and screen-reader observations |
| Final security acceptance | Hermes and jmservera | Close SEC-08, retain SEC-06 production observations, and record the production-owner conclusion |
| Visual acceptance | Amy or named visual reviewer | Capture and accept the revision-tagged visual matrix |

## Overall Status

Iterate. Repository remediation is ready for refreshed CI and review, but merge and relaunch approval remain blocked by hosted runtime and external acceptance evidence. Keep both rollout flags disabled.
