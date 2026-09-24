<!-- markdownlint-disable-file -->
# Plan Critique: autodispatch-self-block

* Plan: .copilot-tracking/plans/2026-09-24/autodispatch-self-block-plan.md
* Research: .copilot-tracking/research/2026-09-24/autodispatch-self-block-research.md
* Base reviewed: `3c4e6f7` (worktree `squad/autodispatch-self-block`)

## Disposition

**Accept with changes.** Option C is the right shape: the "ignore" decision rests on primary job
evidence, not on the receipt, so receipt forgery can at worst add blocking. One Critical hole
remains: a named verdict source whose evidence is no longer readable goes through the existing
"unreadable → ignore" path and fails OPEN (F1). Fix F1 and F2 before implementing.

## Findings

| ID | Sev | Finding / evidence | Recommended change |
|----|-----|--------------------|--------------------|
| F1 | Critical | The source run is re-evaluated with the generic per-run logic (P01-T04). In that logic, unreadable jobs/logs → `_run_metadata_associates_identity` → `continue` (`scripts/auto_dispatch_detect.py:1275-1303`). For an auto run with no jobs/logs, `_compat_identity_for_run` also returns `ignore` unless the metadata matches (`:450-460`). Auto `run-name` is `Auto-dispatch: main` for `workflow_run` (`auto-podcast-dispatch.yml:28`), so the metadata never matches. Run logs expire (default retention 90 days), and a source fetched by ID from outside the lookback window is exactly the old run most likely to have expired logs. A verdict that said "this run may have handed off" would then be silently dropped. | Treat an enqueued verdict source as *known related*: any jobs/logs fetch failure, empty/expired logs, missing jobs, or a non-`completed` status → `ambiguous_prior_submission` with reason `derived_verdict_source_unverifiable`. Never let a source reach the metadata-association `continue`. |
| F2 | Major | The ignored run is not proven to be *the verdict's origin*. P01-T01 checks only that the dispatch job was skipped. The W39 run also has a `Check for duplicate dispatch` step (`yml:169-185`) whose failure is what produced the receipt (`yml:209-212`). | Also require that the detect job's `Check for duplicate dispatch` step concluded `failure`. The receipt must be the only `ambiguous_prior_submission` receipt, and its `actions_run_url` must match `html_url` exactly. This is cheap, and it ties the receipt to a real dedup verdict in that attempt. |
| F3 | Major | Chain and cycle bounds are implicit. The de-dup queue stops A→B→A and self-reference (`prior_run_url == actions_run_url`). However, fetches by ID are unbounded apart from the budget, and the budget only counts runs whose *source* is valid. | State the rules explicitly: `prior_run_url` equal to its own run → fail closed; at most `MAX_PRE_HANDOFF_SELF_BLOCKED_RETRIES` fetches by ID; a repeated source is a no-op; exceeding the limit → fail closed. Also validate that the source `html_url` repo equals `repo`. |
| F4 | Minor | "Protected podcast dispatch skipped" is enough for the **latest attempt only**. `_run_jobs` uses the default `filter=latest` (`:516-520`), and `run_attempt` on the list API is the latest attempt. The plan's `run_attempt == 1` check handles this, and the global workflow concurrency group (`yml:35-37`, `cancel-in-progress: false`) serializes re-runs with new runs, so a re-run cannot be in flight during a scan (it would show as non-`completed`). The consequence: a manual **Re-run** of a self-blocked run blocks that identity for good. | Keep `run_attempt == 1` and treat a missing value as fail closed. Document in the summary text: "use a new workflow_dispatch, not Re-run". Do not add per-attempt job queries (over-engineering). |
| F5 | Minor | Job-name spoofing. The job name is the only discriminator, and `path` matches runs from any branch. A branch-modified `auto-podcast-dispatch.yml` (`workflow_dispatch` from a branch) could skip "Protected podcast dispatch" and hand off from another job. The environment/ref guard (`yml:292-302`) likely blocks secrets there, but the plan relies on this without saying so. | Require `head_branch == "main"`, `event ∈ {workflow_run, workflow_dispatch}`, and exactly one job named `Protected podcast dispatch`. |
| F6 | Minor | Budget semantics (P01-T05). (a) "reach 3" is ambiguous about off-by-one. (b) The count is limited to the 50-run lookback, so it refills as runs age out. (c) Nothing in the workflow retries on its own; triggers are sync completion or manual dispatch (`yml:12-16`). So the budget does not guard against duplicates, which the proof already rules out. It only limits operator noise, and it can turn three transient API flakes into a permanent block. | Keep it (R4) but define it: "≥3 ignored self-blocked runs for this exact identity within the lookback → block". The reason and summary must give the recovery path (manual `trigger-podcast.yml` after review). Note in the plan that the budget is an operational bound, not a safety control. |
| F7 | Minor | Parse ordering. The `missing_manifest_sha256` return (`:1239-1250`) runs before the exact-identity match. So older verdict receipts with an empty `manifest_sha256` keep blocking. That is fail closed and acceptable, but P01-T04 says "exact-identity" without saying so. | State this in the plan and add a test. Insert the new branch *after* the conflict/missing-manifest checks and *before* the `AMBIGUOUS_RECEIPT_STATES` return (`:1257`). |
| F8 | Minor | Self-poisoning of logs. P01-T07 adds `::notice::` lines and summary text. `_parse_dispatch_receipts` matches `RECEIPT_PREFIX` anywhere in a line (`:232-248`). | The new output must never echo receipt JSON or the literal prefix. Write the summary *before* `sys.exit(1)` on the ambiguous path (`:866-878`). The existing "Record ambiguous prior dispatch notice" step (`yml:244-264`) will now duplicate the summary; either accept that or say so. |
| F9 | Minor | Concurrency with an in-progress run of the same identity is mostly covered today. Auto runs are serialized by the global group. An in-progress manual run is caught through `run-name` containing `publish_run_id` (`trigger-podcast.yml:20`) → metadata association → ambiguous. Keep the plan's `status == completed` requirement. Separately, the job-level groups differ (`podcast-dispatch-<identity_key>` vs `podcast-dispatch-<week>-<publish_run_id>`), so auto and manual handoffs are not serialized with each other. That is pre-existing and out of scope. | No change needed. Record it as a known residual in the PR. |
| F10 | Minor | Aging out of the lookback. Only the *verdict source* is fetched by ID. Other runs that the original scan never reached (it returned on the first hit) may have aged out. That is the same risk as the base 50-run window, and the v2 ledger backstops it (`:1180-1191`). | Accept. Mention in the PR that the ledger is the authoritative backstop for post-v2 handoffs. |

Over-engineering: nothing serious. `_self_emitted` is redundant given F2's step check, but it
costs nothing. Do not add per-attempt job APIs or YAML changes. Keeping the YAML unchanged is correct.

Live-state note: the real W39 identity should now come out `duplicate`, not `clear`, because the
manual dispatch that escaped is real handoff evidence. P02-T01 must stay synthetic, and the PR
must not claim that W39 would auto-dispatch now.

## Test gaps

1. F1: the verdict source is in the lookback but its logs are unreadable/expired; the source is
   fetched by ID and returns 404/410; the source run is `in_progress`. All must return
   `ambiguous_prior_submission` / `derived_verdict_source_unverifiable`.
2. W39 fixture fidelity. Use the real source shape (cancelled `trigger-podcast.yml` run
   `32730109166`-like jobs) and include the `Reconcile podcast publication` job in the W39 run's
   jobs list. Show that P02-T01 fails on `3c4e6f7`.
3. F2: a self-emitted verdict where the dedup step concluded `success` or `skipped`, or where two
   verdict receipts are present → blocks.
4. F3: a self-referencing `prior_run_url`, an A→B→A cycle, a foreign-repo URL, a non-numeric ID,
   and a source from an unrelated workflow path → fail closed, with a bounded number of fetches
   (assert the URLs fetched).
5. F4/F5: `run_attempt` missing or 2; `head_branch != main`; duplicate `Protected podcast dispatch`
   job names; dispatch job `skipped` but with a non-skipped step; run conclusion `success`
   (document whether it is ignored or blocks).
6. F6: budget boundary (2 ignored → clear, 3 → `pre_handoff_retry_budget_exhausted`). Ignored runs
   for another identity do not count.
7. F7: a verdict receipt with an empty `manifest_sha256` still blocks (`missing_manifest_sha256`).
8. F8: the CLI summary and notices contain no `PODCAST_DISPATCH_RECEIPT::`. The summary is written
   for the clear, duplicate, and ambiguous outcomes, including before the exit(1).
9. Harness: `TestDuplicateCheck._run` (`tests/test_auto_dispatch_detect.py:381-389`) has no
   `status`, `conclusion`, `head_branch`, or `event`. Add these as parameters rather than
   defaults, so existing tests keep exercising the fail-closed path.
10. The ignored run also carries a `handoff_entered` or `accepted` receipt for the same identity
    → blocks (P02-T02 covers this; make sure it is in the same run, not only a sibling run).
