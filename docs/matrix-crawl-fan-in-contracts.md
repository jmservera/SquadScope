# Matrix Crawl Fan-In Contracts

**Status:** Reference specification  
**Related issues:** #333, #435, #436, #437, #438, #439  
**PRD:** [docs/processed/PRD-matrix-crawl-map-reduce-analysis.md](processed/PRD-matrix-crawl-map-reduce-analysis.md)

---

## Overview

This document specifies the fan-in contracts for SquadScope's matrix crawl architecture. Fan-in is the merge step that combines per-shard or per-source artifacts into canonical downstream payloads. These contracts ensure deterministic, reproducible output regardless of whether collection ran as a monolithic process or as parallel matrix legs.

---

## Shared Run Context Schema

Every crawl leg, fan-in validator, mapper, and reducer receives the same immutable run context. No matrix leg may compute its own time window from the local wall clock.

```json
{
  "schema_version": "run_context_v1",
  "run_id": "<week>-<sha256-prefix>",
  "week": "2026-W23",
  "since": "2026-06-01T00:00:00Z",
  "until": "2026-06-08T00:00:00Z",
  "source_config_checksum": "sha256:<hex>",
  "topic_config_checksum": "sha256:<hex>",
  "code_sha": "<sha256-of-relevant-source-files>",
  "created_at": "2026-06-05T17:42:56Z"
}
```

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Must be `run_context_v1`. Fan-in rejects mismatches. |
| `run_id` | string | Stable identifier: `{week}-{sha256-prefix}`. |
| `week` | string | ISO week in `YYYY-WNN` format. |
| `since` | string (ISO-8601) | Inclusive start of the collection window. |
| `until` | string (ISO-8601) | Exclusive end of the collection window. |
| `source_config_checksum` | string | SHA-256 of the source configuration file. |
| `topic_config_checksum` | string | SHA-256 of `squadscope.topic.yml`. |
| `code_sha` | string | SHA-256 of relevant pipeline source files. |
| `created_at` | string (ISO-8601) | When the run context was generated. |

---

## Per-Source RSS Artifact Schema

Each RSS matrix leg emits exactly one artifact per source:

```json
{
  "schema_version": 2,
  "source_id": "techcrunch",
  "run_context": { "...shared run context..." },
  "status": "success | partial | failed",
  "articles": [
    {
      "url": "https://...",
      "title": "...",
      "published": "2026-06-03T10:00:00Z",
      "source": "techcrunch",
      "relevance_score": 0.85,
      "github_urls": ["https://github.com/..."],
      "entities": ["Company A", "Project B"]
    }
  ],
  "metrics": {
    "articles_fetched": 20,
    "articles_relevant": 12,
    "fetch_duration_ms": 1200,
    "retries": 0
  },
  "error": null,
  "checksum": "sha256:<hex-of-articles-array>"
}
```

### Validation rules

- `schema_version` must equal `2` (current canonical version).
- `run_context.week` must match the fan-in job's expected week.
- `run_context.source_config_checksum` must match across all legs.
- `checksum` must match the SHA-256 of the serialized `articles` array (sorted by URL, deterministic JSON).
- `status: "failed"` artifacts carry no `articles` and must include an `error` object.

---

## GitHub Crawl Shard Artifact Schema

Each GitHub shard leg (when enabled via experiment) emits:

```json
{
  "schema_version": "github_shard_v1",
  "shard_id": "new_repos | trending_repos | topic_primary | topic_secondary",
  "run_context": { "...shared run context..." },
  "repositories": [
    {
      "full_name": "owner/repo",
      "stars": 1234,
      "stars_gained": 45,
      "description": "...",
      "language": "Python",
      "topics": ["ai", "ml"],
      "created_at": "2026-01-15T...",
      "pushed_at": "2026-06-02T..."
    }
  ],
  "api_metrics": {
    "calls_made": 112,
    "cache_hits": 45,
    "cache_misses": 67,
    "secondary_rate_limit_events": 0,
    "search_api_remaining": 24
  },
  "checksum": "sha256:<hex>"
}
```

---

## Fan-In Merge Rules

### Ordering guarantees

1. **Deterministic repository ordering:** Repositories are sorted by `full_name` (lexicographic, case-sensitive). Ties are not possible since `full_name` is unique.
2. **Deterministic article ordering:** Articles are sorted by `(source_id, url)` tuple.
3. **Stable output:** Same input artifacts → byte-identical canonical output (excluding the `merged_at` timestamp, which is excluded from checksum computation).

### Deduplication

- **Repositories:** Deduplicated by `full_name`. If the same repo appears in multiple shards, the entry with the highest `stars_gained` is kept.
- **Articles:** Deduplicated by normalized URL (scheme + host + path, query params stripped). First occurrence by source priority order wins.

### Idempotency

- Rerunning fan-in with the same input artifacts produces identical output.
- Fan-in does not mutate input artifacts.
- Reruns do not double-count articles, repos, retries, or restored stale artifacts.
- The `run_id` in the run context serves as the idempotency key; the same `run_id` always maps to the same canonical output given the same inputs.

### Failure policy

| Scenario | Behavior |
|----------|----------|
| Required GitHub shard missing or invalid | **Fail closed.** No canonical output produced. Pipeline halts before analysis. |
| Optional RSS source failed | **Degrade.** Produce canonical output if minimum-source policy passes (≥3/5 sources succeed). Record explicit warnings. |
| Schema version mismatch | **Reject artifact.** Treat as missing. Apply required/optional rules above. |
| Window/checksum mismatch | **Reject artifact.** Log validation error with details. |
| All legs failed | **Fail closed.** Emit diagnostics artifact only. |

### Minimum-source policy

For RSS fan-in, the merge proceeds if:
- At least 60% of configured sources report `status: "success"` or `status: "partial"`.
- All `status: "partial"` sources still have ≥1 valid article.
- The canonical output includes a `warnings` array documenting degraded sources.

---

## Canonical Output Schema

Fan-in produces exactly two canonical artifacts consumed by downstream analysis:

### `data/raw/{week}.json` (GitHub)

The existing monolithic format, produced identically whether from one crawl process or merged shards.

### `data/raw/{week}-external-news.json` (RSS/News)

```json
{
  "schema_version": 2,
  "run_context": { "..." },
  "sources": {
    "techcrunch": { "status": "success", "articles_count": 12 },
    "nvidia_blog": { "status": "success", "articles_count": 5 },
    "huggingface": { "status": "failed", "error": "timeout" }
  },
  "articles": [ "...merged, deduplicated, sorted..." ],
  "metrics": {
    "total_articles": 39,
    "total_relevant": 23,
    "sources_succeeded": 4,
    "sources_failed": 1
  },
  "warnings": ["huggingface: fetch timeout after 15s"],
  "merged_at": "2026-06-05T18:00:00Z",
  "checksum": "sha256:<hex-of-articles>"
}
```

---

## Contract Versioning

- Schema versions use `<domain>_v<N>` format (e.g., `run_context_v1`, `github_shard_v1`).
- Breaking changes increment the version number.
- Fan-in rejects artifacts with unknown or mismatched schema versions.
- The `schema_version` field is required in every artifact; omission is treated as a validation failure.

---

## Downstream Consumers

The following components depend on canonical fan-in output and must NOT need to know whether collection was monolithic or matrix-based:

- `scripts/correlate.py` — correlation analysis
- `scripts/render_press_context.py` — press context rendering
- `scripts/generate_content.py` — AI analysis
- `scripts/map_reduce_dry_run.py` — map/reduce dry-run
- `scripts/analysis_gate.py` — quality gate validation
- Publishing workflow steps

---

## References

- PRD: [Matrix Crawl and Map/Reduce Analysis](processed/PRD-matrix-crawl-map-reduce-analysis.md)
- Issue #333: Define crawl matrix readiness and fan-in validation path
- Issue #435: Run GitHub crawl shard experiment
- Issue #436: Implement RSS matrix fan-in
- Issue #437: Wire observability metrics
- Issue #438: Automated QA gates
