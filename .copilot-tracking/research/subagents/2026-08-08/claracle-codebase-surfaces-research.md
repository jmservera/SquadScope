---
title: Claracle BRD-CLARACLE-003 Codebase Surfaces Research
description: Read-only implementation research mapping Claracle post-relaunch requirements to owning code, content, tests, workflows, and team responsibilities
author: GitHub Copilot
ms.date: 2026-08-08
ms.topic: reference
keywords:
  - claracle
  - business requirements
  - implementation planning
  - codebase research
estimated_reading_time: 15
---

<!-- markdownlint-disable-file -->

## Research Scope

Status: Complete

This research maps BR-001 through BR-009 and carried-over CR-02, CR-05, and CR-06 from BRD-CLARACLE-003 to exact implementation and validation surfaces in the SquadScope workspace.

The investigation was read-only except for this report. It examined the checked-in
`main` workspace, the local `origin/publish` tracking reference, generated Hugo
content, a clean temporary Hugo build, tests, workflows, and retained review
evidence. Counts in this report are therefore reproducible from repository state,
not estimates copied from the BRD.

## Questions

* Which files and code paths own each requirement's current behavior?
* What is the authoritative current repository-page count, and which artifact or build surface establishes it?
* Why does CR-05 conflict with BR-003?
* What root causes, dependencies, implementation risks, and cheap validation checks are supported by repository evidence?
* How do architecture boundaries and Squad ownership route the implementation and review work?

## Requirement Map

### BR-001 Cohesive visual direction

Target: replace the generic publication feel with an approved, documented visual
direction applied consistently to the homepage, articles, repository summary, and
data views. The BRD requires an explicit subject, audience, purpose, token system,
layout concept, signature element, and self-critique before implementation
(`docs/brds/claracle-post-relaunch-consolidation-brd.md:125`).

Current behavior and owning surfaces:

* `hugo.toml:1-48` establishes PaperMod, the Claracle title, summary, social image,
  theme behavior, article controls, and primary sections.
* `layouts/index.html:1-111` owns the current homepage composition: a minimal hero,
  latest issue, weekly archive, topic rail, and quick links.
* `layouts/data/single.html:1-69` owns the current data-page composition and
  crawlable ranking table.
* `layouts/partials/visuals/observatory-chart.html:1-83` owns the visual language of
  ranking charts and embeds.
* `assets/css/extended/squadscope.css:1-1117`,
  `assets/css/extended/data-pages.css:1-45`, and
  `assets/css/extended/observatory-charts.css:1-149` own the implemented homepage,
  data-page, and chart styling. The codebase does not contain a new BR-001
  design-direction record that satisfies all required frontend-design fields.
* `docs/design/visual-verification.md:1-190` documents the older redesign's visual
  verification process and current responsive, Lighthouse, and accessibility
  thresholds, but explicitly describes an already-shipped redesign rather than the
  new post-relaunch direction.

Root cause: visual components exist, but the BRD deliberately makes design intent
and sponsor selection prerequisites. This is not a defect that can be solved by a
CSS-only patch.

Dependencies and risks:

* Calculon should establish the design direction before Amy changes templates or
  tokens. Leela owns architectural cohesion, Fry owns acceptance evidence, Zapp
  reviews discoverability surfaces, and jmservera is the approval authority.
* A broad styling change affects every page type, both color schemes, reduced-motion
  behavior, screenshots, and Lighthouse. Reusing the current responsive and visual
  gates limits regression risk.

Cheap discriminating check: require the design record to name all seven BRD design
inputs, then render representative home, weekly, repository-summary, and data pages
at desktop and mobile widths before accepting implementation work.

### BR-002 Homepage content hierarchy

Target: useful, original, server-rendered entry points into weekly, monthly, yearly,
topic, repository, and data coverage, with explicit freshness and selection rules
(`docs/brds/claracle-post-relaunch-consolidation-brd.md:126`).

Current behavior and owning surfaces:

* `layouts/index.html:2-4` selects all weekly pages, the newest weekly issue, and six
  top topics.
* `layouts/index.html:12-34` renders the latest weekly report or a useful empty state.
* `layouts/index.html:37-71` renders up to six recent weekly reports.
* `layouts/index.html:73-111` renders active topics and quick links to weekly,
  topics, monthly, yearly, search, and RSS.
* The homepage does not contain original monthly, yearly, repository, or data
  modules. Monthly and yearly appear only as navigation links; repository and data
  coverage are absent from the homepage body.
* `hugo.toml:19-48` provides a site description and home info, while the homepage
  template emits one `h1` and useful HTML without JavaScript.

Root cause: the local homepage redesign optimized for the latest weekly issue and
topic discovery. It has no cross-section selection model, freshness contract, or
server-side module abstraction for the full BRD hierarchy.

Dependencies and risks:

* The audience and primary homepage job remain open BRD decisions. Calculon and Amy
  should settle hierarchy before implementation; Zapp should review unique summaries
  and metadata.
* Optional sections must not leave empty regions or cause layout shift. Repository
  and data modules also depend on the BR-003/004 artifact contracts.

Cheap discriminating check: build Hugo with one optional section removed and inspect
the rendered homepage HTML. It should retain one heading, crawlable original summaries,
working internal links to all six coverage types, and no empty module wrapper.

### BR-003 Consolidated repository summary

Target: remove the low-information repository-detail corpus and replace it with one
accessible, progressively enhanced summary backed by versioned JSON
(`docs/brds/claracle-post-relaunch-consolidation-brd.md:127`).

Current behavior and owning surfaces:

* `config/observatory.toml:1-13` keeps repository-page generation disabled while
  retaining recurrence, lifecycle, and retention settings.
* `scripts/observatory_repos.py:209-226` reads the rollout, recurrence, lifecycle,
  and retention configuration. Lines 537-666 build repository histories; lines
  736-864 build page metadata and aliases; lines 1061-1136 write the section index,
  detail bundles, derived JSON, and lifecycle ledger; lines 1159-1180 enforce the
  disabled rollout before generation.
* `content/repo/` currently contains 266 detail bundles plus `content/repo/_index.md`.
* `data/derived/observatory/repositories.json:1-89172` contains 266 repository
  records and is the strongest existing data source for a consolidated view, but it
  is not yet a documented, versioned BR-003 schema contract. The separate public
  export under `static/datasets/open-source-ai-github-projects-2026/` is a CSV and
  metadata package, not this detail-page parity artifact.
* Seven detail bundles retain aliases: `content/repo/affaan-m-ecc/index.md:283-284`,
  `content/repo/egonex-ai-understand-anything/index.md:252-253`,
  `content/repo/graphify-labs-graphify/index.md:294-295`,
  `content/repo/odysseus-dev-odysseus/index.md:202-203`,
  `content/repo/openinterpreter-openinterpreter/index.md:254-255`,
  `content/repo/react-react-native/index.md:255-256`, and
  `content/repo/react-react/index.md:248-249`.
* No repository-summary client, repository JSON schema file, no-JavaScript summary,
  or redirect/canonical inventory test currently exists.

Authoritative count reconciliation:

* 266 repository detail pages: generated bundles and JSON records. This is the count
  of low-information pages BR-003 intends to replace.
* 267 repository source pages: the 266 details plus `content/repo/_index.md`.
* 274 rendered `/repo/` HTML URLs in a clean Hugo build: 267 canonical source pages
  plus seven alias redirect pages.

The BRD phrase "approximately 267" therefore describes the source-page surface,
not 267 detail records. Implementation planning should use 266 removals, one retained
or redesigned section index, and seven explicit alias dispositions. Production and
search inventories should also be compared before redirects are finalized because a
local render cannot establish external inbound-link value.

Dependencies and risks:

* Zapp and Leela should approve redirect, canonical, sitemap, and indexability
  treatment. Amy owns the interface, Bender owns deterministic artifact generation,
  Fry owns keyboard, fallback, empty/error, and inventory tests.
* Deleting `content/repo/` before redirect and canonical policy is approved risks
  breaking indexed or linked URLs. Treat aliases independently from current canonical
  details.
* The Star Velocity Explorer supplies a suitable local pattern: versioned static JSON,
  search and filters, safe GitHub links, status messages, and deterministic generation
  (`scripts/export_trend_explorer_data.py:1-220`,
  `assets/js/star-velocity-explorer.js:1-260`,
  `tests/test_trend_explorer_tool.py:12-109`). Its server shell is not a complete
  fallback, so BR-003 must go further and emit useful repository results in HTML.

Cheap discriminating check: assert the generated artifact has 266 unique repository
identities, render the summary with JavaScript disabled, then assert a clean Hugo
build emits no canonical detail pages while every approved legacy URL resolves to its
redirect or canonical destination.

### BR-004 Interactive priority data pages

Target: agreed priority data pages use versioned JSON for accessible filtering,
sorting, charts, stable state where useful, provenance, downloads, and meaningful
server HTML (`docs/brds/claracle-post-relaunch-consolidation-brd.md:128`).

Current behavior and owning surfaces:

* `scripts/generate_data_pages.py:18-25` defines raw/archive inputs, the content
  destination, and a 100-row cap.
* `scripts/generate_data_pages.py:85-222` normalizes repository observations from
  checked-in weekly artifacts and preserves source paths.
* `scripts/generate_data_pages.py:225-260` writes rankings into TOML front matter
  rather than standalone JSON.
* `layouts/data/single.html:13-59` provides provenance and an accessible crawlable
  table with repository links. This is a sound no-JavaScript baseline.
* `layouts/partials/visuals/observatory-chart.html:14-34` serializes an inline JSON
  subset for the static chart, but no controls consume it for filtering, sorting, or
  chart exploration.
* No data-page JSON schema files were found. The current generated rankings have no
  version field, public schema contract, shareable state, or explicit client-side
  performance budget.

Root cause: Wave 2 shipped deterministic read-only pages and embeds, not the later
interactive artifact contract now requested by BR-004.

Dependencies and risks:

* The BRD leaves "priority" pages undecided. The three generated ranking pages should
  be explicitly accepted or narrowed before a shared client contract is designed.
* Reuse the repository-summary schema envelope and interaction utilities where fields
  overlap, but do not force different metrics into one opaque record type.
* Preserve the current table as the server-rendered summary and accessibility
  alternative. Client enhancement must not hide attribution or downloads.

Cheap discriminating check: disable JavaScript and verify the ranking remains useful;
then load malformed, empty, and valid versioned payloads and verify labeled controls,
stable URL state, keyboard behavior, attribution, and bounded rendering time.

### BR-005 Visualization replacement

Target: replace bar charts only where another representation better answers the
analytical question, after documenting the inventory and comparing at least two
alternatives (`docs/brds/claracle-post-relaunch-consolidation-brd.md:129`).

Current behavior and owning surfaces:

* `layouts/partials/visuals/observatory-chart.html:35-56` renders every ranking as a
  horizontal SVG bar chart scaled to the maximum value.
* `layouts/partials/visuals/observatory-chart.html:37-40` supplies an SVG title and
  description, while `layouts/data/single.html:31-59` supplies the full accessible
  table alternative.
* `layouts/partials/cost-dashboard.html:14-24` separately renders a weekly cost
  polyline, showing the codebase already distinguishes a trend from a ranking.
* The repository contains no BR-005 chart inventory, analytical-question record, or
  comparison of two representations against representative data.

Root cause: one reusable ranking partial was intentionally chosen for all Observatory
rankings. The BRD now requires an evidence-led visualization decision before code
replacement.

Dependencies and risks:

* Calculon and Amy own the decision and implementation; Fry validates mobile,
  keyboard, screen-reader, and non-color-only encoding; sponsor review is required.
* Replacing SVG with a client-only chart would regress crawlability, embeds, and the
  current table alternative. Long repository labels already have a known mobile
  truncation concern in `docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md:79-83`.

Cheap discriminating check: evaluate the current bars and two alternatives with the
same dense top-10 and top-100 samples at 393px and 1280px, including labels and the
equivalent table, before selecting an implementation.

### BR-006 Complete yearly narrative

Target: generate a complete, reviewed journalistic article with traceable evidence,
sections, links, and search metadata, without clipped generation artifacts
(`docs/brds/claracle-post-relaunch-consolidation-brd.md:130`).

Current behavior and owning surfaces:

* `scripts/month_synthesis.py:117-121` truncates individual source fields with a
  Unicode ellipsis.
* `scripts/month_synthesis.py:247-256` hard-limits monthly narrative to 350 words and
  appends an ellipsis when over budget.
* `scripts/month_synthesis.py:277-346` truncates weekly summaries, signals, noise,
  gaps, and conclusions before composing the monthly narrative.
* `scripts/generate_yearly_narrative.py:561-578` contains another ellipsizing helper
  used on monthly source material.
* `scripts/generate_yearly_narrative.py:635-674` clips monthly synthesis paragraphs
  and fallback text while building the yearly progression.
* `scripts/generate_yearly_narrative.py:792-813` applies a final 500-word compressor
  that repeatedly truncates and appends an ellipsis.
* `scripts/generate_yearly_narrative.py:841-889` derives summary metadata and monthly
  navigation from the already-compressed narrative.

Root cause: truncation is cumulative. Weekly facts are clipped into monthly prose,
monthly prose is clipped again when read by the yearly generator, and the final yearly
narrative has a hard cap. Raising only the final 500-word cap would preserve upstream
ellipsis artifacts and would not meet BR-006.

Dependencies and risks:

* Farnsworth owns editorial synthesis, Bender owns deterministic generation, Zapp
  reviews metadata and structure, Fry validates output, Nibbler reviews generated AI
  content and prompt-injection handling, and a human editor must verify claims.
* The fix should preserve bounded prompt inputs separately from published article
  completeness. Source packs or structured evidence can remain bounded without
  clipping the final prose mid-thought.

Cheap discriminating check: generate 2026 from representative long monthly inputs and
assert the body contains no terminal Unicode ellipsis or literal `[...]`, includes
meaningful sections and monthly/source links, and passes claim-to-source review.

### BR-007 Actionable repository names in embeds

Target: every displayed repository name links to the correct source and exposes a
bounded summary on hover, keyboard focus, touch, and assistive technology
(`docs/brds/claracle-post-relaunch-consolidation-brd.md:131`).

Current behavior and owning surfaces:

* `scripts/generate_data_pages.py:200-222` already places URL, context, language, and
  observation metadata in each ranking row.
* `layouts/data/single.html:45-54` links repository names in the full data table.
* `layouts/partials/visuals/observatory-chart.html:43-49` renders repository names as
  plain SVG `<text>`, not anchors or focusable controls.
* `layouts/partials/visuals/observatory-chart.html:18-28` includes URL and context in
  inline JSON but does not expose either through the visual interaction.

Root cause: the embeddable chart was designed as a static SVG with an accessible table
on the source page. Its data already contains most of the needed fields, but the embed
has no interaction/fallback contract for summaries.

Dependencies and risks:

* Define summary source and maximum length before implementing tooltips. The existing
  `context` field is deterministic but may not be the intended repository description.
* SVG links need safe external navigation and visible focus. A tooltip alone is
  insufficient for touch and screen readers; persistent details or an accessible list
  should expose the same text.

Cheap discriminating check: tab through every displayed repository in the standalone
embed, activate each link, and compare hover, focus, touch, and accessibility-tree
summary text at mobile and desktop sizes.

### BR-008 Primary navigation order

Target: Weekly, Monthly, and Yearly appear first in that order across all navigation
modes (`docs/brds/claracle-post-relaunch-consolidation-brd.md:132`).

Current behavior and owning surfaces:

* `hugo.toml:57-106` defines the complete weighted menu.
* Current order is All weeks, Topics, Monthly, Data, Tools, Yearly, Search,
  Methodology, About. Topics therefore interrupts Weekly and Monthly, while Data and
  Tools interrupt Monthly and Yearly.
* No test asserts the menu order or supported-width accessibility.

Root cause: existing menu weights predate the explicit BR-008 hierarchy.

Dependencies and risks: this is a small configuration change owned by Amy, but it
still requires mobile overflow, keyboard order, active-state, and assistive-technology
checks because the menu has nine items.

Cheap discriminating check: assert the first three rendered menu URLs are `/weekly/`,
`/monthly/`, and `/yearly/`, then run the existing responsive matrix at its narrowest
supported width.

### BR-009 Authoritative current cost information

Target: generate the About-page cost display from an authoritative source with period,
generation time, ownership, and an automated freshness failure
(`docs/brds/claracle-post-relaunch-consolidation-brd.md:133`).

Current behavior and owning surfaces:

* `content/about/_index.md:21-25` embeds the cost dashboard but contains no source or
  last-updated metadata.
* `layouts/partials/cost-dashboard.html:1-13` reads
  `data/metrics/cost-summary.json` and silently renders "No cost data available yet"
  when absent.
* `data/metrics/cost-summary.json:1-9` is a manually shaped summary ending at 2026-W21
  with cumulative cost `$0.95`.
* `scripts/track_token_usage.py:14-16` defines
  `data/metrics/token-usage.jsonl` as the active usage ledger.
* `scripts/track_token_usage.py:167-217` creates timestamped weekly stage records with
  token counts, model, source, cost, and estimation status.
* `data/metrics/token-usage.jsonl:1-6` reaches 2026-W23. It includes multiple stage
  records and null costs for `model: none`, so aggregation policy must be explicit.
* No generator bridges the ledger to `cost-summary.json`, and no test or workflow gate
  fails on missing, malformed, or stale dashboard data.

Root cause: the display and active ledger evolved independently. The dashboard still
consumes an unowned static summary rather than a deterministic projection of the
ledger.

Dependencies and risks:

* URL and Bender should define pipeline placement and deterministic aggregation;
  jmservera owns the budget interpretation. Fry should add malformed/missing/age gates.
* Summing repeated W23 analysis attempts without a run identity or accepted-record
  policy can overstate spend. Null cost is valid for no-AI records and must not be
  coerced silently to a billed value.

Cheap discriminating check: generate the summary from a fixture ledger containing
multiple stages, retries, null costs, and an old timestamp; assert deterministic totals,
period and generated-at fields, then verify the freshness check fails beyond the
approved threshold.

### CR-02 Final visual acceptance

Target: Amy and Fry accept the 64-screenshot matrix plus retained manual interaction
captures (`docs/brds/claracle-post-relaunch-consolidation-brd.md:74`).

Current evidence:

* `docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md:15-42`
  identifies the preferred CI evidence, exact revision, 64 screenshots, four metadata
  files, toolchain, and known PR merge-commit caveat.
* `docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md:58-76`
  shows automated route coverage but explicitly says interaction states were not
  captured.
* `docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md:91-132`
  records 68/68 automated visual checks and Amy/Fry acceptance of rendered/automated
  evidence, while leaving manual interaction captures and live assistive-technology
  review open.

Conclusion: CR-02 is not fully closed by the recorded evidence. The named review is
present, but the acceptance requirement includes retained filter combinations,
expanded detail, copy actions, and visible keyboard-focus captures. Those remain
explicitly absent.

Cheap discriminating check: attach the four manual interaction-state capture groups
to the retained matrix and add a dated Amy/Fry disposition that cites them.

### CR-05 Repository-page rollout activation

Target: sponsor-gated activation of `[repo_pages] enabled = true`, preserving rollout
invariants and rollback (`docs/brds/claracle-post-relaunch-consolidation-brd.md:82`).

Current behavior: `config/observatory.toml:1-13` keeps the flag disabled, while the
generated 266-page corpus is already checked in. Workflow tests preserve generated
paths and guarded hydration (`tests/test_pipeline.py:580-694`).

Conflict with BR-003: CR-05 activates continued generation and publication of the
exact detail-page corpus that BR-003 requires production to stop emitting. Both cannot
be accepted in the same target state. CR-05 is a carried-over rollout action from the
previous relaunch design; BR-003 is the newer post-relaunch product direction.

Recommended disposition: Leela and jmservera should supersede or defer CR-05 rather
than flip it during BR-003 implementation. If activation is still needed as a bounded
telemetry experiment, it needs an explicit expiration and must not be represented as
the final BRD state. Do not delete the lifecycle generator until redirect inventory and
rollback needs are resolved.

Cheap discriminating check: add a decision record that selects one production target
state. A configuration test should then prevent both "detail generation enabled" and
"BR-003 consolidated-only production" from being considered accepted simultaneously.

### CR-06 Cost-experiment hydration

Target: produce an admissible Q-01 cost experiment without collapsing five seed topic
hubs to the stale single `ai-ml` hub on `publish`
(`docs/brds/claracle-post-relaunch-consolidation-brd.md:88`).

Current behavior and root cause:

* `config/observatory.toml:15-21` defines five main-branch seed hubs.
* `content/topics/` on `main` contains the five seed `_index.md` files. The inspected
  `origin/publish` tree contains only the legacy `ai-ml` hub.
* `.github/workflows/build-cost-experiment.yml:75-89` asks
  `scripts.publish_hydration paths` for every generated path, then replaces each path
  wholesale whenever any file exists on the reviewed publish commit.
* Because `content/topics/` exists on `publish`, the loop removes main's full directory
  and checks out the one stale publish subtree. The later reference/rollout check at
  `.github/workflows/build-cost-experiment.yml:91-100` sees the already-collapsed
  corpus, and the experiment at lines 135-149 measures the wrong topic-hub state.

This is experiment-only. Production deploy hydration has guarded preservation tests in
`tests/test_pipeline.py:626-694`; the BRD also explicitly excludes broader deploy
hydration changes.

Supported fixes:

* Publish the five reviewed seed `_index.md` files to `publish`, making hydration
  representative of the intended corpus.
* Or exclude `content/topics/` from the experiment's expected `topic_hubs` count so
  Q-01 does not claim to measure a corpus the reviewed publish commit does not contain.

The first option produces the more representative experiment. Either workflow change
requires URL pipeline review and Hermes security review under repository policy.

Cheap discriminating check: hydrate into a temporary tree from reviewed main/publish
SHAs and assert the expected topic-hub count before timing starts, then complete a clean
manual workflow run with retained samples and a dated budget-owner conclusion.

## Cross-Cutting Validation and Ownership

### Existing reusable gates

* Python gates: `ruff check .`, `ruff format --check .`, and `pytest tests/`, as required
  by `.github/copilot-instructions.md`.
* Hugo and rendered output: `hugo --minify`, followed by inspection for user-facing
  changes.
* `tests/test_trend_explorer_tool.py:12-109` covers deterministic JSON, freshness,
  server bootstrap, and malformed/empty client states. This is the closest reusable
  unit pattern for BR-003/004.
* `tests/test_pipeline.py:580-694` covers generated-path ordering, publication,
  guarded hydration, and read-only freshness checks.
* `docs/design/visual-verification.md:122-180` defines overflow, touch-target,
  pre-content, Lighthouse, and CLS thresholds.
* `.github/workflows/security-scanning.yml:1-100` runs blocking Bandit and Zizmor
  checks. `.github/workflows/checkov.yml:1-86` runs blocking Checkov checks for GitHub
  Actions, Dockerfiles, and secrets.

### Missing acceptance coverage

* No exact repository inventory, alias disposition, redirect, canonical, or consolidated
  no-JavaScript acceptance test
* No published JSON schema validation for repository or data-page artifacts
* No navigation-order test for BR-008
* No missing, malformed, or age-based cost freshness gate for BR-009
* No test that rejects ellipsized yearly body output or verifies source traceability
* No browser coverage for BR-007's equivalent hover, focus, touch, and screen-reader
  summaries
* No retained manual interaction captures sufficient to close CR-02

### Ownership routing

The repository routing table at `.squad/routing.md:5-20` and team roster at
`.squad/team.md:9-22` support this implementation split:

* Leela: requirements conflict, architecture, scope, and final code review
* Calculon: BR-001 design direction and BR-005 visualization decision
* Amy: Hugo templates, client interaction, navigation, responsive implementation,
  CR-02 visual review
* Bender: deterministic repository/data/cost artifact generation and lifecycle logic
* Farnsworth: BR-006 editorial synthesis
* Fry: unit, Hugo, browser, accessibility, fallback, and freshness gates
* Zapp: metadata, canonical/redirect/sitemap policy, crawlable summaries, search impact
* URL: workflow, hydration, publication, cost pipeline, and CR-06
* Hermes: workflow/security review and any rollout activation
* Nibbler: generated editorial text, external inputs, and AI-safety review
* jmservera: sponsor design acceptance, rollout authority, and budget conclusion

## Critical Discoveries

* The repository count is not one number: 266 detail records, 267 source pages including
  the section index, and 274 rendered URLs including seven aliases.
* CR-05 directly conflicts with BR-003. Enabling detail generation cannot be the final
  state of a requirement that forbids production detail output.
* BR-006 truncation is cumulative across monthly and yearly generators. Fixing only the
  final yearly cap leaves clipped source prose.
* BR-009 has two disconnected data paths: the About dashboard consumes a stale W21
  summary while the active ledger reaches W23.
* CR-06 is caused by directory-level experiment hydration against an incomplete
  `publish` subtree, not by topic taxonomy generation and not by production deployment.
* Existing data pages already have strong crawlable tables and provenance. BR-004
  should progressively enhance them rather than replace them with client-only output.
* Existing ranking JSON embeds contain URLs and context, so BR-007 is primarily a
  rendering and accessible-interaction gap, not a missing-data problem.

## Remaining Gaps and Clarifying Questions

Research answered the codebase-surface questions, but the repository cannot decide the
following product and authority questions:

* Which audience and single primary job should govern the redesigned homepage?
* Which data pages are the agreed BR-004 priorities?
* Which visualization answers each affected page's analytical question?
* Should `context` or repository `description` be the BR-007 summary source, and what
  maximum length is approved?
* Which cost records count as accepted spend when a week contains retries, multiple
  stages, or `model: none`, and what staleness threshold is approved?
* Does the sponsor formally supersede CR-05, or authorize a temporary activation before
  BR-003 consolidation?
* Which canonical repository URLs have real search or inbound-link value? That requires
  production analytics/Search Console or an external link inventory, not local code.

## Recommended Next Research

* [ ] Export production repository URLs, Search Console status, inbound links, and
  sitemap membership to finalize BR-003 redirect/canonical dispositions.
* [ ] Run a short design discovery with Calculon, Amy, Zapp, and jmservera to settle
  BR-001/002 audience, hierarchy, and signature before implementation.
* [ ] Evaluate two BR-005 visualization alternatives with representative dense data and
  the supported mobile/desktop matrix.
* [ ] Trace workflow run identifiers around `track_token_usage.py` to define retry and
  accepted-cost aggregation semantics before building BR-009's projection.
* [ ] Record the Leela/jmservera decision resolving CR-05 against BR-003.
* [ ] Capture and retain the missing CR-02 interaction states, then record final Amy/Fry
  disposition.