# Research: CodeQL cache-poisoning alerts #1208–#1211

**Date:** 2026-09-28  
**Repository / worktree:** `jmservera/SquadScope` / `squad/815-cache-poisoning` at `c499ae6d23cbaed143c44f3a08c583e6e208872d`  
**Scope:** Research only; no workflow source was changed.

## Questions and evidence

### Is untrusted code checked out and executed in a default-branch context?

Yes. `workflow_dispatch` exposes `reviewed_main_sha` as a required string input, and the
job runs when the selected ref is `main`. The first checkout uses that input as its `ref`
before any validation. See `.github/workflows/build-cost-experiment.yml:4-23`,
`.github/workflows/build-cost-experiment.yml:34-56`.

The validation that constrains the value to a SHA and requires equality with
`github.sha` occurs only after the checkout. See
`.github/workflows/build-cost-experiment.yml:58-80`. Consequently it cannot establish
that the code already placed in the workspace was trusted.

The checked-out workspace is then executed by Python before and after hydration
(`scripts.publish_hydration` and `scripts.build_cost_experiment`) and supplies the site
corpus to the build experiment. See `.github/workflows/build-cost-experiment.yml:82-111`
and `.github/workflows/build-cost-experiment.yml:146-163`; module entry points are in
`scripts/publish_hydration.py:125-155` and `scripts/build_cost_experiment.py:106-112`.
The workflow has only `contents: read` and disables persisted checkout credentials
(`.github/workflows/build-cost-experiment.yml:24-25,36-37,51-56`), which limits impact
but does not remove the default-branch cache-poisoning pattern identified by CodeQL.

GitHub's alert records corroborate the dataflow source and all four sinks:

| Alert | Reported sink | Relationship |
| --- | --- | --- |
| #1208 | workflow lines 82-101 | supports: input-based checkout taints hydration step |
| #1209 | workflow lines 101-113 | supports: same checkout taints verification step |
| #1210 | workflow lines 140-146 | supports: same checkout taints Pagefind installation step |
| #1211 | workflow lines 146-165 | supports: same checkout taints experiment execution |

Source provenance: GitHub Code Scanning API, retrieved 2026-09-28:
`https://api.github.com/repos/jmservera/SquadScope/code-scanning/alerts/1208`,
`/1209`, `/1210`, and `/1211`. Each is open, high severity,
`actions/cache-poisoning/poisonable-step`, for the same `inputs.reviewed_main_sha`
checkout at workflow line 53.

### Low-risk root-cause fix

Change the initial checkout to a trusted run-context value:

```yaml
- name: Check out selected main workflow commit
  uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
  with:
    ref: ${{ github.sha }}
    fetch-depth: 0
    submodules: recursive
    persist-credentials: false
```

Keep the existing admission check that `REVIEWED_MAIN_SHA == WORKFLOW_SHA`. Thus the
manual field remains an explicit evidence assertion and an invalid dispatch still fails,
but it no longer controls code checkout. A valid dispatch checks out the same immutable
main commit as before. This is smaller and less disruptive than removing the input or
redesigning the experiment interface.

`reviewed_publish_sha` should remain subject to its existing SHA and ancestry checks
before use (`.github/workflows/build-cost-experiment.yml:66-79`). It only hydrates the
enumerated generated-data paths after the trusted main checkout
(`.github/workflows/build-cost-experiment.yml:82-100`); this research found no alert
that names it as the taint source. Do not broaden this fix without a new finding.

### Validation plan

1. Confirm the patch contains no input-controlled `actions/checkout` ref:
   `git diff --check` and inspect the changed checkout block.
2. Parse the workflow YAML, for example:
   `ruby -e "require 'yaml'; YAML.load_file('.github/workflows/build-cost-experiment.yml'); puts 'YAML valid'"`.
3. Run the focused behavior tests for the modules the workflow invokes:
   `python3 -m pytest tests/test_publish_hydration.py` and the existing focused
   `build_cost_experiment` test module, if present in the worktree.
4. Push the workflow change to the default branch and let GitHub Advanced Security
   reanalyze it. Closure criterion: alerts #1208–#1211 are fixed/dismissed as absent from
   the new analysis. Local YAML checks cannot reproduce CodeQL's Actions taint analysis.

## Cheap assessment: issue #816 (CKV_GHA_7)

Issue #816 lists exactly six workflows: `auto-podcast-dispatch`,
`build-cost-experiment`, `trigger-podcast`, `podcaster-handoff-smoke`,
`squad-promote`, and `restore-publish-backup`. The issue asks that each dispatch input be
validated/allowlisted or intentionally justified by an inline Livingston-reviewed
`checkov:skip`. Source: GitHub issue #816, retrieved 2026-09-28:
`https://github.com/jmservera/SquadScope/issues/816`.

All six currently have a workflow-local `checkov:skip=CKV_GHA_7` comment immediately
above `workflow_dispatch.inputs`: `.github/workflows/auto-podcast-dispatch.yml:16-26`,
`.github/workflows/build-cost-experiment.yml:4-23`,
`.github/workflows/trigger-podcast.yml:4-18`,
`.github/workflows/podcaster-handoff-smoke.yml:4-26`,
`.github/workflows/squad-promote.yml:4-12`, and
`.github/workflows/restore-publish-backup.yml:4-10`.

The comments satisfy the mechanical inline-skip portion, but this quick review cannot
establish the requested Livingston review or prove all stated validation claims:

* Build-cost's `reviewed_main_sha` validation is semantically correct only after the
  proposed trusted checkout change; today its ordering is also the root cause of #815.
* `squad-promote` is a closed `true`/`false` choice
  (`.github/workflows/squad-promote.yml:7-12,44-45,117-119`), a low-risk intentional
  input.
* The remaining inputs feed operational or external handoff behavior, including
  `trigger-podcast`'s `breaking_news` and Podcaster secret-bearing handoff
  (`.github/workflows/trigger-podcast.yml:58-61,125-142`) and the smoke workflow's
  caller-supplied article values (`.github/workflows/podcaster-handoff-smoke.yml:85-132`).
  They need a separate focused validation/authorization review rather than an
  unsubstantiated closure.

## Recommendation and stop decision

Implement only the `github.sha` checkout substitution and step-name update for #815,
retain the equality admission check, then rely on a new CodeQL analysis to close all four
alerts. Treat #816 as **partially evidenced, not closed**: the skips exist, but review of
the operational input contracts is outside the cheap assessment and needs an explicit
owner decision. Research stopped at the requested scope boundary; no source workflow was
modified.
