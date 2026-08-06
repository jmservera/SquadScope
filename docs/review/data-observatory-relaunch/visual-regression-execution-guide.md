<!-- markdownlint-disable-file -->

# Phase 7.3: Visual Regression Evidence Guide

**Date**: 2026-08-06
**Status**: Capture automated in CI; named visual review outstanding

---

## What this suite does

`tests/visual/observatory-visual-regression.spec.mjs` captures revision-tagged
visual evidence for the Data Observatory relaunch and asserts two structural
invariants the relaunch review depends on:

- Every non-home route renders a real breadcrumb: a `nav.breadcrumbs` element
  containing an `ol` with `list-style-type: none`, a flex or grid layout, and a
  terminal `[aria-current="page"]` label.
- No route overflows horizontally at any viewport in the matrix.

It does **not** perform pixel-diff comparison against committed baselines. There
are no `toHaveScreenshot()` assertions and no `snapshots/` directory to update,
so `--update-snapshots` has no effect on this spec. Regression detection is by
named review of the per-revision evidence matrix.

Analytics consent behavior is intentionally not re-asserted here; it is covered
by the blocking `observatory-analytics.spec.mjs` gate.

## Coverage matrix

Routes are resolved at collection time from the built `public/sitemap.xml`, so
dated sections do not rot as weekly and monthly editions roll over.

| Route key | Selection rule |
| --- | --- |
| `home` | `/` |
| `about` | `/about/` |
| `dashboard` | `/dashboard/` |
| `search` | `/search/` |
| `charts` | `/charts/` |
| `repo-index` | `/repo/` |
| `repo-detail` | first `/repo/<slug>/` in sitemap order |
| `topic` | first `/topics/<slug>/` in sitemap order |
| `weekly` | most recent `/weekly/<yyyy>/w<ww>/` |
| `monthly` | most recent `/monthly/<yyyy>/<mm>/` |

Any candidate route absent from the sitemap is skipped rather than failing the
run. If the sitemap is unavailable, the suite falls back to `/` alone.

The Playwright config defines four projects, all Chromium-based:

| Project | Viewport | Color scheme |
| --- | --- | --- |
| `desktop-light` | 1280x800 | light |
| `desktop-dark` | 1280x800 | dark |
| `mobile-light` | Pixel 5 | light |
| `mobile-dark` | Pixel 5 | dark |

With 10 resolved routes this yields **40 screenshots plus 4 metadata files**
per run. Firefox and WebKit are not configured; earlier revisions of this guide
claimed a three-browser, 162-variant matrix that the configuration never
supported.

## Execution

### CI (primary path)

`.github/workflows/ci.yml` runs the suite in the `production-site` job, after
the axe and responsive gates and against the same served production build:

```yaml
- name: Capture visual regression evidence
  run: npx --no-install playwright test --config tests/visual/playwright.config.mjs tests/visual/observatory-visual-regression.spec.mjs
```

Output is uploaded under `screenshots/visual-regression/` inside the
`production-quality-reports` artifact (30-day retention).

### Local

```bash
export HUGO_PARAMS_GA_MEASUREMENT_ID=G-TEST-OBSERVATORY
hugo --minify --baseURL "http://127.0.0.1:1313/"
python3 scripts/serve_static.py --directory public --bind 127.0.0.1 --port 1313 &

npm install --no-save --no-package-lock "@playwright/test@1.54.2"
npx playwright install --with-deps chromium

BASE_URL=http://127.0.0.1:1313 npx --no-install playwright test \
  --config tests/visual/playwright.config.mjs \
  tests/visual/observatory-visual-regression.spec.mjs
```

Set `HUGO_PARAMS_GA_MEASUREMENT_ID` as shown; the checked-in default is empty for
forks, and the analytics gate in the same suite requires the test measurement ID.

A local capture records the git HEAD and branch in `metadata.json` so it can still be
tied to a revision. See the
[2026-08-06 local acceptance evidence](local-acceptance-evidence-2026-08-06.md) for a
worked example.

On Debian and Ubuntu hosts, Chromium additionally requires `libnspr4` and
`libnss3`. `playwright install --with-deps` installs them; otherwise the browser
fails to launch.

## Evidence layout

```text
screenshots/visual-regression/
├── desktop-light/
│   ├── home.png
│   ├── about.png
│   ├── ... (one per resolved route)
│   └── metadata.json
├── desktop-dark/
├── mobile-light/
└── mobile-dark/
```

Each `metadata.json` records the provenance needed to tie evidence to a revision:

```json
{
  "revision": "<GITHUB_SHA, else local git HEAD>",
  "branch": "<GITHUB_REF_NAME, else local git branch>",
  "origin": "ci | local",
  "workingTreeClean": true,
  "runId": "<GITHUB_RUN_ID or null>",
  "timestamp": "<ISO 8601>",
  "project": "desktop-light",
  "colorScheme": "light",
  "viewport": { "width": 1280, "height": 800 },
  "playwrightVersion": "1.54.2",
  "routes": [{ "name": "home", "path": "/" }]
}
```

These paths are gitignored. Evidence lives in CI artifacts, not in the tree.

## Visual acceptance checklist

For a named reviewer (Amy for visual design, Fry for QA):

- [ ] Obtain the evidence set: download `production-quality-reports` from a successful
  `main` CI run, or use a local capture when CI is unavailable.
- [ ] Confirm `metadata.json` revision matches the revision under review.
- [ ] For a local capture, confirm `workingTreeClean` is `true`; a dirty tree means the
  screenshots do not correspond to the recorded revision alone.
- [ ] Confirm all four project directories are present and populated.
- [ ] Review each route across light and dark at desktop and mobile.
- [ ] Confirm breadcrumbs render as chevron-separated links with no list markers.
- [ ] Confirm no clipped, overlapping, or overflowing content.
- [ ] Record the disposition in [status-of-record.md](./status-of-record.md).

## Cross-references

- Suite: [`tests/visual/observatory-visual-regression.spec.mjs`](../../../tests/visual/observatory-visual-regression.spec.mjs)
- Config: [`tests/visual/playwright.config.mjs`](../../../tests/visual/playwright.config.mjs)
- CI workflow: [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml)
- Status: [status-of-record.md](./status-of-record.md)
