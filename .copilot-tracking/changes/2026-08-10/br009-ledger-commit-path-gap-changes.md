<!-- markdownlint-disable-file -->

# Changes: BR-009 Ledger Commit-Path Gap Fix

## Related Plan

`.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md`

## Implementation Date

2026-08-10

## Summary

Fixes the "ledger commit-path gap" documented in PR #697/#699's changes log
and `/memories/repo/squadscope.md`: the `analyze` job's freshly appended
`data/metrics/token-usage.jsonl` row was never committed anywhere, and the
downstream `generate` job's "Hydrate prior generated state from publish" step
re-checks-out `data/metrics/` from `origin/publish` (the prior run's
committed state) before any cost-generation step could run — so the current
run's fresh ledger row would be silently discarded if `generate_cost_summary.py`
were wired into the workflow without this fix. This change only fixes the
commit-path plumbing; it does NOT wire `generate_cost_summary.py` into the
workflow (BR-009 activation remains a separate follow-up, gated on this fix).

## Modified

* `.github/workflows/crawl-and-publish.yml`:
  * `analyze` job: added an "Upload token usage ledger" artifact-upload step
    (name `token-usage-ledger`, `if: always()`) uploading only
    `data/metrics/token-usage.jsonl` — not the whole `data/metrics/` tree, to
    avoid accidentally introducing run-scoped diagnostic files (e.g.
    `analysis-prompt-*.md`) into the committed `publish` branch, which is not
    the current behavior and was not the scope of this fix
  * `generate` job: added a "Download token usage ledger artifact" step
    (`continue-on-error: true`, since a dry-run/candidate-only analyze run
    never uploads it) right after the existing "Download analyzed data
    artifact" step, downloading into `data/metrics/`, overlaying this run's
    fresh ledger row on top of the publish-branch hydration that ran earlier
    in the same job. This mirrors the existing, already-tested pattern used
    for `data/analyzed/` (hydrate-from-publish, then overlay this run's
    artifact)
  * `generate` job (round 2, URL squad review): gave the download step an
    `id` and added a "Warn if ledger artifact was unavailable" step that
    emits a `::warning::` annotation when the download did not succeed, so a
    silently-skipped ledger sync (tolerated by `continue-on-error`) is
    visible in run logs instead of regressing to the exact "row lost" bug
    this fix addresses with zero visibility
* `tests/test_pipeline.py`: added
  `test_analyze_job_uploads_token_usage_ledger_for_generate_job`, asserting
  the upload step's name/artifact-name/path/`if: always()`, and that the
  download step in `generate` runs after the publish hydration step

## Validation

* `python3 -c "import yaml; yaml.safe_load(...)"` -> workflow YAML parses
* `pytest tests/test_pipeline.py tests/test_atomic_publish_proof.py tests/test_sync_publish_workflow.py tests/test_publish_hydration.py` -> 53 passed, 19 subtests passed
* `pytest tests/` -> 1562 passed
* `zizmor --persona=regular .github/workflows/crawl-and-publish.yml` -> same
  3 pre-existing medium `secrets-outside-env` findings, all at unrelated
  lines (COPILOT_GITHUB_TOKEN, WEBHOOK_URL); no new findings introduced by
  the added artifact/warning steps
* Squad acceptance review per `.squad/routing.md` (workflow changes route to
  URL + Hermes): URL — ACCEPT WITH FOLLOW-UPS (confirmed scope, job
  ordering, commit-step compatibility, zizmor clean; recommended the
  visibility warning implemented above); Hermes — ACCEPT (confirmed no
  fork-reachable trigger, no sensitive data in the ledger file, correct
  action pinning, zizmor identical before/after)

## Deviations

None from the documented gap description. This fix is scoped narrowly to the
commit-path plumbing only; it does not attempt to wire
`scripts/generate_cost_summary.py` into the workflow, which remains a
separate, still-open follow-up requiring its own sponsor/legacy-policy
context already recorded elsewhere.
