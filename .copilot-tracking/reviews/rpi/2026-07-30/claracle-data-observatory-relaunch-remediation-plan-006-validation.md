---
title: Claracle Data Observatory Relaunch Remediation Phase 6 Validation
description: RPI validation of Phase 6 implementation against the plan, changes log, research, and current pull request evidence
ms.date: 2026-07-30
ms.topic: reference
---

## Validation Scope

* Plan: `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md`
* Changes log: `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md`
* Research: `.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md`
* Phase: 6
* Status: Partial
* Validation basis: Local pull request branch `feat/observatory-relaunch-remediation` at pushed commit `f7adea1`, compared with merge base `83000a4ffab8ee83906b81a3f6bb3034a14156b4` on `origin/main`
* Remote pull request limitation: GitHub pull request metadata and status checks could not be retrieved because the GitHub CLI query was interrupted; repository evidence uses the local merge-base diff and current workspace

## Phase Requirements

Phase 6 is marked complete in the plan at
`.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md:200-206`.
The detailed plan defines these requirements:

1. Add a shared event dispatcher that sends nothing before analytics consent, queues no pre-consent telemetry, and stops dispatch after withdrawal (`.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:284-297`).
2. Emit `dataset_download`, `chart_embed_view`, and bounded `tool_interaction` events containing only normalized IDs, paths, action names, and sanitized referrer hosts (`.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:300-314`).
3. Exclude search terms and repository names from payloads (`.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:28`).
4. Prove no pre-consent GA script, cookie, data-layer event, or network request; prove expected post-consent events and bounded payloads through browser tests (`.copilot-tracking/research/subagents/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:416-419`).
5. Document that off-site embed telemetry is best-effort because cross-origin consent may not transfer, without weakening consent (`.copilot-tracking/research/subagents/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:418-420`).

## Plan-To-Changes Comparison

| Plan item | Changes-log claim | Verified status | Evidence |
|-----------|-------------------|-----------------|----------|
| Step 6.1 shared consent-aware event API | Complete pending browser CI | Implemented; runtime acceptance incomplete | `assets/js/observatory-analytics.js:4-78,110-116,140-144`; `layouts/partials/cookie-consent.html:48-89,121-136`; `layouts/partials/head.html:217-220` |
| Step 6.2 instrument dataset, chart, and tool interactions | Complete pending browser CI | Implemented; browser contract not enforced | `assets/js/observatory-analytics.js:85-138`; `assets/js/star-velocity-explorer.js:21-29,158-181`; `layouts/partials/visuals/observatory-chart.html:15-33`; `layouts/embeds/baseof.html:17-21` |
| Browser consent, withdrawal, payload, and network assertions | Blocked locally by missing `libnspr4.so` | Partial and absent from CI | `tests/visual/observatory-analytics.spec.mjs:10-116`; `.github/workflows/ci.yml:171-172` |
| Off-site embed limitation | Documented | Partial | `docs/review/data-observatory-relaunch/security-review.md:93-102,141,153`; no equivalent limitation appears in `docs/data-observatory-runbook.md` |

The changes log labels MAJ-09 as complete pending browser CI at
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:30`
and records blocked browser execution at lines 171-177. The claim that Phase 6 is complete at line 230
is not fully supported because CI does not invoke the Phase 6 browser spec.

## Verified Repository Evidence

The local pull request diff adds or modifies all expected Phase 6 surfaces:

* Adds `assets/js/observatory-analytics.js` and `tests/visual/observatory-analytics.spec.mjs`
* Modifies `assets/js/star-velocity-explorer.js`, `layouts/partials/cookie-consent.html`, `layouts/partials/head.html`, `layouts/partials/visuals/observatory-chart.html`, and `layouts/embeds/baseof.html`
* Modifies `.github/workflows/ci.yml`, but its browser command does not include the Phase 6 spec

The implementation evidence is substantive:

* The dispatcher allowlists event fields and action names, normalizes IDs, restricts paths to same-origin values, sanitizes hostnames, and returns before `gtag` when consent is absent (`assets/js/observatory-analytics.js:4-78`).
* Consent state is initialized false and follows the existing Cookie Consent analytics category on consent and preference changes (`layouts/partials/cookie-consent.html:55-89,118-136`).
* Dataset clicks are delegated only for same-origin `/datasets/` links (`assets/js/observatory-analytics.js:117-138`).
* The Star Velocity Explorer emits only bounded action identifiers and does not pass query text or repository names (`assets/js/star-velocity-explorer.js:21-29,158-181`).
* Standalone charts expose a normalized chart identity and embed marker used by the dispatcher (`layouts/partials/visuals/observatory-chart.html:15-33`; `assets/js/observatory-analytics.js:85-107`).

Focused validation performed on 2026-07-30:

* `node --check assets/js/observatory-analytics.js`: passed
* `node --check assets/js/star-velocity-explorer.js`: passed
* `node --check tests/visual/observatory-analytics.spec.mjs`: passed
* Hugo build and rendered assertions: not repeated because Hugo is unavailable in this environment
* Playwright discovery and execution: not repeated because no local Playwright package is installed

## External Acceptance Evidence

Repository implementation does not prove first-visit production network behavior, GA4 cookie behavior,
GA4 receipt, or production secret configuration. The security review keeps those checks external at
`docs/review/data-observatory-relaunch/security-review.md:118-124`.

Cross-origin embed acceptance is also unresolved. The security review records that consent does not
automatically cross origins and leaves SEC-02 open pending a no-analytics embed or explicit privacy
policy decision (`docs/review/data-observatory-relaunch/security-review.md:93-102,141,153`). This is an
external Amy and Hermes acceptance decision, not evidence that the bounded dispatcher is absent.

## Findings

### Critical

None recorded.

### Major

1. The Phase 6 browser contract is not invoked by CI. The only production browser command runs
   `tests/visual/a11y-perf.spec.mjs` and `tests/visual/observatory-a11y.spec.mjs`; it omits
   `tests/visual/observatory-analytics.spec.mjs` (`.github/workflows/ci.yml:171-172`). The changes log
   therefore cannot rely on pending browser CI to close consent, withdrawal, payload, and network
   acceptance. A future regression can merge while the dedicated Phase 6 suite remains unexecuted.

2. The browser spec does not validate the complete research contract. It replaces `window.gtag` and
   directly calls `window.ObservatoryAnalytics.setConsent(true/false)`
   (`tests/visual/observatory-analytics.spec.mjs:10-18,58,70,82,108`) instead of accepting and
   withdrawing consent through Cookie Consent. It checks one pre-consent request list but never
   asserts absence of the GA script or analytics cookies, despite the explicit requirement at
   `.copilot-tracking/research/subagents/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:416-419`.
   The source wiring is plausible, but the required end-to-end privacy behavior remains unproven.

### Minor

1. The off-site embed limitation is recorded in the security review and as a source comment, but not
   in the runbook as research requested. Evidence appears at
   `docs/review/data-observatory-relaunch/security-review.md:93-102` and
   `layouts/embeds/baseof.html:20`; `docs/data-observatory-runbook.md` has no corresponding
   cross-origin consent limitation. This is a documentation placement gap, while the larger SEC-02
   acceptance decision remains explicitly open.

## Coverage Assessment

Status: **Partial**.

Both Phase 6 implementation steps exist in the current pull request, and static inspection supports
the bounded, opt-in design. Step 6.1 is implementation-complete but runtime-acceptance incomplete.
Step 6.2 is implementation-complete except for the requested runbook placement, but its browser
privacy contract is incomplete and not wired into CI. No Critical functionality gap was found.

Repository implementation and external acceptance must remain distinct:

* Repository implementation: Substantially complete
* Repository automated acceptance: Incomplete
* Production GA4 acceptance: Not established
* Cross-origin embed privacy acceptance: Open under SEC-02

## Clarifying Questions

1. Should embedded endpoints omit analytics entirely, or should Amy and Hermes approve an explicit
   referrer and cross-origin consent policy for SEC-02?

## Recommended Next Validations

* [ ] Add `tests/visual/observatory-analytics.spec.mjs` to the blocking CI Playwright command and retain the run artifact
* [ ] Exercise Cookie Consent accept, withdraw, and persisted/reload states without calling the analytics adapter directly
* [ ] Assert no GA script, GA cookie, data-layer event, or analytics network request before consent
* [ ] Assert post-consent events and post-withdrawal suppression against the real Cookie Consent integration
* [ ] Resolve SEC-02, document the selected embed privacy behavior in the runbook, and add its browser contract
* [ ] Capture the current pull request URL and successful status checks; remote PR metadata was unavailable in this session
* [ ] Retain production GA4 Realtime and consent-denied network evidence as external acceptance, separate from repository test results
