[![Crawl and publish weekly data](https://github.com/jmservera/SquadScope/actions/workflows/crawl-and-publish.yml/badge.svg)](https://github.com/jmservera/SquadScope/actions/workflows/crawl-and-publish.yml)
[![Deploy Hugo site](https://github.com/jmservera/SquadScope/actions/workflows/deploy-site.yml/badge.svg)](https://github.com/jmservera/SquadScope/actions/workflows/deploy-site.yml)
# Claracle (SquadScope)

Claracle is an automated AI-powered site that publishes weekly, monthly, and yearly summaries of tech trends sourced from GitHub. The system crawls trending and newly-created repositories, applies AI analysis to identify signal vs. noise, and publishes curated insights with zero manual intervention.

## What is Claracle?

Claracle solves the information overload problem in open-source development. Each week, millions of repositories are created or gain stars. Claracle:

1. **Crawls** GitHub API for new and trending repositories in a given week
2. **Analyzes** the data with Copilot to identify what's genuinely important vs. hype
3. **Generates** human-readable weekly summaries with signal, noise, and gaps analysis
4. **Publishes** to GitHub Pages with RSS feeds for consumption
5. **Reskills** every 5 runs to improve its own analysis quality

Result: Curated tech trend insights delivered automatically every Monday.

## Architecture

Claracle uses a **5-stage pipeline** executed entirely in GitHub Actions:

```
Crawl → Analyze → Generate → Deploy → Reskill
  ↓        ↓          ↓         ↓        ↓
JSON    Markdown   Hugo      Pages    Improvements
```

**Stage 1: Crawl** (`scripts/crawl.py`, `scripts/techcrunch_crawler.py`)
- Queries GitHub API for repos created/trending in the current week
- Fetches configured external RSS feeds from `config/external_news_sources.json` in parallel as an enrichment signal
- Applies heuristic filtering (language, topic, description quality)
- Outputs: `data/raw/YYYY-WNN.json`, `data/raw/YYYY-WNN-external-news.json`, `data/snapshots/YYYY-WNN-stars.json`

**Stage 2: Analyze** (Copilot CLI only)
- Reads raw JSON; applies AI analysis to classify repos as signal/noise/gaps
- Outputs: `data/analyzed/YYYY-WNN-summary.md` with quality score and summary sections
- Quality gate: Blocks publish if quality_score < 60 or missing required sections

**Stage 3: Generate** (`scripts/generate_content.py`)
- Converts analyzed Markdown into Hugo content structure
- Outputs: `content/weekly/YYYY/WNN.md` ready for Hugo build

**Stage 4: Deploy** (Hugo + GitHub Pages)
- Builds static site from Hugo and publishes to GitHub Pages
- Outputs: Live website + RSS feeds at `https://www.claracle.com/index.xml` and `https://www.claracle.com/feed/`

**Stage 5: Reskill** (every 5th run)
- Every 5th run, Copilot reviews squad history and recent analysis outputs
- Writes observations and improvement recommendations to `.squad/reskill/YYYY-WNN.md`
- Optional: Can trigger PR with proposed prompt refinements (not auto-merged)

## Theme and stack

- **Static site generator:** Hugo (extended, v0.146.0+)
- **Theme:** [PaperMod](https://github.com/adityatelange/hugo-PaperMod)
- **Search:** Pagefind (static, client-side)
- **Notifications:** RSS feeds + GitHub Releases
- **Automation:** GitHub Actions
- **Deployment:** GitHub Pages
- **Analysis engine:** Copilot CLI only; no GitHub Models/OpenAI analysis fallback

## Quick start

### For end users

1. **Visit the site:** [Claracle](https://www.claracle.com/): Browse weekly, monthly, yearly summaries
2. **Subscribe to RSS:** Add `https://www.claracle.com/index.xml` or `https://www.claracle.com/feed/` to your reader
3. **Check GitHub Releases:** New summaries also posted as releases

### For operators (see `docs/operator-guide.md` for full setup)

1. Fork this repository
2. Configure `COPILOT_GH_TOKEN` secret in your repo (fine-grained PAT with Copilot Requests permission)
3. Enable GitHub Pages (Actions source)
4. Test manual run: `gh workflow run crawl-and-publish.yml`
5. Monitor the first automated run

⚠️ **First-time operators:** Start with `docs/rollout-checklist.md` to ensure all prerequisites are in place.

## Local development

1. **Install Hugo:** `brew install hugo` (macOS) or download from [hugo releases](https://github.com/gohugoio/hugo/releases) (v0.146.0 or newer)
2. **Clone with submodules:**
   ```bash
   git clone --recurse-submodules https://github.com/jmservera/SquadScope.git
   git submodule update --init --recursive
   ```
3. **Start dev server:** `hugo server` (default: http://localhost:1313)
4. **Create production build:** `hugo --minify` (output: `public/`)

## Content structure

- `content/weekly/YYYY/WNN.md` — immutable weekly summaries (published once, never modified)
- `content/monthly/YYYY/MM.md` — monthly rollups (append-only)
- `content/yearly/YYYY.md` — yearly summaries (append-only)
- `data/raw/YYYY-WNN.json` — GitHub crawler output (JSON object with keys: `week`, `new_repos`, `trending_repos`, `signals`, `metadata`)
- `data/raw/YYYY-WNN-external-news.json` — external RSS enrichment output from sources configured in `config/external_news_sources.json`
- `data/analyzed/YYYY-WNN-summary.md` — AI analysis with quality score
- `data/snapshots/YYYY-WNN-stars.json` — star count snapshots for trending analysis

## Automated weekly pipeline

`.github/workflows/crawl-and-publish.yml` runs the full weekly automation every Monday at 06:53 UTC:

1. **Crawl:** GitHub API → `data/raw/YYYY-WNN.json`; external RSS feeds → `data/raw/YYYY-WNN-external-news.json`
2. **Analyze:** Copilot → `data/analyzed/YYYY-WNN-summary.md`
3. **Quality gate:** Validates quality_score ≥ 60; blocks publish if failed
4. **Generate:** Markdown → `content/weekly/YYYY/WNN.md`
5. **Deploy:** Hugo build → GitHub Pages
6. **Reskill:** Every 5th run, review and improve squad state

### Schedule and manual runs

- **Automated schedule:** Monday 06:53 UTC (`53 6 * * 1`)
- **Manual trigger:** `gh workflow run crawl-and-publish.yml` or GitHub Actions UI

### Required secrets

- `COPILOT_GH_TOKEN` — Fine-grained PAT with **Account → Copilot Requests** permission for Copilot CLI analysis
- `GITHUB_TOKEN` — Built-in; used for crawling, commits, Pages deployment, and issue/notification automation
- `PODCASTER_API_KEY` — Optional; used with the `PODCASTER_ENDPOINT` Actions variable for the post-publish Podcaster handoff. The value must never be logged or committed.

## Crawler notes

- `signals.top_topics` de-duplicates repositories by `full_name` across new and trending buckets
- `data/snapshots/YYYY-WNN-stars.json` preserves the broader pre-filter candidate set for consistent week-over-week `stars_gained` comparisons
- Live runs use open-ended `created:>` / `pushed:>` GitHub search filters
- `--as-of` mode switches to bounded date ranges for deterministic historical backfills

## Deployment

- **Standard deploys:** Direct pushes to `main` trigger `.github/workflows/deploy-site.yml`
- **Weekly automation:** `crawl-and-publish.yml` handles full pipeline and deploys Pages
- **Deduplication:** Deploy workflow skips bot-authored pushes to avoid duplicate Pages runs

## Documentation

- **`docs/operator-guide.md`** — Complete setup, configuration, and troubleshooting guide for new operators
- **`docs/rollout-checklist.md`** — Step-by-step verification checklist for first-time deployments
- **`docs/pipeline-validation.md`** — Stage checklist, artifact handoffs, success criteria, and known limitations
- **`docs/analysis-spec.md`** — Detailed specification for analysis output format and quality gate criteria
- **`.squad/decisions.md`** — Architectural decisions and decision history
