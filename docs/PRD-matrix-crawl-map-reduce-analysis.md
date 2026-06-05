# PRD: Matrix Crawl and Map/Reduce Analysis for SquadScope

**Author:** Leela (Lead/Architect)  
**Date:** 2026-06-05  
**Status:** Draft  
**Type:** Product / Design Requirements Document  
**Depends on:** docs/analysis-spec.md, docs/pipeline-validation.md, .squad/decisions.md, scripts/analysis_gate.py  
**Inputs synthesized:** Bender matrix crawl findings, Farnsworth map/reduce analysis findings, Fry QA gates

---

## Executive Summary

SquadScope should not add a GitHub Actions crawl matrix by default yet. The recent implementation avoided matrix fan-out because the measured RSS work is already fast (about one second for five feeds) and the dominant crawl cost is GitHub API collection, which is constrained by cache behavior, Search API quota, and secondary-rate-limit risk. A matrix is not automatically faster; at current scale it can add runner setup, artifact fan-in, cache merge complexity, and rate-limit instability without improving the bottleneck.

This PRD recommends a staged architecture:

1. **Keep current crawl topology by default:** monolithic/cached GitHub crawl plus bounded in-process RSS fetching.
2. **Make crawl artifacts matrix-ready:** introduce shared run context, schema validation, deterministic fan-in contracts, checksums, source status, and metrics.
3. **Gate crawl matrix rollout by measurements:** RSS matrix only when source count/runtime/isolation triggers fire; GitHub matrix only after a shard experiment proves at least **25% crawl speedup**, no more than **10% API-call growth**, and no secondary-rate-limit regression.
4. **Adopt map/reduce as an analysis experiment, not a crawl-speed fix:** use mapper claim ledgers and a reducer/final writer to shrink LLM context, preserve citations, dedupe claims, resolve contradictions, and satisfy the existing analysis spec/gate.

The major product value is reliability and quality under growing evidence volume, not premature parallelism. Crawl fan-out should be evidence-triggered. Analysis map/reduce should be tested in dry-run/A-B mode before it can publish.

A completed live workflow run, `27030646485`, strengthens this prioritization. The crawl path was healthy (213 new repos, 236 trending repos, 455 GitHub API calls, about 4m30s main crawler), and external news was healthy (5/5 sources, 39 articles, 23 relevant, zero failures/dedupe, schema v2 telemetry/checksum present). The dominant risk moved downstream: analysis took about 28m41s, failed three Copilot gates, could not use the GitHub Models `openai/gpt-4o` fallback because access was unavailable, and ultimately succeeded only through no-AI fallback. Final token ledger input was about 112.9k versus about 74.3k at preflight, confirming that analysis duration, context growth, and fallback behavior now matter more than crawl parallelism.

---

## Problem Statement

The user asked why the team did not use a matrix to run the crawl faster, and whether a map/reduce technique could divide analysis into smaller parts to reduce LLM context.

Two concerns are related but distinct:

- **Crawl speed and reliability:** Can GitHub Actions matrix jobs fetch RSS or GitHub data faster than the current crawl?
- **Analysis context and quality:** Can the LLM analysis stage be decomposed into smaller, citation-preserving map outputs that a reducer combines into one coherent weekly summary?

The recent multi-source news implementation increased RSS coverage from one TechCrunch feed to five external sources, but the measured RSS stage remained about one second. Meanwhile the GitHub crawler still took roughly 4.5-6 minutes and used shared cache/rate-limit behavior. The completed run `27030646485` showed this path healthy: about 4m30s main crawler time, 455 API calls, 213 new repos, 236 trending repos, and a fully successful external-news artifact with 5/5 sources, 39 articles, 23 relevant, zero failures/dedupe, and schema v2 telemetry/checksum. Splitting the wrong work would increase complexity without reducing critical path. However, analysis input size is growing: raw GitHub JSON and external-news/correlation evidence can exceed tens of thousands of token-estimate before prompt instructions, learned state, and previous summaries are added. In the same completed run, final input tokens reached about 112.9k versus about 74.3k at preflight. That creates attention dilution, citation drift, structural gate failures, weaker editorial synthesis, and slow/repeated fallback behavior.

Therefore this PRD separates the decisions:

- **Crawl matrix:** justified only by measured runtime, source count, failure isolation, or GitHub shard experiment evidence.
- **Analysis map/reduce:** justified as an experiment to reduce per-call context, improve citation discipline, and keep final output compliant with `docs/analysis-spec.md` and `scripts/analysis_gate.py`.

---

## Goals & Non-Goals

### Goals

- **G1:** Explain why the recent crawl implementation did not use a matrix for speed.
- **G2:** Define measurable triggers and experiments for enabling RSS and GitHub crawl matrices.
- **G3:** Specify viable matrix/fan-out/fan-in designs for RSS and GitHub crawl while preserving canonical downstream artifacts.
- **G4:** Define an LLM analysis map/reduce architecture that divides work into smaller bounded contexts.
- **G5:** Define mapper and reducer contracts that preserve citations, dedupe claims, expose contradictions, and satisfy the existing analysis spec/gate.
- **G6:** Require observability for crawl legs, fan-in, mappers, reducers, fallbacks, token/cost behavior, and quality gates.
- **G7:** Provide rollout, QA gates, risks, mitigations, and acceptance criteria before any default-on change.

### Non-Goals

- Implementing the matrix or map/reduce pipeline in this PRD.
- Replacing the current canonical raw artifact paths by default.
- Replacing `docs/analysis-spec.md` or weakening `scripts/analysis_gate.py`.
- Letting mapper outputs become publishable article prose.
- Adding paid services, vector databases, or embedding infrastructure for the MVP.
- Publishing map/reduce output before evidence-contract validation, analysis gate pass, and human/editorial comparison.
- Matrixing GitHub crawl merely because matrix jobs are available.
- Treating article volume alone as proof of success.

---

## Current Baseline / Why No Matrix Yet

### Evidence from recent runs

Observed crawl timings and artifacts show:

| Run | Shape | Crawl job | Main GitHub crawl | RSS/news step | Output | API observations |
| --- | --- | ---: | ---: | ---: | --- | --- |
| Old run `26753498571 / 78847225991` | single TechCrunch feed | ~6m23s | ~5m58s | sub-second | 196 new repos, 238 trending repos, 20 TechCrunch articles / 7 relevant | 447 API calls; Search API min remaining 24/30; core remained high |
| New run `27026348186 / 79767247136` | five external RSS feeds, in-process parallel | ~5m08s | ~4m47s | ~1s | 213 new repos, 236 trending repos, 54 articles / 27 relevant | 455 API calls; Search API min remaining 24/30; core remained high |
| Completed run `27030646485 / 79781846313` | five external RSS feeds | full workflow success | ~4m30s | ~1s | 213 new repos, 236 trending repos; 39 articles / 23 relevant; 5/5 sources; 0 failures/dedupe; schema v2 telemetry/checksum present | 455 API calls; crawl healthy; analysis became dominant risk |

### Live-run analysis signal

Run `27030646485` did not reveal a crawler problem that needs a new crawler issue. Instead, it exposed analysis as the dominant risk:

- Analysis duration was about **28m41s**, much longer than the crawl critical path.
- Three Copilot analysis gates failed before fallback.
- GitHub Models fallback could not use `openai/gpt-4o` because access was unavailable.
- The no-AI fallback ultimately passed, preserving workflow success but reducing confidence in AI-generated editorial quality.
- The final token ledger was about **112.9k input tokens** versus about **74.3k preflight**, showing substantial context expansion after preflight.

This strengthens the map/reduce case: compaction, retry policy, gate-aware slicing, and provider fallback behavior should be prioritized before crawl matrix work. A focused analysis issue may be useful to track these fixes, but a new crawler issue is not warranted by this run.

### Why matrix was not used in the recent implementation

The decision was architectural and evidence-based:

1. **RSS was not the bottleneck.** Five-source RSS collection completed in about one second. A per-source matrix would repeat checkout, Python setup, dependency installation, artifact upload/download, and merge logic. That overhead is larger than the current RSS work.
2. **RSS is already parallelized in-process.** The newer RSS path uses bounded worker concurrency and writes one canonical external-news artifact. This is appropriate for a small number of I/O-bound feeds.
3. **GitHub API crawl is rate/cache constrained.** The GitHub crawler uses shared cache, shared token/rate-limit visibility, one star snapshot, and deterministic output. Splitting queries before measuring shard behavior risks Search API quota pressure, secondary-rate-limit regressions, duplicate candidates, cache conflicts, and incorrect star-gain semantics.
4. **Downstream contracts expect canonical artifacts.** `correlate.py`, `render_press_context.py`, analysis, rebuild mode, and publishing should not need to know whether collection was single-process or matrix-based.
5. **Matrix fan-out is not automatically faster.** If the slow part is GitHub API wait/backoff or cache misses, parallel jobs can simply exhaust quota faster and force serialized backoff.

### Current decision baseline

Default path remains:

```text
crawl-github (monolithic, cached, required)
    +
crawl-external-news (bounded in-process RSS, optional/degraded)
    -> canonical raw artifacts
    -> correlation / press context
    -> analysis
```

Future work should make the artifact boundary matrix-ready without changing default topology prematurely.

---

## Proposed Architecture

### Overview

```text
                         shared run context
                    week / since / until / run_id
                               │
              ┌────────────────┴────────────────┐
              │                                 │
     required GitHub crawl              optional RSS/news crawl
   monolith by default; shard         in-process by default; matrix
   experiment only behind gate        per source only behind gate
              │                                 │
              └──────────────┬──────────────────┘
                             ▼
                deterministic fan-in / validate
       canonical data/raw/{week}.json + {week}-external-news.json
                             │
                             ▼
                 deterministic preflight / slicing
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
       analysis mapper(s)            optional press/correlation mapper(s)
       claim ledgers only            claim ledgers only
              └──────────────┬──────────────┘
                             ▼
                reducer: dedupe / resolve / select
                             │
                             ▼
                  final writer: one coherent article
                             │
                             ▼
              analysis_gate.py + evidence-contract validation
```

### Matrix Crawl

#### Design principle

Matrix collection is allowed only when it improves a measured property: crawl p95, failure isolation, retry granularity, source-specific quota/credential isolation, or rebuild/debuggability. Matrix jobs must never commit or feed analysis directly. They write validated artifacts, and a fan-in job emits the canonical payload consumed downstream.

#### RSS matrix option

**When default path stays in-process:** current five-feed RSS collection, normal p95 below threshold, homogeneous RSS/HTTP behavior, no source-specific credentials or quotas.

**When RSS matrix is justified:** enable a per-source matrix only if one or more triggers fire:

- RSS/news stage p95 exceeds **60 seconds** across recent runs.
- Configured external source count exceeds **10**.
- A source needs independent credentials, quota policy, network isolation, retry policy, parser/runtime dependency, or failure semantics.
- A single flaky/slow source repeatedly forces rerunning the whole crawl job.
- Product requires per-source downloadable diagnostics even when the aggregate crawl degrades.

**RSS matrix design:**

1. A setup job computes a shared context: `run_id`, `week`, `since`, `until`, source config checksum, topic config checksum, and code SHA.
2. Matrix legs run one source per leg with `strategy.fail-fast: false`.
3. Each leg uploads exactly one artifact on `if: always()` containing either articles or a structured status/error payload.
4. A fan-in job downloads all source artifacts, validates schemas/checksums/window consistency, dedupes article URLs deterministically, records per-source status, and writes canonical `data/raw/{week}-external-news.json`.
5. Analysis consumes only the canonical merged artifact, never raw per-source artifacts.

#### GitHub matrix option

**When default path stays monolithic:** normal GitHub crawl p95 is acceptable, Search API remains tight, cache behavior is shared, star snapshot semantics remain global, or no shard experiment has proven benefit.

**When GitHub matrix is justified:** enable only after a no-publish shard experiment proves all of:

- At least **25% crawl wall-clock speedup** versus monolithic baseline, measured on comparable weekly windows.
- No more than **10% total GitHub API-call growth** versus baseline.
- No secondary-rate-limit regression: same or fewer secondary-limit events/backoff seconds.
- Search API quota remains above an agreed safety floor and is visible per shard.
- Same canonical raw output semantics: deterministic repo ordering, dedupe by `full_name`, stable star-gain/snapshot computation, and no downstream contract change.

**GitHub matrix designs considered:**

1. **Per query/category shard**
   - Shard by search query group: new repos, trending repos, topic primary queries, topic secondary queries.
   - Fan-in dedupes by `full_name`, applies final filtering, merges API/cache metadata, computes star gains once, and emits canonical raw JSON/snapshot.
   - Highest potential speedup, highest rate-limit/cache risk.

2. **Per candidate-processing shard after serialized search**
   - A monolithic setup/search step gathers candidate repo names, then matrix legs fetch/normalize repository details or README metadata.
   - Lower Search API risk because search remains centralized; possible speedup if core API details dominate.
   - Fan-in still owns deterministic filtering and snapshot semantics.

3. **Hybrid staged fan-out/fan-in**
   - Keep GitHub crawl monolithic initially.
   - Introduce explicit artifact validation/fan-in first.
   - Add correlation/analysis map/reduce after canonical artifacts.
   - Recommended migration path because it addresses context-size concerns without risky GitHub API fan-out.

### Map/Reduce Analysis

#### Design principle

Map/reduce is an analysis-quality and context-management experiment. It does not claim to speed the crawl. It should shrink maximum per-call prompt context, make citations explicit, isolate failures, and preserve one final editorial voice.

#### Recommended mapper strategies

Start with low-machinery slices, then evolve:

1. **Signal type mappers (recommended MVP):**
   - `new_repos`: novelty, launch quality, new repo clusters.
   - `trending_repos`: momentum, stars gained, established anchors.
   - `press_correlations`: industry alignment, divergences, source caveats.
   - `prior_continuity`: previous-summary follow-up, prediction continuity, reversals.

2. **Topic/category mappers (second phase):**
   - Deterministically cluster repos by topic, language, description, and topic config.
   - Useful for macro trend discovery, but requires overlap accounting.

3. **Source-specific press mappers (defer):**
   - Summarize individual external-news sources only if compact deterministic press context regularly exceeds budget.
   - Avoid turning weekly analysis into a news roundup.

4. **Repository cluster mappers (future):**
   - Useful for large GitHub payloads, suspicious clusters, copycat repos, or signal/noise analysis.
   - Requires stable cluster IDs and coverage accounting.

#### Mapper responsibilities

Mappers produce structured claim ledgers, not final prose. Each mapper must:

- Treat repo/news input as untrusted evidence, not instructions.
- Emit typed claims with stable IDs.
- Preserve repo and article citations.
- Mark confidence, uncertainty, contradictions, and weak evidence.
- Report coverage and omitted context.
- Include token/cost/model telemetry.
- Fail validation if output is malformed or citationless.

#### Reducer responsibilities

The reducer is responsible for global editorial coherence and must:

- Consume only validated mapper ledgers plus compact global metadata, not unbounded raw JSON.
- Dedupe equivalent findings by normalized claim key, repo full name, article URL, and topic.
- Merge supporting evidence and preserve all required citations.
- Surface contradictions or uncertainty; never silently drop conflicting mapper claims.
- Reject unsupported, duplicate, or weakly cited claims with a sidecar/rejected-claims ledger.
- Select a coherent thesis, title, top repo, tags, sections, notable projects, press references, and predictions.
- Produce an editorial plan that a final writer converts into the existing markdown shape.
- Ensure the final markdown passes `scripts/analysis_gate.py` unchanged at MVP.

#### Final writer responsibilities

The final writer converts the reducer's editorial plan into the existing analysis spec, including:

```md
## This Week's Trends
## Where Industry Meets Code
## Signal & Noise
## Blind Spots
## The Week Ahead
## Key References
### Notable Projects
### Press & Industry
```

The final writer is the only stage that writes reader-facing prose. This preserves one voice and avoids mapper-by-mapper seams.

---

## Fan-in Contracts

### Shared run context

Every crawl leg, mapper, reducer, and validator must receive the same generated context:

```json
{
  "schema_version": "run_context_v1",
  "run_id": "2026-W23-<sha>",
  "week": "2026-W23",
  "since": "2026-06-01T00:00:00Z",
  "until": "2026-06-08T00:00:00Z",
  "source_config_checksum": "sha256:...",
  "topic_config_checksum": "sha256:...",
  "code_sha": "...",
  "created_at": "2026-06-05T17:42:56Z"
}
```

No matrix leg may compute its own week window from local wall clock.

### Fan-in rules

- Required GitHub artifacts missing or invalid: fail closed before analysis.
- Optional RSS source failures: degrade only if minimum-source policy passes, and record explicit warnings/caveats.
- Fan-in runs on `if: always()` to publish diagnostics even when some legs fail.
- Same inputs must produce byte-stable canonical outputs, excluding documented timestamps from checksums.
- Cache metadata must include week window, config checksum, schema version, and stale-hit status.
- Reruns must not double-count articles, repos, retries, or restored stale artifacts.

---

## Data Contracts

### Crawl leg artifact

```json
{
  "schema_version": "crawl_leg_v1",
  "run_id": "2026-W23-<sha>",
  "week": "2026-W23",
  "since": "2026-06-01T00:00:00Z",
  "until": "2026-06-08T00:00:00Z",
  "leg_id": "rss:hugging-face-blog",
  "source_type": "rss|github_search|github_repo_details",
  "started_at": "ISO-8601",
  "finished_at": "ISO-8601",
  "duration_seconds": 1.23,
  "status": "success|failed|partial|skipped",
  "payload": {},
  "errors": [],
  "metrics": {
    "item_count": 9,
    "relevant_count": 4,
    "dedupe_count": 0,
    "api_calls": 0,
    "cache_hits": 0,
    "stale_cache_hits": 0,
    "retry_count": 0,
    "rate_limit_remaining": null,
    "rate_limit_resource": null
  },
  "checksum": "sha256:..."
}
```

### RSS source payload

```json
{
  "schema_version": "rss_source_v1",
  "week": "2026-W23",
  "source": "hugging_face_blog",
  "source_config_checksum": "sha256:...",
  "articles": [
    {
      "title": "Article title",
      "url": "https://example.com/article",
      "source": "Hugging Face Blog",
      "published_at": "2026-06-03T12:00:00Z",
      "summary": "Short retained summary",
      "categories": ["ai"],
      "github_links": ["https://github.com/owner/repo"],
      "relevance_score": 0.82
    }
  ],
  "source_status": {
    "status": "success|failed|partial",
    "attempts": 1,
    "timeout_seconds": 15,
    "duration_seconds": 0.7,
    "error_class": null,
    "error_message": null
  },
  "artifact_checksum": "sha256:..."
}
```

Fan-in emits canonical `data/raw/{week}-external-news.json` with stable metadata: `schema_version`, `sources_requested`, `sources_succeeded`, `sources_failed`, `sources_with_articles`, `dedupe_count`, `errors`, `source_status`, and checksum.

### GitHub shard artifact

```json
{
  "schema_version": "github_shard_v1",
  "week": "2026-W23",
  "crawl_window": {"since": "ISO-8601", "until": "ISO-8601"},
  "shard_id": "github:new-repos:q1",
  "query": "created:... stars:...",
  "query_type": "new|trending|topic_primary|topic_secondary|repo_details",
  "repos": [
    {
      "full_name": "owner/repo",
      "url": "https://github.com/owner/repo",
      "stars": 123,
      "stars_gained": null,
      "topics": ["ai"],
      "language": "Python",
      "pushed_at": "ISO-8601",
      "created_at": "ISO-8601",
      "fork": false,
      "template": false
    }
  ],
  "api_calls_used": 12,
  "cache_hits": 4,
  "stale_cache_hits": 0,
  "rate_limit": {
    "resource": "search",
    "limit": 30,
    "remaining": 24,
    "reset": "ISO-8601"
  },
  "partial_failures": [],
  "artifact_checksum": "sha256:..."
}
```

Fan-in remains responsible for dedupe, final ordering, significance filtering, cache metadata reconciliation, star snapshot/delta computation, and canonical `data/raw/{week}.json` shape.

### Analysis mapper output

```json
{
  "schema_version": "analysis_map_v1",
  "run_id": "2026-W23-<sha>",
  "week": "2026-W23",
  "shard_id": "signal-type:new-repos",
  "slice": {
    "strategy": "signal_type|topic|source|repo_cluster",
    "input_refs": ["data/raw/2026-W23.json#new_repos[0:50]"],
    "input_token_estimate": 12000,
    "repo_count": 50,
    "article_count": 0
  },
  "coverage": {
    "repo_ids_seen": ["owner/repo"],
    "article_urls_seen": [],
    "excluded_reason_counts": {"low_relevance": 3}
  },
  "findings": [
    {
      "claim_id": "stable-claim-id",
      "claim": "A concise evidence-bound claim.",
      "category": "trend|signal|noise|gap|press_correlation|press_divergence|continuity",
      "source_type": "github|news|mixed|prior_summary",
      "evidence_refs": [
        {
          "type": "repo",
          "ref": "owner/repo",
          "url": "https://github.com/owner/repo",
          "role": "anchor|supporting|counterexample",
          "evidence_note": "Why this supports or weakens the claim"
        }
      ],
      "repo_full_name": "owner/repo",
      "news_url": null,
      "confidence": 0.72,
      "contra_refs": [],
      "uncertainties": ["stars_gained unavailable"],
      "quality_flags": ["needs_reducer_review"]
    }
  ],
  "citations": [
    {"type": "repo", "url": "https://github.com/owner/repo", "title": "owner/repo"}
  ],
  "reference_candidates": {
    "notable_projects": ["owner/repo"],
    "press_articles": []
  },
  "token_estimate": 1800,
  "model": "copilot|github-models|none",
  "status": "success|failed|partial",
  "errors": []
}
```

### Reducer input

```json
{
  "schema_version": "analysis_reduce_input_v1",
  "run_id": "2026-W23-<sha>",
  "week": "2026-W23",
  "global_totals": {
    "repos_featured": 449,
    "stars_tracked": 123456,
    "new_repo_count": 213,
    "trending_repo_count": 236
  },
  "source_coverage": {
    "sources_requested": ["techcrunch", "github_blog"],
    "sources_succeeded": ["techcrunch"],
    "sources_failed": ["github_blog"]
  },
  "mapper_outputs": ["analysis_map_v1 objects"],
  "validation_summary": {
    "malformed_maps": 0,
    "missing_required_citations": 0,
    "week_mismatches": 0
  }
}
```

### Reducer output / editorial plan

```json
{
  "schema_version": "analysis_editorial_plan_v1",
  "title": "Final headline candidate",
  "summary": "One-sentence thesis",
  "top_repo": "owner/repo",
  "tags": ["ai", "developer-tools"],
  "selected_claims": [
    {
      "claim_id": "reducer-claim-id",
      "section": "This Week's Trends|Where Industry Meets Code|Signal & Noise|Blind Spots|The Week Ahead",
      "merged_from": ["mapper-claim-id-1", "mapper-claim-id-2"],
      "normalized_claim_key": "topic:agent-runtime-observability",
      "citation_bindings": {
        "repos": ["owner/repo"],
        "articles": ["https://example.com/article"]
      },
      "confidence": 0.81,
      "rationale": "Why this claim survived reduce"
    }
  ],
  "key_references": {
    "notable_projects": ["owner/repo"],
    "press_articles": ["https://example.com/article"]
  },
  "rejected_claims": [
    {"claim_id": "mapper-claim-id-3", "reason": "duplicate|unsupported|contradicted|weak_citation"}
  ],
  "contradictions": [
    {
      "claim_ids": ["a", "b"],
      "resolution": "surface_as_uncertainty|prefer_claim|reject_both",
      "rationale": "Evidence comparison"
    }
  ],
  "quality_notes": ["One source failed; press claims caveated"]
}
```

---

## Observability and Metrics

### Crawl metrics

Per crawl leg:

- `leg_id`, source name/type, status, start/end/duration.
- Item count, relevant count, dedupe count, artifact size, checksum.
- Cache hit/stale-hit count.
- API calls, rate-limit limit/remaining/reset/resource.
- Retry count, timeout count, error class/message.

Aggregate crawl:

- Required/optional leg counts.
- Failed/skipped/degraded leg counts.
- Merged artifact size/checksum.
- Total API calls and per-resource rate-limit status.
- Cache hit ratio and stale-cache usage.
- Fan-in validation result and deterministic checksum.

### Analysis metrics

Per mapper:

- Shard ID, input refs/checksums, input token estimate, output token estimate.
- Model/provider, duration, retries, status.
- Finding count, citation count, malformed citation count.
- Schema validation result and coverage counts.

Reducer/final writer:

- Input mapper count, failed/skipped mapper count.
- Duplicate claim count and contradiction count.
- Rejected/merged claim counts.
- Final prompt/output token estimates.
- Model/provider, duration, retry count.
- `analysis_gate.py` result and evidence-contract validation result.

Pipeline path:

- Selected path: `single-pass`, `map-reduce`, `github-models`, `no-ai`.
- Fallback reason, provider/model attempted, access/permission failures, and retry count.
- Copilot gate attempts/failures, GitHub Models fallback result, and no-AI fallback result.
- Preflight token estimate versus final token ledger, including unexplained growth.
- Analysis duration by attempt and total analysis wall-clock.
- Final publish eligibility.
- Human comparison score during A/B period.

### Thresholds to alert or block

- GitHub matrix experiment exceeds **10% API-call growth**.
- Secondary-rate-limit events/backoff increase versus baseline.
- RSS p95 exceeds **60 seconds**.
- Source count exceeds **10**.
- Single analysis prompt exceeds configured token budget.
- Final token ledger exceeds preflight by more than an agreed tolerance.
- Analysis duration or retry count exceeds configured budget.
- Copilot/GitHub Models gates repeatedly fail and no-AI fallback becomes the only passing path.
- Mapper/reducer total cost exceeds budget.
- Final reducer output loses required citations or fails `analysis_gate.py`.

---

## Rollout Plan

### Phase 0 — Baseline and contracts

- Record p50/p95 durations for GitHub crawl, RSS/news crawl, fan-in/correlation, press context rendering, and analysis across at least 5-10 runs.
- Define JSON schemas for crawl legs, RSS source artifacts, GitHub shards, mapper outputs, reducer input, and editorial plan.
- Add validators and fixture tests for deterministic merge and analysis contract validation.
- Keep current workflow behavior unchanged.

### Phase 1 — Fan-in dry-run

- Add a non-publishing fan-in validator that accepts current canonical artifacts and fixture per-source artifacts.
- Verify canonical outputs are byte-stable for same inputs.
- Add failure fixtures: missing optional RSS leg, malformed JSON, mismatched week, stale cache, duplicate URLs.

### Phase 2 — Analysis map/reduce dry-run

- Add feature-flagged/dry-run map/reduce path.
- Mappers emit claim ledgers only.
- Reducer emits editorial plan plus rejected-claims/conflicts sidecar.
- Final writer output is compared to current single-pass output but is not published.
- Existing single-pass/Copilot -> GitHub Models -> no-AI fallback remains source of truth.

### Phase 3 — A/B comparison

Run for at least four weekly cycles or equivalent replay fixtures:

- Compare gate pass rate.
- Compare citation preservation and unsupported-claim count.
- Compare max per-call token estimate, final ledger growth versus preflight, total cost/runtime, and retry/fallback count.
- Compare editorial quality: synthesis, specificity, skepticism, blind spots, and voice.
- Measure rerun stability: top repo and key reference overlap.

### Phase 4 — Controlled crawl matrix experiments

RSS experiment:

- Run RSS matrix as dry-run only when trigger threshold fires or via workflow dispatch.
- Compare runtime, artifact reliability, partial-source diagnostics, and merge determinism versus in-process RSS.

GitHub experiment:

- Run no-publish shard experiment with isolated caches and strict API/rate telemetry.
- Do not publish sharded output until fan-in matches monolithic canonical output semantics.
- Enable only if >=25% speedup, <=10% API-call growth, and no secondary-rate-limit regression.

### Phase 5 — Guarded default-on

- Start with workflow dispatch flag.
- Then scheduled dry-run.
- Then default-on for map/reduce only if acceptance criteria pass.
- Retain single-pass/no-AI fallback for at least one release cycle after default-on.
- Crawl matrix remains independently gated; map/reduce can ship without crawl matrix.

---

## QA Gates

### Crawl fan-out/fan-in gates

- All legs share one generated `run_id`, `week`, `since`, `until`, source config checksum, topic config checksum, and code SHA.
- Every leg uploads exactly one status/payload artifact on `if: always()`.
- Fan-in validates schema, checksum, source names, week/window consistency, and required fields.
- Same inputs produce byte-stable canonical artifacts.
- Optional RSS failures are visible and gated by minimum-source-success policy.
- Required GitHub failures fail closed.
- Reruns do not double-count repos/articles.
- Cache metadata prevents silent mixed-window or mixed-config artifacts.
- Downstream analysis consumes one canonical GitHub raw payload and one canonical external-news payload regardless of collection topology.

### Map/reduce gates

- Mapper output is structured JSON and schema-valid, not prose-only markdown.
- Each finding includes claim, evidence refs, confidence, category, source type, optional repo/news IDs, and `contra_refs`.
- Reducer rejects missing/malformed citations before final writer.
- Duplicate findings collapse without losing all citations.
- Contradictions are resolved with rationale or surfaced as uncertainty.
- Final markdown passes `scripts/analysis_gate.py` unchanged for MVP.
- Final repo mentions render as `[owner/repo](https://github.com/owner/repo)` and resolve to seen repo coverage.
- Final press claims cite retained article URLs.
- If map/reduce fails, pipeline falls back to existing single-pass/GitHub Models/no-AI path.

### Test matrix

| Area | Scenario | Expected result |
| --- | --- | --- |
| Shared context | Matrix legs receive generated week/window | Matching `week/since/until/run_id`; mismatch fails fan-in |
| Deterministic fan-in | Same fixture artifacts merged twice | Identical canonical bytes/checksum |
| Optional source failure | One RSS source times out | Canonical artifact records failure; publish can continue if minimum-source policy passes |
| Required GitHub failure | Required raw GitHub shard missing | Analysis blocked; failure notification path applies |
| Retry accounting | Optional RSS leg fails then succeeds on retry | Retry status recorded; no duplicate articles |
| Stale cache | Cache restored for wrong week/config | Rejected or marked unusable; no silent mixing |
| Rate limit | GitHub Search quota near floor | Shard experiment throttles/skips fan-out; no uncontrolled bursts |
| Mapper malformed output | Mapper emits prose or invalid JSON | Reducer rejects map artifact |
| Mapper failure | One required mapper fails | Retry/fallback; reducer cannot silently omit it |
| Duplicate claims | Same claim appears in two mappers | Reducer emits one claim with combined citations |
| Contradiction | One mapper says signal, another says noise | Reducer records resolution or uncertainty |
| Citation loss | Final claim lacks source refs | Evidence validation fails before publish |
| Over-budget context | Reducer input exceeds token budget | Hierarchical reduce or fallback before model call |
| Gate regression | Final markdown missing required heading | `analysis_gate.py` fails; fallback exercised |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Matrixing GitHub search increases rate-limit pressure | Slower or failed crawls | Require shard experiment, API-call cap, secondary-rate regression gate, central fan-in |
| RSS matrix adds overhead without speed benefit | More complexity, no runtime gain | Gate on p95/source count/isolation triggers; keep in-process default |
| Bad fan-in corrupts data | Duplicate repos/articles, wrong trends | Schema validation, deterministic ordering, checksums, fixture tests |
| Cache conflicts or stale cache mixing | Incorrect crawl results | Cache keys include week/window/config/schema; stale use observable and bounded |
| Mapper loses nuance/citations | Unsupported final claims | Claim ledger schema, citation validation, reducer rejected-claims sidecar |
| Reducer hides contradictions | Misleading analysis | Require contradiction ledger and explicit resolution/surfacing |
| Multiple LLM calls increase total cost | Higher spend despite smaller contexts | Token/cost ledger, budget preflight, A/B threshold before default-on |
| Editorial voice fragments | Patchwork article | Mappers never write final prose; final writer creates one coherent article |
| Partial mapper failure biases analysis | Missing source/category | Required/optional shard policy, retries, visible degraded state, fallback |
| Prompt injection through repo/news content | Unsafe instructions influence mapper | Keep untrusted evidence boundaries in every mapper/reducer prompt |

---

## Acceptance Criteria

### Crawl matrix acceptance

A crawl matrix may be enabled by default only when:

1. Baseline telemetry for current monolithic/in-process path is recorded.
2. Fan-in validates every shard schema/checksum before analysis.
3. Canonical downstream artifact paths remain unchanged.
4. Same shard inputs produce byte-stable canonical artifacts.
5. Optional RSS failures are reflected in metadata and downstream caveats.
6. Required GitHub failures fail closed unless an explicit partial-data policy is approved.
7. RSS matrix is triggered by source count/runtime/isolation need, not by default.
8. GitHub shard experiment proves >=25% wall-clock crawl speedup.
9. GitHub shard experiment keeps API-call growth <=10%.
10. GitHub shard experiment shows no secondary-rate-limit regression.
11. Existing crawl/correlation/press-context/rebuild tests remain green.
12. New tests cover schema validation, deterministic fan-in, duplicate handling, missing shard handling, stale cache rejection, and partial failure metadata.

### Map/reduce acceptance

The map/reduce analysis path may become publishable only when:

1. Given the same weekly raw GitHub JSON and compact press context, final markdown passes `scripts/analysis_gate.py`.
2. Every final repo mention resolves to preflight/mapper coverage and is rendered as a proper GitHub markdown link.
3. Every final press claim cites an article URL retained in source coverage or press context.
4. Reducer emits rejected-claims and contradictions sidecars for audit.
5. Duplicate claims collapse without losing citation provenance.
6. Contradictions are resolved with rationale or surfaced as uncertainty.
7. Final article has one editorial voice and satisfies the existing section/frontmatter shape.
8. Max per-call token estimate decreases materially versus the current single-pass prompt; target **>=30% max context reduction**.
9. Quality does not regress in human review against single-pass output.
10. Reruns on identical input are stable: same top repo or documented reason for change, and at least 70% overlap in selected key references.
11. Existing Copilot -> GitHub Models -> no-AI fallback path remains available until map/reduce beats current path on gate pass rate, citation coverage, and editorial review.

---

## Open Questions

1. What exact RSS p95 observation window should trigger matrix work: last 5 runs, last 10 runs, or rolling 30 days?
2. Should the RSS source-count trigger be exactly 10, or should it vary by source type/latency class?
3. What minimum RSS source success policy is acceptable for publishing: at least one source, majority of configured sources, or required source classes?
4. Which GitHub shard design should be tested first: per-query/category, serialized search plus parallel details, or another hybrid?
5. What Search API safety floor should block GitHub fan-out?
6. Should map/reduce mappers run as separate Actions jobs, subprocesses inside one job, or model calls orchestrated by one script?
7. What is the agreed per-run token/cost/runtime budget for map/reduce experiments?
8. What tolerance should be allowed between preflight token estimate and final token ledger before blocking or compacting?
9. Should evidence-contract validation live inside `analysis_gate.py` or remain a separate pre-gate validator initially?
10. How should hierarchical reduce trigger when reducer input is still over budget?
11. Who performs the human editorial comparison during the first four A/B runs?
12. Should a focused analysis issue track compaction, Copilot gate retries, GitHub Models access/fallback behavior, and no-AI fallback quality after run `27030646485`?

---

## Recommendation Summary

Do not matrix crawl by default now. RSS is too fast at current scale, and GitHub crawl is constrained by API/cache/rate behavior that needs proof before fan-out. Make crawl artifacts matrix-ready, then gate RSS matrix on source count/runtime/isolation triggers and GitHub matrix on a shard experiment proving >=25% speedup with <=10% API-call growth and no secondary-rate-limit regression.

Do experiment with analysis map/reduce. Run `27030646485` makes this the priority: crawl and external-news collection were healthy, while analysis duration, token growth, Copilot gate failures, unavailable `openai/gpt-4o` fallback access, and eventual no-AI success were the dominant risks. Use mapper claim ledgers and a reducer/final writer to reduce LLM context, preserve citations, dedupe claims, expose contradictions, and keep the final weekly summary compliant with the existing analysis spec and gate.
