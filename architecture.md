# SquadScope / Claracle Architecture

## Overview

SquadScope, publicly branded as **Claracle**, is an AI-powered GitHub trend observatory. It crawls GitHub and selected external sources each week, uses Copilot CLI to analyze signal versus noise, generates Hugo content, deploys a public static site at **www.claracle.com**, periodically reskills its AI squad state, and hands published articles to the Podcaster system for episode generation.

## Tech Stack

- **Hugo** static site generator with the **PaperMod** theme
- **Pagefind** for client-side search
- **Python** scripts for crawl, analysis prep, content generation, publishing, and handoff automation
- **GitHub Actions** for orchestration
- **GitHub Pages** for hosting
- **GitHub Copilot CLI** for AI analysis (two-step: `weekly-synthesis` → `weekly-analysis`, both gpt-5.5) and reskill work
- **No OpenAI / GitHub Models fallback** for weekly analysis

## Directory Structure

- `scripts/` — Python pipeline automation for crawl, analyze, generate, publish, reskill, and handoff
- `content/` — Hugo content, including `weekly/`, `monthly/`, and `yearly/`
- `data/` — pipeline artifacts, including `raw/`, `analyzed/`, `snapshots/`, `metrics/`, and `cache/`
- `config/` — cross-workflow shared config such as `podcast.json` and `external_news_sources.json`
- `layouts/`, `assets/`, `static/` — Hugo theme and site customizations
- `infra/` — reserved for Infrastructure as Code if/when introduced; not present today
- `tests/` — unit and integration tests
- `docs/` — operator guides, pipeline specs, design notes, and audits
- `.squad/` — AI team state, history, reskill outputs, and conventions

## Data Flow

1. **Crawl**  
   GitHub API data is written to `data/raw/YYYY-WNN.json`, and external RSS/news enrichment is written to `data/raw/YYYY-WNN-external-news.json`.
2. **Analyze**  
   Two-step Copilot CLI analysis using dedicated agents (both gpt-5.5):
   - *Weekly Synthesis* agent produces a compact industry narrative from press/historical context
   - *Weekly Analysis* agent consumes the synthesis plus raw data to generate `data/analyzed/YYYY-WNN-summary.md`
   - Additional outputs: `data/analyzed/YYYY-WNN-correlations.json`, `data/analyzed/YYYY-WNN-press-context.md`
3. **Generate**  
   The analyzed summary is transformed into Hugo content at `content/weekly/YYYY/WNN.md`.
4. **Deploy**  
   Hugo builds the site and GitHub Pages serves the generated output.
5. **Reskill**  
   Every 5th successful crawl run writes retrospective squad learning to `.squad/reskill/YYYY-WNN.md`.
6. **Podcaster Handoff**  
   After publish, the article and podcast config are POSTed to the Podcaster API.

## Shared Interfaces (with SquadScope-Podcaster)

- `config/podcast.json` is the source of truth for podcast editorial direction
  - `podcast_config`: hosts, voices, styles, show name, and URL
  - `script_directions`: `opening_cues`, `closing_cues`, and `episode_style`
  - `music_mix`: track, voice guardrail, and intro/outro mix parameters
- Handoff payload fields:
  - `week`
  - `article_url`
  - `article_content`
  - `article_title`
  - `article_sha256`
  - `source_artifacts`
  - `podcast_config`
  - `script_directions`
  - `breaking_news` — optional last-moment news text to include in the episode (omitted when not provided)
- Transport: HTTP `POST` with `x-podcaster-api-key` header
- Handoff implementation: `scripts/podcaster_handoff.py`

## Environment Variables / Secrets

- `PODCASTER_ENDPOINT` — Podcaster API URL
- `PODCASTER_API_KEY` — Podcaster authentication key
- `GITHUB_TOKEN` — GitHub crawl and workflow access
- Copilot token/permission via GitHub Actions for Copilot CLI analysis

## Key Commands

- Weekly pipeline: `.github/workflows/crawl-and-publish.yml`
- Local development: `hugo server`
- Build: `hugo --minify`
- Crawl: `python3 scripts/crawl.py --as-of YYYY-MM-DD`
- Generate: `python3 scripts/generate_content.py`
- Handoff: `python3 scripts/podcaster_handoff.py`
