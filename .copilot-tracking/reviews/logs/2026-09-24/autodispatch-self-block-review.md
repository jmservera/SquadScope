<!-- markdownlint-disable-file -->
# RPI Review: Auto-dispatch self-block on own pre-handoff verdict

* Task ID: SS-AUTODISPATCH-SELF-BLOCK-2026-09-24
* PR: jmservera/SquadScope#794
* Execution status: complete
* Outcome: **Accepted** — no open Critical/Major findings

## Requirement traceability

| Req | Evidence |
|---|---|
| R1 pre-handoff attempt does not block | `test_w39_own_pre_handoff_verdict_does_not_block_retry` (fails on `origin/main`), `test_w39_pre_recovery_history_replay_allows_retry`; live read-only replay → `clear` |
| R2 handed-off / unknown still blocks | `test_handed_off_*`, `test_handoff_receipt_*`, `test_verdict_source_with_real_submission_still_blocks`, `test_unknown_outcome_variants_still_block`, `test_unreadable_or_incomplete_job_evidence_still_blocks`, `test_unverifiable_verdict_source_still_blocks`, `test_cancelled_source_job_that_got_a_runner_still_blocks`; live current history → `duplicate` |
| R3 identity scope | `test_verdict_for_other_identity_is_not_counted`, `test_manual_handoff_failure_is_scoped_to_its_publish_run` |
| R4 bounded retries | budget tests (2 clear, 3 block), `test_verdict_source_chain_is_bounded_and_cycle_safe` |
| R5 loud logs/summary | CLI summary tests (no receipt prefix) |

## Review rounds

1. Independent code review (subagent): Major — fixture invented a skipped step; real source
   `32730109166` still blocked. Fixed (`_job_never_started`, real fixtures) and a second unscoped
   blocker found by live replay (`30162265246`) scoped by publish run.
2. Independent re-review of the delta: no findings.
3. Copilot PR reviewer: 4 + 2 comments; 5 hardening fixes applied, 1 rebutted with a test
   (ignored runs are preserved on early returns).
4. Copilot PR reviewer, later rounds: hardening applied for verdict-source cycles, source-run
   metadata validation, exactly-one-relevant-job legacy proofs, nested step validation, positive
   evidence for strict sources, and queue-order-independent strict revalidation of
   already-processed sources (`strict_unproven_ids`, with a reversed-order regression test).
   Claims contradicted by live API evidence were rebutted with that evidence.

## Follow-up

* Residual: `duplicate_prevented` verdict receipts still block by design (point to a real submission).
* Residual: provable pre-handoff requires attempt 1; operators must use a new `workflow_dispatch`
  instead of Re-run (stated in the step summary).
* No further stage work routed.
