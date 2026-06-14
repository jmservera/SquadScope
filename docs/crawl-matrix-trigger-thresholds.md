# Crawl Matrix Trigger Thresholds

**Status:** Active  
**Related issues:** #333, #435, #436  
**PRD:** [docs/processed/PRD-matrix-crawl-map-reduce-analysis.md](processed/PRD-matrix-crawl-map-reduce-analysis.md)

---

## Overview

This document specifies the evidence-based trigger thresholds that must be met before enabling RSS matrix fan-out or GitHub shard experiments in the default pipeline path. These thresholds ensure that matrix complexity is only introduced when measurable evidence justifies it.

**Baseline requirement:** At least 5 representative production runs must be observed before any trigger evaluation is valid (or an explicitly documented shorter window with rationale).

---

## RSS Matrix Triggers

The RSS/news collection path remains in-process (monolithic) unless ALL of the following conditions are met:

| Trigger | Threshold | Measurement |
|---------|-----------|-------------|
| **p95 runtime** | > 60 seconds | Measured across ≥5 runs from observability ledger (`source_type: rss`) |
| **Source count** | > 10 configured sources | Count of active entries in source config |
| **Source-specific isolation** | Required | Any source needing independent credentials, rate limits, or network isolation |
| **Flaky-source retry** | Required | Any source requiring retry logic that would delay other sources |

### Decision logic

```
IF baseline_runs >= 5
  AND (rss_p95 > 60s OR source_count > 10 OR isolation_required OR flaky_retry_needed)
THEN propose RSS matrix enablement (requires explicit approval)
ELSE RSS matrix remains disabled
```

### Current baseline status

Run `python -m scripts.baseline_telemetry check` to see current values.

---

## GitHub Shard/Matrix Triggers

GitHub crawl sharding remains **no-publish experimental** unless ALL of the following are met:

| Trigger | Threshold | Measurement |
|---------|-----------|-------------|
| **Wall-clock speedup** | ≥ 25% reduction vs. monolithic baseline | Compare shard experiment p50 to monolithic baseline p50 |
| **API-call growth** | ≤ 10% increase | Total API calls (shard sum) vs. monolithic baseline |
| **Secondary rate-limit regression** | Zero events | No secondary rate-limit events in shard experiment |
| **Cache coherence** | Maintained | Cache hit ratio within 5% of monolithic baseline |
| **Output parity** | Byte-stable | Canonical merged output matches monolithic output (excluding timestamps) |

### Decision logic

```
IF shard_experiment_runs >= 3
  AND speedup_pct >= 25
  AND api_call_growth_pct <= 10
  AND secondary_rate_limit_events == 0
  AND cache_hit_ratio_delta <= 5%
  AND byte_stable_output == true
THEN propose GitHub shard default-on (requires explicit approval + ADR update)
ELSE GitHub shard remains no-publish experiment only
```

### Experiment execution

See `scripts/crawl_shard_experiment.py` (issue #435) for the no-publish experiment runner. Results are written to `data/experiments/shard-435/`.

---

## Trigger Evaluation Process

1. **Collect baseline:** Pipeline operator runs ≥5 production cycles with observability metrics enabled.
2. **Generate report:** `python -m scripts.baseline_telemetry report --output data/metrics/baseline-report.json`
3. **Check triggers:** `python -m scripts.baseline_telemetry check --min-runs 5`
4. **If triggered:** Open a proposal issue referencing the baseline report. Requires team review and ADR update before enabling.
5. **If not triggered:** No action. Re-evaluate after next 5-run window.

---

## Existing Behavior Preservation

These triggers are gates ONLY. Until a trigger fires and is explicitly approved:

- ✅ `scripts/crawl.py` — monolithic GitHub crawl unchanged
- ✅ `scripts/techcrunch_crawler.py` — in-process RSS crawl unchanged  
- ✅ `scripts/correlate.py` — correlation analysis unchanged
- ✅ `scripts/render_press_context.py` — press context rendering unchanged
- ✅ `scripts/generate_content.py` — analysis unchanged
- ✅ `scripts/publish_manifest.py` — publish manifest unchanged
- ✅ Canonical artifact paths (`data/raw/{week}.json`, `data/raw/{topic}/{week}-external-news.json`) unchanged

---

## References

- [Fan-in contracts](matrix-crawl-fan-in-contracts.md)
- [ADR: Matrix Crawl Fan-In](decisions/adr-matrix-crawl-fan-in.md)
- [Operator Runbook](matrix-crawl-runbook.md)
- Baseline telemetry: `scripts/baseline_telemetry.py`
- Run context schema: `scripts/run_context.py`
- Fan-in validator: `scripts/fan_in_validator.py`
