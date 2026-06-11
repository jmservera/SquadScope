# PRD: TechCrunch RSS Integration for Cross-Source Trend Correlation

> **Archival note (2026-06-11):** This is the **earlier, superseded** draft of the TechCrunch
> RSS PRD, preserved for history. It was replaced by the revised, shipped PRD
> [`PRD-techcrunch-integration.md`](./PRD-techcrunch-integration.md)
> ("TechCrunch RSS Integration for Cross-Signal Enrichment"), which is the canonical record of
> the implemented feature. See issue #377 for the reconciliation of the duplicate filename.

**Author:** Farnsworth (Analyst/Content Curator)  
**Date:** 2026-05-19  
**Status:** Superseded — see canonical `PRD-techcrunch-integration.md`  
**Type:** Feature PRD  
**Depends on:** .squad/decisions-archive.md (Decision #7: Crawler Plugin Architecture), docs/processed/PRD-topic-channels.md

---

## Executive Summary

SquadScope currently derives all insights from a single signal source: GitHub activity. While GitHub reveals *what developers are building*, it cannot tell us *why* activity is spiking — whether it's organic community interest, a VC-backed launch, or a viral TechCrunch article driving attention. This PRD proposes integrating TechCrunch's RSS feed as SquadScope's first non-GitHub data source, enabling **cross-source trend correlation** that distinguishes organic momentum from press-driven hype.

**Key insight:** GitHub star surges often lag TechCrunch coverage by 24–72 hours. Detecting this pattern lets SquadScope editorially distinguish "genuinely important" (organic growth) from "temporarily hyped" (press-driven spike that fades within a week).

---

## Problem Statement

### What GitHub data alone cannot tell us

1. **Causality is invisible.** A repo gaining 2,000 stars in a week is interesting, but *why* matters editorially. Is it because the project shipped a breakthrough feature, or because TechCrunch wrote about it and HN amplified?

2. **Funding and launch context is missing.** When a startup raises a $50M Series B and open-sources their core library, GitHub shows a star spike — but without the funding context, the analysis misattributes organic community excitement.

3. **Industry narrative gaps.** SquadScope's "Gaps" section (what's missing from the conversation) is currently limited to what's absent from GitHub. But sometimes the gap is between what the industry *claims* to care about (per press coverage) and what's actually *being built* (per GitHub).

4. **Hype detection requires a baseline.** To identify noise, you need to know what the press machine is amplifying. Without press data, everything on GitHub looks equally "organic."

5. **Prediction accuracy suffers.** The topic-channels PRD envisions a prediction ledger. Cross-referencing press coverage with subsequent GitHub activity dramatically improves prediction calibration.

---

## Value Proposition

### For SquadScope readers

| Current State (GitHub-only) | With TechCrunch Correlation |
|---|---|
| "Repo X gained 3,000 stars this week" | "Repo X gained 3,000 stars after TechCrunch covered their $30M raise — watch if stars sustain past week 2" |
| "These 5 AI repos are trending" | "3 of 5 trending AI repos correlate with press coverage; 2 show organic growth (stronger signal)" |
| "Gap: No new observability tools" | "Gap: TechCrunch covered 4 observability startups this month, but none have meaningful GitHub traction yet — vaporware risk" |

### For SquadScope's editorial stance

- **Critical thinking becomes measurable:** "Press-amplified vs. organically growing" is a concrete, data-backed editorial judgment
- **Signal vs. noise gets sharper:** Hype detection moves from vibes-based to correlation-based
- **The Gaps section gains depth:** Disconnects between press narrative and actual developer activity become visible

---

## Correlation Model

### How TechCrunch articles map to GitHub signals

```
┌─────────────────┐         ┌──────────────────────┐
│  TechCrunch RSS │         │  GitHub Weekly Crawl  │
│  (article feed) │         │  (repo activity)      │
└────────┬────────┘         └──────────┬───────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐         ┌──────────────────────┐
│ Extract:        │         │ Extract:             │
│ - Company/proj  │         │ - Repo name/org      │
│ - Category      │         │ - Star delta         │
│ - Funding amt   │         │ - Fork delta         │
│ - GitHub links  │         │ - Contributor growth  │
└────────┬────────┘         └──────────┬───────────┘
         │                              │
         └──────────┬───────────────────┘
                    ▼
         ┌─────────────────────┐
         │  Correlation Engine  │
         │  (fuzzy matching)    │
         └──────────┬──────────┘
                    ▼
         ┌─────────────────────┐
         │  Annotated Analysis │
         │  - press_correlated │
         │  - organic_growth   │
         │  - hype_risk_score  │
         └─────────────────────┘
```

### Correlation heuristics

1. **Direct link match:** TechCrunch article contains a GitHub URL → exact match to crawled repo
2. **Organization match:** Article mentions company X → match to `github.com/X/*` repos gaining stars
3. **Project name match:** Article title/body contains project name → fuzzy match against repo names in weekly crawl
4. **Category correlation:** Article tagged "AI" published Monday → AI-category repos spiking by Thursday
5. **Temporal lag analysis:** Stars gained within 72 hours of article publication → likely press-correlated

### Hype risk scoring

| Pattern | Hype Risk | Editorial Label |
|---------|-----------|-----------------|
| Stars spike post-article, sustain 2+ weeks | Low | "Press-validated, community-sustained" |
| Stars spike post-article, decay within 7 days | High | "Press-driven hype, fading interest" |
| Stars growing before any press coverage | Very Low | "Organic growth — genuinely interesting" |
| Press coverage but no GitHub activity | Medium | "Announced but unbuilt / closed-source" |

---

## Technical Approach

### Data Source: TechCrunch RSS

- **Feed URL:** `https://techcrunch.com/feed/`
- **Format:** RSS 2.0 / XML
- **Update frequency:** ~20-40 articles/day
- **Relevant categories:** Startups, Apps, AI, Funding, Open Source
- **Rate limits:** None (public RSS)
- **Content available in feed:** Title, excerpt/summary, author, publish date, categories, link

### Architecture: Fits Decision #7 (Crawler Plugin)

The existing `DataSource` protocol interface applies directly:

```python
class TechCrunchSource:
    """Crawler plugin for TechCrunch RSS feed."""

    def get_name(self) -> str:
        return "techcrunch"

    def get_rate_limits(self) -> RateLimits:
        return RateLimits(requests_per_hour=10, burst=5)

    async def crawl(self, config: CrawlConfig) -> CrawlResult:
        """Fetch and parse TechCrunch RSS, extract structured articles."""
        ...
```

### Data flow integration

```
Existing:   data/raw/YYYY-WNN.json          (GitHub crawl)
New:        data/raw/YYYY-WNN-techcrunch.json (TechCrunch crawl)
Merged:     data/analyzed/YYYY-WNN-summary.md  (cross-referenced analysis)
```

### RSS parsing requirements

| Requirement | Approach |
|-------------|----------|
| XML parsing | `feedparser` (Python) — battle-tested RSS library |
| Category extraction | Map TC categories to SquadScope topic taxonomy |
| GitHub link extraction | Regex scan article content for `github.com` URLs |
| Entity extraction | Match company/project names against crawled repos |
| Deduplication | Hash on article URL; skip already-processed items |
| Storage | JSON array, same weekly naming as GitHub crawl |

### Output schema (per article)

```json
{
  "source": "techcrunch",
  "title": "Anthropic open-sources Claude's tool-use framework",
  "url": "https://techcrunch.com/2026/05/15/...",
  "published_at": "2026-05-15T14:30:00Z",
  "categories": ["ai", "open-source", "funding"],
  "github_links": ["https://github.com/anthropics/tool-use-sdk"],
  "entities": ["Anthropic", "Claude"],
  "funding_amount": null,
  "relevance_score": 0.85
}
```

### Analyzer changes

The analyzer prompt gains a new context block:

```
## Press Context (TechCrunch, week of {date})
{N} articles published relevant to tech/open-source.
Notable coverage:
- {title} ({category}) — mentions {github_links}
- ...

Cross-reference: For each trending repo, note if press coverage
preceded the star surge. Label as "press-correlated" or "organic."
```

---

## Phases

### Phase 1: RSS Crawl Plugin (1–2 weeks)

- Implement `TechCrunchSource` crawler plugin
- Parse RSS feed, extract structured article data
- Store as `data/raw/YYYY-WNN-techcrunch.json`
- Filter to tech/open-source relevant articles only
- Basic deduplication
- **Output:** Weekly TechCrunch article JSON alongside GitHub JSON

### Phase 2: Correlation Engine (2–3 weeks)

- Implement GitHub URL extraction from articles
- Fuzzy entity matching (company name → GitHub org)
- Temporal correlation (article date vs. star surge timing)
- Add `press_correlated: bool` and `hype_risk: low|medium|high` to repo analysis
- **Output:** Enriched analysis with cross-source annotations

### Phase 3: Editorial Integration (1–2 weeks)

- Update analyzer prompt to consume TechCrunch context
- Add "Press vs. Reality" subsection to weekly summary
- Surface disconnects in Gaps section
- Update Hugo templates to render correlation badges
- **Output:** Reader-facing cross-source insights on the published site

### Phase 4: Prediction Enhancement (future)

- Track whether press-correlated repos sustain momentum
- Feed correlation accuracy back into prediction ledger
- Calibrate hype risk scoring over time
- **Output:** Improved prediction accuracy in topic channels

---

## Cost & Resource Impact

| Resource | Impact |
|----------|--------|
| RSS fetch | Negligible (1 HTTP request/week, public feed, no auth) |
| Storage | ~50-100 KB/week JSON (40 articles × metadata) |
| Analyzer tokens | +500-800 tokens input context per run (~$0.002/week) |
| API rate limits | Zero impact (RSS is not GitHub API) |
| CI minutes | +5-10 seconds per run (RSS fetch + parse) |
| Dependencies | `feedparser` (Python, MIT license, mature) |

**Total incremental cost: <$0.01/week.** Trivial relative to base pipeline costs documented in PRD-cost-estimation.md.

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| TechCrunch changes RSS format | Low | Medium | feedparser handles format variations; alert on parse failures |
| RSS feed discontinued | Very Low | Low | Graceful degradation — analysis runs without press context |
| False correlations (noise) | Medium | Medium | Require temporal proximity (72h) + name match confidence >0.7 |
| Over-weighting press signal | Medium | High | Editorial rule: press correlation is annotation, not ranking factor |
| Content extraction blocked | Low | Low | Use RSS summary only, don't scrape full articles |

---

## Open Questions

1. **OQ1: Should we also extract from TechCrunch's category-specific feeds?**
   - `techcrunch.com/category/artificial-intelligence/feed/` for topic-channel alignment
   - Pro: Better relevance filtering. Con: More feeds to manage.

2. **OQ2: Full article fetch vs. RSS excerpt only?**
   - RSS includes ~200 word excerpt. Full article requires HTTP fetch + HTML parsing.
   - Recommendation: Start with RSS excerpt only. Avoids scraping concerns and ToS issues.

3. **OQ3: Should correlation annotations be visible to readers or analyst-only?**
   - Option A: Show "📰 Press-correlated" badge on repo entries
   - Option B: Keep as internal signal that shapes editorial tone only
   - Recommendation: Option A for transparency (readers deserve to know *why* something is trending)

4. **OQ4: Add HackerNews as a second correlation source simultaneously?**
   - HN has an API, overlaps with TechCrunch coverage, and better represents developer sentiment
   - Recommendation: TechCrunch first (simpler, RSS), HN second (API, different signal)

5. **OQ5: How to handle TechCrunch articles about closed-source products?**
   - Many TC articles cover proprietary SaaS with no GitHub presence
   - Recommendation: Filter to articles containing GitHub links OR open-source keywords only

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Articles crawled per week | 15-40 relevant | Count in weekly JSON |
| Correlation hit rate | >30% of trending repos have press match | Cross-reference accuracy |
| Hype detection accuracy | >70% of "high hype risk" repos show star decay at week +2 | Retrospective validation |
| Reader value signal | Qualitative improvement in Gaps section depth | Editorial review |
| Zero pipeline failures from RSS source | 100% graceful degradation | CI logs |

---

## Relationship to Existing PRDs

- **PRD-topic-channels.md:** TechCrunch correlation enriches per-topic analysis. AI-focused TC articles correlate with `ai-ml` topic channel repos.
- **PRD-cost-estimation.md:** Incremental cost is negligible (<$0.01/week). No tier change needed.
- **.squad/decisions-archive.md Decision #7:** This is the first concrete implementation of the crawler plugin architecture.
- **.squad/decisions-archive.md MCP Tools:** TechCrunch RSS fetch can be an MCP tool, registered in allowlist per Decision 5.

---

## Editorial Philosophy Note

TechCrunch integration does NOT mean SquadScope becomes a TechCrunch aggregator. The feed is a **correlation signal**, not content to republish. SquadScope's voice remains: "Here's what's actually happening on GitHub this week, and here's what the press says is happening. Notice the gap? That's where the real story is."

The editorial value is in the *delta* between press narrative and developer activity — not in summarizing TechCrunch articles.
