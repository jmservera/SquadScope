<!-- markdownlint-disable-file -->
# Research: Durable restore-consistency fix (#640)

## Scope

`run_mode=restore` (intended to refresh observatory surfaces from stored raw
evidence) also regenerates and republishes the week's weekly article. The
`sync-publish-to-main.yml` job wipes and re-syncs `content/weekly/` from
`publish` to `main`, so a restore overwrites the original published article
with a non-deterministic LLM regeneration. The same restore also rewrote the
promotion record to reference a candidate manifest that was never persisted,
breaking the Podcaster handoff smoke (remediated reactively for 2026-W31).

## Success criteria (from #640)

- A restore intended to refresh `content/data` does not change any already-published `content/weekly/*` article.
- Topic frontmatter on prior weeks is preserved through restore+sync.
- Regression test covers the chosen behavior.

## Evidence log

- `.github/workflows/crawl-and-publish.yml`
  - `generate` job: hydrates prior state from `publish`, downloads analyzed +
    candidate + raw artifacts, then `Generate weekly content candidate` →
    `Rehash and promote final weekly content` (rewrites `content/weekly/<year>/W<nn>.md`),
    then observatory steps, then `Commit generated content to data branch`.
  - Commit step resets working tree to `origin/publish` (`git checkout -f -B publish origin/publish`),
    extracts regenerated files (`tar -xf generated-state.tar`), stages
    `GENERATED_PATHS`, and force-pushes to `publish`.
  - The commit step copies the current-branch tooling to `publish-safety-tool.py`
    BEFORE the reset, so a current-version helper is available after the reset.
- `.github/workflows/sync-publish-to-main.yml`: `rm -rf ... content/weekly ...`
  then `git checkout origin/publish -- content/weekly/ ...` → publish is canonical.
- `scripts/rerun_modes.py`: mode validation; restore action = "restore published
  artifacts for <week> and regenerate through guarded promotion".
- Published weekly transaction = 3 files: `content/weekly/<year>/W<nn>.md`,
  `data/analyzed/<week>-summary.md`, `data/published/<week>/promotion-manifest.json`.
- `scripts/podcaster_handoff.py` (`promotion_transaction_v1`) verifies the
  promotion record's `source_manifest.path` bytes → dangling references break it.

## Alternatives evaluated

- **A — Data-only restore mode (gate article steps):** skip article/promotion
  steps entirely in restore. Cleanest semantically but touches many interdependent
  steps in a high-risk force-pushing workflow; hard to test end-to-end.
- **B — Preserve published transaction (SELECTED):** after regeneration and the
  branch reset, in restore mode revert the 3 published-transaction files to their
  `publish` versions (`git checkout HEAD -- <path>` where HEAD == origin/publish)
  before staging. Observatory surfaces stay regenerated. The commit — and thus the
  sync — leave the published article, summary, and promotion record byte-identical.
  Minimal, testable, and also prevents the dangling-manifest class.
- **C — Guard the sync:** sync has no knowledge of run_mode; detecting a
  restore-driven rewrite there is fragile. Rejected.

## Selected approach

Option B. Add a small unit-tested helper `weekly_transaction_paths(week)` +
`weekly-transaction-paths` CLI to `scripts/publish_safety.py`. In the commit
step, gated on `run_mode == restore`, iterate those paths and
`git checkout HEAD -- <path>` for each that exists on `publish`, before staging.
Update `rerun_modes.py` restore action wording. Add tests.

## Next steps

1. Helper + CLI in `publish_safety.py`.
2. Gated preservation block in the commit step (pass `RUN_MODE` env).
3. Update `rerun_modes.py` restore action string.
4. Tests: `test_publish_safety.py` (paths), `test_pipeline.py` (workflow guard).
5. Validate: pytest, ruff, zizmor, yaml.
