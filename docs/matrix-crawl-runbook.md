# Matrix Crawl Operator Runbook

**Status:** Operational reference  
**Audience:** Pipeline operators, on-call engineers  
**Related issues:** #435, #436, #437, #438, #439

---

## Overview

This runbook covers how to trigger, monitor, and troubleshoot the SquadScope matrix crawl and map/reduce dry-run pipeline. The default crawl topology is monolithic (non-matrix). Matrix fan-out is opt-in and experimental.

---

## 1. Triggering a Crawl Run

### Scheduled (default)

The `crawl-and-publish.yml` workflow runs automatically on Sundays at 11:53 UTC (`53 11 * * 0`). Treat this as a best-effort GitHub-hosted schedule, not an exact start minute; scheduled runs can start hours late on shared runners. For the supported mitigation ladder (manual trigger, external scheduler -> `workflow_dispatch`, optional self-hosted runners), see [`docs/operator-guide.md#schedule-latency-and-mitigation-ladder`](operator-guide.md#schedule-latency-and-mitigation-ladder).

### Manual dispatch

Use the GitHub Actions UI or CLI:

```bash
# Normal monolithic crawl
gh workflow run crawl-and-publish.yml

# Dry-run mode (no publishing, safe for experiments)
gh workflow run crawl-and-publish.yml \
  -f run_mode=dry-run

# Map/reduce dry-run analysis path
gh workflow run crawl-and-publish.yml \
  -f run_mode=dry-run \
  -f analysis_path=map-reduce-dry-run

# Force refresh all sources (ignore same-day cache)
gh workflow run crawl-and-publish.yml \
  -f source_refresh_policy=force-refresh

# Restore a specific past week
gh workflow run crawl-and-publish.yml \
  -f run_mode=restore \
  -f rebuild_week=2026-W23 \
  -f source_run_id=26753498571
```

### Run modes

| Mode | Publishes? | Creates release? | Use case |
|------|:----------:|:----------------:|----------|
| `normal` | Yes | If gated | Weekly production run |
| `dry-run` | No | No | Testing changes, experiments |
| `candidate-only` | No | No | Map/reduce validation |
| `restore` | Yes | Optional | Rebuilding a past week |
| `force-replace` | Yes | Yes | Explicit re-publication |

### Analysis paths

| Path | Description | Publishes? |
|------|-------------|:----------:|
| `single-pass` | Current monolithic AI analysis (default) | Yes |
| `map-reduce-dry-run` | Experimental map/reduce scaffolding | Never |

---

## 2. Monitoring a Run

### Key artifacts to check

| Artifact | Location | Purpose |
|----------|----------|---------|
| `crawl-cache` | Actions artifact | GitHub API response cache |
| `raw-data` | Actions artifact (90 days) | Job transport, same-day reuse, and emergency recovery; not durable storage |
| Immutable raw store | `publish:data/raw-store/<week>/<source_run_id>/` | Durable source-bound payloads, hashes, and artifact provenance |
| `crawl-snapshots` | Actions artifact | Star/trending snapshots |
| Rerun mode summary | `data/diagnostics/rerun-mode.json` | Mode validation output |
| External news | `data/raw/{week}-external-news.json` | RSS crawl result |
| Map/reduce candidates | `data/candidates/map-reduce/` | Dry-run output (if enabled) |

### Metrics to watch (per #437)

- **Crawl duration:** GitHub crawl p95 target < 6 minutes
- **API calls:** Typical range 440–460 per run
- **Search API remaining:** Should stay ≥ 24/30 after crawl
- **Secondary rate limits:** Target: 0 events per run
- **RSS fetch time:** Target < 5s total for all sources
- **Source success rate:** Target ≥ 4/5 sources

### Checking run status

```bash
# List recent workflow runs
gh run list --workflow=crawl-and-publish.yml --limit 5

# View a specific run
gh run view <run-id>

# Download artifacts for inspection
gh run download <run-id> -n raw-data
```

---

## 3. Troubleshooting

### GitHub crawl failures

| Symptom | Likely cause | Action |
|---------|-------------|--------|
| Secondary rate limit (HTTP 403 with `retry-after`) | Too many concurrent API calls | Check if shard experiment is running; reduce parallelism |
| Search API quota exhausted | Excessive search queries | Wait for quota reset (resets per-minute); check for duplicate queries |
| Crawl timeout (>10 min) | Network issues or API degradation | Retry; check [githubstatus.com](https://githubstatus.com) |
| Cache miss storm | Config/code change invalidated cache | Expected on first run after changes; subsequent runs will rebuild cache |
| Empty results | Token permission issue | Verify `GITHUB_TOKEN` has `contents: read` and is not expired |

### RSS/News crawl failures

| Symptom | Likely cause | Action |
|---------|-------------|--------|
| Single source timeout | Upstream feed slow/down | Check source URL manually; feed will retry once by default |
| All sources failed | Network/DNS issue on runner | Check runner connectivity; retry the run |
| Schema validation failure | Feed format changed | Check `scripts/techcrunch_crawler.py` parsing logic against current feed |
| Deduplication anomaly | URL normalization issue | Check `GITHUB_URL_RE` and URL stripping logic |

### Fan-in validation failures

| Symptom | Likely cause | Action |
|---------|-------------|--------|
| Schema version mismatch | Mixed artifact versions | Ensure all legs use same code SHA (check `code_sha` in run context) |
| Checksum mismatch | Non-deterministic serialization | Check for floating-point ordering or timestamp injection in articles |
| Window mismatch | Leg computed own time | Verify all legs receive shared run context, not local `date` calls |
| Missing required artifact | GitHub shard crashed | Check individual shard job logs; fix and re-run |
| Minimum-source policy failed | ≥3 RSS sources down | Verify upstream feeds; consider temporary source list override |

### Map/reduce dry-run failures

| Symptom | Likely cause | Action |
|---------|-------------|--------|
| Missing raw JSON input | Crawl step didn't complete | Ensure crawl job succeeded before analysis |
| Mapper schema violation | Contract change | Compare mapper output against `MAP_SCHEMA` in `scripts/map_reduce_dry_run.py` |
| QA gate failure | Quality regression | Check `data/candidates/map-reduce/qa-report.json` for specific failures |
| Token budget exceeded | Input growth | Check preflight vs actual token counts; may need input slicing |

---

## 4. Operational Procedures

### Enabling RSS matrix mode (when triggers fire)

Prerequisites (per PRD triggers):
- RSS p95 > 60 seconds, OR
- Source count > 10, OR  
- Source needs independent credentials/isolation

Steps:
1. Create a feature branch
2. Modify workflow to add matrix strategy with `fail-fast: false`
3. Each leg runs one source, uploads per-source artifact
4. Add fan-in job that downloads all, validates, and merges
5. Test with `dry-run` mode first
6. Monitor metrics for 3+ runs before enabling for production

### Running a GitHub shard experiment (#435)

1. Trigger with `run_mode=dry-run` and shard configuration
2. Run baseline (monolithic) and shard variant on same week window
3. Compare: wall-clock time, API calls, rate-limit events, output stability
4. Document results in experiment report
5. Acceptance criteria: ≥25% speedup, ≤10% API growth, 0 rate-limit regression

### Recovering from a failed run

```bash
# 1. Check what failed
gh run view <run-id> --log-failed

# 2. If crawl cache is stale, force refresh
gh workflow run crawl-and-publish.yml \
  -f source_refresh_policy=force-refresh

# 3. If a specific week needs rebuilding
gh workflow run crawl-and-publish.yml \
  -f run_mode=restore \
  -f rebuild_week=2026-W23 \
  -f source_run_id=26753498571

# 4. If analysis failed but crawl succeeded, re-run from artifacts
gh run rerun <run-id> --failed
```

### Validating fan-in locally

```bash
# Run the deterministic map/reduce dry-run locally
python scripts/map_reduce_dry_run.py \
  --raw-json data/raw/2026-W23.json \
  --output-dir data/candidates/map-reduce/ \
  --current-datetime "2026-06-05T17:42:56Z" \
  --run-id "local-test"

# Verify canonical output is byte-stable
python scripts/map_reduce_dry_run.py \
  --raw-json data/raw/2026-W23.json \
  --output-dir /tmp/mr-verify/ \
  --current-datetime "2026-06-05T17:42:56Z" \
  --run-id "local-test"

diff data/candidates/map-reduce/ /tmp/mr-verify/
```

---

## 5. Escalation Path

1. **Self-serve:** Check this runbook and workflow logs
2. **Team:** Tag the issue with `squad:bender` (crawler) or `squad:fry` (tests/QA)
3. **Architecture:** Tag `squad:leela` for design decisions or contract changes
4. **External:** GitHub API issues → check [githubstatus.com](https://githubstatus.com); RSS feed issues → check upstream provider status

---

## References

- Workflow: [`.github/workflows/crawl-and-publish.yml`](../.github/workflows/crawl-and-publish.yml)
- Fan-in contracts: [`docs/matrix-crawl-fan-in-contracts.md`](matrix-crawl-fan-in-contracts.md)
- PRD: [`docs/processed/PRD-matrix-crawl-map-reduce-analysis.md`](processed/PRD-matrix-crawl-map-reduce-analysis.md)
- Operator guide: [`docs/operator-guide.md`](operator-guide.md)
- Pipeline validation: [`docs/pipeline-validation.md`](pipeline-validation.md)
