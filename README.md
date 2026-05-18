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

## Deployment

Pushing to `main` triggers `.github/workflows/deploy-site.yml`, which builds the Hugo site and deploys the generated `public/` directory to GitHub Pages.
