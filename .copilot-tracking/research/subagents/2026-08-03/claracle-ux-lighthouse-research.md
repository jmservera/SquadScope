<!-- markdownlint-disable-file -->

# Claracle UX and Lighthouse issue research

## Research scope

* Investigate open issue #622 against current `main` for Star Velocity bar scaling intent or defect, topics index aggregation in a production-representative state, and mobile consent placement.
* Investigate open issue #626 and map its five requested improvements to current files and tests.
* Identify the smallest safe source changes and focused validation without editing source files.

## Baseline

* Research was performed on `main` at `4b7c5cf506b2e8b73350ff94ce80669c93810e66`, which matched local `HEAD` and `origin/main` when checked.
* Existing unrelated working-tree changes were not modified.
* Issue [#622](https://github.com/jmservera/SquadScope/issues/622) is open and explicitly classified as non-blocking UX polish.
* Issue [#626](https://github.com/jmservera/SquadScope/issues/626) is open and requires five independently shippable hardening changes. Performance 90, accessibility 95, best-practices 95, and CLS 0.1 must remain unchanged.
* Current-main CI run [30839710156](https://github.com/jmservera/SquadScope/actions/runs/30839710156) passed at the exact researched revision and retained the production-quality Lighthouse reports.

## Issue #622 findings

### Star Velocity bar scaling

Verdict: the bars are not normalized per row. Point-to-bar binding uses the correct raw `point.stars` value, but the presentation has an undocumented hard-coded global scale and clips valid data.

* assets/js/star-velocity-explorer.js sets each height to `point.stars / 2500` percent, clamped to 6 through 100 percent. The visual floor is 15,000 stars and the ceiling is 250,000 stars.
* assets/css/extended/trend-explorer.css gives every bar a fully rounded top through `border-radius: 999px 999px 0 0`, producing the dome appearance cited by the issue.
* The current static/tools/star-velocity-explorer.json contains 100 repositories and 990 points. One point hits the floor, 85 points exceed the ceiling, and eight repositories have every observation clipped to 100 percent.
* The top rows are not uniformly normalized. For example, `mattpocock/skills` renders from 36.1 to 80.0 percent, `obra/superpowers` from 78.3 to 100 percent, and `pewdiepie-archdaemon/odysseus` from 6 to 32.4 percent.
* docs/decisions/adr-star-velocity-explorer.md calls the sparkline an observed-history visualization and says the UI labels observed star change and latest stars. It does not define per-row normalization or the 250,000-star ceiling.
* scripts/export_trend_explorer_data.py calculates velocity as latest observed stars minus first observed stars. The sparkline intentionally receives absolute history points, while ranking and metadata use the derived change.

The defect is therefore the arbitrary saturating scale and unclear visual semantics, not a wrong field lookup. Converting the chart to per-row normalization would be a new product decision and would prevent cross-repository height comparison.

Smallest safe change:

* In assets/js/star-velocity-explorer.js, derive one stable maximum from the complete payload and pass it into `renderRows`; scale raw history points against that maximum instead of 250,000. Do not derive the maximum from the filtered subset because filtering would change a repository's apparent height.
* Add visible helper text and an accessible sparkline label stating that heights represent absolute observed stars scaled to the dataset maximum. Keep the existing tooltip values.
* In assets/css/extended/trend-explorer.css, use a modest fixed top radius instead of a pill radius.
* Extend tests/test_trend_explorer_tool.py so the Node fixture verifies low, intermediate, and maximum values produce ordered, unclipped heights and that the scale does not change after filtering.

If product ownership wants velocity rather than absolute history, compute each point's change from the repository's first observation and scale all deltas against the dataset-wide maximum observed change. That is semantically stronger but broader than the issue's smallest corrective change.

### Topics index aggregation

Verdict: the Hugo aggregation key is correct. The original empty state is stale, but current main and production are not equivalent because deployment hydrates generated content from `origin/publish`.

* layouts/topics/terms.html reads `site.Taxonomies.topics.ByCount`, uses Hugo's normalized term name to resolve `/topics/<urlized-term>`, and then uses the same URLized key for display metadata from data/taxonomy/topics.json. There is no separate weekly-to-seed string join to repair.
* hugo.toml defines the singular `topic` taxonomy over `topics` frontmatter.
* Current main has canonical topics on W21 through W32. A current-main build should produce five hubs with counts AI Coding Agents 12, Developer Tools 4, Open-Source LLMs 4, MCP Ecosystem 2, and AI Agents in Healthcare 1.
* The ignored checked-in public/topics/index.html is one week old but proves the layout works: it renders all five hubs at 11, 3, 4, 2, and 1. public/topics/mcp-ecosystem/index.html includes W21 and W26.
* Live <https://claracle.com/topics/> is populated, not empty, but currently shows only AI Coding Agents and Developer Tools with one issue each.
* Production's state is reproducible from `origin/publish` at `4120078d`. Only W32 has `topics` frontmatter there. Its taxonomy registry records one AI Coding Agents issue, one Developer Tools issue, and zero for the other promoted hubs.
* .github/workflows/deploy-site.yml replaces content/weekly, content/topics, and data/taxonomy from `origin/publish` before Hugo builds. The production result is therefore correct for its hydrated input, while current main's historical topic backfill never reaches production.
* The `publish-hydration-parity` job in .github/workflows/ci.yml checks embed and promotion references after hydration but does not build Hugo or assert taxonomy membership.

Smallest safe change:

* Do not change layouts/topics/terms.html.
* Promote the canonical W21 through W31 topic backfill and matching data/taxonomy/topics.json state to `publish` through the existing generated-content transaction. Do not hand-edit or weaken the frozen weekly pipeline.
* Add a hydration-aware rendered regression test to the `publish-hydration-parity` job. After reproducing hydration, build Hugo and assert that every promoted hub with a positive registry count appears on `/topics/`, with MCP containing W21 and W26. A lighter alternative is a Python parity check between hydrated weekly frontmatter and registry counts, but a rendered assertion protects the exact defect users saw.
* Keep tests/test_topic_hubs.py for current-main lifecycle and RSS behavior; add production hydration coverage rather than overloading its source-only fixture.

### Mobile consent placement

Verdict: current placement is bottom-anchored and keeps page identity visible, but it covers the first page action and has no occlusion regression test.

* layouts/partials/cookie-consent.html configures CookieConsent `cloud inline` at `bottom center`.
* assets/css/extended/cookieconsent-theme.css changes theme, shadow, and 44 px target sizing but does not override mobile geometry.
* The retained mobile Lighthouse final screenshot for the topic route shows the title and description fully above the dialog. The dialog covers the topic subscription control and lower content.
* tests/visual/observatory-a11y.spec.mjs verifies focus trapping and restoration only on the desktop-light project.
* tests/visual/a11y-perf.spec.mjs checks overflow and touch targets across 320, 360, 390, 414, and 768 px widths, but does not compare dialog and primary-content bounds.

Smallest safe change:

* Add a fresh-consent mobile matrix test in tests/visual/observatory-a11y.spec.mjs. Assert the dialog is fully inside the viewport, has no horizontal overflow, exposes all three actions, can scroll its description, and starts below the page header's bottom edge.
* Treat the current layout as acceptable if the title and description define primary content. If the subscription control must also remain visible, product ownership must choose between shorter consent copy, a more compact mobile layout, or reserved page space; CSS repositioning alone only moves the occlusion.

## Issue #626 mapping

### Extend lean page CSS bundles

Current state:

* layouts/partials/head.html only recognizes `.Type == "tools"`.
* Tool pages exclude article-visuals.css and observatory-charts.css, then emit assets/css/extended-tools.css and assets/css/stylesheet-tools.css.
* Search, about, methodology, and privacy still receive the full extended bundle even though their layouts do not render those visual components.
* About uses the cost dashboard, but its CSS is in assets/css/common/cost-dashboard.css and remains in the core bundle.

Smallest safe change:

* In layouts/partials/head.html, introduce one lean-page predicate covering tool type, search layout, and the about, methodology, and privacy section types. Reuse the existing exclusions and lean target names because the resulting bundle contents are identical.
* Add a rendered bundle test, preferably tests/test_page_css_bundles.py, that builds Hugo and verifies the five lean routes share the lean stylesheet, representative weekly/data routes use the full stylesheet, and the lean asset omits `.article-visual` and `.observatory-chart` selectors while retaining each page's required selectors.

Validation: Hugo production build, rendered bundle test, internal links, Playwright responsive suite, and all nine unchanged Lighthouse gates.

### Add Brotli to the production-like server

Current state:

* scripts/serve_static.py defines `GzipHandler`, checks for the substring `gzip`, and compresses eligible responses at level 6.
* No Brotli package exists in requirements.txt or pyproject.toml.
* tests/test_pipeline.py only verifies CI uses scripts/serve_static.py rather than `http.server`; no response-level server tests exist.

Smallest safe change:

* Add a constrained Brotli codec dependency to requirements.txt.
* Rename the handler to a compression-neutral name, parse `Accept-Encoding` quality values, prefer `br`, fall back to gzip, and leave binary or unaccepted responses uncompressed. Preserve `Content-Length`, `HEAD`, redirect sanitization, and `Vary: Accept-Encoding` behavior.
* Add tests/test_serve_static.py with a temporary server and fixtures for Brotli, gzip fallback, `br;q=0`, identity, binary content, `HEAD`, `Vary`, and decompression fidelity.
* Keep the .github/workflows/ci.yml server command unchanged unless the handler's public class name is referenced by tests only.

Validation: the new server tests, pip audit, curl requests with `Accept-Encoding: br`, gzip, and identity, followed by the unchanged Lighthouse suite.

### Document Lighthouse methodology

Current state:

* scripts/design/lighthouse-gates.mjs runs nine mobile routes, three times each, and gates medians at the unchanged thresholds.
* .github/workflows/ci.yml serves a production Hugo build through scripts/serve_static.py before Playwright and Lighthouse, then uploads per-page reports and summary.json.
* docs/qa-gates.md only documents map/reduce acceptance criteria.
* docs/design/visual-verification.md is stale: it describes four Lighthouse routes and omits the performance threshold and median-of-three/compressed-server rationale.

Smallest safe change:

* Add a Lighthouse section to docs/qa-gates.md covering the nine routes, mobile form factor, median-of-three calculation, representative report selection, compressed local server, artifact paths, thresholds, and failure interpretation.
* Update the conflicting Lighthouse subsection in docs/design/visual-verification.md in the same change.
* No executable behavior change is required.

Validation: Markdown checks and a manual comparison against scripts/design/lighthouse-gates.mjs and .github/workflows/ci.yml.

### Tighten data-page CLS

Current state and correction to the issue premise:

* Current-main CI reports data CLS `0.0395178947`, the highest of the nine routes but below 0.1.
* The retained `cls-culprits-insight` attributes the entire shift to Inter loading from `fonts.gstatic.com`; the shifted node is `section.data-page__provenance`.
* layouts/data/single.html renders provenance and a ranking table. It does not render an Observatory chart.
* assets/css/extended/data-pages.css has no missing chart container to reserve.
* layouts/partials/head.html requests Google Fonts with `display=swap`, which permits the measured late font swap.

Smallest safe change:

* Do not add guessed chart space.
* Change the Google Fonts request in layouts/partials/head.html from `display=swap` to `display=optional`, then compare all nine routes. This prevents a late swap when the font misses the short optional-use window and is the smallest change aimed at the observed culprit.
* If retaining Inter on every first visit is more important than the CLS margin, self-host and preload the required WOFF2 files with metric-compatible fallback overrides. That is a larger follow-up, not the first safe change.

Validation: run median-of-three Lighthouse at least twice on the data route and once on the full matrix; inspect `cls-culprits-insight`, not only the aggregate score. Confirm typography in desktop/mobile and light/dark Playwright screenshots.

### Parallelize per-page Lighthouse execution

Current state:

* scripts/design/lighthouse-gates.mjs uses synchronous `execSync` and a serial `for` loop over nine pages. Each page runs its three samples sequentially.
* Per-page report names and final aggregate failure reporting already provide deterministic artifact boundaries.
* .github/workflows/ci.yml invokes the script once and needs no job-matrix expansion.

Smallest safe change:

* Replace the synchronous child process with an async `execFile` or `spawn` wrapper.
* Add bounded page concurrency, defaulting to three and configurable with `--concurrency`. Keep each page's three runs sequential so median samples for one page do not compete with each other.
* Preserve PAGES order when writing summary.json and the console table, wait for every page before evaluating failures, and retain one representative report per page.
* Avoid `Promise.all` over all 27 Chrome runs; unrestricted concurrency can increase noise and memory pressure enough to defeat the gate's stability goal.
* Add Node built-in tests for median/failure logic and bounded result ordering if helpers are extracted. The decisive validation remains repeated CI comparison of score variance, artifacts, failures, and wall-clock duration.

Validation: run `--runs 1 --concurrency 1` versus `--runs 1 --concurrency 3`, then the default median-of-three matrix twice. Confirm identical page order and threshold decisions, nine per-page reports, one summary, lower wall-clock time, and no increase in flaky scores.

## Validation performed

* Fetched the public issue bodies for #622, #626, and originating issue #605.
* Confirmed current `HEAD`, `main`, and `origin/main` all pointed to `4b7c5cf` before the research.
* Compared current-main weekly frontmatter, ignored public output, live production, and `origin/publish` at `4120078d`.
* Quantified current Star Velocity floor and ceiling saturation with `jq` against static/tools/star-velocity-explorer.json.
* Downloaded and inspected current-main CI run 30839710156's summary and data-page `cls-culprits-insight` report.
* Inspected the retained mobile Lighthouse final screenshot for the topic route.
* Ran `uv run --no-sync pytest -q tests/test_trend_explorer_tool.py tests/test_topic_hubs.py tests/test_pipeline.py`: 49 passed, 3 skipped, and 19 subtests passed. The three Hugo-dependent tests skipped because Hugo is not installed locally.

## Recommended validation after implementation

```bash
uv run --no-sync pytest -q \
  tests/test_trend_explorer_tool.py \
  tests/test_topic_hubs.py \
  tests/test_page_css_bundles.py \
  tests/test_serve_static.py \
  tests/test_pipeline.py
```

```bash
hugo --minify --baseURL http://127.0.0.1:1313/
npx pagefind@1.5.2 --site public/
uv run --no-sync python scripts/serve_static.py \
  --directory public --bind 127.0.0.1 --port 1313
```

With the server running:

```bash
BASE_URL=http://127.0.0.1:1313 \
  npx --no-install playwright test \
  --config tests/visual/playwright.config.mjs \
  tests/visual/a11y-perf.spec.mjs \
  tests/visual/observatory-a11y.spec.mjs
```

```bash
node scripts/design/lighthouse-gates.mjs \
  --base http://127.0.0.1:1313 \
  --runs 3 \
  --concurrency 3
```

Also run the repository-mandated `ruff check .`, `ruff format --check .`, full `pytest tests/`, `hugo --minify`, and PR Production site job. Do not lower thresholds to absorb any regression.

## Recommended next research

* [ ] Ask product ownership whether the first subscription action, rather than the title and description, must remain visible behind fresh consent on short mobile viewports.
* [ ] If global absolute-star scaling is rejected, choose and document dataset-wide velocity-delta scaling before implementation.
* [ ] Measure median Lighthouse wall-clock time and score variance for bounded concurrency values two and three on GitHub-hosted runners.
* [ ] Confirm the canonical generated-content procedure for promoting the W21 through W31 topic backfill to `publish` without bypassing the frozen weekly pipeline.

## Clarifying questions

* Is the Star Velocity sparkline intended to compare absolute repository size across rows, or weekly/cumulative star gain? Existing code and ADR establish absolute observed history but do not state the visual comparison contract.
* Does “primary content” for consent placement include the topic subscription control, or only the page title and description?
