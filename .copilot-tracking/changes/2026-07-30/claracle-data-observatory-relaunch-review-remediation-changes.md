<!-- markdownlint-disable-file -->
# Changes: Claracle Data Observatory Relaunch Review Remediation

## Metadata

* Related plan: `.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md`
* Implementation date: 2026-07-30
* Branch: `feat/observatory-relaunch-remediation`
* Pull request: `jmservera/SquadScope#623`
* Candidate base commit: `f7adea1a4f06b2e0d3417956e9d00b42343939fc`

## Summary

Repository remediation is implemented for lifecycle safety, exact-content Podcaster verification, breadcrumbs, analytics privacy coverage, browser-project parity, dynamic-topic sanitization, dataset reporting, and workflow security. Both rollout flags remain disabled.

Atomic publication proof, protected Podcaster execution, hosted browser and Lighthouse validation, and separate sponsor decisions are complete. Timing-budget approval, production analytics and GSC baseline evidence, final security and accessibility sign-off, external debugger conclusions, and refreshed visual acceptance remain open.

## Added

* `data/derived/observatory/repository-lifecycle.json` - deterministic lifecycle seed with 2,242 fallback histories and 263 qualified histories
* `.copilot-tracking/research/2026-07-30/claracle-data-observatory-relaunch-review-remediation-research.md`
* `.copilot-tracking/research/subagents/2026-07-30/claracle-data-observatory-relaunch-review-remediation-research.md`
* `.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md`
* `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md`
* `.copilot-tracking/plans/logs/2026-07-30/claracle-data-observatory-relaunch-review-remediation-log.md`

## Modified

### Lifecycle and Podcaster

* `scripts/observatory_repos.py` and `tests/test_observatory_repos.py` - fail-closed deletion confirmation, ledger-only seed, migration, parity, rendering, and idempotence
* `scripts/podcaster_handoff.py`, `tests/test_podcaster_handoff.py`, and `.github/workflows/podcaster-handoff-smoke.yml` - opt-in exact UTF-8 article payload and checked-in release evidence verifier
* `tests/test_pipeline.py` - executable workflow, publication, local-baseURL, and security contracts

### Browser, Privacy, and Navigation

* `layouts/partials/breadcrumbs.html` and `assets/css/common/post-single.css` - semantic marker-free wrapping breadcrumb with decorative chevrons and no duplicate schema
* `tests/test_rendered_seo_metadata.py` and `tests/visual/observatory-a11y.spec.mjs` - visible breadcrumb, schema ownership, computed style, and mobile overflow contracts
* `tests/visual/observatory-analytics.spec.mjs` - real consent acceptance, rejection, reload, withdrawal, cookies, requests, and UI event coverage
* `tests/visual/playwright.config.mjs` and `.github/workflows/ci.yml` - four Chromium desktop/mobile light/dark projects, blocking analytics spec, and local-server Hugo base URL
* `README.md` and `docs/operator-guide.md` - separate localhost static-build and production-build commands

### Content and Workflow Security

* `scripts/manage_topic_hubs.py`, `tests/test_topic_hubs.py`, and `data/taxonomy/topic-candidates.json` - sanitizer boundary, structured YAML, explicit disabled decision, and regenerated candidate evidence
* `scripts/export_observatory_dataset.py` and `tests/test_export_observatory_dataset.py` - safe reporting for external output directories
* `docs/data-observatory-runbook.md` - lifecycle seed procedure and pending cross-origin embed consent policy
* `.github/workflows/security-scanning.yml`, `.github/workflows/crawl-and-publish.yml`, `.github/workflows/sync-squad-labels.yml`, and ten `.github/workflows/squad-*.yml` files - aligned Zizmor scope, least privilege, disabled checkout credential persistence, and explicit push authentication
* `docs/devsecops/zizmor-baseline.md` - pinned version, full workflow scope, and narrow low-severity package disposition

### Acceptance Reconciliation

* `docs/review/data-observatory-relaunch/README.md`, `status-of-record.md`, and `owner-action-register.md` - retained the successful atomic proof and corrected stale Podcaster, sponsor, security, and validation status
* `docs/prds/claracle-data-observatory-relaunch.md` and `docs/brds/claracle-data-observatory-relaunch-brd.md` - recorded protected Podcaster completion and separate sponsor decisions without enabling either rollout flag or closing remaining external gates

## Validation

| Check | Result |
|---|---|
| Ruff lint | Passed |
| Ruff format | 139 files formatted |
| Full pytest | 1,396 passed, 34 subtests passed, 2 expected warnings |
| Rendered SEO, links, and topics | 37 passed with Hugo Extended 0.161.1 |
| Lifecycle rendered fixture | 1 passed |
| Isolated all-generator proof | First pass refreshed candidate registry; second pass byte-identical; all freshness checks passed |
| Hugo production build | 2,669 pages; 12,185 ms in the recorded isolated run |
| Pagefind 1.5.2 | 288 pages indexed; 6,228 ms in the recorded isolated run |
| Internal links | Passed |
| Pipeline tests after local-baseURL correction | 28 passed, 19 subtests passed |
| Checkov | 724 passed, 0 failed, 4 reviewed skips |
| Zizmor 1.27.0 full workflow scope | 0 high, 0 medium, 1 documented low finding |
| Git diff check | Passed |
| Local base URL | Generated HTML contains no `claracle.com` links; internal absolute URLs use `http://127.0.0.1:1313/` |
| Current-main hosted validation | Run `31039618366` passed Python, hydration parity, Hugo, Pagefind, rendered metadata and links, internal links, Playwright, and Lighthouse at `211f0974ce375e427591803cc3f3dfd39e169ead` |
| Atomic publish proof | Run `31040602642` passed normal commit, identical no-op rerun, injected failure with unchanged ref, accepted-tree identity, and hydrated-tree identity |
| Protected Podcaster | Run `30908778884` succeeded for `2026-W32` / publish run `30782430176`; downstream job `podcast-2026-W32-d07bb05dc073` returned `accepted` |

## Open Evidence

* Local Playwright and Lighthouse remain unavailable because the host lacks required browser shared libraries; exact-current-main hosted validation passed instead.
* Three comparable timing reports, median and p95 calculations, and budget-owner approval are pending.
* Production denied and granted analytics observations, GSC processing and numeric baseline values, social and schema debugger conclusions, keyboard and screen-reader review, refreshed visuals, SEC-08 disposition, and production-owner acceptance are pending.
* Both `dynamic_topics.enabled` and `repo_pages.enabled` remain `false`.
