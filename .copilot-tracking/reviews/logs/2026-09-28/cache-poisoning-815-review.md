<!-- markdownlint-disable-file -->
# Review: CodeQL cache-poisoning alerts #1208-#1211

## Scope and Evidence

* Task ID: jmservera/SquadScope#815
* Review date: 2026-09-28
* Review scope: Full task scope for `build-cost-experiment.yml` cache-poisoning alerts.
* Assessed boundary: Remove the CodeQL dataflow from `inputs.reviewed_main_sha`
  to privileged checkout/executed repository code without removing functionality,
  weakening CodeQL/Checkov, or unpinning actions. Cheap issue #816 assessment is
  included only as a scoped disposition, not as implemented closure.
* Plan: .copilot-tracking/plans/2026-09-28/cache-poisoning-815-plan.md
* Phase details: Unavailable; no separate phase details artifact was created for
  this single-change RPI cycle.
* Plan critique: Unavailable; planner subagent did not produce a usable critique
  artifact.
* Changes: Git diff for `.github/workflows/build-cost-experiment.yml`.
* Other evidence considered:
  .copilot-tracking/research/2026-09-28/cache-poisoning-815.md, actionlint,
  Checkov, Zizmor, and focused pytest output.

## Opening Review State

* Interpreted review goal: Confirm the implemented workflow change closes the
  CodeQL cache-poisoning root cause while preserving validated manual evidence
  semantics.
* Review scope: Full task scope for jmservera/SquadScope#815.
* Evidence readiness: Research, plan, implementation diff, and validation output
  are available. Phase details and plan critique are absent, but the task
  boundary is sufficiently small and directly evidenced for a credible verdict.
* Acceptance basis: GitHub alert evidence, user requirements, repository
  workflow-security conventions, and the plan's validation criteria.
* First comparison boundary: `workflow_dispatch` input source to first checkout
  and subsequent executed steps in `.github/workflows/build-cost-experiment.yml`.
* Active read-only boundaries: Review mutates only this review log; source,
  plan, and research artifacts are evidence only during review.
* Initial blockers: None.

## Execution Status

* Execution status: Complete
* Review execution evidence: Implementation changed the first checkout `ref` to
  `${{ github.sha }}` and preserved the existing equality admission check for
  `reviewed_main_sha`.

## Plan-to-Change Reconciliation

| Current plan scope | Descriptive changes-record summary | Current-state reconciliation | Gap or rationale |
| --- | --- | --- | --- |
| Remove untrusted dispatch input from privileged checkout | `ref: ${{ inputs.reviewed_main_sha }}` became `ref: ${{ github.sha }}` | Reconciled | Directly implements the planned root-cause fix. |
| Preserve evidence input and behavior | `reviewed_main_sha` input and equality check remain unchanged | Reconciled | Valid dispatches already required equality with `github.sha`. |
| Do not bundle #816 unless cheap and low-risk | No #816 workflow changes included | Reconciled | Research found existing skips but not enough owner/evidence coverage to close safely. |

## Completed Work Assessment

| Related marker | Files | What changed and why | Completion evidence | Validation | Assessment |
| --- | --- | --- | --- | --- | --- |
| #815 | `.github/workflows/build-cost-experiment.yml` | First checkout now uses selected workflow SHA rather than operator input, removing the CodeQL taint source before repository code executes. | Focused diff shows only step name and checkout ref changed. | actionlint, Checkov, Zizmor, and focused pytest passed. | Reconciled. |

## Implementation-Time Plan and Detail Update Assessment

| Affected area or marker | What changed and why | Triggering evidence and user decision | Reconciliation performed | Planning and critique state | Assessment |
| --- | --- | --- | --- | --- | --- |
| #815 implementation | Narrowed change to first checkout only. | CodeQL alerts identified the tainted `reviewed_main_sha` checkout. User requested root-cause fix. | Research, plan, diff, and validation agree. | No material plan revision needed after implementation. | Reconciled. |
| #816 disposition | Deferred separate PR/work. | User allowed #816 only if cheap and low-risk; research found safe closure needs separate operational input review. | Plan and review mark it as out of scope. | No #816 plan opened in this task. | Reconciled. |

## Critique and Material Revision Assessment

* Latest critique dispositions: No separate critique artifact exists. The
  implemented change matches the research recommendation and plan.
* Material revisions: None after implementation.
* Dependent-work pause assessment: No dependent implementation continued beyond
  the reviewed source change.
* Justification assessment: Supported by alert details, workflow ordering, and
  passing validation.

## Plan Follow-Up Assessment

| Follow-up item | Why outside immediate scope | Owner or next action | Assessment and route |
| --- | --- | --- | --- |
| jmservera/SquadScope#816 workflow_dispatch CKV_GHA_7 closure | Requires owner/security review of six operational dispatch contracts; not cheap enough to bundle with #815. | Separate issue/PR owner. | Distinct follow-up item; not a #815 defect. |

Unresolved plan follow-up items remain distinct follow-up work. Do not treat them
as defects or add them to active `Pxx` or `Pxx-Txx` implementation, completion,
or acceptance scope.

## Findings

No substantive defects found.

## Defects

* None.

## Routed Findings

| Finding | Destination | Owner or next action | Reason for route |
| --- | --- | --- | --- |
| None | None | None | No defects, decision gaps, or material evidence gaps remain for #815. |

Later implementation of a routed finding does not require another Review.

## Residual Work

* jmservera/SquadScope#816 remains a distinct follow-up item for a separate PR if
  an owner confirms the operator-input validation/skip posture across the six
  listed workflows.

## Blockers and Remaining Work

* Blockers: None.
* Remaining active work: Push branch, open PR, and watch GitHub checks.

## Validation Evidence

| Command | Scope | Status | Summary |
| --- | --- | --- | --- |
| `/tmp/actionlint-install/actionlint .github/workflows/build-cost-experiment.yml` | Changed workflow | Passed | Workflow syntax/actionlint checks passed. |
| `checkov -d . --framework github_actions --skip-path node_modules --skip-path .venv --skip-path public --skip-path resources --skip-path themes --compact --quiet` | GitHub Actions security scan | Passed | 1073 passed, 0 failed, 7 skipped. |
| `zizmor .github/workflows/build-cost-experiment.yml` | Changed workflow | Passed | No findings. |
| `python3 -m pytest tests/test_publish_hydration.py tests/test_build_cost_experiment.py -q` | Workflow-invoked modules | Passed | 35 tests passed. |

## Outcome

* Outcome: Conformant with justified divergence
* Outcome rationale: The #815 root-cause fix is complete and validated. The
  justified divergence is not opening a #816 PR in this same pass because the
  allowed condition was "cheap and low-risk" and research found that safe
  closure requires a separate review.

## Closeout Routing Record

<!-- Persist outcome and route facts only. The rpi-review reference owns rendered closeout prose. -->

| Finding class | Destination | Owner or next action |
| --- | --- | --- |
| Implementation defect | None | None. |
| Decision gap or invalid assumption | None | None for #815. |
| Material evidence gap | None | None for #815. |
| Non-blocking residual work | Distinct follow-up for jmservera/SquadScope#816 | Separate owner/PR to validate or justify dispatch inputs across six workflows. |

* Execution status: Complete
* Outcome: Conformant with justified divergence
* Validation coverage: actionlint, Checkov, Zizmor, focused pytest passed.
* Blockers: None.

| Artifact | Description |
| --- | --- |
| [.copilot-tracking/research/2026-09-28/cache-poisoning-815.md](.copilot-tracking/research/2026-09-28/cache-poisoning-815.md) | Research evidence and root-cause recommendation. |
| [.copilot-tracking/plans/2026-09-28/cache-poisoning-815-plan.md](.copilot-tracking/plans/2026-09-28/cache-poisoning-815-plan.md) | Implementation and validation plan. |
| [.copilot-tracking/reviews/2026-09-28/cache-poisoning-815-review.md](.copilot-tracking/reviews/2026-09-28/cache-poisoning-815-review.md) | Implementation-time review summary. |
| [.copilot-tracking/reviews/logs/2026-09-28/cache-poisoning-815-review.md](.copilot-tracking/reviews/logs/2026-09-28/cache-poisoning-815-review.md) | Canonical RPI review log. |

## Next Steps

No RPI correction command is required for #815. Continue with commit, PR, and
remote CI review.

