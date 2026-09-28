# Plan: CodeQL cache-poisoning alerts #1208-#1211

**Date:** 2026-09-28  
**Issue:** jmservera/SquadScope#815  
**Branch:** `squad/815-cache-poisoning`

## Objective

Remove the CodeQL `actions/cache-poisoning/poisonable-step` dataflow from
`inputs.reviewed_main_sha` to executed workflow steps in
`.github/workflows/build-cost-experiment.yml`, without removing the manual
evidence input or weakening security gates.

## Evidence

Research artifact:
`.copilot-tracking/research/2026-09-28/cache-poisoning-815.md`.

GitHub Code Scanning alerts #1208-#1211 all report the same source:
`inputs.reviewed_main_sha` on `workflow_dispatch`, used by the first checkout
before admission checks run. The checked-out workspace then feeds hydration,
verification, setup, and experiment steps.

## Implementation steps

1. Keep `reviewed_main_sha` as a required exact-SHA evidence input.
2. Change the initial checkout `ref` from `${{ inputs.reviewed_main_sha }}` to
   `${{ github.sha }}` so the workflow always checks out the selected trusted
   workflow commit in the privileged context.
3. Retain the existing admission check that fails unless
   `reviewed_main_sha == github.sha`; valid dispatches therefore preserve prior
   behavior, while invalid dispatches fail before experiment work.
4. Do not change CodeQL, Checkov, permissions, or cache-related gates.

## Validation

- Parse/lint changed workflow with `actionlint`.
- Run the repository's workflow security/lint commands where available:
  Checkov baseline and Zizmor baseline.
- Run focused Python tests for the workflow-invoked modules:
  `tests/test_publish_hydration.py` and `tests/test_build_cost_experiment.py`.
- Push branch and open a PR; watch checks.

## Rollback

Revert the single checkout `ref` change if the experiment's manual dispatch no
longer works as intended. The equality admission check makes rollback unlikely
because successful dispatches already require `reviewed_main_sha` to equal
`github.sha`.

## Review criteria

- No input-controlled checkout remains in `build-cost-experiment.yml`.
- `reviewed_publish_sha` remains SHA/ancestry-validated before it is used to
  hydrate generated corpus paths.
- All actions remain SHA-pinned.
- CI and workflow lint checks pass or failures are unrelated and documented.

