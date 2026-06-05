# Bender PR #242 Copilot Review Fixes

- Keep category/project-name-only press matches weak even when temporally spiking or corroborated by multiple articles/sources.
- Pass both `--since` and `--until` from the crawl workflow to preserve deterministic canonical `crawl_window` metadata.
- Record bounded fetch attempts and timeout telemetry on `NewsFeedSource` even when `fetch_feed()` raises before returning a feed.
- Keep press-context article lookup comments aligned with the actual URL-to-title mapping.
