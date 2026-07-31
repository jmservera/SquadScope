---
title: Claracle Data Observatory Relaunch Remediation Phase 9 Validation
description: RPI validation of Phase 9 documentation and acceptance evidence
author: GitHub Copilot
ms.date: 2026-07-30
ms.topic: reference
---

## Validation Scope

Status: Partial

This validation compares Phase 9 of the remediation plan with the changes log,
primary research, and current repository evidence. Repository implementation and
external acceptance are assessed separately.

The research explicitly states that repository inspection cannot prove GSC ownership,
sitemap submission, GA4 Realtime receipt, debugger results, Hermes sign-off, or a
downstream Podcaster acceptance
(`.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:50-52`).
No such result is inferred in this validation.

## Phase 9 Requirements

Phase 9 contains four steps
(`.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:408-471`):

1. Record an actionable Observatory runbook and an auditable Star Velocity Explorer
	 architecture decision.
2. Document the complete security surface, assign findings and dispositions, and obtain
	 Hermes sign-off before accepting NFR-004.
3. Retain dated external evidence for GSC, GA4, social previews, structured-data tools,
	 production sitemap and feeds, Podcaster, and accessibility review.
4. Replace deficient visuals, reconcile PRD and BRD status, and enable each rollout flag
	 only through a separate approved change.

The plan checklist records only Step 9.1 as complete and leaves Steps 9.2 through 9.4
open
(`.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md:229-239`).
This is consistent with the current evidence.

## Plan-to-Changes Comparison

| Plan item | Changes-log claim | Verified status | Assessment |
|-----------|-------------------|-----------------|------------|
| Step 9.1: Runbook and ADR | MAJ-07 and MIN-02 are complete (`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:28`, `:36`) | Complete | The runbook covers owners, escalation, generation order, flags, lifecycle overrides, freshness, recovery, and rollback (`docs/data-observatory-runbook.md:20-45`, `:64-133`, `:151-184`). The ADR compares discoverability, effort, static-hosting fit, alternatives, and consequences (`docs/decisions/adr-star-velocity-explorer.md:22-67`). |
| Step 9.2: Security review and sign-off | Review documented; Hermes and URL sign-off pending (`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:31`) | Partial | The review covers the planned surfaces and assigns owners, but SEC-01 through SEC-06 remain open or conditional and all three sign-off rows are pending (`docs/review/data-observatory-relaunch/security-review.md:140-169`). |
| Step 9.3: External launch evidence | External checks remain pending (`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:35`, `:208`) | Not complete | The evidence index has the required slots, but all 13 external gates are pending (`docs/review/data-observatory-relaunch/README.md:48-63`). The GA4/GSC record contains no captured values (`docs/growth/ga4-gsc-baseline-2026-07-29.md:46-69`). |
| Step 9.4: Status and visuals | Status claims corrected; refreshed evidence and sponsor acceptance pending (`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:33`, `:37`) | Partial | PRD and BRD status are honest, and both flags remain off. The ten images are historical, not accepted replacements, and no sponsor approval is recorded (`docs/review/data-observatory-relaunch/README.md:67-74`, `docs/brds/claracle-data-observatory-relaunch-brd.md:14-25`). |

## Verified Repository Evidence

### Operational and design evidence

The repository contains both required Step 9.1 documents. The runbook names operational
owners and escalation routes (`docs/data-observatory-runbook.md:29-45`) and documents
non-destructive flag rollback (`docs/data-observatory-runbook.md:165-177`). The ADR records
the selected client-side tool and rejected alternatives
(`docs/decisions/adr-star-velocity-explorer.md:30-58`). Step 9.1 is complete from repository
evidence.

### Security evidence

The security review is substantive repository evidence, but it is not acceptance. It
states that Hermes review is pending (`docs/review/data-observatory-relaunch/security-review.md:17-19`).
SEC-01 is a high-severity repository implementation gap because candidate titles still
bypass the standard sanitizer; the review requires sanitization and adversarial tests
before rollout (`docs/review/data-observatory-relaunch/security-review.md:140`). SEC-02
through SEC-06 also require dispositions or external verification
(`docs/review/data-observatory-relaunch/security-review.md:141-145`). Hermes, URL, and
jmservera have no recorded dates or approvals
(`docs/review/data-observatory-relaunch/security-review.md:165-169`).

### Platform evidence

Repository wiring is documented, but no platform acceptance is present. The GA4/GSC
matrix marks all eight checks pending and every baseline metric not captured
(`docs/growth/ga4-gsc-baseline-2026-07-29.md:46-69`). The broader acceptance matrix also
marks social preview, Rich Results, Schema.org, production responses, Podcaster, and
accessibility checks pending (`docs/review/data-observatory-relaunch/README.md:48-63`). A
workspace documentation search found no dated successful observation or retained external
result that supersedes those statuses.

### Visual evidence

The screenshot checklist says the existing files were not refreshed, the topic image has
zero recent weekly issues, and four relevant captures are obscured by the cookie banner
(`docs/review/data-observatory-relaunch/screenshots/README.md:17-21`). Direct inspection
confirmed these defects in:

* `docs/review/data-observatory-relaunch/screenshots/03-topic-hub-mcp.png`
* `docs/review/data-observatory-relaunch/screenshots/04-repo-ollama.png`
* `docs/review/data-observatory-relaunch/screenshots/08-star-velocity-tool.png`
* `docs/review/data-observatory-relaunch/screenshots/10-internal-linking-block.png`

The required desktop, mobile, dark-theme, interaction, and unobscured replacement matrix
is documented but has no accepted capture set
(`docs/review/data-observatory-relaunch/screenshots/README.md:39-55`).

### Sponsor and rollout evidence

The PRD reports acceptance pending and both flags off without rollout approval
(`docs/prds/claracle-data-observatory-relaunch.md:10-26`, `:250-262`). The BRD states that
requirements are approved as requirements, but no artifact records sponsor approval for
either flag (`docs/brds/claracle-data-observatory-relaunch-brd.md:14-25`). Current
configuration confirms `repo_pages.enabled = false` and
`topic_hubs.dynamic_creation.enabled = false` (`config/observatory.toml:1-2`, `:18-19`).
This is correct containment, not completed external acceptance.

## Findings

### Critical: Security acceptance and rollout-blocking remediation are incomplete

Step 9.2 requires findings, dispositions, and Hermes sign-off. The review contains an open
high-severity sanitizer gap plus unresolved privacy, publication-policy, lifecycle, and
secret-verification findings. No Hermes or URL sign-off is recorded. Repository work is
still required for SEC-01 through SEC-03, while Hermes and URL acceptance remains external.
NFR-004 must remain pending.

Evidence: `docs/review/data-observatory-relaunch/security-review.md:140-169`.

### Critical: Required external platform acceptance evidence is absent

Step 9.3 requires dated observations, values, actors, and retained links. All 13 gates in
the acceptance matrix are pending, and all GA4/GSC baseline values are uncaptured. This is
an external acceptance gap, not proof that repository wiring is incorrect. FR-035,
NFR-007, the external portion of NFR-008, and release acceptance remain open.

Evidence: `docs/review/data-observatory-relaunch/README.md:48-63` and
`docs/growth/ga4-gsc-baseline-2026-07-29.md:46-69`.

### Critical: Sponsor approval is absent for both rollout controls

No dated sponsor approval identifies either rollout flag, and both controls remain off.
This is the correct repository state until security, lifecycle, and acceptance evidence is
complete, but Step 9.4 and relaunch acceptance cannot pass without two separate approvals.

Evidence: `docs/brds/claracle-data-observatory-relaunch-brd.md:14-25`,
`docs/review/data-observatory-relaunch/README.md:63`, and
`config/observatory.toml:1-2`, `:18-19`.

### Major: Visual evidence does not satisfy the required capture matrix

The checked-in captures are historical and cannot support Phase 9 visual acceptance. The
topic capture contradicts the required populated state, representative feature captures
are obscured, and mobile, dark-theme, revision, viewport, and interaction metadata are not
retained. Status documentation correctly disclaims these files, so this is an evidence gap
rather than an unsupported acceptance claim.

Evidence: `docs/review/data-observatory-relaunch/screenshots/README.md:17-55` and the four
directly inspected PNG files listed above.

## Coverage Assessment

Phase 9 is partially implemented:

* One of four steps is complete: Step 9.1
* Two of four steps are partial: Steps 9.2 and 9.4
* One of four steps is not complete: Step 9.3
* Zero of three security and release sign-off rows are complete
* Zero of 13 external acceptance matrix gates are complete
* Zero accepted refreshed visual sets are present
* Zero of two rollout flags has sponsor approval; both correctly remain disabled

Repository documentation coverage is strong and status reconciliation is accurate. The
phase cannot pass because required security remediation and sign-off, external platform
observations, refreshed visual evidence, accessibility review, and sponsor approval are
not present. The changes log accurately identifies these boundaries
(`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:201-208`).

## Clarifying Questions

* Which approved evidence location should retain redacted GA4, GSC, debugger, accessibility,
	and production-response artifacts?
* Which deployed revision should external reviewers use for platform, visual, and Podcaster
	acceptance?
* Who will record the dated accessibility conclusion alongside Fry's automated results?

## Recommended Next Validations

* Remediate SEC-01 through SEC-03, rerun focused security tests, and obtain dated Hermes and
	URL dispositions for SEC-01 through SEC-06
* Execute the GA4 consent-denied, consent-granted, and Realtime checks, then capture GSC
	verification, sitemap submission, and baseline values
* Retain dated production sitemap/feed, social preview, Rich Results, and Schema.org results
* Execute and link the protected exact-release Podcaster run
* Run the automated, keyboard, and screen-reader accessibility review on the selected revision
* Replace the historical screenshots with the complete populated and unobscured capture matrix
* Obtain separate dated sponsor approval for dynamic topic creation and repository-page creation
* Revalidate Phase 9 after the evidence index, security sign-off table, PRD, and BRD are updated