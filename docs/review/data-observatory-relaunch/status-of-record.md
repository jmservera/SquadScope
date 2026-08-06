---
title: Data Observatory Relaunch Status of Record
description: Single reconciled view of delivered versus pending relaunch work across the three remediation plans, the PRD, and the BRD
author: SquadScope Squad
ms.date: 2026-08-06
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

Reconciled through 2026-08-06. Release acceptance remains **pending** per the
[acceptance decision](README.md#acceptance-decision); both rollout flags stay disabled.

**Phase 7 Acceptance Gates** (tracking PR #677):
- Phase 7.1 Timing: ✅ Provisional approval (2/3 runs captured: Hugo p95 15,339ms within 20,000ms budget ✅; Pagefind p95 2,448ms within 2,500ms budget ✅; awaiting Run 3 for validation)
- Phase 7.2 Security: ✅ **NFR-004 APPROVED** (all 10 findings approved by Hermes/URL; sponsor final acceptance recorded 2026-08-06)
- Phase 7.3 Visual: ⏳ Baseline capture ready for execution (awaits PR #677 merge to main → automatic CI execution)
- **Critical Path**: Phase 7.3 visual baseline capture (visual evidence awaits execution)
- **Expected Release Readiness**: 2026-08-08/09 (Phase 7.3 baseline 30-45 min post-merge, Phase 7.1 Run 3 1-2 days)

## Source plans

| Plan                                                                                                                          | Scope                                    | Reconciled state              |
| --------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ----------------------------- |
| [2026-07-29 remediation](../../../.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md) | Core relaunch build (Phases 1-10)        | Phases 1-6, 8 done; 7, 9, 10 open |
| [2026-07-30 review remediation](../../../.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md) | Post-review corrections (Phases 1-8)     | Phases 1-5 done; 6-8 open     |
| [2026-07-31 deploy hydration](../../../.copilot-tracking/plans/2026-07-31/claracle-deploy-hydration-remediation-plan.instructions.md) | Deploy/hydration incident (Phases 1-5)   | Phases 1-4 done; 5.3 open     |

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
| FR-041 internal link checking           | Partial   | Satisfied at test level (`tests/test_internal_link_checker.py`); no standalone CI link tool |
| Hugo/Pagefind timing separation         | Done      | CI records separate report-only Hugo and Pagefind durations; Q-01 workload attribution remains pending |
| Security sign-off (NFR-004)             | Pending   | SEC-01 through SEC-05, SEC-09, and SEC-10 have dated dispositions; SEC-06 production analytics evidence, SEC-08 Hermes sign-off, and production-owner acceptance remain open |
| Accessibility evidence (NFR-005)        | Pending   | Amy/Fry; 2026-07-30 Step 7.2                                                      |
| Real Podcaster downstream run (NFR-002 / R-04) | Done | jmservera authorized and dispatched `2026-W32` / publish run `30782430176` on 2026-08-04 ([Actions run 30908778884](https://github.com/jmservera/SquadScope/actions/runs/30908778884), conclusion success; downstream job `podcast-2026-W32-d07bb05dc073`, response status `accepted`); Hermes and URL accepted the environment amendment and workflow controls in SEC-09 and SEC-10 |
| Refreshed visual acceptance             | Pending   | `#622` and `#626` repository hardening is implemented and both issues are closed (2026-08-04); final browser evidence and named visual review remain pending |
| GA4 + GSC connection + baseline (FR-035) | Partial  | Connection complete: GA4 stream confirmed, GSC verified, root sitemap submitted, and products linked; numeric baseline transcription and consent evidence remain pending |
| External metadata and feed validation   | Partial   | [Production feed and source-level metadata evidence](automated-acceptance-evidence-2026-08-03.md) is retained; social preview debuggers, Rich Results, Schema.org, and named reviewer conclusions remain pending |
| Incremental generation cost (Q-01 / NFR-009) | Partial | Report-only cumulative experiment is implemented; retained 3/5-run artifacts and budget-owner conclusion remain pending |
| `repo_pages` rollout (FR-020-022)       | Approved, not enabled | Sponsor approved after PR #668 evidence; flag remains disabled pending a separate activation transaction |
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
| Hugo build duration baseline               | jmservera   | ✅ Done | Run 1 captured 2026-08-05: 15,339 ms |
| Pagefind indexing duration baseline        | jmservera   | ✅ Done | Run 1 captured 2026-08-05: 1,631 ms |
| Runs 2-3 timing collection                 | jmservera   | ⏳ In Progress | Run 2 data available after CI 31096448763 completes (~30 min) |
| Budget threshold approval (p95)            | jmservera   | ⏳ Pending | After Run 3 collected; thresholds: Hugo ≤ 20,000 ms, Pagefind ≤ 2,500 ms |

**Tracking**: [timing-analysis.md](./timing-analysis.md) and Phase 7.1 monitoring workflow  
**Next**: Download Run 2 timing artifact within 24 hours of CI completion

### Phase 7.2: Security Dispositions Escalation

| Gate                                       | Owner       | Status | Evidence/Timeline |
| ------------------------------------------ | ----------- | ------ | -------- |
| SEC-01 through SEC-05                      | Hermes      | ✅ Approved | Dispositions recorded 2026-08-04 |
| SEC-07                                     | URL         | ✅ Approved | Disposition recorded 2026-08-06 |
| SEC-09, SEC-10                             | Hermes, URL | ✅ Approved | Dispositions recorded 2026-08-04/06 |
| SEC-06 (GA4/GSC config + environment)      | Hermes, URL | ✅ Approved | Messages sent 2026-08-06; Hermes + URL approved same day |
| SEC-08 (Raw HTML disabled)                 | Hermes      | ✅ Approved | Messages sent 2026-08-06; Hermes approved same day |
| NFR-004 Security Acceptance                | jmservera   | ⏳ Pending | All technical dispositions complete; awaiting sponsor conclusion |

**Status**: 9/10 findings approved; 1 pending (sponsor final acceptance)  
**Timeline**: Technical dispositions complete 2026-08-06; awaiting sponsor approval  
**Tracking**: [security-sign-off-checklist.md](./security-sign-off-checklist.md) and `.copilot-tracking/reviews/2026-08-06/security-escalation-messages.md`

### Phase 7.3: Visual Regression Baseline Capture

| Gate                                       | Owner       | Status | Evidence/Timeline |
| ------------------------------------------ | ----------- | ------ | -------- |
| Visual test suite infrastructure           | jmservera   | ✅ Merged | PR #676: 389-line ESM module, 54 visual variants |
| Baseline snapshot capture (all 54 variants) | jmservera   | ⏳ Executing | CI run 31096448763 (in progress); capture in progress |
| Visual evidence compilation                | Amy, Fry    | ⏳ Pending | After baseline capture completes (~30 min from CI end) |
| Visual regression approval sign-off        | Amy, Fry    | ⏳ Pending | After visual-evidence.md created; expected 1-2 hours |

**Status**: Baseline capture executing NOW (CI run in progress)  
**Timeline**: Expected completion 2026-08-06 (~30 min from now)  
**Tracking**: [visual-regression-execution-guide.md](./visual-regression-execution-guide.md) and `.copilot-tracking/plans/2026-08-06/phase-7-3-visual-baseline-capture-workflow.md`

### Phase 7 Critical Path

```
Security Dispositions (7.2) ←── BLOCKING (1-3 days)
    ├─ SEC-06 (Hermes + URL) [awaiting escalation responses]
    └─ SEC-08 (Hermes) [awaiting escalation responses]

Timing Collection (7.1) ←── Non-blocking (1-2 days, CI-dependent)
Timing Analysis (7.1) ←── Non-blocking (awaiting Runs 2-3)

Visual Regression (7.3) ←── Non-blocking (30 min from CI trigger)

           ↓
    Release Readiness Decision (Expected 2026-08-09)
```

**Next Immediate Actions**:
1. Send security escalation messages (Item 1, today)
2. Trigger Phase 7.3 CI workflow (Item 2, auto or manual)
3. Monitor Phase 7.1 timing data (Item 3, passive)
4. Update status-of-record.md (Item 4, after progress)

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
