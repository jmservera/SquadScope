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
- 2026-05-25 Phase 2 chrome: `layouts/partials/header.html` now owns the tokenized brand/nav/GitHub/theme-toggle header, and `layouts/partials/footer.html` overrides PaperMod's footer while preserving its scroll/theme/copy-code scripts.
- 2026-05-25 PaperMod gotcha: adding a skip-to-content link requires overriding `layouts/_default/baseof.html`; keep the theme submodule untouched and place site-level chrome overrides in root `layouts/partials/`.
- 2026-05-25 Phase 3 homepage: use `layouts/index.html` for editorial entry-point structure; keep home-specific styling in `assets/css/extended/squadscope.css` and reuse token variables only.
- 2026-05-25 Home visual verification runs through `node scripts/design/verify-visual.mjs --base http://localhost:1313/SquadScope/` after starting `/tmp/hugo server -D --bind 0.0.0.0 --port 1313 --baseURL http://localhost:1313/SquadScope/`.
- 2026-05-25 Phase 4 article layout: keep analyzer Markdown clean and derive article components from Hugo partials/render hooks (`article-content`, `repo-card`, `render-link`) instead of raw HTML in content.
- 2026-05-25 Weekly press context uses canonical `## Where Industry Meets Code`; wrapping it in a Hugo partial preserves clean heading flow while giving it complementary landmark styling.
- 2026-05-25 Phase 5 cost transparency lives in the About page via `{{< cost-dashboard >}}`; keep the shortcode as a thin wrapper over `layouts/partials/cost-dashboard.html` so direct `/dashboard/` links can reuse it.
- 2026-05-25 PR #199 follow-up: cost dashboard metric lists live in `assets/css/common/cost-dashboard.css`; strengthen `.post-content .cost-dashboard__metrics` specificity so global `.md-content dl/dt/dd` flex rules cannot override dashboard grid layout in article content.
- 2026-06-01 Issue #216: remove the header/home topic chip strips, keep desktop topic discovery in the homepage rail, and send mobile users to `/topics/` so topic navigation stops crowding small screens.
- 2026-06-01 The live `/topics/` route is driven by `layouts/topics/terms.html` because Hugo treats `topics` as a taxonomy landing page; fixes for an empty Topics page belong there, not only in `content/topics/_index.md`.
- 2026-06-01 PaperMod already exposes share buttons behind `params.ShowShareButtons`; add `params.ShareButtons` in `hugo.toml`, then override `layouts/partials/share_icons.html` at the project layer to add mobile Web Share API behavior without touching the theme submodule.
- 2026-06-01 Share-button styling belongs in `assets/css/common/post-single.css`, where article footer controls already map to the site token system and stay consistent across weekly/monthly/yearly article views.
- 2026-06-01 `git submodule update --init --recursive && hugo --minify` only passes here after upgrading to Hugo 0.147.9 locally, adding a project `google_analytics.html` partial, fixing `layouts/partials/cost-dashboard.html` to read from `.Site.Data`, and vendoring the PaperMod partials the site expects under `layouts/partials/`.

## Round 2026-06-01T12:19

### Issue #216: Mobile Topic Buttons
- PR #219 opened with clean Hugo build
- Mobile UX improved for topics navigation
- Responsive design verified on small screens

## Round 2026-06-01T12:41

### PR #219 Merged
- Review comments resolved: front matter `.Description` used, h2→h3 for card titles
- Accessibility improvement: hidden topic chips on screens ≤768px
- Commit e39720c
- Merged (squash)
- Issue #216 closed

## Round 2026-06-01T15:40

### Issue #226: Share Button Implementation
- PR #228 opened
- Implemented article-level sharing via PaperMod theme
- Vendored theme partials to project layouts
- Mobile Web Share API + desktop fallback links (X/LinkedIn/Facebook)
- Tokenized footer styling maintained
- Ready for review
