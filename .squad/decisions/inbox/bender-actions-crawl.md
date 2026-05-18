# Bender decision inbox: Actions crawl workflow

- **Date:** 2026-05-18T12:07:20.778+02:00
- **Author:** Bender
- **Issue:** #8

## Proposed team decision

Restore `data/cache/` from the latest successful `crawl-and-publish.yml` run before executing `scripts/crawl.py`.

## Why

- Reuses the crawler's on-disk GitHub API cache across weekly runs
- Lowers repeated README/search calls on warm runs
- Keeps the crawl stage self-contained until downstream jobs arrive in later issues

## Workflow implication

The workflow needs `actions: read` in addition to `contents: write` so it can discover the prior successful run and download the `crawl-cache` artifact.
