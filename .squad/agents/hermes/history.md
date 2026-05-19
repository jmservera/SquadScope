# Hermes — History

## Project Context
- **Project:** SquadScope — A GitHub Pages site summarizing weekly tech news from GitHub trending repos, correlated with TechCrunch RSS feed
- **Stack:** Python scripts (crawl, analyze, correlate), Hugo static site, GitHub Actions CI/CD
- **User:** jmservera
- **Team:** Futurama universe cast — Leela (Lead), Bender (Crawler), Farnsworth (Analyst), Amy (Frontend), Fry (Tester), Hermes (Security)
- **Joined:** 2026-05-19

## Learnings

### Day 1 Context
- CI workflow uses PR-based commits (no direct push to main) — branch protection enforced
- Ruleset has empty bypass_actors — no admin bypass
- Pipeline: crawl GitHub API → crawl TechCrunch RSS → correlate → AI analysis → generate Hugo content → deploy
- AI fallback chain: Copilot CLI → GitHub Models API → no-AI data summary
- Token/secrets used: GITHUB_TOKEN (scoped per job), GitHub Models API token
- Rate limiting handled with exponential backoff in crawl.py and analyze_fallback.py
