# Calculon's History

## Core Context
- **Project:** SquadScope
- **User:** jmservera
- **Created:** 2026-05-25
- **Stack:** Hugo (v0.161.1) static site, PaperMod-derived theme, GitHub Pages deploy, Pagefind search
- **Description:** Weekly editorial trend analysis of GitHub repos and tech press. Editorial publication, not a dashboard. Reader-first.
- **Current state:** Site has functional content (W21, W22 published) but visuals are inherited from a generic PaperMod-style theme. Needs distinct editorial design direction.

## What the team has built
- Crawl → analyze → publish pipeline (Mon 08:30 UTC + manual)
- W21 article: "Agent Skills Go Mainstream While Star Farmers Game the Charts"
- W22 article: "Supply-Chain Scanners, Skills Economies, and GitHub's Star-Farm Flood"
- Monthly + yearly rollups
- TechCrunch press correlation
- Cost dashboard shortcode

## Key files in my domain
- `hugo.toml` — theme params, mounts, colors (currently default PaperMod)
- `layouts/` — Hugo templates (header.html, weekly/single.html, partials/report-metrics.html, shortcodes/cost-dashboard.html, index.html)
- `assets/` — CSS, JS (theme-derived)
- `static/` — favicons, icons, social images (currently default Hugo favicon)

## Learnings

### 2026-05-25: Initial Design Direction

**Design Principles Established:**
1. Reading First — Typography/spacing optimized for long-form scanning
2. One Signal Per Glance — Each content block delivers single clear message
3. Dense ≠ Cluttered — White space between dense blocks, not padding around sparse content

**Icon Concept:** Radar Sweep — concentric circles with sweep line and signal blip. Represents continuous scanning of GitHub landscape. Geometric, scales from 16px to 512px. Uses `currentColor` for automatic light/dark adaptation.

**Palette Decisions:**
- Light: bg #FAFAFA, text #1A1A1A, accent #0066CC
- Dark: bg #0D0D0D, text #E8E8E8, accent #4DA3FF
- All combinations WCAG AA verified

**Key Files Created:**
- `docs/design/redesign-proposal-2026-05.md` — Full design proposal with tokens, layout specs, component specs
- `docs/design/icon-spec.md` — Icon concept, SVG code, asset list

**Migration Phases:** 6 phases (tokens → header/footer → home → articles → cost dashboard → icons)

**Issues Created:** #170-#177
