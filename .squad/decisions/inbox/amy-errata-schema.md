# Article errata schema

**Date:** 2026-05-25  
**Author:** Amy  
**Status:** Proposed

## Decision

Articles declare corrections in front-matter using `errata: [{date, note}]`; the article footer renders those entries at the end of the article.

## Schema example

```yaml
errata:
  - date: 2026-05-26
    note: "Corrected the company name in the EU AI Act section (was 'Mistral.ai', now 'Mistral AI')."
```

## Rationale

Keeping corrections in front-matter makes the article-level errata path data-driven, reviewable in Git, and visible to readers without requiring silent edits to published analysis.
