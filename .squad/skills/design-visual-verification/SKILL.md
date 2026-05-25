---
name: "design-visual-verification"
description: "Visually verify that what Amy ships matches what Calculon specified — screenshot diffs at viewport × theme × page matrix using Playwright."
domain: "design, frontend, testing"
confidence: "low"
source: "manual"
tools: []
---

## Context

Before approving any frontend PR that changes layouts, typography, components, or theme tokens, Calculon runs a Playwright screenshot pass against the live Hugo preview of the PR branch. Screenshots are diffed against a baseline saved on `main`. Mismatches are compared against the acceptance criteria in `docs/design/redesign-proposal-2026-05.md`.

This skill was established 2026-05-25. Bump confidence to **medium** after it has been used successfully on 2+ PRs.

---

## When to Use

- Any frontend PR touching: CSS/design tokens, Hugo templates, layout, typography, spacing, color, dark-mode overrides, or the cost-dashboard shortcode.
- After each redesign phase (#170–#175) lands — update baseline immediately so the next phase starts clean.
- **Do not skip** even for "small" changes — a one-line token change can affect every heading on every page.

---

## Workflow

### 1. Checkout the PR branch and start Hugo

```bash
git checkout <pr-branch>
hugo server -D --bind 0.0.0.0
# Hugo serves at http://localhost:1313/SquadScope/ by default
```

Wait for Hugo to print `Web Server is available at …` before running the script.

### 2. Run the verification script

```bash
# Run with default base URL (http://localhost:1313/SquadScope/)
node scripts/design/verify-visual.mjs

# Or specify a different base URL
node scripts/design/verify-visual.mjs --base http://localhost:1313/SquadScope/
```

Screenshots land in `screenshots/design-verification/YYYY-MM-DD/`.

### 3. Diff against main baseline

```bash
# Checkout main baseline first time (or use git stash approach)
git stash
hugo server -D --bind 0.0.0.0 &
node scripts/design/verify-visual.mjs --out screenshots/baseline/
git stash pop
```

Compare the two `screenshots/` folders visually (Preview / Finder diff, or use `pixelmatch` CLI).

For structured regression, run via Playwright snapshot mode:

```bash
# Generate/update baseline on main
npx playwright test tests/visual/ --update-snapshots

# On PR branch — test against baseline
npx playwright test tests/visual/
```

### 4. Compare against acceptance criteria

Open `docs/design/redesign-proposal-2026-05.md`. Each phase has an **Acceptance Criteria** section. For each viewport × theme screenshot, check:

- Heading typescale matches spec (`--heading-xl`, `--heading-lg`, etc.)
- Accent color, bg, and text color match palette tokens
- No unexpected overflow or scroll bars at mobile (375px)
- Dark mode: no near-black-on-black contrast failures
- Cost dashboard date element is hidden in screenshots (see Pitfalls)

### 5. Comment on the PR

Post a PR comment containing:

```markdown
## 🎨 Visual Verification — Calculon Review

| Page | Viewport | Light | Dark | Notes |
|------|----------|-------|------|-------|
| `/` | 375 | ✅ / ⚠️ | ✅ / ⚠️ | … |
| `/` | 768 | | | |
| `/` | 1280 | | | |
| `/` | 1920 | | | |
| `/weekly/2026/w22/` | … | | | |
| `/monthly/2026/05/` | … | | | |
| `/yearly/2026/` | … | | | |

### Mismatches against spec
- [ ] List any deviations from `docs/design/redesign-proposal-2026-05.md` acceptance criteria

**Decision:** ✅ Approved / 🔄 Changes requested
```

---

## Viewport Matrix

| Name | Width | Height |
|------|-------|--------|
| mobile | 375 | 667 |
| tablet | 768 | 1024 |
| desktop | 1280 | 800 |
| wide | 1920 | 1080 |

---

## Theme Matrix

| Theme | Playwright setting |
|-------|--------------------|
| light | `page.emulateMedia({ colorScheme: 'light' })` |
| dark | `page.emulateMedia({ colorScheme: 'dark' })` |

---

## Pages Matrix

| Key | Path |
|-----|------|
| home | `/` |
| latest-weekly | `/weekly/2026/w22/` |
| monthly-rollup | `/monthly/2026/05/` |
| yearly-rollup | `/yearly/2026/` |

---

## Patterns

### Navigate, emulate, screenshot

```js
import { chromium } from 'playwright';

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: 1280, height: 800 },
  colorScheme: 'dark',   // or 'light'
});
const page = await context.newPage();

// Wait for fonts to load before screenshotting
await page.goto('http://localhost:1313/SquadScope/');
await page.waitForLoadState('networkidle');

// Hide dynamic elements that create screenshot noise
await page.addStyleTag({ content: '.cost-dashboard__date { visibility: hidden !important; }' });

await page.screenshot({ path: 'home-1280-dark.png', fullPage: true });
await browser.close();
```

### Playwright Test snapshot assertion

```ts
// tests/visual/home.spec.ts
import { test, expect } from '@playwright/test';

test('home — desktop — dark', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  await page.addStyleTag({ content: '.cost-dashboard__date { visibility: hidden !important; }' });
  await expect(page).toHaveScreenshot('home-desktop-dark.png', { maxDiffPixels: 150 });
});
```

### Update snapshots after intentional design change

```bash
npx playwright test tests/visual/ --update-snapshots
git add tests/visual/*.spec.ts-snapshots/
git commit -m "chore: update visual baselines for phase N"
```

---

## Anti-Patterns

- **Don't screenshot before `networkidle`** — fonts and theme CSS may not have applied yet, producing false diffs.
- **Don't leave the cost-dashboard date visible** — it changes every run and will always fail snapshot comparison. Hide it with `page.addStyleTag`.
- **Don't set `maxDiffPixels: 0`** — sub-pixel anti-aliasing differences on text will produce constant noise. Start at 150 and tighten per page.
- **Don't compare across OS/CI and local** — browser rendering differs. Always run baseline and comparison in the same environment.
- **Don't approve a PR without running dark mode** — dark-mode bugs are invisible in light screenshots.

---

## Pitfalls

1. **Font rendering noise** — Use `page.waitForLoadState('networkidle')` and consider adding a small `page.waitForTimeout(500)` after load to ensure web fonts have rendered before capturing.
2. **Dynamic date in cost dashboard** — The `{{< cost-dashboard >}}` shortcode displays a run date. Hide or mock this element via `page.addStyleTag` before screenshotting.
3. **Run counters / live data** — Any element showing "last crawl N repos" is dynamic. Add `.dynamic-counter { visibility: hidden !important; }` to the style injection.
4. **Hugo draft pages** — Run `hugo server -D` (the `-D` flag) to include draft content matching the pages matrix.
5. **Pixel diff thresholds** — Set `maxDiffPixels: 150` as default; tighten to 50 once stable; loosen temporarily for pages with many text nodes if needed.

---

## Confidence Bump Criteria

- **low → medium:** Used successfully on 2+ merged frontend PRs. At least one mismatch caught and fixed by the process.
- **medium → high:** Baseline management is automated in CI (not just local); thresholds are stable; no false positives in 5+ consecutive PRs.
