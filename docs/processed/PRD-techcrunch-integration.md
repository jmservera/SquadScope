# PRD: TechCrunch RSS Integration for Cross-Signal Enrichment

**Author:** Farnsworth (Analyst), revised by Bender (Crawler)  
**Date:** 2026-05-19  
**Status:** Completed — implemented and archived 2026-06-10 (see `scripts/techcrunch_crawler.py`, `tests/test_techcrunch_crawler.py`, and `data/raw/*-external-news.json`)  
**Type:** Feature PRD (Enrichment Signal)  
**Depends on:** .squad/decisions.md (Decision #7 — Crawler Plugin Architecture), docs/PRD-topic-channels.md

> **Archived as-is.** This PRD is preserved as a historical planning record. The current canonical paths, field names, and interfaces live in code — see `scripts/techcrunch_crawler.py`, `config/external_news_sources.json`, and `.github/workflows/crawl-and-publish.yml`. The most misleading specifics below have been corrected to match what shipped (the crawler now ingests multiple external news sources, not TechCrunch alone).

---

## Executive Summary

SquadScope tracks GitHub repository trends weekly. This PRD proposes adding TechCrunch RSS as a **supplementary enrichment signal** — not a primary data source — to detect the *delta* between press hype and actual GitHub traction. When TechCrunch covers a technology or project that also shows unusual GitHub star activity, that correlation is newsworthy. When press coverage does NOT correlate with GitHub activity, that absence is equally informative.

**Key constraint acknowledged upfront:** The correlation hit rate between TechCrunch articles and specific GitHub repositories is estimated at only **5–15%**. This feature is designed as a low-cost enrichment layer that adds value when correlations exist, and degrades gracefully (adds zero noise) when they don't.

---

## Problem Statement

### The Gap: Press Hype vs. Real Adoption

1. **GitHub stars measure developer interest.** A repo gaining 500 stars in a week signals genuine traction from people who build things.

2. **TechCrunch coverage measures press/VC interest.** An article about a startup or technology signals attention from the funding and media ecosystem.

3. **The delta between these signals is the insight.** Three scenarios produce editorial value:
   - **Hype confirmed:** TechCrunch covers X, and X's GitHub repos are surging → "Real momentum, developers agree"
   - **Hype without substance:** TechCrunch covers Y, but Y has zero or declining GitHub activity → "Marketing over engineering"
   - **Quiet breakout:** No press coverage, but a repo is exploding on GitHub → "Under the radar"

4. **Currently, SquadScope only sees scenario 3.** Adding press signal enables detecting scenarios 1 and 2, making the weekly digest more insightful.

### Why TechCrunch Specifically

- TechCrunch has a well-maintained RSS feed (`https://techcrunch.com/feed/`) with full article metadata
- It covers the startup/tech ecosystem most likely to overlap with open-source GitHub activity
- RSS is free, requires no API key, and is stable
- Other sources (HN, Reddit) can follow the same plugin pattern later

---

## Value Proposition: The Delta Model

The value of this integration is **NOT** in summarizing TechCrunch articles (readers can read TechCrunch themselves). The value is in the **cross-reference delta**:

```
Value = f(TechCrunch_coverage, GitHub_activity) where:
  - Both high  → "Confirmed trend"    (correlation)
  - TC high, GH low  → "Hype alert"   (anti-correlation)
  - TC low, GH high  → "Sleeper hit"  (absence signal)
  - Both low  → No signal             (filtered out)
```

This positions SquadScope as providing analysis that neither TechCrunch nor GitHub alone can offer.

---

## Honest Assessment: Correlation Rates

### Expected Hit Rates

| Correlation Type | Estimated Rate | Reasoning |
|-----------------|---------------|-----------|
| Direct match (TC mentions a specific repo) | 2–5% | Few TC articles name exact repos |
| Indirect match (TC covers technology X, repo uses topic X) | 10–15% | Broader topic matching catches more |
| No correlation found | 80–93% | Most TC articles have no GitHub signal |

### Why Low Rates Are Acceptable

1. **Low false-positive cost:** Uncorrelated articles are simply ignored — they add zero noise to the output.
2. **High value per hit:** When a correlation IS found, it's genuinely interesting editorial content.
3. **Asymmetric payoff:** Even 2–3 notable correlations per week would meaningfully enrich a weekly digest.
4. **Trend over time:** Cross-referencing accumulated over weeks reveals patterns invisible in any single week.

### What This Feature Is NOT

- NOT a TechCrunch summarizer
- NOT a primary data source for SquadScope
- NOT expected to produce signal every week
- NOT a replacement for GitHub-native trend detection

---

## Filtering Strategy

### The Problem: Volume

TechCrunch publishes **30–50 articles per day** (210–350 per week). Without aggressive filtering, this overwhelms the pipeline with noise. The crawler must reduce this to a manageable set before any correlation attempt.

### Three-Stage Filtering Pipeline

```
Stage 1: Category Filter (RSS metadata)
  Input:  ~250 articles/week (full RSS feed)
  Filter: Keep only categories relevant to developer tools/open-source
  Output: ~60-80 articles/week (70% reduction)
  Method: Allowlist of RSS <category> tags

Stage 2: Keyword Filter (title + description)
  Input:  ~60-80 articles/week
  Filter: Must contain technology/developer keywords
  Output: ~20-30 articles/week (60% reduction)
  Method: Keyword scoring (open-source, GitHub, developer, API, SDK, framework, etc.)

Stage 3: Entity Extraction (lightweight)
  Input:  ~20-30 articles/week
  Filter: Extract mentioned technologies, companies, project names
  Output: ~20-30 enriched article records with entity tags
  Method: Regex patterns + known project name dictionary
```

### Category Allowlist (Initial)

```yaml
allowed_categories:
  - Apps
  - Artificial Intelligence
  - Cloud
  - Developer
  - Enterprise
  - Hardware
  - Open Source
  - Robotics
  - Security
  - Startups

blocked_categories:
  - Media & Entertainment
  - Transportation
  - Government & Policy
  - Crypto  # Too noisy, low GitHub correlation
```

### Keyword Scoring

Each article gets a relevance score (0–10) based on title + description:

| Keyword Group | Weight | Examples |
|--------------|--------|----------|
| Direct GitHub mentions | +5 | "GitHub", "open source", "repository" |
| Developer tools | +3 | "API", "SDK", "framework", "library", "CLI" |
| Technology names | +2 | "Python", "Rust", "Kubernetes", "LLM" |
| Funding/startup | +1 | "raises", "Series A", "launch" |

**Threshold:** Articles scoring ≥ 3 proceed to entity extraction. Expected pass rate: ~40% of category-filtered articles.

---

## Temporal Alignment

### The Problem: RSS is Real-Time, SquadScope is Weekly

TechCrunch publishes continuously. SquadScope runs weekly (Monday 06:53 UTC). This creates a timing mismatch:

- An article published Tuesday about Project X won't be seen until the following Monday
- By then, the GitHub star surge may have already peaked and fallen

### Solution: Weekly Batch with 7-Day Window

```
┌─────────────────────────────────────────────────────┐
│  Monday 06:53 UTC: Crawl job runs                   │
│                                                     │
│  1. Fetch all RSS items from past 7 days            │
│  2. Filter (3-stage pipeline above)                 │
│  3. Extract entities from filtered articles         │
│  4. Cross-reference entities against weekly          │
│     GitHub trending repos (already collected)       │
│  5. Output correlation data for Farnsworth          │
└─────────────────────────────────────────────────────┘
```

### Why Weekly Batch Is Sufficient

1. **SquadScope is a weekly digest.** Real-time alerting is out of scope.
2. **7-day accumulation helps.** A trend covered across multiple articles in a week is stronger signal.
3. **GitHub stars data is also weekly.** Both signals align on the same time window.
4. **Simplicity:** No state management, no incremental polling, no deduplication across runs.

### Freshness Guarantee

- RSS feed items older than 7 days are discarded
- If the RSS feed doesn't contain 7 days of history (TechCrunch's feed typically holds 20–30 items), supplement with the feed's full available content
- Each item's `<pubDate>` is checked against the collection window

---

## Correlation Approach

### Entity-to-Repository Matching

```
TechCrunch Entity          →  GitHub Signal
─────────────────────────────────────────────────
"Anthropic" (company)      →  repos with topic:anthropic or org:anthropic
"LangChain" (project)      →  repo langchain-ai/langchain stars_gained
"Rust 2024 edition" (tech) →  repos with topic:rust AND stars_gained > threshold
"Series B: Acme Corp"      →  repos owned by acme-corp org
```

### Matching Strategies (in priority order)

1. **Exact name match:** Article mentions "LangChain" → search for repos named `langchain*`
2. **Organization match:** Article mentions company → search GitHub org
3. **Topic match:** Article discusses technology → match against repo topics
4. **Description match:** Fuzzy match article entities against repo descriptions

### Scoring Correlation Strength

| Match Type | Confidence | Example |
|-----------|-----------|---------|
| Exact repo name in article | 0.9 | "...announced on their GitHub repo langchain-ai/langchain..." |
| Organization name + topic overlap | 0.7 | Article about Anthropic + repo topics include "claude" |
| Technology keyword + trending | 0.5 | Article about "Rust" + Rust repo trending |
| Company name only (no GitHub signal) | 0.3 | Article about startup with no public repos |

### Output Format

```json
{
  "week": "2026-W21",
  "correlations": [
    {
      "article_title": "LangChain raises $25M Series A",
      "article_url": "https://techcrunch.com/...",
      "article_date": "2026-05-15",
      "matched_repos": ["langchain-ai/langchain"],
      "match_type": "exact_name",
      "confidence": 0.9,
      "github_signal": {
        "stars_gained": 847,
        "percentile": 98
      },
      "delta_type": "confirmed_trend"
    }
  ],
  "unmatched_articles": 24,
  "total_filtered_articles": 27
}
```

---

## Technical Implementation

### Architecture: Plugin Pattern (Decision #7)

This integration implements the `DataSource` protocol defined in Decision #7:

```python
# As shipped: scripts/techcrunch_crawler.py
class NewsFeedSource:
    """RSS data source following the DataSource protocol."""

    def __init__(self, config: NewsSourceConfig) -> None:
        self.config = config

    def get_name(self) -> str:
        return self.config.name

    def get_rate_limits(self) -> dict:
        # Plain dict, not a RateLimits type.
        return {"requests_per_minute": self.config.requests_per_minute}

    def crawl(
        self,
        since: datetime,
        until: datetime,
        feed_url: str | None = None,
    ) -> list[dict]:
        """Fetch, filter, and extract entities from an RSS feed."""
        ...
```

`TechCrunchSource` is a thin subclass of `NewsFeedSource`; each source is
described by a `NewsSourceConfig` (`name`, `feed_url`, `requests_per_minute`)
loaded from `config/external_news_sources.json`.

### File Layout

```
scripts/
  techcrunch_crawler.py    # Multi-source RSS crawler (DataSource protocol)
  correlate.py             # Cross-reference GitHub vs external news
config/
  external_news_sources.json  # Per-source feed_url + requests_per_minute
data/
  raw/
    {week}-external-news.json   # Merged crawl output (legacy: {week}-techcrunch.json)
  analyzed/
    {week}-correlations.json    # Cross-reference results (output for Farnsworth)
```

### Dependencies

| Dependency | Purpose | Size Impact |
|-----------|---------|-------------|
| `feedparser` | RSS parsing | ~200 KB, pure Python |
| `re` (stdlib) | Entity extraction patterns | None |
| `datetime` (stdlib) | Window filtering | None |

No additional API keys or authentication required. RSS is public.

### Integration with Existing Crawl Workflow

```yaml
# In crawl-and-publish.yml (additions only)
- name: Crawl external news RSS
  run: |
    python3 scripts/techcrunch_crawler.py \
      --sources config/external_news_sources.json \
      --output "data/raw/${WEEK}-external-news.json" \
      --since "$SINCE" \
      --until "$UNTIL"

- name: Cross-reference correlations
  run: |
    python3 scripts/correlate.py \
      --raw "$WEEK_FILE" \
      --techcrunch "data/raw/${WEEK}-external-news.json" \
      --output "data/analyzed/${WEEK}-correlations.json"
```

### Error Handling

| Failure Mode | Response | Impact |
|-------------|----------|--------|
| RSS feed unreachable | Retry 3×, then skip TechCrunch for this week | None — enrichment is optional |
| RSS feed format changed | Log warning, skip parsing, open issue | None — graceful degradation |
| Zero correlations found | Normal — output empty correlations file | Expected most weeks |
| Malformed XML in feed | Skip malformed items, process rest | Partial data is fine |

---

## Cost Estimate

### Compute Cost

| Resource | Usage | Cost |
|---------|-------|------|
| RSS fetch | 1 HTTP request/week | $0.00 |
| Python processing | ~5 seconds CPU | $0.00 (free Actions minutes) |
| Correlation script | ~2 seconds CPU | $0.00 |
| **Total infrastructure cost** | | **$0.00/week** |

### Token Cost (if Farnsworth uses correlations in analysis)

| Component | Size | Tokens | Cost Impact |
|-----------|------|--------|-------------|
| Correlations JSON (typical week, 2–5 hits) | ~2 KB | ~570 | +$0.002/week |
| Correlations JSON (zero hits) | ~0.2 KB | ~57 | +$0.0002/week |
| Correlations JSON (exceptional week, 10+ hits) | ~5 KB | ~1,400 | +$0.004/week |

**Annual token cost impact: $0.10–$0.21/year** (negligible relative to $16/year baseline).

### Development Cost

| Task | Effort | Priority |
|------|--------|----------|
| `techcrunch.py` plugin | 2–3 hours | Medium |
| `correlate.py` script | 2–3 hours | Medium |
| Configuration + tests | 1–2 hours | Medium |
| Workflow integration | 1 hour | Low |
| **Total** | **6–9 hours** | |

---

## Success Criteria

### Quantitative Metrics (measured after 8 weeks of operation)

| Metric | Target | Measurement |
|--------|--------|-------------|
| RSS fetch success rate | ≥ 95% | Weeks with successful fetch / total weeks |
| Filter reduction ratio | 85–95% reduction | (Raw articles - filtered) / raw articles |
| Correlation hit rate | ≥ 5% of filtered articles | Articles with ≥1 GitHub match / filtered articles |
| False positive rate | ≤ 2% | Matches marked incorrect in manual review / total matches |
| Zero-noise weeks | 100% | Weeks where zero-correlation produces zero output noise |
| Enrichment value (subjective) | ≥ 3/5 quality rating | Monthly review: "Did correlations improve the digest?" |

### Qualitative Success Indicators

- At least 1 "hype vs reality" insight per month that wouldn't exist without this signal
- Zero instances where TechCrunch noise degrades the digest quality
- The feature is invisible when it has nothing useful to contribute

### Failure Criteria (triggers feature removal)

- Hit rate below 2% after 8 weeks → feature adds complexity without value
- False positives above 10% → feature introduces noise
- RSS feed breaks and stays broken for 4+ consecutive weeks → dependency unreliable
- Farnsworth (analyst) consistently ignores correlation data in analysis → no downstream value

---

## Phased Rollout

### Phase 1: RSS Collection Only (Week 1–2)

- Implement `scripts/techcrunch_crawler.py` with 3-stage filtering
- Output `data/raw/{week}-external-news.json` (legacy `data/raw/{week}-techcrunch.json`)
- No integration with analysis — just collect and validate filter quality
- **Exit criteria:** Filter reduces volume by ≥ 80%, entity extraction produces meaningful tags

### Phase 2: Correlation Script (Week 3–4)

- Implement `correlate.py` cross-reference logic
- Output `data/analyzed/{week}-correlations.json`
- Manual review of correlation quality for 2 weeks
- **Exit criteria:** Hit rate ≥ 3%, false positive rate ≤ 5%

### Phase 3: Analysis Integration (Week 5–6)

- Farnsworth consumes `data/analyzed/{week}-correlations.json` in analysis prompt
- Correlation data appears in weekly digest when relevant
- **Exit criteria:** At least 1 correlation adds editorial value in 2 of 4 weeks

### Phase 4: Steady State (Week 7+)

- Monitor success metrics
- Tune keyword lists and category filters based on actual hit rates
- Consider adding second source (HN) if TechCrunch proves the plugin model

---

## Open Questions

| # | Question | Impact | Proposed Resolution |
|---|----------|--------|---------------------|
| OQ1 | Does TechCrunch's RSS feed include full article text or just excerpts? | Medium — affects entity extraction quality | Spike: inspect actual feed content. If excerpts only, extraction limited to title + summary. |
| OQ2 | How stable is TechCrunch's RSS feed over time? | Low — RSS is a mature standard | Monitor for 4 weeks before hard dependency. Breakage triggers graceful skip. |
| OQ3 | Should entity extraction use AI (LLM) or stay rule-based? | Medium — cost vs quality trade-off | Start rule-based (zero cost). Upgrade to LLM extraction in Phase 4 if hit rates are too low. |
| OQ4 | What's the right confidence threshold for surfacing correlations? | Medium — affects noise level | Start conservative (confidence ≥ 0.7). Lower if too few results after 4 weeks. |
| OQ5 | Should correlations appear as a separate section in the digest or inline? | Low — editorial decision | Defer to Farnsworth. Provide data; let analyst decide presentation. |
| OQ6 | Can we use GitHub's topic taxonomy to improve matching? | Medium — could boost hit rate | Investigate `GET /repos/{owner}/{repo}/topics` coverage during Phase 2. |

---

## Relationship to Other PRDs

- **PRD-topic-channels.md:** Topic channels define per-domain crawling. TechCrunch integration is orthogonal — it enriches ANY topic channel with press signal. A `rust` channel could correlate TechCrunch Rust articles with Rust repo trends.
- **PRD-cost-estimation.md:** TechCrunch adds negligible cost ($0.10–$0.21/year in tokens). No budget concern.
- **Decision #7 (Plugin Architecture):** TechCrunch is the first non-GitHub `DataSource` plugin, validating the extensible crawler design.

---

*Archived as-is. This PRD reflects the original plan; the integration shipped on 2026-06-10. For canonical paths, field names, and interfaces, see the code (`scripts/techcrunch_crawler.py`, `config/external_news_sources.json`, `.github/workflows/crawl-and-publish.yml`).*
