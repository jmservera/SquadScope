---
title: Data Observatory Relaunch Status of Record
description: Single reconciled view of delivered versus pending relaunch work across the three remediation plans, the PRD, and the BRD
author: SquadScope Squad
ms.date: 2026-08-02
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

Reconciled on 2026-08-02. Release acceptance remains **pending** per the
[acceptance decision](README.md#acceptance-decision); both rollout flags stay disabled.

## Source plans

| Plan                                                                                                                          | Scope                                    | Reconciled state              |
| --------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ----------------------------- |
| [2026-07-29 remediation](../../../.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md) | Core relaunch build (Phases 1-10)        | Phases 1-6, 8 done; 7, 9, 10 open |
| [2026-07-30 review remediation](../../../.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md) | Post-review corrections (Phases 1-8)     | Phases 1-5 done; 6-8 open     |
| [2026-07-31 deploy hydration](../../../.copilot-tracking/plans/2026-07-31/claracle-deploy-hydration-remediation-plan.instructions.md) | Deploy/hydration incident (Phases 1-5)   | Phases 1-4 done; 5.3 open     |

## Delivered since the plans were written

| Workstream                              | Evidence (merged)                                                | Requirement trace          |
| --------------------------------------- | ---------------------------------------------------------------- | -------------------------- |
| Deploy stopped hydrating empty `content/data` | `#627` → `#628` (interim Path B)                            | NFR-011                    |
| Publish commit stages only existing generated paths | `#634`                                                   | NFR-011, provenance        |
| Safe hydration guard generalized; `content/data` deploy restored | `#633` → `#637`                                 | NFR-011, NFR-012, R-08     |
| Embed `source_page` validation before build (CI guard) | `scripts/check_embed_sources.py`, `tests/test_embed_sources.py`, wired in `ci.yml` (`#641`) | NFR-011, NFR-012 |
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
| Atomic publish transaction              | Done      | 2026-07-29 Phase 4; restore integrity hardened by `#640`/`#646`                  |
| SEO / rendered link contracts           | Done      | 2026-07-29 Phase 5                                                                |
| Consent-gated analytics API             | Done      | 2026-07-29 Phase 6                                                                |
| Deploy / hydration parity + CI guard    | Done      | 2026-07-31 Phases 1-4 (`#628`/`#634`/`#637`/`#641`)                              |
| Podcaster release smoke (dry-run gate)  | Done      | Blocking post-deploy gate green (`#636`/`#639`/`#643`/`#645`)                    |
| FR-041 internal link checking           | Partial   | Satisfied at test level (`tests/test_internal_link_checker.py`); no standalone CI link tool |
| Hugo/Pagefind timing separation         | Pending   | 2026-07-29 Step 7.3                                                               |
| Security sign-off (NFR-004)             | Pending   | Hermes; 2026-07-29 Step 9.2 / 2026-07-30 Step 7.1                                |
| Accessibility evidence (NFR-005)        | Pending   | Amy/Fry; 2026-07-30 Step 7.2                                                      |
| Real Podcaster downstream run (NFR-002 / R-04) | Pending | Protected environment; 2026-07-30 Step 6.3                                    |
| Refreshed visual acceptance             | Pending   | Screenshot capture checklist                                                      |
| GA4 + GSC connection + baseline (FR-035) | Pending  | `#599` is closed, but its human-action checklist remains; `ga_measurement_id` is empty |
| Incremental generation cost (Q-01 / NFR-009) | Pending | Design spike required                                                          |
| `repo_pages` rollout (FR-020-022)       | Deferred  | Flag disabled; needs sponsor approval + own plan                                 |
| `dynamic_topic_creation` rollout (FR-004) | Deferred | Flag disabled; needs sponsor approval + own plan                                |
| Sponsor rollout approval                | Pending   | jmservera; see [launch-gate register](#launch-gate-register)                     |

## Epic issue dispositions

| Issue                                             | Title                                       | Disposition                                                        |
| ------------------------------------------------- | ------------------------------------------- | ----------------------------------------------------------------- |
| [#594](https://github.com/jmservera/SquadScope/issues/594) | Epic: Claracle Data Observatory Relaunch | Open — tracks overall relaunch                                    |
| [#644](https://github.com/jmservera/SquadScope/issues/644) | Deploy Hugo site failed (run 30718600607) | CLOSED — resolved by `#645`/`#646`                                |
| [#626](https://github.com/jmservera/SquadScope/issues/626) | Lighthouse / performance quality-gate follow-ups | Readiness scope — see gate register                        |
| [#622](https://github.com/jmservera/SquadScope/issues/622) | Post-review UX polish                    | Readiness scope — see gate register                               |
| [#599](https://github.com/jmservera/SquadScope/issues/599) | Connect GA4 + Google Search Console (FR-035) | Closed as completed on 2026-08-01; the recorded human actions remain a pending launch gate |

## Launch-gate register

Each gate lists its owner, blocking dependency, and the evidence path that closes it.
The external acceptance matrix in the [acceptance evidence index](README.md#external-acceptance-matrix)
holds the platform-level rows; this register adds ownership and sequencing.

| Gate                                       | Owner       | Dependency                                   | Evidence path                                                        |
| ------------------------------------------ | ----------- | -------------------------------------------- | ------------------------------------------------------------------- |
| GA4 + GSC connection + dated baseline (FR-035; `#599` closed with human actions outstanding) | jmservera | Platform access; blocks OBJ-2/OBJ-4 baselines | [Dated baseline](../../growth/ga4-gsc-baseline-2026-07-29.md) |
| Security sign-off (NFR-004)                | Hermes      | Security review disposition                  | [Security review](security-review.md)                               |
| Accessibility evidence (NFR-005)           | Amy / Fry   | Production browser access                    | Accessibility review record                                         |
| Real Podcaster downstream run (NFR-002 / R-04) | URL     | Protected environment; passing deploy        | 2026-07-30 Step 6.3 evidence                                        |
| Refreshed visual acceptance                | Amy         | Populated content render                     | [Screenshot capture checklist](screenshots/README.md)               |
| Incremental generation cost (Q-01 / NFR-009) | URL       | Timing spike                                 | Design spike record                                                 |
| Lighthouse follow-ups (`#626`)             | Amy / Fry   | Performance budget                           | `#626`                                                              |
| Post-review UX polish (`#622`)             | Amy         | None                                         | `#622`                                                              |
| Sponsor rollout approval                   | jmservera   | All above gates                              | Dated approval identifying each flag separately                     |

## Deferred to separate plans

These are out of scope for the readiness reconciliation and each needs its own plan
(see the [reconciliation planning log](../../../.copilot-tracking/plans/logs/2026-08-02/claracle-relaunch-readiness-reconciliation-log.md#suggested-follow-on-work)):

- GA4 + GSC connection implementation (FR-035; continue the human-action checklist recorded on closed issue `#599`)
- `repo_pages` rollout (requires sponsor approval)
- `dynamic_topic_creation` rollout (requires sponsor approval)
- Incremental-generation-cost design spike (Q-01 / NFR-009)
