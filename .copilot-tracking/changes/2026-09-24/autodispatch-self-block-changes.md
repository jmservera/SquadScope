<!-- markdownlint-disable-file -->
# Changes: Auto-dispatch self-block on own pre-handoff verdict

* Task ID: SS-AUTODISPATCH-SELF-BLOCK-2026-09-24
* Plan: .copilot-tracking/plans/2026-09-24/autodispatch-self-block-plan.md

## Modified

* `scripts/auto_dispatch_detect.py`
  * New constants for derived verdict states, retry budget, source-fetch cap and proof inputs.
  * `_run_proves_no_handoff`, `_receipt_self_emitted`, `_verdict_source_run_id`, `_fetch_run`.
  * `check_duplicate_result` delegates history classification to `_scan_candidate_runs`, a
    de-duplicated queue that ignores a run's own self-emitted `ambiguous_prior_submission`
    verdict only with positive pre-handoff job proof, then re-proves the verdict source strictly.
  * `DuplicateCheckResult.ignored_pre_handoff_runs`; retry budget
    (`pre_handoff_retry_budget_exhausted`).
  * `_report_dedup_decision`: `::notice::` per ignored run and a step-summary section for every
    decision.
  * Review follow-up (independent review Major finding): `_job_never_started` proves a manual
    `trigger-podcast` job cancelled before any runner picked it up (W39 source `32730109166`:
    `runner_id 0`, no steps); a manual run whose handoff step did not succeed is ignored only
    when its log names a different publish run (e.g. `30162265246` → `29744859230`).
* `tests/test_auto_dispatch_detect.py`: `TestSelfBlockedPreHandoffRetry` (22 tests), fixtures use the
  real job shapes of runs `35562322880`, `32730109166`, `30162265246`.

## Validation

* New W39 regression test fails on `origin/main` (`'ambiguous_prior_submission' != 'clear'`) and
  passes with the change.
* `ruff check .` pass; `ruff format --check .` pass; `pytest tests/` all pass.
* Read-only live replay against GitHub REST for the W39 identity: history before the manual
  recovery → `clear` (ignores `35562322880`); current history → `duplicate` (`35919420880`,
  `submitted`).
