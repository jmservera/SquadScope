<!-- markdownlint-disable-file -->
# Planning Log: Claracle All Follow-Ups

## Selected Paths

* Atomic proof: execute checked-in production commit logic only against a local bare remote.
* Podcaster: protected exact manual generation, no automatic real dispatch.
* Cost: read-only cumulative variants with report-only statistics.
* UX: retain absolute-star semantics and remove clipping with a stable dataset maximum.
* Lighthouse: preserve every threshold while improving fidelity, documentation, and wall-clock behavior.

## Known Deferrals

* Human approvals and private production observations
* GitHub environment policy and secret configuration
* Actual real Podcaster dispatch and downstream completion
* Actual cost experiment dispatch and budget approval
* Historical topic backfill promotion to `publish`
* Dynamic canary and repository-page production rollouts

## Deviations

* The atomic harness initially revealed that identical publish reruns could create
	backup-only commits. The production workflow now compares candidate generated state
	with `publish` before immutable backup creation.
* The atomic integration fixture became dependent on retained proof content. A unique
	temporary-run nonce now guarantees a normal mutation while preserving identical reruns.
* The protected Podcaster workflow contained an indentation error in its embedded Python.
	The block was corrected and its source is now compiled by the workflow contract test.
* System Python could not install Brotli because the environment is externally managed.
	Dependencies were synchronized into the existing `.venv` with `uv pip install`.
* PR #655's first CI run surfaced issues invisible to local testing, where all branches
	are already fetched: `origin/publish` was not resolvable on the shallow, single-ref
	`actions/checkout`. Fixed by fetching `origin publish` before the rev-parse, mirroring
	the production commit step's own fetch-then-rev-parse pattern.
* Bandit flagged 12 low-severity/high-confidence subprocess findings in the two new
	scripts (`atomic_publish_proof.py`, `build_cost_experiment.py`). Suppressed with
	`# nosec` annotations following the repo's existing convention (see
	`scripts/copilot_failure.py`). Discovered that Bandit 1.9.4's nosec comment parser
	drops all but the last code in a comma-separated list (`# nosec B603,B607`) due to a
	regex capture-group reuse bug; switched those three lines to a bare `# nosec` instead.
* GitHub's Checkov code-scanning check flagged `build-cost-experiment.yml`'s
	`workflow_dispatch` inputs (`CKV_GHA_7`) even though a skip comment was present,
	because the comment sat above `on:` instead of nested inside `workflow_dispatch:`
	(the placement `trigger-podcast.yml` already used successfully). Moved the skip
	comment to match.
* Automated PR review (`copilot-pull-request-reviewer`) flagged that
	`trigger-podcast.yml`'s job lacked a `main`-only branch guard even though it checks out
	the default branch explicitly (the dispatched workflow YAML itself still runs from the
	dispatched ref). Added `if: ${{ github.ref == 'refs/heads/main' }}` at the job level,
	matching `build-cost-experiment.yml`'s existing guard.
* Automated PR review also flagged `tests/test_pipeline.py` reading workflow triggers via
	`workflow[True]` (relies on PyYAML 1.1 boolean-key parsing of `on:`). Replaced with the
	safer `workflow.get("on", workflow.get(True))` pattern already used in
	`tests/test_build_cost_experiment.py` and `tests/test_copilot_pricing_review.py`.
* The second CI run (after the `origin/publish` fetch fix) got further and revealed a
	second shallow-clone issue: `seed_isolated_origin()` pushes `HEAD`'s SHA to a fresh
	empty bare repo, which git rejects with "shallow update not allowed" because CI's
	`HEAD` is shallow (only the tip commit's objects exist) while `origin/publish` (fetched
	without `--depth`) is not. Fixed by running `git fetch --unshallow origin` first when
	`git rev-parse --is-shallow-repository` reports `true`. Verified by reproducing
	`actions/checkout`'s exact shallow-fetch approach (not a single-branch clone) against
	the real GitHub remote and re-running the proof end to end (exit 0).

## Validation Iterations

* Combined focused Python validation: 127 passed, 2 Hugo-dependent skips, and 26 subtests
* Full Python validation: 1,434 passed, 20 skipped, 2 expected warnings, and 34 subtests
* Protected workflow contract validation: 30 passed and 19 subtests
* Lighthouse Node tests: 2 passed
* Ruff check and format check: passed
* Diff whitespace validation: passed
* Checkov: 843 passed, 0 failed, and 5 skipped
* Zizmor: 0 medium or high findings; one pre-existing low-severity ad-hoc package finding
* No workflow was dispatched, `config/podcast.json` was unchanged, and both rollout flags remained disabled