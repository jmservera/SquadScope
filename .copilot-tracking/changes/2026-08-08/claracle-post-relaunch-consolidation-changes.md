<!-- markdownlint-disable-file -->

# Changes: Claracle Post-Relaunch Consolidation

## Related Plan

`.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md`

## Implementation Date

2026-08-08

## Summary

Implemented the locally actionable governance, contract, repository-inventory,
navigation, cost-projection, and yearly-editorial slices selected after planning.
The changes establish deterministic evidence and fail-closed behavior without
claiming named acceptance, cost activation, URL migration, rollout approval, or
release GO.

## Added

* `.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md`
  with CR-01 through CR-06 and BR-001 through BR-009 coverage, dependency gates,
  parallel lanes, validation strategy, and success criteria
* `.copilot-tracking/details/2026-08-08/claracle-post-relaunch-consolidation-details.md`
  with phase-specific operations, cheap checks, exit criteria, and V1.1 policy
  discrepancies
* `.copilot-tracking/plans/logs/2026-08-08/claracle-post-relaunch-consolidation-log.md`
  with selected alternatives, deferrals, human gates, and suggested delivery
  slices
* `.copilot-tracking/reviews/2026-08-08/claracle-post-relaunch-consolidation-plan-review.md`
  with request fulfillment and planning validation results
* `docs/review/claracle-post-relaunch/redesigned-release-finding-map.md`
  with successor gates for unresolved historical findings
* `docs/design/claracle-experience-design-brief.md` as a proposed BR-001 design
  candidate pending accountable approval
* Shared Observatory, repository inventory, cost summary, and yearly evidence
  JSON schemas
* Repository URL inventory and deterministic generator with contract tests
* Deterministic cost projection and tests
* Deterministic yearly evidence-pack generator and tests

## Modified

* `.github/workflows/build-cost-experiment.yml` preserves the five reviewed topic
  hubs during experiment hydration
* `.github/workflows/crawl-and-publish.yml` passes immutable workflow run and
  attempt identity to both token-ledger producers
* `scripts/track_token_usage.py` records workflow identity when supplied
* `scripts/month_synthesis.py` persists complete monthly source packs and
  invalidates clipped version 2 caches
* `scripts/generate_yearly_narrative.py` composes publication prose at sentence
  and paragraph boundaries without ellipsis clipping
* `scripts/generate_rollups.py` emits yearly claim/source evidence packs
* `hugo.toml` orders Weekly, Monthly, and Yearly first
* Focused tests cover hydration, navigation, producer identity, repository
  inventory, cost reconciliation, yearly evidence, and full-year publication

## Removed

None.

## Deviations

* The pre-V1.1 handoff's unconditional redirect-host prerequisite was replaced
  with the approved conditional rule: change hosting only when the final URL map
  contains a genuine-equivalent redirect.
* Cost projection activation remains blocked. Existing ledger rows lack immutable
  workflow identity, and no sponsor-approved legacy exclusion policy or fresh
  identified production record exists.
* Repository migration remains blocked. URL Inspection, exact-page Search
  Analytics, sampled links, first-party referrals, production reconciliation,
  and approved per-URL dispositions are not available locally.
* Design, accessibility, editorial, SEO, security, and sponsor approvals remain
  open. Automated evidence does not substitute for those named decisions.
* Existing BRD, status, session-state, research, and instruction changes were
  treated as user-owned context and were not rewritten by this implementation
  review.

## Release Summary

The selected local implementation slices pass affected automated checks. Cost
publication, repository migration, named acceptance, production rollout, and
outcome measurement remain blocked or future work under the controlling plan.
