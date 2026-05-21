# Amy — History

## Core Context
- Owns the Hugo presentation layer and weekly publishing surface.
- Treats analyzer markdown as input and keeps rendering concerns separate from data collection.

## Learnings
- The site is rooted at `hugo.toml` with layouts under `layouts/` and weekly content organized beneath `content/weekly/`.
- Weekly publication flows from analyzed markdown in `data/analyzed/` into archetype-compatible Hugo pages in `content/weekly/`, then into the Pages build artifact.
- `scripts/generate_content.py` should preserve the analysis body while dropping analyzer-only frontmatter fields that do not belong in published content.
- Frontend changes should assume the weekly brief is an editorial article first and a repo reference list second.
