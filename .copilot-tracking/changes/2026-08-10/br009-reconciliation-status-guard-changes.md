<!-- markdownlint-disable-file -->

# Changes: BR-009 Reconciliation Status Guard (Fast-Follow)

## Related Plan

`.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md`

## Implementation Date

2026-08-10

## Summary

Fast-follow to PR #697 (merged as `9af3026d`). The squad acceptance review of
the BR-009 cost dashboard (`.copilot-tracking/reviews/2026-08-10/br-009-squad-acceptance-review.md`)
surfaced one real, converging gap from two independent reviewers (Fry, tester;
Nibbler, Responsible AI): `reconciliation.status` was validated for
*presence* but never for its *value*, so a structurally-complete but
unreconciled payload (`"status": "partial"`) would still render a
full-confidence total — contradicting BR-009's literal BRD acceptance
criterion ("fail when required data is... unreconciled"). Fry additionally
flagged that `totals.cost`/`input_tokens`/`output_tokens` used the same
unguarded numeric-cast pattern that two earlier Copilot review rounds had
already found unsafe for `provenance.maximum_age_days` (Hugo's `int`/`float`
cast aborts the whole `hugo` build, not just the page, on a map/slice input).

## Modified

* `layouts/partials/cost-dashboard.html`:
  * Added a `reconciliation.status == "reconciled"` equality check (in
    addition to the existing presence check) so an unreconciled record fails
    closed instead of rendering
  * Added a `reflect.IsMap`/`reflect.IsSlice` + numeric-regex guard for
    `totals.cost`/`input_tokens`/`output_tokens` before their `float`/`int`
    casts later in the partial, matching the pattern already used for
    `provenance.maximum_age_days`
  * Round 2 (Copilot review on this PR): guarded `reconciliation.status`
    itself against a map/slice value before comparing it, converting via
    `string` rather than raw `eq`/`ne` on an untrusted shape — locally
    confirmed this Hugo version's `eq`/`ne` do not error on map/slice
    comparisons, but the guard matches this file's established defense-in-depth
    convention and removes any dependency on that specific behavior
* `tests/test_cost_dashboard_rendering.py`: added
  `test_about_page_shows_unavailable_when_reconciliation_is_not_reconciled`,
  `test_about_page_shows_unavailable_when_totals_field_is_non_numeric`, and
  `test_about_page_shows_unavailable_when_reconciliation_status_is_an_object`

## Validation

* `pytest tests/test_cost_dashboard_rendering.py` -> 14 passed
* `pytest tests/` -> 1561 passed
* `ruff check` / `ruff format --check` clean
* `hugo --minify` full-site build succeeds; `/about/` and `/dashboard/` both
  still render the unavailable state against real (file-absent) repository
  data

## Deviations

None — this is a scoped, direct fix for the converging squad-review finding,
with no change to the surrounding fail-closed design or BR-009's remaining
open activation blocker (the ledger commit-path gap, unchanged by this PR).
