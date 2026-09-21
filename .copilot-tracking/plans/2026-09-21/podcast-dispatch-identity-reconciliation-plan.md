<!-- markdownlint-disable-file -->
# RPI Plan: Podcast Dispatch Identity Reconciliation

## Task Metadata

* Task ID: SS-PODCAST-DISPATCH-IDENTITY-RECONCILIATION-2026-09-21
* Task slug: podcast-dispatch-identity-reconciliation
* Planning status: Implementation in progress; local P04-T02 evidence complete, P05-T01 active, hosted gates deferred until the post-review PR
* Plan date: 2026-09-21
* Phase details: .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md
* Plan critique: .copilot-tracking/critiques/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md

## Executive Summary

This finalized plan fixes the W38/W39 failure mode by making podcast-dispatch history decisions apply only to the full canonical publication identity: `week`, `publish_run_id`, `article_sha256`, and `manifest_sha256`. A cancelled or unreadable historical run with no demonstrable relationship to that tuple will no longer poison unrelated publications. Evidence tied to the exact identity remains fail-closed.

Before the protected Podcaster mutation, the workflow will prepare a secret-free receipt, append authoritative `attempt_prepared` evidence to a GitHub Issue ledger, and attempt a required 90-day artifact mirror. Any failure before the durable `handoff_entered` transition sends zero requests and remains safely retryable; mirror failure records `pre_submit_failed`. Immediately before invoking Podcaster, the workflow must durably append `handoff_entered`. From that point, a crash or missing acknowledgement blocks automatic retry and enters reconciliation. Post-call ledger and artifact writes run independently so one persistence failure cannot suppress the other.

An always-running reconciliation job will require accepted work to produce machine-readable evidence of synthesis start, video terminal state, and authoritative provider outcome. It uses a 58-minute evidence-acquisition deadline, 30-second polling, 10-second deadline-capped HTTP calls, five consecutive evidence errors, a reserved 2-minute incident/summary cleanup window, and a 61-minute workflow timeout backstop. It measures accepted-to-synthesis-start latency, warns at 10 minutes, and continues toward terminal evidence. Missing configuration, stages, timeout, failure, or unknown provider state fails visibly and opens or updates a canonical-identity incident. Only `video=succeeded` and `provider=published` with `external_verified=true` establishes success.

### User Decisions and Requirements Highlights

* Preserve idempotency and exact-identity fail-closed behavior; do not convert uncertainty into a retry.
* Keep active implementation in SquadScope. Podcaster work is a separate contract follow-up, and SquadScope must fail visibly until terminal evidence is available.
* Cover empty cancelled runs, `no_anchor`, observe-only, unrelated legacy ambiguity, exact-identity ambiguity, mutation crashes, monitor restarts, and missing terminal stages.
* Keep all existing CI and safety gates; push the completed branch and open a PR with the required fully-qualified references.

### What You May Not Know

* Current `DispatchIdentity` omits `manifest_sha256` even though the workflow already computes and prints it.
* Current receipt evidence is parsed from expiring run logs; the proposed Issue ledger is the authoritative append-only state record, while 90-day artifacts are required diagnostic mirrors but never determine retry safety.
* `jmservera/SquadScope-Coordinator#17` is unrelated closed yearly-rollup work according to research. The PR will link it exactly as requested but must not claim it is the incident authority or use an auto-close keyword.
* Podcaster's machine-readable status transport is not proven deployed. The SquadScope adapter contract is explicit below; absent configuration or incompatible evidence is an intentional visible failure, not a silent success.

### Unresolved Decisions or Blockers

* None for SquadScope implementation. The Podcaster terminal contract remains an external deployment dependency: absent or incompatible `PODCASTER_STATUS_ENDPOINT` evidence intentionally produces a visible `status_contract/unavailable` incident rather than success or redispatch.
* The 10-minute synthesis-latency warning is an initial operational threshold because production percentiles are unavailable. It is configurable within the hard monitor bounds and is an accepted residual tuning risk, not an implementation blocker.

For current user input, see [User Decisions and Requirements](#user-decisions-and-requirements). The planner keeps the synthesized sections below current as evidence and caller direction evolve.

## User Decisions and Requirements

* Follow a thorough Research → Plan → Implementation → independent Review → Follow-up lifecycle, with exactly one independent plan critique before implementation.
* Deduplicate by canonical publication identity: week, publish run, article digest, and manifest digest.
* Unknown legacy identity must not block demonstrably unrelated identities; uncertainty for the exact identity remains fail-closed.
* Add regression coverage for cancelled runs with empty jobs/steps/logs, `no_anchor`, observe-only, unrelated ambiguous historical submissions, and exact-identity ambiguity.
* Persist secret-free canonical handoff receipts around mutation with dispatch run, publication identity, attempt/API status, and Podcaster job/correlation ID; persistence failure before handoff entry must remain provably non-mutating and retryable.
* Bound terminal monitoring through synthesis start, video terminal state, and authoritative provider outcome; measure dispatch-accepted-to-synthesis-start latency, warn before the terminal deadline, and make missing stages visibly fail with a deduplicated incident.
* Preserve idempotency and fail-closed exact ambiguity.
* Use focused and repository-standard validation without weakening CI or safety gates.
* Push the completed branch for independent review. Do not open the PR until that review completes; the later PR must link `jmservera/SquadScope-Coordinator#17` and related fully-qualified Podcaster work.
* Coordinate conceptually with Podcaster without modifying `/home/azureuser/source/SquadScope-Podcaster`.

## Goals

* Scope all duplicate and ambiguity decisions to the four-field canonical publication identity.
* Establish durable, ordered, secret-free evidence with an explicit retryable preparation state and fail-closed handoff-entry boundary.
* Reconcile accepted work to authoritative terminal evidence within deterministic request, polling, cleanup, and workflow bounds, including actionable synthesis-start latency.
* Create actionable, deduplicated incidents without automatically repeating an ambiguous provider mutation.
* Deliver reviewable SquadScope changes with locked regression ownership and complete validation evidence.

## Scope and Non-Goals

### In Scope

* `scripts/auto_dispatch_detect.py` identity, receipt compatibility, historical-run classification, and duplicate CLI changes.
* `scripts/podcaster_handoff.py` safe API status and correlation outputs.
* One new SquadScope state/reconciliation helper, `scripts/podcast_dispatch_state.py`.
* `.github/workflows/auto-podcast-dispatch.yml` receipt ordering, artifact retention, reconciliation, permissions, and incident wiring.
* Existing detector, handoff, and workflow contract tests plus one new reconciliation/state test module.
* Implementation evidence, branch push, PR creation, and independent implementation review handoff.

### Non-Goals

* Any modification to `/home/azureuser/source/SquadScope-Podcaster`.
* Inventing or claiming deployment of a Podcaster endpoint.
* Automatic retry after `handoff_entered`, `submission_unknown`, response loss, or ambiguous provider mutation.
* Treating HTTP 2xx/`accepted`, synthesis start, or video completion alone as publication success.
* Rewriting historical v1 receipts or requiring old runs to gain unavailable evidence.
* Changing publish generation, article/manifest generation, protected environment approval, or unrelated workflows.
* Weakening or skipping tests, Ruff, Checkov, Bandit, Zizmor, pip-audit, or smoke gates.

## Functional Requirements

* **FR-01 Canonical identity:** `CanonicalPublicationIdentity` contains validated `week`, `publish_run_id`, `article_sha256`, and `manifest_sha256`; equality, concurrency naming, receipt matching, dedup, monitor correlation, and incident keys use all four fields.
  * Observable acceptance criteria: changing only `manifest_sha256` produces a different identity and cannot match a submitted receipt for another manifest; detector output `identity_key` is the stable SHA-256-derived workflow concurrency suffix.
* **FR-02 Identity-scoped legacy classification:** v2 receipts compare all four fields. A v1/log-only run may affect a request only when its identity is reconstructed from trusted publish evidence or its run metadata/logs demonstrably associate it with the requested identity.
  * Observable acceptance criteria: a cancelled run with empty jobs/steps/logs is unrelated and nonblocking unless trusted evidence maps it to the exact identity; exact mapped uncertainty returns `ambiguous_prior_submission`.
* **FR-03 Durable mutation receipts:** append `podcast_dispatch_receipt_v2` JSON to a dedicated Issue ledger and upload artifact mirrors with `retention-days: 90`; the ledger is authoritative and mirrors are diagnostic.
  * Observable acceptance criteria: prepare creates no durable state; `attempt_prepared` proves mutation has not begun and is retryable; mirror failure records `pre_submit_failed` and sends zero requests; `handoff_entered` is durably appended immediately before the sole `podcaster_handoff.py` invocation; post-call states include dispatch run ID, attempt ID, identity, API status, receipt state, and safe job/correlation ID.
* **FR-04 Crash and retry semantics:** retry eligibility is reduced across all trusted receipts for the exact identity. Any `handoff_entered`, `accepted`, or `submission_unknown` evidence is monotonic blocking and cannot be superseded by a later retryable receipt. Only when no blocking evidence exists, missing/failed `attempt_prepared`, `attempt_prepared`, and `pre_submit_failed` are known non-mutation states and may retry. `submission_rejected` is retryable only when the captured HTTP/category contract proves rejection occurred before acceptance; otherwise it is normalized to `submission_unknown`.
  * Observable acceptance criteria: crash during prepare or before `handoff_entered` is retryable; failure persisting `handoff_entered` prevents invocation and remains retryable; crash after its successful append is blocked even if invocation did not complete; accepted acknowledgement prevents a second handoff.
* **FR-05 Non-mutation states:** `no_anchor` emits no mutation receipt and cannot enter terminal monitoring. Observe-only emits a durable `observation_only` artifact/ledger record but is never duplicate, submission, or terminal-success evidence.
  * Observable acceptance criteria: both paths send zero Podcaster requests.
* **FR-06 Handoff output:** `post_handoff`, `write_action_outputs`, and `PodcasterHandoffError` expose only safe status metadata: numeric HTTP status when known, response status, returned `job_id`, and optional `correlation_id` (falling back to `job_id`).
  * Observable acceptance criteria: API keys, request payload content, and response bodies are absent from receipts and incidents.
* **FR-07 Terminal status contract:** `PODCASTER_STATUS_ENDPOINT` is queried with accepted job/correlation ID and the full identity. It must return `schema_version=podcast_publication_status_v1`, matching identity/job values, `synthesis.state`, `video.state`, `provider.state`, and `provider.external_verified`.
  * Observable acceptance criteria: mismatched identity/job evidence is rejected as `evidence_mismatch`; absent endpoint is `status_contract/unavailable`.
* **FR-08 Bounded reconciliation and latency telemetry:** from the accepted receipt timestamp, poll every 30 seconds with each HTTP request capped at `min(10 seconds, remaining evidence budget)`. Stop evidence acquisition at 3,480 seconds, after five consecutive transport/schema failures, or on authoritative terminal failure; reserve 120 seconds for classification, incident upsert, and summary, with reconciliation job `timeout-minutes: 61`.
  * Observable acceptance criteria: sleeps truncate to remaining budget; no request starts without positive budget; monitor classification plus incident attempt completes within 3,600 seconds under the fake clock; accepted-to-first-authoritative-`synthesis=started|succeeded` latency is emitted in whole seconds to the job summary and safe receipt/incident evidence; at 600 seconds without synthesis start, upsert `synthesis_latency/warning` and continue monitoring; later start records latency and exact-identity success reconciles the warning.
* **FR-09 Incident lifecycle:** create or comment on an open issue using key `sha256("podcast-dispatch-incident-v1\0" + canonical_identity + "\0" + stage + "\0" + state)`.
  * Observable acceptance criteria: repeated identical failures update one issue; safe evidence includes run URL, identity, job/correlation ID, stage/state, and recovery rule; terminal success comments on and closes open incidents for that exact identity only.
* **FR-10 Workflow result:** the reconciliation job runs with `if: always()` after detection and real generation. Accepted work cannot leave the workflow successful unless terminal evidence passes.
  * Observable acceptance criteria: missing post-receipt, monitor timeout, contract absence, stage failure, or provider uncertainty fails the job after incident upsert.
* **FR-11 Delivery:** implementation creates the changes record, commits and pushes the completed branch, and hands it to independent review before PR creation.
  * Observable acceptance criteria: the pushed branch and review handoff include W38/W39 incident evidence, local validation, known Podcaster contract dependency, safe rollback point, principal risks, and the fully-qualified references required for the later PR.

## Non-Functional Requirements

* **NFR-01 Idempotency:** no code path may call Podcaster when any trusted receipt for the exact identity is `handoff_entered`, accepted/submitted, or unknown/in-flight; later retryable preparation evidence cannot override it.
  * Objective threshold or evaluation condition: duplicate-delivery and restart tests observe exactly one mocked handoff call.
  * Observable acceptance criteria: exact ambiguity always blocks until authoritative reconciliation.
* **NFR-02 Bounded operation:** evidence polling is at most 3,480 seconds, total monitor classification/incident work is budgeted to 3,600 seconds, interval is 30 seconds, request timeout is at most 10 seconds and remaining-budget capped, consecutive evidence errors are at most five, and the workflow backstop is 61 minutes.
  * Observable acceptance criteria: constants/CLI validation plus fake-clock, hung-request, truncated-sleep, cleanup-margin, and workflow-structure tests enforce every bound.
* **NFR-03 Data minimization:** receipts/incidents contain identifiers, enum states, timestamps, hashes, safe URLs, and numeric status only.
  * Observable acceptance criteria: tests assert API key and payload/article content never appear.
* **NFR-04 Compatibility and retention:** read v1 log receipts and v2 Issue/artifact receipts; write only v2. Artifact mirrors retain 90 days; Issue ledger comments are the authoritative durable append-only source and are not automatically deleted. Artifact failure cannot convert a known pre-handoff failure into submission uncertainty.
  * Observable acceptance criteria: v1 semantic tests remain passing, v2 round-trip tests pass, and retry classification uses ledger state rather than mirror presence.
* **NFR-05 Trusted operational evidence:** treat Issue bodies/comments and downloaded artifacts as untrusted input. Accept ledger records only from the repository's `github-actions[bot]`, with strict schema/field validation and a dispatch run that belongs to the expected repository/workflow.
  * Observable acceptance criteria: forged-author, malformed JSON, wrong-repository, and wrong-workflow records are ignored and cannot block or establish success.
* **NFR-06 Least privilege:** only the detector gets `issues: read`/`actions: read`; only receipt/incident jobs receive `issues: write`; protected mutation keeps `contents: read` and the existing environment.
  * Observable acceptance criteria: workflow contract tests and Zizmor/Checkov report no new blocking findings.
* **NFR-07 Safe failure:** unavailable or malformed terminal evidence fails visibly but never causes a second mutation.
  * Observable acceptance criteria: every failure state has a nonzero workflow result and incident key.
* **NFR-08 Repository quality:** use Python 3.12, Ruff formatting/lint rules, existing urllib/GitHub CLI conventions, pinned actions, and no new runtime dependency.
  * Observable acceptance criteria: locked validation commands pass without manifest changes.

## Acceptance Criteria

* Full four-field identity is used consistently across detector input, receipt matching, concurrency/dedup state, monitor correlation, and incidents.
* Unrelated empty/unreadable cancelled history does not block; exact-identity unreadable or unknown evidence does.
* `attempt_prepared`/`pre_submit_failed` proves no mutation and permits retry; only successful `handoff_entered` persistence crosses the fail-closed boundary; a handoff-entry/post gap blocks redispatch.
* Observe-only is durably observable but never counted as submission; `no_anchor` cannot emit a mutation receipt or monitor success.
* Accepted work must prove synthesis start, successful video terminal state, and externally verified provider publication.
* Missing contract/stage, mismatched evidence, timeout, provider unknown/failure, and monitor restart produce deterministic visible behavior and deduplicated incidents; synthesis-start latency is measured, summarized, and warned at 600 seconds.
* No secrets or article/payload content enter receipts, artifacts, summaries, or incidents.
* Focused tests, full Python tests, Ruff, Checkov, Bandit, Zizmor, pip-audit, and the Podcaster smoke workflow evidence are recorded before PR readiness.
* No source/test/workflow removal occurs; no more than two implementation files are added, excluding the implementation changes-record artifact.
* Exactly one independent plan critique is complete; PC-001 through PC-006 are dispositioned below and no second critique is requested or permitted.
* Completed implementation is pushed and routed to independent implementation review before the PR is opened; the later PR carries the required fully-qualified links.

## Implementation Context Record

| Context item | Current artifact or record |
|---|---|
| Plan | .copilot-tracking/plans/2026-09-21/podcast-dispatch-identity-reconciliation-plan.md |
| Phase details | .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md |
| Latest critique | .copilot-tracking/critiques/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md; Revise verdict resolved by PC-001 through PC-006 dispositions |
| Relevant research | .copilot-tracking/research/2026-09-21/podcast-dispatch-identity-reconciliation-research.md |
| Changes-record role | .copilot-tracking/changes/2026-09-21/podcast-dispatch-identity-reconciliation-changes.md is created by implementation as the evidence record |
| Planning execution and readiness | Planning complete; Ready for implementation with one accepted external-contract/tuning residual risk |
| Continuation context | Return ready artifacts to the requesting parent for implementation handoff; do not run another plan critique |

## Sources

* .squad/agents/leela/charter.md: Lead/architect ownership of interfaces and review gates.
* .squad/decisions.md: Trusted article/manifest correlation, prior dedup defenses, pause/alert behavior, protected approval, and W37 protection.
* .copilot-tracking/research/2026-09-21/podcast-dispatch-identity-reconciliation-research.md: W38/W39 incident evidence, current symbols, mutation seam, tests, cross-repository contracts, and planning-ready recommendations.
* scripts/auto_dispatch_detect.py: `DispatchIdentity`, `_receipt_identity_matches`, `_compat_identity_for_run`, `check_duplicate_result`, receipt states, and finite history behavior.
* scripts/podcaster_handoff.py: `PodcasterHandoffError`, `validate_response`, `write_action_outputs`, `write_action_receipt_state`, `post_handoff`, and `main`.
* .github/workflows/auto-podcast-dispatch.yml: `detect`, `real-generation`, `observe-summary`, manifest revalidation, handoff, and current log receipt steps.
* tests/test_auto_dispatch_detect.py, tests/test_podcaster_handoff.py, tests/test_pipeline.py: current semantic and workflow-contract ownership.
* .github/copilot-instructions.md and docs/devsecops/checkov-baseline.md / docs/devsecops/zizmor-baseline.md: repository validation and safety gates.
* `jmservera/SquadScope-Podcaster#678`, `#679`, `#681`, `#682`, and PR `#680`: conceptual terminal-evidence contracts; no local Podcaster modification.
* Authoritative caller requirements dated 2026-09-21.

## Phase Checklist

<!-- rpi:phase id=P01 -->
### [x] P01: Establish canonical state and identity-scoped history

* Intent: centralize v2 identity/receipt semantics and stop unrelated legacy ambiguity from acting as a global blocker.
* Dependencies: one independent critique completed; PC-001 through PC-006 resolved in this plan.

<!-- rpi:task id=P01-T01 -->
#### [x] P01-T01: Add canonical state and receipt model

* Requirement and evidence: FR-01, FR-03, FR-04; research C9-C13 and C19-C22.
* Expected result: new `scripts/podcast_dispatch_state.py` validates identity, serializes/parses v2 receipts, reads the Issue ledger/artifact JSON, and computes stable incident keys.
* Detail section: P01-T01 in .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md

<!-- rpi:task id=P01-T02 -->
#### [x] P01-T02: Refactor detector to full identity and scoped ambiguity

* Requirement and evidence: FR-01, FR-02, FR-05; run 32730109166 and current `check_duplicate_result`.
* Expected result: detector and CLI require `manifest_sha256`; unrelated empty/unreadable history is ignored, while exact mapped uncertainty remains `ambiguous_prior_submission`.
* Detail section: P01-T02 in .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md

<!-- rpi:phase id=P02 -->
### [x] P02: Enforce durable receipt ordering around mutation

* Intent: make mutation eligibility and outcome durable, correlated, and crash-safe.
* Dependencies: P01.

<!-- rpi:task id=P02-T01 -->
#### [x] P02-T01: Expose safe handoff API and correlation status

* Requirement and evidence: FR-06 and NFR-03; current `post_handoff` and action outputs.
* Expected result: handoff emits safe HTTP/status/job/correlation metadata without logging secrets or payloads.
* Detail section: P02-T01 in .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md

<!-- rpi:task id=P02-T02 -->
#### [x] P02-T02: Gate mutation on durable pre-receipt and persist post-receipt

* Requirement and evidence: FR-03-FR-05; protected `real-generation` mutation boundary.
* Expected result: `attempt_prepared` and mirror handling remain retryable, durable `handoff_entered` is the sole fail-closed boundary, and independent post-ledger/post-artifact acknowledgements are always attempted; observe-only is recorded separately.
* Detail section: P02-T02 in .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md

<!-- rpi:phase id=P03 -->
### [x] P03: Reconcile terminal outcome, latency, and incidents

* Intent: prevent accepted requests from being reported as successful without terminal publication evidence.
* Dependencies: P02 accepted/post receipt.

<!-- rpi:task id=P03-T01 -->
#### [x] P03-T01: Implement bounded terminal monitor

* Requirement and evidence: FR-07, FR-08, NFR-02, NFR-07; research C15-C17 and C21.
* Expected result: identity-bound status polling, request deadlines, synthesis-latency warning, cleanup reserve, and workflow timeout reach authoritative success or a bounded explicit failure.
* Detail section: P03-T01 in .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md

<!-- rpi:task id=P03-T02 -->
#### [x] P03-T02: Add deduplicated incident lifecycle and workflow finalizer

* Requirement and evidence: FR-09, FR-10; existing issue-upsert conventions.
* Expected result: always-running reconciliation fails visibly, upserts one issue per identity/stage/state, and reconciles only exact-identity incidents on verified success.
* Detail section: P03-T02 in .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md

<!-- rpi:phase id=P04 -->
### [ ] P04: Complete locked regression and validation evidence

* Intent: prove semantic safety and repository conformance before delivery.
* Dependencies: P01-P03.

<!-- rpi:task id=P04-T01 -->
#### [x] P04-T01: Implement locked semantic and regression matrix

* Requirement and evidence: caller regression list and research required test matrix.
* Expected result: owned tests cover identity, legacy evidence, crash boundaries, no-mutation paths, monitor stages, incidents, security, and workflow structure.
* Detail section: P04-T01 in .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md

<!-- rpi:task id=P04-T02 -->
#### [ ] P04-T02: Run focused and repository-standard gates

* Requirement and evidence: NFR-06-NFR-08 and repository instructions.
* Expected result: all listed commands and hosted smoke evidence pass without suppressions, skipped gates, or dependency changes.
* Detail section: P04-T02 in .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md

<!-- rpi:phase id=P05 -->
### [ ] P05: Deliver review branch and independent review handoff

* Intent: preserve implementation evidence, publish the completed branch, and route the change through independent review and follow-up.
* Dependencies: local P04-T02 evidence complete. Hosted gates remain mandatory after independent review opens the PR and before merge/readiness.

<!-- rpi:task id=P05-T01 -->
#### [ ] P05-T01: Record evidence and push review branch

* Requirement and evidence: FR-11 and caller delivery requirements, including independent review before PR creation.
* Expected result: changes record is current, the branch is committed and pushed, and the independent reviewer receives the W38/W39 evidence, local validation, Podcaster contract dependency, rollback point, principal risks, and required future-PR references.
* Detail section: P05-T01 in .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md

<!-- rpi:task id=P05-T02 -->
#### [ ] P05-T02: Route independent implementation review and follow-up

* Requirement and evidence: required lifecycle.
* Expected result: independent review compares plan/changes/tests/PR; accepted follow-ups are recorded without silently expanding this implementation.
* Detail section: P05-T02 in .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md

## Dependencies

* **Pre-implementation gate:** satisfied by the one completed critique at `.copilot-tracking/critiques/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md`; all PC-001 through PC-006 dispositions are recorded below.
* **GitHub Issues:** a dedicated ledger issue identified by exact title `Podcast dispatch receipt ledger`; workflow may create it if absent and must use exact marker `<!-- podcast-dispatch-ledger:v2 -->`. Pre-receipt failure blocks mutation.
* **GitHub Actions artifacts:** pinned `actions/upload-artifact` with `retention-days: 90`; artifacts are required diagnostic mirrors but do not replace the authoritative Issue ledger or determine retry safety.
* **Podcaster terminal contract:** `PODCASTER_STATUS_ENDPOINT` and existing API-key authentication; missing/incompatible contract is an explicit incident and failing workflow outcome.
* **Protected environment:** `podcaster-real-generation` approval remains required.
* **Cross-repository references:** Podcaster issues/PRs are contract evidence and follow-up ownership, not locally verified implementation.

## Test and Change Ownership Lock

### Exact removals

* None. No source, test, workflow, safety gate, or existing assertion is authorized for deletion.

### Maximum additions

* At most two implementation files:
  1. `scripts/podcast_dispatch_state.py`
  2. `tests/test_podcast_dispatch_state.py`
* The implementation-stage tracking record `.copilot-tracking/changes/2026-09-21/podcast-dispatch-identity-reconciliation-changes.md` is additionally created as required RPI evidence and is not production code.
* Any need for another production/test file is a plan deviation requiring planner disposition before implementation continues.

### Canonical and generated targets

* Canonical edited source: `scripts/auto_dispatch_detect.py`, `scripts/podcaster_handoff.py`, `scripts/podcast_dispatch_state.py`, `.github/workflows/auto-podcast-dispatch.yml`.
* Canonical edited tests: `tests/test_auto_dispatch_detect.py`, `tests/test_podcaster_handoff.py`, `tests/test_pipeline.py`, `tests/test_podcast_dispatch_state.py`.
* Generated runtime evidence: `podcast-dispatch-pre-receipt.json`, `podcast-dispatch-post-receipt.json`, and `podcast-dispatch-observation.json` inside workflow artifacts; never commit them. Pre-receipt JSON may represent `attempt_prepared`, `pre_submit_failed`, or `handoff_entered`, but the Issue ledger remains authoritative.
* Generated repository content/data: none.
* Dependency manifests: none.
* Documentation target: no standalone documentation addition; workflow summaries, PR description, changes record, and code help text carry operational detail. If implementation exposes operator configuration not adequately represented there, update an existing relevant runbook within the same file-addition cap (edit only).

### Semantic versus regression coverage

* Semantic ownership:
  * `tests/test_podcast_dispatch_state.py`: v2 schema, validation, Issue ledger parsing/writes, monitor state machine/bounds, status-contract correlation, incident key/upsert/reconcile, secret minimization.
  * `tests/test_auto_dispatch_detect.py`: four-field identity and legacy/v1 compatibility classification.
  * `tests/test_podcaster_handoff.py`: safe HTTP status and correlation outputs plus unknown/rejected semantics.
  * `tests/test_pipeline.py`: workflow ordering, permissions, retention, concurrency identity, finalizer, and no gate weakening.
* Regression ownership:
  * empty cancelled jobs/steps/log ZIP unrelated vs exact mapped;
  * `no_anchor` and observe-only non-mutation behavior;
  * unrelated ambiguous history and exact-identity ambiguity;
  * duplicate delivery and crash before pre, after pre, after acceptance/before post;
  * mirror failure and runner loss before `handoff_entered` remain zero-request/retryable, while crash after `handoff_entered` remains blocked;
  * independent post-ledger/post-artifact failure attempts and preserved failing reconciliation;
  * accepted job missing synth/video/provider evidence;
  * timely synthesis start, 600-second warning, no synthesis start, hung request, truncated sleep, and cleanup-margin bounds;
  * externally verified terminal success and monitor restart;
  * no secrets in receipts/incidents.

### Required validation evidence before PR readiness

```bash
python -m pytest -q \
  tests/test_auto_dispatch_detect.py \
  tests/test_podcaster_handoff.py \
  tests/test_podcast_dispatch_state.py \
  tests/test_pipeline.py
ruff check scripts/auto_dispatch_detect.py scripts/podcaster_handoff.py \
  scripts/podcast_dispatch_state.py tests/test_auto_dispatch_detect.py \
  tests/test_podcaster_handoff.py tests/test_podcast_dispatch_state.py tests/test_pipeline.py
ruff format --check scripts/auto_dispatch_detect.py scripts/podcaster_handoff.py \
  scripts/podcast_dispatch_state.py tests/test_auto_dispatch_detect.py \
  tests/test_podcaster_handoff.py tests/test_podcast_dispatch_state.py tests/test_pipeline.py
pytest tests/
ruff check .
ruff format --check .
python -m pip_audit -r requirements.txt
bandit -c .bandit.yaml -r .
checkov --directory . --framework github_actions dockerfile secrets \
  --skip-path node_modules --skip-path .venv --skip-path public \
  --skip-path resources --skip-path themes --compact
GH_TOKEN="$(gh auth token)" zizmor --persona regular --min-severity medium .github/workflows/
```

* Hosted evidence: required CI, lint, Checkov, security scanning, and `.github/workflows/podcaster-handoff-smoke.yml` must complete under their existing protection/approval rules. Do not substitute a dry local mock for hosted smoke evidence.
* If an installed local scanner version differs from the pinned repository baseline, record the version and rely on the pinned hosted result; do not alter baseline/suppressions to obtain green output.

## Rollback and Risk Notes

* **Safe rollback point:** revert monitor/incident activation while retaining v2 receipt reading/writing and four-field dedup. Do not roll back to global ambiguity or delete ledger evidence.
* **Receipt write outage:** prepare or `attempt_prepared`/`handoff_entered` append failure prevents mutation. `attempt_prepared`, mirror failure, and `pre_submit_failed` are known non-mutation states and remain retryable after Issues/artifact availability is restored.
* **Mutation-boundary runner loss:** only a successful authoritative `handoff_entered` append marks possible mutation. Runner loss from that point through acknowledgement blocks redispatch and requires readback/manual reconciliation.
* **Post-write outage:** ledger append and artifact upload are separate `if: always()` persistence attempts with independent outcome capture; failure of either keeps the workflow failed and reconciliation active, while the available path preserves evidence.
* **Podcaster status outage/schema drift:** monitor fails `status_contract` or `evidence_unavailable`; no redispatch occurs.
* **Issue-ledger growth:** comments are weekly/attempt scale and paginated. Artifact mirrors expire after 90 days; ledger comments persist until explicit operator retention policy changes.
* **Legacy evidence:** absence is never affirmative proof. Only trusted exact association may block; unrelated unknown history is ignored.
* **Incident races:** issue upsert searches exact marker/key and must re-check after create failure/race before creating another.
* **Provider semantics:** only authoritative `external_verified=true` publication closes success; `unknown` remains failed/reconcilable.
* **Latency threshold:** the initial 600-second warning is evidence-light because production percentiles are unavailable. Keep it configurable, record observed latency, and tune later without weakening the 3,480/3,600-second hard bounds.

## Critique Disposition

Exactly one independent critique was completed at `.copilot-tracking/critiques/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md`. Its `Revise` verdict is resolved in this coherent revision; no second critique is required or authorized.

| Finding | Disposition | Concrete correction or evidence-based rejection |
|---|---|---|
| PC-001 | Resolved | FR-08, NFR-02, P03, and P04 now measure accepted-receipt timestamp to first authoritative `synthesis=started|succeeded`, emit whole-second latency to safe receipt/incident evidence and the job summary, warn at 600 seconds, continue bounded monitoring, reconcile the warning on exact success, and require fake-clock tests for timely, warning, and absent-start cases. |
| PC-002 | Resolved | FR-08/NFR-02 and P03 now cap each HTTP request at 10 seconds and remaining budget, truncate sleeps, stop polling at 3,480 seconds, reserve 120 seconds for classification/incident/summary, and set `timeout-minutes: 61`; hung-request and cleanup-margin tests prove the bounded behavior. |
| PC-003 | Resolved first | The receipt machine now separates prepare → authoritative `attempt_prepared` → required mirror → authoritative `handoff_entered` → mutate → acknowledge. Any failure or crash before successful `handoff_entered` persistence is known non-mutation and retryable; mirror failure records `pre_submit_failed` and sends zero requests. Successful `handoff_entered` is the only transition that creates fail-closed submission uncertainty. |
| PC-004 | Resolved | Post-mutation ledger append and artifact upload are separate always-running, failure-independent steps with captured outcomes. Ledger remains authoritative; a final assertion preserves failure and reconciliation if either path fails, and tests prove neither write suppresses the other. |
| PC-005 | Resolved | P05-T01 and PR acceptance now require W38/W39 incident evidence, local and hosted validation, the undeployed Podcaster contract dependency, rollback point, principal risks, and all fully-qualified references; Coordinator#17 remains non-closing. |
| PC-006 | Resolved | All plan/detail metadata, dependencies, context, and handoff references use the caller-authorized `.copilot-tracking/critiques/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md` path and recognize this completed critique as the sole plan-critique gate. |

## Follow-Up Items

* **Podcaster owner:** deploy and document the `podcast_publication_status_v1` machine-readable readback contract for accepted `job_id`/correlation ID and full canonical identity. Related evidence/work: `jmservera/SquadScope-Podcaster#678`, `#679`, `#681`, `#682`, and PR `#680`.
* **Operations owner:** configure `PODCASTER_STATUS_ENDPOINT` in the protected environment after the Podcaster contract is available. Until then, SquadScope intentionally opens/deduplicates `status_contract/unavailable` incidents and fails reconciliation.
* **Repository owner:** decide any future Issue-ledger archival/rotation policy before GitHub operational limits are approached. The active implementation must paginate and retain the ledger; archival is not required for initial acceptance.
* **Coordinator:** clarify why closed unrelated `jmservera/SquadScope-Coordinator#17` must be linked if later PR wording needs more than a non-closing “Related” reference. This does not block the requested link.
* **Delivery owner after independent review:** open the PR only after review, using the required incident evidence, validation, rollback/risk sections, and fully-qualified non-closing references.

## Handoff

* Implementation artifact: .copilot-tracking/changes/2026-09-21/podcast-dispatch-identity-reconciliation-changes.md
* Ready phase or task: P01
* Remaining provisional question or blocker: none; Podcaster status deployment is an explicit external dependency with a safe failing behavior
* Implementation handoff: run `/rpi-implement` against this plan and use the implementation artifact above as the changes/evidence record; do not run another plan critique
