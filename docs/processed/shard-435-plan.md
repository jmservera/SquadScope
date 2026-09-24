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

## Outcome (archived 2026-09-24)

**Decision: defer — do not adopt sharded production crawl.** Tracked in #800; the decision record is in `.squad/decisions.md`.

The runs below were local-only and nothing was published. Raw payloads are not committed. Each run used `--api-budget-multiplier 1.1`, the default isolated cache mode, and a GitHub REST token. The windows were the three most recent complete weeks.

| Run | Window | Shards | Budget | Baseline s | Shard s | Speedup | API calls (b/s) | Rate-limit events (b/s) | Byte-stable fan-in | Repo sets equal | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| b1500-W38 | 2026-09-14→21 | 3 | 1500 | 333.5 | 318.6 | 4.5% ❌ | 447 / 447 (0%) ✅ | 0 / 0 ✅ | no ❌ (live drift) | yes | fail |
| b1500-W37 | 2026-09-07→14 | 3 | 1500 | 331.3 | 317.5 | 4.2% ❌ | 444 / 444 (0%) ✅ | 0 / 0 ✅ | no ❌ (live drift) | yes | fail |
| b1500-W36 | 2026-08-31→09-07 | 3 | 1500 | 334.0 | 314.2 | 5.9% ❌ | 447 / 447 (0%) ✅ | 0 / 0 ✅ | no ❌ (live drift) | yes | fail |
| s5-W38 (supplementary) | 2026-09-14→21 | 5 | 1500 | 337.1 | 117.6 | 65.1% ✅ | 447 / 447 (0%) ✅ | 0 / 0 ✅ | no ❌ (live drift) | yes | fail (byte-stability) |
| s5-W37 (supplementary) | 2026-09-07→14 | 5 | 1500 | 338.9 | 122.7 | 63.8% ✅ | 444 / 444 (0%) ✅ | 0 / 0 ✅ | no ❌ (live drift) | yes | fail (byte-stability) |

Findings:

- **The suggested command (`--shards 3`) cannot meet the speed guardrail.** Shards 1 and 2 are the search groups, so only one `validate-*` worker remains. README validation is paced at 0.35 s per client and dominates wall-clock time, so the gain was only 4–6%.
- **The suggested 300 s budget is too small.** A first run with it (W38) stopped the shard arm after 12 of 216 trending repos (`wall_clock_budget` and `work_redistributed` events). Its apparent 70% speedup was therefore incomplete work, and the verdict was `inconclusive`.
- **With three validation workers (`--shards 5`), the speed, API, and rate-limit guardrails pass**: about 64% faster, no API growth, and no secondary-rate-limit events at this scale.
- **Byte-stability cannot be proven by running live arms back to back.** In every run, both arms produced identical `full_name` sets and each was sorted correctly. The only differences were `stars`, `forks`, `pushed_at`, and `updated_at`, caused by live GitHub drift during the roughly 5 minutes between arms. Proving deterministic fan-in needs a record/replay harness, not two live crawls.
- **Local-token confound, now fixed.** With an SSO-bound OAuth token, SAML-enforcement 403s on `microsoft/*` READMEs were retried with 60 s backoff. That added about 14 minutes and 21 false rate-limit events to the baseline. Fixed in PR #804. A dropped-connection crash seen during the same runs was fixed in PR #803.

Why defer: the monolithic crawl already finishes in about 5.5 minutes, so the best-case saving is about 3.5 minutes per weekly run. That does not justify moving production to a threaded crawl before fan-in is proven byte-stable, particularly under the current production freeze.

Revisit only if crawl wall-clock becomes a real bottleneck. If that happens, first add a record/replay byte-stability check, then re-run with `--shards 5` or more from Actions using the production token type.
