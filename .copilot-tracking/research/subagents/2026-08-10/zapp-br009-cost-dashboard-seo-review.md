# Zapp SEO Acceptance Review — BR-009 Cost Dashboard (PR #697 / commit 9af3026d)

## Research Topics / Questions

1. Does the cost-dashboard partial maintain a sane heading hierarchy (no skipped
   levels, no duplicate H1s, consistent `<h2 id="cost-dashboard-title">`) on
   both `/about/` and `/dashboard/`?
2. Could the fail-closed "unavailable" copy be mistaken by crawlers for
   stale/broken content?
3. Does this change touch any JSON-LD, meta description, or page title
   templates (accidental scope creep)?
4. Verdict: ACCEPT / ACCEPT WITH FOLLOW-UPS / NOT APPLICABLE.

## Scope Confirmation (git show --stat 9af3026d)

Files changed in the squash-merged PR #697:

* `.copilot-tracking/changes/2026-08-08/claracle-post-relaunch-consolidation-changes.md`
* `.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md`
* `assets/css/common/cost-dashboard.css`
* `data/metrics/cost-summary.json` (deleted — hand-authored placeholder removed)
* `layouts/partials/cost-dashboard.html` (the rendering logic under review)
* `tests/test_cost_dashboard_rendering.py`

`content/about/_index.md` and `content/dashboard.md` were **not** modified by
this commit — the `{{< cost-dashboard >}}` shortcode embedding predates this
PR. Neither `layouts/partials/seo.html`, `layouts/partials/templates/opengraph.html`,
`layouts/partials/templates/schema_json.html`, nor any front-matter file was
touched. Confirms no scope creep into SEO/meta/structured-data surfaces.

## Heading Hierarchy — `layouts/partials/cost-dashboard.html`

Both branches (unavailable state, lines ~101-107; available state, lines
~118-150) emit exactly one heading each:

```html
<p class="section-topline">Pipeline transparency</p>
<h2 id="cost-dashboard-title">AI pipeline cost</h2>
```

* Only ever one `<h2 id="cost-dashboard-title">` per page render (the shortcode
  is invoked once per page). No duplicate ids within a single document.
* No `<h1>` is emitted by the partial. Page `<h1>` comes from
  `layouts/_default/single.html:8` (`<h1 class="post-title entry-hint-parent">{{ .Title }}</h1>`),
  which both `/about/` and `/dashboard/` use (dashboard.md sets `layout: "single"`
  explicitly; about uses the default single template for its section).
* `layouts/partials/anchored_headings.html` only post-processes headings that
  already carry an explicit `id="..."` attribute
  (regex: `(<h[1-6] id="([^"]+)".+)(</h[1-6]+>)`), appending a hidden `#`
  anchor link. Since `cost-dashboard-title` is the only explicit id in this
  partial and doesn't collide with goldmark's auto-slugged ids for the
  page's own markdown headings (`about-claracle`, `pipeline-transparency`),
  this is safe — no anchor collision, no duplicate-id violation.

### `/about/` page heading sequence (content/about/_index.md)

1. H1 "About" (page title, from front matter)
2. H2 "About Claracle" (markdown `## About Claracle`)
3. H2 "Pipeline transparency" (markdown `## Pipeline transparency`)
4. H2 "AI pipeline cost" (`id="cost-dashboard-title"`, from the partial)

No skipped levels (H1 → H2 → H2 → H2), no duplicate H1. Structurally sound.

**Minor nit (not a structural defect):** the partial's eyebrow line
`<p class="section-topline">Pipeline transparency</p>` repeats, verbatim, the
text of the markdown H2 immediately preceding it in `content/about/_index.md`.
This is a `<p>`, not a heading, so it does not create a duplicate-heading
problem, but it is a redundant on-page string right above the H2 it
duplicates. This is a pre-existing content-authoring pattern (the `.section-topline`
"eyebrow" convention mirrors `layouts/_default/single.html`'s own
`{{ .Type | humanize }}` eyebrow above the page H1), not something introduced
newly in this diff — the diff only changed the data-rendering logic inside
the section, not this markup shape.

### `/dashboard/` page heading sequence (content/dashboard.md)

1. H1 "AI Pipeline Cost" (page title, from front matter)
2. (plain paragraph — no heading)
3. H2 "AI pipeline cost" (`id="cost-dashboard-title"`, from the partial)

No skipped levels, no duplicate H1. The H1 title ("AI Pipeline Cost") and the
partial's H2 ("AI pipeline cost") are near-identical text — a soft, cosmetic
title/heading echo, common and generally harmless for SEO (search engines
routinely see H1/H2 text overlap on focused single-topic pages). Not a defect.

## Fail-Closed "Unavailable" State — Indexing Risk Assessment

```html
<section class="cost-dashboard cost-dashboard--unavailable" aria-labelledby="cost-dashboard-title">
  <div class="cost-dashboard__header">
    <p class="section-topline">Pipeline transparency</p>
    <h2 id="cost-dashboard-title">AI pipeline cost</h2>
  </div>
  <p>Cost data is not currently available. ...</p>
</section>
```

* This is a static-site build-time render decision (Hugo), not a runtime
  error page: there is no HTTP error status, no `noindex` meta, no
  `robots.txt` exclusion tied to this state. If a production build happens to
  run while `data/metrics/cost-summary.json` is missing/stale/malformed, the
  literal "Cost data is not currently available." sentence gets baked into
  the deployed HTML for both `/about/` and `/dashboard/` until the next
  successful rebuild with valid data.
* The copy itself is self-explanatory and not alarmist or error-like
  ("...republishes automatically once fresh data clears the freshness and
  reconciliation checks") — a crawler or a human reading a cached snapshot
  would reasonably interpret this as "data pending," not "broken page" or
  "thin/spam content."
* Because Production activation (wiring `scripts/generate_cost_summary.py`
  into `crawl-and-publish.yml`) is explicitly still blocked per this commit's
  message ("Production activation ... remains blocked on the sponsor's
  legacy-row exclusion policy decision and is intentionally not part of this
  change"), the unavailable state is very likely to be **the currently live
  state in production** until that follow-up work lands. That means both
  `/about/` and `/dashboard/` may currently ship the "not currently
  available" copy in production, indexable as-is.
* This is a low-severity, by-design condition (deliberate fail-closed
  behavior per BR-009's acceptance criteria), not a bug introduced by this
  diff. It does not corrupt page structure, misrepresent the page's primary
  topic, or trigger duplicate-content/thin-content penalties on its own —
  but if it persists for an extended period in production it is worth a
  light-touch follow-up (see below).

## Structured Data / Meta / Title Impact

* `layouts/partials/seo.html` (meta description, OpenGraph, Twitter card,
  JSON-LD `BreadcrumbList`/`Article`/`CollectionPage`/`Dataset`/etc.) derives
  entirely from front matter (`.Title`, `.Description`, `.Params.summary`)
  and site-level config — none of it reads `.Site.Data.metrics."cost-summary"`
  or anything from `cost-dashboard.html`.
* `cost-dashboard.html` is rendered strictly inside `.Content` /
  `post-content md-content` (via the shortcode → `.Content` → `anchored_headings.html`
  pipeline in `layouts/_default/single.html`), which sits below the
  `<header>` block where SEO meta/JSON-LD partials are invoked. There is no
  code path from `cost-dashboard.html` back into `<head>` or into any
  `application/ld+json` block.
* Confirmed via `git show --stat`: no SEO/meta/schema template files were
  touched by PR #697.

## Verdict

**ACCEPT WITH FOLLOW-UPS** (no blocking SEO issue; one operational watch-item).

* No heading-hierarchy defect, no duplicate H1, no id collisions, no
  structured-data/meta/title scope creep. The change is a pure data-rendering
  correctness fix (BR-009 schema alignment + fail-closed validation) and has
  no meaningful negative SEO surface area on its own.
* Follow-up (non-blocking, track for the pipeline-activation work, not this
  PR): once `scripts/generate_cost_summary.py` is wired into
  `crawl-and-publish.yml`, verify production rebuilds land soon enough that
  `/about/` and `/dashboard/` are not serving the "Cost data is not currently
  available" copy to crawlers for extended stretches. Consider whether the
  redundant `section-topline`/H2 text duplication on `/about/` (eyebrow line
  repeating the immediately preceding markdown H2) is worth a copy tweak —
  cosmetic only, no urgency.

## Clarifying Questions

None required to answer the assigned scope — all four questions were
answerable via direct source inspection and `git show`.
