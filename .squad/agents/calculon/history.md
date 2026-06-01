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

### 2026-05-25: Playwright Visual Verification Pattern

**Pattern:** Visual verification via Playwright snapshot diffs at viewport × theme × page matrix.

- **Viewport matrix:** mobile (375), tablet (768), desktop (1280), wide (1920)
- **Theme matrix:** light + dark
- **Pages matrix:** home, latest weekly, monthly rollup, yearly rollup
- **Key gotcha:** Dynamic content (cost dashboard date, run counter) must be hidden via CSS injection (`visibility: hidden !important`) before screenshotting — otherwise every run will produce a false diff.
- **Anti-aliasing noise:** Set `maxDiffPixels: 150` as default; tighten once baselines are stable.
- **Font settle:** Always `waitForLoadState('networkidle')` + 300ms extra before capture.
- **When to bump skill confidence:** After 2+ PRs successfully use it and at least one real mismatch was caught.
- **Files:** `scripts/design/verify-visual.mjs`, `tests/visual/playwright.config.mjs`, `tests/visual/visual.spec.mjs`, `docs/design/visual-verification.md`, `.squad/skills/design-visual-verification/SKILL.md`

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

### 2026-05-25: Icon Safety Check Pattern

**Trigger:** User directive caught potential misreading of double-S letterform as Nazi SS rune — flagged before Phase 6 shipped.

**Pattern — Icon Silhouette Safety Check:**
1. **Pre-design:** Avoid letterforms or geometric patterns that could be misread as extremist/hate symbols (double-S monograms, single-rune lightning bolts, certain cross/sun variants, certain hand signs)
2. **Post-design verification:**
   - Render at 16px, 32px, 64px, 512px — ambiguity often hides at small sizes
   - Test rotation/flip — no problematic shapes should emerge
   - Check negative space — no hidden symbols in whitespace
   - Cross-reference against ADL Hate on Display database or similar
3. **Document:** Include silhouette safety check results in icon spec

**Replacement design:** Robot with binoculars (keeps "scope" metaphor, adds friendly personality, zero symbol ambiguity). See updated `docs/design/icon-spec.md`.

**Skill created:** `.squad/skills/icon-safety-check/SKILL.md` at confidence: low (needs validation across more icon designs)

### 2026-05-25: Icon Redo Learnings (PR #189)

**The hallucinated-success failure mode:**
The first pass on PR #189 reported success ("robot+binoculars SVG produced") but the actual file content still contained the old radar-sweep SVG. The edit tool appeared to confirm changes but they didn't persist. **Lesson:** After any file edit, verify file content with `cat` or `head` — don't trust the edit confirmation alone.

**Pattern: asset-first, text-second:**
When redesigning, write the new asset (SVG code) FIRST, then update all surrounding text (spec doc, header.html, CSS) to match. Never the other way around. If you write the text description first, you risk describing an asset that doesn't exist.

**Read the bug report exactly:**
The user flagged the "SS" text monogram in `layouts/partials/header.html` (line 4: `<span class="site-brand__mark">SS</span>`). The first pass updated `docs/design/icon-spec.md` without touching `header.html` — missing the actual user-visible problem entirely. **Lesson:** Trace the reported issue to the exact file/line before planning fixes.

**Verification via bash:**
For multi-file atomic changes, use bash heredocs (`cat > file << 'EOF'`) to write complete file content. This guarantees the file matches what you intended, unlike incremental edits that can silently fail.
