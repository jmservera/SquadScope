<!-- markdownlint-disable-file -->
# Pending Plan Items Research — 2026-08-07

Research target: /home/jmservera/source/SquadScope (SquadScope / Claracle)

## Research Topics and Questions

1. Dynamic topic creation `--dry-run` behavior: parsing, mutations, `--check`, config keys, currently eligible candidates, tests.
2. Cost experiment tooling: invocation, arguments, local runnability.
3. Quality gate commands in `.github/workflows/ci.yml` and local tool availability.
4. Phase 7 delivered state: which gates are closed, human-blocked, or repo-work-blocked.
5. PRD/BRD reconciliation state for NFR-011, NFR-012, R-08, Q-03, versions.

## Status

**Complete** for all five areas. Follow-on items and clarifying questions are recorded at the end.

---

## 1. Dynamic Topic Creation `--dry-run`

### 1.1 Key finding: the plan item is already delivered

The plan item at `.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md` line 71 reads:

> `* [ ] Change --dry-run from an early exit into a non-mutating proposed-change report, or add an equivalent preview command`

This is **stale**. The work landed in commit `e3a00a6` — `feat(topic-hubs): change --dry-run into a non-mutating proposed-change report (Phase 3) (#670)`. The checkbox in the plan file was never ticked.

Prior history on the file: `879c42c` (#623), `f9a17c8` (#616).

### 1.2 Where `--dry-run` is parsed and what it does today

Script: `scripts/manage_topic_hubs.py`

| Item | Location |
| --- | --- |
| `parse_args()` | lines 572-579 |
| `parser.add_argument("--dry-run", action="store_true")` | line 578 |
| `main()` passes `dry_run=args.dry_run` | lines 582-591 (`dry_run=args.dry_run` at line 587) |
| `create_dynamic_hubs(..., dry_run: bool = False)` signature | lines 483-489 (`dry_run` param at line 488) |
| Dry-run branch inside `create_dynamic_hubs` | lines 492-498 |
| `preview_dynamic_hubs()` | lines 422-481 |

Current dry-run behavior (lines 492-498):

* Calls `preview_dynamic_hubs(root=..., config_path=..., current_date=...)`.
* Prints `json.dumps({"schema_version": 1, "candidates": report}, indent=2, sort_keys=True)` to stdout.
* Returns `[]` (so `main()` prints no created paths).
* Deliberately runs **before** the `if not config.enabled:` guard (line 499), so the preview works while `dynamic_creation.enabled = false`. The inline comment at lines 493-495 documents this as the reviewer workflow before flipping the flag.

`preview_dynamic_hubs()` output schema, one entry per candidate (lines 445-480):

```text
slug, title, evidence_weeks, supporting_sources, weekly_issue_count,
action ("promote" | "skip"), skip_reason, proposed_hub_path,
proposed_weekly_assignments, registry_effect
```

`registry_effect` is `"promote-existing-term"` when the slug already exists in `data/taxonomy/topics.json` `terms`, else `"create-new-term"` (lines 476-478). A malformed registry (`terms` not a mapping) falls back to `{}` rather than crashing (lines 434-439).

Skip reasons mirror `create_dynamic_hubs` exactly:

* `existing-or-ignored` — slug in `existing_hub_keys(content/)` or in `config.ignore_topics` (line 462).
* `missing-supporting-evidence` — `not signal.eligible or not signal.supporting_signals` (line 464).
* `below-threshold` — `weekly_count < min_weekly_issues` or `not candidate_is_recent(...)` (lines 465-467).

### 1.3 Every mutation the non-dry-run path performs

`create_dynamic_hubs()` (lines 483-570), reached only when `config.enabled` is true:

| # | Mutation | Function | Lines |
| --- | --- | --- | --- |
| 1 | Creates the log directory and appends a `dynamic-topic-check ...` line | `append_log` | 416-420 (called at 505-510) |
| 2 | `mkdir -p content/topics/<slug>/` | inline `target.parent.mkdir` | 528 |
| 3 | Writes `content/topics/<slug>/_index.md` with YAML frontmatter + body | `render_hub` (210-245); write at 529 | 210-245, 529 |
| 4 | Appends a `create topic=... slug=...` log line | `append_log` | 522-527 |
| 5 | Creates/updates the canonical term in `data/taxonomy/topics.json` (`display_name`, `slug`, `first_seen`, `last_used`, `count`, `times_used`, `weekly_issue_count`, `is_hub: true`, `promoted: true`, `aliases`) and rewrites the file | `add_topic_to_registry` | 258-282 (called at 530) |
| 6 | Rewrites the `topics:` frontmatter line of every evidenced `content/weekly/<year>/W<nn>.md`, inserting the title; inserts a new `topics:` line after `categories:` when absent | `assign_topic_to_weeks` | 308-342 (called at 531) |
| 7 | Appends a JSON `promote-topic` event line to the log | `append_log` | 532-546 |
| 8 | Alias-driven backfill: adds promoted canonical topics to weeklies whose tags/headings/raw signals match aliases (reads `content/weekly/**`, `data/analyzed/*-summary.md`, `data/raw/*.json`; writes weekly frontmatter) | `assign_promoted_topics_from_sources` → `assign_topic_to_weeks` | 344-414 (called at 549) |
| 9 | Appends a JSON `assign-promoted-topics` event line to the log | `append_log` | 550-561 |
| 10 | Rewrites the taxonomy registries when anything changed | `update_taxonomy_registries` (`scripts/taxonomy_registry.py`) | called at 563 |
| 11 | Appends a `dynamic-topic-summary created=N skipped=M` log line | `append_log` | 564 |

A separate, currently-unused mutator `promote_topic_in_registry` (lines 247-256) only flips `is_hub`/`promoted` on an existing term.

The log path resolves from config to `data/topic-hubs/dynamic-topic-creation.log`. That directory **does not exist today** (`ls data/topic-hubs/` → no such file or directory), confirming the mutating path has never run in this working tree.

### 1.4 What `--check` does and how it differs

`manage_topic_hubs.py` has **no `--check` flag**. The `--check` in this area belongs to the upstream candidate-discovery script.

`scripts/discover_topic_candidates.py`

| Item | Location |
| --- | --- |
| `parser.add_argument("--check", action="store_true")` | line 346 |
| `update_candidate_registry(..., check: bool = False)` | lines 324-338 |
| `main()` returns 1 with `"Topic candidate registry is stale."` when `--check` and stale | lines 350-370 |

Semantics:

* `discover_topic_candidates.py` (no `--check`): regenerates `data/taxonomy/topic-candidates.json` from evidence and **writes** it if stale.
* `discover_topic_candidates.py --check`: computes the rendered registry, compares with the file on disk, **writes nothing**, exits 1 if stale. It is a freshness/CI-drift gate on the *candidate evidence input*.
* `manage_topic_hubs.py --dry-run`: consumes that already-written candidate registry and reports which candidates *would* be promoted into hubs. It is a preview of the *promotion decision*, not a staleness check.

The same `--check` idiom appears in `scripts/backfill_weekly_topics.py:117`, `scripts/export_observatory_dataset.py:504`, `scripts/export_trend_explorer_data.py:184`, `scripts/generate_data_pages.py:492`, `scripts/observatory_repos.py:1178`.

### 1.5 Config keys and current values

`config/observatory.toml` lines 14-33:

```toml
[topic_hubs]
seed_topics = [
  "AI Coding Agents",
  "MCP Ecosystem",
  "Open-Source LLMs",
  "Developer Tools",
  "AI Agents in Healthcare",
]

[topic_hubs.dynamic_creation]
enabled = false
min_weekly_issues = 4
lookback_days = 62
log_path = "data/topic-hubs/dynamic-topic-creation.log"
ignore_topics = [
  "ai",
  "artificial intelligence",
  "apps",
  "security",
  "startups",
  "the download",
]
```

Loaded by `load_config()` at `scripts/manage_topic_hubs.py` lines 75-90. `min_weekly_issues` and `lookback_days` use `dynamic[...]` (KeyError if missing); `enabled` and `ignore_topics` use `.get()` defaults. `ignore_topics` entries are normalized with `normalized_key()` (slugified), so `"artificial intelligence"` becomes `artificial-intelligence`.

Related, for context: `[repo_pages] enabled = false` (line 2). Both rollout flags are off, which `scripts/build_cost_experiment.py::assert_rollouts_disabled` (lines 92-98) hard-asserts.

### 1.6 Currently eligible candidate topics (from stored data, no pipeline run)

Determined by calling `preview_dynamic_hubs(current_date='2026-08-07')`, a pure read with no writes.

| Metric | Value |
| --- | --- |
| Candidates in `data/taxonomy/topic-candidates.json` | 2,501 |
| `action == "promote"` | **1,051** |
| `skip_reason == "missing-supporting-evidence"` | 1,450 |
| `skip_reason == "existing-or-ignored"` | 0 |
| `skip_reason == "below-threshold"` | 0 |
| Existing hubs (`content/topics/*/`) | 5 (`ai-agents-in-healthcare`, `ai-coding-agents`, `developer-tools`, `mcp-ecosystem`, `open-source-llms`) |
| Terms in `data/taxonomy/topics.json` | 5 (the seed hubs) |
| Registry effect for every promotable candidate | `create-new-term` |
| Proposed weekly assignments per promotable candidate | 4 |

**This is the material risk finding.** Evidence weeks in the candidate registry span only `2026-W29` through `2026-W32` (4 weeks), and `min_weekly_issues = 4`, so any candidate present in all four weeks with at least one supporting signal is eligible. That yields 1,051 proposed hubs, including obvious noise: `agent`, `agents`, `agentic`, `acme`, `acp`, `activejob`, `activerecord`, `ai-tools`, `airtable`, `sass`, `video`, `videos`, `vim`, `vite`, `visualization`, `visual-studio-code`, `vless`, `virtual-reality`. The 6-entry `ignore_topics` list currently filters nothing (0 skips attributed to it).

Sample of the promote set, first 20 alphabetically: `a-stock`, `acme`, `acp`, `activejob`, `activerecord`, `advanced-driver-assistance-systems`, `advanced-paste`, `agent`, `agent-collaboration`, `agent-computer`, `agent-harness`, `agent-orchestration`, `agentic`, `agentic-ai`, `agentic-coding`, `agentic-framework`, `agentic-rag`, `agentic-retrieval`, `agentic-search`, `agentic-workflow`.

`data/candidates/` holds per-week publish-manifest evidence directories (`2026-W23`, `2026-W24`, `2026-W25`, ...); it is **not** the candidate topic registry. The registry consumed by `manage_topic_hubs.py` is `data/taxonomy/topic-candidates.json` (see `load_config` line 87 and `collect_candidates` lines 152-197).

Implication for the plan: the delivered `--dry-run` report is the correct tool, but the *decision* it supports — flipping `enabled = true` — is currently unsafe without raising `min_weekly_issues`, lengthening the evidence window, hardening `ignore_topics`, or requiring a stronger `supporting_signals` bar. SEC-01's recorded condition ("dynamic creation remains disabled until separate canary review and approval") is consistent with this.

### 1.7 Existing tests covering dry-run / preview

`tests/test_topic_hubs.py`:

| Test | Lines | Coverage |
| --- | --- | --- |
| `test_preview_dynamic_hubs_reports_without_mutating_and_works_while_disabled` | 376-472 | Preview works with `enabled = false`; asserts `action`, `proposed_hub_path`, `proposed_weekly_assignments`, `registry_effect`, and each `skip_reason`; snapshots every file before/after and asserts byte equality; asserts `data/topic-hubs/` is never created; then asserts `create_dynamic_hubs(dry_run=True)` returns `[]` and also mutates nothing |
| `test_preview_dynamic_hubs_tolerates_malformed_registry_terms` | 475-517 | `terms` as a list does not crash the preview; still reports `create-new-term` |

Note: `tests/test_topic_hubs.py` is **excluded** from the fast `python` CI job (`--ignore=tests/test_topic_hubs.py`, `.github/workflows/ci.yml` line ~49) and instead runs in the `production-site` job under "Run rendered SEO and link contracts" (`.github/workflows/ci.yml` lines 221-227).

---

## 2. Cost Experiment Tooling

### 2.1 Script

`scripts/build_cost_experiment.py` — "Run an isolated, report-only Hugo and Pagefind build-cost experiment."

| Item | Location |
| --- | --- |
| `create_parser()` | lines 555-570 |
| `run_experiment()` | lines 479-553 |
| `main()` | lines 573-582 |
| `assert_rollouts_disabled()` | lines 92-98 |
| `discover_workload()` | lines 128-157 |
| `materialize_variant()` | lines 177-205 |
| `build_sample()` | lines 236-316 |
| `aggregate_samples()` | lines 327-416 |
| `render_summary_markdown()` | lines 418-457 |
| `write_checksums()` | lines 459-470 |

All twelve CLI arguments are `required=True` (lines 558-569):

`--source` (Path), `--reports` (Path), `--repetitions` (int, `choices=(3, 5)`), `--main-sha`, `--publish-sha`, `--workflow-sha`, `--run-id`, `--run-attempt` (int), `--runner-os`, `--runner-arch`, `--image-os`, `--image-version`.

Design constants (lines 23-63):

* `EXPECTED_CLASS_COUNTS = {"topic_hubs": 5, "data_pages": 3, "repository_pages": 263}`
* `CLASS_PATTERNS = {"topic_hubs": "content/topics/*/_index.md", "data_pages": "content/data/*/index.md", "repository_pages": "content/repo/*/index.md"}`
* `VARIANTS`: cumulative `baseline` (0) → `topic_hubs` (+5) → `data_pages` (+3) → `repository_pages` (+263)
* `COPY_EXCLUDES`: `.copilot-tracking`, `.git`, `.venv`, `node_modules`, `public`, `reports`, `resources`, `screenshots`, `venv`

Each sample runs `hugo --minify --cleanDestinationDir --destination public` then `npx --no-install pagefind --site public/` (lines 254-267, 274-276), timed with `time.monotonic_ns()`.

### 2.2 Workflow

`.github/workflows/build-cost-experiment.yml` — "Hugo and Pagefind build-cost experiment".

* Trigger: `workflow_dispatch` only (line 4). No push, schedule, or PR trigger.
* Inputs: `reviewed_main_sha` (required string), `reviewed_publish_sha` (required string), `repetitions` (required choice `'3'` or `'5'`, default `'5'`).
* Gate: `if: ${{ github.ref == 'refs/heads/main' }}` (line 32); `permissions: contents: read`; concurrency group `hugo-pagefind-build-cost-experiment` with `cancel-in-progress: false`.
* Env pins: `HUGO_VERSION: 0.161.1`, `PAGEFIND_VERSION: 1.5.2`, `BLOCKING_THRESHOLD_MS: 'null'`.
* Steps: checkout at `reviewed_main_sha` (`fetch-depth: 0`, `submodules: recursive`) → SHA admission (40-lowercase-hex regex, `reviewed_main_sha == github.sha`, `reviewed_publish_sha` reachable from `origin/publish`) → hydrate generated paths from the publish commit via `python3 -m scripts.publish_hydration paths` plus `git checkout <publish_sha> -- <path>` → `python3 -m scripts.publish_hydration check` plus an inline `assert_rollouts_disabled(Path.cwd())` → Node 24 → Python 3.12 → checksum-verified Hugo tarball → `npm install --global --prefix "${RUNNER_TEMP}/pagefind" "pagefind@1.5.2"` → the experiment run → job summary → artifact upload (`reports/build-cost-experiment/`, 90-day retention).

Invocation (workflow lines 143-157):

```bash
python3 -m scripts.build_cost_experiment \
  --source . \
  --reports reports/build-cost-experiment \
  --repetitions "${REPETITIONS}" \
  --main-sha "${REVIEWED_MAIN_SHA}" \
  --publish-sha "${REVIEWED_PUBLISH_SHA}" \
  --workflow-sha "${WORKFLOW_SHA}" \
  --run-id "${RUN_ID}" \
  --run-attempt "${RUN_ATTEMPT}" \
  --runner-os "${RUNNER_OS}" \
  --runner-arch "${RUNNER_ARCH}" \
  --image-os "${ImageOS:-ubuntu24}" \
  --image-version "${ImageVersion:-unknown}"
```

### 2.3 Can it run locally without dispatching the workflow?

**Mechanically yes, but not usefully — it fails on the current tree, and the output would not be admissible evidence.**

Blockers, in the order they bite:

1. **Workload count mismatch (hard failure).** `discover_workload()` enforces `EXPECTED_CLASS_COUNTS` (lines 150-154) and raises `ExperimentError` otherwise. Current working tree:

   | Class | Pattern | Local count | Expected |
   | --- | --- | --- | --- |
   | `topic_hubs` | `content/topics/*/_index.md` | 5 | 5 (match) |
   | `data_pages` | `content/data/*/index.md` | 3 | 3 (match) |
   | `repository_pages` | `content/repo/*/index.md` | **266** | 263 (**mismatch**) |

   The counts are calibrated against the hydrated publish corpus at the reviewed SHAs, not against an arbitrary `main` checkout. `enforce_expected_counts=False` exists as a kwarg (lines 128-130, 177-181) but is not exposed on the CLI.

2. **Pagefind is not installed locally.** `npx --no-install pagefind --version` fails with `npx canceled due to missing packages`. Needs `npm install pagefind@1.5.2` (network).

3. **Hugo version mismatch.** Local `hugo v0.146.0+extended`; the experiment pins `0.161.1`. Timings across versions are not comparable.

4. **Provenance arguments.** `--main-sha`, `--publish-sha`, and `--workflow-sha` must each be 40 lowercase hex (`validate_sha`, lines 85-90); `--run-id` and `--run-attempt` are free-form but would carry no real Actions provenance.

5. **Reports directory must not pre-exist** (`run_experiment`, lines 482-484).

6. **Runtime.** 3 or 5 repetitions times 4 variants equals 12 or 20 full `copytree` plus Hugo plus Pagefind cycles.

The workflow's own value is the immutability guarantee (exact reviewed SHAs, publish-hydrated corpus, pinned tools, retained checksummed artifacts), which is precisely what a local run cannot provide. `assert_rollouts_disabled()` currently passes locally because both flags are `false`. Local verification of the *logic* is done through the unit tests, not the CLI.

---

## 3. Quality Gate Commands (`.github/workflows/ci.yml`)

Three jobs: `python`, `publish-hydration-parity`, `production-site`. No `working-directory:` key appears anywhere; every step runs at the repository root.

### 3.1 `production-site` job env (lines 105-112)

```yaml
HUGO_VERSION: 0.161.1
PAGEFIND_VERSION: 1.5.2
PLAYWRIGHT_VERSION: 1.54.2
AXE_PLAYWRIGHT_VERSION: 4.10.2
LIGHTHOUSE_VERSION: 12.8.2
BASE_URL: http://127.0.0.1:1313
HUGO_PARAMS_GA_MEASUREMENT_ID: G-TEST-OBSERVATORY
```

Node is `actions/setup-node` v6.4.0 with `node-version: '24'`; Python is `actions/setup-python` v6.2.0 with `3.12`.

### 3.2 Gate commands

| Gate | CI step (line) | Command | Needs |
| --- | --- | --- | --- |
| Dependency install | 178-186 | `python -m pip install --upgrade pytest -r requirements.txt`; then `npm install --no-save --no-package-lock "@playwright/test@1.54.2" "@axe-core/playwright@4.10.2" "lighthouse@12.8.2"`; then `npx --no-install playwright install --with-deps chromium` | Node plus network |
| Embed source validation | 188-189 | `python scripts/check_embed_sources.py` | Python |
| **Hugo build with timing** | 191-198 | `started_at="$(date +%s%N)"; hugo --minify --baseURL "${BASE_URL}/"; finished_at="$(date +%s%N)"; echo "duration_ms=$(( (finished_at - started_at) / 1000000 ))" >> "${GITHUB_OUTPUT}"` (step id `hugo-build`) | Hugo 0.161.1 |
| **Pagefind with timing** | 200-207 | `started_at="$(date +%s%N)"; npx "pagefind@${PAGEFIND_VERSION}" --site public/; finished_at="$(date +%s%N)"; echo "duration_ms=..." >> "${GITHUB_OUTPUT}"` (step id `pagefind-build`); note this is `npx pagefind@1.5.2` **without** `--no-install` | Node plus network |
| Build-timing report | 209-219 | `mkdir -p reports` plus `printf ... > reports/build-timing.json`; env `COMMIT_SHA`, `HUGO_DURATION_MS`, `PAGEFIND_DURATION_MS`; emits `"mode": "report-only"` and `"blocking_threshold_ms": null` | — |
| **Rendered metadata checks** | 221-227 | `python -m pytest tests/test_rendered_seo_metadata.py tests/test_rendered_weekly_links.py tests/test_internal_link_checker.py tests/test_topic_hubs.py` | Built `public/` |
| **Internal link check** | 229-230 | `python scripts/check_internal_links.py public --base-url "https://claracle.com/"` | Built `public/` |
| Serve production build | 232-237 | `python scripts/serve_static.py --directory public --bind 127.0.0.1 --port 1313 > reports/site-server.log 2>&1 &`; `echo $! > reports/site-server.pid`; `curl --fail --silent --show-error --retry 30 --retry-delay 1 --retry-connrefused "${BASE_URL}/"` | — |
| **axe accessibility and responsive** | 239-240 | `npx --no-install playwright test --config tests/visual/playwright.config.mjs tests/visual/a11y-perf.spec.mjs tests/visual/observatory-a11y.spec.mjs tests/visual/observatory-analytics.spec.mjs` | Playwright, Chromium, running server |
| **Lighthouse** | 242-243 | `node scripts/design/lighthouse-gates.mjs --base "${BASE_URL}"` | Lighthouse 12.8.2, Chrome, running server |
| **Visual evidence capture** | 251-256 | `npx --no-install playwright test --config tests/visual/playwright.config.mjs tests/visual/observatory-visual-regression.spec.mjs`; `if: ${{ !cancelled() }}`; env `PLAYWRIGHT_REPORT_SUFFIX: -visual` | Playwright, Chromium, running server |
| Visual evidence index | 258-260 | `python scripts/design/build_visual_evidence_index.py`; `if: ${{ !cancelled() }}` | Python |
| Artifact upload | 262-274 | `actions/upload-artifact` v7.0.1, name `production-quality-reports`, 30-day retention; paths `reports/build-timing.json`, `reports/site-server.log`, `screenshots/lighthouse-results/`, `screenshots/playwright-output*/`, `screenshots/playwright-report*.json`, `screenshots/playwright-report*/`, `screenshots/visual-regression/` | — |

Ordering matters and is documented in the workflow (comment at lines 244-250): the visual capture runs **last** so evidence collection never perturbs the earlier gates and so Lighthouse gets an unloaded runner; it runs under `!cancelled()` so evidence survives an earlier gate failure.

`python` job (lines 19-56): `python -m pip_audit -r requirements.txt`; `python -m pytest --ignore=tests/test_rendered_seo_metadata.py --ignore=tests/test_rendered_weekly_links.py --ignore=tests/test_internal_link_checker.py --ignore=tests/test_topic_hubs.py`; `python scripts/manage_image_registry.py validate`; `python scripts/validate_content_images.py`. Also `node --test tests/*.test.mjs` in `production-site` (lines 170-171).

`publish-hydration-parity` job (lines 58-100): reproduces deploy hydration via `python3 -m scripts.publish_hydration paths`, then `python3 -m scripts.publish_hydration check`, labelled "Validate hydrated references (NFR-011 / NFR-012)".

### 3.3 Local tool availability (verified 2026-08-07)

| Tool | Local state | CI expectation | Verdict |
| --- | --- | --- | --- |
| `package.json` / `package-lock.json` | **Absent**; CI installs Node deps ad hoc with `npm install --no-save --no-package-lock` (the zizmor `adhoc-packages` ignore comment at line 179 states "the plan excludes adding a Node manifest") | none | matches CI |
| `node_modules/` | Present and untracked; contains `@playwright`, `@axe-core`, `axe-core`, `chrome-launcher`, `csp_evaluator`, `@puppeteer` | installed per run | OK |
| `node` | v22.22.3 (nvm) | 24 | **mismatch** |
| `npx playwright` | **1.54.2** (matches `PLAYWRIGHT_VERSION`) | 1.54.2 | OK |
| Playwright browsers | `~/.cache/ms-playwright`: `chromium-1181`, `chromium_headless_shell-1181`, `ffmpeg-1011` | chromium | OK |
| `npx lighthouse` | **12.8.2** (matches `LIGHTHOUSE_VERSION`) | 12.8.2 | OK |
| `npx pagefind` | **Not installed**; `npx --no-install pagefind` fails with `npx canceled due to missing packages` | 1.5.2 | **needs `npm install pagefind@1.5.2`** |
| `hugo` | `/usr/local/bin/hugo` v0.146.0+extended | 0.161.1 | **mismatch** |
| `python3` | `/usr/bin/python3` | 3.12 | confirm minor version before relying on it |
| `tests/visual/` specs | All present: `a11y-perf.spec.mjs`, `observatory-a11y.spec.mjs`, `observatory-analytics.spec.mjs`, `observatory-visual-regression.spec.mjs`, `visual.spec.mjs`, `playwright.config.mjs` | — | OK |

Summary for local reproduction:

* **Runnable now:** pytest suites, `check_embed_sources.py`, `check_internal_links.py`, `serve_static.py`, `build_visual_evidence_index.py`, the axe/analytics/visual Playwright specs, and the Lighthouse gate.
* **Blocked without a network install:** the Pagefind index step (`npm install pagefind@1.5.2`).
* **Not version-faithful:** Hugo (0.146.0 versus 0.161.1) and Node (22 versus 24). Any locally captured timing figure is therefore **not** admissible against the Phase 7.1 baseline, which is explicitly recorded as Hugo 0.161.1 and Pagefind 1.5.2 on `ubuntu-latest`.

`visual-review-handoff-2026-08-07.md` independently states the same constraint: local capture is a *fallback for a CI outage*, and final acceptance should cite a `main` run.

---

## 4. Phase 7 Delivered State

Sources read: `docs/review/data-observatory-relaunch/status-of-record.md`, `timing-analysis.md`, `visual-review-handoff-2026-08-07.md`, `security-sign-off-checklist.md`.

Header state of `status-of-record.md`: reconciled through 2026-08-06; release acceptance **pending**; both rollout flags stay disabled; tracking PR #677; `ms.date: 2026-08-06`.

### (a) Delivered or closed — no further work

| Gate | Evidence |
| --- | --- |
| **Phase 7.2 Security / NFR-004 — fully closed** | All 10 findings SEC-01 through SEC-10 have dated dispositions (SEC-01 to SEC-05 and SEC-09 on 2026-08-04; SEC-06, SEC-07, SEC-08, SEC-10 on 2026-08-06). SEC-05 and SEC-09 are *Accepted-with-Conditions* with conditions enforced as process and workflow controls. jmservera sponsor acceptance recorded 2026-08-06. All acceptance-criteria checkboxes in `security-sign-off-checklist.md` are `[x]`. |
| Phase 7.1 timing **data collection** | Three comparable production `main` runs transcribed from retained artifacts: `31039618366` (Hugo 2,822 / Pagefind 2,707), `31079871801` (2,456 / 2,255), `31081291997` (3,058 / 2,316). Median and p95 computed: Hugo 2,822 / 3,058; Pagefind 2,316 / 2,707. Three `[x]` items in the timing "Pending Deliverables" list. |
| Phase 7.3 **capture automation** | Visual suite resolves its route matrix from the built `sitemap.xml`; gate and evidence capture wired into `ci.yml`; run `31160859598` confirmed 64 screenshots plus `index.html`; 15 routes plus a consent capture times 4 projects (desktop/mobile by light/dark); per-project `metadata.json` tagged with revision, branch, run ID, viewport, Playwright version. |
| Atomic publish transaction | Run `31040602642` at `211f0974ce375e427591803cc3f3dfd39e169ead`. |
| Deploy/hydration parity plus CI guard (NFR-011/012) | `#628`, `#632`, `#634`, `#637`, `#641`; `publish-hydration-parity` CI job. |
| Podcaster release smoke and real downstream run (NFR-002 / R-04) | `#636`, `#639`, `#643`, `#645`, `#646`; protected run `30908778884`, downstream job `podcast-2026-W32-d07bb05dc073`, response `accepted`. |
| `#644`, `#626`, `#622`, `#599` | All CLOSED. |

### (b) Pending on a human owner only — **no repository work required**

Blocked purely by a signature or decision. Every artifact the decision needs already exists in the repo.

| Item | Owner | What is missing | Where it gets recorded |
| --- | --- | --- | --- |
| **Timing budget threshold approval (p95)** | timing-budget owner | Accept or adjust Hugo <= 6,000 ms, Pagefind <= 5,500 ms, Total <= 11,500 ms; confirm 3 samples suffice; confirm the report-only posture holds | `timing-analysis.md` "Approval Chain" plus status-of-record 7.1 row |
| **Infrastructure owner (URL) timing sign-off** | URL | Validate collection methodology and artifact durability | `timing-analysis.md` |
| **Production owner (jmservera) timing acceptance** | jmservera | Confirm enforcement mechanism and rollback plan | `timing-analysis.md` |
| **Visual evidence compilation and approval** | Amy, Fry | Named review of the already-produced matrix; disposition table rows read `Pending` with empty Date | `visual-review-handoff-2026-08-07.md` Disposition table plus status-of-record 7.3 rows |

The prior provisional timing approval is explicitly **withdrawn** because it relied on an incorrect Run 1 baseline (Hugo 15,339 / Pagefind 1,631 ms) and a non-comparable `pull_request` Run 2. Both errors are already corrected in the document; no further code or data work is needed to re-enable the decision.

### (c) Pending on executable repository work

| Item | What still needs producing | Notes |
| --- | --- | --- |
| **Timing enforcement gate activation** | Edit `.github/workflows/ci.yml` to fail on exceeded budgets and set `blocking_threshold_ms` in `reports/build-timing.json` | Last unchecked box in `timing-analysis.md` "Pending Deliverables"; **sequenced after** the human approval, so it is not currently actionable |
| **Manual interaction-state visual captures** | Tool filter combinations, expanded lifecycle or provenance detail, copy actions, visible keyboard focus on the internal-link block | `visual-review-handoff-2026-08-07.md` states these "remain a manual reviewer step and must be recorded separately before the gate closes"; human execution, but produces new artifacts |
| **Incremental generation cost (Q-01 / NFR-009)** | Dispatch `build-cost-experiment.yml` with reviewed SHAs; retain the 3/5-run artifacts; obtain the budget-owner conclusion | Tooling implemented; artifacts not yet produced (status-of-record: "Partial") |
| **GA4/GSC dated baseline transcription and production consent evidence (FR-035 / NFR-007 / NFR-008)** | Transcribe the supplied export into `docs/growth/ga4-gsc-baseline-2026-07-29.md`; retain production consent observations | Connection itself is complete; deferred to a separate plan |
| **External metadata and feed validation** | Social preview debuggers, Rich Results, Schema.org, named reviewer conclusions | Production feed and source-level metadata evidence already retained |
| **FR-041 standalone CI link tool** | status-of-record says "no standalone CI link tool" | `.github/workflows/ci.yml` line 230 already runs `scripts/check_internal_links.py`, so this row may itself be stale; see clarifying questions |
| **Accessibility evidence (NFR-005)** | Amy and Fry, production browser plus assistive technology | Distinct from the automated axe gate |
| **`dynamic_topic_creation` canary** | One approved canary before activation | See section 1.6; the current candidate set makes a naive canary unsafe |
| **`repo_pages` activation transaction** | Sponsor-approved; flag remains `false` and needs a separate activation change | Approved after PR #668 evidence |

**Critical path per status-of-record:** timing-budget owner approval and named visual review, that is, "gated on human sign-off rather than on further automation".

---

## 5. PRD and BRD Reconciliation State

### 5.1 PRD — `docs/prds/claracle-data-observatory-relaunch.md`

Frontmatter `ms.date: 2026-08-05` (line 5). Header line 10:

> `Version 1.4 | Status Acceptance pending | Owner jmservera | Team SquadScope Squad | Target Wave 1 (foundation) | Lifecycle Definition`

| ID | Location | Current text | Reconciliation note |
| --- | --- | --- | --- |
| **NFR-011** | line 184, section 7 table with columns NFR ID / Category / Requirement / Metric-Target / Priority / Validation / Notes and **no Status column** | Reliability; "Deploy and CI build the same hydrated content set"; metric "CI reproduces the publish-hydration that deploy performs, so generated-content divergence between `main` and `publish` fails CI rather than the production deploy"; Priority **Must**; Validation "CI deploy-parity build; `test_pipeline.py` provenance invariant"; Notes "Root cause of the 2026-07-31 deploy failure (issue #627)" | No delivered or closed marker exists in the PRD. status-of-record records this as **Done** (`publish-hydration-parity` job plus `scripts/publish_hydration.py`). |
| **NFR-012** | line 185 | Reliability; "Embedded charts never break the site build"; metric "Every `content/embeds/*` `source_page` resolves to an existing data page in the built content set"; Priority **Must**; Validation "Build-time reference check"; Notes "The dangling embed reference aborted the 2026-07-31 deploy" | Same: no status marker. status-of-record records **Done** (`#641` guard, `scripts/check_embed_sources.py`, wired in `ci.yml`). |
| **R-08** | line 232, section 10 Risks table, which does have a Status column | Status: **"Open; interim fix ships `content/data` pages from `main` until the crawl publishes them (issue #627)"** | **Stale.** The interim fix was superseded. Q-03 (line 285) and status-of-record both record hydration restored via `#637` with the `#641` guard preventing recurrence. R-08 should read closed or mitigated. |
| **Q-03** | line 285, section 14 Open Questions | Owner Bender; Deadline "Post-#627 crawl run"; Status: **"Resolved: hydration restored via `#637` after the crawl repopulated `publish`; CI embed-source guard (`#641`) prevents recurrence"** | Already reconciled. Directly contradicts the R-08 status above. |

Changelog head (section 15, line 287 onward), most recent entry:

| Version | Date | Author | Summary | Type |
| --- | --- | --- | --- | --- |
| **1.4** | **2026-08-05** | SquadScope Squad | "Recorded the successful protected Podcaster run, atomic proof, and separate sponsor decisions while preserving open technical and external gates" | Updated |

Prior entries: 1.3 (2026-08-02), 1.2 (2026-07-31), 1.1 (2026-07-30), 1.0 (2026-07-29).

Related context in the same tables:

* Q-01 (line 284) — "Quantify incremental generation cost/time for hubs, data, and repo pages", Owner Leela, Status **Open**. Matches the unproduced cost-experiment artifacts in section 4(c).
* R-03 (line 227) — "Auto-generation breaks internal links ... CI link-check gate (FR-041)", Owner Fry, Status **Open**, despite `ci.yml` line 230 running `scripts/check_internal_links.py`.
* R-05 (line 229) — "Open; sign-off pending", despite NFR-004 being approved on 2026-08-06. **Stale.**
* R-04 (line 228) — already reconciled: "Closed for relaunch evidence; protected run `30908778884` succeeded and downstream returned `accepted`".

### 5.2 BRD — `docs/brds/claracle-data-observatory-relaunch-brd.md`

Frontmatter `ms.date: 2026-08-05` (line 5). Document Control block (lines 11-19):

| Field | Value |
| --- | --- |
| BRD ID | BRD-CLARACLE-002 |
| Status | Acceptance pending; sponsor decisions recorded with conditions |
| **Version** | **1.3** |
| Author | BRD Builder (facilitated) |
| Sponsor | jmservera (also the human approval authority) |
| Last updated | 2026-08-05 |
| Related repositories | SquadScope, SquadScope-Podcaster, SquadScope-Coordinator |

Change History head: **1.3 | 2026-08-05 | SquadScope Squad | "Recorded the protected Podcaster result and separate sponsor decisions while preserving their technical conditions and open acceptance gates"**. Prior: 1.2 (2026-08-02), 1.1 (2026-07-30), 1.0 (2026-07-29).

The BRD Acceptance Status prose still lists "Final security acceptance" among the open gates, which is **stale** as of the 2026-08-06 NFR-004 approval.

### 5.3 Reconciliation gap summary

Both PRD (1.4) and BRD (1.3) are dated **2026-08-05** and therefore predate the 2026-08-06 security approval and the 2026-08-06 and 2026-08-07 timing correction and visual handoff. Concretely stale:

1. PRD R-08 status still reads "Open; interim fix ..." while PRD Q-03 says resolved.
2. PRD R-05 reads "Open; sign-off pending" while NFR-004 is approved (2026-08-06).
3. PRD R-03 and FR-041 framing versus `ci.yml` line 230 already running the standalone link checker.
4. BRD Acceptance Status prose still lists final security acceptance as open.
5. Neither NFR-011 nor NFR-012 carries any delivered marker, because their table has no Status column, so their closure lives only in the status of record.

---

## Key Discoveries

1. **`--dry-run` is already a non-mutating proposed-change report** (`scripts/manage_topic_hubs.py` lines 422-481 and 492-498, commit `e3a00a6` / PR #670), with two dedicated no-mutation tests. The plan checkbox at `.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md` line 71 is stale.
2. **Flipping `dynamic_creation.enabled = true` today would create about 1,051 topic hubs**, mutate `data/taxonomy/topics.json`, and rewrite roughly 4 weekly frontmatter files per hub. The candidate registry spans only 4 evidence weeks against `min_weekly_issues = 4`, so the threshold filters nothing, and the 6-entry `ignore_topics` list produces zero skips.
3. **The cost experiment cannot produce admissible evidence locally**: `EXPECTED_CLASS_COUNTS["repository_pages"] = 263` versus 266 files on the current tree (hard `ExperimentError`), Pagefind absent, Hugo 0.146.0 versus the pinned 0.161.1.
4. **Phase 7 is human-gated, not code-gated.** Security is fully closed. Timing data and visual evidence are both produced. Only the timing-budget approval (three named sign-offs) and the Amy/Fry visual disposition remain, plus the manual interaction-state captures the handoff explicitly carves out.
5. **PRD 1.4 and BRD 1.3 both predate the 2026-08-06 security approval**, leaving R-08, R-05, and the BRD acceptance prose internally inconsistent with Q-03 and the status of record.

## Recommended Next Research (not completed)

- [ ] Read `scripts/taxonomy_registry.py::update_taxonomy_registries` to enumerate exactly which `data/taxonomy/*` files mutation 10 rewrites.
- [ ] Read `tests/visual/playwright.config.mjs` and `scripts/design/lighthouse-gates.mjs` to confirm the exact env vars, thresholds, and output paths each gate expects locally.
- [ ] Determine why `content/repo/*/index.md` is 266 locally versus the experiment's calibrated 263, and whether the constant or the corpus is authoritative.
- [ ] Inspect `docs/review/data-observatory-relaunch/owner-action-register.md` for the named owners and message threads behind the four human sign-offs.
- [ ] Confirm whether `scripts/discover_topic_candidates.py --check` runs anywhere in CI; no match was found in `ci.yml`.

## Clarifying Questions

1. **Dry-run scope.** Since the non-mutating report already exists, is the intended remaining work (a) ticking the plan checkbox and reconciling docs, (b) hardening the eligibility policy so a promotion decision is actually safe, or (c) both? The 1,051-candidate result strongly suggests (b) is the real open item.
2. **FR-041 status.** status-of-record says "no standalone CI link tool", but `.github/workflows/ci.yml` line 230 runs `python scripts/check_internal_links.py public --base-url "https://claracle.com/"`. Should FR-041 and R-03 be reconciled to Done, or is a different capability meant?
3. **Cost-experiment corpus.** Should `EXPECTED_CLASS_COUNTS` be re-derived from the current publish corpus before the next dispatch, or is 263 pinned intentionally to a specific reviewed publish SHA?
4. **PRD and BRD revision.** Should the PRD advance to 1.5 and the BRD to 1.4 to absorb the 2026-08-06 security approval and the 2026-08-06/07 timing and visual corrections, or is the status of record intentionally the only live surface until release acceptance?
5. **Local gate parity.** Is installing Hugo 0.161.1 and `pagefind@1.5.2` locally in scope, or should local verification stay limited to the Python, Playwright, and Lighthouse subset that already matches CI versions?
