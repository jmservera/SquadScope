<!-- markdownlint-disable-file -->
# Implementation Details: Claracle Data Observatory Relaunch Review Remediation

## Context Reference

Sources: `.copilot-tracking/research/2026-07-30/claracle-data-observatory-relaunch-review-remediation-research.md`, delegated review-remediation research, the 2026-07-30 implementation review, ten RPI validations, and PR #623 hosted check evidence.

## Implementation Phase 1: Lifecycle Safety and Durable Seed

<!-- parallelizable: true -->

### Step 1.1: Fail closed on deletion confirmation

Validate every reviewed `status = "deleted"` override before mutation. Require a valid ISO date that is not in the future, derive retention exclusively from that confirmation date, and reject an operator-supplied earlier deadline. Preserve last-seen data only as provenance.

Files:
* `scripts/observatory_repos.py` - override validation and retention calculation
* `tests/test_observatory_repos.py` - old-last-seen, missing, invalid, future, shortened-deadline, boundary, and non-mutation cases
* `docs/data-observatory-runbook.md` - mandatory confirmation-date procedure

Discrepancy references:
* Addresses review CR-01 and QUAL-CR-01

Success criteria:
* A 2026 confirmation retains through the corresponding date in 2029 regardless of a 2024 last-seen week
* Missing or invalid confirmation fails before page, ledger, taxonomy, or derived writes
* Expiry occurs only when `as_of > retained_until`

Dependencies:
* Existing lifecycle configuration and fixtures

### Step 1.2: Add a ledger-only lifecycle seed mode

Add an explicit `--seed-lifecycle` operation that loads existing observations and prior ledger state, validates parity with current generated repository pages and derived entries, and atomically writes only the lifecycle ledger. Keep normal disabled generation non-mutating and do not query GitHub or invent stable IDs.

Files:
* `scripts/observatory_repos.py` - seed operation, parity checks, atomic ledger write, and count reporting
* `data/derived/observatory/repository-lifecycle.json` - deterministic seeded fallback histories
* `tests/test_observatory_repos.py` - corpus seed, mismatch, fallback-to-ID migration, and byte-stability tests
* `docs/data-observatory-runbook.md` - migration and recovery procedure

Discrepancy references:
* Addresses review MAJ-02 and QUAL-MAJ-03

Success criteria:
* Seed contains 2,242 fallback histories and 263 qualified histories for the frozen current corpus, or fails with reviewed mismatch evidence if the corpus changes
* Existing pages and `repositories.json` remain byte-identical
* A second seed produces no diff, and future stable IDs absorb matching fallback histories without data loss
* `repo_pages.enabled` remains false

Dependencies:
* Step 1.1 validation semantics

### Step 1.3: Validate lifecycle rendering and idempotence

Use a temporary enabled fixture, not production configuration, to generate twice and validate canonical pages, aliases, lifecycle notices, raw tags, curated topics, and internal links through Hugo.

Files:
* `tests/test_observatory_repos.py` - generated-byte and rendered lifecycle contracts
* `tests/test_rendered_weekly_links.py` - applicable repository-link resolution where needed

Success criteria:
* Second fixture generation is byte-identical
* Canonical page, prior-name alias, notices, raw tags, and promoted topic links render and resolve
* Production rollout remains disabled

Dependencies:
* Steps 1.1 and 1.2

## Implementation Phase 2: Exact-Release Podcaster Contract

<!-- parallelizable: true -->

### Step 2.1: Add an opt-in exact article mode

Preserve normal 50,000-character truncation and payload fields. Add an opt-in builder and CLI mode used only by protected release smoke to include complete UTF-8 article content and a hash of those exact bytes.

Files:
* `scripts/podcaster_handoff.py` - opt-in exact-content builder and CLI flag
* `tests/test_podcaster_handoff.py` - short, normal-over-limit, exact-over-limit, Unicode, mismatch, and no-network cases

Discrepancy references:
* Addresses review CR-02 and QUAL-CR-02

Success criteria:
* Default handoff behavior and existing Podcaster contract remain unchanged
* Exact mode includes complete promoted bytes above 50,000 characters and the matching hash
* Any mismatch fails before the downstream network call

Dependencies:
* Coordination with SquadScope-Podcaster body-size acceptance before protected execution

### Step 2.2: Replace or execute workflow verifier logic

Repair the malformed payload verifier and move promotion and payload checks into a checked-in Python entry point or directly testable functions. Make the workflow call that implementation with exact mode instead of relying on unexecuted heredoc strings.

Files:
* `.github/workflows/podcaster-handoff-smoke.yml` - executable verifier and exact-mode invocation
* `scripts/podcaster_handoff.py` or a focused script under `scripts/` - testable release verifier
* `tests/test_pipeline.py` - YAML contract plus execution of verifier logic
* `tests/test_podcaster_handoff.py` - valid and adversarial promotion fixtures

Discrepancy references:
* Addresses review minor workflow-test finding and RPI-008-M01

Success criteria:
* Every embedded Python block compiles, or no embedded Python remains
* Wrong path, week, article hash, source hash, transaction ID, payload content, and missing fields fail before network access
* Workflow passes the opt-in exact-content flag and retains protected environment boundaries

Dependencies:
* Step 2.1

### Step 2.3: Validate the protected exact-release workflow locally

Run focused payload, pipeline, Checkov, and Zizmor checks. Confirm `config/podcast.json` and the default payload shape remain unchanged.

Files:
* `tests/test_pipeline.py` - reusable workflow and caller contracts
* `tests/test_podcaster_handoff.py` - shared-contract regression coverage

Success criteria:
* Focused tests execute verifier behavior rather than source-string presence alone
* Checkov and modified-workflow Zizmor checks pass
* Protected downstream run remains explicitly pending until deployment

Dependencies:
* Steps 2.1 and 2.2

## Implementation Phase 3: Breadcrumb and Browser Quality

<!-- parallelizable: false -->

### Step 3.1: Render a real visible breadcrumb

Retain the repository's `layouts/partials/breadcrumbs.html` accessible navigation and reuse its established `.breadcrumbs` class plus PaperMod chevron visual language. Keep the semantic ordered list, add decorative separators inside list items, and remove the duplicate JSON-LD block from the visible partial.

Files:
* `layouts/partials/breadcrumbs.html` - single visible breadcrumb with ancestor links, decorative chevrons, and terminal current-page text
* `assets/css/common/post-single.css` - marker-free wrapping flex list, item alignment, and mobile-safe label wrapping
* `layouts/partials/seo.html` - retained sole `BreadcrumbList` owner; modify only if hierarchy parity requires it
* `tests/test_rendered_seo_metadata.py` - one visible breadcrumb and exactly one schema breadcrumb
* `tests/visual/observatory-a11y.spec.mjs` - desktop/mobile computed-style and overflow checks

Discrepancy references:
* Addresses the user's 2026-07-30 breadcrumb requirement

Success criteria:
* No browser list numbering is visible
* Exactly one `nav.breadcrumbs` contains one direct `ol`, ordered ancestor links, one terminal non-link `aria-current="page"`, and decorative separators hidden from assistive technology
* `.breadcrumbs ol` has `list-style-type: none`, wraps as flex, and does not overflow on mobile
* Every non-home page emits exactly one valid JSON-LD `BreadcrumbList`
* Existing layout call sites produce no duplicate breadcrumb UI

Dependencies:
* Existing breadcrumb partial and SEO schema contract

### Step 3.2: Make analytics privacy tests end to end and blocking

Add the analytics browser spec to the production CI command. Use actual Cookie Consent interactions and a non-secret test measurement ID; intercept Google endpoints while asserting script, cookie, queue, payload, reload, and withdrawal behavior.

Files:
* `.github/workflows/ci.yml` - blocking analytics spec and test measurement ID
* `tests/visual/observatory-analytics.spec.mjs` - real consent lifecycle and UI-driven events
* `layouts/partials/cookie-consent.html` - modify only if tests expose a wiring defect
* `assets/js/observatory-analytics.js` - modify only for verified bounded-event defects

Discrepancy references:
* Addresses review MAJ-03 and QUAL-MAJ-01

Success criteria:
* Fresh and rejected contexts send no GA script, cookie, request, queued event, or custom telemetry
* Acceptance and reload initialize GA once and preserve bounded payloads
* Withdrawal sets the disable flag, clears seeded analytics cookies, and blocks future events
* Dataset, tool, and chart events use real UI handlers

Dependencies:
* Existing Cookie Consent configuration

### Step 3.3: Repair the browser matrix and rerun production quality

Inspect artifact `8744139176`, classify every failure, and align installed browsers with configured projects. Prefer Chromium-backed desktop/mobile light/dark projects unless Safari compatibility is explicitly required, in which case install and name WebKit separately. Preserve browser-before-Lighthouse sequencing and report upload.

Files:
* `tests/visual/playwright.config.mjs` - deterministic browser/project mapping
* `.github/workflows/ci.yml` - matching pinned browser installation
* `tests/visual/a11y-perf.spec.mjs` - modify only for verified product defects
* `tests/visual/observatory-a11y.spec.mjs` - breadcrumb and verified accessibility fixes
* `scripts/design/lighthouse-gates.mjs` - preserve thresholds and route reports

Discrepancy references:
* Addresses review CR-03

Success criteria:
* All blocking Playwright projects execute rather than skip for missing engines
* Axe, keyboard, focus, responsive, analytics, and breadcrumb checks pass
* Lighthouse executes afterward and every required route meets Performance 0.90, accessibility 0.95, and CLS 0.1
* The rerun URL and report artifact are retained in the changes log

Dependencies:
* Steps 3.1 and 3.2

## Implementation Phase 4: Dynamic Topic and Minor Repository Corrections

<!-- parallelizable: false -->

### Step 4.1: Sanitize candidate titles and generate structured frontmatter

Route candidate titles through the repository sanitizer, reject suspicious boundary and injection content, apply title-specific rules, and replace handwritten frontmatter interpolation with structured YAML generation.

Files:
* `scripts/manage_topic_hubs.py` - sanitizer integration, disabled decision, and safe rendering
* `scripts/discover_topic_candidates.py` - safe evidence boundary where needed
* `scripts/sanitize_repo_content.py` - reuse existing sanitizer without weakening it
* `tests/test_topic_hubs.py` - adversarial title matrix, no-mutation assertions, YAML parsing, and Hugo rendering

Discrepancy references:
* Addresses review CR-05 SEC-01 and MAJ-01

Success criteria:
* Disabled creation emits a stable decision and remains non-mutating
* Quotes, colons, document markers, multiline/control text, Markdown/HTML, boundaries, and injection phrases cannot create artifacts
* Accepted titles parse as YAML and render safely
* Dynamic creation remains disabled

Dependencies:
* Existing sanitizer and candidate registry

### Step 4.2: Correct reusable freshness error reporting

Format stale external output paths without assuming they are under the repository root.

Files:
* `scripts/export_observatory_dataset.py` - safe display path helper
* `tests/test_pipeline.py` or focused dataset tests - external output-dir regression

Discrepancy references:
* Addresses review minor dataset freshness finding

Success criteria:
* External stale outputs report clearly without `ValueError`
* Default workflow freshness behavior remains unchanged

Dependencies:
* None

### Step 4.3: Document embed privacy and update traceability

Record the approved or pending cross-origin embed consent policy in the runbook. Replace descriptive evidence placeholders with exact paths, CI URLs, artifact IDs, owners, and statuses; record resolved dataset drift and current browser evidence.

Files:
* `docs/data-observatory-runbook.md` - cross-origin consent limitation and operator response
* `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md` - exact evidence references
* `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md` - corrected completion state where needed

Discrepancy references:
* Addresses review MAJ-08 and minor documentation/history findings

Success criteria:
* Every finding resolves to an exact repository path, external evidence slot, run URL, or named owner
* Historical failures are dated and followed by current disposition
* No external or security acceptance is overstated

Dependencies:
* Results from Phases 1 through 3

## Implementation Phase 5: Workflow Security Remediation

<!-- parallelizable: true -->

### Step 5.1: Align repository-wide and hosted Zizmor scope

Document the exact workflow include/exclude scope and pinned Zizmor version used locally and in CI. The hosted gate must not silently exclude workflows required by the final repository-wide contract.

Files:
* `.github/workflows/ci.yml` or the owning security workflow - pinned full-scope scan
* Repository Zizmor configuration or documented suppressions - reviewed scope and rationale
* `docs/devsecops/` documentation - ownership and disposition

Discrepancy references:
* Addresses review CR-04

Success criteria:
* Local and hosted scans cover the same intended workflow set with the same version
* Exclusions and suppressions are narrow, reviewed, and documented

Dependencies:
* URL and Squad workflow ownership decision

### Step 5.2: Remove excessive permissions and credential persistence

Scope `contents: write` to jobs that require it and set `persist-credentials: false` on checkout steps that do not push. Preserve explicit authentication only at authorized push points.

Files:
* `.github/workflows/squad-promote.yml` - job-scoped write permission and checkout credentials
* `.github/workflows/squad-ci.yml`
* `.github/workflows/squad-docs.yml`
* `.github/workflows/squad-heartbeat.yml`
* `.github/workflows/squad-insider-release.yml`
* `.github/workflows/squad-issue-assign.yml`
* `.github/workflows/squad-label-enforce.yml`
* `.github/workflows/squad-preview.yml`
* `.github/workflows/squad-release.yml`
* `.github/workflows/squad-triage.yml`
* `.github/workflows/sync-squad-labels.yml`
* `.github/workflows/crawl-and-publish.yml` - disposition or pin ad hoc package install

Success criteria:
* Repository-wide Zizmor has no unreviewed high or medium findings
* Push-capable jobs retain only the minimum required permission and authentication
* Workflow behavior tests and Checkov pass

Dependencies:
* Step 5.1 ownership and scope decision

## Implementation Phase 6: Runtime and Determinism Evidence

<!-- parallelizable: false -->

### Step 6.1: Prove atomic publish behavior

Run a controlled normal publication, an identical rerun, and an injected generator failure. Retain run URLs, publish SHAs, generated-tree comparison, and proof that failure leaves `publish` unchanged. Deploy the accepted publish SHA and verify hydrated path identity.

Files:
* `.github/workflows/crawl-and-publish.yml` - temporary test hook only if a safe existing dispatch cannot exercise failure
* `.github/workflows/deploy-site.yml` - evidence consumer, not contract redesign
* `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md` - immutable runtime evidence

Success criteria:
* One lease-protected commit contains all generated changes
* Identical rerun creates no commit
* Injected failure creates no branch update
* Deployment tree matches the accepted publish commit

Dependencies:
* Repository correction phases complete

### Step 6.2: Prove all-generator idempotence in isolation

Create a clean isolated worktree at the candidate revision, run every generator twice in workflow order, and retain first-run changes plus a clean second-run diff and environment manifest.

Files:
* `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md` - commit, versions, commands, and diff evidence
* Generated artifacts only when the first run proves checked-in state is stale

Success criteria:
* Second run produces no generated diff
* Both rollout flags stay false in production configuration
* Lifecycle seed, topics, repositories, data, datasets, and tool exports are stable together

Dependencies:
* Phases 1 through 5

### Step 6.3: Collect timing and protected Podcaster evidence

Retain three comparable successful Production site timing artifacts, calculate Hugo and Pagefind median and p95, obtain budget approval, and execute the protected exact-release Podcaster smoke for the designated promotion record.

Files:
* `docs/design/data-observatory-model.md` - measured baseline and approved budgets
* `docs/review/data-observatory-relaunch/README.md` - evidence links and status
* `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md` - run URLs and promotion identity

Success criteria:
* Three comparable timing reports identify revision and page volume
* Median, p95, budgets, and approver are explicit before enforcement
* Protected Podcaster run succeeds with exact bytes and retained response evidence

Dependencies:
* Passing Production site and deploy; protected environment access

## Implementation Phase 7: Security and External Acceptance

<!-- parallelizable: false -->

### Step 7.1: Close security findings and sign-off

Resolve SEC-01 through SEC-06 with owners and dispositions, including candidate sanitization, embed policy, lifecycle evidence, publication controls, dataset exposure, and secret scope. Obtain dated Hermes, URL, and owner sign-off.

Files:
* `docs/review/data-observatory-relaunch/security-review.md` - final findings, evidence, and sign-off
* Relevant tests and run URLs from prior phases

Success criteria:
* No open high-severity finding remains
* Every finding has a disposition and evidence
* NFR-004 is accepted only after all named sign-offs

Dependencies:
* Phases 1 through 6

### Step 7.2: Gather platform and accessibility evidence

Execute GA4 denied/granted/Realtime checks, GSC verification and sitemap submission, social and schema debuggers, production sitemap/feed responses, and automated, keyboard, and screen-reader accessibility review.

Files:
* `docs/growth/ga4-gsc-baseline-2026-07-29.md` - dated values and actors
* `docs/review/data-observatory-relaunch/README.md` - evidence index

Success criteria:
* Every external claim has a dated observation, actor, revision, and retained link
* Pending or failed checks remain explicit

Dependencies:
* Designated deployed revision and access to external platforms

### Step 7.3: Replace visuals and obtain rollout approvals

Capture populated, unobscured desktop/mobile, light/dark, and interaction states with revision and viewport metadata. Reconcile PRD and BRD only to verified status and obtain separate sponsor approval for each rollout flag.

Files:
* `docs/review/data-observatory-relaunch/screenshots/` - accepted visual matrix
* `docs/review/data-observatory-relaunch/README.md` - visual evidence and approval references
* `docs/prds/claracle-data-observatory-relaunch.md` - verified delivery and rollout state
* `docs/brds/claracle-data-observatory-relaunch-brd.md` - dated sponsor decisions
* `config/observatory.toml` - flag changes only in separately approved rollout commits

Success criteria:
* Breadcrumbs appear as real marker-free chevron navigation in accepted desktop and mobile captures
* Topic hubs are populated and feature views are unobscured
* Dynamic topic and repository-page approvals are separate and dated
* This remediation PR does not enable either flag without approval

Dependencies:
* All automated gates and external evidence complete

## Implementation Phase 8: Final Validation and Re-Review

<!-- parallelizable: false -->

### Step 8.1: Run full repository validation

Run Ruff lint and format, full pytest, Hugo, Pagefind, internal links, complete Playwright including analytics and breadcrumb checks, Lighthouse, Checkov, and full-scope Zizmor with pinned versions.

Validation commands:
* `python3 -m ruff check .`
* `python3 -m ruff format --check .`
* `python3 -m pytest -q tests/`
* `hugo --minify`
* `npx "pagefind@1.5.2" --site public/`
* `python3 scripts/check_internal_links.py public --base-url "https://claracle.com/"`
* `npx playwright test --config tests/visual/playwright.config.mjs`
* `node scripts/design/lighthouse-gates.mjs --base http://127.0.0.1:8080`
* `checkov --directory . --framework github_actions dockerfile secrets --skip-path node_modules --skip-path .venv --compact --soft-fail`
* `zizmor .github/workflows/`

### Step 8.2: Repair and rerun validation failures

Classify every failure against the remediation scope. Apply isolated corrections for implementation-caused lint, format, test, build, browser, performance, or security failures, rerun the failed check, and then rerun the complete validation suite. Do not weaken assertions, thresholds, scan scope, or workflow gates to obtain a pass.

Success criteria:
* Every implementation-caused failure is corrected and passes both its focused check and the complete suite
* Every unrelated pre-existing failure is recorded with command, output artifact, affected owner, and evidence that the remediation did not cause it
* Validation does not advance to re-review while an unresolved implementation-caused failure remains

Dependencies:
* Step 8.1

### Step 8.3: Revalidate every review finding

Run RPI validation for all affected phases, update the review and changes logs with exact evidence, and require zero unresolved critical or major repository findings before merge recommendation.

Files:
* `.copilot-tracking/reviews/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-review.md` - re-review disposition
* `.copilot-tracking/reviews/rpi/` - refreshed phase validation
* `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md` - final traceability

Success criteria:
* CR-01 through CR-07 and MAJ-01 through MAJ-08 are resolved or remain explicitly external with accepted evidence checkpoints
* Breadcrumb requirement passes source, rendered, computed-style, accessibility, mobile, and visual checks
* PR checks are green and rollout flags remain off until separately approved

Dependencies:
* Phases 1 through 7

### Step 8.4: Report blocking issues

When a failed check or review finding requires further research, external access, cross-repository change, or substantial work beyond an isolated correction, stop the merge recommendation and record the blocker with severity, owner, evidence, affected acceptance criterion, and required next action. External checkpoints remain open rather than being represented as passed.

Success criteria:
* No critical or major blocker is hidden by a green subset of checks
* The final review distinguishes resolved repository findings from open external acceptance checkpoints
* Rollout flags remain disabled while any required blocker or checkpoint is open

Dependencies:
* Steps 8.2 and 8.3
