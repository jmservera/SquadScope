# Bender — History

## Project Context
- **Project:** SquadScope — A GitHub Pages site that summarizes weekly tech news from GitHub
- **Stack:** GitHub Actions, GitHub API, data collection scripts
- **User:** jmservera
- **Goal:** Automated weekly crawling of GitHub for new repos and trending repos (by stars), outputting structured data for analysis.

## Team Updates

**2026-05-18:** PRD now available at `docs/PRD.md`. Review for requirements and constraints on crawler implementation.

## Learnings

- **2026-05-18T10:06:38.734+02:00:** GitHub Actions can run the standalone `copilot` CLI (`@github/copilot`) in programmatic mode with `copilot -p ...`. The safest documented CI auth flow is a fine-grained PAT with the **Copilot Requests** account permission passed as `COPILOT_GITHUB_TOKEN`; `gh auth token` only exposes an existing `gh` token and `gh-copilot` is deprecated in favor of the standalone CLI. GitHub Models (`models: read`) is the clean fallback if direct Copilot CLI automation proves brittle.
- **2026-05-18T10:11:20Z:** Team decided Phase 0 PRD decomposition is final; 24 GitHub issues created (4 investigation + 20 implementation). PRD decomposition captures all decisions. MCP tools can crawl beyond GitHub with remote call allowlist. Ready for issue creation.
