<!-- markdownlint-disable-file -->
# RPI Review: Podcast Dispatch Identity Reconciliation

## Scope and Evidence

* Task ID: SS-PODCAST-DISPATCH-IDENTITY-RECONCILIATION-2026-09-21
* Review date: 2026-09-21
* Review scope: Full approved task at pushed commit `304d08d59f36f5f7286fa97d44add4a1e75be9dc`
* Assessed boundary: Caller requirements, approved plan and details, sole critique dispositions, changes evidence, incident evidence, complete `main...HEAD` production/test/tracking diff, local validation, delivery readiness, and explicit hosted/follow-up work.
* Plan: .copilot-tracking/plans/2026-09-21/podcast-dispatch-identity-reconciliation-plan.md
* Phase details: .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md
* Plan critique: .copilot-tracking/critiques/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md
* Changes: .copilot-tracking/changes/2026-09-21/podcast-dispatch-identity-reconciliation-changes.md
* Other evidence considered: .copilot-tracking/research/2026-09-21/podcast-dispatch-identity-reconciliation-research.md; branch/worktree Git state; changed workflow, production scripts, and tests; independently executed validation where practical.

## Opening Review State

* Interpreted review goal: Conduct one fresh evidence-based acceptance review of the pushed implementation against the complete approved plan and caller boundary, without modifying any artifact except this canonical review record.
* Review scope: Full task, including P01-P05 evidence and all plan follow-up items.
* Evidence readiness: The requested research, plan, details, critique, and changes artifacts exist; the worktree is on the requested branch and exact commit; the complete `main...HEAD` change list is available. The changes record declares execution Partial because hosted checks and this independent review remain open.
* Acceptance basis: The ten caller review boundaries; plan FR-01 through FR-11, NFR-01 through NFR-08, acceptance criteria, critique dispositions PC-001 through PC-006, locked test/change limits, incident evidence, and delivery sequencing.
* First comparison boundary: Reconcile plan markers and critique dispositions with actual production/workflow/test behavior, then independently assess validation and delivery evidence. No acceptance outcome is inferred from artifact summaries alone.
* Active read-only boundaries: Source, tests, workflows, planning artifacts, changes record, Git history, and remote are read-only. This review may write only this file.
* Initial blockers: None. Hosted checks are unavailable before the required post-review PR and will be assessed as remaining delivery work rather than presumed passed.

## Execution Status

* Execution status: Partial
* Review execution evidence: The one requested review is complete against commit `304d08d59f36f5f7286fa97d44add4a1e75be9dc`. Production, workflow, test, tracking, Git, remote-branch, and practical local-validation evidence was compared. Implementation execution remains Partial because hosted gates, PR creation, and defect correction are not complete.

## Plan-to-Change Reconciliation

| Current plan scope | Descriptive changes-record summary | Current-state reconciliation | Gap or rationale |
|---|---|---|---|
| P01 / P01-T01 / P01-T02 | Four-field identity, v2 receipts, and identity-scoped history | Partial | Four-field construction and matching exist, but ledger authentication and fail-open evidence retrieval prevent reliable durable dedup. See RV-001 and RV-002. |
| P02 / P02-T01 / P02-T02 | Safe handoff metadata and prepare → persist → mirror → handoff-entered → mutate → acknowledge ordering | Partial | Workflow ordering and safe response metadata are present. The Issue ledger cannot authenticate, so the required durable boundary cannot operate. See RV-001. |
| P03 / P03-T01 / P03-T02 | Terminal monitor, latency, incidents, and finalizer | Partial | Success requires synth/video/provider evidence, but restart timing, cleanup bounds, evidence classification, ledger fallback, and incident authentication do not meet the accepted contract. See RV-001, RV-003, RV-004, RV-005, and RV-006. |
| P04 / P04-T01 / P04-T02 | Locked regression matrix and validation | Partial | The recorded 142 focused and 1,748 full tests reproduce, as do Ruff, Bandit, Checkov, Zizmor, smoke, and diff checks. Tests omit the material production paths in RV-001 through RV-006. Hosted checks remain unavailable by sequencing; pip-audit was not reproducible from the retained environment. |
| P05 / P05-T01 / P05-T02 | Push branch, independent review, then PR and hosted follow-up | Partial | Commit `304d08d5` is pushed and no PR exists. This review completes P05-T02's review gate, but the High findings block PR creation. Hosted checks and PR delivery remain distinct follow-up after correction. |
| Follow-Up Items | Podcaster contract deployment, environment configuration, ledger retention policy, Coordinator reference clarification, post-review PR | Reconciled | These remain correctly outside active implementation acceptance. They do not cure the implementation defects and remain separately owned. |

## Completed Work Assessment

| Related marker | Files | What changed and why | Completion evidence | Validation | Assessment |
|---|---|---|---|---|---|
| P01 | `scripts/auto_dispatch_detect.py`; `scripts/podcast_dispatch_state.py`; detector/state tests; workflow | Added four-field identity, stable key, v2 receipt parsing, and scoped legacy classification. | Manifest-only mismatch and exact-state tests pass; workflow passes all four fields. | Focused and full tests pass. | Identity construction is substantially present; operational dedup is not accepted because trusted evidence retrieval fails open and the ledger client cannot authenticate. |
| P02 | `scripts/podcaster_handoff.py`; workflow; handoff/pipeline tests | Added numeric API status, correlation ID, ordered durable states, independent post writes, and 90-day mirrors. | Structural order and safe-output tests pass. | Focused and full tests pass. | Response minimization and YAML order conform; durable Issue writes are nonfunctional with the shipped header. |
| P03 | `scripts/podcast_dispatch_state.py`; workflow; state/pipeline tests | Added polling, terminal predicate, latency warning, incidents, and reconciliation job. | Unit tests prove the modeled happy/timeout/error cases. | Focused and full tests pass. | Acceptance gaps remain in authoritative receipt recovery, accepted-time bounds, cleanup bounds, mismatch classification, trust validation, and incident writes. |
| P04 | Four owned test modules | Added the locked semantic/structural suite within the file-addition cap. | 142 focused and 1,748 full tests reproduce. | Passed except hosted and independently reproducible pip-audit evidence. | Test counts conform, but exact behavior coverage is incomplete because several assertions lock unsafe or overly mocked behavior. |
| P05-T01 | All task-owned files and Git state | Committed and pushed the review branch without opening a PR. | Remote branch contains requested commit; `gh pr list` returns no PR. | `git diff --check` passes. | Conformant to review-before-PR sequencing. |

## Implementation-Time Plan and Detail Update Assessment

| Affected area or marker | What changed and why | Triggering evidence and user decision | Reconciliation performed | Planning and critique state | Assessment |
|---|---|---|---|---|---|
| Metadata; P01-T01 | Activated full-plan implementation. | Caller requested full-plan implementation. | Plan, details, and changes record identify active/completed markers. | Sole critique retained. | Reconciled. |
| FR-11; P05-T01 / P05-T02 | Pushed branch before review and deferred PR until after review. | Explicit caller review gate. | Plan/details/changes record reflect the sequence. | No additional critique required. | Reconciled. |
| PC-001 / PC-002 | Added latency warning, request cap, evidence deadline, cleanup reserve, and 61-minute timeout. | Accepted critique corrections. | Plan and details describe concrete bounds. | Disposition recorded as Resolved. | Implementation only partially applies the correction; accepted-time restart behavior and cleanup work remain unbounded. See RV-004. |
| PC-003 / PC-004 | Added retryable pre-boundary states and independent post persistence attempts. | Accepted critique corrections. | Plan, details, workflow order, and tests align descriptively. | Disposition recorded as Resolved. | YAML ordering is reconciled, but operational persistence and authoritative fallback are defective. See RV-001 and RV-003. |
| PC-005 / PC-006 | Added PR evidence requirements and corrected critique paths. | Accepted critique corrections. | Plan/details/changes use the authorized critique artifact and defer PR. | Disposition recorded as Resolved. | Reconciled; PR work remains follow-up. |

## Critique and Material Revision Assessment

* Latest critique dispositions: PC-001 through PC-006 are each dispositioned once in the plan. The revised planning text preserves confirmed caller intent and correctly uses the authorized critique path.
* Material revisions: The plan revision was planning-ready and did not require a second critique. Implementation diverges from the resolved intent for PC-001/PC-002 and PC-004 through defects rather than an approved decision.
* Dependent-work pause assessment: PR creation correctly remained paused for independent review. It must remain paused for RV-001 through RV-004 because they are High functional defects.
* Justification assessment: Delivery sequencing and external Podcaster dependency are justified. The unsafe implementation behaviors are not justified divergences and require correction under the existing plan.

## Plan Follow-Up Assessment

| Follow-up item | Why outside immediate scope | Owner or next action | Assessment and route |
|---|---|---|---|
| Deploy `podcast_publication_status_v1` | Podcaster-owned contract deployment was explicitly excluded. | Podcaster owner; related `jmservera/SquadScope-Podcaster#678`, `jmservera/SquadScope-Podcaster#679`, `jmservera/SquadScope-Podcaster#681`, `jmservera/SquadScope-Podcaster#682`, and `jmservera/SquadScope-Podcaster#680`. | Open distinct follow-up; not a SquadScope defect. |
| Configure `PODCASTER_STATUS_ENDPOINT` | Requires deployed Podcaster contract and protected environment administration. | Operations owner after deployment. | Open distinct follow-up; intended visible failure remains the accepted interim behavior. |
| Decide Issue-ledger archival/rotation | Initial retention policy was explicitly deferred. | Repository owner before operational limits are approached. | Open distinct follow-up; not required for initial implementation correction. |
| Clarify `jmservera/SquadScope-Coordinator#17` wording | The issue is unrelated but the caller requires a non-closing reference. | Coordinator/delivery owner when drafting the PR. | Open distinct follow-up. |
| Open PR and run hosted gates | Correctly sequenced after independent review. | Delivery owner after RV-001 through RV-006 are fixed. | Blocked follow-up; later correction does not require another Review. |

## Findings

<!-- rpi:review id=RV-001 -->
### RV-001 [High]: Durable ledger and incident requests discard the GitHub token

* Related scope: P01-T01, P02-T02, P03-T02; FR-03, FR-09, NFR-06
* Evidence: `scripts/podcast_dispatch_state.py` `_github_headers` returns the literal `Authorization: ******` for every Issue ledger and incident request. A direct probe with a sentinel token returned `******`. The workflow relies on these calls for `attempt_prepared`, `handoff_entered`, post acknowledgement, observations, warnings, terminal incidents, and reconciliation.
* Impact: Issue writes cannot authenticate. Normal real generation fails at the first authoritative prepared-receipt append and cannot reach Podcaster; observe-only persistence and incident lifecycle also fail. The core durable receipt and visible-failure design is nonfunctional.
* Destination: `rpi-implement`
* Smallest useful next action: Send the provided token using the repository-standard GitHub authorization scheme, add request-header tests that assert the token is carried without logging it, and exercise authenticated ledger append/read and incident create/comment paths through mocked HTTP requests.

<!-- rpi:review id=RV-002 -->
### RV-002 [High]: Duplicate detection treats complete evidence outages as clear to mutate

* Related scope: P01-T02; FR-02, FR-04, NFR-01, NFR-04, NFR-07
* Evidence: `scripts/auto_dispatch_detect.py` `check_duplicate_result` catches ledger/history failures and returns `DuplicateCheckResult(status="clear", is_duplicate=False)` when both retrieval attempts fail. `tests/test_auto_dispatch_detect.py::test_api_failure_non_blocking` explicitly locks this behavior. A direct probe reproduced `clear False`.
* Impact: An exact identity with an accepted, `handoff_entered`, or `submission_unknown` durable receipt may be dispatched again whenever GitHub evidence is unavailable. This converts absence of evidence into retry safety and violates the approved monotonic fail-closed idempotency rule.
* Destination: `rpi-implement`
* Smallest useful next action: Return a visible blocking/ambiguous result when trusted ledger or history needed for exact-identity safety cannot be read, keep demonstrably unrelated individual legacy runs nonblocking, and replace the fail-open regression with outage/fallback tests that prove no second handoff.

<!-- rpi:review id=RV-003 -->
### RV-003 [High]: Reconciliation ignores the authoritative ledger and depends on the diagnostic artifact

* Related scope: P02-T02, P03-T02; FR-03, FR-04, FR-10, NFR-04
* Evidence: `.github/workflows/auto-podcast-dispatch.yml` `reconcile` downloads only `podcast-dispatch-post-receipt`; if the file is absent it records `acknowledgement_missing`. It never calls `list_ledger_receipts` to recover the exact post receipt, although the plan declares the Issue ledger authoritative and artifacts diagnostic.
* Impact: A successful accepted ledger append plus failed artifact upload/download cannot enter terminal monitoring and is misclassified as missing acknowledgement. Monitor restart after artifact expiry has the same failure. This breaks independent post-write recovery, authoritative receipt semantics, and the required restart behavior.
* Destination: `rpi-implement`
* Smallest useful next action: Resolve the exact attempt/identity receipt from the trusted ledger first, use the artifact only as a diagnostic mirror or validated fallback, and add both post-write failure-direction plus artifact-expiry/restart tests.

<!-- rpi:review id=RV-004 -->
### RV-004 [High]: Terminal monitoring resets accepted-time deadlines and does not enforce the cleanup bound

* Related scope: P03-T01 / P03-T02; FR-08, NFR-02
* Evidence: `scripts/podcast_dispatch_state.py` starts the 3,480-second deadline and 600-second warning from each monitor process's `monotonic()` start, not from the accepted receipt timestamp. The timestamp is used only for latency through non-injected `time.time()`. `TOTAL_MONITOR_BUDGET_SECONDS` is unused. Warning and final incident GitHub operations can page up to 100 pages with 20-second requests and have no remaining-cleanup-budget cap. A two-hour-old accepted receipt probe waited on the new monitor clock and emitted no warning before the test deadline.
* Impact: Restarting reconciliation can grant another full evidence window and delay the required warning; incident/summary work can exceed the reserved 120 seconds and be terminated by the 61-minute workflow backstop without the required classified incident. The accepted PC-001/PC-002 correction is not implemented.
* Destination: `rpi-implement`
* Smallest useful next action: Derive warning and evidence deadlines from `receipt.created_at`, inject/test wall time consistently, persist or deterministically reconstruct warning state, and pass a hard remaining cleanup budget through bounded GitHub lookups/writes so classification plus incident attempt completes before 3,600 seconds.

<!-- rpi:review id=RV-005 -->
### RV-005 [Medium]: Identity/schema evidence failures are collapsed into a generic transport error

* Related scope: P03-T01; FR-07, FR-08, FR-09
* Evidence: `monitor_terminal_outcome` catches all `ValueError` from `validate_terminal_status`, retries them, and after five failures returns `evidence_unavailable/error_budget_exhausted`. A direct identity-mismatch probe made five attempts and produced the generic result. The plan requires immediate `evidence_mismatch/rejected` and distinct invalid-schema/missing-stage classifications.
* Impact: Cross-identity evidence and incompatible contracts are not reported with their authoritative stage/state, delaying failure and deduplicating incidents under the wrong key. Operators lose the recovery signal required by the accepted status contract.
* Destination: `rpi-implement`
* Smallest useful next action: Use typed validation failures or explicit result mapping so identity/job mismatch fails immediately as `evidence_mismatch/rejected`, schema/stage failures use their specified classifications, and only transport failures consume the consecutive-error budget.

<!-- rpi:review id=RV-006 -->
### RV-006 [Medium]: Ledger trust checks do not verify the expected workflow

* Related scope: P01-T01; NFR-05
* Evidence: `list_ledger_receipts` checks comment author, repository URL, strict receipt schema, and a syntactically matching Actions run URL. It does not retrieve or verify that `dispatch_run_id` belongs to the expected repository workflow, despite the explicit accepted requirement and test lock for wrong-workflow evidence.
* Impact: Any repository workflow running as `github-actions[bot]` with Issue-write permission can append a structurally valid blocking receipt for an arbitrary run ID and exact identity. The detector may then block or establish success from evidence outside the trusted dispatch workflow.
* Destination: `rpi-implement`
* Smallest useful next action: Validate the referenced run through the GitHub Actions API against repository and expected workflow path/ID, cache bounded lookups, and add forged-author, wrong-repository, wrong-run, and wrong-workflow tests.

<!-- rpi:review id=RV-007 -->
### RV-007 [Low]: Hosted validation and PR delivery remain unfinished

* Related scope: P04-T02, P05-T02
* Evidence: No PR exists for `incident/podcast-dispatch-identity-reconciliation`; therefore required hosted CI, lint, Checkov, security scanning, and protected Podcaster smoke have not run. Local pip-audit could not be independently rerun because the retained interpreter has no `pip_audit` module and the disposable environment recorded by implementation is absent.
* Impact: Merge/readiness evidence is incomplete even after functional defects are corrected. This is expected sequencing, not a source defect.
* Destination: distinct follow-up
* Smallest useful next action: After RV-001 through RV-006 are fixed and pushed, open the required PR, run all protected hosted checks without weakening gates, and record the PR/hosted outcomes; retain reproducible pip-audit command/version evidence.

## Defects

* RV-001 through RV-006 are implementation defects routed to `rpi-implement`.

## Routed Findings

| Finding | Destination | Owner or next action | Reason for route |
|---|---|---|---|
| RV-001 | `rpi-implement` | Correct GitHub authentication and add operational request tests. | Functional durable-state defect within the approved design. |
| RV-002 | `rpi-implement` | Replace evidence-outage fail-open behavior with exact-safety fail-closed semantics. | Idempotency defect within the approved design. |
| RV-003 | `rpi-implement` | Reconcile from the authoritative ledger before artifact fallback. | Receipt durability/restart defect within the approved design. |
| RV-004 | `rpi-implement` | Anchor bounds to acceptance and enforce cleanup budget. | Terminal-monitor defect within the approved design. |
| RV-005 | `rpi-implement` | Preserve explicit mismatch/schema classifications. | Status-contract defect within the approved design. |
| RV-006 | `rpi-implement` | Verify referenced run repository/workflow trust. | Operational-evidence trust defect within the approved design. |
| RV-007 | Distinct follow-up | Delivery owner opens the corrected PR and completes hosted/reproducible validation. | Non-blocking delivery evidence that is intentionally post-review/post-fix. |

Later implementation of routed findings does not require another Review.

## Residual Work

* RV-007: post-fix PR creation and hosted validation.
* Existing plan follow-ups remain separately owned: Podcaster status-contract deployment, protected-environment configuration, Issue-ledger retention policy, and required non-closing reference wording.

## Blockers and Remaining Work

* Blockers: RV-001, RV-002, RV-003, and RV-004 are High functional defects. PR creation is blocked until they are fixed; RV-005 and RV-006 should be corrected in the same `rpi-implement` continuation because they are accepted-plan gaps in the same surfaces.
* Remaining active work: P04-T02 hosted evidence and P05 post-review PR delivery remain open. The current implementation should not be represented as PR-ready.

## Validation Evidence

| Command | Scope | Status | Summary |
|---|---|---|---|
| `python3 -m pytest -q tests/test_auto_dispatch_detect.py tests/test_podcaster_handoff.py tests/test_podcast_dispatch_state.py tests/test_pipeline.py` | Focused changed behavior | Passed | 142 passed in 2.85s. |
| `python3 -m pytest -q tests/` | Full repository Python tests | Passed | 1,748 passed, 2 existing warnings, in 53.89s. |
| Focused `ruff check` and `ruff format --check` | Seven changed Python/test files | Passed | All checks passed; 7 files formatted. |
| `ruff check .` and `ruff format --check .` | Full repository | Passed | All checks passed; 194 files formatted. |
| `bandit -q -c .bandit.yaml -r .` | Repository | Passed | Exit 0; informational comment-token warnings only. |
| `checkov --directory . --framework github_actions dockerfile secrets ... --compact` | Workflow, Dockerfile, secret policies | Passed | Checkov 3.2.533: 1,065 passed, 0 failed, 7 skipped. |
| `zizmor --persona regular --min-severity medium .github/workflows/` | All workflows | Passed | Zizmor 1.25.2: no findings; 27 ignored and 100 suppressed by existing baseline/configuration. |
| Changed-script `--help` invocations | CLI import smoke | Passed | All three changed scripts exited 0. |
| `git diff --check main...HEAD` | Complete branch diff | Passed | No whitespace errors. |
| Git/remote/PR inspection | Branch delivery | Passed / Open | Requested commit is on `origin/incident/podcast-dispatch-identity-reconciliation`; no PR exists. |
| Dependency/safety diff inspection | Gate and dependency integrity | Passed | Requirements, CI, lint, Checkov, security, smoke, and baseline files are unchanged. No Podcaster repository file is in the SquadScope branch diff. |
| `python3 -m pip_audit -r requirements.txt` | Dependency audit | Unavailable | Current retained interpreter reports no `pip_audit` module; implementation records a pass from a removed disposable environment. |
| Hosted CI/lint/Checkov/security/smoke | PR/hosted | Unavailable | No PR exists by required review-before-PR sequencing. |
| Direct production-behavior probes | GitHub header, dedup outage, monitor mismatch/restart | Failed acceptance | Reproduced literal `******` authorization, `clear False` on complete evidence outage, generic five-retry mismatch result, and warning/deadline reset from monitor start. |

## Outcome

* Outcome: Not accepted
* Outcome rationale: The implementation includes substantial plan-conformant structure and reproduces all claimed test counts, but High defects make the durable ledger/incident path nonfunctional, allow duplicate mutation during evidence outages, ignore the authoritative ledger during reconciliation, and violate accepted-time/cleanup bounds. These defects block PR creation. No new planning decision or research gap is required; the approved direction remains valid and the complete correction set is routed to implementation.

## Closeout Routing Record

| Finding class | Destination | Owner or next action |
|---|---|---|
| Implementation defect | `rpi-implement` | Correct RV-001 through RV-006 under the current approved plan and push the fixes. |
| Decision gap or invalid assumption | None | No unaccepted product/design decision remains; defects are implementation divergence. |
| Material evidence gap | None | Current evidence is sufficient for the verdict; pip-audit/hosted results are delivery follow-up rather than research. |
| Non-blocking residual work | Distinct follow-up | After fixes, open the PR, run hosted gates/smoke, and complete the existing external/operational follow-ups. |

* Execution status: Partial
* Outcome: Not accepted
* Validation coverage: Focused 142 and full 1,748 tests, focused/full Ruff, Bandit, Checkov, Zizmor, CLI smoke, diff/scope/remote checks, and direct defect probes completed; pip-audit and hosted checks unavailable.
* Blockers: RV-001 through RV-004 block PR creation; RV-005 and RV-006 remain required implementation corrections.

## Relevant Artifacts

| Artifact | Description |
|---|---|
| [.copilot-tracking/research/2026-09-21/podcast-dispatch-identity-reconciliation-research.md](.copilot-tracking/research/2026-09-21/podcast-dispatch-identity-reconciliation-research.md) | Incident, current-state, and cross-repository contract evidence. |
| [.copilot-tracking/plans/2026-09-21/podcast-dispatch-identity-reconciliation-plan.md](.copilot-tracking/plans/2026-09-21/podcast-dispatch-identity-reconciliation-plan.md) | Approved implementation and acceptance plan. |
| [.copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md](.copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md) | Approved phase and task behavior details. |
| [.copilot-tracking/critiques/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md](.copilot-tracking/critiques/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md) | Sole plan critique and PC-001 through PC-006 findings. |
| [.copilot-tracking/changes/2026-09-21/podcast-dispatch-identity-reconciliation-changes.md](.copilot-tracking/changes/2026-09-21/podcast-dispatch-identity-reconciliation-changes.md) | Implementation summary, markers, validation claims, and delivery state. |
| [.copilot-tracking/reviews/logs/2026-09-21/podcast-dispatch-identity-reconciliation-review.md](.copilot-tracking/reviews/logs/2026-09-21/podcast-dispatch-identity-reconciliation-review.md) | Canonical independent implementation review and routing record. |

## Next Steps

Run `/rpi-implement` against `.copilot-tracking/plans/2026-09-21/podcast-dispatch-identity-reconciliation-plan.md` to implement RV-001 through RV-006. Keep PR creation blocked until those fixes are pushed; afterward complete RV-007 and the existing distinct follow-ups. No second Review is required.
