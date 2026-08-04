<!-- markdownlint-disable-file -->
# Claracle Hugo and Pagefind Cost Experiment Research

## Research Scope

* Design a report-only, manually dispatchable Hugo and Pagefind workload-variant cost experiment for current `main`.
* Satisfy the 2026-08-02 gated rollout cost plan while keeping rollout flags disabled.
* Prefer existing scripts and workflows with minimal implementation.
* Define variants, isolation, metrics schema, aggregation, artifacts, tests, and security checks.
* Do not dispatch the experiment during research.

## Status

Complete. Research only; no workflow was dispatched and no source file was changed.

## Findings

* Current `main` is `4b7c5cf506b2e8b73350ff94ce80669c93810e66`, equal to
	`origin/main` at research time. The locally available `origin/publish` is
	`4120078d2615463ad8ae99af1e7801be65c4b11d`.
* Both rollout controls remain disabled in `config/observatory.toml`:
	`repo_pages.enabled = false` and
	`topic_hubs.dynamic_creation.enabled = false`.
* Current `main` has exactly 5 topic-hub leaves, 3 generated data-page leaves,
	and 263 repository-page leaves. Each data and repository class also has a
	section `_index.md`; `content/topics/_index.md` is likewise a class root.
* `.github/workflows/ci.yml` already pins Hugo Extended 0.161.1 and Pagefind
	1.5.2, times them separately, writes `reports/build-timing.json`, and uploads
	a 30-day report-only artifact. This is the correct setup to reuse.
* The existing timing schema is insufficient for Q-01. It omits workload
	variant, publish SHA, runner image, source/rendered/indexed counts, output
	bytes, repetitions, aggregation, and page-class deltas.
* `scripts/publish_hydration.py` owns the canonical deploy hydration path list.
	The experiment should call `python3 -m scripts.publish_hydration paths` and
	`check`, rather than copying another path list.
* The page generators must not run in this experiment. Repository generation
	can rewrite and remove durable pages when enabled, while dynamic topic
	`--dry-run` exits without producing a proposed diff. Checked-in leaves are
	sufficient to measure the current 5/3/263 workload.
* `scripts/baseline_telemetry.py` already defines nearest-rank percentiles as
	sorted value at `ceil(p * n) - 1`. Its implementation can be reused. With
	three or five samples, nearest-rank p95 is the observed maximum and the
	report must say so.
* A dedicated workflow is smaller and safer than adding `workflow_dispatch`
	to `.github/workflows/ci.yml`, which would also dispatch unrelated CI jobs.

## Evidence

* `.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md`
	requires isolated variants, both SHAs, separate Hugo/Pagefind metrics, at
	least three comparable runs, nearest-rank p95, deltas, marginal cost, and a
	non-blocking report.
* `.copilot-tracking/research/subagents/2026-08-02/claracle-rollout-cost-followup-research.md`
	identifies the safe cumulative classes and the hydration, identity, and
	dynamic-preview constraints.
* `.github/workflows/ci.yml` contains the pinned production build setup and
	current report-only timing artifact.
* `.github/workflows/generate-data-pages.yml` demonstrates a read-only manual
	workflow and publish hydration, but duplicates an older subset of paths.
* `scripts/publish_hydration.py` contains the canonical generated path list and
	hydrated-reference checks.
* `scripts/observatory_repos.py` proves disabled generation is non-mutating and
	enabled generation can rewrite or remove durable output.
* `scripts/manage_topic_hubs.py` proves disabled creation is non-mutating and
	enabled `--dry-run` is an early exit rather than a preview.
* `scripts/baseline_telemetry.py` contains the repository's nearest-rank
	percentile implementation.
* `docs/design/data-observatory-model.md` records the sole local observation:
	6,668 ms for Hugo and 6,207 ms for Pagefind over the full workload. It
	explicitly leaves three comparable external runs and aggregation pending.
* `docs/prds/claracle-data-observatory-relaunch.md` keeps Q-01 and NFR-009 open.
* `docs/review/data-observatory-relaunch/security-review.md` requires URL
	workflow review and forbids secrets in evidence.

## Recommended Design

### Minimal implementation surface

Add only these source files when implementation is approved:

1. `.github/workflows/build-cost-experiment.yml`, a manual-only, read-only
	 workflow
2. `scripts/build_cost_experiment.py`, a standard-library variant runner,
	 metrics writer, and aggregator
3. `tests/test_build_cost_experiment.py`, including workflow contract tests

Reuse the Hugo installation and checksum verification from
`.github/workflows/ci.yml`, Pagefind 1.5.2, Node.js 24, Python 3.12, the canonical
publish hydration helper, and `baseline_telemetry.percentile`. Do not add a
package, service, database, generator mode, or rollout switch.

### Manual dispatch contract

Use `workflow_dispatch` only. Give it three constrained inputs:

* Required `reviewed_main_sha`, exactly 40 lowercase hexadecimal characters
* Required `reviewed_publish_sha`, exactly 40 lowercase hexadecimal characters
* `repetitions`, a choice of `3` or `5`, defaulting to `5`

The job must run only when the selected workflow ref is `refs/heads/main`,
compare `reviewed_main_sha` with `github.sha`, fetch `publish`, verify the
reviewed publish commit exists and is reachable from `origin/publish`, then
hydrate from that exact commit. Inputs must pass through environment variables
and argument arrays, never GitHub expression interpolation inside shell text.

There should be no rollout, threshold, arbitrary ref, path, command, or canary
input. Set `permissions: { contents: read }`, use one non-cancelling concurrency
group, and upload an artifact even on a failed sample. Do not use an Actions
cache because cache state would become an uncontrolled experimental variable.

Before measurement, fail unless both rollout flags are boolean false. Run
`python3 -m scripts.publish_hydration check` after hydration. Record the exact
resolved SHAs; never modify or push the checkout.

### Workload variants and isolation

Create one canonical hydrated corpus outside the measured interval. For every
sample, copy that corpus into a new runner-temporary directory, reject symlinks
that escape the corpus, remove only classified workload leaves, and build into
a fresh destination with Hugo's clean-destination behavior. Preserve the three
class-root `_index.md` files in every variant so section scaffolding is constant.

| Order | Variant | Included class leaves | Added leaves | Cumulative leaves |
|-------|---------|-----------------------|-------------:|------------------:|
| 0 | `baseline` | None | 0 | 0 |
| 1 | `topic_hubs` | Five topic hubs | 5 | 5 |
| 2 | `data_pages` | Topic hubs and three data pages | 3 | 8 |
| 3 | `repository_pages` | Topic hubs, data pages, and 263 repository pages | 263 | 271 |

Generate a manifest before timing with every included leaf's relative path,
class, byte size, and SHA-256. Fail closed if paths overlap classes, escape the
repository, or current-main counts differ from 5/3/263 for the reviewed SHA.
Never infer a workload from generated `public/` output.

Run all variants in each repetition on one hosted runner for paired comparison.
Rotate the independent-copy execution order by repetition to reduce warm-cache
position bias. Install Pagefind once before timing and invoke it with
`npx --no-install pagefind`; package resolution and download time must not enter
the Pagefind duration.

An optional `dynamic_canary` variant is not runnable from current `main` because
no exact canary is approved and `--dry-run` cannot produce one. The schema may
reserve this variant. Enable it only through a later reviewed code change that
pins the exact canary patch and file hashes, keeps both production flags false,
and applies the patch to isolated copies. Record one added source page plus the
count and hashes of modified weekly/taxonomy files. Do not execute the dynamic
generator in the timing workflow.

### Raw metrics schema

Write one JSON document per repetition and variant with schema version
`claracle_build_cost_sample_v1`. Required fields are:

```json
{
	"schema_version": "claracle_build_cost_sample_v1",
	"mode": "report-only",
	"blocking_threshold_ms": null,
	"experiment": {
		"run_id": "github.run_id",
		"run_attempt": 1,
		"repetition": 1,
		"execution_position": 1
	},
	"provenance": {
		"main_sha": "40-hex",
		"publish_sha": "40-hex",
		"workflow_sha": "40-hex"
	},
	"runner": {
		"os": "Linux",
		"arch": "X64",
		"image_os": "ubuntu24",
		"image_version": "..."
	},
	"variant": {
		"name": "data_pages",
		"included_classes": ["topic_hubs", "data_pages"],
		"source_pages_total": 8,
		"source_pages_added": 3,
		"source_bytes_total": 0,
		"manifest_sha256": "64-hex"
	},
	"tools": {
		"hugo": "hugo v0.161.1+extended ...",
		"pagefind": "1.5.2",
		"node": "...",
		"python": "..."
	},
	"hugo": {
		"duration_ms": 0,
		"rendered_html_files": 0,
		"output_bytes": 0,
		"exit_code": 0
	},
	"pagefind": {
		"duration_ms": 0,
		"html_files_scanned": 0,
		"indexed_pages": 0,
		"index_bytes": 0,
		"exit_code": 0
	},
	"status": "passed"
}
```

Use `time.monotonic_ns()` around only the Hugo process and only the installed
Pagefind process. Count rendered HTML and Hugo bytes after Hugo and before
Pagefind. Parse Pagefind's retained stdout for files scanned and pages indexed;
fail the sample if expected counters are absent rather than silently substituting
different semantics. Preserve both tool logs beside the JSON.

### Aggregation

Aggregate Hugo and Pagefind separately. Sort numeric samples before every
calculation. For values `x` with sample count `n`:

* Median is the middle value for odd `n`, or the arithmetic mean of the two
	middle values for even `n`
* Nearest-rank p95 is `sorted(x)[ceil(0.95 * n) - 1]`
* Absolute delta is `variant_median_ms - predecessor_median_ms`
* Percent delta is `100 * absolute_delta_ms / predecessor_median_ms`, or null
	when the predecessor median is zero
* Marginal cost is `absolute_delta_ms / source_pages_added`, or null when no
	source page was added

Also retain per-repetition paired deltas and report their median and p95. These
diagnostics expose runner drift even though the plan's headline deltas use
variant medians. Negative deltas are valid observations and must not be clamped.
Optionally report combined Hugo-plus-Pagefind totals, but never replace the two
stage reports with that total.

Aggregation must reject mixed SHAs, versions, runner image versions, variant
manifests, repetition counts, failed samples, duplicate repetition/variant
pairs, or missing variants. A three-run report is acceptable and marked
`minimum`; five runs is `preferred`. No cost value can fail the workflow because
`blocking_threshold_ms` remains null.

### Artifacts

Upload one artifact named
`hugo-pagefind-cost-${github.run_id}-${github.run_attempt}` for 90 days with:

* `manifest.json` containing dispatch inputs, resolved provenance, variant
	definitions, execution order, tool versions, and source-file hashes
* `samples/<repetition>/<variant>.json`
* `logs/<repetition>/<variant>-hugo.log` and `-pagefind.log`
* `summary.json` using schema `claracle_build_cost_summary_v1`
* `summary.md` with sample counts, medians, nearest-rank p95, deltas, marginal
	milliseconds per added source page, and the report-only caveat
* `SHA256SUMS` covering every retained report, sample, and log

Do not upload copied worktrees, rendered sites, hydrated raw data, environment
dumps, npm caches, credentials, or secret-bearing logs. Add the concise summary
to `GITHUB_STEP_SUMMARY`; the artifact remains the evidence of record.

### Tests and validation

Focused unit tests should cover:

* Median for odd and even sample counts and nearest-rank p95 boundaries
* Absolute, percent, paired, and marginal deltas, including zero and negative
	cases
* Rejection of mixed provenance, versions, manifests, duplicates, failures,
	and incomplete repetitions
* Variant materialization preserving class roots and producing 0/5/8/271
	cumulative current-main leaves without changing the canonical tree
* Path traversal and escaping-symlink rejection
* Hugo and Pagefind log parsing with valid and malformed fixtures
* Stable JSON/Markdown ordering and SHA-256 manifest generation
* Workflow shape: manual-only trigger, read-only permissions, pinned actions,
	no persisted checkout credentials, no secrets, no write/push step, null
	threshold, and disabled-flag assertion

Implementation validation should run:

```bash
python -m pytest tests/test_build_cost_experiment.py tests/test_pipeline.py
python -m pytest tests/
ruff check scripts/build_cost_experiment.py tests/test_build_cost_experiment.py
ruff format --check scripts/build_cost_experiment.py tests/test_build_cost_experiment.py
zizmor .github/workflows/build-cost-experiment.yml
checkov --file .github/workflows/build-cost-experiment.yml --framework github_actions --compact
hugo --minify
npx "pagefind@1.5.2" --site public/
```

The implementation PR should also verify `git diff --check` and confirm both
flags remain false. These checks validate implementation; they do not dispatch
the experiment or approve a blocking budget.

### Security properties

* Manual trigger only, default-branch workflow only, and immutable reviewed SHAs
* Read-only token, no environment secrets, no protected environment, no push
* Full-SHA-pinned actions and checksum-verified Hugo download
* Exact Pagefind version installed outside measured intervals
* No arbitrary refs, paths, shell fragments, or generator controls from inputs
* Quoted environment-variable handling and strict SHA/path validation
* No execution of content-derived commands and no rollout generator invocation
* Fail-closed parsers and provenance checks
* Minimal artifact allowlist with checksums and no hydrated or rendered corpus
* Zizmor and Checkov review required for the workflow change
* Hermes and URL review remains separate from this technical report; this
	experiment does not close NFR-004 or authorize either rollout

## Follow-on Research

* [ ] Inspect retained artifacts from the first three or preferably five
	dispatched repetitions after implementation approval
* [ ] Confirm owner acceptance of the paired-run methodology and nominate the
	future budget owner
* [ ] Design the exact optional dynamic canary manifest only after editorial,
	Hermes, URL, and sponsor approval identifies one immutable patch
* [ ] Propose budgets and an observation window from retained evidence; budget
	enforcement is explicitly outside this experiment

## Clarifying Questions

None block implementation of the report-only base experiment. Owner input is
required later for the exact dynamic canary and for any blocking budget.
