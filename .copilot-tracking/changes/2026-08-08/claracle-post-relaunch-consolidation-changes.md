<!-- markdownlint-disable-file -->

# Changes: Claracle Post-Relaunch Consolidation

## Related Plan

`.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md`

## Implementation Date

2026-08-08

## Summary

Implemented the locally actionable governance, contract, repository-inventory,
navigation, cost-projection, and yearly-editorial slices selected after planning.
The changes establish deterministic evidence and fail-closed behavior without
claiming named acceptance, cost activation, URL migration, rollout approval, or
release GO.

## Added

* `.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md`
  with CR-01 through CR-06 and BR-001 through BR-009 coverage, dependency gates,
  parallel lanes, validation strategy, and success criteria
* `.copilot-tracking/details/2026-08-08/claracle-post-relaunch-consolidation-details.md`
  with phase-specific operations, cheap checks, exit criteria, and V1.1 policy
  discrepancies
* `.copilot-tracking/plans/logs/2026-08-08/claracle-post-relaunch-consolidation-log.md`
  with selected alternatives, deferrals, human gates, and suggested delivery
  slices
* `.copilot-tracking/reviews/2026-08-08/claracle-post-relaunch-consolidation-plan-review.md`
  with request fulfillment and planning validation results
* `docs/review/claracle-post-relaunch/redesigned-release-finding-map.md`
  with successor gates for unresolved historical findings
* `docs/design/claracle-experience-design-brief.md` as a proposed BR-001 design
  candidate pending accountable approval
* Shared Observatory, repository inventory, cost summary, and yearly evidence
  JSON schemas
* Repository URL inventory and deterministic generator with contract tests
* Deterministic cost projection and tests
* Deterministic yearly evidence-pack generator and tests

## Modified

* `.github/workflows/build-cost-experiment.yml` preserves the five reviewed topic
  hubs during experiment hydration
* `.github/workflows/crawl-and-publish.yml` passes immutable workflow run and
  attempt identity to both token-ledger producers
* `scripts/track_token_usage.py` records workflow identity when supplied
* `scripts/month_synthesis.py` persists complete monthly source packs and
  invalidates clipped version 2 caches
* `scripts/generate_yearly_narrative.py` composes publication prose at sentence
  and paragraph boundaries without ellipsis clipping
* `scripts/generate_rollups.py` emits yearly claim/source evidence packs
* `hugo.toml` orders Weekly, Monthly, and Yearly first
* Focused tests cover hydration, navigation, producer identity, repository
  inventory, cost reconciliation, yearly evidence, and full-year publication

## Removed

None.

## Deviations

* The pre-V1.1 handoff's unconditional redirect-host prerequisite was replaced
  with the approved conditional rule: change hosting only when the final URL map
  contains a genuine-equivalent redirect.
* Cost projection activation remains blocked. Existing ledger rows lack immutable
  workflow identity, and no sponsor-approved legacy exclusion policy or fresh
  identified production record exists.
* Repository migration remains blocked. URL Inspection, exact-page Search
  Analytics, sampled links, first-party referrals, production reconciliation,
  and approved per-URL dispositions are not available locally.
* Design, accessibility, editorial, SEO, security, and sponsor approvals remain
  open. Automated evidence does not substitute for those named decisions.
* Existing BRD, status, session-state, research, and instruction changes were
  treated as user-owned context and were not rewritten by this implementation
  review.

## Release Summary

The selected local implementation slices pass affected automated checks. Cost
publication, repository migration, named acceptance, production rollout, and
outcome measurement remain blocked or future work under the controlling plan.

## Phase 3 Repository Migration Implementation (2026-08-10)

### Execution State

* Related phase: Phase 3
* Declared scope: Repository Inventory And Migration Candidate
* Branch: `feat/repository-migration-phase3`
* Status: In progress
* First execution boundary: reconcile local, rendered, sitemap, HTTP, canonical,
  alias, internal-link, and content evidence; then generate the BR-003 artifact
  and authoritative explorer.
* Validation intent: focused generator/schema/rendering tests, Ruff, full
  affected pytest, Hugo, internal-link checks, and direct production HTTP
  verification.

### External Evidence Boundary

* Related phase: Phase 3
* Triggering evidence: the live sitemap contains 264 `/repo/` URLs while the
  checked-in inventory contains 274 URL forms; direct checks show both live
  repository pages and already-absent paths returning true HTTP 404.
* Current-state update: production sitemap and HTTP evidence can be captured,
  while exact URL Inspection, Search Analytics, sampled backlink, and
  first-party referral exports are unavailable in this environment.
* Decision: preserve unavailable evidence as uncollected or ambiguous. Do not
  infer zero demand, no indexing, or no inbound links.
* Planning and critique state: approved intent remains current; this narrows the
  evidence implementation without changing the V1.1 retirement policy.

### Production URL Reconciliation

* Related phase: Phase 3
* Files: `scripts/capture_repository_production_snapshot.py`,
  `data/derived/observatory/repository-production-snapshot.json`,
  `scripts/generate_repository_url_inventory.py`,
  `data/derived/observatory/repository-url-inventory.json`,
  `data/schemas/repository-url-inventory.schema.json`
* What changed and why: captured the live sitemap and fail-closed direct HTTP
  status for every local URL, joined the evidence into the versioned inventory,
  isolated alias evidence, and encoded approval and evidence gates so ambiguous
  rows cannot validate as redirect or retire decisions.
* Completion evidence: 274 local URL forms reconcile to 264 sitemap/HTTP-200
  URLs, 10 HTTP-404 URLs, and zero production-only URLs. All 274 dispositions
  and approvals remain pending.
* Validation: focused inventory, snapshot, schema, and alias-isolation tests
  passed; all freshness checks are byte-current.

### BR-003 Repository Explorer

* Related phase: Phase 3
* Files: `scripts/generate_repository_summary.py`,
  `data/observatory/repository_summary.json`,
  `static/data/repositories.json`, `layouts/repo/list.html`,
  `assets/js/repository-explorer.js`,
  `assets/css/extended/repository-explorer.css`, `content/repo/_index.md`,
  `hugo.toml`
* What changed and why: generated a versioned crawl-derived repository artifact
  without enabling CR-05, added Repositories to navigation, and replaced the
  legacy alphabetical list with a complete evidence index. The index defaults
  to recent momentum and links directly to GitHub. Scoped enhancement provides
  filters, sorting, reset, URL persistence, browser history, and empty states;
  no-JavaScript output remains complete and useful.
* Completion evidence: 269 repository records render in authoritative HTML and
  the public JSON download; unsafe non-GitHub origins fail generation.
* Validation: repository explorer, no-JavaScript rendering, URL-state, default
  ordering, malformed/empty, schema, and workflow regression tests passed.

### Pipeline Freshness

* Related phase: Phase 3
* Files: `.github/workflows/crawl-and-publish.yml`,
  `.github/workflows/generate-data-pages.yml`
* What changed and why: generate the repository summary from current crawl
  evidence and require byte-current summary, production snapshot, and joined
  URL inventory during generated-content freshness checks.
* Validation: affected pipeline tests passed; Checkov 3.2.533 reported 894
  passed, zero failed, six skipped; installed Zizmor 1.25.2 reported no
  medium/high findings. The pinned Zizmor 1.27.0 CI gate remains required.

### Phase 3 Validation Record

| Check | Scope | Status | Evidence or reason |
|---|---|---|---|
| pytest | Full repository | Passed | 1,599 passed; two expected warnings |
| Ruff | Full repository | Passed | Check and format check clean |
| Hugo | Production render | Passed | 2,707 pages, eight aliases |
| Pagefind and links | Rendered site | Passed | Index completed; internal links clean |
| Repository freshness | Summary, snapshot, inventory | Passed | All three checks byte-current |
| Checkov 3.2.533 | Workflow/security config | Passed | 894 passed, zero failed, six skipped |
| Zizmor 1.25.2 | Workflows | Passed with version caveat | No medium/high findings; pinned 1.27.0 unavailable locally |

### Phase 3 Pre-Review Reconciliation

* Plan markers and phase details: current.
* Completed-work evidence and handoff prose: current.
* Validation, blockers, remaining work, and follow-up items: current.
* Review readiness: implementation slice is reviewable; Phase 3 as a whole
  remains blocked at the external evidence and named disposition gate.

### Phase 3 Blocker

URL Inspection is now collected for all rows. Content and
destination-equivalence review and named approval remain incomplete, so the 264
live repository URLs cannot yet receive defensible
keep/merge/redirect/retire dispositions and the low-information detail corpus
cannot be removed. The clearing action is to complete those reviews and approve
the resulting per-URL disposition map.

### External Evidence Import (2026-08-11)

* Related phase: Phase 3
* Files: `scripts/import_repository_external_evidence.py`,
  `data/derived/observatory/repository-external-evidence.json`,
  `scripts/generate_repository_url_inventory.py`,
  `data/derived/observatory/repository-url-inventory.json`,
  `data/schemas/repository-url-inventory.schema.json`
* What changed and why: normalized the supplied localized Search Console and
  GA4 exports into a versioned artifact, joined exact observations and metrics
  to all 274 URL rows, and retained source-specific windows. Omitted rows are
  represented as not observed in the named export, not as historical zero.
* Evidence result: Search Analytics observes 51 impressions and zero clicks
  across 10 exact repository URLs for 2026-07-27..2026-08-09. The sampled
  backlink export contains no repository targets. The
  2026-07-27..2026-08-11 GA4 export contains no referral data rows.
* Policy result: the Search Analytics observations disprove a blanket
  no-indexing assumption. URL Inspection remains uncollected for all 274 rows,
  so all dispositions remain pending and no retirement is authorized.
* Validation: 37 focused import, inventory, and public schema-contract tests
  passed; the full suite passed with 1,604 tests and two expected warnings;
  full Ruff check and format check passed. Generated inventory counts confirm
  10 observed and 264 not-observed Search Analytics rows, zero observed sampled
  links or referrals, and 274 uncollected URL Inspection rows.
* Review disposition: Squad initially blocked on zero-shaped omitted metrics,
  permissive malformed-export handling, and missing `Filtres.csv` provenance.
  Omitted metrics now remain `null`; required headers, repository paths, GA4
  metadata, and Search Console filters fail closed; source windows derive from
  the supplied metadata. Focused tests cover malformed headers, legitimate
  metadata-only GA4 output, and an incorrectly scoped Search Console export.

### URL Inspection Capture (2026-08-11)

* Related phase: Phase 3
* Files: `scripts/capture_repository_url_inspection.py`,
  `data/derived/observatory/repository-url-inspection.json`,
  `scripts/generate_repository_url_inventory.py`,
  `data/derived/observatory/repository-url-inventory.json`,
  `data/schemas/repository-url-inventory.schema.json`,
  `.github/workflows/crawl-and-publish.yml`,
  `.github/workflows/generate-data-pages.yml`
* What changed and why: discovered the owner-level Search Console property
  `sc-domain:claracle.com`, captured URL Inspection results for every inventory
  row with bounded retries and concurrency, and joined verdict, coverage,
  crawl, and canonical evidence into inventory schema 1.2.0.
* Evidence result: 15 URLs are submitted and indexed, 99 are discovered but not
  indexed, and 160 are unknown to Google. All 10 URLs with Search Analytics
  impressions are among the indexed URLs.
* Safety result: the token is read only from the ignored temporary file and is
  never persisted in repository artifacts. The snapshot contains no credential.
* Remaining gate: URL Inspection is complete. Content differentiation,
  destination equivalence, and named disposition approval remain incomplete,
  so all 274 rows remain pending and no redirect or retirement is authorized.
* Validation: full Ruff check and format check passed; URL Inspection and
  inventory freshness checks passed; 1,608 tests passed with two expected
  warnings; Checkov 3.2.533 reported 894 passed, zero failed, and six skipped;
  installed Zizmor 1.25.2 reported no medium/high findings, with pinned 1.27.0
  remaining authoritative in CI.
* Review disposition: Squad approved the slice and identified only a test gap
  around authenticated transient retries. A focused regression test now covers
  bearer-header construction, timeout retry, and successful recovery.

### Repository Disposition Candidate (2026-08-11)

* Related phase: Phase 3
* Files: `scripts/generate_repository_disposition_candidate.py`,
  `data/derived/observatory/repository-disposition-candidate.json`,
  `scripts/generate_repository_url_inventory.py`,
  `data/derived/observatory/repository-url-inventory.json`,
  `data/schemas/repository-url-inventory.schema.json`
* What changed and why: captured 8,024 current rendered internal links, reviewed
  repository-specific trend differentiation, joined all external evidence, and
  produced a complete 274-row candidate without forging sponsor approval.
* Candidate result: 11 keeps, one redirect, and 262 retirements. Nine canonical
  detail URLs have observed demand; the consolidated explorer is retained; and
  the currently absent Odysseus canonical is retained as the equivalent target
  for its indexed, impression-bearing legacy alias.
* Hosting result: the one exceptional redirect makes redirect-capable hosting
  necessary if the exact candidate is approved. GitHub Pages cannot emit the
  required one-hop hosting-layer 301/308.
* Approval boundary: every candidate row remains pending under the named
  `jmservera` approval authority. No source page, sitemap entry, internal link,
  hosting configuration, or production URL was changed.
* Validation: full Ruff check and format check passed; inspection, candidate,
  and inventory freshness passed; 1,612 tests passed with two expected warnings;
  Checkov 3.2.533 reported 894 passed, zero failed, and six skipped; installed
  Zizmor 1.25.2 reported no medium/high findings, with pinned 1.27.0 remaining
  authoritative in CI.
* Review correction: Squad blocked indexation being treated as demand and weak
  candidate freshness. The final policy uses impressions, sampled links, or
  referrals as value signals; indexation remains context only. A strict schema,
  per-row invariants, exact rationale and redirect checks, and SHA-256 bindings
  to production, external-export, and URL Inspection evidence now fail closed.

### Approved Repository Migration Transaction (2026-08-11)

* Related phase: Phase 3
* Approval: `jmservera` approved the exact 11-keep, one-redirect, 262-retire
  candidate and authorized Phase 4 only after Phase 3 completion and Phase 5
  only after Phase 4 completion. The approved artifact records that this
  sequencing authorization waives no production, security, or review gate.
* Evidence: `data/migrations/repository-approved-dispositions.json` binds the
  candidate and inventory SHA-256 values and approved commit `05433d5`.
  `data/migrations/repository-migration-rollback.json` binds every removed source
  checksum and the pre-migration revision.
* Source transaction: removed 256 retired canonical profile files, retained 10
  canonical profiles plus `/repo/`, removed the Odysseus Hugo alias, emitted the
  sole approved 301 in `static/_redirects`, and moved related-profile links to
  safe direct GitHub destinations.
* Regeneration safety: removed `content/repo/` from deploy, crawl, freshness, and
  publish-hydration path sets. `repo_pages.enabled` remains false, so neither the
  publish branch nor routine generation can restore retired profiles.
* Hosting boundary: replaced both GitHub Pages deployment paths with
  commit-pinned Cloudflare Wrangler Direct Upload to project `claracle`, pinned
  Wrangler 4.120.1, serialized the shared production deployment boundary, added
  a custom 404, and added approved-map-driven live 200/301/404 probes.
* Security reconciliation: documented BR-003 publication-scope retirement as a
  sponsor-approved, checksum-verified deletion authority that preserves crawl
  history and does not change SEC-04 upstream-deletion lifecycle behavior.
* Review correction: Squad found stale Anthropic profile QA fixtures and the
  implicit SEC-04 conflict. Fixtures now use retained Odysseus or the approved
  map; the security exception is explicit; the weekly webhook uses
  `https://claracle.com`; and cross-workflow deploys serialize without
  cancellation.
* Local evidence: clean Hugo output contains 10 retained profiles plus the
  explorer, no retired sitemap entries or internal links, an exact redirect
  rule, and `404.html`. Wrangler Pages emulation returned retained 200,
  one-hop 301, and retired 404. Checkov 3.2.533 reported 902 passed, zero failed,
  six skipped; Zizmor 1.25.2 reported no medium/high findings on changed
  workflows. After merging current `main`, full Ruff and 1,631 pytest checks
  passed with two expected sanitization warnings.
* External blocker: production completion still requires the Cloudflare account
  ID and scoped API token, project creation, custom-domain attachment,
  Namecheap-to-Cloudflare nameserver cutover, TLS, live probes, and preserved
  rollback evidence. Phase 4 remains gated.
* Review handoff: branch `feat/repository-migration-phase3` is pushed and
  `jmservera/SquadScope#710` is open against `main`; hosted CI and review are in
  progress.
* PR security remediation: replaced standard-library XML parsing with
  `defusedxml`, restricted production snapshot requests to
  `https://claracle.com`, restricted URL Inspection requests to Google's exact
  HTTPS API endpoint, and added rejection tests for unapproved URL schemes and
  authorities. Targeted Bandit and eight capture tests pass.
* Hosted review result: all 16 PR checks pass on head `4f91f87`, Copilot reviewed
  the latest head, and all five security-review threads are resolved. The PR is
  clean and remains unmerged pending Cloudflare production-boundary provisioning
  and required human review.

### Sponsor GitHub Pages Override (2026-08-11)

* Classification: material user-owned hosting and URL-disposition decision.
* Decision: retain GitHub Pages and accept direct 404 behavior for retired
  repository profiles; do not provision Cloudflare.
* Migration effect: supersede the exceptional redirect, retire both the legacy
  Odysseus alias and its redirect-only destination, and revise the authoritative
  map to 10 keeps, zero redirects, and 264 retirements.
* Active work: restore both production workflows to GitHub Pages, remove
  Cloudflare configuration and redirect artifacts, delete the now-unneeded
  destination profile, update validators/tests/docs, and rerun the PR review
  cycle before completing Phase 3.

### Explorer-Only Repository Decision (2026-08-11)

* Classification: final material sponsor decision for the repository URL surface.
* Decision: retain only the JSON-backed `/repo/` explorer and remove every
  individual `/repo/<slug>/` source and route, without redirects or legacy-link
  preservation.
* Migration effect: supersede all prior per-profile keep decisions and revise
  the authoritative map to one keep, zero redirects, and 273 retirements.
* Active work: remove the remaining nine profile sources, move profile-specific
  QA coverage to the explorer, regenerate migration and rollback artifacts, and
  complete the GitHub Pages PR review cycle before Phase 3 can finish.
* Implemented outcome: removed all individual repository sources, retained
  `content/repo/_index.md`, changed the explorer to fetch the versioned
  `/data/repositories.json` artifact, and regenerated the approved map and
  rollback manifest at one keep, zero redirects, and 273 retirements.
* Hosting outcome: restored both production workflows to commit-pinned GitHub
  Pages actions and removed Cloudflare workflow, documentation, secret, and
  redirect dependencies while preserving the publish-hydration exclusion.
* Validation: 1,631 tests pass in the complete phase environment; Ruff, clean
  Hugo rendering, Checkov (902 passed, zero failed), Zizmor (no medium/high
  findings), and changed-script Bandit pass. Browser evidence records a 200 for
  `/data/repositories.json`, 269 rendered records, and no console errors.
* Review: Squad routed the diff through Leela, Amy, URL, Hermes, and Fry and
  approved it with no release-blocking findings. Production smoke sampling and
  fail-closed dataset URL validation were confirmed as intentional.
* Hosted evidence: every check passed on source head `70e42cd` and all review
  threads are resolved. Copilot completed its latest-head review attempt but
  reported that the cumulative PR exceeds its 300-file review limit.
* Remaining blocker: qualified human review and merge authorization are required
  before GitHub Pages can deploy the final artifact and the workflow can capture
  production `/repo/` 200 and retired-route 404 evidence.
* Sponsor clearance: the sponsor completed the required review, authorized
  merging PR 710, and selected automatic continuation through all eligible
  later phases. The production probe remains the final Phase 3 gate.

## CR-06 Harness Repair And Experiment Execution (2026-08-09)

Three cascading build-cost harness defects were repaired through separate
reviewed pull requests, each with 4/4 Squad approval, then the official
report-only experiment was dispatched and completed cleanly.

* PR #686 (merged `67045a3`): `discover_workload`/`run_experiment` derive the
  `repository_pages` count from the reviewed publish tree via
  `--expected-repository-pages` and `build_variants()`, removing the hardcoded
  266-page guard that conflicted with the 263-page publish corpus.
* PR #687 (merged `38c51ca`): `_tool_version` and `_run_timed` invoke `pagefind`
  directly instead of `npx --no-install pagefind`, matching the global install.
* PR #689 (merged `8f680f4`): `materialize_variant` removes
  `content/embeds/*/index.md` and `content/charts/*/index.md` from every variant
  so dependent leaves cannot orphan removed data pages; `_index.md` and sibling
  assets are retained.
* Experiment run `31305223877` on main `8f680f4`, publish `4120078d`, 3
  repetitions, report-only mode completed all jobs successfully. Evidence
  (`summary.md`, `summary.json`, `manifest.json`, per-sample JSON, per-variant
  logs, `SHA256SUMS`) is retained as the run artifact.
* Official medians and marginal cost over the reviewed 266-page repository
  corpus:
  * Hugo `repository_pages`: median 3116 ms, p95 3156 ms, marginal 8.776 ms/page
  * Pagefind `repository_pages`: median 803 ms, p95 979 ms, marginal 2.414 ms/page
  * Hugo `topic_hubs` 0.400 ms/page and `data_pages` 0.667 ms/page marginal;
    Pagefind `data_pages` 5.000 ms/page marginal

Only the dated Q-01/NFR-009 budget-owner conclusion by jmservera remained open
for CR-06 as of the harness repair above; see "Q-01/NFR-009 Budget-Owner
Conclusion" below, where that conclusion is recorded and CR-06 is closed.

## Phase 1 Continuation: BR-007 Contract, Public Schema Fixtures, BR-002 Draft (2026-08-09)

Closed both Phase 1 items that did not require a pending human approval, and
drafted the remaining BR-002 candidate for sponsor review.

### Added

* `data/schemas/embed-summary.schema.json`: BR-007's sanitized-summary and
  safe-GitHub-link data contract (schema-versioned, 160-character display cap,
  always-complete accessible text)
* `docs/design/claracle-embed-summary-contract.md`: the BR-007 sanitization
  pipeline, safe-link rule, and the interaction requirements deferred to Phase 4
* `docs/design/claracle-homepage-module-hierarchy.md`: the BR-002 candidate
  module order, per-module selection/freshness/ownership/fallback rules, the
  empty-module rule, and two open questions, pending Leela/sponsor approval
* `tests/test_public_json_schema_contracts.py`: 23 tests validating a
  representative fixture, one malformed variant, and (where applicable) one
  future-schema-version variant for all seven public JSON contracts
  (repository-url-inventory, cost-summary, yearly-evidence-pack,
  observatory-envelope, ranking-record, repository-record, embed-summary)
  against their `data/schemas/*.json` files using `jsonschema`

### Modified

* `requirements.txt`: added `jsonschema>=4.0,<5.0` as a test dependency

### Deviations

* Repaired a pre-existing broken `idna` install in the local `.venv` (blocked
  `jsonschema`'s format-checker import with `AttributeError: module 'idna' has
  no attribute 'IDNAError'`) via `pip install --force-reinstall --no-deps idna`.
  This is a local environment fix, not a repository change, and is unrelated to
  this plan's scope.
* BR-001 and BR-002 remain unchecked. Both require named sponsor (and
  Calculon/Leela) approval of a design candidate per the BRD acceptance
  criteria; that approval cannot be inferred and was requested from jmservera
  rather than assumed. BR-001's brief was already drafted; BR-002's hierarchy is
  now drafted alongside it.

Full test suite: 1538 passed (`pytest tests/`). Ruff check and format check pass
for the new test file.

## BR-001 And BR-002 Sponsor Approval (2026-08-09)

Sponsor jmservera approved both remaining Phase 1 design candidates in this
session, closing Phase 1 (Shared Contracts And Design Foundation).

* BR-001: approved as-is. `docs/design/claracle-experience-design-brief.md`
  Approval Status updated; the Field Notebook direction, tokens, and layout
  concept stand as written.
* BR-002: approved with two revisions, applied to
  `docs/design/claracle-homepage-module-hierarchy.md`: the repository and data
  evidence modules scale their item count with viewport width instead of a
  fixed count, and the monthly and yearly modules show a short list (three to
  five months, two to three years) instead of a single entry.
* Neither approval authorizes the Phase 2 homepage/shell build by itself; both
  documents still gate on their own representative-view and accessibility
  verification during implementation.

## Phase 2: BR-006 Monthly/Yearly Narrative Clipping Fix (2026-08-09)

Root-caused and fixed the actual BR-006 defect. The Phase 0 changes log had
claimed clipping was "corrected across monthly and yearly generation," but that
fix only reached `scripts/generate_yearly_narrative.py`'s local `trim_words()`.
`scripts/month_synthesis.py` had its own, separate, pre-fix `trim_words()` that
still truncated at a raw word count and appended an ellipsis, so every
committed `data/analyzed/*-month-synthesis.md` (and the yearly page derived from
it) was still clipped mid-sentence, and the published `content/yearly/2026.md`
was only 540 words with several unfinished sentences.

### Modified

* `scripts/month_synthesis.py`: `trim_words()` now selects complete sentences
  within the word budget instead of appending "…" at a raw cutoff (mirrors the
  already-correct version in `generate_yearly_narrative.py`); the `summaries`
  list in `synthesize_month()` now strips a stray trailing period so embedding
  a short complete sentence as a mid-sentence clause (`"opened with X and ended
  with Y"`) no longer produces a false sentence break
* `tests/test_generate_rollups.py`: added `MonthSynthesisTrimWordsTests`
  covering sentence-boundary trimming, the no-fitting-sentence fallback (full
  text, still no ellipsis), and an end-to-end `synthesize_month()` check that no
  part of the narrative/summary/trend-arc/prediction-review contains "…"

### Regenerated (derived content, not hand-edited)

* `data/analyzed/2026-0{5,6,7,8}-month-synthesis.md`: deleted the stale
  pre-fix files and regenerated via `python -m scripts.generate_rollups`
* `data/analyzed/2026-0{5,6,7,8}-month-synthesis-pack.json`: new BR-006
  evidence-pack artifacts (complete, untruncated weekly text), validated against
  `data/schemas/yearly-evidence-pack.schema.json`'s source shape
* `content/monthly/2026/{05,06,07,08}.md`: deleted and fully regenerated (the
  append-only merge otherwise preserves already-published per-week entries, so
  a partial regeneration would have left months 05-06's older, still-clipped
  Month Overview/Trends/Key Takeaways bullets in place)
* `content/yearly/2026.md`: regenerated; narrative body is 1,775 words (within
  the 1,200-1,800 acceptance range; the 1,839 raw `wc -w` figure includes
  frontmatter), zero "…" anywhere in the file
* `data/derived/yearly/2026-evidence-pack.json`: new BR-006 evidence pack (12
  sources, 49 claims), validated against
  `data/schemas/yearly-evidence-pack.schema.json` with `jsonschema`

### Validation

* `pytest tests/` -> 1542 passed (up from 1539; 3 new regression tests)
* `ruff check` / `ruff format --check` clean on `scripts/month_synthesis.py`
  and `tests/test_generate_rollups.py`
* `hugo --minify` built 2,701 pages successfully; `check_internal_links.py`
  found only the two pre-existing, unrelated missing `pagefind/*` assets (no
  Pagefind index built in this ad-hoc check)
* `tests/test_rendered_seo_metadata.py` passes against the regenerated content
* Real `data/derived/yearly/2026-evidence-pack.json` validated against its
  schema with `jsonschema` (not just the test fixture)

### Deviations

* This closes only the BR-006 checklist item within Phase 2. BR-001 (shell),
  BR-002 (homepage), BR-009 (cost display), and the evidence-retention item
  remain open as independently deliverable Phase 2 stories.
* Named editorial review of the regenerated 2026 yearly article (Farnsworth
  accountable, jmservera final editor per the BRD) has not occurred; only
  automated completeness, range, and metadata checks are represented here.
* Monthly pages for 2026-07 and 2026-08 already had zero ellipsis before this
  change (they were generated after an earlier partial fix); only 2026-05 and
  2026-06 needed full regeneration versus a narrower Month Synthesis-only
  refresh.

### PR #692 Review Follow-Ups (2026-08-09)

Three further fixes landed on the same branch/PR in response to Copilot review
comments, all re-validated with the full test suite, `hugo --minify`, and a
fresh evidence-pack schema check:

* `trim_words()` now falls back to the full original text when even the first
  sentence alone exceeds the word budget, instead of silently dropping every
  sentence after it.
* `generate_yearly_narrative.load_month_synthesis_paragraphs()` dedupes prose
  paragraphs; the standalone monthly synthesis file's "Prediction Review"
  section was restating its "Month Synthesis" narrative's own closing
  paragraph, which showed up as a repeated paragraph in each yearly chapter.
* `generate_rollups.generate_monthly_title()`'s single-theme fallback no longer
  risks subject/verb disagreement for plural theme labels (e.g. "Developer
  Tools Leads" -> a noun-phrase construction with no agreement to get wrong).
* `.github/workflows/site-preview.yml`: an unrelated, pre-existing local
  modification (reworking the preview-download instructions) was present in the
  working tree and was inadvertently included in the commit above rather than
  excluded as intended. Since it ended up in this PR anyway, its own bug was
  fixed rather than reverted: the download command was a single-quoted JS
  string so `${context.runId}` never interpolated, `${owner}`/`${repo}` were
  undefined, and the trailing `unzip` step assumed a zip that `gh run download`
  does not produce by default. Converted to a template literal using
  `context.repo.owner`/`context.repo.repo` and dropped the unzip step.


## Q-01/NFR-009 Budget-Owner Conclusion (jmservera, 2026-08-09)

Report-only; no blocking build-cost budget is set. Per run `31305223877` (main
`8f680f4`, publish `4120078d`, 3 repetitions), the only material generation cost
is the `repository_pages` corpus (Hugo median 3116 ms, marginal ~8.8 ms/page;
Pagefind median 803 ms, marginal ~2.4 ms/page). `topic_hubs` and `data_pages`
are negligible (sub-millisecond to low-single-digit ms/page). That corpus is the
low-information repository detail set targeted for removal or reduction under the
consolidation BRD Phase 3 migration; CR-05 keeps `repo_pages` disabled so it is
not regenerated. Build cost is therefore dismissed as a launch gate. Re-evaluate
only if Phase 3 retains or regenerates a repository-page corpus of meaningful
size. The rollout flags were confirmed disabled during measurement, so this
conclusion also clears the sequencing precondition for CR-04.

## CR-04 Dynamic-Topic Canary Activation (2026-08-09)

Activated the first bounded dynamic-topic canary through PR #684 (squash merge
`bd1cf04`).

* `config/observatory.toml`: `topic_hubs.dynamic_creation.enabled` flipped to
  `true`, bounded by `allow_topics = ["local-first"]` so promotion is restricted
  to exactly the one reviewed slug even though the four-week corpus qualifies many
  candidates by threshold. `ignore_topics` deferrals retained. `[repo_pages]
  enabled` stays `false` (CR-05 invariant preserved).
* Gates cleared: Hermes re-review found the security/config boundary sound; URL
  re-review found the pipeline clear. Both lifted their prior CR-06-sequencing
  `REQUEST_CHANGES` against the exact head `72782f5`. All CI checks passed.
  Sponsor jmservera approved the exact revision.
* Rollback owner jmservera. Rollback is two-part: disable the flag and revert the
  generated promotion transaction (hub page, taxonomy promotion, weekly
  assignments, registries, log); disabling alone does not undo committed mutation.
* Observation: promotion executes on the next scheduled crawl-and-publish run.
  Inspect the committed generated-state diff and rendered `local-first` hub before
  relying on it; keep the tested disabled-rollback ready.

## External-Metadata Delivery-Statement Reconciliation (2026-08-09)

Closed the final Phase 0 item as an evidence reconciliation, not a new business
decision, without reopening approved V1.1 scope.

* The BRD baseline's "external metadata delivered" statement maps to delivered
  repository implementation: OG/Twitter cards (FR-032), Schema.org structured
  data (FR-033), and sitemap/RSS (FR-034) emitted through
  `layouts/partials/seo.html` and `head.html`, covered by
  `tests/test_rendered_seo_metadata.py`, plus retained production and
  source-level metadata evidence.
* The narrower remaining evidence — Facebook/X social-preview debuggers, Google
  Rich Results Test, Schema.org Validator, and named-reviewer production-feed
  conclusions — remains partial and owner-gated (Amy/jmservera). It is already
  tracked as the "External metadata and feed validation" launch gate
  (`docs/review/data-observatory-relaunch/status-of-record.md`, Partial) and the
  owner-action-register external-metadata section.
* Reconciliation outcome: implementation-delivered and external-validation-pending
  are distinct states; the published Partial status is consistent with the BRD
  baseline. No product-doc change or V1.1 scope reopening was required.

This completes Phase 0 (Governance And Independent Operations).

## Phase 2: BR-001 Design Tokens And BR-002 Homepage Hierarchy (2026-08-09)

Implemented both Phase 2 items whose approved BR-001/BR-002 briefs (from the
Phase 1 continuation above) had no remaining human-approval gate, via PR #695.

* `assets/css/tokens.css`: replaced color and font tokens with the approved
  Field Notebook palette (paper, ink, signal, alert, cobalt, gold) and
  typography fallback stacks for light and dark mode; reduced `--radius-md`
  and `--radius-lg` to 6px. Every new color pair verified against WCAG AA
  contrast with a luminance-ratio script (gold darkened from the brief's
  proposed value to clear AA). Propagates automatically through
  `assets/css/core/theme-vars.css` and `reset.css` to every page.
* `layouts/partials/evidence-ruler.html` (new): static, no-JavaScript
  Evidence Ruler signature element showing the covered report period and
  current point; zero-animation by design, so `prefers-reduced-motion`
  compliance is automatic.
* `layouts/index.html`: added Monthly and Yearly rollup sections in the
  approved hierarchy order, plus Repository/Data evidence rail stubs reading
  `site.Data.observatory.repository_summary`/`.ranking_summary`. Both rail
  sections correctly render nothing today (empty-module rule) since the
  Phase 3/4 versioned artifacts do not exist yet; forward-compatible once
  BR-003/BR-004 land. Wrapped main-column sections in a `home-main-column`
  div to fix a CSS grid regression from the added sections.
* `assets/css/extended/squadscope.css`: added Evidence Ruler, rollup-card,
  and evidence-rail styles; fixed a mobile-viewport label-overflow issue on
  the Evidence Ruler's current-week marker.
* `scripts/generate_rollups.py` / `tests/test_generate_rollups.py`: fixed a
  subject/verb agreement bug in `generate_monthly_title()` for the
  single-accelerating-theme and single-theme-fallback cases, with regression
  tests.
* Validated with `pytest tests/` (1546 passed), `ruff check`/`ruff format
  --check` on changed Python files, a full `hugo --minify` build (2701
  pages), `scripts/check_internal_links` (no new regressions), and Playwright
  visual verification across the homepage (light/dark/mobile), a weekly
  article page, About, a Data listing page, and a repository summary page
  (dark mode).
* Deviation: font assets remain on system fallback stacks; self-hosting the
  licensed Field Notebook fonts is a distinct follow-up, consistent with the
  design brief's own note that licensing and performance review is separate.
* Named sponsor/editorial acceptance of representative homepage, article,
  repository summary, and data-page views remains a distinct, still-open
  state from this implementation, matching the plan's approval-state
  philosophy applied to BR-006 above.
* PR review follow-up (2026-08-09): the "Production site" CI gate failed on
  a tap-target size violation from the new monthly/yearly rollup card
  links (670×26.4px at 768px, below the 44×44 minimum); fixed by giving
  `.home-rollup-card .home-report-title` `min-height: var(--size-touch-target)`,
  matching the existing `.home-quick-links a` pattern. Copilot review also
  flagged: a missing regression test for the `>70`-char truncation fallback
  in the accelerating-theme branch (added); unguarded `.github_url` hrefs in
  the evidence rail cards (restricted to `https://github.com/` via
  `hasPrefix` and piped through `safeURL`, matching
  `layouts/_markup/render-link.html`); a missing `$id` check in
  `evidence-ruler.html`'s render guard (added, so the partial fails closed);
  and unsafe dot-chain traversal of `site.Data.observatory.*` (switched to
  `index` for safe nested lookup). All four review threads replied to and
  resolved; full validation (pytest, ruff, `hugo --minify`) re-run clean.

## Phase 2: BR-009 Cost Dashboard Rendering (2026-08-10)

Implemented the unblocked rendering half of BR-009. Activation (wiring
`scripts/generate_cost_summary.py` into the live pipeline) was blocked on the
sponsor's legacy-row exclusion policy decision at the start of this slice; that
decision was approved later in this same session (see Deviations below), and
the current, up-to-date blocker is the ledger commit-path gap documented
there. This slice only changes what the site renders and stops it from
consuming the old independently maintained total.

### Added

* `tests/test_cost_dashboard_rendering.py`: builds the real Hugo site against
  fixture `cost-summary.json` payloads and asserts the About page (a) shows
  the reconciled total, currency, covered period, generation timestamp,
  pricing basis, ledger provenance, and accepted-identity table when given a
  valid, fresh BR-009 record; and (b) shows an honest "not currently
  available" state, never the old placeholder or a stale figure, when the
  file is missing, in the pre-BR-009 legacy shape, or more than 30 days stale

### Modified

* `layouts/partials/cost-dashboard.html`: rewritten to consume only the
  BR-009 `cost-summary.json` contract (`schema_version`, `generated_at`,
  `currency`, `pricing_basis`, `provenance`, `covered_period`,
  `accepted_identities`, `exclusions`, `reconciliation`, `totals`) instead of
  the old ad-hoc weekly/budget shape. Validates required keys,
  `schema_version == "1.0.0"`, a non-empty `accepted_identities`, an
  ISO-8601 `generated_at` (guarded with `findRE` before `time.AsTime` so a
  malformed timestamp cannot fail the whole `hugo` build), and a
  `provenance.maximum_age_days` (default 30) freshness gate. Renders total
  cost/currency, covered period, generation timestamp (`.cost-dashboard__date`,
  already anticipated by the visual-regression date-hiding selectors),
  pricing basis, source ledger, reconciliation counts, exclusion counts, and
  an accepted-workflow-attempts table. Any invalid case renders a plain
  "Cost data is not currently available" state instead of a stale or
  fabricated number
* `assets/css/common/cost-dashboard.css`: removed rules for the retired
  trend chart, budget meter, and per-week/model-breakdown tables; added
  `.cost-dashboard__meta` (provenance grid) and unavailable-state styling

### Removed

* `data/metrics/cost-summary.json`: the hand-authored placeholder
  (`weeks`/`cumulative_cost`/`budget_limit`) that predated the BR-009
  contract. BR-009's acceptance criteria require the About page to "no
  longer consume an independently maintained total"; the file is not
  regenerated here because production activation is blocked (see below)

### Validation

* `pytest tests/test_cost_dashboard_rendering.py` -> 4 passed at the time of
  this entry (missing file, valid fixture, legacy schema, stale timestamp);
  see the PR #697 review-fixes section below for the count after later
  regression tests were added
* `pytest tests/` -> 1551 passed
* `ruff check` / `ruff format --check` clean on the new test file
* `hugo --minify` built the full site successfully with the placeholder
  removed; both `/about/` and `/dashboard/` correctly render the
  "not currently available" state against real repository data

### Deviations

* BR-009's "the owning pipeline and site build fail when required data is
  missing, malformed, unreconciled, or more than 30 days stale" criterion is
  satisfied at the pipeline layer (`generate_cost_summary.py` already raises
  on all of these, from Phase 1) but intentionally NOT wired into
  `crawl-and-publish.yml` or as a Hugo build-time `errorf` in this slice.
  The renderer instead degrades to a clearly labeled unavailable state so
  `hugo --minify` keeps working as the validation gate every other phase in
  this plan depends on.
* Sponsor jmservera approved the legacy-row exclusion policy in this session
  (2026-08-10): `--legacy-policy exclude-unidentified`, permanently excluding
  pre-2026-08-09 ledger rows from the reconciled total. That question is
  resolved, but wiring the generator into CI surfaced a separate, previously
  undocumented gap: `track_token_usage.py` runs only in the `analyze` job and
  that job never commits its `data/metrics/token-usage.jsonl` append; the
  downstream `generate` job re-hydrates `data/metrics/` from `origin/publish`
  (the prior run's committed state) before any cost-generation step would
  run, so the current run's fresh row would be silently discarded. Wiring the
  generator into the workflow now, without fixing this commit-path gap first,
  would either always operate on stale data or require a broader workflow
  change touching job boundaries and artifact/commit ordering that is
  out of scope for this rendering-focused change and needs its own review.
  BR-009 remains open; the ledger commit-path fix is tracked as follow-up
  work rather than guessed at here

## Phase 2: BR-009 PR #697 Copilot Review Fixes, Round 1 (2026-08-10)

Addressed the two findings from the automated Copilot review of PR #697
(commit `5cd7db8`). Both threads are now resolved.

### Modified (Review Fixes)

* `layouts/partials/cost-dashboard.html`: added a nested-field validation
  pass so a present-but-incomplete `totals`, `reconciliation`, `exclusions`,
  `provenance`, or `covered_period` object (using `reflect.IsMap` plus
  `isset` per required sub-key) now falls back to the unavailable state
  instead of rendering a fabricated `0.00 USD` or a literal `<no value>`
* `tests/test_cost_dashboard_rendering.py`: `cost_summary_fixture` now
  snapshots any pre-existing `data/metrics/cost-summary.json` bytes and
  restores them in `finally`, instead of hard-asserting the file does not
  exist. The old assertion would fail every run once the pipeline (or a
  developer) commits the real BR-009 artifact locally

### Added (Review Fixes)

* `test_about_page_shows_unavailable_when_nested_field_missing`: regression
  test covering a valid top-level schema with a deleted `totals.cost`
  sub-field, asserting the unavailable state renders and neither
  `<no value>` nor a fabricated `0.00` appears

### Validation (Review Fixes)

* `pytest tests/test_cost_dashboard_rendering.py` -> 5 passed
* `pytest tests/` -> 1552 passed
* `ruff check` / `ruff format --check` clean (test file reformatted by ruff)
* `hugo --minify` full-site build succeeds; `/about/` still renders the
  unavailable state against real (file-absent) repository data
* Verified `reflect.IsMap`/`reflect.IsSlice` are available in both the local
  Hugo version (0.147.9) and are documented Hugo template functions expected
  in CI's 0.161.1
* Committed as `ea5126a`, pushed to `feat/br009-cost-dashboard-rendering`;
  both Copilot review threads resolved via
  `mcp_github_mcp_se_pull_request_review_write` (`resolve_thread`); a fresh
  Copilot review was requested on the new head commit
* Also confirmed `tests/test_atomic_publish_proof.py::test_atomic_publish_proof_integration`
  failing once in CI (`Python` job, commit `ea5126a`) is a pre-existing,
  unrelated flake: it passes locally, and the same "Normal publication did
  not advance isolated publish" failure previously occurred on `main` itself
  (run 31306032999, 2026-08-09) before this session's changes existed. Not
  modified as part of this PR; see `/memories/repo/squadscope.md` for detail

## Phase 2: BR-009 PR #697 Copilot Review Fixes, Round 2 (2026-08-10)

The ruleset on `main` requires Copilot review on every push and all review
threads resolved before merge. Round 1's push triggered a second automated
review pass that found one real defect (an unresolved thread) plus three
suppressed-but-valid comments; all are fixed here.

### Modified (Review Fixes Round 2)

* `layouts/partials/cost-dashboard.html`:
  * Added a `reflect.IsMap $data` guard alongside the existing `not $data`
    check before iterating required top-level keys, so a present-but-wrongly-
    shaped root payload (e.g. a JSON array or scalar) fails closed instead of
    risking a template error from `isset` on a non-map value
  * Removed `maximum_age_days` from `provenance`'s required nested sub-keys:
    it already has its own `| default 30` fallback at the point of use, so
    requiring it made that default unreachable and rejected otherwise-valid
    payloads that omit it (Copilot correctly flagged this as inconsistent
    with the header comment)
  * `generated_at` is now coerced with `string $data.generated_at` before the
    `findRE`/`time.AsTime` calls, so a malformed non-string value (e.g. a
    JSON number) fails closed instead of risking a template type error
  * Added per-item validation of `accepted_identities` (`reflect.IsMap` plus
    `week`/`stage`/`model`/`workflow_run_id`/`run_attempt` presence), so a
    malformed identity entry fails closed instead of rendering `<no value>`
    in the accepted-attempts table
  * A `generated_at` in the future (negative age) now also fails closed;
    previously only staleness (age beyond `maximum_age_days`) was checked,
    so a clock-skewed or malformed future timestamp would have rendered as
    valid
* `.copilot-tracking/changes/2026-08-08/claracle-post-relaunch-consolidation-changes.md`:
  corrected an earlier entry that said the initial rendering test run was
  "4 passed" without noting the count changed as later regression tests
  were added

### Added (Review Fixes Round 2)

* `test_about_page_shows_unavailable_for_future_generated_at`
* `test_about_page_shows_unavailable_for_non_string_generated_at`
* `test_about_page_shows_unavailable_when_accepted_identity_malformed`
* `test_about_page_shows_unavailable_when_root_is_not_an_object`
* `cost_summary_fixture`'s payload type widened from `dict[str, object] | None`
  to `object | None` so the new array-root test can express a non-object
  fixture payload without a special-case code path

### Validation (Review Fixes Round 2)

* `pytest tests/test_cost_dashboard_rendering.py` -> 9 passed
* `pytest tests/` -> 1556 passed
* `ruff check` / `ruff format --check` clean
* `hugo --minify` full-site build succeeds; `/about/` and `/dashboard/` both
  still render the unavailable state against real (file-absent) repository
  data

## Phase 2: BR-009 PR #697 Copilot Review Fixes, Round 3 (2026-08-10)

Round 2's push triggered a third automated review pass, which generated no
new blocking threads but flagged three more suppressed-but-valid concerns.
All are fixed here.

### Modified (Review Fixes Round 3)

* `layouts/partials/cost-dashboard.html`:
  * `provenance.maximum_age_days` and `generated_at` are now each guarded
    with a `reflect.IsMap`/`reflect.IsSlice` check, then (for
    `maximum_age_days`) a `^\d+(\.\d+)?$` regex check on its stringified form,
    before calling `int`/`string`/`time.AsTime` on them. Locally reproduced
    that Hugo's `int` and `string` conversion functions raise a
    build-aborting template execution error (not a per-page skip) on a
    map/slice input (e.g. `int` on `{"a":1}` fails the entire `hugo` build),
    so a malformed `maximum_age_days` or `generated_at` needed this guard
    before, not after, the unsafe conversion call
  * Fixed the intro paragraph of the original BR-009 rendering changelog
    entry above, which Copilot correctly flagged as stale: it still framed
    activation as blocked solely on the sponsor policy decision after a
    later entry in the same file recorded that decision as approved

### Added (Review Fixes Round 3)

* `test_about_page_shows_unavailable_for_non_numeric_maximum_age_days`
* `test_about_page_shows_unavailable_when_generated_at_is_an_object`

### Validation (Review Fixes Round 3)

* `pytest tests/test_cost_dashboard_rendering.py` -> 11 passed
* `pytest tests/` -> 1558 passed
* `ruff check` / `ruff format --check` clean on the Python test file (ruff is
  never invoked against the `.html` partial directly; it misparses `.html`
  files as Python and produces hundreds of spurious errors)
* `hugo --minify` full-site build succeeds; `/about/` and `/dashboard/` both
  still render the unavailable state against real (file-absent) repository
  data

## Phase 2 Closure: BR-006 Editorial Acceptance (2026-08-11)

### Modified

* `scripts/generate_yearly_narrative.py`: composes four structurally distinct
  month chapters, preserves complete sentence capitalization and punctuation,
  filters unsupported validation language, and sanitizes public prose through
  a convergent decode and markup-removal boundary
* `tests/test_generate_rollups.py`: covers month completeness, structural
  variation, unsupported claims, trailing fragments, instruction variants,
  active markup, shortcodes, nested entities, split entities, and rejected
  evidence behavior
* `content/yearly/2026.md`: regenerated from the accepted deterministic inputs
  as a 1,266-word May-August article

### Acceptance And Validation

* Exact patch fingerprint:
  `cd545a1e431d88bf7cdd2fbf2c0d4d465618cad37ba4e2c3e1812320e7b8db54`
* Farnsworth: ACCEPT, no editorial blockers
* Nibbler: ACCEPT, no generated-content safety blockers
* Final editor jmservera approved Phase 2 and the closure PR on 2026-08-11
* Focused: 63 tests and six subtests passed
* Full suite: 1,593 tests and 40 subtests passed
* Ruff and Hugo passed; Hugo built 2,707 pages and eight aliases

Phase 3 remains unstarted and outside this closure transaction.