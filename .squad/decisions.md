# Fry: quality gate fallback hardening


---

# Leela — PR review gate follow-up

- Date: 2026-06-01
- Context: Round review of PR #218 and PR #219 showed both branches were opened by `jmservera`, which means the current GitHub identity cannot submit an approving review on them.
- Decision: Do not bypass the review gate on self-authored pull requests. Treat independent approval as still required before merging branches opened by the same account Leela is operating under.
- Why: GitHub blocks self-approval, and preserving the review gate matters more than forcing a merge from the lead seat.

# Amy — Topic buttons follow-up

- Date: 2026-06-01
- Context: Issue #216 mobile topic buttons regression
- Proposal: Keep topic discovery centered on `/topics/`, remove the global header topic shortcut strip, and hide per-report topic chips on screens up to 768px while leaving desktop topic browsing available through the homepage rail and Topics page.
- Why: The repeated chip rows were consuming too much vertical space on mobile and duplicated navigation that already exists in the primary menu.

---

# Fry: quality gate fallback hardening


---

# Fry — generate-step failure handling


---

# Amy — Share button implementation


---

# Farnsworth — Hindsight validation decision


---

# Fry — Generate-step failure handling


---

# Farnsworth hindsight validation decision


---

# Fry QA triage decision


---

# Leela: Close unverifiable W23 growth execution


---

# Fry PR #236 QA Review


---

# Hermes security review — PR #236 external RSS feeds


---

# PR #236 security unblock


---

# Bender — Crawler parallelism analysis


---

# Farnsworth: LLM input strategy for multi-source news


---

# Fry QA: crawler reliability and performance next iteration


---

# Leela — crawler next-iteration issue


---

# Bender PR #236 Security Fix

## Context
Hermes blocked PR #236 because config-driven external RSS sources were fetched directly without egress URL validation or explicit per-request timeouts.

## Decision
External news RSS source configs now require HTTPS URLs whose host is in the approved feed allowlist, with credentials, local/private/link-local targets, and unexpected ports rejected before crawl. Fetching now goes through `urllib.request.urlopen` with an explicit bounded timeout before handing bytes to `feedparser`, while retaining the existing config-driven source list and bounded in-process worker pool.

## Validation
Added tests for invalid/unapproved URL rejection and explicit fetch timeout propagation. Ran `PYTHONPATH=. .venv/bin/python -m pytest tests -q` with 563 passing tests.

---

---

# Leela — Issue 234 external news source architecture


# Fry — Issue #238 notify triage


---

# Leela PR #241 Review — Idempotent Weekly Release Notify

- Date: 2026-06-05
- Context: Issue #238 showed a real rerun failure in `notify`: `gh release create week-2026-W23` returned HTTP 422 because the weekly release already existed.
- Decision: Keep weekly release notification idempotent by resolving the weekly tag first, editing an existing `week-*` release with `gh release edit`, and creating only when no release exists.
- Review result: Approved in substance. Formal GitHub approval was blocked because the authenticated account is the PR author, so Leela posted an explicit lead approval comment instead of bypassing the review gate.
- Validation: `tests/test_pipeline.py` passed locally (9 tests), full `tests` passed locally (563 tests), CodeQL checks were green, and Copilot PR review completed with no comments.
- Merge gate: Do not merge from this account until the repository's independent-review requirement for `jmservera`-authored PRs is satisfied.
- PR #241 merged at 2026-06-05T17:21:05Z, closing issue #238.

---

---

# Bender issue #237 implementation


---

# Bender PR #242 Copilot Review Fixes

- Keep category/project-name-only press matches weak even when temporally spiking or corroborated by multiple articles/sources.
- Pass both `--since` and `--until` from the crawl workflow to preserve deterministic canonical `crawl_window` metadata.
- Record bounded fetch attempts and timeout telemetry on `NewsFeedSource` even when `fetch_feed()` raises before returning a feed.
- Keep press-context article lookup comments aligned with the actual URL-to-title mapping.
- PR #243 merged at 2026-06-05T17:34:18Z.

---

---

# Leela PR #243 Review

- Verdict: approved in substance after independent lead review.
- Scope checked: issue #237 acceptance criteria follow-up, PR #242 Copilot comments, PR #243 diff, tests, CodeQL, Copilot review state.
- Local validation: clean PR worktree ran `pytest tests -q` with 574 passed.
- Formal GitHub approval blocked: the active account is the PR author and GitHub rejected own-PR approval.
- Merge gate: wait for an independent non-Bender reviewer/approval unless repository policy explicitly permits merge with the lead approval comment.

---

---

### 2026-06-05T17:06:31.753+00:00: User directive — Copilot Review Asynchronous Gate

**By:** jmservera (via Copilot)
**What:** Copilot Review is asynchronous. Before merging a PR, check whether Copilot is still reviewing and do not merge until the review has finished and any review comments are handled.
**Why:** User request — captured for team memory

---

# Bender input — crawl matrix and map/reduce PRD


# Farnsworth — PRD input: LLM analysis map/reduce

Date: 2026-06-05T17:42:56.819+00:00
Requested by: jmservera

## Recommendation

Adopt a staged map/reduce design for the **LLM analysis stage**, but do not start by splitting the raw crawl job into a GitHub Actions matrix for speed alone. Existing evidence says RSS collection is already fast and in-process parallelized, while the GitHub crawl dominates crawl runtime. The stronger reason for map/reduce is **analysis quality and reliability under context pressure**: smaller mapper calls can extract cited, typed claims from bounded evidence windows, and one reducer can preserve the weekly editorial voice and final `docs/analysis-spec.md` contract.

Initial PRD should target an experimental path behind a feature flag or dry-run workflow, with deterministic compaction and validation before any generated weekly summary becomes publishable.

## Current context pressure

Current weekly analysis input is already large before the model writes anything:

- GitHub raw crawl is the dominant payload. The W23 multi-source run recorded in `.squad/decisions.md` produced `213` new repos and `236` trending repos, roughly `296 KB` / `74k` token-estimate in raw GitHub JSON.
- External news expanded from one TechCrunch feed to five sources. W23 external news was `54` articles / `27` relevant articles, roughly `45.5 KB` / `11.4k` token-estimate.
- Rendered press context is intentionally capped by `scripts/render_press_context.py` at an `8k` token-estimate budget, but prompt-mode output can still include ranked articles, correlations, divergences, caveats, and telemetry.
- The weekly prompt itself injects raw JSON, previous summary, `.squad/identity/wisdom.md`, all `.squad/skills/**/*.md`, analysis instructions, security constraints, and optional press context. This overhead competes with repo evidence for attention.
- `analysis_gate.py` is structural: it enforces frontmatter, required headings, word count, placeholder/raw JSON bans, quality score, dates, and repo format. It does not yet validate intermediate faithfulness, mapper contradictions, or claim-level citation integrity.

The current failure mode is not only token overflow. It is attention dilution: long raw inputs encourage listing, citation drift, missed required headings, weak press/repo correlation claims, and generic summaries. A map/reduce design should reduce evidence windows and force explicit claim contracts before final prose.

## Why a matrix was not used for the crawl

The previous crawler analysis supports not using an Actions matrix yet for RSS/source crawling:

- New five-source RSS collection took about one second in the observed run; GitHub repo crawl remained about 4m47s.
- `scripts/techcrunch_crawler.py` already uses bounded in-process parallel source fetching in the newer pipeline.
- Matrix jobs would add checkout/setup/artifact/merge overhead and commit-race complexity without addressing the actual bottleneck.
- A matrix becomes justified when source count, source heterogeneity, source-specific credentials/quotas, or p95 external collection latency materially increases.

For the PRD, separate **crawl parallelism** from **analysis decomposition**. Matrix crawl is a future topology decision; map/reduce analysis is an editorial reliability strategy.

## Candidate map strategies

### 1. By editorial topic/category

Mappers receive repo slices clustered by topics, languages, descriptions, and prior-week continuity hints. They produce candidate trends, noise patterns, blind spots, and key repos.

Pros:
- Matches final article structure: macro trends and gaps.
- Good for discovering cross-repo patterns inside bounded themes.

Cons:
- Topic overlap can duplicate repos or split one trend across mappers.
- Requires deterministic cluster IDs and repo membership to avoid inconsistent claims.

Best use: primary mapper strategy after deterministic clustering.

### 2. By signal type: new, trending, news/correlation, prior continuity

Separate mappers handle:
- `new_repos`: novelty and launch quality.
- `trending_repos`: momentum and established anchors.
- press/correlation artifact: industry alignment/divergence.
- prior summary/history: continuity, reversals, and prediction follow-up.

Pros:
- Mirrors current input sources and reduces per-call context sharply.
- Easier citation provenance because each mapper owns one evidence type.

Cons:
- Final trends often require combining new + trending + press evidence.
- Reducer needs stronger dedupe and conflict logic.

Best use: strong baseline because it requires little new clustering machinery.

### 3. By source

Mappers summarize each external source or source family, preserving source name, URL, article title, date, relevance score, and correlation confidence.

Pros:
- Keeps source provenance clear.
- Prevents TechCrunch/GitHub/NVIDIA/MIT/HF from becoming one flattened press voice.

Cons:
- Risk of over-weighting press summaries in a GitHub-first analysis.
- More LLM calls for relatively small article volume.

Best use: only if relevant article volume exceeds the compact press-context budget or source mix becomes heterogeneous.

### 4. By repository clusters

Deterministically shard repos into clusters by embedding/topic/language/owner/fork-star anomaly patterns, then map each cluster.

Pros:
- Handles large GitHub raw payloads directly.
- Can isolate suspicious clusters such as fork inflation, star farming, exploit churn, or copycat agent repos.

Cons:
- Needs stable clustering and coverage accounting.
- Cluster labels may be misleading if generated by LLM without deterministic support.

Best use: second iteration once signal-type mapping proves useful.

### 5. Source-specific press summaries before main reduce

A deterministic or LLM-assisted press mapper compresses external news into source-aware press claims, then the main reducer joins those claims with repo claims.

Pros:
- Strong citation preservation if contract is strict.
- Keeps `Where Industry Meets Code` from becoming a news roundup.

Cons:
- Adds hallucination/citation drift risk if source summaries are LLM-generated.
- Current compact deterministic press-context path may be enough.

Best use: defer unless `*-external-news.json` regularly breaches press context budget.

## Recommended architecture

### Phase 0 — deterministic preflight

Inputs:
- sanitized weekly raw JSON,
- compact press context from `*-external-news.json` + `*-correlations.json`,
- previous summary,
- wisdom/skills bundle,
- analysis spec and gate constraints.

Preflight outputs:
- token estimates per input segment,
- repo coverage counts and star totals,
- source coverage counts/errors,
- deterministic clusters or slices,
- stable IDs for repos, articles, and candidate evidence groups.

### Phase 1 — mappers produce claim ledgers, not prose articles

Each mapper receives a bounded evidence slice and returns a strict JSON/markdown-ledger contract. Mappers should not write final publication prose or frontmatter. They should extract:

- candidate trend claims,
- signal/noise/gap judgments,
- evidence repo IDs and article IDs,
- confidence and uncertainty,
- citation URLs,
- contradiction flags,
- suggested `Key References` candidates,
- token usage/coverage telemetry.

### Phase 2 — reducer creates one coherent editorial plan

Reducer consumes only mapper ledgers plus compact global metadata. It:

- deduplicates candidate claims by normalized claim key/topic/repo/article URL,
- merges supporting evidence across mappers,
- rejects weak unsupported claims,
- resolves contradictions by evidence strength and citation quality,
- selects 3-5 macro trends, 2-4 correlations/divergences, 2-4 blind spots, 5-10 repo references, and 3-5 press references,
- chooses `title`, `top_repo`, `tags`, `quality_score`, and optional `predictions`,
- emits an editorial outline with citation bindings.

### Phase 3 — final writer/gate

Final writer converts the reducer plan into the exact `docs/analysis-spec.md` output shape:

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

Then `scripts/analysis_gate.py` runs unchanged at first, with future enhancements for evidence/citation checks.

## Reducer responsibilities for global coherence

The reducer is the only stage allowed to create final reader-facing prose. It must:

- preserve one editorial voice and avoid mapper-by-mapper seams;
- maintain a single global thesis and title;
- avoid duplicate claims by normalizing repo full names, article URLs, topic labels, and claim keys;
- keep every repository mention renderable as `[owner/repo](https://github.com/owner/repo)`;
- keep every press claim backed by retained article citations;
- distinguish strong correlations from weak/category/fuzzy matches;
- retain source caveats from external-news metadata;
- keep `repos_featured` and `stars_tracked` tied to deterministic preflight totals rather than mapper estimates;
- satisfy `analysis_gate.py` frontmatter/headings/body constraints.

## Concrete mapper output contract

Suggested `analysis_map_v1` object:

```json
{
  "schema_version": "analysis_map_v1",
  "week": "YYYY-WNN",
  "slice": {
    "id": "signal-type:new-repos",
    "strategy": "signal_type|topic|source|repo_cluster",
    "input_token_estimate": 12000,
    "repo_count": 42,
    "article_count": 0
  },
  "coverage": {
    "repo_ids_seen": ["owner/repo"],
    "article_urls_seen": ["https://example.com/article"],
    "excluded_reason_counts": {"low_relevance": 3}
  },
  "claims": [
    {
      "claim_id": "stable-hash-or-slug",
      "claim_type": "trend|signal|noise|gap|press_correlation|press_divergence|continuity",
      "headline": "Short claim label",
      "summary": "One or two sentences, evidence-bound.",
      "evidence_repos": [
        {
          "full_name": "owner/repo",
          "url": "https://github.com/owner/repo",
          "role": "anchor|supporting|counterexample",
          "stars": 123,
          "stars_gained": null,
          "evidence_note": "Why this repo supports the claim"
        }
      ],
      "evidence_articles": [
        {
          "title": "Article title",
          "url": "https://example.com/article",
          "source": "TechCrunch",
          "published_at": "2026-06-01",
          "role": "corroborates|diverges|context",
          "correlation_strength": "strong|weak|none"
        }
      ],
      "confidence": 0.72,
      "uncertainties": ["stars_gained missing for most trending repos"],
      "quality_flags": ["possible_duplicate", "weak_citation", "needs_reducer_review"]
    }
  ],
  "reference_candidates": {
    "notable_projects": ["owner/repo"],
    "press_articles": ["https://example.com/article"]
  }
}
```

## Concrete reducer input/output contract

Reducer input:

```json
{
  "schema_version": "analysis_reduce_input_v1",
  "week": "YYYY-WNN",
  "run_datetime": "ISO-8601",
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
  "maps": ["analysis_map_v1 objects"]
}
```

Reducer output should be an editorial plan before prose:

```json
{
  "schema_version": "analysis_editorial_plan_v1",
  "title": "Punchy headline",
  "summary": "One-sentence thesis",
  "top_repo": "owner/repo",
  "tags": ["ai", "developer-tools", "security"],
  "selected_claims": [
    {
      "claim_id": "...",
      "section": "This Week's Trends|Where Industry Meets Code|Signal & Noise|Blind Spots|The Week Ahead",
      "merged_from": ["mapper-claim-id"],
      "citation_bindings": {
        "repos": ["owner/repo"],
        "articles": ["https://example.com/article"]
      }
    }
  ],
  "key_references": {
    "notable_projects": ["owner/repo"],
    "press_articles": ["https://example.com/article"]
  },
  "rejected_claims": [
    {"claim_id": "...", "reason": "duplicate|unsupported|contradicted|weak_citation"}
  ],
  "quality_notes": ["Caveat missing stars_gained in trend section"]
}
```

The final writer then emits only markdown conforming to the existing spec.

## Risks

- Mapper contradiction: two mappers may classify the same repo as signal and noise. Reducer needs explicit conflict resolution and rejected-claim logging.
- Citation drift: if mappers paraphrase article claims without preserving URLs/source/date, the final summary may cite the wrong article or overstate correlation.
- Duplicate claims: topic and signal-type mappers may independently discover the same pattern.
- Quality gate complexity: structural gate is simple today; claim-ledger validation, citation coverage, and contradiction checks add test and maintenance burden.
- Cost/token growth: multiple smaller LLM calls can exceed one large call if slices overlap or include repeated instructions/history.
- Runtime: parallel mapper calls help wall-clock time only if model/API concurrency is available and reliable.
- Editorial voice loss: mapper prose can create a patchwork article unless final prose is written by one reducer/writer pass.
- Over-pruning: small slices may miss weak cross-cluster patterns that only appear globally.
- Failure policy: partial mapper failure could bias coverage unless reducer sees missing-slice telemetry and either degrades explicitly or falls back.
- Prompt injection surface: every mapper still ingests untrusted repo/news text and must keep untrusted-content boundaries.

## Evaluation metrics

### Token and runtime metrics

- Total prompt token-estimate by stage: preflight, each mapper, reducer, final writer.
- Maximum per-call token-estimate and p95 per-call token-estimate.
- Total generated tokens and total model calls.
- End-to-end wall-clock time versus current single-call path.
- Cost per successful weekly analysis and cost per fallback/retry.

### Quality and faithfulness metrics

- `analysis_gate.py` pass rate.
- Required section/headings/frontmatter pass rate.
- Citation coverage: percentage of repo/article claims with retained citations.
- Claim support: percentage of final claims traceable to mapper evidence IDs.
- Hallucination/unsupported-claim count from automated or human review.
- Duplicate claim count before/after reduce.
- Contradiction count and reducer resolution rate.
- Press correlation accuracy: strong vs weak labels preserved correctly.
- Editorial quality score from Farnsworth/Leela rubric: synthesis, specificity, skepticism, blind spots, and voice.

### Stability metrics

- Rerun stability: overlap in selected top trends/repos/press references across repeated runs with same inputs.
- Title/top_repo stability across repeated runs.
- Sensitivity to mapper ordering.
- Missing-slice degradation behavior.

## Non-goals for initial PRD

- Do not replace the weekly `docs/analysis-spec.md` output contract.
- Do not make each mapper produce publishable prose.
- Do not split the crawl into an Actions matrix as part of the analysis map/reduce MVP unless separate performance evidence justifies it.
- Do not include raw article dumps or raw correlation dumps in final analysis prompts.
- Do not let weak/category-only correlations become strong claims without corroboration.
- Do not optimize for maximum recall at the expense of citation integrity and editorial judgment.
- Do not require new paid services, embeddings infrastructure, or vector databases for MVP.
- Do not publish map/reduce output until it passes the existing gate and a new evidence-contract validator.

## Guardrails for MVP

- Feature flag the map/reduce path; preserve the current single-call/fallback path.
- Keep deterministic preflight totals authoritative for `repos_featured`, `stars_tracked`, source status, and citation inventories.
- Wrap all repo/news evidence as untrusted data in every mapper prompt.
- Limit mapper output to structured claims with evidence IDs, not final prose.
- Run final `analysis_gate.py` unchanged initially, then add a separate mapper/reducer contract validator.
- Require a human review comparison against the single-call output for the first several weeks.
- Treat no-AI/data-only fallback as the terminal reliability fallback if mapper/reducer calls fail.

## Acceptance criteria

1. Given the same weekly raw GitHub JSON and compact press context, the map/reduce experiment produces a final markdown summary that passes `scripts/analysis_gate.py`.
2. Every final repo mention resolves to a repo seen in preflight or mapper coverage and is rendered as a proper GitHub markdown link.
3. Every final press claim cites an article URL retained in source coverage or press context.
4. The reducer emits a rejected-claims/conflicts ledger for audit, even if not published.
5. The final article contains 3-5 coherent macro trends, explicit signal/noise judgment, useful blind spots, and a single editorial voice.
6. The map/reduce path demonstrates lower max per-call token-estimate than the current single-call prompt, with measured total cost/runtime reported.
7. Reruns on identical input are stable enough for publication: same top_repo or documented reason for change, and at least 70% overlap in selected key references.
8. Partial mapper failure either retries that slice or marks the final output as degraded; it must not silently omit a source/category.
9. Existing single-call and no-AI fallback paths remain available until map/reduce beats them on gate pass rate, citation coverage, and human editorial review.

---

# Fry QA input — matrix crawl + map/reduce analysis PRD

Date: 2026-06-05T18:15:23Z
Requested by: jmservera
Owner: Fry / QA

## QA position

A matrix is not automatically faster for the current crawl. Prior evidence shows the external RSS stage is about one second, while GitHub search/repo crawling dominates and already approaches the tighter Search API budget. The PRD should treat matrix crawl as a measured experiment: first make artifacts merge-ready and deterministic, then fan out only workloads with independent latency, retry, and quota profiles.

Map/reduce analysis is worth ideating because it can shrink per-model context and isolate failures, but it must not weaken the existing analysis contract. The reducer's final markdown must still pass `scripts/analysis_gate.py`, preserve repo/news citations, produce the current frontmatter shape, and keep the existing Copilot -> GitHub Models -> no-AI fallback path viable.

## PRD-ready QA gates

### 1. Matrix crawl fan-out/fan-in

Required gates before default-on:

- **Deterministic run context:** every leg receives the same `week`, `since`, `until`, source config revision, topic config revision, and run id. No leg may compute its own week window from local wall clock except via a shared generated context artifact.
- **Per-leg artifact contract:** each leg writes exactly one JSON artifact with `{schema_version, run_id, week, since, until, leg_id, source_type, started_at, finished_at, duration_seconds, status, payload, errors, metrics, checksum}`.
- **Fan-in determinism:** merge output must be byte-stable for the same inputs: canonical ordering, deterministic dedupe keys, stable error ordering, and a checksum recorded in metadata.
- **Partial failure semantics:** required legs fail the workflow; optional legs degrade with explicit `status=failed` artifacts and a minimum-source-success gate.
- **Retry behavior:** retry only failed optional legs when possible; fan-in must distinguish first-attempt failure, retry success, and terminal failure. A rerun must not double-count articles/repos.
- **Cache consistency:** cache keys include query/source config, week window, and schema version. Stale cache use must be marked in metadata and never silently mix different windows.
- **Rate-limit safety:** GitHub-query fan-out must be capped by search quota remaining and secondary-rate-limit backoff. RSS/API legs need per-host concurrency limits and timeout/retry ceilings.
- **Artifact compatibility:** downstream analysis consumes one canonical raw payload and one canonical external-news payload regardless of matrix vs single-process collection.

### 2. Map/reduce analysis

Required gates before default-on:

- **Mapper schema validation:** each mapper emits structured JSON, not prose-only markdown: `{schema_version, run_id, week, shard_id, input_refs, findings[], citations[], token_estimate, model, status, errors}`.
- **Finding shape:** each finding includes `claim`, `evidence_refs`, `confidence`, `category`, `source_type`, `repo_full_name?`, `news_url?`, and `contra_refs[]`.
- **Citation preservation:** reducer must be able to trace every final claim to repo URLs, raw payload paths, and news URLs. Missing or malformed citations fail reducer validation.
- **Reducer behavior:** reducer must dedupe equivalent findings, surface contradictions instead of hiding them, prefer higher-confidence/evidence-backed findings, and record rejected/merged finding IDs in a sidecar.
- **Contradiction tests:** contradictory mapper outputs must either resolve with documented rationale or appear in the final analysis as uncertainty/blind spot; they must not disappear silently.
- **Duplicate tests:** duplicate repo/news claims across shards must collapse to one final claim without losing all citations.
- **Gate compatibility:** final markdown must pass `analysis_gate.py` unchanged unless the PRD explicitly extends the gate. Frontmatter, headings, week/date, predictions, and no-placeholder rules still apply.
- **Fallback compatibility:** if any map/reduce stage cannot produce a valid final summary, the pipeline must still try the current single-pass/GitHub Models/no-AI fallback path.

## Test matrix

| Area | Scenario | Expected QA outcome |
| --- | --- | --- |
| Crawl context | All legs receive shared generated week window | Artifacts have identical `week/since/until/run_id`; mismatch fails fan-in |
| Crawl determinism | Same fixture artifacts merged twice | Identical merged JSON bytes/checksum |
| Crawl optional failure | One RSS/source leg times out | Workflow continues if minimum source threshold met; error recorded; analysis sees canonical artifact |
| Crawl required failure | GitHub raw repo leg fails | Analyze does not run; notify-failure path catches pipeline failure |
| Crawl retry | Failed optional leg succeeds on retry | Final metadata records retry count and no duplicate payload entries |
| Crawl cache | Stale cache restored for wrong week/config | Fan-in rejects or marks unusable; no silent mixed-window output |
| Crawl rate limit | Search quota near floor | GitHub fan-out throttles or skips risky fan-out; no uncontrolled parallel search bursts |
| No news data | External-news artifact absent or empty | Press context says no press data; analysis gate can still pass |
| Mapper schema | Mapper emits malformed JSON/prose | Reducer rejects mapper artifact and records mapper failure |
| Mapper failure | One mapper exits non-zero | Required shard fails workflow or optional shard degrades by configured policy; reducer cannot silently omit |
| Duplicate findings | Same repo trend in two shards | Reducer emits one finding with combined citations |
| Contradictions | One mapper says trend is signal, another says noise | Reducer records rationale or uncertainty; contradiction sidecar includes both sources |
| Citation loss | Reducer final claim lacks source refs | Reducer validation fails before `analysis_gate.py` |
| Over-budget context | Single reducer input exceeds token budget | Reducer switches to hierarchical reduce or fails to fallback before spending unbounded tokens |
| Week mismatch | Mapper output `week` differs from raw payload | Reducer rejects artifact |
| Token spike | Mapper/reducer token estimate exceeds budget threshold | Dry-run blocks default path; metrics identify model/stage/shard |
| Gate regression | Final summary missing heading or generic title | Existing `analysis_gate.py` fails and fallback path is exercised |

## Failure modes to require in PRD

- One matrix leg fails: fan-in runs with `if: always()` for diagnostics, but publish/analyze only continue if required artifacts exist and optional-source thresholds pass.
- One mapper fails: reducer must not hide it; either fail the map/reduce path or explicitly degrade based on shard criticality, then fallback to single-pass/no-AI if final gate fails.
- No news data: treated as valid degraded input, not a crash; final summary uses existing "No press data" behavior.
- Over-budget context: preflight estimates for each mapper, reducer, and aggregate final prompt; hard fail or hierarchical reduce before model invocation.
- Stale cache: cache metadata includes created_at, week window, source config checksum, and schema version; stale use is observable and bounded.
- Inconsistent week windows: fan-in/reducer reject mixed `week/since/until` artifacts.
- Token/cost spikes: per-shard and total token ledger records estimates/actuals; alert if p95 or per-run cost exceeds threshold.

## Observability requirements

Minimum notices/metrics per run:

- Per crawl leg: `leg_id`, source name/type, status, start/end/duration, item count, relevant count, dedupe count, artifact size, checksum, cache hit/stale hit, API calls, retry count, error class.
- Aggregate crawl: required/optional leg counts, failed leg counts, merged artifact size/checksum, total API calls, rate-limit remaining/reset/resource, cache hit ratio.
- Per mapper: shard id, input artifact refs/checksums, prompt size, token estimate/actual, model/source, duration, output size, finding count, citation count, quality/schema validation result.
- Reducer: input shard count, failed/skipped shard count, duplicate count, contradiction count, final prompt/output tokens, duration, model/source, final quality gate result.
- Pipeline path: selected path (`single-pass`, `map-reduce`, `github-models`, `no-ai`), fallback reason, and final `analysis_gate` outcome.

## Rollout plan and acceptance thresholds

1. **Design-only contract:** define artifact schemas and validators; do not change default workflow path.
2. **Local fixture dry-run:** run fan-in and map/reduce reducer on deterministic fixtures with no network/model calls.
3. **CI dry-run mode:** add non-publishing matrix/map-reduce jobs that upload artifacts and metrics but keep single-pass analysis as source of truth.
4. **A/B comparison:** for at least 4 weekly runs, compare current single-pass vs map/reduce outputs for gate pass rate, citation preservation, token use, cost, duration, and human review quality.
5. **Default switch only if thresholds pass:**
   - 100% final `analysis_gate.py` pass rate in dry-run comparison.
   - 0 missing required citations in reducer validation.
   - No increase in failed weekly publishes.
   - >=25% reduction in analysis prompt tokens or >=20% reduction in analysis wall time, without quality regression.
   - Crawl matrix only enabled if measured crawl stage p95 improves by >=20% or it materially improves retry isolation for sources with real failure/latency.
   - Token/cost per run stays within agreed budget and has alerts before hard overrun.
6. **Guarded rollout:** workflow_dispatch flag first, then scheduled dry-run, then default-on with single-pass fallback retained for at least one release cycle.

## Local and CI validation needed

Local validation:

- Unit tests for artifact schemas, fan-in merge determinism, dedupe ordering, cache metadata rejection, and failure classification.
- Unit tests for mapper schema validator, reducer dedupe/contradiction handling, citation preservation, week-window rejection, and token-budget preflight.
- Existing focused tests should remain green: `tests/test_crawl.py`, `tests/test_techcrunch_crawler.py`, `tests/test_pipeline.py`, `tests/test_analysis_gate.py`, `tests/test_analyze_fallback.py`, `tests/test_track_token_usage.py`, `tests/test_preflight_cost_check.py`, `tests/test_render_press_context.py`, `tests/test_correlate.py`.

CI validation:

- Matrix dry-run job with fixture legs and one forced optional failure.
- Fan-in job using `if: always()` that publishes diagnostics artifacts even on failed legs.
- Map/reduce dry-run job that compares reducer output to single-pass output but does not publish.
- Quality gate runs on final reducer markdown and fallback markdown.
- Token/cost ledger checks include mapper/reducer stages and enforce budget alerts.
- Rebuild mode validation hydrates canonical merged artifacts and does not depend on per-leg artifacts being present forever.

---

# Leela decision input — matrix crawl + map/reduce analysis PRD

Date: 2026-06-05T17:42:56.819+00:00
Owner: Leela / Lead
Artifact: `docs/PRD-matrix-crawl-map-reduce-analysis.md`

## Decision recommendation

Do not enable a crawl matrix by default. The recent implementation correctly avoided it because five-source RSS collection is about one second and already uses bounded in-process parallelism, while GitHub crawling is dominated by API/cache/rate-limit behavior that matrix fan-out could make worse.

Make crawl artifacts matrix-ready through shared run context, schema validation, checksums, deterministic fan-in, and observability. Gate RSS matrix on source count/runtime/isolation triggers. Gate GitHub matrix on a no-publish shard experiment that proves >=25% crawl speedup with <=10% API-call growth and no secondary-rate-limit regression.

Adopt map/reduce only as an analysis experiment for LLM context and quality. Mappers should emit structured claim ledgers with citations, confidence, contradictions, and coverage. The reducer should own dedupe, citation preservation, contradiction handling, editorial coherence, and final `analysis_gate.py` compliance.

## Follow-up needed

- Baseline crawl/analyze p50/p95 and token/cost metrics across multiple runs.
- Define artifact and mapper/reducer JSON schemas plus validators.
- Run map/reduce in dry-run A/B mode before publication eligibility.
- Keep single-pass/GitHub Models/no-AI fallback until map/reduce beats current quality and reliability gates.

---

# Bender run 27030646485 log review

Date: 2026-06-05T17:42:56Z
Run: https://github.com/jmservera/SquadScope/actions/runs/27030646485

## Findings

- Workflow completed successfully, but success came through the no-AI fallback path.
- Crawl job was healthy: `Run crawler` took ~4m30s, used 455 GitHub API calls, found 213 new repos and 236 trending repos, with 0 cache hits.
- External news behaved correctly at current scale: 5/5 sources succeeded in ~1s total, 39 articles, 23 relevant, 0 deduped, checksum `ebe382a11c0b...`.
- Per-source external news telemetry was present in logs and artifact metadata: source names, hosts, attempts, durations, article counts, relevant counts, GitHub-link counts, errors, config checksum, and artifact checksum.
- Correlation/press-context generation succeeded before analysis: 50 correlations from 449 repos; 9 strong and 41 weak; press context 32,765 bytes / ~7,991 token estimate.
- Analysis was the runtime and reliability concern: three Copilot attempts took ~28m41s and failed quality gates; the fallback GitHub Models request failed with `no_access` for `openai/gpt-4o`; data-only no-AI output passed the gate.
- Quality-gate failures were actionable:
  - attempts 1 and 2: `date must match the current run timestamp`;
  - attempt 3: invalid `predictions[*].claim_type` values plus the date mismatch.
- Token telemetry showed the analysis path estimated 112,911 input tokens / 119,620 total tokens, while the pre-flight check estimated 74,318 input tokens before full rendered prompt accounting.
- Non-blocking platform warning: GitHub Actions reported Node.js 20 actions deprecation for checkout/download/upload/setup/deploy actions.

## Directional read

This run supports the current PRD direction to keep external RSS in-process until scale/isolation thresholds are met. RSS is still not the speed bottleneck; the critical path is now analysis duration, prompt size, and retry waste. It also supports deterministic merge/press-context fan-in over LLM map-reduce for now: compact press context worked, but the full analysis prompt is still too large and brittle.

## Recommendations

1. Treat analysis compaction/retry control as higher priority than crawler matrixing.
2. Add or refine telemetry so pre-flight token estimates match the final prompt/token ledger, including press context and rendered instructions.
3. Consider failing faster on repeated deterministic gate failures such as timestamp mismatch and invalid enum values, or patch/sanitize those fields before retrying.
4. Gate Copilot retry count or switch earlier to no-AI/data-only when attempts exceed a duration budget.
5. Resolve the `openai/gpt-4o` GitHub Models access/config mismatch, or configure an accessible fallback model.
6. Track the Node.js 20 Actions deprecation, but it is not run-specific or urgent compared with analysis reliability.

## Issue recommendation

Do not open a separate crawler/RSS matrix issue from this run. The existing PRD/issue direction is enough for external-news telemetry and fan-in. If a new issue is opened, make it about analysis critical-path reduction and fallback model access, not crawler parallelism.

---

## Scribe: 2026-06-05T18:27:00Z — Merged PRD/run-review decision inputs

**Action:** Merged 5 decision inbox files into decisions.md:
- bender-matrix-crawl-prd-input.md (Bender: matrix crawl and fan-in/fan-out design options)
- farnsworth-map-reduce-analysis-prd-input.md (Farnsworth: analysis map/reduce architecture)
- fry-matrix-mapreduce-qa-prd-input.md (Fry QA: PRD-ready gates and test matrix)
- leela-matrix-mapreduce-prd.md (Leela: decision recommendation summary)
- bender-run-27030646485-log-review.md (Bender: run analysis and directional findings)

**Outcome:** decisions.md grew from 45948 → 91562 bytes. Inbox purged. No duplicates found in merge. Added 5 decision dividers. Content addresses crawl matrix topology, analysis map/reduce experiment design, QA gates/tests, run diagnostics, and fallback strategy.

**No archiving trigger:** decisions.md is still within typical document lifecycle size; existing PRD scope is fresh and actionable.

---

## Leela: Analysis rerun safety issue plan

Created: 2026-06-05T20:46:00.582+00:00

### Parent epic

- #248 — [Protect published weekly analysis from unsafe reruns](https://github.com/jmservera/SquadScope/issues/248)

### Immediate objective

Stop failed, degraded, low-quality, or no-AI analysis reruns from overwriting a good published weekly article. This protection should land before map/reduce implementation changes can affect publication.

### Child issues hierarchy

**P0 Safety Layer (11 issues):**
- #249 — Add candidate staging and publish eligibility manifest for analysis outputs | Bender | type:feature, priority:p0
- #250 — Preserve existing good weekly analysis on failed/degraded reruns | Bender | type:feature, priority:p0
- #251 — Block no-AI fallback from replacing AI-authored weekly summaries by default | Farnsworth | type:feature, priority:p0, rai
- #252 — Add explicit safe rerun modes and restore workflow controls | Leela | type:feature, priority:p0
- #253 — Add immutable backups and publish-branch concurrency safeguards | Bender | type:feature, priority:p0
- #254 — Make weekly promotion atomic across analyzed/content/deploy/notify | Bender | type:feature, priority:p0
- #255 — Strengthen analysis publish gate beyond structural validation | Farnsworth | type:feature, priority:p0, rai
- #257 — Add overwrite-protection and rerun idempotency regression tests | Fry | type:feature, priority:p0

**P1 Quality/Run Readiness (2 issues):**
- #256 — Add preflight compaction and fallback policy for next analysis run | Farnsworth | type:feature, priority:p1
- #259 — Document safe rerun, force-replace, and restore operations | Leela | type:docs, priority:p1

**P2 Future Analysis Architecture (1 issue):**
- #258 — Add map/reduce dry-run with claim-ledger contracts and QA comparison gates | Farnsworth with Fry QA support | type:feature, priority:p2, rai

### Summary

Safety-first protection layer for analysis reruns across staging/publish workflow. Prevents silent overwrite of good weekly articles on transient failures, low-quality output, or no-AI fallback misuse. Prioritizes atomic promotion, eligibility gates, and immutable backups before rolling out map/reduce.

### Notes

GitHub issue hierarchy represented via parent #248 with linked child issues and inline comments. All issues labeled `squad` with per-owner tracking.
