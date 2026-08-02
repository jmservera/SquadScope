<!-- markdownlint-disable-file -->
# Research: Claracle Relaunch Readiness Reconciliation (gap analysis)

## Scope

Review of the relaunch plans, PRD, and BRD against actual repository state to
identify what is missing and plan its closure. Verified via repository inspection
on 2026-08-02.

## Source documents

- BRD: docs/brds/claracle-data-observatory-relaunch-brd.md (BRD-CLARACLE-002, Document Control says v1.1)
- PRD: docs/prds/claracle-data-observatory-relaunch.md (v1.2, 2026-07-31)
- Plans:
  - .copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md (Phases 1-6 done; 7-10 partial/open)
  - .copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md (Phases 1-5 done; 6-8 open)
  - .copilot-tracking/plans/2026-07-31/claracle-deploy-hydration-remediation-plan.instructions.md (Phase 1 done; 2-5 open)

## Verified findings (evidence)

- Initial blocker: issue #644 "Deploy Hugo site failed (run 30718600607)" was the incident under investigation. Final verification found it closed as completed on 2026-08-01 after #645/#646 restored a green deploy.
- GA4/GSC NOT connected: hugo.toml `ga_measurement_id = ""`. Issue #599 was closed as completed on 2026-08-01, but its recorded human-action checklist remains outstanding (FR-035/DR-002/NFR-007). Growth KPI baselines (OBJ-2/3/4, G-002/003/004) were not captured.
- Repo pages gated off: config/observatory.toml `[repo_pages] enabled = false` and `[repo_pages.lifecycle] enabled = false` (FR-020-022 not live; matches PRD flag `repo_pages`).
- Internal link checking exists as tests/test_internal_link_checker.py (FR-041 partially satisfied at test level, not a separate CI link tool).
- Issue dispositions: #644 and #599 closed as completed on 2026-08-01; #626 (Lighthouse follow-ups), #622 (UX polish), and #594 (Epic) remained open at final verification. Closing #599 did not complete its human-action checklist.

## Session work NOT reflected in docs

- Deploy/hydration cascade #627-#637; Podcaster smoke #639/#643; restore-consistency #640/#646 all merged but absent from the PRD changelog and plan checkboxes.
- Deploy-hydration plan Phase 4 (embed source_page guard) shipped as check_embed_sources.py (#641) but left unmarked.

## Document/consistency gaps

- BRD version drift: Document Control = v1.1 but Acceptance section + PRD REF-1 cite BRD v1.0.
- No single status-of-record reconciling the three overlapping plans; checkboxes are stale.
- PRD changelog behind reality (no v1.3 for #627-#646 workstream; NFR-002 restore sub-behavior undocumented).
- No sponsor-approval artifact exists (BRD notes none recorded); both rollout flags cannot flip without it.
- DR-002 dated baseline snapshot never captured -> success currently unmeasurable.

## Unmet launch gates (PRD/BRD)

- NFR-004 Hermes security sign-off (pending)
- NFR-005 accessibility evidence (pending)
- NFR-002 / R-04 real Podcaster downstream run evidence (pending)
- Refreshed visual acceptance (pending)
- Q-01 / NFR-009 incremental generation cost/time (still TBD)
- Sponsor approval to enable dynamic_topic_creation + repo_pages

## Planning approach

Single reconciliation plan:
1. Triage/resolve #644 (live blocker) first.
2. Reconcile the three plan checklists to delivered state + produce one status-of-record.
3. Reconcile product docs (PRD v1.3 changelog + restore NFR; fix BRD version drift; add sponsor-approval + launch-gate register).
4. Sequence remaining launch gates into one owner/evidence register (do not fully implement external/human gates here).
5. Validate docs (markdown lint, link integrity) + re-review.

Deferred to separate plans (out of scope here):
- GA4/GSC connection implementation (FR-035; continue the human-action checklist on closed issue #599)
- repo_pages rollout + dynamic topic rollout (require sponsor approval)
- Incremental-generation-cost design spike (Q-01)
