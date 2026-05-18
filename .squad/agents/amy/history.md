# Amy — History

## Project Context
- **Project:** SquadScope — A GitHub Pages site that summarizes weekly tech news from GitHub
- **Stack:** GitHub Pages, static site generator (TBD), HTML/CSS/JS
- **User:** jmservera
- **Goal:** Build a clean, accessible GitHub Pages site that presents weekly tech trend analysis in an engaging format.

## Team Updates

**2026-05-18:** PRD now available at `docs/PRD.md`. Review for design requirements and site generation framework (Hugo recommended, Astro alternative).

**2026-05-18T10:27:35Z:** Phase 0 is complete. Architecture decision published in `.squad/decisions.md`. `COPILOT_GH_TOKEN` secret configured. Ready for Phase 1 work (site foundation and crawler implementation).

## Learnings

- **2026-05-18T10:27:35.339+02:00:** Hugo now scaffolds from the repo root with the primary site config in `hugo.toml` and the PaperMod theme installed as a git submodule at `themes/PaperMod`.
- **2026-05-18T10:27:35.339+02:00:** The MVP content structure lives under `content/weekly/`, `content/monthly/`, and `content/yearly/`, with archive/search entry pages at `content/archive.md` and `content/search.md`.
- **2026-05-18T10:27:35.339+02:00:** GitHub Pages deployment for the Hugo site is wired through `.github/workflows/deploy-site.yml`, and local builds should use `hugo --minify` after initializing submodules.
