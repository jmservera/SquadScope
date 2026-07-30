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
| Implement the review-remediation plan | Partial | Repository phases 1 through 5 and deterministic Step 6.2 are complete; protected runtime and external phases remain open |
| Render a real breadcrumb using the existing construct | Complete | Existing partial retained; marker-free chevrons, wrapping, accessibility, and single schema ownership pass rendered tests |
| Generate a PR or parallel PRs | Complete | Existing PR #623 owns the branch; one PR preserves the coupled remediation and validation history |
| Keep rollout controls disabled until approval | Complete | Both production flags remain false |
| Support correct local navigation | Complete | CI and documented static builds override Hugo `baseURL` with the local server URL |

## Repository Finding Disposition

* CR-01 is resolved in repository code: deletion confirmation is required, validated, non-future, and cannot shorten configured retention.
* CR-02 is resolved in repository code: exact article content is opt-in, byte-hashed, verified before transport, and invoked by checked-in workflow logic.
* CR-03 repository corrections are complete: the browser matrix is four Chromium projects, analytics privacy is blocking, and local-baseURL navigation is fixed. Hosted browser and Lighthouse execution remains pending.
* CR-04 is resolved at blocking severity: full-scope Zizmor reports zero high and medium findings. One pinned-package low finding has a narrow documented disposition.
* CR-05 repository sanitization is resolved. Hermes, URL, and owner acceptance remains pending.
* CR-06 remains open because external platform, production endpoint, accessibility, and downstream evidence requires protected access and named actors.
* CR-07 remains open because separate sponsor approval for both rollout flags is absent.
* MAJ-01 through MAJ-03 and the external dataset-path defect are resolved in repository code and tests.
* MAJ-04 through MAJ-08 remain partially open where they require hosted runtime, timing, visual, immutable run, or external acceptance evidence.

## Validation Review

* Full Python validation passed: 1,396 tests and 34 subtests.
* Hugo 0.161.1 rendered validation passed: 37 contract tests plus the lifecycle fixture.
* The isolated publication generator sequence is byte-clean on its second pass.
* Hugo, Pagefind, and internal-link validation passed on one isolated artifact.
* Checkov passed with 724 checks and no failures.
* Zizmor has zero high or medium findings across `.github/workflows/`.
* Local Playwright and Lighthouse are blocked before browser launch by missing host shared libraries. Hosted CI is the required next evidence source.

## Placement and Quality

The changes are placed in the owning abstractions: lifecycle validation and seeding remain in the repository generator; exact-content behavior remains opt-in in the Podcaster handoff; visible navigation remains in the existing breadcrumb partial; structured data remains in the SEO partial; privacy behavior is tested through the real consent UI; and workflow permissions are scoped at their jobs and checkouts.

No rollout flag, threshold, assertion, or security scan scope was weakened to obtain a pass.

## Blocking Issues

| Blocker | Owner or access | Required next action |
|---|---|---|
| Hosted Production site browser and Lighthouse result | GitHub Actions | Push candidate revision and retain successful run plus report artifact |
| Atomic publish and failure rollback proof | Workflow operator | Run controlled normal, no-op, and injected-failure scenarios |
| Protected exact-content Podcaster result | Podcaster maintainer and protected environment | Execute designated promotion after deployment |
| Three-run timing and approved budgets | Timing owner | Retain three comparable reports and approve median/p95 budgets |
| Platform and accessibility evidence | GA4/GSC actors and accessibility reviewer | Record dated observations and retained links |
| Security and workflow-owner sign-off | Hermes and URL | Close or accept all named findings |
| Visual and rollout approval | Sponsor | Accept refreshed matrix and approve each flag separately |

## Overall Status

Iterate. Repository remediation is ready for refreshed CI and review, but merge and relaunch approval remain blocked by hosted runtime and external acceptance evidence. Keep both rollout flags disabled.
