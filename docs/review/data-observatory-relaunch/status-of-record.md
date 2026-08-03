---
title: Data Observatory Relaunch Status of Record
description: Single reconciled view of delivered versus pending relaunch work across the three remediation plans, the PRD, and the BRD
author: SquadScope Squad
ms.date: 2026-08-03
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

Reconciled through 2026-08-03. Release acceptance remains **pending** per the
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
| Atomic publish transaction              | Partial   | Isolated local-remote proof passes normal-run, identical-rerun, injected-failure, unchanged-branch, accepted-tree, and hydrated-tree scenarios; retained manual workflow artifact and reviewer conclusion remain pending |
| SEO / rendered link contracts           | Done      | 2026-07-29 Phase 5                                                                |
| Consent-gated analytics API             | Done      | 2026-07-29 Phase 6                                                                |
| Deploy / hydration parity + CI guard    | Done      | Deploy hydration is restored (`#628`/`#632`/`#634`/`#637`); the `#641` guard satisfies NFR-012 reference integrity; the `publish-hydration-parity` CI job reproduces the deploy publish-hydration and validates the promotion record (`scripts/publish_hydration.py`) for NFR-011 |
| Podcaster release smoke (dry-run gate)  | Done      | Blocking post-deploy gate green (`#636`/`#639`/`#643`/`#645`)                    |
| FR-041 internal link checking           | Partial   | Satisfied at test level (`tests/test_internal_link_checker.py`); no standalone CI link tool |
| Hugo/Pagefind timing separation         | Done      | CI records separate report-only Hugo and Pagefind durations; Q-01 workload attribution remains pending |
| Security sign-off (NFR-004)             | Pending   | SEC-02 and SEC-03 repository controls are implemented and tested; SEC-05 has a defense-in-depth recommendation; Hermes finding dispositions remain required |
| Accessibility evidence (NFR-005)        | Pending   | Amy/Fry; 2026-07-30 Step 7.2                                                      |
| Real Podcaster downstream run (NFR-002 / R-04) | Pending | Manual exact-run workflow is bound to `podcaster-real-generation`; environment administration, approval, and one authorized dispatch remain pending |
| Refreshed visual acceptance             | Pending   | `#622` and `#626` repository hardening is implemented; final browser evidence and named visual review remain pending |
| GA4 + GSC connection + baseline (FR-035) | Partial  | Connection complete: GA4 stream confirmed, GSC verified, root sitemap submitted, and products linked; numeric baseline transcription and consent evidence remain pending |
| External metadata and feed validation   | Partial   | [Production feed and source-level metadata evidence](automated-acceptance-evidence-2026-08-03.md) is retained; social preview debuggers, Rich Results, Schema.org, and named reviewer conclusions remain pending |
| Incremental generation cost (Q-01 / NFR-009) | Partial | Report-only cumulative experiment is implemented; retained 3/5-run artifacts and budget-owner conclusion remain pending |
| `repo_pages` rollout (FR-020-022)       | Deferred  | Flag disabled; needs sponsor approval + own plan                                 |
| `dynamic_topic_creation` rollout (FR-004) | Deferred | Flag disabled; needs sponsor approval + own plan                                |
| Sponsor rollout approval                | Pending   | jmservera; see [launch-gate register](#launch-gate-register)                     |

## Epic issue dispositions

| Issue                                             | Title                                       | Disposition                                                        |
| ------------------------------------------------- | ------------------------------------------- | ----------------------------------------------------------------- |
| [#594](https://github.com/jmservera/SquadScope/issues/594) | Epic: Claracle Data Observatory Relaunch | Open — tracks overall relaunch                                    |
| [#644](https://github.com/jmservera/SquadScope/issues/644) | Deploy Hugo site failed (run 30718600607) | CLOSED — resolved by `#645`/`#646`                                |
| [#626](https://github.com/jmservera/SquadScope/issues/626) | Lighthouse / performance quality-gate follow-ups | OPEN — independent hardening; keep thresholds unchanged          |
| [#622](https://github.com/jmservera/SquadScope/issues/622) | Post-review UX polish                    | OPEN — non-blocking polish; resolve factual questions before final visual recapture |
| [#599](https://github.com/jmservera/SquadScope/issues/599) | Connect GA4 + Google Search Console (FR-035) | Closed; owner confirmed GA4, GSC verification, sitemap submission, and product link on 2026-08-02 |

## Launch-gate register

Each gate lists its owner, blocking dependency, and the evidence path that closes it.
The external acceptance matrix in the [acceptance evidence index](README.md#external-acceptance-matrix)
holds the platform-level rows; this register adds ownership and sequencing.

| Gate                                       | Owner       | Dependency                                   | Evidence path                                                        |
| ------------------------------------------ | ----------- | -------------------------------------------- | ------------------------------------------------------------------- |
| GA4 + GSC dated baseline and consent evidence (FR-035/NFR-007/008) | jmservera | Transcribe supplied export and retain production consent observations | [Dated baseline](../../growth/ga4-gsc-baseline-2026-07-29.md) |
| Security sign-off (NFR-004)                | Hermes      | Security review disposition                  | [Security review](security-review.md)                               |
| Accessibility evidence (NFR-005)           | Amy / Fry   | Production browser and assistive technology  | [Owner action register](owner-action-register.md#accessibility-acceptance) |
| Real Podcaster downstream run (NFR-002 / R-04) | URL     | Protected environment policy and maintainer authorization | [Owner action register](owner-action-register.md#protected-real-podcaster-run) |
| Refreshed visual acceptance                | Amy         | Populated content render                     | [Screenshot capture checklist](screenshots/README.md)               |
| External metadata and feed validation      | Amy / jmservera | External debugger and production access   | [Owner action register](owner-action-register.md#external-metadata-and-feed-validation) |
| Incremental generation cost (Q-01 / NFR-009) | URL       | Dispatch immutable workload variants and obtain budget-owner review | [Owner action register](owner-action-register.md#incremental-generation-cost-acceptance) |
| Lighthouse follow-ups (`#626`)             | Amy / Fry   | None; independent hardening                  | `#626`                                                              |
| Post-review UX polish (`#622`)             | Amy         | None; non-blocking                           | `#622`                                                              |
| Sponsor rollout approval                   | jmservera   | Required gate evidence for each flag         | [Owner action register](owner-action-register.md#sponsor-rollout-decision) |

## Deferred to separate plans

These are out of scope for the readiness reconciliation and each needs its own plan
(see the [reconciliation planning log](../../../.copilot-tracking/plans/logs/2026-08-02/claracle-relaunch-readiness-reconciliation-log.md#suggested-follow-on-work)):

- GA4/GSC baseline transcription and production consent evidence (connection and sitemap submission are complete)
- [`repo_pages` rollout](../../../.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md) (requires identity, lifecycle, security, and sponsor approval)
- [`dynamic_topic_creation` rollout](../../../.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md) (requires preview, canary, security, and sponsor approval)
- [Incremental-generation-cost experiment](../../../.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md) (Q-01 / NFR-009)
