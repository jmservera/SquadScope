# Shard 435 Crawl Experiment Plan

## Goal

Run a local-only, no-publish experiment that compares the monolithic GitHub crawl with a sharded variant while enforcing:

- at least 25% wall-clock improvement
- no more than 10% GitHub API growth
- no secondary-rate-limit regression
- byte-stable downstream payloads after deterministic fan-in

## Shard Boundaries

1. **Shard 1 — new-search**
   - runs the new-repository search query group
   - in config mode, runs primary queries first and only falls back to secondary queries when needed

2. **Shard 2 — trending-search**
   - runs the trending-repository search query group
   - skipped only when config mode intentionally has no trending bucket and must preserve existing semantics

3. **Shard 3+ — validate-N**
   - consume deduplicated candidate chunks from a shared queue
   - perform README/detail validation and final filtering
   - requeue unfinished work when a shard hits its wall-clock limit so other shards can absorb the remainder

## Deterministic Fan-in

- keep new/trending buckets separate to preserve the canonical raw-artifact shape
- dedupe within each bucket by `full_name`
- sort final outputs like `crawl.py`
  - new repos by stars descending
  - trending repos by `stars_gained`, then stars descending
- rebuild signals and star snapshots only after fan-in
- compare canonical payload bytes after stripping volatile timestamp metadata

## Guardrails

- **Wall-clock budget:** each shard gets a configurable deadline (default 120s)
- **API budget:** shard mode shares a global counter capped at `baseline_calls × 1.1`
- **Shared backoff:** retry backoff windows are propagated across shard clients
- **Rollback condition:** any secondary rate limit aborts remaining shard work and records a guardrail event

## Assumptions

- threading is sufficient because the workload is API I/O bound
- cache reads are safe to share across shard clients
- cross-bucket duplicates may still appear in both `new_repos` and `trending_repos` because the baseline crawl already allows that
- at least three representative real runs are still required after implementation

## Output Artifacts

All experiment artifacts stay under `data/experiments/shard-435/EXPERIMENT_ID/`:

- `baseline-raw.json`
- `baseline-stars.json`
- `shard-raw.json`
- `shard-stars.json`
- `report.json`

## Suggested Command

```bash
python -m scripts.crawl_shard_experiment \
  --since 2026-06-06 \
  --as-of 2026-06-13 \
  --shards 3 \
  --wall-clock-budget 300 \
  --api-budget-multiplier 1.1 \
  --output-dir data/experiments/shard-435
```
