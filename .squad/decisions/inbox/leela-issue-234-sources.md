# Leela — Issue 234 external news source architecture

Date: 2026-06-05T15:36:19.379+00:00
Issue: #234

## Decision

Keep external news crawling in the existing crawl job and make the RSS source list config-driven via `config/external_news_sources.json`. Fetch the configured feeds concurrently inside `scripts/techcrunch_crawler.py` using a bounded thread pool, and write one weekly enrichment artifact: `data/raw/YYYY-WNN-external-news.json`.

## Rubberduck tradeoff

Separate GitHub Actions jobs would parallelize at the runner level, but every source would repeat checkout, Python setup, dependency install, artifact upload/download, and failure-handling boilerplate. For five RSS feeds, that overhead is larger than the network wait we are optimizing away, and it would fragment a single enrichment contract across multiple artifacts.

In-process threading matches the current architecture better: RSS fetching is I/O-bound, feedparser work is light, and the existing crawl job already owns raw data artifact handoff. A bounded pool preserves Actions compute, keeps one failure surface, and lets future sources be added by config without editing workflow topology.

## Scope boundary

This is a small architectural refactor around an existing RSS crawler, so Leela implemented directly rather than reassigning to Bender. Deeper crawler work, such as source-specific parsing, feed health dashboards, or correlation logic, should remain Bender-owned.
