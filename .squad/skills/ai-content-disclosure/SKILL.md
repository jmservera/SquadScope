---
name: "ai-content-disclosure"
description: "Reusable pattern for visibly disclosing AI-generated editorial content across the Hugo site."
domain: "responsible-ai, frontend, hugo, accessibility"
confidence: "medium"
source: "Amy AI disclosure implementation — 2026-05-25"
owner: "Amy"
---

## Pattern

Use one global Hugo partial for baseline disclosure on every page, then add a stronger badge in article metadata for generated analysis pages.

## Requirements

- Keep visible disclosure text in the normal reading flow; do not rely only on metadata, tooltips, or ARIA.
- Use generic language such as "AI models" rather than vendor-specific names.
- Name accountability: editorial structure and source curation are owned by the SquadScope maintainer.
- Provide an error-reporting path to GitHub issues.
- Keep the footer partial as the single source of truth so new pages inherit disclosure automatically.
- Ensure print styles preserve the disclosure.

## Hugo Implementation

1. Render `layouts/partials/ai-disclosure.html` from `layouts/partials/footer.html`.
2. Add `<meta name="ai-generated" content="true">` in `layouts/partials/head.html`.
3. Add `data-ai-generated="true"` to the `<body>` in `layouts/_default/baseof.html`.
4. Add an `AI-generated analysis` badge in `layouts/partials/article-meta.html` for weekly/topic analysis pages.

## Verification

Build the site, inspect rendered HTML for the meta and body attributes, and visually check the footer disclosure plus article badge in light/dark and mobile/desktop viewports.
