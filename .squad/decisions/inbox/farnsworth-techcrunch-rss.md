# Decision Proposal: TechCrunch RSS as First Non-GitHub Data Source

**Author:** Farnsworth (Analyst)  
**Date:** 2026-05-19T11:48:44.543Z  
**Status:** Proposed  
**PRD:** docs/PRD-techcrunch-integration.md

## Decision

Add TechCrunch RSS (`https://techcrunch.com/feed/`) as SquadScope's first non-GitHub data source, implementing Decision #7's crawler plugin architecture.

## Rationale

1. Cross-source correlation enables hype detection (press-driven vs. organic growth)
2. Near-zero cost and complexity (public RSS, no auth, no rate limits)
3. Directly implements the `DataSource` plugin pattern already approved
4. Enriches editorial judgment without changing SquadScope's voice or pipeline structure

## Impact

- **Bender:** Implements `TechCrunchSource` crawler plugin
- **Farnsworth:** Analyzer prompt gains press-context block; labels repos as press-correlated or organic
- **Amy:** Optional correlation badge in Hugo templates
- **Leela:** No architectural changes needed; plugin arch already designed for this

## Open for team input

- Should we start with full feed or category-specific feeds?
- Correlation annotations: reader-visible or internal-only?
