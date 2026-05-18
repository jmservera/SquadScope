# Bender crawler implementation

- **Date:** 2026-05-18T10:27:35.339+02:00
- **Owner:** Bender
- **Context:** Issue #5 crawler implementation

## Decision
Use a stdlib-only Python crawler (`urllib`) that writes `data/raw/YYYY-WNN.json`, computes trending rank from the latest prior raw snapshot when available, and defaults to fetching the top 250 search results per query while still supporting pagination up to GitHub's 1,000-result search limit via `--max-results`.

## Why
- Keeps CI setup minimal (`requirements.txt` can stay dependency-free)
- Makes weekly crawls deterministic and cheap enough for local and Actions runs
- Preserves a path to deeper crawls without changing the data contract

## Notes
- Search endpoints used: `created:>{date} stars:>50` and `pushed:>{date} stars:>50`
- Significance filter excludes forks, repos without descriptions, repos without READMEs, and obvious tutorial/homework/template repos by heuristic keywords/topics
- Repos whose README endpoint is blocked by org SAML enforcement are skipped instead of failing the whole crawl
