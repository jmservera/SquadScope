<!-- markdownlint-disable-file -->
# Claracle Acceptance Gates Follow-Up Research

## Research Scope

Assess current evidence and executable work for:

* NFR-004 security sign-off
* NFR-005 accessibility
* A real protected Podcaster downstream run
* Refreshed visual acceptance
* Lighthouse issue #626
* UX issue #622
* Sponsor approval

Separate checks that can run locally or through GitHub now from actions that require protected environments or human approval. Inspect the relaunch review package, relevant tests, workflows, scripts, screenshots, PRD, BRD, and current repository patterns.

## Working Hypothesis

The status-of-record identifies the correct pending gates, but most acceptance evidence remains either stale, test-level only, or dependent on protected GitHub environments and named human approvers. Nearby scripts and workflows may provide executable checks without satisfying the final approval gates.

## Evidence Inventory

| Surface | Current evidence | What it proves | Boundary |
| --- | --- | --- | --- |
| Acceptance status | docs/review/data-observatory-relaunch/README.md and status-of-record.md both say release acceptance is pending | The seven requested gates are launch-readiness scope and both rollout flags must remain disabled | These records do not supply the missing approvals |
| Product requirements | docs/prds/claracle-data-observatory-relaunch.md v1.3 and docs/brds/claracle-data-observatory-relaunch-brd.md v1.2 | NFR-004 is Must, NFR-005 is Should, NFR-001 requires Lighthouse Performance >= 90, and each rollout flag needs separate sponsor approval | PRD and BRD record intent, not execution |
| Automated browser quality | .github/workflows/ci.yml production-site job | CI installs pinned Playwright 1.54.2, axe-playwright 4.10.2, and Lighthouse 12.8.2; runs responsive, axe, analytics, and Lighthouse checks; uploads reports for 30 days | The server is a local production build, not the public production origin |
| Current GitHub CI | CI run 30723119836 succeeded for the reconciliation branch; run 30742507113 was in progress when checked on 2026-08-02 | The branch has a recent complete green baseline and a current GitHub check is available | The current in-progress run must finish before its revision is cited as green |
| Lighthouse implementation | scripts/design/lighthouse-gates.mjs | Nine routes run mobile Lighthouse three times; medians must meet performance 0.90, accessibility 0.95, best practices 0.95, and CLS <= 0.1 | This does not complete the five open improvements in issue #626 |
| Accessibility implementation | tests/visual/observatory-a11y.spec.mjs and tests/visual/a11y-perf.spec.mjs | Serious and critical WCAG 2.1 A/AA axe findings fail; keyboard focus, modal focus handling, chart alternatives, overflow, and 44 px targets receive automated coverage | No retained production-origin audit, manual keyboard record, or screen-reader findings exist |
| Protected dry-run smoke | Deploy run 30721575540, job 91426194097 | The post-deploy reusable smoke succeeded on 2026-08-01 using exact retained promotion evidence and `--podcaster-dry-run` | It did not create a real downstream episode |
| Real downstream run | Trigger Podcast run 30202586031 | Week 2026-W30 used manifest run 29744859230 and Podcaster returned `status=accepted` with a retained job ID on 2026-07-26 | .github/workflows/trigger-podcast.yml declares no GitHub environment |
| GitHub environments | GitHub API response on 2026-08-02 | `podcaster-release-smoke` exists, but has no protection rules or deployment branch policy | A named environment is not evidence of protected approval controls |
| Visual evidence | Ten PNGs under docs/review/data-observatory-relaunch/screenshots plus its README | Historical desktop captures show the intended surfaces and the defects cited by issue #622 | They lack revision, viewport, theme, interaction metadata, mobile/dark variants, populated topic membership, and unobscured states |
| Security review | docs/review/data-observatory-relaunch/security-review.md | SEC-01 through SEC-06 and three signatories define the acceptance boundary | The review is stale against some current controls and all sign-off rows remain Pending |

## Gate Findings

### NFR-004 Security Sign-Off

Status: blocked on review reconciliation and named human dispositions, not on a single test command.

* Hermes has not dispositioned SEC-01 through SEC-06; URL and jmservera sign-off rows are also Pending.
* SEC-01 is stale as written. scripts/manage_topic_hubs.py now applies `sanitize_text`, rejects line breaks, boundary markers, HTML, Markdown, control characters, and injection phrases. tests/test_topic_hubs.py includes adversarial cases for those payloads.
* SEC-02 remains substantively open. layouts/partials/visuals/observatory-chart.html emits an iframe snippet without `referrerpolicy`, and standalone embeds can load the common consent-gated analytics adapter. A privacy decision and test are still required.
* SEC-03 is partially implemented. scripts/export_observatory_dataset.py centralizes a fixed `CSV_COLUMNS` list and emits a public-exposure statement, while the ADR requires review for new fields. There is no separately approved field policy or automated assertion that the published fields equal that policy.
* SEC-04 has strong executable evidence in tests/test_observatory_repos.py for rename, archive, confirmed deletion, retention, and expiry. Hermes still must accept the operator-override policy.
* SEC-05 is an explicit accepted-risk decision for phrase-based semantic false negatives. Tests can verify defense in depth, but only Hermes can record the risk disposition.
* SEC-06 requires production analytics evidence and protected Podcaster secret-scope evidence. Repository tests cannot close it.

### NFR-005 Accessibility

Status: automated implementation exists; acceptance evidence is incomplete.

* CI already runs axe against topic, data, repository, chart, and tool routes and rejects serious or critical WCAG 2.1 A/AA violations.
* Existing Playwright tests cover labels, visible focus, keyboard operation, consent-dialog focus trapping and restoration, chart text alternatives, responsive overflow, and touch target size.
* The required acceptance record does not exist. It must identify revision, public production URLs, browser and assistive technology, automated results, manual keyboard findings, screen-reader findings, reviewer, date, and dispositions.

### Real Protected Podcaster Downstream Run

Status: real and environment-bound evidence each exist separately; the required combination does not.

* Run 30202586031 proves a real accepted downstream request for week 2026-W30.
* Run 30721575540 proves a successful post-deploy dry-run through the `podcaster-release-smoke` environment.
* The real workflow and the post-merge path in .github/workflows/sync-publish-to-main.yml do not bind to an environment. The named smoke environment currently has no protection rules. Therefore no current run proves real generation after protected-environment approval.

### Refreshed Visual Acceptance

Status: blocked on final UI/data state and human visual review.

* The historical set contains only ten PNGs and records a generated date of 2026-05-25 in the rendered footer.
* 02-topics-index.png shows no topic hubs with issue matches; 03-topic-hub-mcp.png shows zero recent weekly issues; 08-star-velocity-tool.png shows ambiguous rounded bars; all three are obscured by the consent banner.
* tests/visual/visual.spec.mjs covers only home, about, weekly, monthly, yearly, and cover-card baselines. It does not automate the relaunch capture matrix in docs/review/data-observatory-relaunch/screenshots/README.md.
* Acceptance requires a replacement matrix with revision, date, browser, viewport, theme, consent state, interaction state, source week, populated content, and reviewer conclusion.

### Lighthouse Issue #626

Status: open on GitHub with no assignee and five independently shippable items.

* Extend page-scoped CSS splitting to search, about, methodology, and privacy.
* Add Brotli negotiation to scripts/serve_static.py.
* Document the median-of-three and compressed-server methodology in docs/qa-gates.md.
* Reserve chart space to reduce the data-page CLS margin from its cited approximately 0.040 value.
* Parallelize per-page Lighthouse execution to reduce the roughly ten-minute production-site job.
* Acceptance explicitly forbids lowering the current thresholds.

### UX Issue #622

Status: open on GitHub with no assignee; the issue calls the work non-blocking polish, while the relaunch status-of-record includes it in the readiness register.

* Determine whether Star Velocity Explorer bars are intentionally normalized per row or incorrectly bound. Current screenshots are not sufficient to decide.
* Verify topic index aggregation against a production-representative dataset. Historical captures show the mismatch, but current weekly files W21 through W31 contain canonical `topics` frontmatter, including MCP Ecosystem in W21 and W26. This is likely stale visual evidence unless a fresh Hugo build still renders zero matches.
* Verify mobile consent-banner placement. Existing automated modal tests cover focus behavior but not visual content occlusion.

### Sponsor Approval

Status: human-only and absent.

* Repository search found no dated approval artifact.
* BRD approval of the business requirements is not rollout approval.
* jmservera must approve or reject `dynamic_topic_creation` and `repo_pages` separately, identify the reviewed evidence and revision, and date the decision. Both flags must remain disabled until then.

## Executable Checks Available Now

### Local Without Protected Access

* Pure-Python security controls, topic lifecycle, repository lifecycle, embed contracts, and trend-tool behavior run through the existing `.venv` with `uv run --no-sync`.
* The focused UX/lifecycle run completed with 42 passed and 6 skipped. Every skip required Hugo, which is not installed on this host.
* The focused sanitization and defense-chain run completed with 102 passed.
* Node packages match CI: Playwright 1.54.2, axe-playwright 4.10.2, and Lighthouse 12.8.2.
* Local Playwright execution is blocked before page navigation because the host lacks `libnspr4` and `libnss3`. Installing Playwright system dependencies requires elevated access. Lighthouse is subject to the same Chromium host dependency.
* The checked-in `public/` tree can be served with scripts/serve_static.py, but it is not sufficient acceptance evidence unless it is rebuilt from and tied to the tested source revision.

### GitHub Without Protected Secrets Or Human Approval

* Opening or updating a PR to `main` runs .github/workflows/ci.yml. It builds Hugo, runs rendered contracts, axe, responsive checks, analytics tests, and Lighthouse, and retains production-quality reports for 30 days.
* CI run 30742507113 had passed Python, rendered contracts, internal links, and axe/responsive gates when inspected. Lighthouse was still running. Completed run 30723119836 is the latest full green run for the same reconciliation branch lineage.
* Issues #626 and #622 can be researched, assigned, decomposed, and implemented through normal PRs without protected environment access.
* The dry-run smoke workflow is manually dispatchable, but it requires exact retained publish evidence and repository environment secrets.

### GitHub Actions That Cause External Effects

* .github/workflows/trigger-podcast.yml can dispatch a real generation request for an eligible week and publish run. It is not a read-only validation command.
* No idempotency or duplicate-suppression key is visible in scripts/podcaster_handoff.py. A rerun must be approved by the Podcaster maintainer or target a deliberately authorized episode.
* .github/workflows/deploy-site.yml can redeploy and then run the dry-run smoke. It changes production deployment state and is not needed merely to prove local code quality.

## Protected Or Human Actions

| Action | Required actor or access | Why it cannot be closed locally |
| --- | --- | --- |
| Protect the Podcaster environment | Repository administrator | `podcaster-release-smoke` currently has no protection rules or branch policy |
| Bind real generation to the protected environment | Workflow change reviewed by URL and Hermes | Current real and post-merge jobs declare no environment |
| Authorize a real downstream target week | Podcaster maintainer | A duplicate episode may be created; this repository has no visible idempotency guard |
| Execute and verify the real protected run | Environment approver and Podcaster maintainer | Requires secret-bearing environment and downstream access |
| Manual accessibility review | Fry plus an accessibility reviewer with production browser and assistive technology | Automated axe and keyboard tests do not provide screen-reader findings |
| Visual acceptance | Amy or named visual reviewer | Screenshot generation does not equal a human acceptance conclusion |
| NFR-004 disposition | Hermes, URL, and jmservera | SEC-02, SEC-05, SEC-06 and policy acceptance require threat, workflow, and production-owner judgment |
| Sponsor rollout decision | jmservera | Approval authority is explicitly human and must address each flag separately |

## Exact Evidence Gaps

1. NFR-004 has no dated Hermes disposition for SEC-01 through SEC-06 and no completed URL or sponsor sign-off row. The review also does not acknowledge that SEC-01 sanitization and SEC-04 lifecycle fixtures now exist.
2. SEC-02 lacks a chosen embed privacy model, implementation evidence, and a test for referrer and cross-origin consent behavior.
3. SEC-03 lacks an approved field-level publication policy and an automated comparison between that policy and exported fields. `CSV_COLUMNS` plus a self-authored PASS string is useful implementation evidence but not independent privacy approval.
4. SEC-05 lacks an accepted-risk rationale for semantic prompt-injection false negatives.
5. SEC-06 lacks dated production analytics network/cookie observations and environment-scoped Podcaster secret review.
6. NFR-005 lacks a retained accessibility review record with public URLs, revision, browser, assistive technology, axe results, full keyboard findings, screen-reader findings, reviewer, date, and dispositions.
7. No Actions run combines real Podcaster generation with a protected GitHub environment. Existing evidence is split between real unbound run 30202586031 and environment-bound dry-run 30721575540.
8. The environment named `podcaster-release-smoke` has zero protection rules. Its name alone does not satisfy protected execution.
9. The visual set lacks current revision metadata, mobile and dark captures, consent-resolved feature states, populated topic membership, complete interaction states, empty/error states, and a dated reviewer conclusion.
10. Issue #626 remains open with all five checklist items unchecked. No issue comment or linked PR records partial completion.
11. Issue #622 remains open. Fresh source data suggests the topic aggregation screenshot is stale, but no current rendered capture proves it; bar semantics and mobile consent occlusion remain unclassified.
12. No dated sponsor artifact approves or rejects `dynamic_topic_creation` and `repo_pages` separately. Both are correctly still `enabled = false` in config/observatory.toml.
13. The status-of-record calls #622 a readiness gate while the issue body calls it non-blocking polish and says the epic is accepted. A human release owner must resolve which statement controls launch acceptance.

## Suggested Implementation Sequence

1. Let CI run 30742507113 finish and retain its production-quality artifact URLs. Do not call the revision fully green until Lighthouse completes.
2. Reconcile the security review with current code. Mark SEC-01 implementation-ready for Hermes verification, attach the adversarial test result, attach SEC-04 lifecycle test evidence, and replace stale statements without marking NFR-004 accepted.
3. Resolve SEC-02 and SEC-03 through small independent changes: choose the embed privacy model first, then codify and test the public export field policy. Preserve disabled rollout flags.
4. Resolve issue #622’s factual questions before visual recapture. Rebuild with current W21-W31 frontmatter, confirm topic counts, document Star Velocity normalization semantics, and test consent placement at mobile viewports.
5. Implement issue #626 before final screenshots because CSS splitting and CLS reservation can change layout. Land documentation and Brotli support independently; preserve every threshold. Parallelize Lighthouse only after deterministic per-page artifact naming and failure aggregation are designed.
6. Run the complete GitHub production-site job and review the uploaded axe, responsive, Lighthouse, and Playwright reports. Then perform the manual keyboard and screen-reader review against the final production revision.
7. Capture the complete visual matrix only after #622 and layout-affecting #626 work is final. Record metadata beside every image and obtain Amy's dated acceptance conclusion.
8. Create a protected environment for real Podcaster generation, or add real mode to a separately named protected environment. Require approved branches and the intended reviewer. Bind the real job to it and have URL/Hermes review secret scope.
9. With Podcaster-maintainer authorization, run one real eligible week through the protected environment. Retain the Actions URL, week, manifest run ID, article SHA-256, downstream job ID, final downstream conclusion, approver, and date without recording secret values.
10. Have Hermes, URL, and jmservera complete the security sign-off table after external evidence is attached.
11. Resolve whether #622 is blocking, then have jmservera issue a dated sponsor decision for each rollout flag. Enabling either flag is a separate product change after approval, not part of the approval artifact itself.

## Blockers

* Hugo is absent locally, so rendered source validation cannot run on this host without installing the pinned binary.
* Playwright's Node packages are installed, but required Chromium host libraries are absent and need elevated package installation. GitHub CI is the available executable browser path now.
* The real Podcaster workflow is not environment-bound, and the existing named environment has no protection rules.
* A protected real rerun can create duplicate downstream work; Podcaster maintainer authorization is required because no local idempotency contract was found.
* Production accessibility, screen-reader, visual, security, and sponsor conclusions require named humans.
* Issue #622 has contradictory launch semantics between its GitHub body and the status-of-record.

## Validation Commands

### Local Pure-Python Baseline

```bash
uv run --no-sync pytest -q \
  tests/test_topic_hubs.py \
  tests/test_trend_explorer_tool.py \
  tests/test_observatory_repos.py \
  tests/test_observatory_embeds.py
```

```bash
uv run --no-sync pytest -q \
  tests/test_sanitize_repo_content.py \
  tests/test_prompt_injection_redteam.py \
  tests/test_defense_chain_e2e.py
```

```bash
uv run --no-sync pytest -q tests/test_export_observatory_dataset.py
uv run --no-sync python scripts/export_observatory_dataset.py --check
uv run --no-sync python scripts/export_trend_explorer_data.py --check
```

### Full Local Source Build When Hugo And Browser Libraries Are Available

```bash
hugo --minify --baseURL http://127.0.0.1:1313/
npx pagefind@1.5.2 --site public/
uv run --no-sync python scripts/serve_static.py --directory public --bind 127.0.0.1 --port 1313
```

Run the server in one terminal, then run:

```bash
BASE_URL=http://127.0.0.1:1313 \
  npx --no-install playwright test \
  --config tests/visual/playwright.config.mjs \
  tests/visual/a11y-perf.spec.mjs \
  tests/visual/observatory-a11y.spec.mjs \
  tests/visual/observatory-analytics.spec.mjs
```

```bash
node scripts/design/lighthouse-gates.mjs --base http://127.0.0.1:1313
```

### GitHub Evidence Checks

```bash
gh run view 30742507113 --repo jmservera/SquadScope \
  --json status,conclusion,headSha,jobs,url
```

```bash
gh run view 30721575540 --repo jmservera/SquadScope \
  --json conclusion,headSha,jobs,url
```

```bash
gh run view 30202586031 --repo jmservera/SquadScope --log
```

```bash
gh api repos/jmservera/SquadScope/environments \
  --jq '.environments[] | {name, protection_rules, deployment_branch_policy}'
```

### Side-Effecting Dispatches Requiring Approval

Do not run either command as a read-only check. Substitute an authorized week and retained publish run only after environment protection, workflow binding, and Podcaster-maintainer approval.

```bash
gh workflow run podcaster-handoff-smoke.yml \
  --repo jmservera/SquadScope \
  --ref main \
  -f week=YYYY-WNN \
  -f article_url=https://claracle.com/weekly/YYYY/WNN/ \
  -f article_path=content/weekly/YYYY/WNN.md \
  -f article_sha256=LOWERCASE_SHA256 \
  -f promotion_reference=data/published/YYYY-WNN/promotion-manifest.json
```

```bash
gh workflow run trigger-podcast.yml \
  --repo jmservera/SquadScope \
  --ref main \
  -f week=YYYY-WNN \
  -f publish_run_id=RUN_ID
```

## References

### Repository Evidence

* docs/review/data-observatory-relaunch/README.md
* docs/review/data-observatory-relaunch/status-of-record.md
* docs/review/data-observatory-relaunch/security-review.md
* docs/review/data-observatory-relaunch/screenshots/README.md
* docs/review/data-observatory-relaunch/screenshots/01-home.png through 10-internal-linking-block.png
* docs/prds/claracle-data-observatory-relaunch.md
* docs/brds/claracle-data-observatory-relaunch-brd.md
* .github/workflows/ci.yml
* .github/workflows/deploy-site.yml
* .github/workflows/podcaster-handoff-smoke.yml
* .github/workflows/trigger-podcast.yml
* .github/workflows/sync-publish-to-main.yml
* scripts/design/lighthouse-gates.mjs
* scripts/manage_topic_hubs.py
* scripts/export_observatory_dataset.py
* scripts/podcaster_handoff.py
* tests/visual/a11y-perf.spec.mjs
* tests/visual/observatory-a11y.spec.mjs
* tests/visual/observatory-analytics.spec.mjs
* tests/visual/visual.spec.mjs

### External Evidence

* [Issue #626](https://github.com/jmservera/SquadScope/issues/626)
* [Issue #622](https://github.com/jmservera/SquadScope/issues/622)
* [Latest confirmed green deploy and dry-run smoke](https://github.com/jmservera/SquadScope/actions/runs/30721575540)
* [Real accepted Podcaster run](https://github.com/jmservera/SquadScope/actions/runs/30202586031)
* [Current reconciliation CI](https://github.com/jmservera/SquadScope/actions/runs/30742507113)

## Follow-On Questions

* [ ] Inspect the completed Lighthouse results and uploaded quality artifacts from CI run 30742507113 after it finishes
* [ ] Confirm whether the Podcaster service deduplicates week or manifest requests outside this repository
* [ ] Confirm the intended required reviewer and branch policy for real Podcaster generation
* [ ] Render current W21-W31 content and verify that topic counts replace the historical empty states
* [ ] Determine the intended Star Velocity normalization model from product/design ownership
* [ ] Decide and document the embed referrer and cross-origin consent policy
* [ ] Resolve the blocking versus non-blocking status of issue #622

## Clarifying Questions

* Who should approve the protected real Podcaster environment: URL, Hermes, jmservera, or a Podcaster maintainer?
* Is issue #622 a mandatory relaunch gate as recorded in status-of-record.md, or non-blocking polish as stated in the issue body?
* Does SquadScope-Podcaster guarantee idempotency for a repeated week or manifest, and where is that contract retained?
* Which screen reader and browser combination is the required NFR-005 manual acceptance target?
