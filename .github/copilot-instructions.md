# Copilot Instructions for SquadScope

This repository uses the **Squad agent** as the default for all AI-assisted work.

## Default Agent

Always use `--agent squad` when running Copilot CLI on this repository.

## Repository Context

- **Project:** SquadScope (public brand: Claracle) — AI-powered GitHub trend analysis
- **Architecture:** See `architecture.md` in repo root
- **Squad team:** See `.squad/team.md` for current roster

## Key Conventions

- All pipeline scripts are in `scripts/` (Python)
- Content is Hugo markdown in `content/`
- Config shared with Podcaster lives in `config/podcast.json`
- Changes to `config/podcast.json` MUST be coordinated with SquadScope-Podcaster repo
- Never commit secrets; use GitHub environment secrets
- PRs required for `main` branch (branch protection enabled)
- CI must be correct, not just green — verify rendered output for site changes

## Cross-Repo Impact

Changes to these files affect the Podcaster repo:

- `config/podcast.json` — Podcaster reads this config for episode generation
- `scripts/podcaster_handoff.py` — defines the handoff payload contract

## Testing

- Run `pytest tests/` for unit tests
- Hugo build: `hugo --minify` must succeed
- Handoff smoke: `.github/workflows/podcaster-handoff-smoke.yml`
