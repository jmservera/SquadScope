<!-- markdownlint-disable-file -->
# RPI Phase Details: Podcast Dispatch Identity Reconciliation

## Metadata

* Task ID: SS-PODCAST-DISPATCH-IDENTITY-RECONCILIATION-2026-09-21
* Task slug: podcast-dispatch-identity-reconciliation
* Related plan: .copilot-tracking/plans/2026-09-21/podcast-dispatch-identity-reconciliation-plan.md
* Evidence sources: .squad/decisions.md; .copilot-tracking/research/2026-09-21/podcast-dispatch-identity-reconciliation-research.md; .copilot-tracking/critiques/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md; authoritative caller requirements dated 2026-09-21
* Planning status: Six unresolved PR review threads and the hosted Python configuration failure are corrected, locally validated, committed, and pushed; PR head/check confirmation and hosted P04-T02 evidence remain

## Task-Level Context

* Stable task identity: `SS-PODCAST-DISPATCH-IDENTITY-RECONCILIATION-2026-09-21`.
* Current failure seam: `DispatchIdentity` and `_receipt_identity_matches` omit `manifest_sha256`; `check_duplicate_result` can turn globally unreadable/identity-free history into `ambiguous_prior_submission`.
* Current mutation seam: `real-generation` calls `scripts/podcaster_handoff.py` after exact manifest validation; current evidence is emitted afterward to logs/outputs.
* Safety invariant: only successful durable `handoff_entered` persistence crosses the uncertainty boundary; an exact identity at or beyond that state is never automatically retried.
* Availability invariant at the pre-boundary: prepare, `attempt_prepared`, mirror failure, `pre_submit_failed`, or failed `handoff_entered` persistence proves the handoff was not invoked and remains retryable.
* Availability invariant: history with no demonstrable association to the requested identity is not allowed to poison that identity.
* Cross-repository boundary: SquadScope consumes a defined terminal contract but does not modify or assume deployment in SquadScope-Podcaster.

## Phase Index

| Phase ID | Name | Status | Detail sections |
|---|---|---|---|
| P01 | Establish canonical state and identity-scoped history | Complete after multi-ledger reconciliation and identity-scoped unreadable-history correction | P01, P01-T01, P01-T02 |
| P02 | Enforce durable receipt ordering around mutation | Complete after retry-safe HTTP rejection classification | P02, P02-T01, P02-T02 |
| P03 | Reconcile terminal outcome, latency, and incidents | Complete after protected status endpoint validation, HTTP status enforcement, and incident-marker filtering | P03, P03-T01, P03-T02 |
| P04 | Complete locked regression and validation evidence | In progress: P04-T01 and all local P04-T02 gates pass; hosted checks await push | P04, P04-T01, P04-T02 |
| P05 | Deliver review branch and independent review handoff | Complete; correction commit `93c7c25` pushed and independent review record left unchanged | P05, P05-T01, P05-T02 |

<!-- rpi:phase id=P01 -->
## P01: Establish canonical state and identity-scoped history

### Context

Research C9-C14 and C19-C22 establishes that the current three-field identity is incomplete and that ambiguity is applied too broadly. Existing v1 receipt states are valuable compatibility evidence and must remain readable. The new state module is the single canonical owner for four-field validation, receipt serialization, ledger parsing, and incident-key derivation.

### Intent

Make the identity boundary explicit and reusable before changing mutation or monitoring behavior.

### Boundaries

* Included: full identity model, v2 receipt model, v1 compatibility, Issue ledger access, artifact JSON parsing, identity-scoped legacy decisions.
* Excluded: Podcaster call changes, polling, incidents, Podcaster repository work.

### Likely Targets

* `scripts/podcast_dispatch_state.py` (new): canonical data/state primitives and CLI subcommands.
* `scripts/auto_dispatch_detect.py`: replace/alias `DispatchIdentity`, pass manifest digest, and classify prior evidence.
* `tests/test_podcast_dispatch_state.py` (new): canonical state tests.
* `tests/test_auto_dispatch_detect.py`: detector and legacy regressions.

### Dependencies

* Exactly one independent plan critique completed with PC-001 through PC-006 dispositions applied.
* Existing trusted publish-branch manifest lookup and GitHub API authentication.

### Validation Expectations

* Run focused state/detector tests after each task.
* Preserve all existing v1 test meanings unless assertions are strengthened for the fourth field.

### Completion Evidence

* Four-field equality/mismatch tests pass.
* Empty unrelated cancelled history passes; exact associated uncertainty blocks.
* v1 submitted/unknown/observe-only semantics remain compatible.

### Unresolved Items

* None. Ledger storage and retention are selected in the plan; bounds/contract remain explicit critique targets.

<!-- rpi:task id=P01-T01 -->
### P01-T01: Add canonical state and receipt model

#### Context

`scripts/auto_dispatch_detect.py` currently owns receipt constants and parsing. Moving canonical v2 primitives into one added module avoids duplicating schema rules across detector, workflow receipt commands, and reconciliation.

#### Intent

Create a dependency-free state module that can be imported by scripts and invoked by the workflow.

#### Boundaries

* Included:
  * `CanonicalPublicationIdentity(week, publish_run_id, article_sha256, manifest_sha256)`;
  * `DispatchReceipt` with schema, receipt ID, timestamps, dispatch run/attempt, identity, receipt state (`attempt_prepared`, `pre_submit_failed`, `handoff_entered`, `accepted`, `submission_rejected`, `submission_unknown`, `observation_only`), API status, job/correlation ID, safe URLs, stage/state, persistence outcomes, and optional synthesis-latency seconds;
  * strict enum/hash/run/week validation;
  * `canonical_identity_key` as a stable SHA-256-derived value suitable for workflow concurrency and markers;
  * stable canonical JSON serialization and parsing for `podcast_dispatch_receipt_v2`;
  * v1 parser adapter preserving three-field evidence as legacy, never silently fabricating manifest identity;
  * paginated GitHub Issue lookup/comments using exact ledger marker/title, accepting evidence only from `github-actions[bot]` and the expected repository/workflow/run;
  * artifact JSON parser;
  * incident identity/key calculation.
* Excluded: secrets, request payload, article body/title, response body, automatic Podcaster retry.

#### Likely Targets

* `scripts/podcast_dispatch_state.py`:
  * constants `RECEIPT_SCHEMA_VERSION_V2`, `STATUS_SCHEMA_VERSION_V1`, `LEDGER_MARKER`, `LEDGER_TITLE`;
  * dataclasses `CanonicalPublicationIdentity`, `DispatchReceipt`, `TerminalStatus`, `MonitorResult`;
  * functions `canonical_identity_key`, `parse_receipt`, `serialize_receipt`, `list_ledger_receipts`, `append_ledger_receipt`, `incident_key`;
  * CLI subcommands `write-receipt`, `monitor`, `upsert-incident`, and `reconcile-incidents`.
* `tests/test_podcast_dispatch_state.py`: round-trip, invalid input, pagination, safe fields, and stable-key tests.

#### Dependencies

* Python standard library only; existing `GH_TOKEN`, `GITHUB_REPOSITORY`, and GitHub API version.

#### Validation Expectations

```bash
python -m pytest -q tests/test_podcast_dispatch_state.py
ruff check scripts/podcast_dispatch_state.py tests/test_podcast_dispatch_state.py
ruff format --check scripts/podcast_dispatch_state.py tests/test_podcast_dispatch_state.py
```

#### Completion Evidence

* Deterministic JSON/key snapshots and pagination tests.
* Explicit assertion that secret-like fields and arbitrary payload/body fields are rejected or omitted.

#### Unresolved Items

* None.

<!-- rpi:task id=P01-T02 -->
### P01-T02: Refactor detector to full identity and scoped ambiguity

#### Context

Affected symbols are `DispatchIdentity`, `_receipt_identity_matches`, `_extract_dispatch_identity_from_log_outputs`, `_identity_from_sync_commit`, `_compat_identity_for_run`, `_check_duplicate_cli`, `check_duplicate_result`, and `check_duplicate`. Current CLI/workflow inputs stop at article SHA.

#### Intent

Require the full identity and ensure only demonstrably related evidence can block it.

#### Boundaries

* Included:
  * import/use the canonical identity type;
  * add `manifest_sha256` extraction from logs and trusted `origin/publish` manifest bytes;
  * require `--manifest-sha256` in duplicate CLI and `check_duplicate_result`;
  * output `identity_key` for the workflow concurrency group;
  * read v2 Issue/artifact receipts first, then v1/log compatibility evidence;
  * classify runs as `blocking`, `ambiguous_exact`, `retryable_non_mutation`, `unrelated`, or `non_mutation`;
  * maintain `submitted`/accepted and unknown exact fail-closed semantics.
* Excluded: increasing safety by globally blocking unidentified runs; treating API/history retrieval failure as proof of safety.

#### Likely Targets

* `scripts/auto_dispatch_detect.py`: symbols listed above, receipt state sets, GitHub history access, CLI help.
* `.github/workflows/auto-podcast-dispatch.yml`: give `detect` `issues: read` plus existing `actions: read`; pass `MANIFEST_SHA256`/`--manifest-sha256`; expose `identity_key`; use `podcast-dispatch-${{ needs.detect.outputs.identity_key }}` as the concurrency group.
* `tests/test_auto_dispatch_detect.py`: update `_receipt_log` helper and identity calls.

#### Dependencies

* P01-T01.

#### Validation Expectations

Tests must distinguish:

1. v2 same week/run/article but different manifest → unrelated;
2. v2 exact accepted/unknown/pre-start states;
3. v1 exact reconstruction from trusted manifest;
4. cancelled auto run with empty jobs, zero steps, and empty ZIP unrelated to request → clear;
5. the same run when trusted metadata maps it to exact identity → ambiguous;
6. unreadable jobs/logs with no exact association → clear;
7. unreadable evidence after exact association → ambiguous;
8. legacy observe-only → nonblocking.
9. `attempt_prepared` and `pre_submit_failed` → retryable known non-mutation;
10. `handoff_entered` without acknowledgement → exact ambiguity/blocking.

#### Completion Evidence

```bash
python -m pytest -q tests/test_auto_dispatch_detect.py tests/test_podcast_dispatch_state.py
```

The test mock asserts no Podcaster mutation and records the exact classification reason.

#### Unresolved Items

* `check_duplicate_api` is a legacy fail-open API retained for compatibility but must not remain on the protected workflow path. If it has no callers after refactor, leave it deprecated rather than remove it under the zero-removal lock.

<!-- rpi:phase id=P02 -->
## P02: Enforce durable receipt ordering around mutation

### Context

The protected job currently validates exact publish evidence and then calls `podcaster_handoff.py`; only an `always()` step prints the receipt afterward. Required crash safety needs a retryable preparation phase and one durable handoff-entry boundary immediately before the call. Diagnostic artifact failure must not manufacture submission uncertainty.

### Intent

Make every mutation attempt durably identifiable without conflating preparation with possible mutation, then independently persist acknowledgements after invocation.

### Boundaries

* Included: safe handoff outputs, explicit prepare/persist/mutate/acknowledge state machine, authoritative Issue ledger pre/post append, non-authoritative artifact mirrors, workflow ordering, observation receipt.
* Excluded: terminal success, automatic retry, Podcaster changes.

### Likely Targets

* `scripts/podcaster_handoff.py`
* `.github/workflows/auto-podcast-dispatch.yml`
* `tests/test_podcaster_handoff.py`
* `tests/test_pipeline.py`

### Dependencies

* P01 complete.
* Existing protected environment and exact manifest revalidation preserved.

### Validation Expectations

* Structural workflow tests prove `attempt_prepared`, mirror handling, and `handoff_entered` ordering before handoff.
* Failure-injection tests prove every pre-`handoff_entered` failure sends zero requests and remains retryable.
* Post-write tests prove ledger and artifact persistence are attempted independently.

### Completion Evidence

* One accepted attempt yields ordered `attempt_prepared`, `handoff_entered`, then `accepted`.
* Response loss yields `submission_unknown`.
* Retry after `attempt_prepared`/`pre_submit_failed` may call once; retry after `handoff_entered`/`accepted`/`submission_unknown` does not call Podcaster again.

### Unresolved Items

* None.

<!-- rpi:task id=P02-T01 -->
### P02-T01: Expose safe handoff API and correlation status

#### Context

`post_handoff` knows the numeric HTTP status but discards it. `write_action_outputs` currently emits job ID and response status. `PodcasterHandoffError` carries only receipt state.

#### Intent

Expose the minimum safe metadata required by the durable post-receipt.

#### Boundaries

* Included:
  * add safe `api_status` to successful response handling;
  * add optional safe `correlation_id`, falling back to `job_id`;
  * carry numeric/reason-category API status through `PodcasterHandoffError`;
  * output `podcaster_http_status` and `podcaster_correlation_id`;
  * preserve existing `podcaster_job_id`, `podcaster_status`, and receipt state.
* Excluded: response body persistence, API key output, payload logging.

#### Likely Targets

* `scripts/podcaster_handoff.py`: `PodcasterHandoffError`, `validate_response`, `write_action_outputs`, `write_action_receipt_state`, `post_handoff`, `main`.
* `tests/test_podcaster_handoff.py`: safe-output, 2xx, HTTP error, URL error, malformed response, and secret absence tests.

#### Dependencies

* None beyond P01 schema.

#### Validation Expectations

* Known 2xx produces numeric status plus accepted job/correlation.
* HTTP rejection produces `submission_rejected` with numeric status.
* URL/parse/validation uncertainty produces `submission_unknown` with a non-secret category.

#### Completion Evidence

```bash
python -m pytest -q tests/test_podcaster_handoff.py
```

#### Unresolved Items

* None.

<!-- rpi:task id=P02-T02 -->
### P02-T02: Gate mutation on durable handoff entry and independently persist acknowledgement

#### Context

The workflow already has `manifest-locate`, `handoff`, and `Retain real generation evidence`. This task replaces inline receipt construction with state-helper commands and adds issue/artifact durability.

#### Intent

Order the workflow so pre-handoff failures remain provably retryable, while no request can be sent without a durable fail-closed handoff-entry record.

#### Boundaries

* Included:
  * job-scoped `issues: write` and `actions: read` only where required;
  * attempt ID `${github.run_id}-${github.run_attempt}`;
  * exact ledger lookup/create with marker;
  * **prepare:** construct and locally validate a receipt after manifest validation; failure creates no durable state, sends zero requests, and is retryable;
  * **persist preparation:** append authoritative `attempt_prepared`; append failure sends zero requests and is retryable;
  * **mirror preparation:** upload `podcast-dispatch-pre-receipt` with `retention-days: 90`; on failure append `pre_submit_failed`, fail the job, send zero requests, and remain retryable. If compensation append also fails, `attempt_prepared` is still a defined retryable non-mutation state;
  * **enter mutation:** append authoritative `handoff_entered` only after preparation and mirror succeed. Append failure sends zero requests and leaves the prior retryable state. Successful append is the sole fail-closed uncertainty boundary;
  * **mutate:** call handoff exactly once immediately after `handoff_entered`; runner loss or failure from this point through acknowledgement blocks redispatch and routes to reconciliation;
  * **acknowledge:** construct `accepted`, proven `submission_rejected`, or `submission_unknown`; run ledger append and artifact upload as separate `if: always()` steps with independent `continue-on-error` outcome capture, then execute a final assertion that preserves job failure and reconciliation if either required write failed;
  * create durable `observation_only` receipt/artifact only when full identity exists;
  * leave `no_anchor` without mutation receipt.
* Excluded: invoking after any failed pre-boundary operation, treating artifact presence as authoritative, mutable overwrite of old receipts.

#### Likely Targets

* `.github/workflows/auto-podcast-dispatch.yml`:
  * `detect.outputs.manifest_sha256`;
  * `Check for duplicate dispatch`;
  * `real-generation.permissions`;
  * new `Prepare mutation receipt`, `Persist prepared receipt`, `Mirror prepared receipt`, and `Persist handoff-entered boundary` steps;
  * existing `Trigger podcast generation`;
  * replacement independent `Persist post receipt to ledger`, `Upload post receipt mirror`, and `Assert post persistence` steps;
  * `observe-summary` observation receipt.
* `tests/test_pipeline.py`: parse YAML and assert order, `if`, permissions, retention, names, and exact four-field inputs.

#### Dependencies

* P01-T01 CLI and P02-T01 outputs.

#### Validation Expectations

Workflow contract and failure-injection tests assert:

1. prepare < `attempt_prepared` append < mirror < `handoff_entered` append < handoff < both post persistence paths < final assertion;
2. prepare failure, ledger-preparation failure, mirror failure, and `handoff_entered` append failure each send zero requests and leave a retryable latest authoritative state;
3. crash/runner loss after `handoff_entered` but before acknowledgement blocks retry even if no API response was captured;
4. post ledger failure does not suppress artifact upload, post artifact failure does not suppress ledger append, and either failure leaves the workflow failed/reconcilable without a second handoff;
5. artifact action is pinned and retention is 90;
6. `issues: write` is not workflow-global;
7. no-anchor path cannot reach receipt/handoff/monitor;
8. observe-only cannot reach `real-generation`;
9. concurrency uses detector output `identity_key`, a stable digest of all four identity fields, while dedup remains authoritative.

#### Completion Evidence

```bash
python -m pytest -q tests/test_pipeline.py tests/test_podcaster_handoff.py
```

#### Unresolved Items

* None. The ledger is authoritative; artifact mirroring is required but non-authoritative, and the explicit pre-boundary compensation semantics prevent false permanent uncertainty.

<!-- rpi:phase id=P03 -->
## P03: Reconcile terminal outcome, latency, and incidents

### Context

Research C15-C17 establishes that `accepted` only proves API admission. SquadScope must consume, but not implement, Podcaster terminal evidence and must remain visibly safe if the contract is absent.

### Intent

Turn accepted work into measured synthesis-start latency plus either exact externally verified success or a bounded incident-backed failure.

### Boundaries

* Included: status adapter, deadline-aware polling state machine, synthesis-start latency warning, evidence correlation, workflow finalizer, issue upsert/close.
* Excluded: Podcaster endpoint deployment, provider mutation, automatic resubmission.

### Likely Targets

* `scripts/podcast_dispatch_state.py`
* `.github/workflows/auto-podcast-dispatch.yml`
* `tests/test_podcast_dispatch_state.py`
* `tests/test_pipeline.py`

### Dependencies

* Accepted post-receipt from P02.
* `PODCASTER_STATUS_ENDPOINT` configuration and compatible Podcaster response for a successful production outcome.

### Validation Expectations

* Fake-clock/no-sleep tests for request, polling, warning, cleanup, and workflow bounds.
* Workflow finalizer executes after failed/skipped/successful real-generation as applicable.

### Completion Evidence

* Accepted without synthesis start by 600 seconds creates/updates a warning incident and continues monitoring; absent terminal evidence at the hard bound is failing and incident-backed.
* Exact externally verified completion is success and reconciles only matching incidents.

### Unresolved Items

* Podcaster deployment remains follow-up; its absence is an expected tested failure mode.

<!-- rpi:task id=P03-T01 -->
### P03-T01: Implement bounded terminal monitor

#### Context

The candidate contract is `podcast_publication_status_v1`. It must echo the accepted job/correlation ID and the full canonical identity to prevent cross-job evidence confusion.

#### Intent

Implement deterministic status interpretation, actionable accepted-to-synthesis-start telemetry, and hard request/runtime deadlines.

#### Boundaries

* Included:
  * GET the configured full status endpoint with identity/job query parameters;
  * authenticate through the existing API-key header without logging it;
  * validate schema and exact correlation;
  * accepted receipt `created_at` is the latency start; first exact authoritative response with synthesis `started|succeeded` supplies the end timestamp; compute non-negative integer `dispatch_to_synthesis_seconds`;
  * emit latency and safe dimensions (`identity_key`, dispatch run/attempt, correlation ID, threshold state) to `$GITHUB_STEP_SUMMARY` and the next safe receipt/incident comment; do not emit title/body/payload/secrets;
  * warning threshold 600 seconds: if synthesis has not started, upsert `synthesis_latency/warning` once per deterministic incident key and continue monitoring; later exact synthesis start records measured latency, and exact terminal success reconciles the warning;
  * evidence-acquisition deadline 3,480 seconds, poll interval 30 seconds, max consecutive transport/schema errors five;
  * per-request connect/read timeout `min(10 seconds, positive remaining evidence budget)`; do not start a request with no remaining budget;
  * truncate sleep to the remaining evidence budget;
  * reserve seconds 3,480-3,600 for final classification, receipt/summary emission, and incident upsert; workflow `timeout-minutes: 61` is the platform backstop for setup/teardown plus the bounded state machine;
  * stage states:
    * synthesis: `pending`, `started`, `succeeded`, `failed`, `unknown`;
    * video: `pending`, `succeeded`, `failed`, `unknown`;
    * provider: `pending`, `published`, `failed`, `unknown`;
  * success only when synthesis is `started|succeeded`, video is `succeeded`, provider is `published`, and `external_verified` is true;
  * immediate failure on mismatched evidence or authoritative failed/unknown terminal state;
  * timeout classification by first incomplete stage.
* Excluded: blind repeat of create/publish, acceptance-only success, infinite retry.

#### Likely Targets

* `scripts/podcast_dispatch_state.py`: `fetch_terminal_status`, `validate_terminal_status`, `evaluate_terminal_status`, `monitor_terminal_outcome`.
* `tests/test_podcast_dispatch_state.py`: table-driven state transitions and fake monotonic clock/sleep.

#### Dependencies

* Accepted receipt and P02 job/correlation outputs.

#### Validation Expectations

Test cases include:

* no synth start at 600 seconds → `synthesis_latency/warning`, continuing;
* no synth start by evidence deadline → `synthesis/timeout`;
* synth started, video pending by deadline → `video/timeout`;
* video succeeded, provider pending by deadline → `provider/timeout`;
* missing/malformed field → `evidence_schema/invalid`;
* identity/job mismatch → `evidence_mismatch/rejected`;
* five transport failures → `evidence_unavailable/error_budget_exhausted`;
* a hung request returns at the 10-second/remaining-budget cap and consumes one error;
* final sleep is truncated and no request starts after the evidence deadline;
* timely synthesis emits latency without warning; late synthesis emits latency after one deduplicated warning;
* terminal provider unknown/failed → visible failure;
* exact verified success → terminal success.

#### Completion Evidence

```bash
python -m pytest -q tests/test_podcast_dispatch_state.py
```

#### Unresolved Items

* The endpoint route and Podcaster-side storage are Podcaster-owned. SquadScope accepts a full configured URL rather than deriving an unsupported route.

<!-- rpi:task id=P03-T02 -->
### P03-T02: Add deduplicated incident lifecycle and workflow finalizer

#### Context

Existing workflows use `gh issue list/comment/create`; this task follows that repository convention but uses a deterministic hidden marker rather than title-only matching.

#### Intent

Guarantee every incomplete/unknown accepted attempt is visible and deduplicated.

#### Boundaries

* Included:
  * incident key over canonical identity + failed stage + state;
  * label `podcast-dispatch-incident`;
  * issue body marker `<!-- podcast-dispatch-incident:v1:<key> -->`;
  * exact safe evidence and recovery text;
  * create-or-comment with race re-check;
  * finalizer job with `needs: [detect, real-generation]` and `if: always()`;
  * treat `attempt_prepared`/`pre_submit_failed` as known non-mutation no-op/retryable, detect a `handoff_entered` acknowledgement gap as blocking uncertainty, handle rejected/unknown post states, and monitor accepted states;
  * verified success comments/closes all open incident issues whose exact identity marker matches.
* Excluded: closing incidents for another manifest/article/run; retrying Podcaster; exposing secrets.

#### Likely Targets

* `scripts/podcast_dispatch_state.py`: `upsert_incident`, `reconcile_identity_incidents`, latency summary/evidence, finalizer CLI exit codes.
* `.github/workflows/auto-podcast-dispatch.yml`: new `reconcile` job with `timeout-minutes: 61`; narrow `actions: read`, `issues: write`, `contents: read`; download current receipts; invoke monitor/upsert.
* `tests/test_pipeline.py`: finalizer dependency/condition/permissions and accepted-success gating.

#### Dependencies

* P03-T01.

#### Validation Expectations

* Repeated identical failure makes one create and later comments.
* Repeated 600-second synthesis warning makes one issue/update, continues polling, and exact terminal success closes the exact warning.
* Different stage/state uses a distinct key.
* Same job but different manifest digest cannot share an incident.
* Monitor restart consumes accepted receipt and does not call handoff.
* Incident-upsert failure still leaves the workflow failed and reports the safe incident key in summary.
* The finalizer attempts classification/incident persistence inside the reserved 120-second cleanup budget and never redispatches.

#### Completion Evidence

```bash
python -m pytest -q tests/test_podcast_dispatch_state.py tests/test_pipeline.py
```

#### Unresolved Items

* None.

<!-- rpi:phase id=P04 -->
## P04: Complete locked regression and validation evidence

### Context

The finalized plan locks test ownership and disallows removals/gate weakening. Workflow edits require both semantic tests and repository security scanners.

### Intent

Prove the change against the incident matrix and all affected repository gates.

### Boundaries

* Included: four owned test modules, focused checks, full tests, lint/format, dependency/security/workflow scans, hosted smoke.
* Excluded: suppressions, skip additions, baseline weakening, unrelated cleanup.

### Likely Targets

* `tests/test_auto_dispatch_detect.py`
* `tests/test_podcaster_handoff.py`
* `tests/test_podcast_dispatch_state.py`
* `tests/test_pipeline.py`
* `.copilot-tracking/changes/2026-09-21/podcast-dispatch-identity-reconciliation-changes.md`

### Dependencies

* P01-P03.

### Validation Expectations

* Execute focused checks first, then full repository gates exactly as locked in the plan.

### Completion Evidence

* Changes record captures command, version where relevant, result, and failure disposition.
* No validation is reported as passed if skipped, weakened, or not executed.

### Unresolved Items

* Hosted smoke may require environment approval; waiting for approval is not grounds to bypass it.

<!-- rpi:task id=P04-T01 -->
### P04-T01: Implement locked semantic and regression matrix

#### Context

Tests must distinguish semantic safety assertions from reproductions of W38/W39 evidence shapes.

#### Intent

Complete coverage without deleting existing assertions.

#### Boundaries

* Included:
  * update helper signatures for manifest digest;
  * add exact four-field mismatch/equality tests;
  * model empty ZIP and empty job/step run;
  * cover v1 reconstruction and v2 ledger/artifact precedence;
  * cover receipt crash boundaries and duplicate call counts;
  * cover monitor/incident table, accepted-to-synthesis latency telemetry, request/deadline bounds, and workflow structure;
  * assert secrets/payload content absent.
* Excluded: network integration in unit tests, Podcaster repo tests, broad unrelated test refactors.

#### Likely Targets

* Test ownership exactly as listed in plan `Test and Change Ownership Lock`.

#### Dependencies

* Implemented production/workflow changes.

#### Validation Expectations

* Maximum one new test file (`tests/test_podcast_dispatch_state.py`).
* Existing test names may be updated only when signature/identity wording changes; behavior assertions remain or strengthen.
* Locked additions include timely synthesis latency, 600-second warning dedup, absent synthesis timeout, hung request, remaining-budget request cap, truncated final sleep, cleanup reserve, `timeout-minutes: 61`, mirror failure before handoff, `handoff_entered` crash, and both post dual-write failure directions.

#### Completion Evidence

```bash
python -m pytest -q \
  tests/test_auto_dispatch_detect.py \
  tests/test_podcaster_handoff.py \
  tests/test_podcast_dispatch_state.py \
  tests/test_pipeline.py
```

#### Unresolved Items

* None.

<!-- rpi:task id=P04-T02 -->
### P04-T02: Run focused and repository-standard gates

#### Context

Repository instructions require Python tests, Ruff, Checkov for workflows, Zizmor, and Podcaster smoke. CI additionally runs pip-audit and security scanning.

#### Intent

Produce complete, reproducible readiness evidence.

#### Boundaries

* Included: every command in the plan's required validation block and hosted checks.
* Excluded: changing dependencies merely to avoid a scanner/test result; broad unrelated fixes.

#### Likely Targets

* No target changes expected; failures caused by this implementation are fixed in their owning files.
* `.copilot-tracking/changes/2026-09-21/podcast-dispatch-identity-reconciliation-changes.md`: command evidence.

#### Dependencies

* P04-T01.

#### Validation Expectations

* Focused tests/lint precede full suite.
* Scanner versions match baselines where available.
* Any environment/tool absence is recorded and the equivalent required hosted gate must pass before PR readiness.

#### Completion Evidence

* All required local and hosted results are green with no new ignore/suppression.

#### Unresolved Items

* None.

<!-- rpi:phase id=P05 -->
## P05: Deliver review branch and independent review handoff

### Context

The caller requires a pushed branch, independent review before PR creation, future PR links, and follow-up lifecycle. `Coordinator#17` will be linked as requested but not represented as the incident authority.

### Intent

Make the implementation persistent, reviewable, and correctly routed.

### Boundaries

* Included: changes record, clean scoped diff, branch push, review handoff, follow-up recording, and future-PR evidence preparation.
* Excluded: merging without review, modifying Podcaster, auto-closing unrelated Coordinator issue.

### Likely Targets

* Git branch/remote and review metadata.
* `.copilot-tracking/changes/2026-09-21/podcast-dispatch-identity-reconciliation-changes.md`.

### Dependencies

* Local P04-T02 evidence complete. Hosted checks remain required after independent review opens the PR.

### Validation Expectations

* `git diff --check`, scoped status/diff review, and remote branch verification.

### Completion Evidence

* Pushed commit(s), exact future-PR links, validation summary, and independent review routing recorded.

### Unresolved Items

* None.

<!-- rpi:task id=P05-T01 -->
### P05-T01: Record evidence and push review branch

#### Context

Delivery must preserve the pre-existing dirty worktree. Implementation stages must include only task-owned changes and must not discard or commit unrelated modifications.

#### Intent

Publish a focused review branch without opening the PR before independent review.

#### Boundaries

* Included:
  * inspect task-owned diff and `git diff --check`;
  * update changes record with tests, scanners, hosted evidence, assumptions, and known Podcaster dependency;
  * commit only task-owned files;
  * push current completed branch;
  * prepare evidence for a later PR with W38/W39 incident evidence, implementation/identity and receipt semantics, focused/full validation results, known Podcaster status-contract dependency, safe rollback point, principal risks/residual latency-threshold risk, non-closing `Related: jmservera/SquadScope-Coordinator#17`, and fully-qualified Podcaster references;
  * do not open the PR before independent review.
* Excluded: reset/stash/clean of unrelated dirty files, force push unless branch policy explicitly requires it, `Closes` for Coordinator #17.

#### Likely Targets

* Git/PR state only plus implementation changes record.

#### Dependencies

* P04-T02.

#### Validation Expectations

```bash
git diff --check
git status --short
git diff --stat
```

#### Completion Evidence

* Remote branch exists and the review handoff contains the future PR requirements:
  * W38/W39 run evidence and why unrelated legacy ambiguity no longer poisons identity;
  * local and hosted validation results with any environment-qualified evidence;
  * explicit dependency on Podcaster `podcast_publication_status_v1` deployment/configuration;
  * rollback that retains four-field identity and durable ledger evidence;
  * principal risks: exact post-entry uncertainty, external contract availability, persistent ledger growth, and the initial 600-second warning threshold;
  * fully-qualified links to `jmservera/SquadScope-Coordinator#17`, `jmservera/SquadScope-Podcaster#678`, `#679`, `#681`, `#682`, and PR `jmservera/SquadScope-Podcaster#680`, without auto-closing Coordinator#17.
* The changes record stores the pushed branch/commit and a checked mapping to every required future PR section/reference.

#### Unresolved Items

* None.

<!-- rpi:task id=P05-T02 -->
### P05-T02: Route independent implementation review and follow-up

#### Context

Plan critique and implementation review are distinct gates. Exactly one plan critique has completed before implementation; after the review branch is pushed, an independent implementation review assesses actual changes against plan and evidence before PR creation.

#### Intent

Complete the requested lifecycle without self-review substitution.

#### Boundaries

* Included: provide plan, details, critique/dispositions, changes record, pushed diff/branch, and validation evidence to independent review; record follow-ups by owner.
* Excluded: running a second plan critique, treating planner verification as independent implementation review, absorbing Podcaster-owned work into SquadScope acceptance.

#### Likely Targets

* `.copilot-tracking/reviews/logs/2026-09-21/podcast-dispatch-identity-reconciliation-review.md` owned by the review stage, not this planning stage.
* `.copilot-tracking/critiques/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md` is the sole completed plan critique supplied to implementation review.
* Plan `Follow-Up Items` and changes record if review routes follow-up.

#### Dependencies

* P05-T01.

#### Validation Expectations

* Review explicitly checks identity, mutation ordering, terminal evidence, incidents, tests, security, and scope.

#### Completion Evidence

* Independent verdict and every finding disposition; accepted residual work has a named owner/reference.

#### Unresolved Items

* None.
