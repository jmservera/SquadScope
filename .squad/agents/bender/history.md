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

- **2026-05-18T13:05:53.678+02:00:** Issue #10 integrates `analyze` directly into `crawl-and-publish.yml` after `crawl`, with `raw-data` as the crawl→analyze handoff artifact and `analyzed-data` as the stable downstream artifact contract for future generate jobs.
- **2026-05-18T13:05:53.678+02:00:** The safest Phase 2 analysis execution path is: try standalone `copilot` CLI first (`copilot-requests: write`, PAT in `COPILOT_GITHUB_TOKEN`), then fall back to `scripts/analyze_fallback.py` against the GitHub Models API (`models: read`, `GITHUB_TOKEN`) using the same rendered prompt template.
- **2026-05-18T13:05:53.678+02:00:** The automated reviewer gate should validate the analyzer contract, not just file existence: YAML frontmatter with the exact required keys, ordered H2/H3 sections, `quality_score >= 60`, body word-count floor, and rejection of raw JSON/tool-log leakage before publish continues.
- **2026-05-18T12:07:20.778+02:00:** Copilot review follow-up on crawler hardening: keep star snapshots broad for `stars_gained`, but document that they intentionally cover pre-filter candidates; restore `get_json()` payload compatibility via an internal `get_json_entry()` helper; treat malformed JSON as non-retryable; and search both `RAW_ROOT` and custom `--output` parents when loading prior star snapshots so reruns keep working.
- **2026-05-18T12:07:20.778+02:00:** Issue #8 adds a dedicated `crawl-and-publish.yml` workflow for the crawl stage only: weekly Monday 08:00 UTC plus manual dispatch, serialized with `concurrency`, committing refreshed `data/raw/`, `data/snapshots/`, and `data/cache/`, and restoring the latest successful `crawl-cache` artifact via Actions API lookup so weekly runs can reuse the crawler cache.
- **2026-05-18T10:06:38.734+02:00:** GitHub Actions can run the standalone `copilot` CLI (`@github/copilot`) in programmatic mode with `copilot -p ...`. The safest documented CI auth flow is a fine-grained PAT with the **Copilot Requests** account permission passed as `COPILOT_GITHUB_TOKEN`; `gh auth token` only exposes an existing `gh` token and `gh-copilot` is deprecated in favor of the standalone CLI. GitHub Models (`models: read`) is the clean fallback if direct Copilot CLI automation proves brittle.
- **2026-05-18T10:11:20Z:** Team decided Phase 0 PRD decomposition is final; 24 GitHub issues created (4 investigation + 20 implementation). PRD decomposition captures all decisions. MCP tools can crawl beyond GitHub with remote call allowlist. Ready for issue creation.
- **2026-05-18T10:27:35.339+02:00:** The crawler now uses `GET /search/repositories` for both `created:>{last_week_date} stars:>50` and `pushed:>{last_week_date} stars:>50`, comparing current stars against the most recent prior `data/raw/*.json` snapshot when available to estimate weekly star gains. It authenticates with `GITHUB_TOKEN`, paginates up to the GitHub Search API's 1,000-result ceiling, caches README checks in-process, applies exponential backoff with jitter for rate limits, and skips repos whose README lookup is blocked by org SAML enforcement.
- **2026-05-18T10:59:10Z:** Issue #5 complete. Commit fb14275 (209 new repos, 215 trending in data/raw/2026-W21.json). Ready for Issue #6+. User directive: all future work follows branch → PR → Review → Merge workflow (no direct commits to main).
- **2026-05-18T10:50:21Z:** PR #27 (Issue #8 crawl workflow) review complete. All 7 Copilot findings addressed (abb2a80). Workflow structure: restore `data/cache/` artifact, run `scripts/crawl.py`, upload `crawl-output` + new cache. Permissions `actions: read` + `contents: write`. Ready for merge. Downstream phases can depend on cache artifacts.
