---
title: Data Observatory Relaunch Status of Record
description: Single reconciled view of delivered versus pending relaunch work across the three remediation plans, the PRD, and the BRD
author: SquadScope Squad
ms.date: 2026-08-08
ms.topic: reference
keywords:
  - status of record
  - data observatory
  - relaunch readiness
  - reconciliation
estimated_reading_time: 7
---

## Purpose

This document is the single reconciled view of the Claracle Data Observatory
relaunch. It supersedes the fragmented checkbox state across the three remediation
plans by mapping each workstream to its delivered or pending status with evidence.
It complements the [acceptance evidence index](README.md), which owns the external
gate matrix and the acceptance decision.

- Epic: [#594](https://github.com/jmservera/SquadScope/issues/594)
- PRD: [claracle-data-observatory-relaunch.md](../../prds/claracle-data-observatory-relaunch.md)
- BRD: [claracle-data-observatory-relaunch-brd.md](../../brds/claracle-data-observatory-relaunch-brd.md)

Reconciled through 2026-08-08. Sponsor decision: **NO-GO / SUPERSEDED** at the
immutable visual-review revision `f37b49d`. The feature-complete relaunch did not
receive final release acceptance. Its evidence is frozen as the historical baseline,
and the remaining interaction and live assistive-technology findings carry forward to
BRD-CLARACLE-003. Both rollout flags stay disabled; repository-page activation is
cancelled in favor of the consolidated repository migration.

**Phase 7 Acceptance Gates** (tracking PR #677):
- Phase 7.1 Timing: ✅ **APPROVED 2026-08-08** — data collection complete (three production `main` runs; Hugo p95 3,058 ms, Pagefind p95 2,707 ms); jmservera accepted the revised thresholds (Hugo 6,000 / Pagefind 5,500 / total 11,500 ms) and the enforcement gate is live in `ci.yml`
- Phase 7.2 Security: ✅ **NFR-004 APPROVED** (all 10 findings approved by Hermes/URL; sponsor final acceptance recorded 2026-08-06)
- Phase 7.3 Visual: 🟡 Named review recorded 2026-08-08 — Amy accepts the rendered visual matrix (64 screenshots, `observatory-visual-regression.spec.mjs` 68/68 at `f37b49d`) and Fry accepts the automated a11y/analytics coverage; both dispositions carry residual manual steps (visual interaction-state captures; NFR-005 live screen-reader pass). See the [visual review handoff](visual-review-handoff-2026-08-07.md#disposition)
- **Historical acceptance disposition**: NO-GO / SUPERSEDED 2026-08-08; the open visual-interaction and NFR-005 live screen-reader findings are redesigned-release gates
- **Successor requirements**: [BRD-CLARACLE-003](../../brds/claracle-post-relaunch-consolidation-brd.md)

**Remaining human gates** (single release-readiness view; details in [owner-action-register.md](owner-action-register.md)):

| Gate | Owner(s) | Evidence path |
| ---- | -------- | ------------- |
| Timing budget approval | timing-budget owner, URL, jmservera | Approved 2026-08-08 and enforced in `ci.yml`; see [timing-analysis.md](timing-analysis.md#approval-chain) |
| Visual interaction captures | Amy, Fry | Carried forward to BRD-CLARACLE-003; see [visual review handoff](visual-review-handoff-2026-08-07.md) |
| Accessibility (NFR-005) live screen-reader review | Amy, Fry | Carried forward to BRD-CLARACLE-003; see [owner action register](owner-action-register.md#accessibility-acceptance) |
| Dynamic-topic canary (`local-first`) approval | Hermes, jmservera | [owner-action-register.md](owner-action-register.md#proposed-dynamic-topic-canary-2026-08-08) |
| Cost experiment dispatch (Q-01 / NFR-009) | URL, budget owner | [owner-action-register.md](owner-action-register.md#incremental-generation-cost-acceptance) |
| Dynamic activation transaction | jmservera | [owner-action-register.md](owner-action-register.md#sponsor-rollout-decision); repository-page activation is superseded and remains disabled |

Analytics and search (FR-035 / NFR-007 / NFR-008) closed 2026-08-08; the `local-first`
canary revision is staged (`allow_topics`, `enabled = false`) pending approval.

## Source plans

| Plan                                                                                                                          | Scope                                    | Reconciled state              |
| --------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ----------------------------- |
| [2026-07-29 remediation](../../../.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md) | Core relaunch build (Phases 1-10)        | Phases 1-8, 10 done; 9 open (external launch evidence + visual) |
| [2026-07-30 review remediation](../../../.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md) | Post-review corrections (Phases 1-8)     | Phases 1-6 done; 7-8 open (timing/visual/external human gates) |
| [2026-07-31 deploy hydration](../../../.copilot-tracking/plans/2026-07-31/claracle-deploy-hydration-remediation-plan.instructions.md) | Deploy/hydration incident (Phases 1-5)   | All phases done (5.3 reconciled 2026-08-07) |

## Delivered since the plans were written

| Workstream                              | Evidence (merged)                                                | Requirement trace          |
| --------------------------------------- | ---------------------------------------------------------------- | -------------------------- |
| Deploy stopped hydrating empty `content/data` | `#627` → `#628` (interim Path B), with follow-up provenance correction in `#632` | NFR-011                    |
| Publish commit stages only existing generated paths | `#634`                                                   | NFR-011, provenance        |
| Safe hydration guard generalized; `content/data` deploy restored | `#633` → `#637`                                 | NFR-011, NFR-012, R-08     |
| Embed `source_page` validation before build (CI guard) | `scripts/check_embed_sources.py`, `tests/test_embed_sources.py`, wired in `ci.yml` (`#641`) | NFR-012 |
| CI reproduces the deploy publish-hydration and validates the promotion record | `scripts/publish_hydration.py`, `tests/test_publish_hydration.py`, `publish-hydration-parity` job in `ci.yml` | NFR-011 |
| Embeddable-charts demo linked from the data landing page | `#642`                                            | FR-052                     |
| Podcaster smoke: API key passed to reusable workflow | `#636`                                                 | NFR-002                    |
| Podcaster smoke: tooling checked out from default branch | `#639` → `#643`                                    | NFR-002, R-04              |
| Podcaster smoke: hydrate source manifest referenced by promotion record | `#639` → `#645`                     | NFR-002, R-04              |
| Restore preserves the published weekly transaction | `#640` → `#646`                                          | NFR-002 (restore integrity) |
| Live deploy failure (run 30718600607) | `#644` CLOSED — root cause was a dangling `source_manifest.path` (`data/candidates/2026-W31/30669054860/publish-manifest.json`) breaking the Podcaster smoke gate; resolved by `#645`/`#646`; deploy-site green since 2026-08-01 | — |

## Requirement status summary

| Area                                    | Status    | Notes                                                                            |
| --------------------------------------- | --------- | -------------------------------------------------------------------------------- |
| Weekly topic through-line               | Done      | 2026-07-29 Phase 2                                                                |
| Repository lifecycle (identity, retention) | Done   | 2026-07-29 Phase 3                                                                |
| Atomic publish transaction              | Done      | [Run 31040602642](https://github.com/jmservera/SquadScope/actions/runs/31040602642) passed at `211f0974ce375e427591803cc3f3dfd39e169ead`; retained evidence proves one normal commit, no-op rerun, failure rollback, accepted-tree identity, and hydrated-tree identity |
| SEO / rendered link contracts           | Done      | 2026-07-29 Phase 5                                                                |
| Consent-gated analytics API             | Done      | 2026-07-29 Phase 6                                                                |
| Deploy / hydration parity + CI guard    | Done      | Deploy hydration is restored (`#628`/`#632`/`#634`/`#637`); the `#641` guard satisfies NFR-012 reference integrity; the `publish-hydration-parity` CI job reproduces the deploy publish-hydration and validates the promotion record (`scripts/publish_hydration.py`) for NFR-011 |
| Podcaster release smoke (dry-run gate)  | Done      | Blocking post-deploy gate green (`#636`/`#639`/`#643`/`#645`)                    |
| FR-041 internal link checking           | Done      | `.github/workflows/ci.yml` runs `scripts/check_internal_links.py public --base-url "https://claracle.com/"` in the `production-site` job, in addition to test-level coverage (`tests/test_internal_link_checker.py`); PRD R-03 reconciled Closed |
| Hugo/Pagefind timing separation         | Done      | CI records separate report-only Hugo and Pagefind durations; Q-01 workload attribution remains pending |
| Security sign-off (NFR-004)             | Done      | All ten findings SEC-01 through SEC-10 carry dated dispositions (2026-08-04 and 2026-08-06); sponsor (jmservera) acceptance recorded 2026-08-06 in `security-sign-off-checklist.md` |
| Accessibility evidence (NFR-005)        | Partial   | Fry accepted automated axe/keyboard/focus-trap/responsive coverage 2026-08-08 (a11y-perf passing locally at `f37b49d`; axe + keyboard via retained CI run 31160859598); live screen-reader (AT) pass remains outstanding — see [owner-action-register.md](owner-action-register.md#accessibility-acceptance) |
| Real Podcaster downstream run (NFR-002 / R-04) | Done | jmservera authorized and dispatched `2026-W32` / publish run `30782430176` on 2026-08-04 ([Actions run 30908778884](https://github.com/jmservera/SquadScope/actions/runs/30908778884), conclusion success; downstream job `podcast-2026-W32-d07bb05dc073`, response status `accepted`); Hermes and URL accepted the environment amendment and workflow controls in SEC-09 and SEC-10 |
| Refreshed visual acceptance             | Partial   | Amy accepted the rendered visual matrix 2026-08-08 (64 screenshots at `f37b49d`, `observatory-visual-regression.spec.mjs` 68/68); `#622`/`#626` hardening closed 2026-08-04; manual interaction-state captures remain the open step — see [visual-review-handoff-2026-08-07.md](visual-review-handoff-2026-08-07.md#disposition) |
| GA4 + GSC connection + baseline (FR-035) | Done     | Connection complete; numeric baseline transcribed 2026-08-08 (NFR-007: 51 GA4 sessions, 149 GSC impressions, 294 indexed pages); NFR-008 denied/granted production consent observations captured 2026-08-08 via private-session HAR |
| External metadata and feed validation   | Partial   | [Production feed and source-level metadata evidence](automated-acceptance-evidence-2026-08-03.md) is retained; social preview debuggers, Rich Results, Schema.org, and named reviewer conclusions remain pending |
| Incremental generation cost (Q-01 / NFR-009) | Partial | Report-only cumulative experiment is implemented; retained 3/5-run artifacts and budget-owner conclusion remain pending |
| `repo_pages` rollout (FR-020-022)       | Superseded, not enabled | Activation cancelled 2026-08-08 by BRD-CLARACLE-003 BR-003; identity, lifecycle, alias, and rollback evidence remains migration input |
| `dynamic_topic_creation` rollout (FR-004) | Approved in principle, not enabled | Security disposition and one approved canary remain required before activation |
| Sponsor rollout approval                | Done with conditions | Separate decisions recorded on 2026-08-05; see [owner action register](owner-action-register.md#sponsor-rollout-decision) |

## Epic issue dispositions

| Issue                                             | Title                                       | Disposition                                                        |
| ------------------------------------------------- | ------------------------------------------- | ----------------------------------------------------------------- |
| [#594](https://github.com/jmservera/SquadScope/issues/594) | Epic: Claracle Data Observatory Relaunch | Open — tracks overall relaunch                                    |
| [#644](https://github.com/jmservera/SquadScope/issues/644) | Deploy Hugo site failed (run 30718600607) | CLOSED — resolved by `#645`/`#646`                                |
| [#626](https://github.com/jmservera/SquadScope/issues/626) | Lighthouse / performance quality-gate follow-ups | CLOSED — repository hardening completed 2026-08-04; final visual acceptance remains separate |
| [#622](https://github.com/jmservera/SquadScope/issues/622) | Post-review UX polish                    | CLOSED — repository work completed 2026-08-04; final visual acceptance remains separate |
| [#599](https://github.com/jmservera/SquadScope/issues/599) | Connect GA4 + Google Search Console (FR-035) | Closed; owner confirmed GA4, GSC verification, sitemap submission, and product link on 2026-08-02 |

## Phase 7 Acceptance Gates

Phase 7 consolidates final acceptance evidence and execution workflows across three parallel tracks (timing, security, visual). All work documented in PR #677 with execution planned for 2026-08-06 through 2026-08-09.

### Phase 7.1: Timing Evidence Collection

| Gate                                       | Owner       | Status | Evidence/Timeline |
| ------------------------------------------ | ----------- | ------ | -------- |
| Hugo build duration baseline               | jmservera   | ✅ Done | Run 1 (`31039618366`, 2026-08-05): 2,822 ms |
| Pagefind indexing duration baseline        | jmservera   | ✅ Done | Run 1 (`31039618366`, 2026-08-05): 2,707 ms |
| Runs 2-3 timing collection                 | jmservera   | ✅ Done | Run 2 (`31079871801`) and Run 3 (`31081291997`), both production `main` builds, transcribed from retained artifacts |
| Median and p95 calculation                 | jmservera   | ✅ Done | Hugo median 2,822 ms / p95 3,058 ms; Pagefind median 2,316 ms / p95 2,707 ms |
| Budget threshold approval (p95)            | jmservera   | ✅ Approved | Approved 2026-08-08: Hugo ≤ 6,000 ms, Pagefind ≤ 5,500 ms, total ≤ 11,500 ms; enforcement is live in `ci.yml` |

**Correction (2026-08-06)**: The previously recorded Run 1 figures (Hugo 15,339 ms, Pagefind 1,631 ms) did not match the retained `build-timing.json` artifact, and the previously recorded Run 2 was a `pull_request` build rather than a production `main` build. Both are corrected in [timing-analysis.md](./timing-analysis.md), and the provisional approval that depended on them is withdrawn.

**Tracking**: [timing-analysis.md](./timing-analysis.md)  
**Next**: No timing approval action remains; retain enforcement and evidence.

### Phase 7.2: Security Dispositions Escalation

| Gate                                       | Owner       | Status | Evidence/Timeline |
| ------------------------------------------ | ----------- | ------ | -------- |
| SEC-01 through SEC-05                      | Hermes      | ✅ Approved | Dispositions recorded 2026-08-04 |
| SEC-07                                     | URL         | ✅ Approved | Disposition recorded 2026-08-06 |
| SEC-09, SEC-10                             | Hermes, URL | ✅ Approved | Dispositions recorded 2026-08-04/06 |
| SEC-06 (GA4/GSC config + environment)      | Hermes, URL | ✅ Approved | Messages sent 2026-08-06; Hermes + URL approved same day |
| SEC-08 (Raw HTML disabled)                 | Hermes      | ✅ Approved | Messages sent 2026-08-06; Hermes approved same day |
| NFR-004 Security Acceptance                | jmservera   | ✅ Approved | Sponsor acceptance recorded 2026-08-06; all technical dispositions complete |

**Status**: 10/10 findings approved; NFR-004 sponsor acceptance recorded 2026-08-06  
**Timeline**: Technical dispositions complete 2026-08-06; sponsor approval recorded 2026-08-06  
**Tracking**: [security-sign-off-checklist.md](./security-sign-off-checklist.md) and `.copilot-tracking/reviews/2026-08-06/security-escalation-messages.md`

### Phase 7.3: Visual Regression Baseline Capture

| Gate                                       | Owner       | Status | Evidence/Timeline |
| ------------------------------------------ | ----------- | ------ | -------- |
| Visual test suite infrastructure           | jmservera   | ✅ Merged | Suite resolves its route matrix from the built `sitemap.xml`, so dated weekly and monthly editions no longer rot |
| Gate and evidence capture wired into CI    | jmservera   | ✅ Done | `ci.yml` runs the suite after the a11y and analytics gates, then builds a review index; both steps run unless the job is cancelled, so evidence survives an earlier gate failure. Output uploads under `screenshots/visual-regression/` in the `production-quality-reports` artifact. Confirmed producing 64 screenshots plus `index.html` in [run 31160859598](https://github.com/jmservera/SquadScope/actions/runs/31160859598) |
| Evidence matrix coverage                   | jmservera   | ✅ Done | 15 routes plus a consent capture x 4 projects (desktop/mobile x light/dark) = 64 screenshots plus per-project `metadata.json` tagged with revision, branch, run ID, viewport, and Playwright version |
| Visual evidence compilation                | Amy, Fry    | 🟡 Recorded 2026-08-08 | Amy accepted the rendered matrix (64 screenshots at `f37b49d`); interaction-state captures remain manual. See [handoff disposition](visual-review-handoff-2026-08-07.md#disposition) |
| Visual regression approval sign-off        | Amy, Fry    | 🟡 Recorded 2026-08-08 | Accept on rendered evidence + automated a11y/analytics coverage; residual = visual interaction captures and NFR-005 live screen-reader pass |

**Status**: The gate passes and the evidence matrix is produced automatically; the rendered matrix received named review, while manual interaction and live assistive-technology findings carry into BRD-CLARACLE-003
**Note**: The suite is a blocking gate as well as the evidence producer. It asserts route status, breadcrumb structure, and absence of horizontal overflow, resolves the consent banner before every feature capture, and writes the revision-tagged matrix. It does not perform pixel-diff comparison against committed baselines; regression detection is by named review of the per-revision matrix.  
**Tracking**: [visual-regression-execution-guide.md](./visual-regression-execution-guide.md) and [2026-08-07 visual review handoff](./visual-review-handoff-2026-08-07.md)

### Phase 7 Critical Path

```
Security Dispositions (7.2) ←── ✅ CLEARED (NFR-004 approved 2026-08-06)
    ├─ SEC-06 (Hermes + URL) [approved 2026-08-06]
    └─ SEC-08 (Hermes) [approved 2026-08-06]

Timing Collection (7.1)  ←── ✅ CLEARED (3 production main runs transcribed)
Timing Approval  (7.1)   ←── ✅ APPROVED 2026-08-08 (jmservera; enforced in ci.yml)

Visual Capture   (7.3)   ←── ✅ CLEARED (automated in ci.yml, artifact-retained)
Visual Review    (7.3)   ←── 🟡 RECORDED 2026-08-08 (Amy accept rendered matrix; interaction captures remain)
Accessibility    (NFR-005) ←─ 🟡 RECORDED 2026-08-08 (Fry accept automated coverage; live screen-reader pass remains)

              ↓
            Historical Decision: NO-GO / SUPERSEDED 2026-08-08
            Open findings carried to BRD-CLARACLE-003
```

**Next Immediate Actions**:

1. Preserve the accepted timing and historical visual evidence against revision `f37b49d`.
2. Carry the manual interaction and live screen-reader findings into the redesigned-release acceptance plan.
3. Keep repository-page generation disabled and use its retained evidence for BR-003 migration planning.

## Launch-gate register

Each gate lists its owner, blocking dependency, and the evidence path that closes it.
The external acceptance matrix in the [acceptance evidence index](README.md#external-acceptance-matrix)
holds the platform-level rows; this register adds ownership and sequencing.

| Gate                                       | Owner       | Dependency                                   | Evidence path                                                        |
| ------------------------------------------ | ----------- | -------------------------------------------- | ------------------------------------------------------------------- |
| GA4 + GSC dated baseline and consent evidence (FR-035/NFR-007/008) | jmservera | Transcribe supplied export and retain production consent observations | [Dated baseline](../../growth/ga4-gsc-baseline-2026-07-29.md) |
| Security sign-off (NFR-004)                | Hermes      | Security review disposition                  | [Security review](security-review.md)                               |
| Accessibility evidence (NFR-005)           | Amy / Fry   | Production browser and assistive technology  | [Owner action register](owner-action-register.md#accessibility-acceptance) |
| Real Podcaster downstream run (NFR-002 / R-04) | URL     | Complete: protected run and reviewer dispositions retained | [Owner action register](owner-action-register.md#protected-real-podcaster-run) |
| Refreshed visual acceptance                | Amy         | Populated content render                     | [Screenshot capture checklist](screenshots/README.md)               |
| External metadata and feed validation      | Amy / jmservera | External debugger and production access   | [Owner action register](owner-action-register.md#external-metadata-and-feed-validation) |
| Incremental generation cost (Q-01 / NFR-009) | URL       | Dispatch immutable workload variants and obtain budget-owner review | [Owner action register](owner-action-register.md#incremental-generation-cost-acceptance) |
| Lighthouse follow-ups (`#626`)             | Amy / Fry   | None; independent hardening                  | `#626`                                                              |
| Post-review UX polish (`#622`)             | Amy         | None; non-blocking                           | `#622`                                                              |
| Sponsor rollout approval                   | jmservera   | Complete with flag-specific conditions        | [Owner action register](owner-action-register.md#sponsor-rollout-decision) |

## Deferred to separate plans

These are out of scope for the readiness reconciliation and each needs its own plan
(see the [reconciliation planning log](../../../.copilot-tracking/plans/logs/2026-08-02/claracle-relaunch-readiness-reconciliation-log.md#suggested-follow-on-work)):

- GA4/GSC baseline transcription and production consent evidence (connection and sitemap submission are complete)
- [`repo_pages` rollout](../../../.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md) (requires identity, lifecycle, security, and sponsor approval)
- [`dynamic_topic_creation` rollout](../../../.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md) (requires preview, canary, security, and sponsor approval)
- [Incremental-generation-cost experiment](../../../.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md) (Q-01 / NFR-009)
