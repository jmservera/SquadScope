# Pipeline Validation Checklist

This checklist validates the automated weekly workflow in `.github/workflows/crawl-and-publish.yml`.

## Trigger and scheduling

- [x] `schedule` is enabled in the workflow.
- [x] Cron is `53 11 * * 0`, which targets Sundays at 11:53 UTC.
- [x] The documented expectation is **best effort**: GitHub-hosted scheduled workflows can start late on shared runners, so validation checks the configured cron plus the mitigation path instead of assuming an exact start minute.
- [x] `workflow_dispatch` is enabled for manual runs from the Actions tab or `gh workflow run crawl-and-publish.yml`.
- [x] `concurrency.group` is `weekly-crawl` with `cancel-in-progress: false`, so a second run waits instead of overlapping the active run.

## Secrets and tokens

Required secrets/tokens:

- `COPILOT_GH_TOKEN` — fine-grained PAT used as `COPILOT_GITHUB_TOKEN` for Copilot CLI analysis.
- `GITHUB_TOKEN` — built-in workflow token used for crawling, artifact downloads, commits, token-renewal issue creation, and Pages deployment.
- Optional Podcaster handoff: Actions variable `PODCASTER_ENDPOINT` and Actions secret `PODCASTER_API_KEY`.

## Stage-by-stage validation

### 1. Crawl

**Job:** `crawl`

**Inputs**
- GitHub API access via `GITHUB_TOKEN`
- Restored `crawl-cache` artifact from the latest successful workflow run when available

**Outputs**
- `data/raw/YYYY-WNN.json`
- `data/raw/YYYY-WNN-external-news.json`
- `data/snapshots/YYYY-WNN-stars.json`
- `raw-data` artifact
- `crawl-snapshots` artifact
- `crawl-cache` artifact
- Commit to `main` for `data/raw/` and `data/snapshots/`

**Success criteria**
- Raw payload passes `scripts.crawl.validate_payload()`
- External RSS payload is written for the same ISO week from `config/external_news_sources.json`
- `data/raw/YYYY-WNN-external-news.json` uses canonical `schema_version: 2`, includes `crawl_window`, `source_config_checksum`, `sources_requested/succeeded/failed`, per-source status rows, `dedupe_count`, and `artifact_checksum`
- Optional per-source RSS failures are warnings with a valid partial artifact; malformed config/schema/checksum errors fail the crawl step
- Snapshot file is written for the same ISO week
- Cache artifact uploads even on partial failures
- Job permissions include `actions: read` and `contents: write` at workflow level for cache restore and commits

### 2. Analyze

**Job:** `analyze`

**Inputs**
- `raw-data` artifact downloaded into `data/raw/`
- `COPILOT_GH_TOKEN` for Copilot CLI primary path
- `GITHUB_TOKEN` for diagnostics, commits, and Copilot-token renewal issue creation

**Outputs**
- `data/analyzed/YYYY-WNN-summary.md`
- `data/analyzed/YYYY-WNN-correlations.json`
- `data/analyzed/YYYY-WNN-press-context.md`
- `analyzed-data` artifact
- Commit to `main` for `data/analyzed/`
- Job outputs: `week`, `summary_file`, `current_datetime`

**Success criteria**
- Current raw file week matches the run week
- Correlation and press-context steps consume compact external-news data with legacy `YYYY-WNN-techcrunch.json` fallback
- Press context preserves source names, article URLs/titles/dates, strong-vs-weak labels, and partial-source caveats while staying under the ~8k token budget
- Analysis preflight writes `analysis-preflight.json` with deterministic prompt component byte/token/checksum metadata and raw/prompt evidence inventories before Copilot is invoked.
- Copilot CLI output is staged under `data/candidates/YYYY-WNN/<run-id>/`; if Copilot cannot produce publishable analysis, a no-AI candidate is kept as a rejected artifact and the run fails closed before promotion.
- `scripts/analysis_gate.py` passes before publish continues, rejects repo links outside the current raw evidence inventory where available, and emits structured failure summaries for deterministic retry/preserve decisions.
- `scripts/publish_manifest.py` records promote-vs-preserve decisions against any existing good published summary.
- Job permissions include `actions: read`, `contents: write`, and `issues: write`

### 3. Generate

**Job:** `generate`

**Inputs**
- `analyzed-data` artifact downloaded into `data/analyzed/`
- `needs.analyze.outputs.summary_file`

**Outputs**
- `content/weekly/YYYY/WNN.md`
- `generated-content` artifact
- Commit to `main` for `content/weekly/`
- Job output: `page_path`

**Success criteria**
- `scripts/generate_content.py` converts the weekly summary into Hugo content
- Generated frontmatter keeps publishable fields and drops analysis-only fields like `quality_score`
- Job permissions include `actions: read` and `contents: write`

### 4. Deploy

**Job:** `deploy`

**Inputs**
- Repository checkout with submodules
- `raw-data`, `analyzed-data`, and `generated-content` artifacts restored into the workspace
- Hugo extended `0.161.1`

**Outputs**
- `public/` site build
- GitHub Pages artifact uploaded with `actions/upload-pages-artifact`
- Published Pages deployment via `actions/deploy-pages`

**Success criteria**
- Hugo build succeeds with the pinned version
- Pages artifact is uploaded from `./public`
- Deployment publishes from the same workflow run that generated the content
- Job permissions include `actions: read`, `contents: read`, `pages: write`, and `id-token: write`

## Artifact handoff audit

- `crawl` → `analyze`: `raw-data`
- `crawl` → later runs: `crawl-cache`
- `analyze` → `generate`: `analyzed-data`
- `generate` → `deploy`: `generated-content`
- `generate` + `deploy` → `podcaster-handoff`: normal-mode generated page path plus candidate publish manifest after a successful Pages deploy; Podcaster failures are reported as warnings and do not block or roll back weekly article publication.
- `crawl` and `analyze` also feed `deploy` so the final build uses the same run's data artifacts

## Manual validation flow

### Trigger from GitHub

- Actions tab → **Crawl and publish weekly data** → **Run workflow**
- CLI: `gh workflow run crawl-and-publish.yml`
- External scheduler / automation host: call the same `workflow_dispatch` endpoint or CLI command if punctual timing matters more than GitHub-hosted `schedule` latency

### Trigger locally

- Crawl: `python3 scripts/crawl.py --as-of YYYY-MM-DD`
- External news crawl: `python3 -m scripts.techcrunch_crawler --sources config/external_news_sources.json --output data/raw/YYYY-WNN-external-news.json --since YYYY-MM-DD --until YYYY-MM-DD`
- Correlate press: `python3 -m scripts.correlate --raw data/raw/YYYY-WNN.json --techcrunch data/raw/YYYY-WNN-external-news.json --output data/analyzed/YYYY-WNN-correlations.json`
- Render press context: `python3 -m scripts.render_press_context --week YYYY-WNN`
- Render analysis prompt/diagnostic no-AI output: `python3 scripts/analyze_fallback.py --raw-json data/raw/YYYY-WNN.json --output data/analyzed/YYYY-WNN-summary.md --current-datetime YYYY-MM-DDTHH:MM:SSZ --print-prompt`
- Gate: `python3 scripts/analysis_gate.py --analysis-file data/analyzed/YYYY-WNN-summary.md --raw-json data/raw/YYYY-WNN.json --current-datetime YYYY-MM-DDTHH:MM:SSZ`
- Generate: `python3 scripts/generate_content.py data/analyzed/YYYY-WNN-summary.md`
- Deploy build check: `hugo --minify`

## Known limitations and workarounds

- Copilot CLI in CI depends on `COPILOT_GH_TOKEN`; when token/auth fails, the workflow fails immediately and creates or updates an issue assigned to `@jmservera` to renew the token. There is no GitHub Models/OpenAI fallback for weekly analysis.
- Weekly momentum quality is only as good as the historical star snapshots; first runs and sparse history can make `stars_gained` incomplete.
- Hugo must be `0.146.0+`; the workflow pins `0.161.1` because older runner binaries fail with the current theme.
- The scheduled workflow now deploys Pages directly. `deploy-site.yml` skips bot-authored pushes so the scheduled run does not trigger a duplicate Pages deployment.
- GitHub-hosted `schedule` is best-effort. This repo has observed multi-hour delays on scheduled starts, so the supported mitigation path is manual `gh workflow run`, then external scheduler -> `workflow_dispatch`, with self-hosted runners reserved as optional future work.
