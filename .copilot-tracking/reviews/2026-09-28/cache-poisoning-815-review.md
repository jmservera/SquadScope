# Review: CodeQL cache-poisoning alerts #1208-#1211

**Date:** 2026-09-28  
**Issue:** jmservera/SquadScope#815  
**Status:** In progress until PR checks complete.

## Implementation review

The workflow now checks out `${{ github.sha }}` before executing repository
code. This removes the tainted `workflow_dispatch` input from the checkout
operation identified by CodeQL, while preserving the operator evidence field and
the existing equality admission check.

The change is deliberately limited to `.github/workflows/build-cost-experiment.yml`.
No CodeQL or Checkov configuration was weakened, no alert was dismissed, and no
action pin was loosened.

## Issue #816 disposition

Not included in this PR. A cheap pass found the listed workflows already contain
inline CKV_GHA_7 skips and several runtime validations, but a safe closure would
require a separate operational review of six dispatch contracts. That is not
low-risk enough to bundle into the cache-poisoning PR.

## Validation evidence

Pending:

- `actionlint`
- Checkov workflow scan
- Zizmor workflow scan
- Focused Python tests for publish hydration and build-cost experiment modules
- GitHub PR checks

## Follow-up route

Open a separate jmservera/SquadScope#816 PR only after an owner validates the
operator-controlled dispatch inputs and decides whether to replace each skip
with explicit allowlist checks or retain the documented skip.

