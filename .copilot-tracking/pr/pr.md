# feat(rankings): deliver interactive ranking visualizations

This PR delivered Phase 4 of the Claracle post-relaunch consolidation. It added deterministic public ranking data, responsive visualizations, interactive exploration, accessible context disclosures, and the publishing integration needed to keep those surfaces current.

## Changes

### Ranking data and publishing

- Added a versioned ranking-artifact generator for the three public ranking pages and the homepage ranking summary.
- Extended ranking schemas and generated records with metric definitions, comparison values, language, safe GitHub URLs, provenance, short visible summaries, and complete sanitized accessible text.
- Integrated generation, freshness validation, hydration, artifact collection, commit paths, and deployment across the publishing workflows.

### Ranking experience

- Added server-rendered ranking facts with client-side filtering, sorting, reset, URL state, and explicit loading and failure states.
- Added responsive dot/lollipop and range visualizations with non-color encoding, direct repository links, and linked-table mobile fallbacks.
- Added keyboard, focus, touch, and Escape interactions for contextual disclosures without nesting interactive controls in SVG content.
- Updated homepage and observatory embeds to expose ranking summaries and equivalent accessible repository context.

### Tests and evidence

- Added generator, schema, template, browser, accessibility, and visual-regression coverage for the new ranking surfaces.
- Recorded the five-member representation-comprehension evidence and the conformant Phase 4 RPI review.
- Passed the affected Python, Ruff, Hugo/Pagefind/link, Playwright, visual, Node, Bandit, Checkov, and Zizmor gates.

## Related issues

None.

## External-facing changes

- [ ] If this PR ships copy or graphics that will appear OUTSIDE this repo (social posts, launch blog, announcements, press), I tagged @squad:nibbler for an RAI sign-off before merge.
