<!-- markdownlint-disable-file -->
# Implementation Details: Claracle Relaunch Follow-Up Execution

## Phase 1: Publish Review Corrections

Commit and push the reviewed #599/#644 state corrections, then resolve the two PR #647 threads only after the changed diff is visible remotely.

Success: commit `8fddceb` is on the PR branch and both threads are resolved.

## Phase 2: Reconcile GA4/GSC Evidence

Keep both checked-in Hugo defaults empty. Record only presence-level production observations and secret names. Never record the GA identifier or GSC token.

Owner handoff:

1. Confirm the existing deployed ID maps to the intended Claracle stream.
2. Obtain the URL-prefix GSC HTML-tag token and set `GSC_SITE_VERIFICATION` privately.
3. Verify ownership, submit `https://claracle.com/sitemap.xml`, confirm consented GA4 Realtime receipt, and capture a dated baseline.
4. Update the evidence matrix with redacted conclusions and actual platform values.

Success: repository evidence is accurate; FR-035 remains partial until the owner handoff is evidenced.

## Phase 3: Refresh Acceptance Evidence

Update the security record to acknowledge implemented candidate-title sanitization and lifecycle fixtures while retaining Hermes disposition requirements. Add owner-ready evidence records for manual accessibility, visual review, protected Podcaster execution, and sponsor decisions. Do not mark a human gate complete from automated tests.

Protected Podcaster sequence:

1. Confirm downstream idempotency or authorize a specific eligible week.
2. Define required reviewers and branch policy for a real-generation environment.
3. Bind the real generation job to that environment through a separately reviewed workflow change.
4. Run once and retain the approver, week, manifest run, article digest, Actions URL, downstream job ID, and final conclusion.

Success: the acceptance index identifies current automated evidence and exact remaining owner actions.

## Phase 4: Plan Gated Rollouts and Cost Measurement

Cost experiment:

1. Use one main SHA and one hydrated publish SHA for every workload variant.
2. Measure baseline, topic hubs, data pages, repository pages, and optionally the reviewed dynamic canary.
3. Collect at least three comparable CI runs, preferably five.
4. Retain raw Hugo and Pagefind samples, workload counts, output sizes, medians, nearest-rank p95, absolute deltas, and per-added-page deltas.
5. Keep thresholds report-only until an owner approves the budget and enforcement date.

Repository-page activation:

1. Resolve stable GitHub identity risk or record an explicit accepted-risk disposition.
2. Seed lifecycle parity twice while disabled and require byte-identical output.
3. Run enabled checks and two generations in an isolated checkout at the unchanged threshold.
4. Review every created, rewritten, obsolete, and expired path.
5. Obtain Hermes, URL, and sponsor approval for the exact revision.

Dynamic-topic canary:

1. Review the five eligible candidates and select one unambiguous canary.
2. Add the other four to `ignore_topics` as explicit deferrals.
3. Preview the exact mutation in an isolated checkout because current `--dry-run` is a no-op.
4. Validate hub output, registry changes, weekly assignments, taxonomy, log event, rendered output, and rollback behavior.
5. Obtain security and sponsor approval for one publish transaction.

Success: both rollouts have bounded, reversible execution plans and production flags remain disabled.

## Phase 5: Validate and Review

Run focused tests for workflow mapping, internal links, sanitization, lifecycle, taxonomy, export policy, and documentation. Use PR CI for Hugo, browser, axe, and Lighthouse validation when local binaries or system libraries are unavailable.
