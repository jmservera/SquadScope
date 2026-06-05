# Bender issue #237 implementation

Date: 2026-06-05

## Decision

Keep external RSS/news in the existing crawl job with bounded in-process parallelism, but promote the handoff to a canonical `schema_version: 2` `data/raw/{week}-external-news.json` artifact. The artifact carries crawl window, source config checksum, requested/succeeded/failed sources, per-source status metrics, dedupe count, deterministic checksum, and partial-failure metadata.

## Rationale

The measured bottleneck remains the GitHub repository crawl, not the five-source RSS step. Source-aware telemetry and schema validation improve downstream reliability without adding Actions matrix startup overhead or splitting cache/API behavior.

## Operational notes

`correlate.py` and `render_press_context.py` now preserve article source/title/date/URL citations, label strong versus weak correlations, bound press context size to an ~8k token estimate, and keep legacy `*-techcrunch.json` and no-press fallbacks.
