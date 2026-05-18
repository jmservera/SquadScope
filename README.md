# SquadScope

SquadScope is a Hugo-powered GitHub Pages site for weekly, monthly, and yearly tech trend summaries sourced from GitHub.

## Theme and stack

- Static site generator: Hugo (extended)
- Theme: [PaperMod](https://github.com/adityatelange/hugo-PaperMod)
- Deployment: GitHub Pages via GitHub Actions

## Local development

1. Install the Hugo extended binary (version 0.146.0 or newer).
2. Clone the repository with submodules, or initialize them after cloning:
   - `git clone --recurse-submodules https://github.com/jmservera/SquadScope.git`
   - `git submodule update --init --recursive`
3. Start the local development server:
   - `hugo server`
4. Create a production build:
   - `hugo --minify`

## Content structure

- `content/weekly/` — weekly summaries
- `content/monthly/` — monthly rollups
- `content/yearly/` — yearly summaries
- `data/raw/` — crawler output
- `data/analyzed/` — analysis output
- `data/snapshots/` — star count snapshots

## Crawler notes

- `signals.top_topics` de-duplicates repositories by `full_name` across the new and trending buckets before counting topics, so a repo found by both searches only contributes once.
- `data/snapshots/YYYY-WNN-stars.json` intentionally stores the broader pre-filter search candidate universe to preserve week-over-week `stars_gained` comparisons even when a repo is later filtered out of the published payload.
- Live runs use open-ended `created:>` / `pushed:>` GitHub search filters; `--as-of` runs switch to bounded date ranges so historical backfills stay deterministic.

## Automated weekly pipeline

`.github/workflows/crawl-and-publish.yml` runs the full weekly automation chain:

1. `crawl` writes `data/raw/YYYY-WNN.json` and `data/snapshots/YYYY-WNN-stars.json`.
2. `analyze` turns the raw payload into `data/analyzed/YYYY-WNN-summary.md`.
3. `generate` converts the analysis into `content/weekly/YYYY/WNN.md`.
4. `deploy` builds `public/` with Hugo and publishes the site to GitHub Pages.

### Schedule and manual runs

- Scheduled cron: `0 8 * * 1` (`Monday 08:00 UTC`)
- Manual workflow trigger: GitHub Actions UI or `gh workflow run crawl-and-publish.yml`

### Required secrets

- `COPILOT_GH_TOKEN` for the primary Copilot CLI analysis path
- `GITHUB_TOKEN` for crawling, fallback analysis, commits, and Pages deployment

### Local/manual stage commands

- Crawl: `python3 scripts/crawl.py --as-of YYYY-MM-DD`
- Analyze fallback: `python3 scripts/analyze_fallback.py --raw-json data/raw/YYYY-WNN.json --output data/analyzed/YYYY-WNN-summary.md --current-datetime YYYY-MM-DDTHH:MM:SSZ`
- Gate: `python3 scripts/analysis_gate.py --analysis-file data/analyzed/YYYY-WNN-summary.md --raw-json data/raw/YYYY-WNN.json --current-datetime YYYY-MM-DDTHH:MM:SSZ`
- Generate: `python3 scripts/generate_content.py data/analyzed/YYYY-WNN-summary.md`
- Build: `hugo --minify`

## Deployment

Direct pushes to `main` still trigger `.github/workflows/deploy-site.yml` for standard site deploys. The weekly automation deploys Pages from `crawl-and-publish.yml` and `deploy-site.yml` skips bot-authored pushes from that workflow to avoid duplicate Pages runs.

See `docs/pipeline-validation.md` for the stage checklist, artifact handoffs, success criteria, and known limitations.
