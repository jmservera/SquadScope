# Bender — History

## Project Context
- **Project:** SquadScope — A GitHub Pages site that summarizes weekly tech news from GitHub
- **Stack:** GitHub Actions, GitHub API, data collection scripts
- **User:** jmservera
- **Goal:** Automated weekly crawling of GitHub for new repos and trending repos (by stars), outputting structured data for analysis.

## Team Updates

**2026-05-18:** PRD now available at `docs/PRD.md`. Review for requirements and constraints on crawler implementation.

**2026-05-18T10:27:35Z:** Phase 0 is complete. Architecture decision published in `.squad/decisions.md`. `COPILOT_GH_TOKEN` secret configured. Phase 1 crawler work can proceed with finalized CI analysis interface and fallback strategies.

## Learnings

- **2026-05-18T10:06:38.734+02:00:** GitHub Actions can run the standalone `copilot` CLI (`@github/copilot`) in programmatic mode with `copilot -p ...`. The safest documented CI auth flow is a fine-grained PAT with the **Copilot Requests** account permission passed as `COPILOT_GITHUB_TOKEN`; `gh auth token` only exposes an existing `gh` token and `gh-copilot` is deprecated in favor of the standalone CLI. GitHub Models (`models: read`) is the clean fallback if direct Copilot CLI automation proves brittle.
- **2026-05-18T10:11:20Z:** Team decided Phase 0 PRD decomposition is final; 24 GitHub issues created (4 investigation + 20 implementation). PRD decomposition captures all decisions. MCP tools can crawl beyond GitHub with remote call allowlist. Ready for issue creation.
- **2026-05-18T10:27:35.339+02:00:** The crawler now uses `GET /search/repositories` for both `created:>{last_week_date} stars:>50` and `pushed:>{last_week_date} stars:>50`, comparing current stars against the most recent prior `data/raw/*.json` snapshot when available to estimate weekly star gains. It authenticates with `GITHUB_TOKEN`, paginates up to the GitHub Search API's 1,000-result ceiling, caches README checks in-process, applies exponential backoff with jitter for rate limits, and skips repos whose README lookup is blocked by org SAML enforcement.
