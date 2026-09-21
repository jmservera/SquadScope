<!-- markdownlint-disable-file -->
# RPI Plan Critique: Podcast Dispatch Identity Reconciliation

## Metadata

* Task ID: SS-PODCAST-DISPATCH-IDENTITY-RECONCILIATION-2026-09-21
* Critique date: 2026-09-21
* Plan: .copilot-tracking/plans/2026-09-21/podcast-dispatch-identity-reconciliation-plan.md
* Phase details: .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md
* Critique execution status: Complete

## Inputs and Criterion Boundary

* Task context and caller requirements: assessed all ten authoritative requirements supplied by jmservera, including four-field identity, scoped legacy ambiguity, locked regressions, durable pre/post receipts, bounded authoritative reconciliation, telemetry/alerts, preserved idempotency, full validation, independent review, and pushed PR delivery without Podcaster repository modifications.
* Research and evidence considered: .copilot-tracking/research/2026-09-21/podcast-dispatch-identity-reconciliation-research.md
* Decisions, dependencies, and acceptance criteria considered: the complete plan and phase details, their functional and non-functional requirements, phase/task dependencies, receipt and incident schemas, test ownership lock, validation commands, rollback notes, cross-repository contract boundary, and delivery/review handoff.
* Assessment boundary: this is one complete read-only credibility critique of the supplied artifacts. It does not independently verify repository source, GitHub runs, Podcaster deployment, endpoint behavior, or tool availability, and it does not treat the proposed Podcaster status contract as deployed fact.

## Authoritative incident-scope correction — 2026-09-21

The original critique assessed the plan language available at the time. Current disposition must use the repository owner's authoritative correction: W39 is the sole missed-publication incident; W38 ultimately published successfully after a blocked automatic path and manual recovery run `34958522782` reached Azure. Any critique wording that grouped W38 and W39 as equivalent incidents is superseded by this section. The findings about identity, durability, monitoring, and delivery evidence remain valid.

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|---|---|---|
| Requirement 1; FR-01; P01-T01/P01-T02 | Covered | The canonical model, equality, concurrency key, receipt matching, monitoring correlation, and incidents consistently require week, publish run, article digest, and manifest digest. |
| Requirement 2; FR-02; C19-C20; P01-T02 | Covered | Unassociated legacy evidence is nonblocking while exact reconstructed ambiguity remains fail-closed; the required empty/unreadable distinctions are explicit. |
| Requirement 3; P04-T01 | Covered | The locked matrix includes cancelled empty jobs/steps/logs, `no_anchor`, observe-only, unrelated ambiguity, and exact-identity ambiguity with named test owners. |
| Requirement 4; FR-03/FR-04; P02 | Partial | The fields, secret minimization, and ledger/artifact design are strong, but the artifact hard gate creates a known-no-mutation pre-only state, and failure-independent post persistence is underspecified. See PC-003 and PC-004. |
| Requirement 5; FR-07-FR-10; P03 | Partial | Stage predicates and incident behavior are explicit, but the claimed 3,600-second wall bound lacks bounded HTTP calls and a workflow runtime backstop. See PC-002. |
| Requirement 6; P03/P04 | Missing | Incident upsert covers terminal failures, but actionable dispatch-to-synthesis latency measurement and its alert threshold/evidence are not planned. See PC-001. |
| Requirement 7; NFR-01; FR-04; P01-P03 | Covered | Exact accepted, unknown, in-flight, or ambiguous identities block another mutation; monitor restart consumes receipts without redispatch. |
| Requirement 8; P04-T02 | Covered | Focused and repository-standard tests, Ruff, pip-audit, Bandit, Checkov, Zizmor, hosted CI, and smoke evidence are required without suppressions or weakened gates. |
| Requirement 9; P05-T02 | Covered | Independent implementation review and owner-routed follow-up are explicit and distinct from this plan critique. |
| Requirement 10; FR-11; P05 | Partial | Push/PR and fully-qualified references are explicit, but the PR acceptance contract does not require incident evidence and rollback/risk content. See PC-005. |
| Receipt schema, retention, and security; NFR-03-NFR-06 | Covered | Strict safe fields, author/repository/workflow validation, pagination, 90-day artifacts, persistent ledger comments, least privilege, and no new dependency are specified. |
| Incident dedup; FR-09; P03-T02 | Covered | The deterministic identity + stage + state key, marker, create/comment race re-check, and exact-identity close behavior are credible. |
| Critique lifecycle and artifact pointers | Partial | The plan names a different critique directory from the caller-authorized output, which can break disposition evidence. See PC-006. |
| Cross-repository boundary | Covered | SquadScope consumes and fails closed on an absent contract; Podcaster deployment remains separately owned and no Podcaster modification is authorized. |

## Verdict

* Verdict: Revise
* Rationale: The plan is evidence-aligned and substantially implementation-specific, but it is not yet credible as written on the hard monitor bound, pre/post durability failure semantics, required latency telemetry, and complete PR evidence. These are direct planner corrections within confirmed requirements; no divergent user decision is needed.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 [High]: Dispatch-to-synthesis latency telemetry is absent

* Related IDs: authoritative requirement 6; FR-07-FR-10; P03-T01; P03-T02; P04-T01
* Evidence: .copilot-tracking/plans/2026-09-21/podcast-dispatch-identity-reconciliation-plan.md; .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md
* Concern: The plan creates incidents for missing or failed terminal stages but never defines a dispatch-accepted-to-synthesis-start latency value, where it is emitted, what dimensions are safe, what threshold makes it actionable, or how tests prove the alert. A final timeout incident is not equivalent to actionable latency telemetry.
* Impact: Operators cannot detect synthesis-start degradation before the terminal deadline, establish a baseline, or distinguish slow queueing from missing evidence, leaving an explicit authoritative requirement unimplemented.
* Smallest useful change: Add to P03 a safe latency observation derived from accepted receipt timestamp to first authoritative `synthesis=started|succeeded`, emit it to the job summary and/or durable incident evidence, define a warning threshold below the terminal deadline, and define a missing-synthesis alert/incident transition without changing mutation behavior.
* Action owner: Planning parent
* Exact resolving evidence: Revised FR/NFR and P03/P04 details name the latency start/end timestamps, unit, safe dimensions, warning threshold, missing-terminal alert behavior, output location, and fake-clock tests for timely start, threshold breach, and no start.
* Decision route: Direct planner correction; no user decision needed.

<!-- rpi:critique id=PC-002 -->
### PC-002 [High]: The 3,600-second terminal bound does not bound network or workflow runtime

* Related IDs: authoritative requirement 5; FR-08; NFR-02; P03-T01; P03-T02
* Evidence: .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md P03-T01 specifies polling values but no HTTP timeout or reconciliation job timeout
* Concern: A configured deadline and five-error budget cannot enforce a wall-time maximum if a status request hangs, DNS/TLS stalls, or a call consumes the remaining budget. The plan also omits a workflow `timeout-minutes` backstop and does not specify deadline-aware request/sleep truncation.
* Impact: Reconciliation can exceed the promised bound or be terminated externally without the required classified failure and deduplicated incident.
* Smallest useful change: Specify a finite per-request connect/read timeout capped by remaining deadline, truncate sleeps to remaining time, set a reconciliation-job timeout with enough cleanup margin, and reserve that margin so timeout classification and incident upsert execute before job termination.
* Action owner: Planning parent
* Exact resolving evidence: Revised P03 details provide concrete request timeout and job timeout values, deadline accounting rules, cleanup margin, and fake-clock/hung-request tests proving monitor completion plus incident attempt within the declared maximum.
* Decision route: Direct planner correction; no user decision needed.

<!-- rpi:critique id=PC-003 -->
### PC-003 [High]: The pre-receipt artifact hard gate can falsely create submission uncertainty

* Related IDs: authoritative requirements 4 and 7; FR-03; FR-04; NFR-01; P02-T02; P03-T02
* Evidence: .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md P02-T02 requires ledger append, then artifact upload, then handoff; any failed pre operation blocks mutation, while a pre-only receipt is treated as unknown
* Concern: If the authoritative ledger append succeeds but its artifact mirror upload fails, workflow ordering proves the handoff was never invoked. Nevertheless, the durable `attempt_started` receipt remains, and the planned pre-only finalizer/retry logic classifies it as `submission_unknown`, permanently blocking a demonstrably safe retry. This conflicts with the stated crash-before-mutation retryability and makes a diagnostic mirror an idempotency state transition.
* Impact: A transient artifact-service failure can poison an identity despite proof that no mutation occurred, causing avoidable outage and manual reconciliation.
* Smallest useful change: Make successful authoritative ledger append the mutation gate and treat artifact upload as a required but non-authoritative mirror whose failure fails the workflow after recording a durable `pre_submit_failed`/mirror-failure transition, or explicitly add a durable compensating state that proves handoff was not entered and is retryable. Preserve fail-closed behavior once the handoff step may have begun.
* Action owner: Planning parent
* Exact resolving evidence: Revised P02/P03 state table distinguishes ledger failure, mirror failure before handoff, runner loss before handoff, handoff entered, and post gap; workflow tests prove mirror failure sends zero requests and remains safely retryable while any possibly-entered handoff remains blocked.
* Decision route: Direct planner correction; no user decision needed.

<!-- rpi:critique id=PC-004 -->
### PC-004 [Medium]: Post-mutation dual-write behavior is not failure-independent

* Related IDs: authoritative requirement 4; FR-03; FR-04; NFR-04; P02-T02
* Evidence: .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md says post receipt is constructed/appended/uploaded under `if: always()` but does not define step-level failure continuation or authoritative fallback
* Concern: `if: always()` only schedules a step; it does not ensure later ledger/artifact operations run after an earlier failing command or step. The plan does not specify whether append and upload are separate steps, use `continue-on-error`, capture independent outcomes, or how the job preserves a failing result after both persistence attempts.
* Impact: The first post-write failure can suppress the second persistence path, reducing recoverable evidence precisely after a mutation and weakening the claimed durable post receipt.
* Smallest useful change: Split ledger append and artifact upload into independently attempted always-running steps, capture each outcome, make ledger authoritative, and add a final assertion that fails safely when required persistence is missing without skipping incident reconciliation.
* Action owner: Planning parent
* Exact resolving evidence: Revised P02 workflow pseudocode/acceptance criteria and tests show each post persistence path is attempted when the other fails, record their outcomes, and prove the workflow remains failed and reconcilable without a second handoff.
* Decision route: Direct planner correction; no user decision needed.

<!-- rpi:critique id=PC-005 -->
### PC-005 [Medium]: PR acceptance omits required incident and rollback/risk evidence

* Related IDs: authoritative requirement 10; FR-11; P05-T01
* Evidence: .copilot-tracking/plans/2026-09-21/podcast-dispatch-identity-reconciliation-plan.md FR-11 and P05; .copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md P05-T01
* Concern: The delivery phase requires validation and links, while incident evidence and rollback/risk are only present elsewhere in planning or the changes record. The PR completion evidence does not require these items in the PR description.
* Impact: The pushed deliverable can satisfy the written phase while omitting context explicitly required for reviewer and operator decision-making.
* Smallest useful change: Add PR-body acceptance criteria requiring W39 incident evidence and explicitly successful W38 comparative/recovery evidence, validation/local-hosted results, known Podcaster contract dependency, rollback point, principal risks, and all required fully-qualified references without auto-closing Coordinator#17.
* Action owner: Planning parent
* Exact resolving evidence: Revised P05-T01 checklist and completion evidence enumerate those PR sections, with the final changes record containing the created PR URL and a checked mapping to each required section/reference.
* Authoritative correction disposition: Resolved with corrected incident scope. W39 alone supplies the missed-publication acceptance narrative; W38 supplies only blocked-path and successful-recovery comparison.
* Decision route: Direct planner correction; no user decision needed.

<!-- rpi:critique id=PC-006 -->
### PC-006 [Medium]: Critique artifact paths conflict with the caller-authorized lifecycle record

* Related IDs: pre-implementation critique dependency; Implementation Context Record; Critique Disposition
* Evidence: the caller authorizes .copilot-tracking/critiques/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md, while the plan points to .copilot-tracking/reviews/plans/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md
* Concern: The plan's implementation gate, context record, and worker instruction reference a different artifact than the only critique output authorized and produced by this pass.
* Impact: Implementation may fail to recognize this critique as the required gate, or may incorrectly request a second critique, violating the exactly-one-pass requirement.
* Smallest useful change: Update all plan/details critique pointers and disposition instructions to the caller-authorized `.copilot-tracking/critiques/...` artifact, then record dispositions for PC-001 through PC-006 there or in the plan as intended.
* Action owner: Planning parent
* Exact resolving evidence: Every critique pointer in the revised plan/details resolves to this artifact and the pre-implementation gate records one completed critique with dispositions for the complete finding set.
* Decision route: Direct planner correction; no user decision needed.

## Strengths and Residual Risk

* The four-field identity is consistently carried into equality, dedup, concurrency, receipt correlation, status evidence, and incidents.
* The plan correctly rejects both global legacy poison pills and unsafe clearing of exact-identity uncertainty.
* Test ownership is unusually explicit and covers the caller's required incident shapes, crash seams, non-mutation paths, and no-secret rules.
* The terminal-success predicate appropriately requires synthesis evidence, successful video state, and externally verified provider publication rather than HTTP acceptance.
* The Issue ledger trust checks, schema validation, least-privilege permissions, retention split, incident key, and race re-check are credible.
* Rollback preserves identity and durable evidence rather than reverting to unsafe global ambiguity.
* Residual external risk remains that the Podcaster status contract is not proven deployed. The plan handles this safely as visible failure, but production success and hosted smoke remain dependent on separately owned Podcaster work and protected-environment configuration.

## Questions or Blocking Evidence Gaps

* None requiring user input. The supplied evidence supports a Revise verdict, and every finding can be corrected directly by the planning parent within confirmed requirements.

## Limitations

* This critique did not inspect source files, live workflows, GitHub issue/PR content, or external repository state beyond the supplied research statements.
* It cannot confirm whether GitHub artifact upload semantics, endpoint deployment, environment variables, labels, branch protections, or hosted approvals currently exist.
* It assesses plan credibility, not implementation correctness.

## Recommended Next Action

* Highest-impact finding: PC-003
* Action owner: Planning parent
* Smallest next action: Revise the P02/P03 receipt state table and workflow ordering so a pre-handoff artifact-mirror failure is durably classified as known non-mutation and safely retryable, while any state that may have entered handoff remains fail-closed; then apply the remaining direct corrections from this single critique set.
* User response required: No

## Relevant Artifacts

| Artifact | Description |
|---|---|
| [.copilot-tracking/plans/2026-09-21/podcast-dispatch-identity-reconciliation-plan.md](.copilot-tracking/plans/2026-09-21/podcast-dispatch-identity-reconciliation-plan.md) | Supplied implementation plan assessed in this pass. |
| [.copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md](.copilot-tracking/details/2026-09-21/podcast-dispatch-identity-reconciliation-phase-details.md) | Supplied phase/task implementation details assessed in this pass. |
| [.copilot-tracking/research/2026-09-21/podcast-dispatch-identity-reconciliation-research.md](.copilot-tracking/research/2026-09-21/podcast-dispatch-identity-reconciliation-research.md) | Supplied incident and design evidence used by the critique. |
| [.copilot-tracking/critiques/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md](.copilot-tracking/critiques/2026-09-21/podcast-dispatch-identity-reconciliation-plan-critique.md) | Complete independent critique artifact and finding set. |

## Next Steps

The active planning parent should apply and record dispositions for PC-001 through PC-006, then finalize the plan without requesting a second critique. No user action is required.
