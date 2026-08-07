<!-- markdownlint-disable-file -->

# Phase 7.3: Visual Regression Evidence Guide

**Date**: 2026-08-06
**Status**: Capture automated in CI; named visual review outstanding

---

## What this suite does

`tests/visual/observatory-visual-regression.spec.mjs` is both a blocking gate and
the producer of the visual evidence matrix. Calling it "evidence collection" alone
understates it: a structural failure fails the build.

As a gate it asserts:

- Every route returns an HTTP status below 400.
- Every non-home route with site chrome renders a real breadcrumb: a
  `nav.breadcrumbs` element containing an `ol` with `list-style-type: none`, a flex
  or grid layout, and a terminal `[aria-current="page"]` label.
- No route overflows horizontally at any viewport in the matrix.
- The consent banner is present on an undecided first visit.

As an evidence producer it writes one screenshot per route per project plus a
per-project `metadata.json`, and `scripts/design/build_visual_evidence_index.py`
turns that into a single review page.

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
| `topics-index` | `/topics/` |
| `topic` | first `/topics/<slug>/` in sitemap order |
| `data-detail` | first `/data/<slug>/` in sitemap order |
| `state-of` | first `/state-of/<slug>/` in sitemap order |
| `embed` | first `/embeds/<slug>/` in sitemap order; captured without site chrome |
| `tool` | first `/tools/<slug>/` in sitemap order |
| `weekly` | most recent `/weekly/<yyyy>/w<ww>/` |
| `monthly` | most recent `/monthly/<yyyy>/<mm>/` |
| `home-consent` | `/` with the consent decision deliberately left undecided |

Every route except `home-consent` rejects the consent banner before capture. The
[capture checklist](screenshots/README.md) rejects feature evidence that the banner
obscures, and rejecting keeps the captures free of analytics network activity.
The `home-consent` capture is the banner-specific evidence that checklist also requires.

Any candidate route absent from the sitemap is skipped rather than failing the
run. If no route resolves at all, behaviour depends on where it runs: locally the
suite falls back to `/` alone so a partial build still produces something, and on
CI it fails immediately. Falling back on CI would silently shrink a blocking gate
to a single route.

The Playwright config defines four projects, all Chromium-based:

| Project | Viewport | Color scheme |
| --- | --- | --- |
| `desktop-light` | 1280x800 | light |
| `desktop-dark` | 1280x800 | dark |
| `mobile-light` | Pixel 5 | light |
| `mobile-dark` | Pixel 5 | dark |

With 15 resolved routes plus the consent capture this yields **64 screenshots plus 4
metadata files** per run. Firefox and WebKit are not configured; earlier revisions of
this guide claimed a three-browser, 162-variant matrix that the configuration never
supported.

The suite captures default page state only. The interaction states the
[capture checklist](screenshots/README.md) requires, such as tool filter combinations,
expanded lifecycle detail, and keyboard focus on the internal-link block, remain a
manual reviewer step.

## Execution

### CI (primary path)

`.github/workflows/ci.yml` runs the suite in the `production-site` job, after
the axe and responsive gates and against the same served production build:

```yaml
- name: Run visual structure gate and capture evidence
  if: ${{ !cancelled() }}
  env:
    PLAYWRIGHT_REPORT_SUFFIX: -visual
  run: npx --no-install playwright test --config tests/visual/playwright.config.mjs tests/visual/observatory-visual-regression.spec.mjs

- name: Build visual evidence review index
  if: ${{ !cancelled() }}
  run: python scripts/design/build_visual_evidence_index.py
```

`PLAYWRIGHT_REPORT_SUFFIX` is required whenever a job invokes this config more than
once. Without it the second run overwrites the first run's
`screenshots/playwright-report*` and `screenshots/playwright-output`, and the axe,
analytics, and responsive reports are lost from the artifact.

Both steps run even after an earlier gate fails, because a failing build is when
the visual evidence is most worth having. They are skipped only on cancellation.
If the serve step itself failed they will fail too, which is noise on an already
red job rather than a lost signal.

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

python3 scripts/design/build_visual_evidence_index.py
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
├── index.html            # generated review page: every route with its four variants
├── desktop-light/
│   ├── home.png
│   ├── home-consent.png
│   ├── about.png
│   ├── ... (one per resolved route)
│   └── metadata.json
├── desktop-dark/
├── mobile-light/
└── mobile-dark/
```

Open `index.html` to review. It groups each route with its desktop and mobile,
light and dark variants side by side, and it flags a capture that mixes revisions or
that came from a dirty working tree.

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
- [ ] Open `index.html` from the evidence set.
- [ ] Confirm `metadata.json` revision matches the revision under review.
- [ ] For a local capture, confirm `workingTreeClean` is `true`; a dirty tree means the
  screenshots do not correspond to the recorded revision alone.
- [ ] Confirm all four project directories are present and populated.
- [ ] Review each route across light and dark at desktop and mobile.
- [ ] Confirm no capture other than `home-consent` is obscured by the consent banner.
- [ ] Confirm breadcrumbs render as chevron-separated links with no list markers.
- [ ] Confirm no clipped, overlapping, or overflowing content.
- [ ] Record the disposition in [status-of-record.md](./status-of-record.md).

## Cross-references

- Suite: [`tests/visual/observatory-visual-regression.spec.mjs`](../../../tests/visual/observatory-visual-regression.spec.mjs)
- Config: [`tests/visual/playwright.config.mjs`](../../../tests/visual/playwright.config.mjs)
- CI workflow: [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml)
- Status: [status-of-record.md](./status-of-record.md)
