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