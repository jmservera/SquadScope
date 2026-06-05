# Pipeline Validation Checklist

This checklist validates the automated weekly workflow in `.github/workflows/crawl-and-publish.yml`.

## Trigger and scheduling

- [x] `schedule` is enabled in the workflow.
- [x] Cron is `0 8 * * 1`, which runs every Monday at 08:00 UTC.
- [x] `workflow_dispatch` is enabled for manual runs from the Actions tab or `gh workflow run crawl-and-publish.yml`.
- [x] `concurrency.group` is `weekly-crawl` with `cancel-in-progress: false`, so a second run waits instead of overlapping the active run.

## Secrets and tokens

Required secrets/tokens:

- `COPILOT_GH_TOKEN` — fine-grained PAT used as `COPILOT_GITHUB_TOKEN` for Copilot CLI analysis.
- `GITHUB_TOKEN` — built-in workflow token used for crawling, artifact downloads, commits, fallback GitHub Models calls, and Pages deployment.

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
- Snapshot file is written for the same ISO week
- Cache artifact uploads even on partial failures
- Job permissions include `actions: read` and `contents: write` at workflow level for cache restore and commits

### 2. Analyze

**Job:** `analyze`

**Inputs**
- `raw-data` artifact downloaded into `data/raw/`
- `COPILOT_GH_TOKEN` for Copilot CLI primary path
- `GITHUB_TOKEN` for GitHub Models fallback

**Outputs**
- `data/analyzed/YYYY-WNN-summary.md`
- `analyzed-data` artifact
- Commit to `main` for `data/analyzed/`
- Job outputs: `week`, `summary_file`, `current_datetime`

**Success criteria**
- Current raw file week matches the run week
- Copilot CLI output or fallback output is written to `data/analyzed/`
- `scripts/analysis_gate.py` passes before publish continues
- Job permissions include `actions: read`, `contents: write`, `copilot-requests: write`, and `models: read`

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
- `crawl` and `analyze` also feed `deploy` so the final build uses the same run's data artifacts

## Manual validation flow

### Trigger from GitHub

- Actions tab → **Crawl and publish weekly data** → **Run workflow**
- CLI: `gh workflow run crawl-and-publish.yml`

### Trigger locally

- Crawl: `python3 scripts/crawl.py --as-of YYYY-MM-DD`
- External news crawl: `python3 scripts/techcrunch_crawler.py --sources config/external_news_sources.json --output data/raw/YYYY-WNN-external-news.json --since YYYY-MM-DD --until YYYY-MM-DD`
- Analyze fallback: `python3 scripts/analyze_fallback.py --raw-json data/raw/YYYY-WNN.json --output data/analyzed/YYYY-WNN-summary.md --current-datetime YYYY-MM-DDTHH:MM:SSZ`
- Gate: `python3 scripts/analysis_gate.py --analysis-file data/analyzed/YYYY-WNN-summary.md --raw-json data/raw/YYYY-WNN.json --current-datetime YYYY-MM-DDTHH:MM:SSZ`
- Generate: `python3 scripts/generate_content.py data/analyzed/YYYY-WNN-summary.md`
- Deploy build check: `hugo --minify`

## Known limitations and workarounds

- Copilot CLI in CI depends on `COPILOT_GH_TOKEN`; when unavailable, the workflow falls back to GitHub Models automatically.
- Weekly momentum quality is only as good as the historical star snapshots; first runs and sparse history can make `stars_gained` incomplete.
- Hugo must be `0.146.0+`; the workflow pins `0.161.1` because older runner binaries fail with the current theme.
- The scheduled workflow now deploys Pages directly. `deploy-site.yml` skips bot-authored pushes so the scheduled run does not trigger a duplicate Pages deployment.
