# Amy — History

## Core Context
- Owns the Hugo presentation layer and weekly publishing surface.
- Treats analyzer markdown as input and keeps rendering concerns separate from data collection.

## Learnings
- The site is rooted at `hugo.toml` with layouts under `layouts/` and weekly content organized beneath `content/weekly/`.
- Weekly publication flows from analyzed markdown in `data/analyzed/` into archetype-compatible Hugo pages in `content/weekly/`, then into the Pages build artifact.
- `scripts/generate_content.py` should preserve the analysis body while dropping analyzer-only frontmatter fields that do not belong in published content.
- Frontend changes should assume the weekly brief is an editorial article first and a repo reference list second.
- 2026-05-25 Phase 1 redesign foundation: tokens live in `assets/css/tokens.css`, and Hugo loads them before PaperMod-compatible CSS from `layouts/partials/head.html`.
- 2026-05-25 Project-level `assets/css/core/` and `assets/css/common/` files override PaperMod submodule styles; keep the submodule clean and put SquadScope presentation changes in root assets.
- 2026-05-25 Inter and JetBrains Mono are loaded with preload + stylesheet links; existing PaperMod variables are mapped to new `--color-*`, `--text-*`, and `--space-*` tokens for compatibility.
