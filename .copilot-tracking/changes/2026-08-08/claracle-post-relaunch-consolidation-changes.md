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
`scripts/generate_cost_summary.py` into the live pipeline) remains blocked on
the sponsor's legacy-row exclusion policy decision, per BRD ("jmservera
approves pricing-basis changes and exceptions"); this slice only changes what
the site renders and stops it from consuming the old independently
maintained total.

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

* `pytest tests/test_cost_dashboard_rendering.py` -> 4 passed (missing file,
  valid fixture, legacy schema, stale timestamp)
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
  Doing so today would either require unilaterally choosing a legacy-row
  policy the BRD reserves for sponsor approval, or would fail every future
  crawl-and-publish run outright (all current ledger rows predate workflow
  identity). The renderer instead degrades to a clearly labeled unavailable
  state so `hugo --minify` keeps working as the validation gate every other
  phase in this plan depends on. BR-009 remains open pending that sponsor
  decision; see the plan's BR-009 checklist item for the specific question
