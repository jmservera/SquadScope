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

## Deployment

Pushing to `main` triggers `.github/workflows/deploy-site.yml`, which builds the Hugo site and deploys the generated `public/` directory to GitHub Pages.

The scheduled weekly pipeline in `.github/workflows/crawl-and-publish.yml` now runs `crawl → analyze → generate → deploy`, using `scripts/generate_content.py` to turn `data/analyzed/YYYY-WNN-summary.md` into `content/weekly/YYYY/WNN.md` before the Pages build and Pagefind indexing steps.
