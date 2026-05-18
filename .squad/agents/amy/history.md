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
- **2026-05-18T10:27:35.339+02:00:** Homepage and archive rendering now live in Hugo section/layout templates (`layouts/index.html`, `layouts/archive/list.html`, `layouts/weekly/single.html`) so the newest weekly summary, archive chronology, and per-report metric cards render without manual editing.
- **2026-05-18T10:27:35.339+02:00:** Weekly content generation should follow the `archetypes/weekly.md` frontmatter schema: `title`, `date`, `week`, `tags`, `categories`, `repos_featured`, `stars_tracked`, `top_repo`, and `summary`, followed by the five standard analysis sections.
- **2026-05-18T10:27:35.339+02:00:** RSS is enabled through Hugo outputs in `hugo.toml`, and the verified root feed for this setup is `public/index.xml` alongside section and taxonomy RSS pages.
- **2026-05-18T10:59:10Z:** Issues #3 and #4 complete. Commits c46beab, 05372c3. Ready for Issue #6+. User directive: all future work follows branch → PR → Review → Merge workflow (no direct commits to main).
