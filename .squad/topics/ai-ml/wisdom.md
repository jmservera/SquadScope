# AI & Machine Learning Topic Wisdom

## Signal Patterns
- Papers with code implementations gain rapid adoption
- Framework-adjacent tools (PyTorch/TensorFlow ecosystem) show sustained growth
- LLM-related repos have high initial stars but variable retention
- Research reproducibility repos (paper implementations) peak early then plateau
- Clustered movement across independent teams is stronger signal than any single repo launch
- Geographic/linguistic expansion of a trend (e.g., skills across Chinese platforms) is a distinct sub-signal
- Platform billing/policy changes are leading indicators for self-hosting repo spikes

## Noise Patterns
- Tutorial/course repos with high stars but low forks are often one-time views
- Wrapper libraries around APIs tend to be ephemeral
- Repos that only add a README without substantial code are often hype-driven
- Coordinated star-farming: tight clusters landing at near-identical star counts with zero forks in minutes
- Fork-inflation: repos with fork/star ratio >10x and keyword-stuffed descriptions indicate manipulation
- Creation-timestamp clustering (many repos appearing within minutes) signals coordinated campaigns

## Scoring Adjustments
- Weight Python and Jupyter Notebook repos higher
- Look for arXiv references as quality signals
- Multi-language repos (Python + C++) often indicate serious frameworks
- Lower editorial trust for new repos without fork activity (star-only traction)
- `stars_tracked` and `repos_featured` should be pipeline-computed, not hand-calculated

## Operational Heuristics
- Weekly briefs work best as named macro trends supported by repo evidence with links from crawl `url` field
- Press/industry coverage explains the gap between narrative and developer traction — never repackage
- Multi-source press input must be a compact correlation artifact (≤8k tokens), not raw dumps
- Distinguish strong correlations (same-week developer response) from weak (category-only fuzzy match)
- Reader-facing renders need a cleanup pass stripping AI-only scaffolding before publication
- The learning loop only works when lessons are persisted and injected back through shared wisdom/skills
