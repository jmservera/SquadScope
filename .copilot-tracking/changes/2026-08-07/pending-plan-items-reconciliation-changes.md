<!-- markdownlint-disable-file -->
# Changes: Pending Plan Items Reconciliation

Related plan: `.copilot-tracking/plans/2026-08-07/pending-plan-items-reconciliation-plan.instructions.md`
Implementation dates: 2026-08-07 (Phases 1-3, committed `83d2d62`) and 2026-08-08 (Phases 4-5, this session)

## Summary

Closed the executable classes of the six pending plans. Phases 1-3 (canary
allowlist, cost-experiment corpus guard, PRD/BRD reconciliation) were delivered
and committed in `83d2d62` by a prior session. This session completed Phase 4
(plan checkbox reconciliation across the five older plans plus the review
status-of-record) and Phase 5 (validation), and reconciled the reconciliation
plan's own checklist.

## Changes by Category

### Added

* `content/weekly/2026/W99.md` removed (was a stray, untracked test artifact left
  behind by an interrupted `test_hugo_home_topic_display_is_safe_without_topic_content_page`
  run; the test recreates and unlinks it itself).

### Modified (this session — documentation only)

* `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md`
  — ticked Step 7.3 (separate Hugo/Pagefind CI timing), Step 9.2 (NFR-004 security
  closed), Step 10.1 (validation run), Step 10.2 (idempotence via `#663`/`#664`),
  and Phases 7 and 10 headings; left Steps 9.3 and 9.4 unticked with named owners.
* `.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md`
  — ticked Step 6.3 (timing + protected Podcaster evidence collected) and Step 7.1
  (NFR-004 fully closed) plus Phase 6 heading; refreshed Steps 7.2, 7.3, 8.3 notes
  and left them unticked with named owners.
* `.copilot-tracking/plans/2026-07-31/claracle-deploy-hydration-remediation-plan.instructions.md`
  — ticked Step 5.3 and Phase 5 heading (PRD NFR-011/012, R-08, Q-03 reconciled in
  PRD 1.5).
* `.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md`
  — ticked Phase 3 items 1-2 (`--dry-run` non-mutating report and its no-mutation
  tests, `#670`); annotated the canary/`ignore_topics`/approval items as
  human-authority and recorded that `allow_topics` supersedes the blocklist
  approach; annotated the Phase 4 cost-experiment item as unblocked-via-dispatch
  and Phase 5 rollout items with owners.
* `.copilot-tracking/plans/2026-08-02/claracle-relaunch-followup-execution-plan.instructions.md`
  — annotated the GSC transcription item with its owner (jmservera, deferred).
* `.copilot-tracking/plans/2026-08-06/observatory-phase-7-acceptance-gates-plan.instructions.md`
  — ticked Phase 7.1 timing collection Steps 1-5 and all Phase 7.2 security steps;
  left timing Steps 6-7 unticked with owners.
* `.copilot-tracking/plans/2026-08-06/phase-7-1-timing-collection-monitoring.md`
  — ticked Run 2 and Run 3 capture plus the budget-summary preparation; left the
  submit/record/close approval items unticked with owners.
* `.copilot-tracking/plans/2026-08-06/phase-7-3-visual-baseline-capture-workflow.md`
  — recorded that the committed 54-variant baseline approach was superseded by the
  sitemap-driven CI evidence capture (run `31160859598`) and left the named visual
  review items unticked with owners (Amy, Fry).
* `docs/review/data-observatory-relaunch/status-of-record.md`
  — corrected two internally contradictory rows: NFR-004 security sign-off
  Pending -> Done and FR-041 internal link checking Partial -> Done.
* `.copilot-tracking/plans/2026-08-07/pending-plan-items-reconciliation-plan.instructions.md`
  — ticked all five phases of the reconciliation plan.

### Modified (follow-on doc-consistency sweep, 2026-08-08)

* `docs/review/data-observatory-relaunch/security-review.md` — added a 2026-08-07
  reconciliation banner to the "Review status" section noting NFR-004 was approved
  2026-08-06, while preserving the original 2026-08-02/04 review-pass findings as the
  historical record; points to the authoritative `security-sign-off-checklist.md`.
* `docs/review/data-observatory-relaunch/status-of-record.md` — bumped "Reconciled
  through" to 2026-08-07 and `ms.date` to 2026-08-07 to cover the corrected rows.
  (`README.md` visual-evidence "not accepted" language and the dated
  `automated-acceptance-evidence-2026-08-03.md` snapshot were left unchanged: the
  former is correctly still human-gated, the latter is a point-in-time record.)

### Modified (owner-action-register refresh, 2026-08-08)

* `docs/review/data-observatory-relaunch/owner-action-register.md` — this doc is the
  human-gate action register. Reconciled its Security acceptance section (items 6-8
  struck through as Done 2026-08-06, NFR-004 fully accepted) and updated the
  `dynamic_topic_creation` sponsor-rollout conditions to reflect the delivered
  `--dry-run` preview (`#670`) and the `allow_topics` allowlist; bumped `ms.date`.
  The analytics/search gate section already enumerates the GA4/GSC transcription
  actions owned by jmservera.

### Added — analytics baseline transcription (2026-08-08)

* `docs/growth/ga4-gsc-baseline-2026-07-29.md` — transcribed the GA4 snapshot and the
  GSC Performance/Coverage exports into the Baseline values table (NFR-007), added a
  Transcription notes subsection with source cross-checks and signal/noise flags, and
  added a code-grounded "Production consent observations (NFR-008)" capture-and-record
  scaffold (fill-in table for denied/granted/withdrawal). Raw exports were extracted in
  the git-ignored `.tmp/` and are not committed.
* `docs/review/data-observatory-relaunch/owner-action-register.md`,
  `docs/review/data-observatory-relaunch/status-of-record.md`, and the 2026-08-02
  followup plan — updated to reflect NFR-007 baseline complete; NFR-008 consent pending.

### Added — follow-on items (2026-08-08)

* `data/metrics/growth/launch-baseline-2026-07-29.json` — durable structured record of the
  8 NFR-007 baseline metrics (GA4 + GSC) with provenance and windows, matching the
  `data/metrics/` convention; no measurement identifier stored. Hugo build verified.
* `docs/review/data-observatory-relaunch/owner-action-register.md` — added a "Proposed
  dynamic-topic canary" recommendation (`local-first`, evidence-backed via `--dry-run`)
  and an activation shape using `allow_topics`; added a cost-experiment readiness note
  (workload guard passes at 266; only the manual `workflow_dispatch` remains, owner URL).

### Modified — NFR-008 consent observations captured (2026-08-08)

* `docs/growth/ga4-gsc-baseline-2026-07-29.md` — recorded denied/granted production consent
  observations from two private-session HAR captures: before consent = 0 Google requests;
  after "Accept all" = one `gtag/js` load and two `g/collect` beacons (`anonymize_ip: true`).
  Filled the observation table and External evidence matrix; acceptance rule now records
  NFR-007 and NFR-008 complete. Measurement ID kept out of the record; raw HARs not committed.
* `data/metrics/growth/launch-baseline-2026-07-29.json` — `nfr_008_consent` set to confirmed.
* `docs/review/data-observatory-relaunch/owner-action-register.md`,
  `docs/review/data-observatory-relaunch/status-of-record.md`, and the 2026-08-02 followup
  plan — analytics/search gate now fully evidenced; GA4/GSC row set to Done; followup plan
  Phase 2 (and its heading) ticked.

### Added/Modified — remaining follow-on items (2026-08-08)

* `config/observatory.toml` — staged the first bounded canary: `allow_topics = ["local-first"]`
  with `enabled = false`. A `--dry-run` promotes exactly one slug and skips 2,500 with
  `not-in-allowlist`; both rollout flags remain disabled. Pending Hermes/sponsor approval.
* `docs/review/data-observatory-relaunch/owner-action-register.md` — recorded the staged
  canary revision.
* `docs/review/data-observatory-relaunch/timing-analysis.md` — added an "Enforcement Draft
  (apply only after owner approval)" section with the exact `ci.yml` blocking-budget step,
  ready to apply once the timing-budget owner signs off (ci.yml itself unchanged).
* `docs/review/data-observatory-relaunch/status-of-record.md` — added a consolidated
  "Remaining human gates" single-view table (owner + evidence path) and refreshed the
  source-plan reconciled states.
* `docs/growth/ga4-gsc-baseline-2026-07-29.md` — documented the structured-dataset and
  dated-append trend convention for future GA4/GSC pulls.

### Committed previously (`83d2d62`, Phases 1-3)

* `config/observatory.toml` — added `allow_topics = []` to `[topic_hubs.dynamic_creation]`.
* `scripts/manage_topic_hubs.py` — `allow_topics` config field, `not-in-allowlist`
  skip reason in `preview_dynamic_hubs()` and `create_dynamic_hubs()`, allowlist in
  the check log line.
* `scripts/build_cost_experiment.py` — `EXPECTED_CLASS_COUNTS["repository_pages"]`
  corrected 263 -> 266.
* `tests/test_topic_hubs.py` — allowlist bounding tests.
* `docs/prds/claracle-data-observatory-relaunch.md` — version 1.5; R-03/R-05/R-08
  closed; NFR-011/012 marked Delivered; changelog entry.
* `docs/brds/claracle-data-observatory-relaunch-brd.md` — version/acceptance prose
  reconciled.

## Validation

* `ruff check .` — All checks passed.
* `ruff format --check .` — 157 files already formatted.
* `pytest tests/` — 1484 passed, 2 warnings, 34 subtests passed.
* `hugo --minify` — 2701 pages built.
* `scripts/check_internal_links.py public --base-url "https://claracle.com/"` — exit 0.
  (Three pre-existing data-driven tag pages emit `/SquadScope/`-prefixed links; these
  are non-fatal, unrelated to this reconciliation, and predate these changes.)

## Remaining Human-Gated Items (no repository work possible)

* Timing budget threshold approval — timing-budget owner, URL, jmservera.
* Named visual evidence disposition and manual interaction-state captures — Amy, Fry.
* GA4/GSC dated baseline transcription and production consent evidence — jmservera.
* External metadata/feed validation and named accessibility (NFR-005) review — Amy, Fry.
* Dynamic-topic canary selection and Hermes/sponsor approval — Amy, Hermes, jmservera.
* `repo_pages` / `dynamic_topic_creation` activation transactions — jmservera (both
  rollout flags remain `false`).
* Cost-experiment dispatch (`build-cost-experiment.yml`) with reviewed SHAs — URL.
