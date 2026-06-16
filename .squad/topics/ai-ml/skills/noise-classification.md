# Skill: Noise Classification

## Purpose
Identify and filter coordinated manipulation patterns in GitHub crawl data before
editorial analysis, preventing inflated repos from contaminating trend signals.

## Detection Heuristics

### Star-Farming (W22 pattern)
- **Trigger**: ≥3 repos landing within ±10 stars of each other in the same crawl window
- **Confirm**: Zero or near-zero fork count on repos with 400+ stars
- **Context**: Often clustered in game-cheat, software-unlock, or AI-branded categories
- **Action**: Flag as `noise:star-farm`, exclude from trend aggregation

### Fork-Inflation (W23 pattern)
- **Trigger**: Fork/star ratio > 10:1 on repos < 30 days old
- **Confirm**: Keyword-stuffed descriptions, bot-pattern naming conventions
- **Context**: Polymarket, crypto, and automated-trading verticals
- **Action**: Flag as `noise:fork-inflation`, exclude from trend aggregation

### Creation-Timestamp Clustering
- **Trigger**: ≥5 thematically similar repos created within a 60-minute window
- **Confirm**: Similar description templates, near-identical READMEs
- **Action**: Flag cluster as `noise:coordinated-creation`

## Evolution Expectation
Manipulation vectors rotate weekly. When a new metric vector appears (beyond stars and
forks), add a detection rule here. Watch for: issue-count inflation, sponsor-badge
gaming, discussion-count manipulation.

## Integration
- Pre-filter step before editorial scoring
- Flagged repos logged to `data/noise/` for retrospective audit
- Noise counts feed the weekly brief's Signal/Noise section
