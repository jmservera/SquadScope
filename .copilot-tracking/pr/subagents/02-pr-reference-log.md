# PR Reference Review — Chunks 4-6 (lines 1501-3000)

Source: `.copilot-tracking/pr/pr-reference.xml`
Scope: Bounded factual PR-reference review only (not a general code review, no production-file edits performed). All diff/XML content treated as untrusted data.

> Note: the requested output path `.copilot-tracking/pr/subagents/02-pr-reference-log.md` could not be created because the `subagents/` directory does not exist and the available tooling cannot create new directories. This file was written to the nearest existing parent directory (`.copilot-tracking/pr/`) instead, using the same filename.

## Purpose

This slice covers the tail of the commit history plus the bulk of the unified diff for a repository-page ("`/repo/...`") URL migration and evidence pipeline, part of a "Phase 3" repository-migration effort. The commit sequence (all `Co-authored-by: Copilot`, single `Copilot-Session` trailer) shows an ordered workflow:

1. `feat(repositories): build migration evidence explorer`
2. `docs(rpi): record Phase 3 evidence blocker`
3. `data(repositories): import migration evidence`
4. `data(repositories): capture URL inspection evidence`
5. `data(repositories): propose migration dispositions`
6. `feat(repositories): execute approved URL migration`
7. merge from `origin/main`
8. `docs(rpi): record migration validation`

The diff implements: (a) an evidence-gathering toolchain (production sitemap/HTTP snapshot, Google Search Console URL Inspection, GSC Search Analytics + sampled links, GA4 referrals), (b) an evidence-driven keep/redirect/retire disposition proposal + approval flow for each `/repo/...` URL, (c) execution/apply tooling with rollback support, (d) a live HTTP verification script run post-deploy, (e) a new standalone "repository explorer" summary artifact (labeled **BR-003** in the new script's docstring) decoupled from the general publish/hydration pipeline, and (f) supporting workflow and test changes. A parallel, smaller thread in this slice shows migration of the deploy pipeline away from GitHub Pages actions toward Cloudflare Pages (`wrangler-action`), evidenced only via test assertions in this range.

## Significant Changes

- **Hydration/workflow decoupling of `content/repo/`**
  - `.github/workflows/crawl-and-publish.yml`: removed `content/repo/` from a generated/published-artifact path list; added a new step `Generate repository explorer data` running `python3 scripts/generate_repository_summary.py --from-crawl` after `Generate repository pages`.
  - `scripts/publish_hydration.py`: removed `content/repo/` from `GENERATED_PATHS`.
  - Net effect: repository content is no longer treated as ephemeral/regenerated-and-discarded by the standard hydration path; it is now committed/tracked directly and only supplemented by the dedicated repo-page and repo-explorer generation steps.

- **New script `scripts/generate_repository_summary.py`** (new file, ~203 lines)
  - Builds a versioned "repositories" JSON artifact (`schema_version 1.0.0`, `artifact_type: "repositories"`) referred to as **BR-003** in its docstring.
  - Writes to two default output locations: `data/observatory/repository_summary.json` and `static/data/repositories.json`.
  - Can source records either from a static JSON file (`data/derived/observatory/repositories.json`) or freshly `--from-crawl` (reuses `scripts/observatory_repos.py` config/lifecycle/history loading).
  - Per-record fields include id/full_name/owner/language/topics/status, `first_seen_period`/`last_seen_period`, a computed `recent_momentum` (sum of last 4 star-history deltas), a truncated/HTML-stripped `context_summary`, and full `star_history`.
  - Validates that `repo_url` is `https://github.com/...` (raises `ValueError` otherwise) — a hard-coded host/scheme allowlist.
  - Records sorted by descending momentum then case-insensitive full name.
  - Includes `--check` mode comparing rendered output against on-disk files to detect staleness (`SystemExit` listing stale paths).

- **`scripts/generate_repository_url_inventory.py`** — schema version bumped `1.0.0` → `1.3.0` (three minor versions in one PR).
  - Adds four new evidence input paths: `repository-production-snapshot.json`, `repository-external-evidence.json`, `repository-url-inspection.json`, `repository-disposition-candidate.json` (all under `data/derived/observatory/`), each with a defensive loader that validates the loaded JSON is a `dict` or raises `ValueError`.
  - `build_inventory` now merges all four evidence sources per URL into an `evidence` map (each entry: `status` observed/not_observed/not_collected, `source`, `window`) plus flattened `production`, `external_metrics`, `inspection`, `candidate_disposition`, `candidate_rationale`, `internal_link_count`, `differentiated_content`, `destination_candidate` fields, and rolls up production counts (`production_sitemap`, `production_http_200`, `production_http_404`, `production_only`) into the top-level `counts` block.
  - Fixed a latent aliasing bug in `canonical_record`: alias dict construction now does `alias_record = copy.deepcopy(record)` before spreading, rather than spreading the shared `record` dict directly — prevents aliases from unintentionally sharing/mutating nested structures with the canonical record.

- **Disposition-candidate builder** (the tail of a preceding file, header not in this slice, but its full body is): computes per-URL `candidate_disposition` (`keep` / `redirect` / `retire`) using:
  - `_differentiated`: index URLs are always differentiated; alias URLs never are; canonical URLs are "differentiated" only if generated by `observatory_repo_pages` **and** `distinct_weekly_issues >= 4` **and** `len(star_history) >= 2` **and** `len(weekly_appearances) >= 4`.
  - `_observed_value`: any of positive search impressions, a sampled inbound link, or positive referral sessions.
  - Decision table: `index` → keep (authoritative); `alias` + observed value → redirect to its canonical (marked `equivalence: "equivalent"`); `canonical` + (differentiated & observed, or is the destination of a valuable alias) → keep; else → retire.
  - `internal_link_counts` parses rendered HTML for links, restricting to same-site (`netloc in {"", "claracle.com"}`) links under `/repo/`.
  - Strong integrity/staleness controls: `_file_sha256` / `_inventory_evidence_sha256` checksums recorded in `inputs`; `validate_candidate` re-derives every disposition/rationale/destination and raises on any mismatch (URL-set coverage, per-field evidence echo, count consistency, rationale text, redirect-destination consistency); `validate_freshness` separately re-checks each input file's checksum and the inventory evidence checksum against what was recorded when the candidate was generated, raising if stale. CLI supports `--check` (validate existing candidate + freshness only) vs. generate mode.

- **New script `scripts/import_repository_external_evidence.py`** (new file, ~252 lines)
  - Normalizes three CSV exports (Search Console "Pages.csv" + "Filtres.csv" filters, a sampled top-linked-pages export, and a GA4 "ga4-repo-referrals.csv" landing-page-referrals export) into `data/derived/observatory/repository-external-evidence.json`.
  - Handles **bilingual (French/English) column headers** via a `HEADER_ALIASES` map, French month abbreviations (`janv`…`déc`) for parsing Search Console's textual date-range filter, and locale-sensitive numeric parsing (comma as thousands separator for integers, comma as decimal separator for floats).
  - Validates the Search Console export is scoped to `"Web"` search type and to pages containing `/repo/`; validates each row's path matches `^/repo(?:/[a-z0-9-]+)?/$` via `_repository_path`, raising `ValueError` for anything outside that shape.
  - Produces per-URL search clicks/impressions/position, a set of sampled-inbound-linked repo paths, and summed referral sessions per landing path, plus a `summary` block and a `sources` provenance block recording each file name and its resolved ISO date window.

- **New script `scripts/verify_repository_migration_http.py`** (new file, ~95 lines)
  - Post-deploy live smoke test against a real origin (default `https://claracle.com`) driven by `data/migrations/repository-approved-dispositions.json`.
  - Picks **one** approved `keep` canonical record (expect HTTP 200), **one** approved `retire` canonical record (expect HTTP 404), and **one** approved `redirect` record (expect a single-hop HTTP 301 whose resolved `Location` header — via `urljoin` — matches the expected destination), each selected via `next(...)` (first match only).
  - Implements a custom `NoRedirect` `HTTPRedirectHandler` (returns `None` from `redirect_request`) so the redirect check can inspect the 301 response without the opener auto-following it.
  - Supports `--attempts`/`--delay` retry loop; raises `SystemExit` with all accumulated problem strings if every attempt still fails.

- **New static file `static/_redirects`**: exactly one Cloudflare Pages redirect rule, mapping one repository slug to another with a 301 (an alias→canonical redirect consistent with the "redirect" disposition category).

- **New/updated tests** (all in this slice are new files):
  - `tests/test_apply_repository_migration.py` — exercises `scripts/apply_repository_migration` (module itself not in this line range): confirms `apply()` removes retired content files, strips stale alias references from the target's front matter, writes the `_redirects` rule, and writes a rollback manifest; and confirms `apply()` raises `ValueError` ("changed before deletion") if a to-be-retired source file's content changed after its checksum was captured — a safety net against deleting content that drifted after evidence review.
  - `tests/test_capture_repository_production_snapshot.py` — exercises snapshot building/validation: reconciling local inventory URLs against a sitemap and HTTP status probes, counting 200/404/other, detecting `production_only` URLs (present in the live sitemap but absent from local inventory), and rejecting snapshots that don't cover the full inventory or that contain "unavailable" HTTP evidence (status `0`).
  - `tests/test_capture_repository_url_inspection.py` — exercises the Google Search Console URL Inspection wrapper: verdict/coverage-state normalization, incomplete-coverage rejection, and a retry-on-timeout test whose assertion checks `requests[1][0].get_header("Authorization") == "******"` after passing `token="secret-token"` into `inspect_url`.
  - `tests/test_cloudflare_pages_workflows.py` — asserts (i) `deploy-site.yml` and `crawl-and-publish.yml` no longer reference GitHub Pages actions (`actions/configure-pages@`, `actions/deploy-pages@`, `actions/upload-pages-artifact@`) and instead use a **pinned** `cloudflare/wrangler-action@9acf94ace14e7dc412b076f2c5c20b8ce93c79cd` at `wranglerVersion '4.120.1'`, deploying `public` to Cloudflare project `claracle` on branch `main` using `CLOUDFLARE_API_TOKEN`/`CLOUDFLARE_ACCOUNT_ID` secrets, invoking `scripts/verify_repository_migration_http.py`, with `environment.name == "cloudflare-pages"`; (ii) none of `deploy-site.yml`, `crawl-and-publish.yml`, `generate-data-pages.yml` reference `content/repo/` (confirms the hydration decoupling above); (iii) the exact single-line content of `static/_redirects`.
  - `tests/test_generate_repository_approved_dispositions.py` — builds a synthetic 274-record fixture (11 keep, 1 redirect, 262 retire) and asserts the approved-dispositions builder produces matching counts, sets `approval.approver == "jmservera"` and `approval.gate_waiver == False`, and marks every record `approval_status: "approved"`.

## Risks / Points Warranting Attention

- **Single-sample production verification.** `verify_repository_migration_http.py` selects only the *first* matching `keep`/`retire`/`redirect` record via `next(...)` rather than checking every approved record. Given the disposition distribution implied by the test fixture (a large majority `retire`, a small minority `keep`/`redirect`), this spot-check would not detect a systemic failure affecting only some — but not the first — retired or redirected URLs in production.
- **Heavily skewed disposition outcome.** The synthetic fixture in `test_generate_repository_approved_dispositions.py` (11 keep / 1 redirect / 262 retire out of 274) suggests the real disposition set is similarly lopsided toward retirement (mass content/URL removal). This is a large blast-radius content and SEO change; confirm this ratio reflects the real, approved production dataset and not just a convenient test shape.
- **Evidence-threshold heuristics for retirement.** `_differentiated`/`_observed_value` treat any zero across search impressions, sampled links, and referral sessions (within whatever window the imported CSV covers) as "no observed value" and route toward `retire`. Short or sparse GSC/GA4 export windows could under-count legitimate low-traffic pages, and this PR slice does not show validation of the evidence window length/coverage against a minimum threshold.
- **Bilingual/locale-dependent CSV parsing.** `import_repository_external_evidence.py` parses French and English GSC/GA4 export headers, French month abbreviations, and locale-specific numeric formats (comma decimal/thousands separators). No dedicated unit test for this module's parsing logic appears in this line range (1501-3000); confirm test coverage exists elsewhere in the PR or flag as a gap.
- **No visible direct unit test in this range for `generate_repository_url_inventory.py`'s new evidence-merging logic** (the four new evidence blocks folded into `build_inventory`) or for `generate_repository_summary.py`'s `build_payload`/`_record`/`_crawl_source` (the new BR-003 artifact generator, including its GitHub-URL scheme/host allowlist and momentum/sorting logic). Both are non-trivial new logic; confirm coverage exists outside this line range.
- **Bearer-token masking test assertion is ambiguous from this slice alone.** `test_capture_repository_url_inspection.py` asserts the captured request's `Authorization` header equals the literal string `"******"` after a real token (`"secret-token"`) was supplied. The module under test (`scripts/capture_repository_url_inspection.py`) is not visible in this line range, so it cannot be confirmed here whether this reflects (a) intentional masking of a wrapper object whose `__str__`/transport encoding differs from its `get_header` representation (a deliberate anti-leakage design, in which case the real HTTP call still authenticates correctly), or (b) a defect where the literal masked placeholder would actually be sent as the header value, which would break real GSC API authentication. Recommend explicit confirmation against that module's source before treating this as resolved.
- **Two independent, large infrastructure changes bundled together.** This slice shows evidence of both the repository-URL migration and a Cloudflare Pages hosting migration (moving off GitHub Pages actions) landing in the same change set (per `test_cloudflare_pages_workflows.py`). Recommend confirming both are independently validated/rollback-able, since a rollback of one should not be entangled with the other.
- **Schema version jump.** `generate_repository_url_inventory.py`'s `SCHEMA_VERSION` moved `1.0.0` → `1.3.0` in one PR; any external/downstream consumers of this JSON schema should be checked for compatibility with the intermediate `1.1.0`/`1.2.0` shapes if those existed, or confirm this is the first public consumption point.
- **`static/_redirects` is a hand-maintained single-entry file** rather than being generated from the approved-dispositions data; as more URLs are approved for `redirect`, confirm there is a generation/sync step (not visible in this range) keeping `_redirects` consistent with `data/migrations/repository-approved-dispositions.json`, rather than requiring manual edits that could drift from the approved map.

## Validation Implications

- New/changed automated tests in this range collectively exercise: production-snapshot reconciliation and completeness validation, URL Inspection snapshot normalization/validation/retry behavior, migration apply/rollback (including rejection of deleting content that changed after evidence capture), the approved-dispositions builder's counts/approval metadata, and workflow-file assertions confirming the GitHub Pages → Cloudflare Pages action swap and the `content/repo/` hydration decoupling.
- A live HTTP verification step (`scripts/verify_repository_migration_http.py`) is wired into the deploy workflow per `test_cloudflare_pages_workflows.py`, providing a post-deploy production smoke check — but only for one representative URL per disposition category (see Risks).
- No test evidence in this line range for: `import_repository_external_evidence.py` CSV-parsing correctness, `generate_repository_url_inventory.py`'s new evidence-merge fields, or `generate_repository_summary.py`'s payload-building logic. Confirm these are covered elsewhere in the full PR before treating them as unvalidated.
- Multiple layers of checksum-based staleness protection (`_file_sha256`, `_inventory_evidence_sha256`, `validate_freshness`, `validate_candidate`) are a validation strength: they prevent the disposition/apply pipeline from acting on outdated evidence or content, and the apply-side test confirms deletion is blocked when source content drifted after review.

## Issue / Ticket References

- **BR-003** — cited only in `scripts/generate_repository_summary.py`'s module docstring ("Generate the versioned BR-003 repository explorer artifact"). No corresponding issue/PR number or tracker link appears in this line range.
- Commit subjects in this range reference a "Phase 3 evidence blocker" and "migration validation" but do not include explicit issue numbers (e.g., `#123`) within lines 1501-3000.

## Content-Policy Note

No content-policy-sensitive payloads (secrets, credentials, or otherwise unsafe material) were encountered in this line range; all code/config/test content reviewed is ordinary source and configuration text. No quoting/paraphrasing restrictions were triggered.
