# PR Reference Review — Chunks 7–9 (lines 3001–4096)

> **Path note:** the requested output directory `.copilot-tracking/pr/subagents/` does not
> exist in this workspace, and the tools available in this session can only create files
> under directories that already exist (no directory-creation capability). This log was
> written to `.copilot-tracking/pr/03-pr-reference-log.md` instead, consistent with the same
> workaround already used for the chunk 1–3 log (`01-pr-reference-log.md`). Please
> move/copy it into `subagents/` (or create that directory) if the exact path is required
> downstream.

**Scope note:** Bounded factual review of `pr-reference.xml` lines 3001–4096 only, for PR
description generation. Diff content treated as untrusted data; no production files were
edited as part of this task.

**Branch context (from file header):** `feat/repository-migration-phase3` → `origin/main`.

## Purpose

These lines cover new and updated **test files** supporting a repository-URL migration and
consolidation effort (Phase 3), matching the commit-history subjects visible in the file
(`propose migration dispositions`, `capture URL inspection evidence`, `import migration
evidence`, `execute approved URL migration`, `build migration evidence explorer`, `record
migration validation`). The tests establish the contract for:

- Generating and validating a per-URL "disposition candidate" (keep / redirect / retire)
  from crawl, search, and inspection evidence.
- Locking in an "approved dispositions" ledger that later steps must not drift from.
- Producing a versioned, deterministic `repository_summary.json` dataset that feeds a new
  client-side "Repository Explorer" filter/sort UI, replacing the previous one-page-per-repo
  generation model for most repositories.
- Importing localized Google Search Console / GA4 CSV exports as external evidence, with
  strict scoping/format validation.
- Migrating the deployed site from GitHub Pages to a Cloudflare Pages / custom-domain
  (`claracle.com`) deployment.

## Significant changes observed in this range

1. **`tests/test_generate_repository_approved_dispositions.py` (new; tail already started
   before line 3001):** confirms `approved.build()` raises `ValueError` ("Candidate
   drift") when a candidate's `candidate_disposition` is mutated after generation but before
   the inventory is reconciled — protects the approval ledger from silently accepting stale
   or tampered dispositions.

2. **`tests/test_generate_repository_disposition_candidate.py` (new, ~169 lines):** exercises
   `generate_repository_disposition_candidate`:
   - Index and alias-with-value records are kept; a canonical with demonstrated value is kept;
     an alias pointing to a valuable canonical is classified `redirect`; a no-signal record is
     `retire`. Verified via `counts` (`total/keep/redirect/retire/pending_approval`) and
     per-record `candidate_disposition` / `internal_link_count`.
   - `validate_candidate()` rejects a `keep` disposition on a record with no demand signal and
     rejects any record whose approval status has been forged to `"approved"` (schema expects
     `"pending"` at candidate stage) — this is a `jsonschema.ValidationError`, i.e., schema-level
     enforcement, not just app logic.

3. **`tests/test_generate_repository_summary.py` (new, ~120 lines):** exercises
   `generate_repository_summary`:
   - `build_payload()` is deterministic (same input → identical output twice), stamps
     `schema_version` (`1.0.0`) and `artifact_type` (`repositories`), computes a
     `covered_period` window/label from weekly data, sanitizes HTML out of repo descriptions
     into a bounded (`≤240` char, ellipsis-terminated) `context_summary`, dedupes/sorts topic
     tags, computes `recent_momentum` from star deltas, and defaults record ordering to
     momentum descending.
   - Rejects non-GitHub `repo_url` values and empty source data.
   - `--check` mode requires both configured output paths to exist and match, exiting
     non-zero naming the missing static output otherwise.

4. **`tests/test_generate_repository_url_inventory.py` (existing, extended):**
   - `counts` now also reports `production_sitemap` / `production_http_200` /
     `production_http_404` / `production_only` (nullable until a production snapshot is
     joined).
   - Each record gains `candidate_disposition`, `candidate_rationale`, `internal_link_count`,
     and structured `production` / `external_metrics` / `inspection` sub-objects (all
     `not_collected`/`None` by default).
   - New joins are tested independently: production snapshot (sitemap/HTTP status),
     external evidence (search clicks/impressions/position, sampled inbound links, referral
     sessions), URL Inspection API verdicts (`verdict`, `coverage_state`, canonical fields),
     and the disposition-candidate file (`candidate_disposition`, rationale, internal link
     count) — each surfaced back into per-record `evidence.<source>.status`.
   - Alias and canonical evidence are explicitly isolated: an alias does not inherit its
     canonical's "observed" sitemap/HTTP evidence.
   - A JSON Schema (`data/schemas/repository-url-inventory.schema.json`) is asserted to
     **reject** a record proposing `retire` + `approved` when no supporting evidence has been
     collected — i.e., retirement is schema-gated on evidence, not just convention.

5. **`tests/test_import_repository_external_evidence.py` (new, ~128 lines):** exercises
   `import_repository_external_evidence` against **localized (French) GSC/GA4 CSV exports**
   (`Pages.csv`, `gsc-top-linked-pages.csv`, `ga4-repo-referrals.csv`, `Filtres.csv`):
   - Normalizes localized headers/percentages, extracts search analytics per URL, sampled
     inbound-link paths, and first-party referral session counts from a GA4 report with a
     date-range comment header.
   - Accepts a metadata-only GA4 export (no rows) as an empty-referrals result rather than
     failing.
   - Rejects a search export missing the impressions header, and separately rejects a search
     export whose applied filter is **not scoped to `/repo/`** (must fail if the Google
     Search Console export filter targets a different path, e.g. `/weekly/`).

6. **`tests/test_observatory_repos.py` (existing, modified):** the frozen-corpus lifecycle
   test's invariant changed — it no longer asserts that every qualified repository identity
   has its own rendered page. Instead it asserts qualified identities equal derived-history
   identities (still 266), and separately computes the **subset retained for publishing**
   from `data/migrations/repository-approved-dispositions.json` (`url_type == "canonical"`
   and `disposition == "keep"`), asserting that only that approved subset maps to rendered
   page identities. The inline comment attributes this to **"BR-003"**: published profile
   pages are now limited to sponsor-approved canonical keeps, decoupled from the full derived
   history. A second test in this file also updates the expected rendered repo slug from
   `anthropics-claude-code` to `odysseus-dev-odysseus`.

7. **`tests/test_pipeline.py`:** `content/repo/` is removed from the list of paths the
   publish transaction is expected to carry — i.e., repo profile pages are no longer part of
   the generic generated-content publish/hydration set. The weekly Discord/webhook message
   test now expects the link `https://claracle.com/weekly/` instead of
   `https://jmservera.github.io/SquadScope/weekly/` — confirms a site domain change.

8. **`tests/test_publish_hydration.py`:** adds an explicit assertion that
   `content/repo/` is **not** in `GENERATED_PATHS`, consistent with #7 above — repo pages are
   now curated/migrated rather than routinely regenerated by the publish pipeline.

9. **`tests/test_rendered_seo_metadata.py`, `tests/visual/a11y-perf.spec.mjs`,
   `tests/visual/observatory-a11y.spec.mjs`:** all update the example rendered repository
   fixture path from `repo/anthropics-claude-code/` to `repo/odysseus-dev-odysseus/`,
   consistent with the identity/slug change flagged in item 6.

10. **`tests/test_rendered_weekly_links.py`:** `TARGET_WEEK` changes from `W30` to `W21`
    (moves the boundary case tested toward the start of the dataset). The neighbor-window
    computation is hardened with `max(0, target_index - 1)` to avoid a negative-index slice
    wraparound when the target week is first in the sorted list, and the assertion loosens
    from "exactly 2 chronological neighbor links" to "at least one" — correctly handling
    weeks with fewer than two neighbors at either end of the dataset. This looks like an
    independent robustness/edge-case fix riding along with the migration branch.

11. **`tests/test_repository_explorer.py` (new, ~188 lines):**
    - Runs `scripts/generate_repository_summary.py --from-crawl --check` as a subprocess and
      validates the resulting `data/observatory/repository_summary.json` against both an
      envelope schema and a per-record schema.
    - Builds the site with Hugo (skips if the `hugo` binary is absent) and asserts the
      rendered `/repo/` index contains one `data-repo-record` element per summary record, the
      explorer container marker, a dataset-download affordance, an example external GitHub
      link (`https://github.com/2dust/v2rayN`), and a minified bundle reference
      (`repository-explorer.min.*`).
    - Runs a Node.js smoke test (skips if `node` is absent) that loads
      `assets/js/repository-explorer.js` into a hand-built DOM-like mock and exercises
      `initRepositoryExplorer`: invalid `period`/`sort` query-string values are reset to
      defaults, an empty search result renders "No repositories" guidance, and history is
      updated via one `replaceState` (initial normalization) and one `pushState`
      (user-driven filter change).

## Risks

- **Schema-gated retirement is a strong safety net but only as good as its evidence
  pipeline.** Evidence status is derived from joined production snapshots, external CSV
  imports, and inspection API data — any gap or stale file in that join chain could leave a
  record's evidence permanently `not_collected`, blocking legitimate retirements, or
  conversely a bug in the join could mark evidence `observed` incorrectly and allow an
  unjustified retire/approve. Worth checking that the join precedence (which of production /
  external / inspection evidence "counts") matches the schema's actual gating.
- **Locale-fragile CSV parsing.** External evidence import depends on specific French-locale
  header text and a hyphenated French date-range format from Google's export UI. Any change
  to Google's report locale, column order, or export format could silently misparse figures
  the code doesn't explicitly validate, or throw only for the header cases the tests
  enumerate (missing-impressions-header and out-of-scope-filter are covered; other malformed
  variants are not tested here).
- **Hardcoded single-redirect assertion.** Only `test_approved_redirect_rule_is_one_hop_and_permanent`
  (immediately preceding this chunk) pins `static/_redirects` to exactly one literal 301 line;
  if the real approved-dispositions set for this migration produces more than one redirect,
  that test (outside this chunk but adjacent) would need reconciling against actual output —
  worth flagging for the reviewer even though it's not fully inside lines 3001–4096.
- **Content-surface narrowing.** Moving `content/repo/` out of the generic generated/hydrated
  path set, combined with BR-003 restricting rendered pages to approved "keep" canonicals,
  means most previously-generated repo pages will no longer be rendered/published. If the
  approved-dispositions ledger under-counts legitimate "keep" candidates (e.g., due to a
  threshold or evidence-join bug), previously indexed content could be dropped without the
  redirect/retire safety checks catching it, since those checks operate on the ledger's own
  data rather than an independent source of truth.
- **Deploy/domain cutover.** The webhook URL change (`jmservera.github.io/SquadScope` →
  `claracle.com`) plus the earlier-in-file Cloudflare Pages/wrangler-action wiring imply a
  live domain and hosting-provider cutover bundled into this same feature branch. Any DNS,
  secret (`CLOUDFLARE_API_TOKEN`/`CLOUDFLARE_ACCOUNT_ID`), or verification-timing issue during
  cutover is an operational risk independent of the URL-migration logic itself.
- **Narrow client-side test double.** The Node smoke test for `repository-explorer.js` uses a
  minimal hand-rolled `Element`/`document`/`window` mock rather than a real DOM (jsdom/
  browser). It validates one scenario (invalid query params reset + empty-result messaging +
  history call counts) — real browser behavior (e.g., additional DOM APIs, CSS-dependent
  behavior, keyboard/focus handling) is not exercised here.
- **Test-fixture identity churn.** Multiple unrelated test files (SEO metadata, two Playwright
  visual specs) needed synchronized updates from `anthropics-claude-code` to
  `odysseus-dev-odysseus` as the canonical example repo — indicates the example fixture repo
  itself was migrated/consolidated (per the `test_observatory_repos.py` comment about
  rename/ownership-transfer identity consolidation), so this is expected churn, but it's
  fixture-wide and worth confirming no other hardcoded reference to the old slug was missed
  outside this chunk.

## Validation implications

- New/extended tests depend on `jsonschema` (`Draft202012Validator`, `ValidationError`) being
  available in the test environment, and on schema files (`repository-url-inventory.schema.json`,
  `observatory-envelope.schema.json`, `repository-record.schema.json`, and an implied
  disposition-candidate schema) shipping alongside the code in this PR.
- `tests/test_repository_explorer.py` includes real subprocess/integration checks: it invokes
  `scripts/generate_repository_summary.py --from-crawl --check`, runs a full `hugo --minify`
  build, and shells out to `node`. These gracefully `pytest.skip()` when `hugo`/`node` are
  unavailable, so CI must have both binaries installed for this coverage to actually execute
  rather than silently skip.
- `tests/test_observatory_repos.py`'s updated invariant depends on
  `data/migrations/repository-approved-dispositions.json` existing and being internally
  consistent with the derived corpus (266 qualified identities) — that file's content is
  outside this chunk's line range but is load-bearing for the test to pass; reviewers should
  confirm it's included and matches expectations.
- The domain-change assertion (`https://claracle.com/weekly/`) and the Cloudflare Pages
  deployment assertions (adjacent to this chunk) imply corresponding non-test changes
  (workflow files, `static/_redirects`, DNS/hosting config) must be present elsewhere in the
  PR and kept in lockstep with these test expectations.
- The weekly-links boundary-case fix (`TARGET_WEEK` = `W21`, `max(0, ...)` guard) should be
  checked against the actual production implementation file (not shown in this chunk) to
  confirm the non-test code was updated to match, not just the test's own neighbor-window
  computation.

## Issue references

No explicit issue/PR references (e.g., `#123`, "Fixes #", "Closes #") appear within lines
3001–4096. The only traceability markers present are an internal business-rule id, **BR-003**
(cited in a `tests/test_observatory_repos.py` comment as the rationale for limiting published
repository pages to sponsor-approved canonical keeps), and commit-subject labels visible in
the surrounding commit history (`docs(rpi): record migration validation`,
`docs(rpi): record Phase 3 evidence blocker`) suggesting an internal "RPI"
(repository-page-inventory or similar) tracking document rather than a GitHub issue number.
