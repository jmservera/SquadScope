# Decision: Topic-Specific News Channels Architecture

**Date:** 2026-05-18T13:20:07.067+02:00  
**Author:** Leela (Lead/Architect)  
**Status:** Proposed  
**PRD:** docs/PRD-topic-channels.md  
**PR:** #39

## Decision Summary

Generalize SquadScope into a topic-channel system where each instance serves a single focused domain with isolated learning and calibrated predictions.

## Key Architectural Decisions

### 1. Feature First, Not Platform

SquadScope topic channels extend the existing pipeline (Crawl → Score → Analyze → Generate → Deploy) by adding a topic namespace. No new platform, no new repo structure. Same codebase, configured differently.

### 2. Multi-Instance Single-Topic (v1)

One fork/config per topic. Each fork has its own `squadscope.topic.yml`, its own Actions schedule, its own GitHub Pages site. This avoids orchestration complexity and keeps learning isolation trivial.

Multi-topic single-instance is v2 — only after v1 proves the model works.

### 3. Topic Config as Single Source of Truth

`squadscope.topic.yml` at repo root controls:
- Crawler queries
- Scoring weights and thresholds
- Analysis tone and audience
- Learning state paths
- Quality criteria

### 4. Scoring Pipeline (New Stage)

GitHub topic search is noisy. A new `scripts/score_repos.py` sits between crawl and analyze, scoring repos 0-100 on topic relevance, star momentum, language match, noise penalties, and recency. Only repos scoring ≥40 reach analysis.

### 5. Per-Topic Learning Isolation

Each topic maintains:
- `topics/{id}/wisdom.md` — domain-specific heuristics
- `topics/{id}/skills/` — extracted patterns
- `topics/{id}/predictions.jsonl` — prediction ledger
- `topics/{id}/scorecards/` — hindsight validation results

No cross-topic contamination. Wisdom from AI/ML never leaks into Rust analysis.

### 6. Prediction Ledger with Hindsight Validation

Every analysis appends machine-readable predictions to `predictions.jsonl`. Four weeks later, `scripts/validate_predictions.py` scores them against actual outcomes (star deltas, fork growth). Scorecards feed into reskill.

### 7. Topic Quality Criteria

Topics must meet minimum thresholds to justify a channel:
- Minimum N repos/week passing filters
- Maximum false positive rate
- Minimum genuinely significant repos per issue

## Implications

- Crawler must read config instead of using hardcoded queries
- Analysis prompt becomes a template with injection points
- Hugo gains topic taxonomy and per-topic RSS
- All data paths gain `{topic_id}/` prefix
- Reskill reads per-topic state

## Risks

- Topic configs may need frequent tuning in early weeks (mitigated by quality threshold warnings)
- Fork-per-topic model doesn't scale past ~5 topics (acceptable; v2 addresses this)
- Scoring weights are subjective initially (mitigated by prediction validation loop)

## Open for Discussion

- Should enrichment signals (forks, contributors) be in v1 scorer or deferred?
- Prediction confidence: fixed initial values or prompt-generated?
- Topic config in root vs `topics/` directory?
