# Visual Verification for Design Review

> **Why this exists:** SquadScope has a 6-phase editorial redesign underway (issues #170–#177, spec at `docs/design/redesign-proposal-2026-05.md`). Each phase changes layouts, tokens, or typography. This doc explains how Calculon (Designer) catches regressions before they ship.

---

## Why We Do This

The redesign proposal defines explicit acceptance criteria per phase — heading scale, palette tokens, contrast ratios, layout breakpoints. Without screenshots, design review is reading diffs and hoping. Playwright lets us:

- See the page as a reader would at 4 viewport widths
- Verify light *and* dark mode in the same pass
- Catch regressions automatically once a baseline exists
- Attach evidence screenshots to PR comments

Related: [`docs/design/redesign-proposal-2026-05.md`](redesign-proposal-2026-05.md)

---

## Prerequisites

1. **Hugo installed** — `hugo version` should return ≥ v0.100
2. **Node.js ≥ 18** — `node --version`
3. **Playwright Chromium** — install once:

```bash
npx playwright install chromium --with-deps
```

That's it. No `npm install` needed — run everything via `npx`.

---

## How to Run Locally

### Quick screenshot pass (standalone script)

```bash
# 1. Start Hugo with drafts
hugo server -D --bind 0.0.0.0

# 2. In a second terminal, run the capture script
node scripts/design/verify-visual.mjs

# Screenshots land in:
# screenshots/design-verification/2026-05-25/
```

Each filename follows the pattern: `{page}-{viewport}-{theme}.png`  
Example: `home-desktop-dark.png`, `weekly-w22-mobile-light.png`

A `manifest.json` is written to the same folder with pass/fail status.

### Playwright snapshot regression test

```bash
# 1. Start Hugo
hugo server -D --bind 0.0.0.0

# 2. Generate baselines (run ONCE on the main branch):
npx playwright test --config tests/visual/playwright.config.mjs --update-snapshots

# 3. On PR branch — compare against baselines:
npx playwright test --config tests/visual/playwright.config.mjs
```

Test results appear at `playwright-report/index.html` (open in browser).  
Snapshot baselines are saved to `tests/visual/snapshots/`.

---

## Matrix Covered

### Viewports

| Name | Width | Height |
|------|-------|--------|
| mobile | 375 | 667 |
| tablet | 768 | 1024 |
| desktop | 1280 | 800 |
| wide | 1920 | 1080 |

### Themes

| Mode | Playwright setting |
|------|--------------------|
| light | `colorScheme: 'light'` |
| dark | `colorScheme: 'dark'` |

### Pages

| Key | URL path |
|-----|----------|
| home | `/` |
| latest-weekly | `/weekly/2026/w22/` |
| monthly-rollup | `/monthly/2026/05/` |
| yearly-rollup | `/yearly/2026/` |

**Total:** 4 pages × 4 viewports × 2 themes = **32 screenshots per pass**

---

## How Calculon Uses This in PR Review

1. **Checkout the PR branch**, start Hugo.
2. Run `node scripts/design/verify-visual.mjs`.
3. Open the screenshots. Compare to the acceptance criteria table for the relevant redesign phase in `docs/design/redesign-proposal-2026-05.md`.
4. Run `npx playwright test --config tests/visual/playwright.config.mjs` to get a diff count vs. baseline.
5. Post a PR comment (template in `.squad/skills/design-visual-verification/SKILL.md`) with:
   - The summary table (✅ / ⚠️ per cell)
   - Any mismatches against spec with screenshot attachments
   - Approve or request changes

---

## Updating Baselines

Baselines should be updated when a design change is **intentional** — i.e., a redesign phase has been approved and merged to `main`.

```bash
# After phase N merges to main:
git checkout main && git pull
hugo server -D --bind 0.0.0.0 &
npx playwright test --config tests/visual/playwright.config.mjs --update-snapshots
kill %1   # stop Hugo
git add tests/visual/snapshots/
git commit -m "chore: update visual baselines after phase N merge [skip ci]"
git push
```

**Never update baselines on a PR branch** — that defeats the purpose of regression testing.

---

## Known Limitations

| Issue | Impact | Workaround |
|-------|--------|------------|
| Cost dashboard run date | Changes every crawl — always fails snapshot diff | Suppressed via `visibility: hidden` in `NOISE_SUPPRESSION_CSS` (in both the script and spec) |
| Dynamic repo counters | Same — live data | Same suppression |
| Web font rendering | Sub-pixel differences between OS/CI | `maxDiffPixels: 150` threshold in Playwright config |
| Hugo draft pages | Pages with `draft: true` won't appear | Run Hugo with `-D` flag |
| Dynamic shortcodes | Any shortcode pulling live data will vary | Identify per-shortcode and add CSS suppression selectors |
| OS rendering differences | macOS vs Linux produce different font metrics | Always run baseline and comparison on the same OS |

---

## Files Reference

| File | Purpose |
|------|---------|
| `scripts/design/verify-visual.mjs` | Standalone capture script — no test framework needed |
| `tests/visual/playwright.config.mjs` | Playwright config for snapshot regression tests |
| `tests/visual/visual.spec.mjs` | Snapshot specs for each page |
| `tests/visual/snapshots/` | Committed baseline screenshots |
| `screenshots/design-verification/` | Ad-hoc capture output (gitignored) |
| `.squad/skills/design-visual-verification/SKILL.md` | Full skill pattern for the team |

---

*Established: 2026-05-25 — Calculon (Designer)*
