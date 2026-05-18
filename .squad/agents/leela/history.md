# Leela — History

## Project Context
- **Project:** SquadScope — A GitHub Pages site that summarizes weekly tech news from GitHub
- **Stack:** TBD (GitHub Actions for automation, static site for GitHub Pages)
- **User:** jmservera
- **Goal:** Review new GitHub repos weekly, track trending repos by stars, summarize trends with critical thinking about what's important, what's trending, and what's missing. Future expansion to other tech news platforms.

## Learnings

### 2026-05-18 — PRD Authoring

- **PRD location:** `docs/PRD.md` — comprehensive PRD covering all requirements from jmservera
- **Architecture decisions made:**
  - Hugo recommended as static site generator (speed, simplicity, native RSS)
  - Pagefind for client-side search (static, no server dependency)
  - RSS + GitHub Releases for MVP notifications (zero external dependencies)
  - Plugin pattern for future data source extensibility
  - Reskill every 5 runs via simple counter in `.squad/run-counter.txt`
- **Key open questions flagged:**
  - How to invoke Copilot in GitHub Actions (OQ1, OQ3) — blocks Phase 2
  - Hugo vs Astro preference (OQ2) — awaiting stakeholder input
  - Star threshold for significance filtering (OQ4) — proposed 50 stars/week
- **User preferences noted:**
  - jmservera wants full automation with zero manual intervention
  - "Nap and reskill" metaphor is important — deliberate self-improvement built into the system
  - Free-only notification options
  - Ever-growing archive — nothing deleted
- **Content structure:** weekly (immutable) → monthly (append-only) → yearly (append-only)
- **Data paths:** `data/raw/` (JSON), `data/analyzed/` (Markdown), `content/` (Hugo pages)

### 2026-05-18T10:06:38.734+02:00 — PRD Decomposition

- **Decomposition approach:** Split the PRD into tightly scoped, single-session GitHub issues organized by delivery phase and explicit handoffs between crawl, analyze, generate, notify, and reskill stages.
- **Issue count:** 18 delivery issues + 6 governance/validation issues = 24 total issues.
- **Phase structure:** Added a new **Phase 0: Investigation** in front of Foundation so OQ1/OQ3 (Copilot CLI in Actions + auth path) are resolved before automation work proceeds.
- **Assignment pattern:** Mapped issues to roster strengths — Bender for Actions/crawler/integrations, Farnsworth for analysis/reskill logic, Amy for site/search/UX, Fry for validation, and Leela for architecture/docs.

### 2026-05-18T10:11:20Z — Decisions Merged

- **Copilot CLI:** Standalone CLI with fine-grained PAT (Copilot Requests) approved for Phase 0. Fallback: GitHub Models API.
- **MCP crawling:** Multi-site crawling authorized; remote calls require allowlist in GitHub Copilot agent settings.
- **Phase 0 gating:** OQ1/OQ3 investigation issues must close before Phase 2 analyzer work begins.
- **Next:** Issue creation from scripts/create-issues.sh is ready for execution.
