# Zapp — History

## Core Context
- Owns SEO and content optimization for SquadScope (public brand: Claracle).
- Ensures all generated pages — weekly analyses, monthly rollups, yearly narratives — have search-friendly titles, meta descriptions, and structured data.
- Works alongside Farnsworth (content generation) and Amy (frontend templates) to keep discoverability high.

## Founding Context — June 2026
- Created to address issue jmservera/SquadScope#519: monthly and yearly pages had generic titles ("June 2026 Rollup", "2026 Yearly Narrative") that performed poorly for search.
- Established the pattern of deterministic, content-derived editorial titles (max 70 chars) that include the time period and top themes.
- Monthly titles now surface accelerating/weakening themes as editorial headlines.
- Yearly titles reflect the dominant narrative arc of the year so far.

## Learnings
- Generic time-based titles ("Month Year Rollup") carry zero search intent signal; editorial titles with theme keywords rank better.
- The em-dash separator (` — `) between headline and time period is a clean pattern that works for both SEO and readability.
- Title generation must stay deterministic (based on synthesis themes, not LLM output) to ensure reproducible builds.
- The `_titlecase_tag()` helper with an acronyms set prevents awkward casing like "Ai" or "Mcp".
