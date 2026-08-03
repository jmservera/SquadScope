<!-- markdownlint-disable-file -->
# Claracle Protected Acceptance Gates Research

## Research Scope

* Assess which security, protected Podcaster, atomic publish, and final validation acceptance gates can be evidenced on current `main` as of 2026-08-03.
* Inspect workflows, tests, existing review records, the owner-action register, security review, and controlling plans.
* Determine whether merged changes since 2026-08-02 satisfy evidence that was previously pending.
* Identify exact executable local and CI checks.
* Preserve approval and execution boundaries requiring Hermes, URL, a repository administrator, a Podcaster maintainer, or the sponsor.

## Status

Complete. Research performed on current `main` at
`4b7c5cf506b2e8b73350ff94ce80669c93810e66` on 2026-08-03.

## Evidence Baseline

The controlling records still keep the four requested acceptance areas open:

* `.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md` keeps Steps 6.1, 6.3, 7.1, 8.1, and 8.3 unchecked.
* `docs/review/data-observatory-relaunch/status-of-record.md` classifies atomic publish as Partial and security sign-off, the real protected Podcaster run, and sponsor approval as Pending.
* `docs/review/data-observatory-relaunch/owner-action-register.md` defines the named actors and completion evidence that repository automation cannot supply.
* `docs/review/data-observatory-relaunch/security-review.md` says NFR-004 is not accepted and all Hermes, URL, and jmservera sign-off rows are Pending.

Current `main` has substantial executable implementation evidence. It does not have
the human dispositions, protected environment policy, controlled atomic runtime
matrix, or one-revision final acceptance bundle required to close the gates.

## Gate Assessment

### Security

Status: implementation evidence available; NFR-004 acceptance remains open.

Current repository evidence supports review of SEC-01 through SEC-05:

* SEC-01 candidate-title sanitization and structured serialization are tested.
* SEC-02 official embed snippets use `no-referrer`, and browser tests exercise frame-local, default-off consent behavior.
* SEC-03 exact CSV, metadata, nested-object, and source-path allowlists are enforced and tested.
* SEC-04 rename, archive, confirmed deletion, retention, expiry, and fail-closed lifecycle behavior are tested.
* SEC-05 sanitization, prompt fencing, canary detection, output validation, prompt lint, and red-team controls have executable coverage.
* SEC-06 still depends on production analytics observations and protected Podcaster secret-scope review.

The focused local security/lifecycle command passed with 147 tests and 5
Hugo-dependent skips. Current-main Actions are also green for CI run
[30839710156](https://github.com/jmservera/SquadScope/actions/runs/30839710156),
Security Scanning run
[30839709471](https://github.com/jmservera/SquadScope/actions/runs/30839709471),
CodeQL run
[30839708289](https://github.com/jmservera/SquadScope/actions/runs/30839708289),
and Checkov run
[30839709417](https://github.com/jmservera/SquadScope/actions/runs/30839709417).

These results can be attached to finding dispositions now. They cannot substitute
for Hermes approving, rejecting, or accepting risk for SEC-01 through SEC-06, URL
reviewing protected workflow and secret scope, or jmservera recording the production-owner conclusion.

### Protected Podcaster

Status: contract and split runtime evidence available; protected real-run acceptance remains open.

* Run [30202586031](https://github.com/jmservera/SquadScope/actions/runs/30202586031) proves a real downstream request was accepted for 2026-W30.
* Run [30721575540](https://github.com/jmservera/SquadScope/actions/runs/30721575540) proves an environment-bound dry run.
* `.github/workflows/podcaster-handoff-smoke.yml` declares `environment: podcaster-release-smoke`, but it always passes `--podcaster-dry-run`.
* `.github/workflows/trigger-podcast.yml` and the real post-merge handoff in `.github/workflows/sync-publish-to-main.yml` do not declare an environment.
* The live GitHub environment query on 2026-08-03 shows `podcaster-release-smoke` has no protection rules and no deployment branch policy.
* Local workflow and handoff contract tests passed: 84 tests and 26 subtests.

No merged change since 2026-08-02 binds real generation to a protected environment
or adds protection policy. No current run combines real generation, environment
approval, exact retained promotion identity, and downstream success.

### Atomic Publish

Status: implementation and restore/hydration evidence available; atomic acceptance remains Partial.

Current code and tests evidence single-writer workflow structure, generated-path
coverage, drift checks, immutable backup/restore behavior, rerun-mode validation,
restore transaction preservation, and publish-hydration reference validation. The
focused publication suite passed 24 tests. Scheduled crawl-and-publish run
[30782430176](https://github.com/jmservera/SquadScope/actions/runs/30782430176)
also completed successfully after the August 2 reconciliation.

The controlling Step 6.1 requires one retained matrix containing:

1. A controlled normal publication and resulting `publish` SHA.
2. An identical rerun that creates no commit.
3. An injected generator failure that leaves `publish` unchanged.
4. A generated-tree comparison.
5. Deployment hydration matching the accepted `publish` commit.

Repository and tracking searches found no retained matrix or newly recorded
identical-rerun, injected-failure, unchanged-branch, or accepted-SHA tree comparison.
The successful scheduled run is useful normal-operation evidence but does not close
the controlled matrix.

### Final Validation

Status: a strong current-main automated subset is evidenced; final acceptance remains open.

Local validation on `4b7c5cf` produced:

* Ruff lint: passed
* Ruff format check: passed, 144 files formatted
* Full pytest: 1,401 passed, 19 skipped, 2 warnings, and 34 subtests passed
* Focused security/lifecycle: 147 passed and 5 skipped
* Focused publication/hydration: 24 passed
* Focused workflow/Podcaster: 84 passed and 26 subtests passed

Current-main CI run
[30839710156](https://github.com/jmservera/SquadScope/actions/runs/30839710156)
passed all three jobs: Python, Production site, and Publish hydration parity. The
Production site job builds with Hugo 0.161.1 and Pagefind 1.5.2, runs rendered SEO
and link contracts, the standalone internal-link checker, Playwright axe/responsive/analytics
tests, and Lighthouse gates. Lint, deploy, Bandit/Zizmor, CodeQL, and Checkov also
completed successfully for the same SHA.

This is enough to evidence the current automated baseline and the newly added
NFR-011 hydration parity guard. It is not the Step 8 final acceptance bundle because
atomic Step 6.1, protected Podcaster Step 6.3, security Step 7.1, external acceptance,
and finding-by-finding revalidation remain open. The required immutable evidence is
not yet tied to one fully accepted revision.

## Executable Checks

### Local implementation checks

```bash
uv run --no-sync pytest -q \
	tests/test_sanitize_repo_content.py \
	tests/test_prompt_injection_redteam.py \
	tests/test_defense_chain_e2e.py \
	tests/test_topic_hubs.py \
	tests/test_observatory_repos.py \
	tests/test_observatory_embeds.py \
	tests/test_export_observatory_dataset.py
```

```bash
uv run --no-sync pytest -q \
	tests/test_publish_safety.py \
	tests/test_rerun_modes.py \
	tests/test_publish_hydration.py
```

```bash
uv run --no-sync pytest -q \
	tests/test_pipeline.py \
	tests/test_podcaster_handoff.py
```

```bash
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync pytest -q tests/
```

### Full rendered validation

The controlling plans specify these checks. Hugo and a system Chromium browser are
not installed on the current host, so current-main CI is the executable evidence path
for the rendered checks.

```bash
hugo --minify
npx "pagefind@1.5.2" --site public/
python scripts/check_internal_links.py public --base-url "https://claracle.com/"
python scripts/serve_static.py --directory public --bind 127.0.0.1 --port 1313
```

With the server running:

```bash
BASE_URL=http://127.0.0.1:1313 \
	npx --no-install playwright test \
	--config tests/visual/playwright.config.mjs \
	tests/visual/a11y-perf.spec.mjs \
	tests/visual/observatory-a11y.spec.mjs \
	tests/visual/observatory-analytics.spec.mjs
node scripts/design/lighthouse-gates.mjs --base http://127.0.0.1:1313
```

### Security workflow checks

```bash
checkov --directory . --framework github_actions dockerfile secrets \
	--skip-path node_modules --skip-path .venv --compact --soft-fail
zizmor .github/workflows/
```

CI additionally runs dependency audit, Bandit, CodeQL, blocking Zizmor at medium
severity, Checkov, Ruff, the full Python job, Production site, and Publish hydration
parity. Opening or updating a PR to `main`, or pushing to `main`, executes these
workflows according to their triggers.

### Publish hydration parity

Local unit evidence:

```bash
uv run --no-sync pytest -q tests/test_publish_hydration.py
```

The CI job performs the authoritative integration sequence: fetch `origin/publish`,
hydrate every path returned by `python3 -m scripts.publish_hydration paths`, then run:

```bash
python3 -m scripts.publish_hydration check
```

### Protected or side-effecting operations

The Podcaster workflows and controlled atomic publication are not read-only checks.
Do not dispatch them as validation probes without the approvals listed below. A real
Podcaster dispatch can create downstream work, and an atomic proof run writes the
`publish` branch.

## Authority Boundaries

| Boundary | Required actor | Non-delegable action |
| --- | --- | --- |
| SEC-01 through SEC-06 disposition and NFR-004 conclusion | Hermes | Approve, reject, or record accepted-risk rationale for every finding |
| Workflow security and secret scope | URL | Review the actual protected real-generation workflow and masked environment secret scope |
| GitHub environment policy | Repository administrator | Configure required reviewers and deployment branch policy for real generation |
| Duplicate safety and downstream acceptance | Podcaster maintainer | Confirm idempotency or authorize one exact eligible week and manifest; verify downstream result |
| Protected execution | Environment approver | Approve the real-generation deployment after policy is active |
| Production-owner and rollout decisions | Sponsor (jmservera) | Record production acceptance and separate dated decisions for `dynamic_topic_creation` and `repo_pages` |

Repository tests, green Actions, and this research artifact do not exercise any of
these approval authorities. Both rollout flags must remain disabled until separately approved.

## Post-2026-08-02 Changes

| Merge | Acceptance effect |
| --- | --- |
| `2fdcb096` / #647 | Added and reconciled owner/security/readiness records plus SEC-02/03/05 implementation evidence, but intentionally left protected and human gates open |
| `a405ee1b` / #649 | Published W32 data to `main`; useful normal-operation evidence, not the controlled atomic matrix |
| `e711e283` / #653 | Resynchronized generated W32 artifacts and tests; no protected approval or atomic proof was added |
| `caae7eac` / #650 | Corrected review provenance and kept atomic and protected Podcaster gates open |
| `5367ab49` / #654 | Added theme-submodule retry resilience to CI/deploy; no acceptance gate closed |
| `4b7c5cf5` / #651 | Added `scripts/publish_hydration.py`, tests, and the successful Publish hydration parity CI job; this satisfies the previously pending NFR-011 deploy/publish hydration-parity evidence, but not atomic Step 6.1 |

No post-August-2 merge closes NFR-004 security acceptance, the protected real
Podcaster run, atomic Step 6.1, or the complete final-validation/re-review gate.

## Follow-On Questions

Recommended next evidence work not completed in this research session:

* [ ] Have Hermes disposition SEC-01 through SEC-06 against the current implementation evidence.
* [ ] Have URL review the proposed real-generation environment binding and secret scope.
* [ ] Have a repository administrator configure required reviewers and deployment branch policy.
* [ ] Confirm Podcaster idempotency, or obtain maintainer authorization for one exact week and manifest.
* [ ] Execute and retain the controlled atomic normal/rerun/failure/hydration matrix.
* [ ] Execute one approved real Podcaster run after environment protection and workflow binding.
* [ ] Assemble final automated, external, reviewer, and sponsor evidence against one revision, then rerun finding-by-finding review validation.

Clarifying questions requiring owner input:

* Which named reviewers and branch policy should protect real Podcaster generation?
* Does SquadScope-Podcaster guarantee idempotency for a repeated week or manifest, and where is that contract retained?
* Which exact revision will Hermes, URL, the Podcaster maintainer, and the sponsor use for final acceptance?

## Sources

### Repository sources

* `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md`
* `.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md`
* `.copilot-tracking/details/2026-07-30/claracle-data-observatory-relaunch-review-remediation-details.md`
* `.copilot-tracking/reviews/2026-08-02/claracle-relaunch-readiness-reconciliation-plan-review.md`
* `.copilot-tracking/research/subagents/2026-08-02/claracle-acceptance-gates-followup-research.md`
* `docs/review/data-observatory-relaunch/status-of-record.md`
* `docs/review/data-observatory-relaunch/owner-action-register.md`
* `docs/review/data-observatory-relaunch/security-review.md`
* `.github/workflows/ci.yml`
* `.github/workflows/crawl-and-publish.yml`
* `.github/workflows/podcaster-handoff-smoke.yml`
* `.github/workflows/trigger-podcast.yml`
* `.github/workflows/sync-publish-to-main.yml`
* `.github/workflows/lint.yml`
* `.github/workflows/security-scanning.yml`
* `scripts/publish_hydration.py`
* `tests/test_publish_hydration.py`
* `tests/test_publish_safety.py`
* `tests/test_pipeline.py`
* `tests/test_podcaster_handoff.py`

### Live evidence

* [Current-main CI](https://github.com/jmservera/SquadScope/actions/runs/30839710156)
* [Current-main deploy](https://github.com/jmservera/SquadScope/actions/runs/30839709626)
* [Current-main Security Scanning](https://github.com/jmservera/SquadScope/actions/runs/30839709471)
* [Current-main CodeQL](https://github.com/jmservera/SquadScope/actions/runs/30839708289)
* [Current-main Checkov](https://github.com/jmservera/SquadScope/actions/runs/30839709417)
* [W32 crawl and publish](https://github.com/jmservera/SquadScope/actions/runs/30782430176)
* [Environment-bound dry-run Podcaster smoke](https://github.com/jmservera/SquadScope/actions/runs/30721575540)
* [Real accepted Podcaster run](https://github.com/jmservera/SquadScope/actions/runs/30202586031)
