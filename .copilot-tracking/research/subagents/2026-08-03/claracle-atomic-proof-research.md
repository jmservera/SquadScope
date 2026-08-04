<!-- markdownlint-disable-file -->
# Claracle Atomic Publish Proof Research

## Research Questions

* What is the smallest safe, non-destructive or isolated proof harness for controlled normal publication, identical no-op rerun, injected generator failure with an unchanged branch, generated-tree comparison, and hydration comparison?
* Which current workflow steps, scripts, functions, tests, and conventions should the harness reuse?
* Where must side effects be bounded so the proof cannot mutate the production `publish` branch or external systems?

## Findings

### Baseline and acceptance gap

* The researched revision is `4b7c5cf506b2e8b73350ff94ce80669c93810e66`. `HEAD`, local `main`, and `origin/main` resolve to that SHA.
* `.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md` keeps Step 6.1 open. It requires a controlled normal publish, identical no-op rerun, injected failure with unchanged `publish`, generated-tree comparison, and hydration comparison.
* `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md` requires retained run URLs and publish SHAs. `.copilot-tracking/research/subagents/2026-08-03/claracle-protected-acceptance-gates-research.md` confirms that no retained five-scenario matrix exists.
* The current tests establish workflow shape, helper correctness, generated-path coverage, lease use, no-op syntax, backup immutability, and hydration reference integrity. They do not execute the publication step against a Git remote.

### Current publication control path

* `.github/workflows/crawl-and-publish.yml`, job `generate`, hydrates prior generated state from `origin/publish`, downloads current-run artifacts, runs generators in dependency order, runs five freshness checks, and then enters `Commit generated content to data branch`.
* The commit step calls `scripts.publish_manifest.main()` through `assert-eligible`, calls `scripts.promotion_guard.main()`, snapshots the generated paths, fetches `publish`, checks the analyzed `publish_head_sha`, switches a local branch to the fetched head, calls `scripts.publish_safety.backup_existing()`, restores the generated snapshot, stages generated paths plus `data/backups`, suppresses an empty commit, creates one commit, and pushes with `--force-with-lease`.
* A generator or freshness failure occurs before the commit step. Normal GitHub Actions step semantics therefore prevent any generated-content push. The crawl job can already have published raw evidence earlier; the unchanged-branch assertion for an injected generate failure must use the `publish` SHA immediately before the `generate` job, not the workflow-start SHA.
* `.github/workflows/deploy-site.yml` mirrors generated paths from `publish` only when each path exists there. `scripts.publish_hydration.GENERATED_PATHS` is the tested canonical deploy list, and `scripts.publish_hydration.check_publish_references()` validates embed and promotion references after hydration.

### Existing callable boundaries

* `scripts.publish_safety.backup_existing()` and `restore_backup()` provide immutable, hash-recorded backup behavior.
* `scripts.publish_safety.weekly_transaction_paths()` identifies the weekly article, analyzed summary, and promotion record that restore mode must preserve.
* `scripts.promotion_guard.promote_candidate()` writes the summary, article, and `promotion_transaction_v1` record transactionally within one worktree.
* `scripts.publish_hydration.check_publish_references()` checks a hydrated root without network or branch mutation.
* `tests/test_pipeline.py` parses workflow YAML and already asserts generator order, path coverage, expected-SHA drift protection, lease use, and `git diff --cached --quiet && exit 0`.
* `tests/test_publish_hydration.py` supplies the current convention for minimal consistent release fixtures and verifies that the Python hydration path list matches the deploy workflow.

### Smallest safe harness shape

The harness should not add a failure input to `crawl-and-publish.yml` and should not push an acceptance branch to GitHub. It should extract the exact `run` body of the named `Commit generated content to data branch` step from the checked-out workflow and execute that body in a temporary clone whose `origin` is a temporary local bare repository. This tests the production commit logic without copying it into a second publisher or refactoring a proven production step solely for acceptance.

The local bare repository should be seeded with two refs:

* `main` from the reviewed SHA
* `publish` from the fetched `origin/publish` SHA

The harness should hydrate a temporary main clone from the local `publish`, select the latest valid retained promotion and source manifest, and apply one deterministic generated-path mutation under `data/derived/observatory/`. It should then run this matrix:

1. Execute the real commit-step shell with the local bare remote. Require one new commit, one parent, a successful lease push, and no changed files outside the workflow's generated paths plus `data/backups/`.
2. Recreate a clean main clone, hydrate from the accepted local `publish`, apply identical bytes, and execute the same shell. Require no new commit and an unchanged local remote SHA.
3. Recreate another clone, hydrate from the accepted local `publish`, write a partial generated file, and exit the injected generator command nonzero before invoking the commit shell. Require an unchanged local remote SHA and record the nonzero exit.
4. Hash path, mode, size, and SHA-256 for every file under the commit step's `GENERATED_PATHS` before publication and from the accepted commit. Require identical manifests. Exclude `data/backups/` from this generator-output identity comparison but list it separately as publication metadata.
5. Start from a clean main clone, apply the deploy hydration algorithm using `scripts.publish_hydration.GENERATED_PATHS` at the accepted local `publish` SHA, compare every publish-present hydrated path with that commit, record main-preserved paths absent from publish, and require `check_publish_references()` to return no problems.

The result should be one JSON record containing reviewed main SHA, source publish SHA, accepted proof SHA, workflow SHA-256, extracted commit-step SHA-256, scenario exit states, before/after remote SHAs, commit count, changed paths, candidate/accepted/hydrated tree digests, preserved-main paths, reference-check result, and tool versions. A human-readable text summary can accompany the JSON, but the JSON is the acceptance authority.

## Recommended Implementation

### Exact files

* Add `scripts/atomic_publish_proof.py` as the isolated orchestrator. Keep Git invocation, temporary-repository setup, workflow-step extraction, tree-manifest creation, hydration, assertions, and JSON output here.
* Add `tests/test_atomic_publish_proof.py` for parser guards, remote isolation, the five scenarios, changed-path boundaries, and evidence schema.
* Add `.github/workflows/atomic-publish-proof.yml` as a manual, read-only evidence runner. It should check out with `persist-credentials: false`, fetch `publish`, run the harness, and upload the JSON and tree manifests. Set workflow and job permissions to `contents: read` only.
* Do not modify `.github/workflows/crawl-and-publish.yml` for the first implementation. The harness should fail closed if the `generate` job, named commit step, expected lease command, or no-op guard cannot be found.
* Do not modify `.github/workflows/deploy-site.yml`. Reuse `scripts.publish_hydration.GENERATED_PATHS` and `check_publish_references()` as its existing tested proxy.

### Suggested functions

`scripts/atomic_publish_proof.py` should keep the API narrow:

* `extract_commit_step(workflow_path: Path) -> str`
* `run_git(repo: Path, *args: str) -> str`
* `seed_isolated_origin(main_ref: str, publish_ref: str, root: Path) -> Path`
* `hydrate_generated_paths(repo: Path, publish_ref: str, paths: Sequence[str]) -> list[str]`
* `generated_tree_manifest(repo: Path, ref: str | None, paths: Sequence[str]) -> dict[str, object]`
* `run_commit_step(repo: Path, script: str, environment: Mapping[str, str]) -> CompletedProcess[str]`
* `run_proof(repo_root: Path, output_dir: Path) -> dict[str, object]`

Use `subprocess.run()` with argument arrays for Git. The extracted shell body is the only intentional shell execution and must run with a fixed Bash executable, a controlled environment, and no inherited token. Resolve and validate every repository path under the temporary root before execution.

### Focused tests

* Unit-test extraction against `.github/workflows/crawl-and-publish.yml` and assert the body contains the expected-SHA drift check, cached-diff no-op, one `git commit`, and lease push.
* Unit-test tree manifests for additions, deletions, executable modes, and deterministic ordering.
* Unit-test hydration semantics for a path present on publish and a path absent there but committed on main.
* Run one integration test against a temporary bare remote. Assert normal publication advances the proof `publish` ref by exactly one commit; identical rerun and injected failure do not advance it; candidate and accepted generated manifests match; hydrated and accepted publish-present paths match; and no real remote URL appears in subprocess arguments or evidence.
* Keep existing focused checks: `pytest tests/test_atomic_publish_proof.py tests/test_publish_hydration.py tests/test_publish_safety.py tests/test_pipeline.py` and `ruff check scripts/atomic_publish_proof.py tests/test_atomic_publish_proof.py`.

### Side-effect boundaries

* The only writable Git remote is a bare repository created below `tempfile.TemporaryDirectory()`.
* The GitHub evidence workflow has no `contents: write`, no persisted checkout credential, no environment, no deployment permission, and no secrets.
* Remove `GH_TOKEN`, `GITHUB_TOKEN`, SSH agent variables, and credential-helper configuration from the child environment. Set `GIT_TERMINAL_PROMPT=0`.
* Reject non-local proof remote URLs and verify the bare remote resolves below the temporary root before each publication scenario.
* Never use the production branch name as a GitHub ref. `publish` exists only inside the local bare repository.
* Do not invoke crawl APIs, Copilot, GitHub Models, releases, deployments, issue creation, webhook notification, sync-to-main, or Podcaster handoff.
* Read `origin/publish` only to seed realistic retained state. All generated mutations, commits, pushes, and failure residue remain temporary.

### Why this is the smallest safe option

An acceptance branch in the production repository would still trigger branch-adjacent automation and require write credentials. A new publisher helper would duplicate or refactor the production transaction, so a green harness could diverge from the actual workflow or introduce publication risk. Extracting and executing the checked-in commit step against a local bare remote keeps production unchanged, proves real Git lease and no-op behavior, and gives the manual workflow a durable run URL and artifact without granting mutation authority.

## Evidence

* `.github/workflows/crawl-and-publish.yml`: workflow inputs and concurrency; `Record publish branch base`; generate hydration; ordered generators and freshness checks; `Commit generated content to data branch`.
* `.github/workflows/deploy-site.yml`: `Hydrate generated content from publish`.
* `.github/workflows/ci.yml`: read-only `publish-hydration-parity` job.
* `scripts/publish_hydration.py`: `GENERATED_PATHS`, `check_publish_references()`, and CLI path/check commands.
* `scripts/publish_safety.py`: immutable backup and restore functions plus weekly transaction paths.
* `scripts/promotion_guard.py`: transactional candidate promotion and stable promotion transaction identity.
* `tests/test_pipeline.py`: static transaction ordering, path, lease, and no-op contracts.
* `tests/test_publish_hydration.py`: consistent release fixture, reference failures, deploy-list parity, and CI hydration contract.
* `tests/test_publish_safety.py`: immutable backup, provenance, restoration, and raw-store tests.
* `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md`: controlling Step 6.1 criteria.
* `.copilot-tracking/reviews/2026-08-02/claracle-relaunch-readiness-reconciliation-plan-review.md`: atomic acceptance overstatement finding.
* `.copilot-tracking/research/subagents/2026-08-03/claracle-protected-acceptance-gates-research.md`: current-main evidence status and missing matrix.

## Follow-On Questions

No blocking design question remains. Before implementation, choose the artifact retention period and whether the controlling changes log should store the complete JSON or only the immutable workflow run and artifact identifiers.
