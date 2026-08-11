<!-- markdownlint-disable-file -->

# Implementation Details: Claracle Post-Relaunch Consolidation

## Context References

* Plan: `.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md`
* Research: `.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md`
* Handoff: `.copilot-tracking/research/subagents/2026-08-08/claracle-v1-implementation-handoff-research.md`
* Business baseline: `docs/brds/claracle-post-relaunch-consolidation-brd.md`
* Planning log: `.copilot-tracking/plans/logs/2026-08-08/claracle-post-relaunch-consolidation-log.md`
* Repository instructions: `.github/copilot-instructions.md`, `AGENTS.md`,
  `architecture.md`, `.squad/team.md`, and `.squad/routing.md`

## Execution Rules

* Use a dedicated branch and pull request for each independently reviewable
  concern. Do not mix product code, generated-data updates, and infrastructure.
* Make the smallest grounded edit for each story and run its cheapest
  discriminating check immediately afterward.
* Regenerate derived content with its owning script. Do not hand-edit generated
  output or commit `public/`, `resources/_gen/`, or transient evidence.
* Keep rollout flags disabled unless the exact operational transaction has the
  approvals required by CR-04. CR-05 remains permanently superseded in V1.1.
* Do not infer URL-level retirement eligibility from aggregate analytics,
  sitemap membership, local-build absence, or sampled link-report absence.
* Record missing external evidence as not observed in named sources, never as an
  absolute claim that a URL was never indexed or linked.

## Phase 0 Details: Governance And Independent Operations

### Steps And File Operations

1. Build a finding-to-gate matrix from the frozen visual and accessibility
   evidence. Store evidence alongside the redesigned-release acceptance records,
   preserving the historical files unchanged.
2. Verify the status record cites supersession revision `f37b49d` and CR-05's
   disabled state. Treat discrepancies as documentation corrections, not product
   scope changes.
3. For CR-04, use the existing allowlist and dynamic-hub workflow. Require the
   exact revision, Hermes and sponsor approval, a single reviewed slug,
   transaction evidence, production observation, and tested disabled rollback.
4. For CR-06, inspect `.github/workflows/build-cost-experiment.yml`, the owning
   experiment script, and its tests. Correct only the topic-hub hydration/count
   mismatch, retain run artifacts, and record the budget-owner conclusion.

### Cheapest Checks

* Assert both rollout flags and `[repo_pages] enabled` remain false before and
  after repository changes.
* Run the focused dynamic-topic and cost-experiment contract tests before any
  workflow dispatch.
* Compare historical evidence hashes or revisions to prove they were not
  rewritten while adding redesigned-release mappings.

### Exit Criteria

Every carried finding has one owner, severity, and redesigned-release gate;
CR-05 is not activated; CR-04 remains independent; CR-06 has an admissible run
and dated owner conclusion.

## Phase 1 Details: Shared Contracts And Design Foundation

### Steps And File Operations

1. Follow `.github/skills/frontend-design/SKILL.md` to produce the BR-001 design
   brief and representative homepage, article, repository, and data-page views.
2. Inventory existing generator, layout, content, and JavaScript ownership before
   selecting public artifact paths. Prefer one normalized shared envelope and
   typed domain records rather than one-off page payloads.
3. Define schemas with explicit version, generation time, covered period,
   provenance, freshness, compatibility, and validation rules. Keep complete
   server-rendered summaries authoritative.
4. Define URL parameters and canonicalization rules for repository and ranking
   state. Unknown, invalid, and future values must reset predictably without
   breaking the useful Hugo output.
5. Define the annual evidence pack, generated-context sanitization, and cost
   accepted-attempt algorithm as testable contracts before modifying prompts,
   layouts, or production data.

### Cheapest Checks

* Validate one representative fixture for each schema and reject one malformed
  and one future-version fixture.
* Render one repository and one ranking fixture without JavaScript and verify
  useful summaries, links, provenance, and download access remain present.
* Aggregate a cost fixture containing two stages, a retry, one accepted attempt,
  one `model: none` record, and a 31-day-old latest period.

### Exit Criteria

Calculon and the sponsor approve the design brief; each public artifact has a
documented versioned contract and deterministic fixture; homepage and annual
content contracts are approved; no dependent implementation relies on an
unresolved schema or interaction decision.

## Phase 2 Details: Shell, Homepage, Navigation, Editorial, And Cost

### Steps And File Operations

1. Implement shared tokens and shell behavior in the owning Hugo assets and
   partials. Preserve repository conventions and avoid page-local duplicate
   systems.
2. Implement homepage modules in authoritative Hugo HTML. Optional modules must
   disappear without leaving blank sections or layout shift.
3. Change navigation through the owning menu configuration or shared partial and
   test rendered order, active state, URLs, keyboard order, zoom, and clipping.
4. Trace monthly and yearly clipping to the earliest truncating operation. Keep
   bounded model inputs separate from complete publication and reject raw or
   incomplete artifacts before rendering.
5. Generate cost data from `data/metrics/token-usage.jsonl` through one owning
   pipeline path. Remove any independently maintained public total only after
   deterministic reconciliation and stale-input failure are proven.

### Cheapest Checks

* Render the narrowest supported navigation viewport and assert the first three
  destinations are Weekly, Monthly, and Yearly.
* Feed one deliberately long monthly fixture through the full annual path and
  reject ellipses, clipping markers, incomplete sentences, missing sections, or
  untraceable substantive claims.
* Build the About page from valid and stale cost fixtures and prove stale input
  blocks publication rather than displaying an old value.

### Exit Criteria

The shared shell and homepage work without JavaScript; navigation order is
correct in every supported mode; annual output meets length, completeness,
metadata, and traceability contracts; About displays one reconciled current cost
record; all routed automated and named reviews are retained.

## Phase 3 Details: Repository Inventory And Migration Candidate

### Current Implementation State (2026-08-10)

* Declared scope is Phase 3 only.
* The approved write boundary includes the URL inventory and evidence snapshot,
  BR-003 repository artifact generator, `/repo/` Hugo template, scoped
  enhancement JavaScript and CSS, navigation, generated repository data, tests,
  and these current RPI records.
* Live production evidence currently reconciles 264 `/repo/` sitemap URLs
  against 274 local URL forms. Ten local URLs are absent from the sitemap.
* Exact GSC URL Inspection and Search Analytics exports, sampled backlink
  exports, and first-party referral exports are unavailable. Their state remains
  unknown; no per-URL zero-demand or no-link conclusion is authorized.
* First execution boundary: create a deterministic evidence snapshot and
  versioned repository summary, then render the authoritative no-JavaScript
  explorer before deciding whether the removal gate has sufficient evidence.

### Phase 3 Implementation Result (2026-08-11)

* Production reconciliation is complete: 274 local URL forms, 264 sitemap and
  HTTP-200 URLs, 10 direct HTTP 404 URLs, and zero production-only URLs.
* The deterministic BR-003 artifact is generated from the crawl corpus even
  while `repo_pages.enabled` remains false. It contains 269 current records,
  validates GitHub origins, retains provenance, and defaults to recent momentum.
* `/repo/` renders the complete server-side evidence index with direct GitHub
  links and a public download. JavaScript adds search, topic, language, status,
  period, sort, reset, URL persistence, browser history, and empty-result
  guidance; without JavaScript the full momentum-sorted index remains useful.
* Inventory aliases have isolated evidence objects. The schema requires every
  evidence field, approved status for non-pending dispositions, and collected,
  non-ambiguous evidence with named sources and windows before redirect or
  retirement can validate.
* Snapshot capture fails closed on unavailable HTTP evidence. Pipeline freshness
  checks validate the repository artifact, retained production snapshot, and
  joined URL inventory.
* External evidence remains unavailable. All 274 dispositions and approvals are
  pending; no details were deleted and no redirect was generated.

### Phase 3 Validation Result

* `pytest tests/`: 1,599 passed, two expected warnings.
* `ruff check .` and `ruff format --check .`: passed.
* Hugo: 2,707 pages and eight aliases built.
* Pagefind 1.5.2: completed; rendered internal-link check passed.
* Repository summary, production snapshot, and URL inventory checks: passed.
* Checkov 3.2.533: 894 passed, zero failed, six skipped.
* Installed Zizmor 1.25.2: no medium/high findings. The repository-pinned
  1.27.0 binary was unavailable locally, so the pinned-version CI gate remains
  authoritative for the workflow diff.

### Steps And File Operations

1. Produce one versioned URL inventory joining source records, generated pages,
   local rendered URLs, aliases, sitemap and internal links, deployed status,
   canonical targets, and production-only discoveries.
2. Import URL Inspection, exact-page Search Analytics for the recorded window,
   sampled link evidence, and available first-party referral evidence without
   converting missing observations into zero.
3. Add content differentiation and destination-equivalence review. Require named
   approval for each keep, merge, redirect, or retire row.
4. Determine the hosting boundary only after disposition approval. If no redirect
   row remains, verify direct HTTP 404 and retain GitHub Pages. If a genuine
   equivalent remains, implement a one-hop 301/308 at a host that deploys content
   and redirect rules atomically.
5. Generate the repository JSON artifact and authoritative Hugo explorer summary
   from the approved records. Add scoped search, topic, language, status, period,
   recent-momentum sort, URL state, sanitized summaries, and direct GitHub links.
6. Remove low-information details only in the reviewed migration transaction and
   retain a rollback artifact. Never enable the superseded corpus as a bridge.

### Cheapest Checks

* Reconcile all four count classes before deleting any page. A count mismatch or
  unclassified production URL fails the migration candidate.
* Validate one representative keep, retire, alias, and conditional redirect row
  end to end before generating the complete map.
* Test no-JavaScript output, invalid URL state, empty result, malformed payload,
  keyboard operation, and assistive-technology labels on one fixture.

### Exit Criteria

Every observed URL has an approved disposition and adequate named evidence; no
ambiguous URL retires; the selected host matches the final map; the candidate
emits no low-information detail pages; redirects, if any, are one hop; direct
retirements return true HTTP 404; sitemap, canonicals, internal links, custom 404,
atomic deployment, and rollback all pass.

## Phase 4 Details: Ranking Data, Visualization, And Embeds

### Steps And File Operations

1. Convert one ranking fixture to the shared envelope and prove deterministic
   generation, useful no-JavaScript table, malformed behavior, and URL reset.
   Extend the proven pattern to all three approved ranking pages.
2. State one analytical question and intended inference per page. Build the
   common dense, sparse, tied, zero, long-label, top-10, top-100, and mobile
   fixture set before selecting visual forms.
3. Prototype at least two suitable representations per question, retain raw
   five-member proxy evidence, and implement only choices meeting four-of-five.
4. Preserve an equivalent accessible table and non-color encoding for every
   selected visualization.
5. Implement one embed summary disclosure model for hover, focus, touch, Escape,
   persistence, accessibility-tree access, collision, zoom, and narrow widths.

### Cheapest Checks

* Reject any visualization that fails either a dense or long-label mobile fixture
  before running the full proxy test.
* Test one long repository label at narrow width and compare hover, focus, touch,
  and accessibility-tree text before applying the embed pattern globally.
* Verify essential facts and source/download links remain available when JSON or
  JavaScript is unavailable.

### Exit Criteria

All three pages pass SSR, provenance, download, state, error, accessibility,
timing, and interaction contracts; each selected representation has retained
four-of-five evidence; embed names link safely to GitHub and expose equivalent
sanitized summaries without obscuring controls.

## Phase 5 Details: Release And Outcome Evidence

### Steps And File Operations

1. Freeze one candidate revision after Phases 2 through 4 pass their binary gates.
2. Run all affected repository checks and retain reports against that revision.
3. Complete named manual evidence against the same revision. Do not combine
   evidence from different candidates into a release claim.
4. Apply the BRD severity policy and record owner, due date, or an expiring sponsor
   exception where permitted. Severity-1 and severity-2 findings block release.
5. After sponsor GO, deploy with rollback readiness and capture release-day,
   seven-day, 28-day, three-month, and six-month observations at their due dates.

### Exit Criteria

One immutable revision has complete automated and named evidence, no unresolved
blocking finding, sponsor GO, tested rollback, and scheduled outcome ownership.

## Plan Discrepancies

* The V1 implementation handoff treated redirect-capable hosting as an
  unconditional prerequisite. Approved BRD version 1.1 makes it conditional on
  at least one genuine-equivalent redirect row in the final URL map.
* The primary research still labels V1.1 approval as proposed in one phased-model
  paragraph. The BRD and session state are controlling and record V1.1 approved.
* External metadata is described as delivered in the BRD baseline while the
  handoff notes narrower debugger and named-review evidence remains partial. This
  requires evidence reconciliation, not a new business decision.
