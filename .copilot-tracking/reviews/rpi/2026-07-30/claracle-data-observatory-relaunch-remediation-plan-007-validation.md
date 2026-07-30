---
title: Claracle Data Observatory Relaunch Remediation Phase 7 Validation
description: RPI validation of Phase 7 performance, accessibility, and timing gates
author: GitHub Copilot
ms.date: 2026-07-30
ms.topic: review
---

## Validation Scope

* Plan: `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md`
* Changes log: `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md`
* Research: `.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md`
* Phase: 7
* Status: Partial
* Active pull request: `jmservera/SquadScope#623`, commit
	`f7adea1a4f06b2e0d3417956e9d00b42343939fc`
* Validation date: 2026-07-30

Repository implementation and external browser or owner acceptance are assessed
separately.

## Phase 7 Requirements

### Step 7.1 Lighthouse and browser coverage

* Add topic, data, repository, chart, and tool routes
* Enforce Lighthouse Performance at least 0.90, accessibility at least 0.95,
	and CLS at most 0.1
* Upload machine-readable reports that identify the route and failed category
* Run the gates from the production-equivalent Phase 4 build

Source: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:323-339`.

### Step 7.2 WCAG and interaction checks

* Test WCAG 2.1 A/AA serious and critical axe violations
* Test labels, keyboard operation, visible focus, consent behavior, chart text
	alternatives, responsive overflow, mobile, and dark theme
* Require core keyboard behavior and chart alternatives to pass

Source: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:340-356`.

### Step 7.3 Separate Hugo and Pagefind timing

* Capture separate report-only durations for at least three representative CI
	runs
* Calculate median and p95 from comparable reports
* Record an explicit owner-approved budget before enforcing a blocking threshold
* Do not present an invented threshold as acceptance evidence

Source: `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:357-372`.
Research independently requires measured baselines before approval at
`.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:31-32,66`.

## Plan-to-Changes Comparison

### Step 7.1

Status: Repository implementation complete; acceptance failed or unproven.

The changes log claims expanded CI, five Observatory routes, report uploads,
and pending local browser execution at
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:131-135,180-188`.
The claimed files exist and are modified by PR 623. The source implementation
matches the planned route and threshold shape. The active PR does not provide a
passing browser result: CI run `30502305707` failed the Production site job at
the axe and responsive browser gate, and the later Lighthouse step was skipped.

### Step 7.2

Status: Repository implementation complete; acceptance failed.

The changes log lists the new accessibility spec and browser matrix at
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:79-80,132-134`.
The files are present in PR 623 and contain the planned axe, keyboard, focus,
consent, chart, responsive, mobile, and theme checks. The only external CI run
completed the browser step with `failure`, so the required no-unreviewed-serious-
or-critical result is not established.

### Step 7.3

Status: Partial and accurately left open by the plan.

The changes log records one local sample and explicitly leaves the three-run
median, p95, and approved budget pending at
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:180-188`.
PR CI run `30502305707` successfully wrote and retained one external
`production-quality-reports` artifact. It is the branch's only CI run. Therefore,
only one of three required external reports exists, no representative statistics
can be calculated, and no owner-approved budget exists.

## Verified Repository Evidence

### Production CI ownership

`.github/workflows/ci.yml:58-66` defines one Production site job with pinned
Hugo, Pagefind, Playwright, axe, and Lighthouse versions. It installs Chromium
with host dependencies at `.github/workflows/ci.yml:114-121`, captures Hugo and
Pagefind separately at `.github/workflows/ci.yml:123-151`, serves the same build,
runs Playwright before Lighthouse at `.github/workflows/ci.yml:164-175`, and
uploads timing, Lighthouse, and Playwright reports at
`.github/workflows/ci.yml:177-190`.

### Lighthouse implementation

`scripts/design/lighthouse-gates.mjs:18-33` defines Performance 0.90,
accessibility 0.95, CLS 0.1, and all five Observatory routes in addition to the
legacy matrix. `scripts/design/lighthouse-gates.mjs:68-94` records structured
category failures. `scripts/design/lighthouse-gates.mjs:112-143` includes each
route in the summary, writes per-route JSON plus `summary.json`, and exits nonzero
when any route fails.

### Accessibility implementation

`tests/visual/observatory-a11y.spec.mjs:4-45` runs WCAG 2.1 A/AA axe checks and
responsive overflow assertions across topic, data, repository, chart, and tool
routes. `tests/visual/observatory-a11y.spec.mjs:48-102` covers labels, keyboard
input, focus visibility and restoration, consent dialogs, and the chart image
alternative and source caption. `tests/visual/a11y-perf.spec.mjs:12-31,54-119`
adds the Observatory routes to the five-viewport overflow and 44-by-44 tap-target
matrix. `tests/visual/playwright.config.mjs:54-87` defines desktop and mobile,
light and dark projects, while `.github/workflows/ci.yml:171-172` invokes both
browser specs.

### Timing implementation

`.github/workflows/ci.yml:123-151` measures Hugo and Pagefind independently and
writes `reports/build-timing.json` with `mode` set to `report-only` and a null
blocking threshold. `docs/design/data-observatory-model.md:413-433` records one
local sample, states that it is not a representative CI baseline, lists the
three-run, median, p95, budget, and approval gaps, and correctly states that no
blocking threshold is approved or enforced.

No `build-timing.json`, Lighthouse result, or Playwright JSON report is checked
into the workspace. That is consistent with ephemeral CI reports, but repository
source alone cannot establish a passing browser result.

## External Acceptance Evidence

PR 623 is open from `feat/observatory-relaunch-remediation` into `main`. All six
Phase 7 files inspected above are changed by the PR. The PR page reports 15 of 16
checks passing, with CI as the remaining failure.

The only branch CI run is
<https://github.com/jmservera/SquadScope/actions/runs/30502305707>. Its Production
site job is
<https://github.com/jmservera/SquadScope/actions/runs/30502305707/job/90744394455>
and has these relevant conclusions:

* Hugo timing capture: success
* Pagefind timing capture: success
* Report-only timing write: success
* Production server startup: success
* Axe and responsive browser gates: failure
* Lighthouse gates: skipped
* Production quality report upload: success

The retained artifact is `production-quality-reports`, artifact ID `8744139176`,
created on 2026-07-30 with expiry on 2026-08-29. Public run metadata does not
expose the individual Playwright failures or timing values. The artifact must be
inspected by an authenticated reviewer before failures can be triaged.

The successful Site Preview run
<https://github.com/jmservera/SquadScope/actions/runs/30502305725> built and
retained rendered HTML only. It does not substitute for the failed Phase 7
browser job, skipped Lighthouse execution, accessibility review, or timing
baseline.

## Findings

### Critical

#### RPI-007-001 Browser acceptance is failing and Lighthouse did not execute

The sole PR Production site job failed at `Run axe and responsive browser gates`.
Because the workflow is sequential at `.github/workflows/ci.yml:171-175`, the
Lighthouse gate was skipped. There is consequently no passing evidence that the
new page classes meet Performance 0.90, accessibility 0.95, CLS 0.1, or the
required axe and interaction checks. Source-level gate definitions are complete,
but NFR-001 and NFR-005 launch acceptance remains blocked.

Required action: inspect artifact `8744139176`, correct or explicitly review
every browser failure, rerun PR CI to success, and retain both Playwright and
Lighthouse reports for the same revision.

### Major

#### RPI-007-002 The timing baseline has only one of three required CI reports

The branch has one CI run and one retained timing artifact. The plan requires at
least three comparable external CI runs before median, p95, budget proposal, and
owner approval. `docs/design/data-observatory-model.md:420-433` correctly leaves
all four acceptance items pending, so no unsupported threshold was introduced.
NFR-009 remains incomplete and no blocking timing budget may be enabled yet.

Required action: collect two more comparable successful Production site timing
artifacts at stable page volume, record all three values and revisions, calculate
median and p95 separately for Hugo and Pagefind, then obtain explicit owner
approval for the proposed budgets.

### Minor

#### RPI-007-003 The changes log does not include the current PR failure evidence

The Phase 7 history at
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:180-188`
accurately says browser execution and timing approval are pending, but it only
describes the local missing-library blocker. It does not record that CI run
`30502305707` installed dependencies successfully, then failed Playwright and
skipped Lighthouse. This omission makes the log less useful as the promised
progressive implementation and acceptance record.

Required action: after triage, add the run URL, failed gate, Lighthouse skipped
state, artifact ID, and final rerun conclusion to the changes log.

## Coverage Assessment

Overall Phase 7 status is **Partial**.

* Step 7.1 source implementation: Complete
* Step 7.1 browser acceptance: Failed or unproven
* Step 7.2 source implementation: Complete
* Step 7.2 browser acceptance: Failed
* Step 7.3 timing instrumentation: Complete in report-only mode
* Step 7.3 representative timing evidence: Partial, one of three CI reports
* Step 7.3 median and p95: Missing
* Step 7.3 owner-approved budget: Missing

Repository implementation coverage is high: all planned files and control paths
are present in PR 623. Acceptance coverage is low: neither browser through-line
has a passing external result, Lighthouse has no result for this revision, and
timing has only its first required CI sample. The changes log and plan correctly
keep Phase 7 open, but the current PR cannot satisfy the relaunch gate.

## Clarifying Questions

* Which assertions failed inside artifact `8744139176`, and are any axe findings
	proposed for review rather than remediation?
* Who will approve the final separate Hugo and Pagefind budgets after the third
	comparable CI report is available?

## Recommended Next Validations

* [ ] Download and inspect artifact `8744139176`, including
	`screenshots/playwright-report.json` and the HTML report
* [ ] Rerun PR 623 Production site after resolving every Playwright failure
* [ ] Confirm Lighthouse executes and all nine route summaries pass on the same
	revision
* [ ] Retain two additional comparable `build-timing.json` artifacts
* [ ] Calculate and document separate Hugo and Pagefind median and p95 values
* [ ] Obtain and record owner approval before adding any blocking timing budget
* [ ] Perform the named keyboard and screen-reader accessibility review required
	by the release evidence index
* [ ] Update the changes log with dated CI and artifact links