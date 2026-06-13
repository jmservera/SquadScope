# Observability Metrics Schema

`scripts/observability_metrics.py` defines the durable ledger schema for crawl and analysis observability artifacts written to `data/metrics/observability/`.

## Schema version

- Current version: `observability_v1`
- Writers must set `schema_version` exactly.
- Downstream checks should fail if `validate_ledger()` reports any missing required field paths.

## Artifact layout

Current pipeline writers emit:

- `data/metrics/observability/{week}-github-crawl.json`
- `data/metrics/observability/{week}-external-news-crawl.json`
- `data/metrics/observability/{week}-map-reduce.json`

These are runtime artifacts and are gitignored.

## Top-level ledger fields

Required:

- `schema_version`
- `run_id`
- `week`
- `timestamp`
- `crawl_metrics`
- `environment`

Optional:

- `analysis_metrics`

## `crawl_metrics[]`

Required fields:

- `source_type` (`github` or `external-news`)
- `duration_seconds`
- `api_calls`
- `cache_hits`
- `cache_misses`
- `stale_cache_hits`
- `rate_limit_events`
- `secondary_rate_limit_hit`

Optional fields:

- `duration_p95_seconds`
- `duration_sample_count`

Notes:

- GitHub crawl currently records overall run duration as the comparable sampled duration.
- External-news crawl records p95 from per-source fetch durations when available.

## `analysis_metrics`

Required fields when present:

- `duration_seconds`
- `token_ledger`
- `map_stages`

Optional:

- `reduce_stage`

### `token_ledger`

Required:

- `input_tokens`
- `output_tokens`
- `total_tokens`

Common additional field:

- `cost_usd`

### `map_stages[]` and `reduce_stage`

Required:

- `stage`
- `duration_seconds`
- `input_tokens`
- `output_tokens`
- `cost_usd`
- `status` (`pass` or `fail`)
- `gate_failure_reasons`

## Validation

Use `validate_ledger()` from `scripts.observability_metrics`:

```python
from scripts.observability_metrics import validate_ledger

errors = validate_ledger(payload)
if errors:
    raise SystemExit(f"Missing required observability fields: {errors}")
```

`emit_ledger()` already validates before writing and raises `ValueError` on schema gaps.

## Example

Representative end-to-end sample:

- `tests/fixtures/observability/2026-W21-full-run.json`

Minimal shape:

```json
{
  "schema_version": "observability_v1",
  "run_id": "12345",
  "week": "2026-W21",
  "timestamp": "2026-05-20T12:00:00Z",
  "crawl_metrics": [
    {
      "source_type": "github",
      "duration_seconds": 12.4,
      "api_calls": 27,
      "cache_hits": 14,
      "cache_misses": 27,
      "stale_cache_hits": 1,
      "rate_limit_events": 2,
      "secondary_rate_limit_hit": false
    }
  ],
  "analysis_metrics": {
    "duration_seconds": 3.2,
    "token_ledger": {
      "input_tokens": 1234,
      "output_tokens": 456,
      "total_tokens": 1690,
      "cost_usd": 0.0
    },
    "map_stages": [],
    "reduce_stage": null
  },
  "environment": {
    "pipeline": "map-reduce-dry-run"
  }
}
```

## Downstream check guidance

- Treat `schema_version` as a compatibility gate.
- Call `validate_ledger()` and fail on any returned field path.
- Prefer exact field-path assertions over permissive defaults so missing metrics break CI early.
- For experiment reports tied to issue #356, link the representative fixture above plus the emitted runtime artifacts from the relevant workflow run.
