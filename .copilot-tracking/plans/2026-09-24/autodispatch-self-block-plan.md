<!-- markdownlint-disable-file -->
# RPI Plan: Auto-dispatch self-block on own pre-handoff verdict

## Task Metadata

* Task ID: SS-AUTODISPATCH-SELF-BLOCK-2026-09-24
* Task slug: autodispatch-self-block
* Plan date: 2026-09-24
* Research: .copilot-tracking/research/2026-09-24/autodispatch-self-block-research.md
* Critique: .copilot-tracking/critiques/2026-09-24/autodispatch-self-block-plan-critique.md
* Branch: `squad/autodispatch-self-block` from `origin/main` @ `3c4e6f7`

## Requirements

* R1 A prior attempt that provably never handed off does not block a retry. Proof comes from
  primary GitHub evidence, never from absence of evidence.
* R2 A prior attempt that handed off, or whose handoff outcome is unknown, still blocks.
* R3 Dedup remains scoped to the four-field weekly identity.
* R4 Automatic retries are bounded.
* R5 Logs and step summary explain why dispatch proceeded or was blocked.
* R6 Regression tests: W39 self-block (fails before, passes after), handed-off, unknown.

## Phases

### P01 Dedup gate change (`scripts/auto_dispatch_detect.py`)

* P01-T01 Add `DERIVED_VERDICT_RECEIPT_STATES = {"ambiguous_prior_submission"}`,
  `MAX_PRE_HANDOFF_SELF_BLOCKED_RETRIES = 3`, and helper
  `_run_proves_no_handoff(run, jobs)`: path is `auto-podcast-dispatch.yml`; `status == completed`;
  `conclusion ∈ {failure, cancelled}`; `run_attempt == 1`; a `Protected podcast dispatch` job is
  present with conclusion `skipped` and no step concluded other than `skipped`.
* P01-T02 Helper `_self_emitted(receipt, run)`: v1 dict receipt whose `actions_run_url` equals the
  run's `html_url`.
* P01-T03 Helper `_verdict_source_run_id(receipt, repo)`: parse `prior_run_url` against
  `https://github.com/{repo}/actions/runs/{id}`; empty → `None` (no source); malformed/foreign →
  sentinel that fails closed.
* P01-T04 In `check_duplicate_result`, convert candidate iteration to a de-duplicated queue.
  For an exact-identity receipt with a derived-verdict state: if jobs are readable, the run proves
  no handoff and the receipt is self-emitted, record the run as an ignored pre-handoff attempt,
  enqueue its verdict source (fetch `/actions/runs/{id}` when not already queued; source must be
  one of the two dispatch workflows; fetch failure/foreign workflow → `ambiguous_prior_submission`
  reason `derived_verdict_source_unverifiable`), and continue with the run's other receipts.
  Otherwise keep the existing fail-closed `ambiguous_prior_submission` return.
* P01-T05 Retry budget: when ignored self-blocked attempts for the identity reach
  `MAX_PRE_HANDOFF_SELF_BLOCKED_RETRIES`, return `ambiguous_prior_submission` reason
  `pre_handoff_retry_budget_exhausted`.
* P01-T06 `DuplicateCheckResult.ignored_pre_handoff_runs: tuple[str, ...] = ()`, populated on every
  return path after scanning begins.
* P01-T07 `_check_duplicate_cli`: emit `::notice::` per ignored run and append a
  "Podcast dispatch dedup decision" section to `$GITHUB_STEP_SUMMARY` for clear, duplicate, and
  ambiguous outcomes (status, reason, prior run, ignored pre-handoff runs, identity).

### P02 Tests (`tests/test_auto_dispatch_detect.py`)

* P02-T01 W39 self-block: auto run with W39-shaped jobs (dedup step failure, dispatch job skipped)
  and self-emitted `ambiguous_prior_submission` receipt → `clear`, run listed as ignored. Must fail
  on unfixed code.
* P02-T02 Handed-off: same shape but `Protected podcast dispatch` ran (success) or a
  `handoff_entered`/`submitted` receipt coexists → blocks.
* P02-T03 Unknown: jobs unreadable; dispatch job absent; run still in progress; `run_attempt` 2;
  receipt not self-emitted → `ambiguous_prior_submission`.
* P02-T04 Source re-evaluation: verdict source in lookback with blocking evidence → still blocks;
  source outside lookback fetched by ID; source fetch failure → fail closed.
* P02-T05 Identity scope: verdict receipt for another identity never counted.
* P02-T06 Budget: three ignored self-blocked runs → `pre_handoff_retry_budget_exhausted`.
* P02-T07 CLI summary written with reason and ignored runs.

### P03 Validation and delivery

* `ruff check .`, `ruff format --check .`, `pytest tests/` (per `.github/copilot-instructions.md`).
* PR, independent review, CI green, squash-merge. No workflow dispatches.

## Out of scope

* `duplicate_prevented` verdict receipts keep blocking (they point to proof of submission).
* Workflow YAML is unchanged; the CLI owns the summary.

## Critique dispositions (independent critique, Accept with changes)

* F1 Critical — accepted: verdict sources are evaluated strictly; unreadable jobs/logs without
  positive pre-handoff proof, empty history, or an incomplete source run fail closed
  (`derived_verdict_source_unverifiable`), including sources already scanned leniently.
* F2 Major — accepted: require `Check for duplicate dispatch` = `failure` and exactly one verdict
  receipt in the run.
* F3 Major — accepted: self-reference, foreign repo, malformed URL fail closed; source fetches
  capped at `MAX_VERDICT_SOURCE_FETCHES = 5` (`derived_verdict_source_chain_too_long`).
* F4 — accepted: summary tells operators to use a new `workflow_dispatch`, not Re-run.
* F5 — accepted: `head_branch == main`, event ∈ {workflow_run, workflow_dispatch}, exactly one
  detect and one dispatch job, every dispatch step `skipped`, receipt `workflow` field checked.
* F6 — accepted: budget defined as "ignore at most 2" (`MAX_IGNORED_SELF_BLOCKED_ATTEMPTS = 2`;
  2 clears, 3 blocks) and evaluated after the full scan so stronger duplicate evidence wins.
* F7, F9, F10 — accepted as documented residual behavior.
* F8 — accepted: summary/log text never contains the receipt prefix; summary is written before
  the blocking exit.
