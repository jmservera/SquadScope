# Source-selection methodology disclosure

- **Date:** 2026-05-25
- **Owner:** Farnsworth
- **Status:** Proposed for merge

## Decision

Source-selection biases are publicly disclosed at `/methodology/`; updates to scoring, source ingestion, crawl thresholds, or press coverage should be reflected there.

## Context

Nibbler's second responsible-AI sweep identified source-selection bias disclosure as a high-severity fairness and transparency gap. The methodology page gives readers a plain-English explanation of source inputs, ranking logic, and interpretation limits.

## Consequences

- Pipeline changes that alter source mix or scoring should include a reader-facing methodology update.
- Future bias metrics can link back to `/methodology/` as the stable disclosure surface.
