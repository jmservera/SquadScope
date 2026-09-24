<!-- markdownlint-disable-file -->
# RPI Research: Auto-dispatch self-block on own pre-handoff verdict

## Task Metadata

* Task ID: SS-AUTODISPATCH-SELF-BLOCK-2026-09-24
* Task slug: autodispatch-self-block
* Research date: 2026-09-24
* Base: `origin/main` @ `3c4e6f7` (includes `jmservera/SquadScope#773`, `jmservera/SquadScope#772`)
* Planning Readiness: **Ready**

## Question

Why does a retry of the W39 automatic podcast dispatch refuse to proceed after
`jmservera/SquadScope#773`, and what evidence proves that a prior attempt never handed off?

## Evidence

1. Run `35562322880` (`auto-podcast-dispatch.yml`, `workflow_run`, attempt 1, conclusion `failure`):
   * Job `Detect eligible weekly publication`: step `Check for duplicate dispatch` = `failure`
     (pre-#773 reason `legacy_submission_without_canonical_receipt`, prior run `32730109166`,
     an unrelated cancelled `trigger-podcast.yml` run).
   * Step `Emit detect receipt` = `success` and printed
     `PODCAST_DISPATCH_RECEIPT::{"receipt_state":"ambiguous_prior_submission", week, publish_run_id,
     article_sha256, manifest_sha256, prior_run_url=.../32730109166, actions_run_url=.../35562322880}`.
   * Job `Protected podcast dispatch` = `skipped` (zero steps). The Podcaster was never called.
2. `scripts/auto_dispatch_detect.py::check_duplicate_result` scans the last 50 runs of both
   workflows, parses `PODCAST_DISPATCH_RECEIPT::` lines, and for an exact four-field identity
   match returns `ambiguous_prior_submission` when `receipt_state ∈ AMBIGUOUS_RECEIPT_STATES`,
   which contains `ambiguous_prior_submission`.
3. Consequence: the detect job's *verdict* receipt (a derived conclusion, not handoff evidence) is
   read back by every later attempt for the same identity as if it were handoff uncertainty.
   Even after #773 removed the original false cause, run `35562322880` itself now blocks every
   retry for the W39 identity — a self-perpetuating block. Only a manual dispatch escaped it.
4. Primary handoff evidence already exists and is independent of the verdict: the
   `Protected podcast dispatch` job conclusion and `run_attempt` (`_legacy_auto_pre_submit_only`),
   v2 `handoff_entered`/`accepted`/`submission_unknown` receipts, and the Issue ledger. None of
   those derived-verdict receipts are written to the ledger (v2 `RECEIPT_STATES` excludes them).
5. The verdict receipt records `prior_run_url`, i.e. the source of the original ambiguity. That
   source run is itself a candidate that the scan re-evaluates from primary evidence when it is
   within the lookback window; `32730109166` is index 5 of 71 `trigger-podcast.yml` runs.
6. `duplicate_prevented` receipts are also derived verdicts but point to proof of a real
   submission; they are out of scope and keep blocking.

## Root cause

`ambiguous_prior_submission` is used for two different things: a detect-time verdict and
(inherited) handoff uncertainty. The dedup gate treats its own earlier verdict as evidence of a
possible handoff, even when primary job evidence proves the run never reached the handoff job.

## Options

* A. Stop emitting the verdict receipt — rejected: loses the audit trail and older runs keep blocking.
* B. Ignore `ambiguous_prior_submission` receipts entirely — rejected: fails open if the verdict
  source aged out of the lookback window.
* C. **Selected.** Treat a verdict receipt as non-blocking only when (a) it was emitted by the run
  that carries it (`actions_run_url` equals the run URL), (b) the run is an
  `auto-podcast-dispatch.yml` run, completed with `failure`/`cancelled`, single attempt, jobs
  readable, and the `Protected podcast dispatch` job is present and `skipped`, and (c) its
  `prior_run_url` source is re-evaluated from primary evidence (queued for scanning, fetched by
  ID when outside the lookback; unreadable/foreign source → fail closed). Bound automatic
  retries with a per-identity budget of ignored self-blocked attempts; log every decision.

## Planning Readiness

Ready. No user decision required; the task statement fixes the policy (UNKNOWN ≠ FAILED).
