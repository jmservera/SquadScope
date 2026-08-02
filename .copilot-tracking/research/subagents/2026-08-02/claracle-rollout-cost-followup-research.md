<!-- markdownlint-disable-file -->
# Claracle Rollout and Cost Follow-Up Research

## Research Scope

* Investigate existing `repo_pages` rollout behavior and safety dependencies
* Investigate existing `dynamic_topic_creation` rollout behavior and safety dependencies
* Determine how Hugo and Pagefind timings are separated today
* Determine what measurable instrumentation exists for incremental generation cost Q-01/NFR-009
* Identify the smallest implementation-ready phases and precise validations

## Executive Findings

* Both production creation controls are off. `repo_pages.enabled = false` and
	`topic_hubs.dynamic_creation.enabled = false` are defined in
	`config/observatory.toml:1-33`.
* The flags freeze mutation, not visibility. The repository contains 263 generated
	repository pages plus `content/repo/_index.md`, five seed topic hubs, and three
	generated data-page leaves. Hugo still renders those durable files while the
	generators are disabled.
* Repository rollout is an all-current-state activation, not a first publication of
	263 pages. The July 29 implementation commits generated pages; commit `879c42c`
	added `repo_pages.enabled = false`, changed dynamic creation from true to false,
	and preserved the generated state and lifecycle ledger.
* Dynamic activation currently has five eligible candidates among 2,173 candidates:
	AI Memory, fable, inference, Local First, and Self Hosted. Enabling the flag without
	changing the ignore list can promote all five in one publish transaction.
* Hugo and Pagefind are timed separately only in the CI `production-site` job. CI
	writes one report-only `reports/build-timing.json` artifact with separate
	`duration_ms` values and no threshold. This is total build timing, not incremental
	cost attribution by hubs, data pages, or repository pages.
* Q-01/NFR-009 remains open. One local observation exists, but there is no retained
	representative series, median/p95 report, approved budget, per-page-class workload
	metadata, or blocking threshold.
* The smallest safe sequence is: measure immutable workload variants first, close
	security and identity blockers, canary one reviewed dynamic topic through the
	existing ignore list, then activate repository regeneration as one reviewed
	transaction. Repository threshold changes are not a safe canary because generated
	pages outside the new expected set are treated as obsolete and can be deleted.

## Existing Flag Behavior

### Repository pages

`scripts/observatory_repos.py:205-220` loads the flag, recurrence threshold, three-year
retention, lifecycle overrides, and lifecycle-ledger path. The threshold is strictly
`>` and defaults to more than three distinct weekly issues, equivalent to four weeks.

`scripts/observatory_repos.py:997-1020` returns immediately when disabled. It does not
read or update the ledger, generate derived data, create pages, delete durable pages,
or validate staleness. The same early return applies to `--check`, so a green disabled
freshness check does not prove repository outputs are current.

`scripts/observatory_repos.py:922-994` computes all expected page and derived outputs
when enabled. In write mode it creates or rewrites expected outputs and removes
obsolete generated pages. In check mode it returns stale, obsolete, and expired paths
without writing. This means recurrence-threshold reduction or a small threshold-based
canary can classify existing generated pages as obsolete.

`scripts/observatory_repos.py:813-859` provides a separate lifecycle seed operation.
It requires production `repo_pages.enabled = false`, validates parity among qualified
histories, repository pages, and derived repository data, then atomically writes only
`data/derived/observatory/repository-lifecycle.json`. It is byte-stable when repeated.

Current durable state, corroborated by
`tests/test_observatory_repos.py:570-581`, is:

| Measure | Current value |
|---------|--------------:|
| Lifecycle histories | 2,242 |
| Qualified histories | 263 |
| Generated repository page leaves | 263 |
| Histories with stable `github_id` | 0 |
| Lifecycle statuses | 2,242 active; no checked-in rename/archive/delete transition |

The code can absorb fallback name history into a stable GitHub ID later, as tested in
`tests/test_observatory_repos.py:584-627`, but production inputs have not supplied those
IDs. Stable canonical rename behavior is therefore implemented but not evidenced on
the production corpus.

### Dynamic topic creation

Candidate discovery is independent from promotion. The publish workflow always runs
`scripts/discover_topic_candidates.py`, which derives a byte-stable registry from
weekly content, analyzed summaries, and raw observations. It uses the configured
four-week threshold, 62-day lookback, ignore list, and repository recurrence threshold
from `scripts/discover_topic_candidates.py:53-67`.

`scripts/manage_topic_hubs.py:407-419` exits before reading candidates or writing a log
when the creation flag is disabled. `--dry-run` also exits at this point when enabled;
it is a no-op safety switch, not a preview of proposed changes.

When enabled, `scripts/manage_topic_hubs.py:421-486` can perform one transaction that:

* Creates `content/topics/<slug>/_index.md`
* Promotes the term in `data/taxonomy/topics.json`
* Assigns the topic to historical weekly frontmatter supported by evidence
* Reassigns already promoted topics from current source evidence
* Refreshes taxonomy registries
* Appends decision and summary entries to
	`data/topic-hubs/dynamic-topic-creation.log`

Creation is additive. Quiet or subsequently ineligible hubs are not deleted. Turning
the flag off stops future mutation but does not reverse promoted registry entries,
topic pages, weekly assignments, or logs.

The current candidate registry in `data/taxonomy/topic-candidates.json` has 2,173
candidates and five eligible candidates. Each eligible candidate has at least four
weekly issues and at least one supporting signal. The threshold alone is not editorial
approval; `fable` and `inference`, for example, are broad terms requiring human review.

The existing `ignore_topics` list can implement a configuration-only canary by adding
four reviewed deferrals and allowing one candidate. There is no positive allowlist,
maximum creations per run, or useful non-mutating preview mode.

## Rollout Safety Dependencies

### Shared dependencies

* Generated state must be hydrated from `publish` before any preflight or measurement.
	The publish generator does this in
	`.github/workflows/crawl-and-publish.yml:1048-1077`; deployment does it in
	`.github/workflows/deploy-site.yml:88-122`.
* The `weekly-crawl` concurrency group uses `cancel-in-progress: false` at
	`.github/workflows/crawl-and-publish.yml:64-66`, preventing overlapping publish
	mutations.
* Generated content, taxonomy, topic logs, and repository derived state are committed
	together by `.github/workflows/crawl-and-publish.yml:1224-1263` and must be reviewed
	as one transaction.
* Hermes security acceptance, URL workflow review, and jmservera sponsor approval are
	all pending in
	`docs/review/data-observatory-relaunch/security-review.md:151-169`.
* The PRD requires separate sponsor-approved rollouts after security and lifecycle
	evidence in `docs/prds/claracle-data-observatory-relaunch.md:260-267`.

### Repository-specific dependencies

* Run lifecycle parity seed twice while disabled against the hydrated publish revision.
* Acquire stable GitHub identity fields or explicitly disposition fallback name identity
	risk before claiming FR-020 stable canonical URLs or FR-022 rename safety.
* Exercise reviewed rename, archive, and deletion evidence. Current production ledger
	contains only active histories, while fixture coverage exists in
	`tests/test_observatory_repos.py:664-761`.
* Run enabled `--check` and a full generation in a disposable worktree before changing
	production config. Review every created, rewritten, obsolete, and expired path.
* Preserve the current threshold during activation. A threshold canary is unsafe because
	the generator removes obsolete generated pages.

### Dynamic-topic-specific dependencies

* Hermes must disposition SEC-01. Structured YAML and adversarial title rejection are
	implemented in `tests/test_topic_hubs.py:527-586`, but the security review still
	records dynamic title handling as rollout-blocking.
* Review each eligible candidate's evidence, semantics, aliases, and affected weekly
	files before promotion.
* Use a disposable worktree with a temporary enabled config to obtain the proposed diff,
	because current `--dry-run` does not evaluate candidates.
* Select a single canary through `ignore_topics`, retain the other eligible candidates as
	explicit deferrals, and obtain sponsor approval for that exact config and diff.

## Hugo and Pagefind Timing Separation

The CI production-site job has separate timed steps:

* Hugo Extended 0.161.1 at `.github/workflows/ci.yml:127-134`
* Pagefind 1.5.2 at `.github/workflows/ci.yml:136-143`
* JSON report writing at `.github/workflows/ci.yml:145-156`
* Artifact retention under `production-quality-reports` at
	`.github/workflows/ci.yml:181-191`

The report schema records commit, report-only mode, tool versions, and separate
durations. `blocking_threshold_ms` is null. This correctly prevents an unapproved
budget from becoming a gate.

Timing comparability gaps remain:

* CI builds the checked-out branch and does not hydrate generated state from `publish`.
	Deploy and crawl do hydrate it, so CI timing can measure a different workload.
* Crawl, deploy, and preview invoke unpinned `npx pagefind`; only CI pins Pagefind 1.5.2.
	References: `.github/workflows/crawl-and-publish.yml:1446-1449`,
	`.github/workflows/deploy-site.yml:178-181`, and
	`.github/workflows/site-preview.yml:116-119`.
* The report omits source-page counts, rendered-page counts, HTML files scanned, indexed
	pages, output bytes, runner identity, hydration source SHA, and workload variant.
* The artifact is ephemeral and no repository process aggregates comparable reports.
* Hugo and Pagefind are sequentially separated, but neither generator execution time nor
	incremental page-class contribution is measured.

## Existing Cost and Measurement Evidence

`docs/design/data-observatory-model.md:400-449` records one local report-only sample:

| Stage | Duration | Workload evidence |
|-------|---------:|-------------------|
| Hugo 0.161.1 | 6,668 ms | 2,669 rendered pages |
| Pagefind 1.5.2 | 6,207 ms | 1,477 HTML files scanned; 288 pages indexed |

The design document correctly labels this observation as insufficient and requires
three comparable external CI reports, median and p95, a proposed blocking budget, and
owner approval. Prior validation reaches the same conclusion in
`.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-007-validation.md:128-203`.

Reusable percentile code exists in `scripts/baseline_telemetry.py:69-124`, with tests in
`tests/test_baseline_telemetry.py`, but it is scoped to crawl/analysis observability
ledgers and uses a five-run readiness baseline. It does not consume
`build-timing.json` or calculate incremental generation cost.

The current repository provides useful workload counters but no integrated cost record:

* 5 seed topic hubs under `content/topics/`
* 3 generated data-page leaves under `content/data/`
* 263 generated repository page leaves under `content/repo/`
* 5 currently eligible dynamic topic candidates
* Generator summaries such as `Generated <n> repository pages` and
	`dynamic-topic-summary created=<n> skipped=<n>`

Q-01 is therefore measurable with existing tools, but not answered by existing data.

## Selected Approach

### Phase 1: Implement a report-only incremental cost experiment

Use a disposable worktree hydrated from the same `publish` SHA for every variant. Keep
Hugo, Pagefind, runner image, config, and source revision fixed. Build into clean,
variant-specific destinations so tracked `public/` content cannot contaminate results.

Measure these cumulative variants:

1. Observatory generated page classes excluded
2. Add the five checked-in topic hubs
3. Add the three generated data pages
4. Add the 263 checked-in repository pages
5. Optionally add the exact reviewed dynamic canary diff

Run at least three comparable CI repetitions because that is the documented acceptance
minimum; five runs aligns with the repository's existing baseline-telemetry convention.
For each repetition and variant, record:

* Main SHA and hydrated publish SHA
* Runner image and tool versions
* Source Markdown counts by page class
* Hugo duration and rendered page count
* Pagefind duration, HTML files scanned, and indexed page count
* Hugo destination bytes and Pagefind index bytes
* Exit status and run/artifact URL

Aggregate median, nearest-rank p95, absolute delta, percent delta, and marginal
milliseconds/added source page separately for Hugo and Pagefind. Do not enforce a budget
in this phase. Publish the report and obtain owner approval before replacing the null
threshold.

### Phase 2: Prepare repository activation without enabling production

1. Resolve or explicitly accept the missing stable-ID risk and review lifecycle evidence.
2. Hydrate the target publish revision and run lifecycle seed twice while disabled.
3. Confirm 263-way parity and byte-identical second seed.
4. In a disposable worktree, enable the existing config without changing the threshold.
5. Run `observatory_repos.py --check`, then generation twice, and review all output diffs.
6. Run repository tests, Hugo, pinned Pagefind, rendered SEO/link checks, internal links,
	 Lighthouse, axe, and the Q-01 workload measurement.
7. Obtain Hermes, URL, and sponsor sign-offs for the exact revision and diff.

### Phase 3: Canary one dynamic topic

1. Review all five eligible candidates and select one unambiguous canary. `local-first`
	 currently has the strongest evidence breadth with six weekly issues and five
	 supporting signals, but editorial/security review must make the final choice.
2. Add the other four candidates to `ignore_topics` as explicit temporary deferrals.
3. Produce the enabled result in a disposable worktree and review the hub, canonical
	 registry change, historical weekly assignments, taxonomy changes, and log event.
4. Run the focused and rendered validation suite and capture incremental timing.
5. Obtain approval, enable the flag for one publish run, inspect the committed generated
	 transaction, and turn the flag off or retain the restricted ignore list according to
	 the approved rollout decision.

### Phase 4: Activate repository regeneration

Enable `repo_pages` at the unchanged threshold only after Phases 1 and 2 pass. Treat the
first publish as a single 263-page lifecycle activation. Verify no unexpected obsolete or
expired paths before promotion. Rollback requires both disabling the flag and reverting
the generated transaction; disabling alone preserves mutations already committed.

### Phase 5: Expand and enforce

Remove dynamic candidate deferrals one reviewed candidate at a time. After enough stable
timing samples and explicit owner approval, add separate Hugo and Pagefind budgets with a
report-only observation period before making either threshold blocking.

## Dependencies and Blockers

### Blocking

* Hermes NFR-004/security sign-off is pending, including SEC-01 dynamic-title disposition
	and SEC-04 lifecycle deletion policy.
* URL workflow/security sign-off and jmservera sponsor rollout approval are pending.
* All 2,242 production repository histories lack stable GitHub IDs; stable rename identity
	is not evidenced.
* Production lifecycle state has no reviewed rename, archive, or deletion transition.
* Dynamic `--dry-run` cannot preview the mutation set; a disposable worktree is required
	unless preview semantics are implemented first.
* Q-01 lacks comparable CI samples, aggregation, approved budgets, and page-class
	attribution.

### Non-blocking implementation dependencies

* Access to the canonical `publish` branch and retained workflow artifacts
* Hugo Extended 0.161.1, Pagefind 1.5.2, Python 3.12, and Node.js 24
* A clean disposable worktree or equivalent isolated checkout per workload variant
* Existing generated-state transaction paths in crawl, deploy, and freshness workflows
* Existing tests for disabled-state preservation, deterministic generation, structured
	YAML, adversarial titles, lifecycle retention, stable-ID migration, and Hugo rendering

## Precise Validations

### Flag and generator behavior

```bash
python -m pytest tests/test_observatory_repos.py tests/test_topic_hubs.py tests/test_taxonomy_registry.py
python scripts/discover_topic_candidates.py --check
python scripts/generate_data_pages.py --check
python scripts/export_observatory_dataset.py --check
python scripts/export_trend_explorer_data.py --check
```

Run repository freshness against a temporary config with `repo_pages.enabled = true`;
the production disabled config makes `observatory_repos.py --check` a no-op.

For repository activation, require:

* Lifecycle seed parity is 263 qualified histories, 263 page identities, and 263 derived
	identities
* The second lifecycle seed is byte-identical
* Enabled check reports no unexplained stale, obsolete, or expired paths
* Two enabled generations produce byte-identical outputs
* No page removal occurs without reviewed positive lifecycle evidence and elapsed
	retention

For dynamic canary activation, require:

* Exactly one approved hub is created
* Only evidence-backed weekly files receive the topic assignment
* Registry YAML/JSON remains parseable and canonical aliases resolve
* A structured promotion log records evidence weeks, sources, and assigned paths
* A second run is additive and byte-stable except for explicitly designed append-log
	behavior
* Disabled rollback creates or deletes nothing

### Rendered and pipeline behavior

```bash
hugo --minify
npx "pagefind@1.5.2" --site public/
python scripts/check_internal_links.py public --base-url "https://claracle.com/"
python -m pytest tests/test_rendered_seo_metadata.py tests/test_rendered_weekly_links.py tests/test_internal_link_checker.py
python -m pytest tests/
ruff check .
ruff format --check .
```

Also run the existing Lighthouse and axe route matrices, which include a topic, data, and
repository page at `scripts/design/lighthouse-gates.mjs:28-36` and the Observatory visual
tests. If a workflow changes, run Zizmor and Checkov under the repository guardrails.

### Cost acceptance

* Every timing artifact identifies both main and publish SHAs and the workload variant
* Hugo and Pagefind retain separate raw samples and statistics
* Each variant starts from a clean destination and uses pinned versions
* At least three comparable CI repetitions exist; five are preferred
* Median and p95 are reproducible from retained machine-readable samples
* Incremental deltas are reported by page class, not inferred from one total build
* The approved budget names its owner, sample window, headroom rationale, and enforcement
	date
* Thresholds remain report-only until approval is recorded

## Evidence Index

* `config/observatory.toml:1-33` controls both disabled rollouts
* `scripts/observatory_repos.py:205-220,813-859,922-1020` defines config, lifecycle seed,
	writes/checks, and disabled behavior
* `scripts/discover_topic_candidates.py:53-67` defines candidate policy inputs
* `scripts/manage_topic_hubs.py:407-486` defines disabled, dry-run, and mutation behavior
* `tests/test_observatory_repos.py:570-790` proves frozen-corpus parity, stable-ID
	migration, disabled preservation, lifecycle rendering, and Hugo output
* `tests/test_topic_hubs.py:204-376,444-588` proves additive creation, persistence,
	disabled preservation, unsafe-title rejection, and structured YAML
* `.github/workflows/crawl-and-publish.yml:1048-1077,1139-1210,1224-1263` hydrates,
	generates, checks, and commits the generated transaction
* `.github/workflows/ci.yml:127-156,181-191` emits and uploads separate timing data
* `.github/workflows/deploy-site.yml:88-122,178-181` hydrates production generated state
	and builds Hugo/Pagefind
* `.github/workflows/generate-data-pages.yml:1-66` hydrates publish state for monthly
	freshness checks
* `docs/data-observatory-runbook.md:18-132` defines operating boundaries, generation
	order, lifecycle policy, and seed procedure
* `docs/design/data-observatory-model.md:400-449` records the only local timing sample and
	pending cost acceptance
* `docs/prds/claracle-data-observatory-relaunch.md:121-176,260-278` defines FR-004,
	FR-020-022, NFR-009, rollout flags, and Q-01
* `docs/review/data-observatory-relaunch/security-review.md:140-169` records open security
	findings and pending sign-offs
* `.copilot-tracking/plans/logs/2026-08-02/claracle-relaunch-readiness-reconciliation-log.md:10-18,64-74`
	records these workstreams as separate follow-on plans
* Git commits `0baae6d`, `f9a17c8`, and `879c42c` establish generated-page, dynamic-topic,
	and rollout-freeze provenance

## Recommended Next Research

* [ ] Inspect authenticated retained `production-quality-reports` artifacts from at least
	three comparable successful runs; repository source cannot supply their raw values
* [ ] Confirm whether upstream crawl payloads can begin persisting `id`/`node_id`, archive,
	disabled, and rename evidence before repository activation
* [ ] Have editorial/security owners disposition the five currently eligible topic
	candidates and nominate an exact canary
* [ ] Obtain the named owner and approved method for the Hugo/Pagefind regression budget

## Clarifying Questions

* Will missing stable GitHub IDs block `repo_pages` activation, or will the sponsor accept
	fallback name identity for the first activation window?
* Which eligible dynamic topic, if any, is approved as the first canary?
* Who gives final approval for separate Hugo and Pagefind budgets after the timing series?
